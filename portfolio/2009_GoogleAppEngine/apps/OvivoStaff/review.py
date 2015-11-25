import os, logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import datastore
from google.appengine.ext import db
from models import Company
from google.appengine.api import memcache

def get_companies_data(query_str):
    q = db.GqlQuery(query_str)
    results_number = q.count()
    companies = []
    urls = []
    descriptions = []
    description_words = []
    addresses = []
    postal_codes = []
    phone = []
    phone_type = []
    tags = []
    g_description = []
    g_description_words = []
    description_headers = []
    description_paragraph = []
    description_p_fractions = []
    category = []
    city_fractions = []
    google_map_iframe = []
    unique_cities = get_unique_cities()
    first_letters_list = []
    cities_ordered = get_ordered_cities()
    first_letters_list = get_first_letters_list(unique_cities)
    navbar = search_navbar()
    for i in q:
        companies.append(i.company_name)
        urls.append(i.company_site_url)
        descriptions.append(i.short_description)
        description_words.append(i.sh_d_fractions)
        addresses.append(i.address)
        postal_codes.append(i.postal_code)
        phone.append(i.phone)
        phone_type.append(i.phone_type)
        tags.append(i.tags)
        g_description.append(i.gen_description)
        g_description_words.append(i.gen_d_fractions)
        description_headers.append(i.description_headers)
        description_paragraph.append(i.description_paragraph)
        description_p_fractions.append(i.description_p_fractions)
        category.append(i.category)
        city_fractions.append(i.city_fractions)
        # compound google iframe query:
        address_query = i.address.replace(' ', '+')
        # 725 * 550
        map_query = '<iframe width="300" height="300" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=dk&amp;geocode=&amp;q=' + address_query + '&amp;aq=&amp;sll=q&amp;sspn=q&amp;t=m&amp;ie=UTF8&amp;hq=&amp;hnear=' + address_query + '&amp;z=14&amp;ll=q&amp;output=embed"></iframe>'
        google_map_iframe.append(map_query)
    companies_data = zip(companies, addresses, postal_codes, urls, descriptions, description_words, phone, phone_type, tags, g_description,g_description_words, description_headers, description_paragraph, description_p_fractions, category, city_fractions, google_map_iframe)
    return companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar

def get_unique_cities():
    l = memcache.get(key="unique_cities")
    if l:
        logging.info("Unique cities list exists")
    else:
        l = []
        query_str = ["SELECT * FROM Company LIMIT 500 OFFSET 0", "SELECT * FROM Company LIMIT 500 OFFSET 500", "SELECT * FROM Company LIMIT 500 OFFSET 1000"]
        for j in query_str:
            companies = db.GqlQuery(j)
            for i in companies:
                if i.city in l:
                    logging.info("This is not unique")
                else:
                    l.append(i.city)
        l.sort()
        memcache.set(key="unique_cities", value=l, time=3600)
    return l

def get_unique_tags():
    l = memcache.get(key="unique_tags")
    if l:
        logging.info("Unique tags list exists")
    else:
        l = []
        query_str = ["SELECT * FROM Company LIMIT 500 OFFSET 0", "SELECT * FROM Company LIMIT 500 OFFSET 500", "SELECT * FROM Company LIMIT 500 OFFSET 1000"]
        for j in query_str:
            companies = db.GqlQuery(j)
            for i in companies:
                for j in i.tags:
                    if j!="Not specified else":
                        if ',' in j:
                            e = j.split(',')
                            for k in e:
                                if k.strip() in l:
                                    logging.info('This is trailing tag and it is not unique')
                                else:
                                    l.append(k.strip())
                        else:
                            if j in l:
                                logging.info("This is not unique")
                            else:
                                l.append(j)
        l.sort()
        memcache.set(key="unique_tags", value=l, time=3600)
    return l


def get_first_letters_list(l):
    first_letters_list = []
    for k in l:
        if k[0] not in first_letters_list:
            first_letters_list.append(k[0])
    return first_letters_list

def get_ordered_cities():
    # try to get list with alphabetical cities split
    cities_list = get_unique_cities()
    ordered_cities_list = []
    first_letters_list = get_first_letters_list(cities_list)
    for i in first_letters_list:
        list_fraction = []
        for j in cities_list:
            if j[0]==i:
                list_fraction.append(j)
        ordered_cities_list.append(list_fraction)
    return ordered_cities_list       
    
def search_navbar():
    # create a template search navbar
    menu = ''
    cities = get_unique_cities()
    cities_first_letters = get_first_letters_list(cities)
    cities_ordered = get_ordered_cities()
    for i, j in zip(cities_first_letters,cities_ordered):
        cities_list = ''
        for k in j:
            cities_list = cities_list+'<li><a href="/vikarbureau/'+k+'">'+k+'</a></li>'
            #'<li><a href="review?term='+k+'&search_option=in_cities">'+k+'</a></li>'
        menu = menu+'<li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" href="#">'+i+'<b class="caret"></b></a><ul class="dropdown-menu">'+cities_list+'</ul></li>'
    #navbar = "Hello, World</br>I'm Antony"
    navbar = '<ul class="nav nav-pills">'+menu+'</ul>'
    return navbar

def doRender(handler, tname='index.htm', values={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    newval = dict(values)
    newval['path'] = handler.request.path
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = self.request.path
        if doRender(self,path):
            return
        doRender(self,'index.htm')
        
class ReviewHandler(webapp.RequestHandler):
    def get(self):
        path = self.request.path
        if doRender(self,path):
            logging.ingo('Hi from review!')
            return
        q_term = self.request.get('term').strip()
        q_option = self.request.get('search_option')
        if q_term:
            if q_option=="in_tags":
                query_str = "SELECT * FROM Company WHERE tags='%s'" % q_term.lower()
            if q_option == "in_names":
                query_str = "SELECT * FROM Company WHERE company_n_fractions ='%s'" % q_term.title()
            if q_option == "in_postalcode":
                query_str = "SELECT * FROM Company WHERE postal_code = %s" % int(q_term)
            if q_option == "in_cities":
                query_str = "SELECT * FROM Company WHERE city ='%s'" % q_term.title()
            if q_option == "in_description":
                query_str = "SELECT * FROM Company WHERE description_p_fractions ='%s'" % q_term.lower()
        else:
            query_str = "SELECT * FROM Company LIMIT 25"
        companies_data, results_number, first_letters_list, unique_cities, cities_ordered, navbar = get_companies_data(query_str)
        template_values = {'companies':companies_data, 'Q_term':q_term, 'results_number':results_number, 'cities_first_letters':first_letters_list, 'cities':unique_cities, 'cities_ordered':cities_ordered, 'search_navbar':navbar}
        doRender(self,'review.htm', template_values)

application = webapp.WSGIApplication([('/.*', ReviewHandler),], debug=True)
