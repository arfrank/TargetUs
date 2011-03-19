from tipfy.ext import db
import model.util.properties

class BaseModel(db.Expando):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
    