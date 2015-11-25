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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            authurl = users.create_logout_url(self.request.path_info)
        else:
            nickname = ""
            authurl = users.create_login_url(self.request.path_info)
        t_values = {'name':nickname, 'authurl':authurl}
        template = jinja_environment.get_template('concept.htm')
        self.response.out.write(template.render(t_values))

application = webapp.WSGIApplication([(r'/concept', MainHandler),], debug=True)
