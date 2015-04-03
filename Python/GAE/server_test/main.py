import json
import logging
from decimal import Decimal
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import run_wsgi_app
from m.fn import get_quremo

# Web application with primitive arithmetical calculations
# and API for external usage

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.write('Hello world!<p>\
        This is the index page.</p>')


class DivideHandler(webapp.RequestHandler):
    def get(self, divisor, raw_dividend):
        dividend = self.request.query_string.split('=')[1]
        (q, r, m) = get_quremo(divisor, dividend)
        self.response.headers['Content-Type'] = 'application/json'
        obj = {'quotient': q, 'result': r, 'modulus': m}
        self.response.out.write(json.dumps(obj))


application = webapp.WSGIApplication([
    ('/', MainHandler),
    (r'/divide/(.*)/(.*)', DivideHandler)
    ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
