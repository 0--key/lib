from google.appengine.ext import db

class Company(db.Model):
    company_name = db.StringProperty()
    company_n_fractions = db.StringListProperty()
    company_site_url = db.LinkProperty()
    short_description = db.TextProperty()
    sh_d_fractions = db.StringListProperty()# to lower
    phone = db.StringListProperty()
    phone_type = db.StringProperty()
    gen_description = db.TextProperty()
    gen_d_fractions = db.StringListProperty()# to lower
    description_headers = db.StringListProperty()
    description_paragraph = db.TextProperty()
    description_p_fractions = db.StringListProperty()# to lower
    tags = db.StringListProperty()# to lower
    category = db.StringListProperty()# to lower
    address = db.PostalAddressProperty()
    postal_code = db.IntegerProperty() # 
    city = db.StringProperty() #
    city_fractions = db.StringListProperty() #
    country = db.StringProperty() #
    continent = db.StringProperty() #

class Description(db.Model):
    company = db.ReferenceProperty(Company)
    headers = db.StringListProperty()
    paragraph = db.TextProperty()

class City(db.Model):
    city = db.StringProperty()
    unique = db.BooleanProperty(default=False)

"""
class Continents(db.Model):
    continent = db.StringProperty()

class PostalCodes(db.Model):
    code = db.IntegerProperty()

class Countries(db.Model):
    continent = db.ReferenceProperty(Continents)
    country = db.StringProperty()

class Cities(db.Model):
    country = db.ReferenceProperty(Countries)
    city = db.StringProperty()
    city_fractions = db.StringListProperty()

class SearchMetadata(db.Model):
    company = db.ReferenceProperty(Company)
    city = db.ReferenceProperty(Cities)
    postal_code = db.ReferenceProperty(PostalCodes)
    key_words = db.StringListProperty()"""
