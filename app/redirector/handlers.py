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
from utils import devices

class MainHandler(RequestHandler):
	middleware = [SessionMiddleware()]

	def get_namespace(self, headers):
		headers.get('Host')
		namespace = self.request.host.split('.')[0]
		www = self.request.host
		return namespace, www

	def get(self, hash=None):
		#GET THE CURRENT TIME!
		now = time.time()
		#DETERMINE NAMESPACE AND THE ACTUAL HOST URL
		namespace, host = self.get_namespace(self.request.headers)

		#SEE IF THAT HASH IS CACHED FOR THIS NAMESPACE SO I DONT NEED TO LOOKUP the hash key?
		hashed = memcache.get(namespace+'-hash-'+str(hash))
		if not hashed:
			hashed = hashes.Hash.all().filter('hash =',hash).get()

		#IF HASHED DOESNT EXIST
		if False and not hashed:
			return self.abort(404)
		#OTHERWISE LETS START PROCESSING
		else:
			device, family = devices.determine_device(self.request.headers)
			logging.info(device)
			logging.info(family)

			#SET THE HASH
			#memcache.set(namespace+'-hash-'+str(hash), True,time =  2629743, namespace = namespace)
			
			#redirector should set cookie
			r = self.redirect('/')
			
			#CHECK COOKIES HASH
			hash_cookie = self.request.cookies.get(hash)
			hash_unique = True
			if hash_cookie and 'visited' in hash_cookie:
				hash_unique = False
			else:
				r.set_cookie(hash,{'visited':True}, domain=host, max_age = 2629743)

			#CHECK COOKIE NAMESPACE
			namespace_cookie = self.request.cookies.get('namespace_global')
			namespace_unique = True
			if namespace_cookie and 'visited' in namespace_cookie:
				namespace_unique = False
			else:
		 		r.set_cookie('namespace_global',{'visited':True}, domain=host, max_age = 2629743)

			#set a queue request to process in the background
			#deferred.defer(self.processStatistics, t = 'farts')
			taskqueue.Queue('statistics').add(taskqueue.Task(url = '/background/statistics', params = 
					{
						'Hash_unique':hash_unique,
						'Namespace_unique':namespace_unique,
						
						'Device':device,
						'Family':family,
						'User-Agent':self.request.headers.get('User-Agent'),
						
						'Time' : int(now),
						
						'Hash': hash,
						'Host': self.request.host,

						''
					}
				)
			)
			#and redirect the person, all very quickly

			#return self.redirect(self.request.headers.get('Host'))
			logging.info(r.headers)
			return r
