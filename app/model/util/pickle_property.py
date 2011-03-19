from google.appengine.ext import db
from google.appengine.api import datastore_errors
import pickle

class PickledProperty(db.Property):
    data_type = db.Text
    force_type = None

    def validate(self, value):
        value = super(PickledProperty, self).validate(value)
        if value is not None and self.force_type and \
            not isinstance(value, self.force_type):
                raise datastore_errors.BadValueError(
                    'Property %s must be of type "%s".' % (self.name,
                        self.force_type))
        return value

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        if value is not None:
            return db.Text(pickle.dumps(value))

    def make_value_from_datastore(self, value):
        if value is not None:
            return pickle.loads(str(value))
            
# the object to be pickled and stored
class MyObject(object):
  pass
  
# the property that forces values to be of type MyObject
class MyObjectProperty(PickledProperty):
    data_type = db.Text
    force_type = MyObject
