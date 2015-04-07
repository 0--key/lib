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
logger.setLevel(logging.INFO)
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


# Define functionalyty in accordion with low RAM consumption
# and allocate json into HD DB

def conc_two_json_files(conn, json1, json2):
    """
    concatenates two json with unique rows only
    by means md5 technology comparison
    """
    cur = conn.cursor()
    conn.commit()
    output_file_name = "date" + ".json"
    logger.info('While this is just chatty')
    return True


def __init__(self):
    print 'I have launched!'
    return True

print "I'm here!"

# functional body is here

if sys.argv[0]:
    conn = sqlite3.connect('scraped.db')
    conc_two_json_files(conn, 'file1', 'file2')
