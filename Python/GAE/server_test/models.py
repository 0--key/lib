from google.appengine.ext import ndb


class Results(ndb.Model):
    """Primitive key --> value model"""
    a_key = ndb.StringProperty()
    a_value = ndb.PickleProperty()
