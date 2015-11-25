import os
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from google.appengine.api import users
from google.appengine.ext import db
from models import Placebo

def next_id(ID):
    ID_chunks = ID.split('.')
    count_chunks = len(ID_chunks)
    last_chunk = ID_chunks[count_chunks - 1]
    ID_chunks[count_chunks - 1] = str(int(last_chunk)+1)
    ID = '.'.join(ID_chunks)
    return ID

def doRender(handler, tname='helper.xml', values={}):
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
        result = []
        if self.request.get('id')!='':
            # now extract last number from id
            ID = str(self.request.get('id'))
            # extract display name
            query_dName = "SELECT * FROM Placebo WHERE OID = '%s' LIMIT 1" % (ID)
            first_string = db.GqlQuery (query_dName)
            for j in first_string:
                dName = j.concept.capitalize()
            for i in range(3):
                  query_str = "SELECT * FROM Placebo WHERE OID = '%s'" % (ID)
                  placebo = db.GqlQuery (query_str)
                  result.append(placebo)
                  #print ID
                  ID = next_id(ID)
#        else:
#            query_str = "SELECT * FROM Placebo LIMIT 20"
#            placebo = db.GqlQuery (query_str)
#            result.append(placebo)

        ID = str(self.request.get('id'))
        template_values = {'placebo':result, 'ID':ID, 'dName':dName}
        doRender(self,'helper.xml',template_values)

def main():
    application = webapp.WSGIApplication([
            ('/.*', MainHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
