from werkzeug import cached_property

from tipfy import RequestHandler
from tipfy.auth import (login_required, user_required,
    UserRequiredIfAuthenticatedMiddleware)
#from tipfy.auth.facebook import FacebookMixin
#from tipfy.auth.friendfeed import FriendFeedMixin
#from tipfy.auth.google import GoogleMixin
#from tipfy.auth.twitter import TwitterMixin
from tipfy.sessions import SessionMiddleware
from tipfy.utils import json_encode

from tipfyext.jinja2 import Jinja2Mixin
from tipfyext import wtforms
from tipfyext.wtforms import Form, fields, validators

import logging

class NamespaceMiddleware(object):
    def before_dispatch(self, handler):
		#check that the namespace saved in the session matches the current namespace
		auth = handler.auth
		from google.appengine.api import namespace_manager
		namespace_manager.set_namespace('www')
		host = handler.request.headers.get('Host')
		splits = host.lower().split('.')
		if auth.session and auth.session.get('namespace') != splits[0]:
			namespace_manager.set_namespace(auth.session['namespace'])
			if len(splits) > 1:
				return handler.redirect(auth.session['namespace']+'.'.join(splits[1:]))
			else:
				return handler.redirect('/')
		else:
			if 'appspot' in splits and len(splits)>=4:
				logging.info('setting namespace to '+splits[0])
				namespace_manager.set_namespace(splits[0])
			elif len(splits) >= 3:
				logging.info('setting namespace to '+splits[0])
				namespace_manager.set_namespace(splits[0])
# ----- Handlers -----

class BaseHandler(RequestHandler, Jinja2Mixin):
    middleware = [SessionMiddleware(), UserRequiredIfAuthenticatedMiddleware(), NamespaceMiddleware()]

    @cached_property
    def messages(self):
        """A list of status messages to be displayed to the user."""
        return self.session.get_flashes(key='_messages')

    def render_response(self, filename, **kwargs):
        auth_session = None
        if self.auth.session:
            auth_session = self.auth.session

        kwargs.update({
            'auth_session': auth_session,
            'current_user': self.auth.user,
            'login_url':    self.auth.login_url(),
            'logout_url':   self.auth.logout_url(),
            'current_url':  self.request.url,
        })
        if self.messages:
            kwargs['messages'] = json_encode([dict(body=body, level=level)
                for body, level in self.messages])

        return super(BaseHandler, self).render_response(filename, **kwargs)

    def redirect_path(self, default='/'):
        if '_continue' in self.session:
            url = self.session.pop('_continue')
        else:
            url = self.request.args.get('continue', '/')

        if not url.startswith('/'):
            url = default

        return url

    def _on_auth_redirect(self):
        """Redirects after successful authentication using third party
        services.
        """
        if '_continue' in self.session:
            url = self.session.pop('_continue')
        else:
            url = '/'

        if not self.auth.user:
            url = self.auth.signup_url()

        return self.redirect(url)
