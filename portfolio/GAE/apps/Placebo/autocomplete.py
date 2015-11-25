import os
import logging
import simplejson
import wsgiref.handlers
from google.appengine.ext import webapp

from google.appengine.ext import db
from models import Placebo

class MainHandler(webapp.RequestHandler):
    def get(self):
        field_names = {'concept': 'concept_words', 'category': 'category_words', 'taxonomy': 'taxonomy_words'}
        term = str(self.request.get('term')).lower()
        name = str(self.request.get('name')).lower()
        
        if term and name in field_names.keys():
            results = db.GqlQuery("SELECT * FROM Placebo WHERE %s >= '%s'" % (field_names[name], term))
            results = dict([(word, None) for result in results for word in result.__dict__['_entity'][field_names[name]] if word.startswith(term)]).keys()
            response = [{'id': i, 'value': result} for i, result in enumerate(results)]
            response = simplejson.dumps(response)
            self.response.out.write(response)

def main():
    application = webapp.WSGIApplication([
            ('/.*', MainHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
