import os
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import blobstore
#import models 
from google.appengine.ext import db
from models import Stuff

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

class FileManager(webapp.RequestHandler):
        def get(self):
            if self.request.get("myfile"):
                way = 'file is saved'
            else: way = 'initial'
            default = str(users.get_current_user())
            doRender(self,'files.htm', {'msg1' : default,
                                        'msg2' : way})

class SaveBlob(webapp.RequestHandler):
    def post(self):
#        default=users.get_current_user()
        if self.request.get('myfile'):
          #  myfile = self.request.get('myfile')
            new_file = Stuff()
           # self.new_file.owner = self.users.get_current_user()
            new_file.pulp = self.request.get('myfile')
            new_file.put()
            way = 'File puts on datastore'
        else: way = 'File is not exists'
        self.redirect("/files/")



class UploadFile(webapp.RequestHandler):
    def get(self):
#        action = self.request.get('action')
        doRender(self,'files_upload.htm', {'msg' : 'This is UploadFile handler :-)',
#                                    'action' : action
                                           })
    

def main():
    application = webapp.WSGIApplication([
            ('/files/UploadFile', UploadFile),
            ('/files/SaveBlob', SaveBlob),
            ('/.*', FileManager)
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
