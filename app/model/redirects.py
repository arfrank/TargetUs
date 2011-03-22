from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel

class Redirect(BaseModel):
	hash = db.StringProperty()
	host = db.TextProperty()
	user_agent = db.TextProperty()
	headers = tipfydb.PickleProperty()
	destination = db.TextProperty()
	timestamp = db.IntegerProperty()
	