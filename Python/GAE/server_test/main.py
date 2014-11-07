from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.write('Hello world!<p>\
        This is the index page.</p>')


class DivideHandler(webapp.RequestHandler):
    def get(self, divisor, raw_dividend):
        dividend = self.request.query_string
        self.response.write('Hello world!\
        This is the quotient page %s, %s' % (divisor, dividend))


application = webapp.WSGIApplication([
    ('/', MainHandler),
    (r'/divide/(.*)/(.*)', DivideHandler)
    ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
