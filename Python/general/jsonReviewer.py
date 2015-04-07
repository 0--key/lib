import sys, logging
import sqlite3, json

"""
Few general statistical methods are there:
 - unique;
 - similar by criteria
"""
# Configure logging for degug purposes
logger = logging.getLogger('json_processing_app')
hdlr = logging.FileHandler('/var/tmp/json_processing_app.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
# Lets generate json out from sqlite3 DB with 29k unique items
"""
sqlite> .schema products
CREATE TABLE "products" (id integer primary key autoincrement, name, sku, manufacturer, manuf_url, weight, pack_weight, dimension, description, ingredients, warning, suggested_use);
CREATE INDEX sku_index ON "products"(sku);

sqlite> select count(*) from products;
29676

sqlite> select count(sku) from products;
29676
"""
# Define classes and their methods firstly
class Product():
    """
    product from iherb web store
    """
    def __init__(self, data_row):
        """
        init data table cells fulfillment
        [id, name, sku, manufacturer, manuf_url, weight,
        pack_weight, dimension, description, ingredients,
        warning, suggested_use]
        """
        data_fields = [id, name, sku, manufacturer, manuf_url,
                       weight, pack_weight, dimension, description,
                       ingredients, warning, suggested_use]
        self.id = data_row['id']
        return True
    def __add__():
        return True


# Initially create JSON file with data:

def init_json_file_gen():
    """
    Generates JSON file out from DB
    """
    conn = sqlite3.connect('scraped.db')
    cur = conn.cursor()
    cur.execute('select * from products')
    p_data = cur.fetchall()
    for i in p_data:
        msg = i
        logger.info(msg)
    conn.commit()
    conn.close
    print 'Job done'
    return True
# Define functionalyty in accordion with low RAM consumption
# and allocate json into HD DB

def conc_two_json_files(conn, json1, json2):
    """
    concatenates two json with unique rows only
    by means md5 technology comparison and temporary
    sqlite3 data allocation
    """
    cur = conn.cursor()
    conn.commit()
    output_file_name = "date" + ".json"
    msg = "This is filenames: %s, %s" % (json1, json2)
    logger.info(msg)
    logger.debug('While this is switch')
    return True


def conc_two_json_files_in_memory(json1, json2):
    """
    concatenates two json with unique rows only
    by means md5 technology comparison and temporary
    RAM data allocation
    """
    return True

# functional body is here

if sys.argv[0]:
    if sys.argv[1] == '-r':
        # in-memory data temporary allocation
        pass
    if sys.argv[1] == '-d':
        # hard way for big data analyse
        # and unique data temporary storing into SQLite3 tables
        # for further processing
        conn = sqlite3.connect('tmp_data.db')
        conc_two_json_files(conn, sys.argv[2], sys.argv[3])
        conn.close()
    if sys.argv[1] == '-i':
        # initial data fulfillment
        init_json_file_gen()
        
