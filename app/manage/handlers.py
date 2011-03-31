# -*- coding: utf-8 -*-
from base_handlers import BaseHandler,LoggedInHandler
import model
from model import hashes
from tipfy.auth import (login_required, user_required, UserRequiredIfAuthenticatedMiddleware)
from model.util.model_forms import model_form
from werkzeug import cached_property

class MainHandler(LoggedInHandler):
	@user_required
	def get(self, **kwargs):
		return self.render_response('manage/home.html', section='Home')

class CreateHandler(LoggedInHandler):
	@cached_property
	def form(self):
		hash_form =  model_form(hashes.Hash, exclude=('user', 'hits'))
		return hash_form()

	def get(self, **kwargs):
		context = {
			'form': self.form,
		}
		return self.render_response('manage/create.html', **context)

	def post(self, **kwargs):
		pass


class EditHandler(LoggedInHandler):
	def get(self, **kwargs):
		pass

	def post(self, **kwargs):
		pass


	
class InviteHandler(LoggedInHandler):
	def get(self, **kwargs):
		pass