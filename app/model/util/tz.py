from google.appengine.ext import db
from timezones.utils import adjust_datetime_to_timezone,localtime_for_timezone
from django.conf import settings
import datetime

def usertime_to_servertime(value): 
    return adjust_datetime_to_timezone(value, settings.USER_TIME_ZONE, settings.TIME_ZONE)
def servertime_to_usertime(value): 
    return localtime_for_timezone(value, settings.USER_TIME_ZONE)

class TzDateTimeProperty(db.djangoforms.DateTimeProperty): 

    def __init__(self, usertime=False, **kwargs):
        if not isinstance(usertime, bool):
            raise TypeError('User time must be a bool.')
        self.usertime = usertime
        super(TzDateTimeProperty, self).__init__(**kwargs)

    def get_value_for_datastore(self, model_instance):
        value = super(TzDateTimeProperty, self).get_value_for_datastore(model_instance)

        if value is not None:
            if self.usertime: return usertime_to_servertime(value)
            return value

    def make_value_from_datastore(self, value):
        if value is not None:
            return servertime_to_usertime(value)
