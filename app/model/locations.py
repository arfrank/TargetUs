from tipfy.appengine import db
from model.base import BaseModel
from model import hashes

class Location(BaseModel):
	family = db.StringProperty()
	device = db.StringProperty()
	version = db.StringProperty()

	hash = db.ReferenceProperty(hashes.Hash)
	location = db.TextProperty()
	hits = db.IntegerProperty(default = 0)