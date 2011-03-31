from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
from model.base import BaseModel
from model import locations

class Redirect(locations.Location):
	#which location we are hitting - inherit it so we have some continuation if the locations are updated and we have to tell it to go away
	hash = db.StringProperty()
	host = db.TextProperty()
	user_agent = db.TextProperty()
	headers = tipfydb.PickleProperty()
	destination = db.TextProperty()
	timestamp = db.IntegerProperty()
	