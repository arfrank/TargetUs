from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel

class Redirect(BaseModel):
	referrer = db.TextProperty()
	headers = tipfydb.PickleProperty()
	destination = db.TextProperty()