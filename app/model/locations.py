from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel

class Location(BaseModel):
	family = db.StringProperty(default = None)
	device = db.StringProperty(default = None)
	version = db.StringProperty(default = None)

	#will always reference the hash property, just cant put it hear due to circular reference
	hash = db.ReferenceProperty()

	location = db.TextProperty()
	hits = db.IntegerProperty(default = 0)
	
	def increment(self):
		self.hits +=1
		return self.put()