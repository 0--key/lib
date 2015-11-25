import os
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from google.appengine.api import users
from google.appengine.ext import db
from models import Placebo

def doRender(handler, tname='helper.htm', values={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.isfile(temp):
        return False

    # Make a copy of the dictionary and add the path
    newval = dict(values)
    newval['path'] = handler.request.path
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True

def Extract_Words(raw_string):
    # this function must:
    # split input string into chunks
    # remove all parasitic symbols from every chunk
    # create list of chunks if its lenght > than 2
    raw_chunks = raw_string.split(" ")
    word_list = []
    for raw_word in raw_chunks:
        logging.info('Creating an empty list')
        word = raw_word.replace(' ','')
        word = word.replace('"','')
        word = word.replace(',','')
        word = word.replace(';','')
        word = word.replace('/','')
        word = word.replace(':','')
        if len(word) > 2:
            word = word.lower()
            word_list.append(word)
            logging.info('Append word '+word)
    return word_list
        

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = self.request.path
        if doRender(self,path) :
            return 
        doRender(self,'csv_upload.htm')

class PurgeHandler(webapp.RequestHandler):
    def get(self):
        # lets clear datastore
        clear_query = Placebo.all()
        num_entities = clear_query.count()
        while num_entities > 400:
            clear_query = Placebo.all()
            garbage = clear_query.fetch(400)
            db.delete(garbage)
            num_entities = num_entities - 400
        else:
            db.delete(clear_query)
        self.redirect('/')
        
class CSVHandler(webapp.RequestHandler):
    def post(self):
        # this is the main block of code
        # lets jazz
        # first - catch the passed file:
        if self.request.get("csv"):
            # datastore is clear !
            # let's save new spreadsheet into it
            j = 0
            new_data_source = self.request.get("csv")
            # remove all parasitic symbols from the source
            new_data_clear = new_data_source.replace ('\n', '')
            # next step is to split this Megastring into the lines:
            data_chunks = new_data_clear.splitlines()
            # and deeper split everyone into the words:
            for line in data_chunks:
                line = line.replace ('"', '')
                line = line.replace ('; ', '#%')
                data = line.split(";")
                # lets put chunks into datastore
                row = Placebo()
                row.developer = data[0]
                row.OID = data[1]
                row.concept = data[2]
                row.concept_words = Extract_Words(data[2])
                row.category = data[3]
                row.category_words = Extract_Words(row.category)
                row.taxonomy = data[4]
                row.taxonomy_words = Extract_Words(row.taxonomy)
                row.taxonomy_version = data[5]
                row.code = data[6]
                row.descriptor = data[7].replace ('#%', '; ')
                row.put()
                j = j+1
                logging.info('Putting '+str(j)+' rows')
        self.redirect('/')

def main():
    application = webapp.WSGIApplication([
            ('/uploadadmin/uploadcsv', CSVHandler),
        ('/uploadadmin/purge', PurgeHandler),
            ('/.*', MainHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
