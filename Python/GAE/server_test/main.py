import json
from decimal import Decimal
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


def quremo(a, b):
    """Primitive ariphmetic calculations"""
    qu = Decimal(b) / Decimal(a)
    re = int(qu)
    mo = Decimal(b) % Decimal(a)
    return str(qu), str(re), str(mo)


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.write('Hello world!<p>\
        This is the index page.</p>')


class DivideHandler(webapp.RequestHandler):
    def get(self, divisor, raw_dividend):
        dividend = self.request.query_string.split('=')[1]
        (q, r, m) = quremo(divisor, dividend)
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
