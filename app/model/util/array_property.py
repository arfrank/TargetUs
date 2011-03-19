import array
from google.appengine.ext import db
from google.appengine.api import datastore_errors

class ArrayProperty(db.Property):
  def __init__(self, data_type, **kwargs):
    self.data_type = data_type
    super(ArrayProperty, self).__init__(**kwargs)

  def default_value(self):
    return array.array(self.typecode)

  def validate(self, value):
    if not isinstance(value, array.array) or value.typecode != self.typecode:
      raise datastore_errors.BadValueError(
        "Property %s must be an array instance with typecode %s"
        % (self.name, self.typecode))
    value = super(ArrayProperty, self).validate(value)
    return value

  def get_value_for_datastore(self, model_instance):
    value = self.__get__(model_instance, model_instance.__class__)
    return db.Blob(value.tostring())

  def make_value_from_datastore(self, value):
    a = array.array(self.typecode)
    if value is None: return a
    a.fromstring(value)
    return a

  data_type=db.Blob
