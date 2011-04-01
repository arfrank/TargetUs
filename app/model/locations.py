from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel
from model.hashes import Hash

class Location(BaseModel):
	family = db.StringProperty(default = None)
	device = db.StringProperty(default = None)
	version = db.StringProperty(default = None)

	hash = db.ReferenceProperty(Hash)

	location = db.TextProperty()
	hits = db.IntegerProperty(default = 0)
	
	def increment(self):
		self.hits +=1
		return self.put()