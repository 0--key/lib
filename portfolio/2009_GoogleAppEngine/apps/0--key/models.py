from google.appengine.ext import db

class Stuff (db.Model):
    owner = db.UserProperty(required=True, auto_current_user=True)
    pulp = db.BlobProperty()

class Greeting(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    avatar = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class Placebo(db.Model):
    developer = db.StringProperty()
    OID = db.StringProperty()
    concept = db.StringProperty()
    category = db.StringProperty()
    taxonomy = db.StringProperty()
    taxonomy_version = db.StringProperty()
    code = db.StringProperty()
    descriptor = db.StringProperty()
