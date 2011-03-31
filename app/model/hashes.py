from tipfy.appengine import db as tipfydb
from tipfy.appengine.auth.model import User
from google.appengine.ext import db
from model.base import BaseModel

class Hash(BaseModel):
	user = db.ReferenceProperty(User) #who created the hash - not truely important, but good for reference
	desc = db.TextProperty()
	hits = db.IntegerProperty(default = 0)
	default = db.TextProperty()