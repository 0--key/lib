from google.appengine.ext import db

class Placebo(db.Model):
    developer = db.StringProperty()
    OID = db.StringProperty()
    concept = db.StringProperty()
    concept_words = db.ListProperty(str)
    category = db.StringProperty()
    category_words = db.ListProperty(str)
    taxonomy = db.StringProperty()
    taxonomy_words = db.ListProperty(str)
    taxonomy_version = db.StringProperty()
    code = db.StringProperty()
    descriptor = db.StringProperty()
