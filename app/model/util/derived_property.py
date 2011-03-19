import hashlib
from google.appengine.ext import db


def DerivedProperty(func=None, *args, **kwargs):
  """Implements a 'derived' datastore property.
  
  Derived properties are not set directly, but are instead generated by a
  function when required. They are useful to provide fields in the datastore
  that can be used for filtering or sorting in ways that are not otherwise
  possible with unmodified data - for example, filtering by the length of a
  BlobProperty, or case insensitive matching by querying the lower cased version
  of a string.
  
  DerivedProperty can be declared as a regular property, passing a function as
  the first argument, or it can be used as a decorator for the function that
  does the calculation, either with or without arguments.
  
  Example:
  
  >>> class DatastoreFile(db.Model):
  ...   name = db.StringProperty(required=True)
  ...   name_lower = DerivedProperty(lambda self: self.name.lower())
  ...   
  ...   data = db.BlobProperty(required=True)
  ...   @DerivedProperty
  ...   def size(self):
  ...     return len(self.data)
  ...
  ...   @DerivedProperty(name='sha1')
  ...   def hash(self):
  ...     return hashlib.sha1(self.data).hexdigest()
  
  You can read derived properties the same way you would regular ones:
  
  >>> file = DatastoreFile(name='Test.txt', data='Hello, world!')
  >>> file.name_lower
  'test.txt'
  >>> file.hash
  '943a702d06f34599aee1f8da8ef9f7296031d699'
  
  Attempting to set a derived property will throw an error:
  
  >>> file.name_lower = 'foobar'
  Traceback (most recent call last):
      ...
  DerivedPropertyError: Cannot assign to a DerivedProperty
  
  When persisted, derived properties are stored to the datastore, and can be
  filtered on and sorted by:
  
  >>> file.put() # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'DatastoreFile', ...)
  
  >>> DatastoreFile.all().filter('size =', 13).get().name
  u'Test.txt'
  """
  if func:
    # Regular invocation, or used as a decorator without arguments
    return _DerivedProperty(func, *args, **kwargs)
  else:
    # We're being called as a decorator with arguments
    def decorate(decorated_func):
      return _DerivedProperty(decorated_func, *args, **kwargs)
    return decorate


class _DerivedProperty(db.Property):
  def __init__(self, derive_func, *args, **kwargs):
    """Constructor.
    
    Args:
      func: A function that takes one argument, the model instance, and
        returns a calculated value.
    """
    super(_DerivedProperty, self).__init__(*args, **kwargs)
    self.derive_func = derive_func

  def __get__(self, model_instance, model_class):
    if model_instance is None:
      return self
    return self.derive_func(model_instance)

  def __set__(self, model_instance, value):
    raise db.DerivedPropertyError("Cannot assign to a DerivedProperty")


class LowerCaseProperty(_DerivedProperty):
  """A convenience class for generating lower-cased fields for filtering.
  
  Example usage:
  
  >>> class Pet(db.Model):
  ...   name = db.StringProperty(required=True)
  ...   name_lower = LowerCaseProperty(name)
  
  >>> pet = Pet(name='Fido')
  >>> pet.name_lower
  'fido'
  """
  def __init__(self, property, *args, **kwargs):
    """Constructor.
    
    Args:
      property: The property to lower-case.
    """
    super(LowerCaseProperty, self).__init__(
        lambda self: property.__get__(self, type(self)).lower(),
        *args, **kwargs)


class LengthProperty(_DerivedProperty):
  """A convenience class for recording the length of another field
  
  Example usage:
  
  >>> class TagList(db.Model):
  ...   tags = db.ListProperty(unicode, required=True)
  ...   num_tags = LengthProperty(tags)
  
  >>> tags = TagList(tags=[u'cool', u'zany'])
  >>> tags.num_tags
  2
  """
  def __init__(self, property, *args, **kwargs):
    """Constructor.
    
    Args:
      property: The property to lower-case.
    """
    super(LengthProperty, self).__init__(
        lambda self: len(property.__get__(self, type(self))),
        *args, **kwargs)
