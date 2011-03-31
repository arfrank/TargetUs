# -*- coding: utf-8 -*-
from base_handlers import BaseHandler
import model
from tipfy.auth import (login_required, user_required, UserRequiredIfAuthenticatedMiddleware)

class MainHandler(BaseHandler):
	@user_required
	def get(self, **kwargs):
		return self.render_response('manage/home.html', section='Home')

class CreateHandler(BaseHandler):
	@user_required
	def get(self, **kwargs):
		pass

	@user_required
	def post(self, **kwargs):
		pass


class EditHandler(BaseHandler):
	@user_required
	def get(self, **kwargs):
		pass

	@user_required
	def post(self, **kwargs):
		pass


	
class InviteHandler(BaseHandler):
	@user_required
	def get(self, **kwargs):
		pass