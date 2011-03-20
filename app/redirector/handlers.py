# -*- coding: utf-8 -*-
"""
	redirection handlers
	~~~~~~~~~~~~~~~~~~~~

"""
from tipfy import RequestHandler, Response
from tipfy.sessions import SessionStore
from tipfy.sessions import SessionMiddleware
from tipfyext.jinja2 import Jinja2Mixin
from model import redirects, hashes
import logging, time
from google.appengine.ext import deferred
from google.appengine.api import memcache, taskqueue

class MainHandler(RequestHandler):
	middleware = [SessionMiddleware()]
	
	def processStatistics(self,**kwargs):
		logging.info('THIS IS DEFFERED FOR THINGS!')
		logging.info(t)

	def get_namespace(self, headers):
		headers.get('Host')
		namespace = ''
		www = self.request.host
		return namespace, www

	def get(self, hash=None):
		now = time.time()
		namespace, host = self.get_namespace(self.request.headers)
		
		#r = r.get_cookie()
		#logging.info(hash)
		#c = self.session_store.get_session(hash, domain = host)
		#logging.info(c)
		#if 'visited' in c:
		#	logging.info('found in cookie')
		#kwargs = {'max_age':2629743, 'domain':host}
		#self.session_store.set_session(hash, {'visited':True}, **kwargs)
		#self.session_store.save(r)
		#cookie = SessionStore(r).get_session(key=hash, max_age = 2629743, domain = host )
		#logging.info(cookie)
		#logging.info(cookie.value)
		
		hashed = memcache.get(namespace+'-hash-'+str(hash))
		if not hashed:
			hashed = hashes.Hash.all().filter('hash =',hash).get()

		if False and not hashed:
			return self.abort(404)
		else:
			#memcache.set(namespace+'-hash-'+hash, True,time =  2629743, namespace = namespace)
			
			#redirector should set cookie
			r = self.redirect('http://cnn.com')
			
			c = self.request.cookies.get(hash)

			logging.info(c)
	 		r.set_cookie(hash,{'visited':True}, domain=host, max_age = 2629743)
	 		r.set_cookie('_namespace_global',{'visited':True}, domain=host, max_age = 2629743)
			logging.info(str(r.headers))


			#set a queue request to process in the background
			#deferred.defer(self.processStatistics, t = 'farts')
			taskqueue.Queue('statistics').add(taskqueue.Task(url = '/background/statistics', params = {'unique':True, 'header':self.request.headers, 'time' : int(now), 'hash':hash,'host':self.request.host } ) )
			#and redirect the person, all very quickly

			#return self.redirect(self.request.headers.get('Host'))
	
			return r
