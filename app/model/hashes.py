from tipfy.appengine import db as tipfydb
from tipfy.appengine.auth.model import User
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import namespace_manager

from model.base import BaseModel
from model.locations import Location

from config import config

import logging

class Hash(BaseModel):
	hash = db.StringProperty()
	user = db.ReferenceProperty(User) #who created the hash - not truely important, but good for reference
	desc = db.TextProperty()
	hits = db.IntegerProperty(default = 0)
	default = db.TextProperty()
	
	def __unicode__(self):
		return self.hash
			
	def get_locations(self):
		return Location.all().filter('hash =',self).filter('deleted =',False)
	
	
	
	def get_location(self, family):
		logging.info('Hashes: get_location: Family = '+str(family))
		l = Location.all().filter('hash =',self).filter('deleted =',False).filter('family =',family.lower()).get()
		if l:
			logging.info('Hashes: get_location: Found based on family')
			return l
		logging.info('Hashes: get_location:  Falling back to default')
		l = Location.all().filter('hash =',self).filter('deleted =',False).filter('family =','default').get()
		return l

	def alter_locations(self, **kwargs):
		#expecting in kwargs
		#ios, android, webos, blackberry, default
		ls = []
		for k,v in kwargs.items():
			if k == 'default':
				self.default == v
				self.put()
			ls.extend(self.alter_location(k,v))
		db.put(ls)

	def alter_location(self, family, location, **kwargs):
		ls = []
		l = Location.all().filter('hash = ',self).filter('family = ',family).filter('deleted = ',False).get()
		if l:
			if l.location == location:
				return []
			else:
				l.deleted = True
				ls.append(l)
				#should also clear out memcache here for this entry
		m = Location()
		m.hash = self
		m.location = location
		m.family = family
		ls.append(m)
		return ls
		
	def get_url(self):
		return 'http://'+namespace_manager.get_namespace()+'.'+config['site']['subdomain']+'r/'+self.hash

	def get_qr_url(self):
		return 'https://chart.googleapis.com/chart?chs=200x200&chld=H&cht=qr&chl='+self.get_url()+'&choe=UTF-8'
		
	def increment(self):
		self.hits +=1
		return self.put()