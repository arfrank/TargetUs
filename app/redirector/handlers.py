# -*- coding: utf-8 -*-
"""
	redirection handlers
	~~~~~~~~~~~~~~~~~~~~

	Hello, World!: the simplest tipfy app.

"""
from tipfy import RequestHandler, Response
from tipfyext.jinja2 import Jinja2Mixin


class MainHandler(RequestHandler):
	def get(self, hash=None):
		if not hash:
			return Response('Hello, World!')
		else:
			pass #return self.redirect('https://www.google.com')