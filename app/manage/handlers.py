# -*- coding: utf-8 -*-
from base_handlers import BaseHandler,LoggedInHandler
import model
from model import hashes, locations
from tipfy.auth import (login_required, user_required, UserRequiredIfAuthenticatedMiddleware)
from model.util.model_forms import model_form
from werkzeug import cached_property
import logging
from tipfyext import wtforms
from tipfyext.wtforms import Form, fields, validators
from google.appengine.ext import db
REQUIRED = validators.required()

class MainHandler(LoggedInHandler):
	def get(self, **kwargs):
		return self.render_response('manage/home.html', section='manage')

def ensure_hash(form,field):
	#we're already in the right namespace
	if field.data != '':
		h = hashes.Hash.all().filter('hash =',field.data).get()
		logging.info('Ensure Hash Unique: '+h)
		#uniqueness
		if h:
			raise wtforms.ValidationError('That hash has already been used.')
		#also validate that its allowed for things
		#^[0-9A-Za-z._-]{0,100}$

class LocationForm(Form):
	family = fields.SelectField()
	location = fields.TextField('Redirect URL', validators = [validators.URL()])

class CreateForm(Form):
	hash = fields.TextField('Hash', validators = [ensure_hash, validators.Regexp('^[0-9A-Za-z]{0,100}$', message="Hashes may only use A-Z, a-z and 0-9")])
	"""
	redirector1 = fields.SelectField('redirector1')
	redirector2 = fields.SelectField('redirector2')
	redirector3 = fields.SelectField('redirector3')
	redirector4 = fields.SelectField('redirector4')
	
	redirect1 = fields.TextField('redirect1')
	redirect2 = fields.TextField('redirect2')
	redirect3 = fields.TextField('redirect3')
	redirect4 = fields.TextField('redirect4')
	"""
	desc = fields.TextField('Link Description', validators = [REQUIRED])
	ios = fields.TextField('iOS (iPhone/iPad/iPod)', validators = [validators.URL(),validators.Optional()])
	android = fields.TextField('Android', validators = [validators.URL(),validators.Optional()])
 	webOS = fields.TextField('webOS (HP/Palm)', validators = [validators.URL(),validators.Optional()])
	blackberry = fields.TextField('Blackberry', validators = [validators.URL(),validators.Optional()])
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

			locs = {}
			if self.form.ios.data:
				locs['ios'] = self.form.ios.data
			if self.form.android.data:
				locs['android'] = self.form.android.data
			if self.form.webOS.data:
				locs['webos'] = self.form.webOS.data
			if self.form.blackberry.data:
				locs['blackberry'] = self.form.blackberry.data
			locs['default'] = self.form.default.data
			h.alter_locations(**locs)

			return self.redirect('/manage/view/'+h.hash)

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
			return self.redirect(self.url_for('manage/create'))
		
		h = hashes.Hash.all().filter('hash = ', str(hash)).get()
		if not h:
			return self.redirect(self.url_for('manage/create'))
		context = {
			'hash': h,
			'form':self.form,
		}
		return self.render_response('manage/edit.html', **context)

	def post(self, **kwargs):
		pass

class AllHandler(LoggedInHandler):
	def get(self,**kwargs):
		context = {
			'section':'All',
			'hashes': hashes.Hash.all().filter('deleted = ',False),
		}
		return self.render_response('manage/all.html', **context)

class ViewHandler(LoggedInHandler):
	def get(self,hash = None, **kwargs):
		logging.info('ViewHandler: hash = '+hash)
		context = {
			'section':'View',
			'hash': hashes.Hash.all().filter('deleted = ',False).filter('hash = ',hash).get(),
		}
		return self.render_response('manage/view.html', **context)



class InviteHandler(LoggedInHandler):
	def get(self, **kwargs):
		pass