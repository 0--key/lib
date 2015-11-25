import logging
from google.appengine.api import datastore_types
from google.appengine.ext import db
from models import Company, Description, City
from google.appengine.api import memcache

# this function extract an unique words out from raw list:
def pure_unique(raw_list):
    if len(raw_list)>1:
        unique = []
        for s in raw_list:
            if s.strip(',.:-;').lower() not in unique and len(s.strip(',.:-;'))>2:
                unique.append(s.strip(',.:-;').lower())
    else:
        unique = raw_list.strip(',.:-;')
    return unique

unique_cities_list = []

def unique_cities(l):
    query_str = ["SELECT * FROM Company LIMIT 500 OFFSET 0", "SELECT * FROM Company LIMIT 500 OFFSET 500", "SELECT * FROM Company LIMIT 500 OFFSET 1000"]
    for j in query_str:
        companies = db.GqlQuery(j)
        for i in companies:
            if i.city in l:
                logging.info("This is not unique")
            else:
                l.append(i.city)
    return l

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


# lets create an united transformation function to companies data processing:
def post_import_transformations(input_dict, instance, bulkload_state_copy):
    # company name no need any conversion
    # but lets extract fractions out there:
    instance['company_n_fractions'] = input_dict['company_name'].split()
    # company site url will be:
    if "site unknown" in input_dict['company_site_url']: instance['company_site_url']="http://example.com"
    # short descripion not need in any changes
    # lets extract an unique words out there:
    if input_dict['short_description'] and input_dict['short_description'] != 'Not specified':
        sh_d_raw_list = input_dict['short_description'].split()
        instance['sh_d_fractions'] = pure_unique(sh_d_raw_list)
        logging.info('Short description words extraction')
    else:
        instance['sh_d_fractions'] = ['',]
    # now get a phone numbers:
    if input_dict['phone'].split(',')>1:
        result = []
        for i in input_dict['phone'].split(','):
            if '\n' in i: break
            else: result.append(i)
        instance['phone'] = result
    # phone types cleaning:
    if '\n' in input_dict['phone_type']:
        instance['phone_type'] = ''
    # general description processing:
    if instance['gen_description']:
        dirty_g_d = db.Text(input_dict['gen_description'])
        clean_g_d = dirty_g_d.replace('###', ' ')
        instance['gen_description'] = db.Text(clean_g_d)
        gen_d_raw_list = clean_g_d.split()
        instance['gen_d_fractions'] = pure_unique(gen_d_raw_list)
        logging.info('Gen description cleanizing')
    else:
        instance['gen_descripton'] = 'Not specified'
        instance['gen_d_fractions'] = ['',]
    # this is detail description headers, description itself and its unique content:
    if '###' in instance['description_headers']:
        instance['description_headers'] = input_dict['description_headers'].split('###')
    else:
        instance['description_headers'] = [input_dict['description_headers'],]
    if instance['description_paragraph']:
        dirty_d_p = db.Text(input_dict['description_paragraphs'])
        clean_d_p = dirty_d_p.replace('###', ' ')
        instance['description_paragraph'] = db.Text(clean_d_p)
        description_word_raw_list = clean_d_p.split()
        instance['description_p_fractions'] = pure_unique(description_word_raw_list)
        logging.info('Description and its headers cleanizing')
    else:
        instance['description_p_fractions'] = ['',]
    # seems tags not need any conversion???
    # may be to lower???
    if input_dict['tags']: instance['tags'] = input_dict['tags'].lower().split('###')
    else: instance['tags'] = ['Not specified else',]
    # category:
    if input_dict['category']: instance['category'] = input_dict['category'].lower().split(',')
    # full postal address seems totally clear
    # extract postal code, city and its fractions out them:
    if input_dict['address']:
        for j in input_dict['address'].split(','):
            try:
                code = int(j[1:6])
                break
            except:
                continue
        instance['postal_code'] = code
        instance['city'] = ' '.join(input_dict['address'].split(',')[-1].lstrip().split()[1:])
        instance['city_fractions'] = list(instance['city'].split())
        logging.info('postal code: %r', code)
        logging.info('city: %r', instance['city'])
    else:
        instance['address'] = 'Unknown'
        instance['postal_code'] = 1234
        instance['city'] = 'Not specified'
        instance['city_fractions'] = ['Not specified',]
        logging.info('Address not specified')
    # this is a static part out db Europe and Denmark right now
    instance['country'] = u'Denmark'
    instance['continent'] = u'Europe'
    return instance

def description_processing(input_dict, instance, bulkload_state_copy):
    #try:
    if input_dict['address'] == '': input_dict['address'] = 'Address not specified'
    q = db.GqlQuery("SELECT * FROM Company WHERE company_name = :1 AND address = :2", input_dict['company_name'], input_dict['address'])
    # q = db.GqlQuery(query)
    for i in q:
        instance['company'] = i.key()
        if len(input_dict['description_headers'].split('###'))>1:
            instance['headers'] = input_dict['description_headers'].split('###')
        if len(input_dict['description_paragraphs'].split('###'))>1:
            # lets purge all repeating textual fractions:
            # lets check is the chunks identical:
            paragraph_chunks = []
            k = 0
            for j in input_dict['description_paragraphs'].split('###'):
                if j != paragraph_chunks: paragraph_chunks.append(j)
            for l in paragraph_chunks:
                # now purge all repeating sentences out there:
                chunk_sentences = []
                for m in l.split('. '):
                    if m != chunk_sentences: chunk_sentences.append(m)
            instance['paragraph'] = '. '.join(chunk_sentences)
        
    return instance

