import os, logging
import wsgiref.handlers
from google.appengine.ext import webapp
from review import get_unique_cities


class MainHandler(webapp.RequestHandler):
    def get(self):
        unique_cities=get_unique_cities()
        self.response.out.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n') 
        logging.info("Now it is rendered")
        for city in unique_cities:
            self.response.out.write('\t<url>\n\t\t<loc>http://ovivogae.appspot.com/vikarbureau/'+city+'</loc>\n\t\t<lastmod>2012-04-29</lastmod>\n\t\t<changefreq>monthly</changefreq>\n\t</url>\n')
        self.response.out.write('</urlset>')

application = webapp.WSGIApplication([('/.*', MainHandler),], debug=True)
