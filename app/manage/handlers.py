# -*- coding: utf-8 -*-
from base_handlers import BaseHandler
import model
from tipfy.auth import (login_required, user_required, UserRequiredIfAuthenticatedMiddleware)

class MainHandler(BaseHandler):
	@user_required
	def get(self, **kwargs):
		return self.render_response('manage/home.html', section='Home')
