import json
import logging
from decimal import Decimal
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Results


def quremo(a, b):
    """Primitive ariphmetic calculations"""
    qu = Decimal(b) / Decimal(a)
    re = int(qu)
    mo = Decimal(b) % Decimal(a)
    logging.info("It's a log")
    return str(qu), str(re), str(mo)


def get_quremo(a, b):
    """Memcache or DataStore interaction implementation
    with aim to avoid server calculations overload"""
    a_key = a + '&' + b  # an unique key for each pair
    cached_result = memcache.get(key=a_key)
    if cached_result is None:
        calc_val = quremo(a, b)
        memcache.add(key=a_key, value=calc_val, time=3600)
        logging.info("Data was cached successfully")
    else:
        calc_val = cached_result
        logging.info("Data was retrieved out from MemCache")
    return calc_val


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
