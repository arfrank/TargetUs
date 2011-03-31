from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel
from model import hashes

class Location(BaseModel):
	family = db.StringProperty()
	device = db.StringProperty()
	version = db.StringProperty()

	location = db.TextProperty()
	hits = db.IntegerProperty(default = 0)