import logging

from werkzeug import cached_property

from tipfy import RequestHandler
from tipfy.auth import (login_required, user_required,
	UserRequiredIfAuthenticatedMiddleware)
from tipfy.auth.facebook import FacebookMixin
from tipfy.auth.friendfeed import FriendFeedMixin
from tipfy.auth.google import GoogleMixin
from tipfy.auth.twitter import TwitterMixin
from tipfy.sessions import SessionMiddleware
from tipfy.utils import json_encode

from tipfyext.jinja2 import Jinja2Mixin
from tipfyext import wtforms
from tipfyext.wtforms import Form, fields, validators

from base_handlers import BaseHandler

# ----- Forms -----

REQUIRED = validators.required()

class LoginForm(Form):
	username = fields.TextField('Username', validators=[REQUIRED])
	password = fields.PasswordField('Password', validators=[REQUIRED])
	remember = fields.BooleanField('Keep me signed in')


class SignupForm(Form):
	nickname = fields.TextField('Nickname', validators=[REQUIRED])


class RegistrationForm(Form):
	username = fields.TextField('Username', validators=[REQUIRED])
	password = fields.PasswordField('Password', validators=[REQUIRED])
	password_confirm = fields.PasswordField('Confirm the password', validators=[REQUIRED])
	namespace = fields.TextField('Namespace', validators=[REQUIRED])



class HomeHandler(BaseHandler):
	def get(self, **kwargs):
		return self.render_response('auth/home.html', section='home')


class ContentHandler(BaseHandler):
	@user_required
	def get(self, **kwargs):
		return self.render_response('auth/content.html', section='content')


class LoginHandler(BaseHandler):
	def get(self, **kwargs):
		logging.info(self.request.host)
		if not self.request.host.split('.')[0].lower() == 'www' or self.request.host.split('.')[0].lower() == self.app.get_config('site','appspot_id'):
			return self.render_response('auth/redirect.html')
 		redirect_url = self.redirect_path()

		if self.auth.user:
			# User is already registered, so don't display the signup form.
			return self.redirect(redirect_url)

		opts = {'continue': self.redirect_path()}
		context = {
			'form':					self.form,
			#'facebook_login_url':	 self.url_for('auth/facebook', **opts),
			#'friendfeed_login_url': self.url_for('auth/friendfeed', **opts),
			#'google_login_url':	 self.url_for('auth/google', **opts),
			#'twitter_login_url':	 self.url_for('auth/twitter', **opts),
			#'yahoo_login_url':		 self.url_for('auth/yahoo', **opts),
		}
		return self.render_response('auth/login.html', **context)

	def post(self, **kwargs):
		redirect_url = self.redirect_path()

		if self.auth.user:
			# User is already registered, so don't display the signup form.
			return self.redirect(redirect_url)

		if self.form.validate():
			username = self.form.username.data
			password = self.form.password.data
			remember = self.form.remember.data

			res = self.auth.login_with_form(username, password, remember)
			if res:
				self.session.add_flash('Welcome back!', 'success', '_messages')
				return self.redirect(redirect_url)

		self.messages.append(('Authentication failed. Please try again.',
			'error'))
		return self.get(**kwargs)

	@cached_property
	def form(self):
		return LoginForm(self.request)


class LogoutHandler(BaseHandler):
	def get(self, **kwargs):
		self.auth.logout()
		return self.redirect(self.redirect_path())


class SignupHandler(BaseHandler):
	@login_required
	def get(self, **kwargs):
		if self.auth.user:
			# User is already registered, so don't display the signup form.
			return self.redirect(self.redirect_path())

		return self.render_response('auth/signup.html', form=self.form)

	@login_required
	def post(self, **kwargs):
		redirect_url = self.redirect_path()

		if self.auth.user:
			# User is already registered, so don't process the signup form.
			return self.redirect(redirect_url)

		if self.form.validate():
			auth_id = self.auth.session.get('id')
			user = self.auth.create_user(self.form.nickname.data, auth_id)
			if user:
				self.auth.login_with_auth_id(user.auth_id, True)
				self.session.add_flash('You are now registered. Welcome!',
					'success', '_messages')
				return self.redirect(redirect_url)
			else:
				self.messages.append(('This nickname is already registered.',
					'error'))
				return self.get(**kwargs)

		self.messages.append(('A problem occurred. Please correct the '
			'errors listed in the form.', 'error'))
		return self.get(**kwargs)

	@cached_property
	def form(self):
		return SignupForm(self.request)


class RegisterHandler(BaseHandler):
	def get(self, **kwargs):
		redirect_url = self.redirect_path()

		if self.auth.user:
			# User is already registered, so don't display the registration form.
			return self.redirect(redirect_url)

		return self.render_response('auth/register.html', form=self.form)

	def post(self, **kwargs):
		redirect_url = self.redirect_path()

		if self.auth.user:
			# User is already registered, so don't process the signup form.
			return self.redirect(redirect_url)

		if self.form.validate():
			username = self.form.username.data
			password = self.form.password.data
			password_confirm = self.form.password_confirm.data

			if password != password_confirm:
				self.messages.append(("Password confirmation didn't match.",
					'error'))
				return self.get(**kwargs)

			auth_id = 'own|%s' % username
			user = self.auth.create_user(username, auth_id, password=password)
			if user:
				self.auth.login_with_auth_id(user.auth_id, True)
				self.session.add_flash('You are now registered. Welcome!',
					'success', '_messages')
				return self.redirect(redirect_url)
			else:
				self.messages.append(('This nickname is already registered.',
					'error'))
				return self.get(**kwargs)

		self.messages.append(('A problem occurred. Please correct the '
			'errors listed in the form.', 'error'))
		return self.get(**kwargs)

	@cached_property
	def form(self):
		return RegistrationForm(self.request)


class FacebookAuthHandler(BaseHandler, FacebookMixin):
	def head(self, **kwargs):
		"""Facebook will make a HEAD request before returning a callback."""
		return self.app.response_class('')

	def get(self):
		url = self.redirect_path()

		if self.auth.session:
			# User is already signed in, so redirect back.
			return self.redirect(url)

		self.session['_continue'] = url

		if self.request.args.get('session', None):
			return self.get_authenticated_user(self._on_auth)

		return self.authenticate_redirect()

	def _on_auth(self, user):
		"""
		"""
		if not user:
			self.abort(403)

		# try user name, fallback to uid.
		username = user.pop('username', None)
		if not username:
			username = user.pop('uid', '')

		auth_id = 'facebook|%s' % username
		self.auth.login_with_auth_id(auth_id, remember=True,
			session_key=user.get('session_key'))
		return self._on_auth_redirect()


class FriendFeedAuthHandler(BaseHandler, FriendFeedMixin):
	"""
	"""
	def get(self):
		url = self.redirect_path()

		if self.auth.session:
			# User is already signed in, so redirect back.
			return self.redirect(url)

		self.session['_continue'] = url

		if self.request.args.get('oauth_token', None):
			return self.get_authenticated_user(self._on_auth)

		return self.authorize_redirect()

	def _on_auth(self, user):
		if not user:
			self.abort(403)

		auth_id = 'friendfeed|%s' % user.pop('username', '')
		self.auth.login_with_auth_id(auth_id, remember=True,
			access_token=user.get('access_token'))
		return self._on_auth_redirect()


class TwitterAuthHandler(BaseHandler, TwitterMixin):
	def get(self):
		url = self.redirect_path()

		if self.auth.user:
			# User is already signed in, so redirect back.
			return self.redirect(url)

		self.session['_continue'] = url

		if self.request.args.get('oauth_token', None):
			return self.get_authenticated_user(self._on_auth)

		return self.authorize_redirect(callback_uri='/auth/twitter/')

	def _on_auth(self, user):
		if not user:
			self.abort(403)

		auth_id = 'twitter|%s' % user.pop('username', '')
		self.auth.login_with_auth_id(auth_id, remember=True,
			access_token=user.get('access_token'))
		return self._on_auth_redirect()


class GoogleAuthHandler(BaseHandler, GoogleMixin):
	def get(self):
		url = self.redirect_path()

		if self.auth.session:
			# User is already signed in, so redirect back.
			return self.redirect(url)

		self.session['_continue'] = url

		if self.request.args.get('openid.mode', None):
			return self.get_authenticated_user(self._on_auth)

		return self.authenticate_redirect()

	def _on_auth(self, user):
		if not user:
			self.abort(403)

		auth_id = 'google|%s' % user.pop('email', '')
		self.auth.login_with_auth_id(auth_id, remember=True)
		return self._on_auth_redirect()
