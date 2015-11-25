import os, logging, md5, jinja2
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import datastore
from google.appengine.ext import db
from google.appengine.api import users
from models import Company
from google.appengine.api import memcache
from review import get_companies_data, get_unique_tags
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), './templates')
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

class VikarbureauHandler(webapp2.RequestHandler):
    def get(self, raw_city):
        city = self.request.path_info.split('/')[-1].decode('utf8')
        if raw_city:
            query_str = "SELECT * FROM Company WHERE city='%s'" % city
        else:
            query_str = "SELECT * FROM Company WHERE city='Aabybro'"
            city='Aabybro'
        # lets try to memcache the polular pages:
        cache_key = md5.new(query_str.encode('ascii', 'ignore')).hexdigest()
        if memcache.get(key=cache_key):
            companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = memcache.get(key=cache_key)
            logging.info("Cache works perfectly!")
        else:
            companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = get_companies_data(query_str)
            memcache.set(key=cache_key, value=get_companies_data(query_str), time=3600)
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            authurl = users.create_logout_url(self.request.path_info)
        else:
            nickname = ""
            authurl = users.create_login_url(self.request.path_info)
        template_values = {'companies':companies_data, 'results_number':results_number, 'cities_first_letters':first_letters_list, 'cities':unique_cities, 'cities_ordered':cities_ordered, 'search_navbar':navbar, 'category':city, 'tags':get_unique_tags(), 'name':nickname, 'authurl':authurl}
        template = jinja_environment.get_template('vikarbureau_restyled.htm')
        self.response.out.write(template.render(template_values))

class TagHandler(webapp2.RequestHandler):
    def get(self, raw_tag):
        tag = self.request.path_info.split('/')[-1].decode('utf8')
        if raw_tag:
            query_str = "SELECT * FROM Company WHERE tags='%s'" % tag
        else:
            query_str = "SELECT * FROM Company WHERE tags='alarm'"
            tag='alarm'
        # lets try to memcache the polular pages:
        cache_key = md5.new(query_str.encode('ascii', 'ignore')).hexdigest()
        if memcache.get(key=cache_key):
            companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = memcache.get(key=cache_key)
            logging.info("Cache works perfectly!")
        else:
            companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = get_companies_data(query_str)
            memcache.set(key=cache_key, value=get_companies_data(query_str), time=3600)
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            authurl = users.create_logout_url(self.request.path_info)
        else:
            nickname = ""
            authurl = users.create_login_url(self.request.path_info)
        template_values = {'companies':companies_data, 'results_number':results_number, 'cities_first_letters':first_letters_list, 'cities':unique_cities, 'cities_ordered':cities_ordered, 'search_navbar':navbar, 'category':tag, 'tags':get_unique_tags(), 'name':nickname, 'authurl':authurl}
        template = jinja_environment.get_template('vikarbureau_restyled.htm')
        self.response.out.write(template.render(template_values))



application = webapp.WSGIApplication([(r'/vikarbureau/(.*)', VikarbureauHandler), (r'/tag/(.*)', TagHandler)], debug=True)
