from google.appengine.ext import db
#from tipfy.appengine import db as tipfydb
from model import base

class Namespace(base.BaseModel):
	name = db.StringProperty()
	