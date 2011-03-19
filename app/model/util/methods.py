from google.appengine.ext import db
import logging

def getRelationalEntityIndexes(all_parent_keys, cls, relationship='parent', sort=False):
  """ 
  
  Args:
       sort - method
  
  for a list of parent keys and a class and relationship, query for a 
  sorted list of relational entities
  Warning: sorting alphabetically on keyname works differently
  than db order() ('_' is after z, instead of before a) 
  
  Also, use db.Key.from_path instead where possible.
  
  """
  relational_entities = []
  from utils.utils import slice_up_list
  parent_key_lists = slice_up_list(all_parent_keys)
  for parent_keys in parent_key_lists:
    relational_entities.extend(cls.all().filter(
    relationship +' IN',parent_keys).fetch(1000))
  # This needs a sort for the contents to be ordered correctly!
  if sort:
    relational_entities.sort(key=sort)
  return relational_entities
  
  
def count_entities(cls, fetch_count=1000, key_offset = None):
    """
    Count *all* of the rows (without maxing out at 1000)
    """
    count = 0
    query = cls.all().order('__key__')
    if key_offset: query = query.filter('__key__ > ',db.Key(key_offset))

    while count % fetch_count == 0:
        current_count = query.count()
        if current_count == 0:
           break
        count += current_count

        if current_count == fetch_count:
            last_key = query.fetch(1, fetch_count - 1)[0].key()
            query = query.filter('__key__ > ', last_key)
            logging.info("count for class %s:  %d with last_key %s" % (cls.__name__, count, str(last_key)))
    return count



def run_method_on_entities(cls, method, fetch_count=500, key_offset = None, task_args=None):
    """
    Run method on *all* of the rows (without maxing out at 1000)
    """
    count = 0
    if cls.__class__.__name__ == 'Query': query = cls.order('__key__')
    else: query = cls.all().order('__key__')
    if key_offset: 
      logging.info('key offset is %s' % key_offset)
      query = query.filter('__key__ > ', db.Key(key_offset))

    while count % fetch_count == 0:
        entities = query.fetch(fetch_count)
        if not task_args:
          from utils.utils import defer
          defer(method, [ str(entity.key()) for entity in entities])
        elif task_args: # deprecated
          from utils.utils import add_task
          _task_args = task_args.copy()
          _task_args['name'] = task_args['name'] + str(count)
          _task_args['params']['entities'] = [ str(entity.key()) for entity in entities]
          print ""
          print _task_args['params']['entities']
          add_task(**_task_args)
          
        current_count = len(entities)
        if current_count == 0:
           break
        count += current_count

        if current_count >= fetch_count:          
            last_key = query.fetch(1, fetch_count-1)[0].key()
            query = query.filter('__key__ > ', last_key)
            logging.info("count for class %s:  %d with last_key %s" % (cls.__name__, count, str(last_key)))
    return count




class Mapper(object):
  # Subclasses should replace this with a model class (eg, model.Person).
  KIND = None

  # Subclasses can replace this with a list of (property, value) tuples to filter by.
  FILTERS = []
  
  def map(self, entity):
    """Updates a single entity.
   
    Implementers should return a tuple containing two iterables (to_update, to_delete).
    """
    return ([], [])

  def get_query(self):
    """Returns a query over the specified kind, with any appropriate filters applied."""
    q = self.KIND.all()
    for prop, value in self.FILTERS:
      q.filter("%s =" % prop, value)
    q.order("__key__")
    return q

  def run(self, batch_size=100):
    """Executes the map procedure over all matching entities."""
    q = self.get_query()
    entities = q.fetch(batch_size)
    while entities:
      to_put = []
      to_delete = []
      for entity in entities:
        map_updates, map_deletes = self.map(entity)
        to_put.extend(map_updates)
        to_delete.extend(map_deletes)
      if to_put:
        db.put(to_put)
      if to_delete:
        db.delete(to_delete)
      q = self.get_query()
      q.filter("__key__ >", entities[-1].key())
      entities = q.fetch(batch_size)
  
  

"""

# use bulkloader with JSON

class JSONLoader(bulkloader.Loader):
    def generate_records(self, filename):
        for item in json.load(open(filename)):
            yield item['fields']

"""

def autoretry_datastore_timeouts(attempts=5.0, interval=0.1, exponent=2.0):
    """
    Copyright (C)  2009  ROBIN BHATTACHARYYA.
    
    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
    
    ======================================================================
    
    This function wraps the AppEngine Datastore API to autoretry 
    datastore timeouts at the lowest accessible level.  

    The benefits of this approach are:

    1. Small Footprint:  Does not monkey with Model internals 
                         which may break in future releases.
    2. Max Performance:  Retrying at this lowest level means 
                         serialization and key formatting is not 
                         needlessly repeated on each retry.

    At initialization time, execute this:
    
    >>> autoretry_datastore_timeouts()
    
    Should only be called once, subsequent calls have no effect.
    
    >>> autoretry_datastore_timeouts() # no effect
    
    Parameters can each be specified as floats.
    
    :param attempts: maximum number of times to retry.
    :param interval: base seconds to sleep between retries.
    :param exponent: rate of exponential back-off.
    """
    
    raise ValueError
    import time
    from google.appengine.ext import db
    from google.appengine.api import apiproxy_stub_map
    
    attempts = float(attempts)
    interval = float(interval)
    exponent = float(exponent)
    wrapped = apiproxy_stub_map.MakeSyncCall

    
    def wrapper(*args, **kwargs):
        count = 0.0
        while True:
            try:
                return wrapped(*args, **kwargs)
            except db.Timeout:
                logging.error('model.util.autoretry_datastore_timeouts \
                auto-retrying db call')
                #return
                sleep = (exponent ** count) * interval
                count += 1.0
                if count > attempts: raise
                time.sleep(sleep)

    setattr(wrapper, '_should_wrap', False)
    if getattr(wrapped, '_should_wrap', True):
        apiproxy_stub_map.MakeSyncCall = wrapper
