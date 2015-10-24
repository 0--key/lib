import os
import wsgiref.handlers
import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images
from models import Greeting
from google.appengine.ext import blobstore

def doRender(handler, tname='index.htm', values={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.isfile(temp):
        return False

    # Make a copy of the dictionary and add the path
    newval = dict(values)
    newval['path'] = handler.request.path
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True


class MainPage(webapp.RequestHandler):
    def get(self):
#        self.response.out.write('<html><body>')
        query_str = "SELECT * FROM Greeting ORDER BY date DESC LIMIT 10"
        greetings = db.GqlQuery (query_str)
        template_values = {'greetings':greetings}
        doRender(self,'guestbook.htm',template_values)

class Image (webapp.RequestHandler):
    def get(self):
        greeting = db.get(self.request.get("img_id"))
        if greeting.avatar:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(greeting.avatar)
        else:
            self.response.out.write("No image")

class Guestbook(webapp.RequestHandler):
    def post(self):
      greeting = Greeting()
      if users.get_current_user():
          greeting.author = users.get_current_user()
      greeting.content = self.request.get("content")
      avatar = images.resize(self.request.get("img"), 64, 64)
      greeting.avatar = db.Blob(avatar)
      greeting.put()
      self.redirect('/guestbook/')


application = webapp.WSGIApplication([('/guestbook/img', Image), ('/guestbook/sign', Guestbook),
                                      ('/.*', MainPage)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
