# -*- coding: utf-8 -*-
from base_handlers import BaseHandler,LoggedInHandler
import model
from model import hashes
from tipfy.auth import (login_required, user_required, UserRequiredIfAuthenticatedMiddleware)
from model.util.model_forms import model_form
from werkzeug import cached_property
import logging
from tipfyext import wtforms
from tipfyext.wtforms import Form, fields, validators

REQUIRED = validators.required()

class MainHandler(LoggedInHandler):
	@user_required
	def get(self, **kwargs):
		return self.render_response('manage/home.html', section='Home')

def ensure_hash(form,field):
	#we're already in the right namespace
	if field.data != '':
		h = hashes.Hash.all().filter('hash =',field.data).get()
		logging.info(h)
		#uniqueness
		if h:
			raise wtforms.ValidationError('That hash has already been used.')
		#also validate that its allowed for things
		restricted = [' ',',','?','.']
		for r in restricted:
			if r in field.data:
				raise wtforms.ValidationError('Hashes may only contain a-z, A-Z &amp; 0-9')
				

class CreateForm(Form):
	hash = fields.TextField('Hash Tag', validators = [ensure_hash])
	desc = fields.TextField('Link Description', validators = [REQUIRED])
	default = fields.TextField('Default', validators = [REQUIRED, validators.URL()])
	
class CreateHandler(LoggedInHandler):
	@cached_property
	def form(self):
		return CreateForm(self.request)

	def get(self, **kwargs):
		context = {
			'form': self.form,
		}
		return self.render_response('manage/create.html', **context)

	def post(self, **kwargs):
		if self.form.validate():
			h = hashes.Hash()
			h.hash = self.form.hash.data
			h.desc = self.form.desc.data
			h.user = self.auth.user
			h.default = self.form.default.data
			h.put()
			return self.redirect('/manage/edit/'+h.hash)

		self.messages.append(('Authentication failed. Please try again.',
			'error'))
		return self.get(**kwargs)

class EditForm(Form):
	pass

class EditHandler(LoggedInHandler):
	@cached_property
	def form(self):
		return EditForm(self.request)

	def get(self, hash = None, **kwargs):
		if hash == None:
			return self.redirect(url_for('manage/create'))
		
		h = hashes.Hash.all().filter('hash = ', str(hash)).get()
		if not h:
			return self.redirect(url_for('manage/create'))
		context = {
			'hash': h,
			'form':self.form,
		}
		return self.render_response('manage/edit.html', **context)

	def post(self, **kwargs):
		pass


	
class InviteHandler(LoggedInHandler):
	def get(self, **kwargs):
		pass