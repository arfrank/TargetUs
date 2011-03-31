from tipfy.appengine import db as tipfydb
from google.appengine.ext import db
import model.util.properties

class BaseModel(db.Expando):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
	deleted = db.BooleanProperty(default = False)

	def get_active(self):
		return self.all().filter('deleted =',False)
		
	def get_newest(self):
		return self.all().order('-created').get()
