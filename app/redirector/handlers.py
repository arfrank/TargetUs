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

from google.appengine.api import namespace_manager

class MainHandler(RequestHandler):
	middleware = [SessionMiddleware()]

	def get_namespace(self, headers):
		headers.get('Host')
		namespace = self.request.host.split('.')[0]
		www = self.request.host
		return namespace, www

	def check_cookie(self,response, cookie_name, host):
		cookie = self.request.cookies.get(cookie_name)

		unique = True
		if cookie and 'visited' in cookie:
			unique = False
		else:
			response.set_cookie(cookie_name,{'visited':True}, domain=host, max_age = 2629743)

		return response, unique


	def get(self, hash=None):
		#GET THE CURRENT TIME!
		now = time.time()
		
		#DETERMINE NAMESPACE AND THE ACTUAL HOST URL
		namespace, host = self.get_namespace(self.request.headers)
		if self.request.args.get('namespace'):
			namespace = self.request.args.get('namespace')
		logging.info('Redirector: Setting namespace to: '+namespace)
		namespace_manager.set_namespace(namespace)

		#SEE IF THAT HASH IS CACHED FOR THIS NAMESPACE SO I DONT NEED TO LOOKUP the hash key?
		hashed = memcache.get(namespace+'-hash-'+str(hash))
		h_found = False
		if hashed:
			h_found = True
			hashed = hashes.Hash.get_by_key_name(str(hashed))

		if not hashed:
			h_found = False
			hashed = hashes.Hash.all().filter('hash =',hash).filter('deleted =',False).get()

		#IF HASHED DOESNT EXIST
		if not hashed:
			return self.abort(404)
		#OTHERWISE LETS START PROCESSING
		else:
			family, device = devices.determine_device(self.request.headers)
			logging.info('Redirector: Headers Following')
			logging.info(self.request.headers)
			logging.info('Redirector: Family = '+family)
			logging.info('Redirector: Device = '+device)

			#SET THE HASH
			if not h_found:
				logging.info('Redirector: Not found in memcache, setting memcache key')
				memcache.set(namespace+'-hash-'+str(hash), hashed.key().name(),time =  2629743)
			
			#redirector should set cookie
			loc = hashed.get_location(family)
			logging.info('Redirector: Redirect found: Family = '+loc.family+' Loc='+loc.location)
			r = self.redirect(loc.location)
			
			
			#CHECK UNIQUENESS FROM COOKIES FOR STATISTICS
			#CHECK COOKIES HASH
			r, hash_unique  = self.check_cookie(r,hash,host)
			#CHECK COOKIE NAMESPACE
			r, namespace_unique = self.check_cookie(r,'namespace_global',host)

			#set a queue request to process in the background
			#deferred.defer(self.processStatistics, t = 'farts')
			taskqueue.Queue('statistics').add(taskqueue.Task(url = '/background/statistics', params = 
					{
						'Hash_unique':hash_unique,
						'Namespace_unique':namespace_unique,
						'Namespace' : namespace,

						'Device':device,
						'Family':family,
						'User-Agent':self.request.headers.get('User-Agent'),
						
						'Time' : int(now),
						
						'Hash': hash,
						'Host': self.request.host,
					}
				)
			)
			
			#create a redirect element
			
			
			#and redirect the person, all very quickly
			#return self.redirect(self.request.headers.get('Host'))
			logging.info(r.headers)
			return r
