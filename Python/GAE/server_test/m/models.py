from google.appengine.ext import ndb


class Result(ndb.Model):
    """Primitive key --> value model"""
    a_key = ndb.StringProperty()
    a_value = ndb.PickleProperty()
