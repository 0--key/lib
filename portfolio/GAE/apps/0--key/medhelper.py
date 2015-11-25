import os
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from google.appengine.api import users
from google.appengine.ext import db
from models import Placebo


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
        doRender(self,'helper.htm')

class CSVUploadForm(webapp.RequestHandler):
    def get(self):
        path = self.request.path
        if doRender(self,path) :
            return 
        doRender(self,'csv_upload.htm')

class CSVHandler(webapp.RequestHandler):
    def post(self):
        # this is the main block of code
        # lets jazz
        # first - catch the passed file:
        if self.request.get("csv"):
            j = 0
            new_data_source = self.request.get("csv")
            # next step is split this file into lines:
            data_chunks = new_data_source.splitlines()
            # and deeper split everyone into words:
            for line in data_chunks:
                data = line.split(";")
                # lets put chunks into datastore
                row = Placebo()
                try: row.developer = data[0]
                except IndexError:
#                    logging.info(data[0]+str(j))
                    pass
                try: row.OID = data[1]
                except IndexError:
#                    logging.info(data[1]+str(j))
                    pass
                try: row.concept = data[2]
                except IndexError:
#                    logging.info(data[2]+str(j))
                    pass
                try: row.category = data[3]
                except IndexError:
#                    logging.info(data[3]+str(j))
                    pass
                try: row.taxonomy = data[4]
                except IndexError:
#                    logging.info(data[4]+str(j))
                    pass
                try: row.taxonomy_version = data[5]
                except IndexError:
#                    logging.info(data[5]+str(j))
                    pass
                try: row.code = data[6]
                except IndexError:
#                    logging.info(data[6]+str(j))
                    pass
                try: row.descriptor = data[7]
                except IndexError:
#                    logging.info(data[7]+str(j))
                    pass
                row.put()
                j = j+1
                logging.info('Putting '+str(j)+' rows')
#                if j == 1904:
 #                   logging.info(data[1])
#      greeting.avatar = db.Blob(avatar)
#      greeting.put()
        self.redirect('/nurce/')


def main():
    application = webapp.WSGIApplication([
            ('/nurce/uploadform', CSVUploadForm),
            ('/nurce/uploadcsv', CSVHandler),
            ('/.*', MainHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
