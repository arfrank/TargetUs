# -*- coding: utf-8 -*-
from base_handlers import BaseHandler

class MainHandler(BaseHandler):
    def get(self, **kwargs):
        return self.render_response('main/home.html', section='Home')
