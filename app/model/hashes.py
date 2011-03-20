from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel

class Hash(BaseModel):
	location = db.TextProperty()