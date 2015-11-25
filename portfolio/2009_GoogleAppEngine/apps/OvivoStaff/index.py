import os
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


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

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = self.request.path
        if doRender(self,path) :
            return 
        doRender(self,'index.htm')


application = webapp.WSGIApplication([('/.*', MainHandler),], debug=True)

