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

class MainHandler(webapp.RequestHandler):
    def get(self):
        developer = str(self.request.get('developer'))
        concept = str(self.request.get('concept')).lower()
        category = str(self.request.get('category')).lower()
        taxonomy = str(self.request.get('taxonomy')).lower()
        result = []
        warnings = ''
        if concept == '' and category == '' and taxonomy == '':
            warnings = 'You need to specify the searching words'
            category = taxonomy = concept = num_entities = '' 
        else:        
            if concept != '' and category != '' and taxonomy != '':
                query_str = "SELECT * FROM Placebo WHERE concept_words = '%s' AND category_words = '%s' AND taxonomy_words = '%s'" % (concept, category, taxonomy)
            # for pairs
            if concept == '' and category == '' and taxonomy != '':
                query_str = "SELECT * FROM Placebo WHERE taxonomy_words = '%s' AND developer = '%s'" % (taxonomy, developer)
            if concept == '' and category != '' and taxonomy == '':
                query_str = "SELECT * FROM Placebo WHERE category_words = '%s' AND developer = '%s'" % (category, developer)
            if concept != '' and category == '' and taxonomy == '':
                query_str = "SELECT * FROM Placebo WHERE concept_words = '%s' AND developer = '%s'" % (concept, developer)
            # and single absence too:
            if concept == '' and category != '' and taxonomy != '':
                query_str = "SELECT * FROM Placebo WHERE category_words = '%s' AND taxonomy_words = '%s' AND developer = '%s'" % (category, taxonomy, developer)
            if category == '' and concept != '' and taxonomy != '':
                query_str = "SELECT * FROM Placebo WHERE concept_words = '%s' AND taxonomy_words = '%s' AND developer = '%s'" % (concept, taxonomy, developer)
            if taxonomy == '' and category != '' and concept != '':
                query_str = "SELECT * FROM Placebo WHERE concept_words = '%s' AND category_words = '%s' AND developer = '%s'" % (concept, category, developer)
            query_str = query_str + " ORDER BY OID ASC"
            placebo = db.GqlQuery (query_str)
            num_entities = int(placebo.count())
            result.append(placebo)
            
        template_values = {'placebo':result,'concept':concept,'warnings':warnings,
                           'category':category,'taxonomy':taxonomy,'num_entities':num_entities}
        doRender(self,'helper.htm',template_values)


def main():
    application = webapp.WSGIApplication([
            ('/.*', MainHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
