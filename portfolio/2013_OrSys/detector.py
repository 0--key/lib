import MySQLdb
import logging
import datetime
from settings import db_password, db_name, MdbUser, MdbPassword, Mdb, MdbIP
from functions import getPhoneID, getFaxID, getAddressID


logging.basicConfig(filename='logs/detector.log', level=logging.DEBUG)
# logger = logging.getLogger(__name__)


def check_new_orders(lastOid):
    """New recent orders check up """
    checkUp = False
    db = MySQLdb.connect(host=MdbIP, user=MdbUser, passwd=MdbPassword, db=Mdb)
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT entity_id FROM sales_flat_order ORDER BY created_at DESC
        LIMIT 1""")
    lastMid = int(MySQL_c.fetchone()[0])
    db.commit()
    db.close()
    if lastMid > lastOid:
        checkUp = True
    return checkUp


def getLastOid():
    """Retrieve last detected order id out from OrSys"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT magento_id FROM orders ORDER BY magento_time DESC LIMIT 1""")
    lastOid = int(MySQL_c.fetchone()[0])
    db.commit()
    db.close()
    return lastOid


def getFreshOrderDataSet(o_id):
    """Retrieve data about order and products inside it"""
    logging.basicConfig(filename='logs/detector.log', level=logging.DEBUG)
    #
    db = MySQLdb.connect(host=MdbIP, user=MdbUser, passwd=MdbPassword, db=Mdb)
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT customer_firstname, customer_lastname, customer_email,
        shipping_address_id, billing_address_id, created_at
        FROM sales_flat_order WHERE entity_id=%s""", (o_id,))
    (customer_firstname, customer_lastname, customer_email,
     shipping_address_id, billing_address_id, mag_time) = MySQL_c.fetchone()
    #
    sh_address = getAddress(shipping_address_id)
    b_address = getAddress(billing_address_id)
    try:
        cName = customer_firstname + ' ' + customer_lastname
    except TypeError:
        cName = 'corrupted'
        logging.debug('This is corrupted custorer name in %s', o_id)
    o_Data = {
        'cName': cName,
        'cEmail': customer_email, 'shAddress': sh_address,
        'bAddress': b_address, 'magTime': mag_time, 'mID': o_id
              }
    MySQL_c.execute(
        """SELECT sku, qty_ordered, price, name FROM sales_flat_order_item
        WHERE order_id=%s""", (o_id))
    productsDataSet = MySQL_c.fetchall()
    db.commit()
    db.close()
    return o_Data, productsDataSet


def getAddress(aID):
    """Retrieve address attributes from remote Magento DB"""
    db = MySQLdb.connect(host=MdbIP, user=MdbUser, passwd=MdbPassword, db=Mdb)
    MySQL_c = db.cursor()
    aA = {}
    MySQL_c.execute(
        """SELECT region, postcode, firstname, lastname, street, city, email,
        telephone, fax FROM sales_flat_order_address WHERE entity_id=%s""",
        (aID,))
    (region, postcode, firstname, lastname, street, city, email, telephone,
     fax) = MySQL_c.fetchone()
    db.commit()
    db.close()
    (aA['region'], aA['postcode'], aA['firstname'], aA['lastname'],
     aA['street'], aA['city'], aA['email'], aA['telephone'], aA['fax']) = (
        region, postcode, firstname, lastname, street, city, email,
        telephone, fax)
    return aA


def insertOrder(o_Data):
    """Accordingly with the definition :-)"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    rTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    shippingAddress = o_Data['shAddress']
    (province, ZIP,
     firstname, lastname,
     street, city,
     email, telephone,
     fax) = (
        shippingAddress['region'], shippingAddress['postcode'],
        shippingAddress['firstname'], shippingAddress['lastname'],
        shippingAddress['street'], shippingAddress['city'],
        shippingAddress['email'], shippingAddress['telephone'],
        shippingAddress['fax']
        )
    country = 'Australia'  # it is a tap
    shAid = getAddressID(street, city, province, ZIP, country, 1)
    shPhid = getPhoneID(telephone, 1)
    c_id = getCustomerID(firstname, lastname, email, shPhid, shAid)
    prepData = (
        o_Data['mID'], c_id, shAid, shPhid,
        o_Data['magTime'], rTime, 'revocated')
    MySQL_c.execute(
        """INSERT INTO orders (magento_id, customer_id, shipping_address_id,
        shipping_phone_id, magento_time, orsys_reg_time, status) VALUES(%s, %s,
        %s, %s, %s, %s, %s)""", prepData)
    o_id = MySQL_c.lastrowid
    db.commit()
    db.close()
    return o_id


def getCustomerID(firstName, lastName, email, shPhid, shAid):
    """Fetches customer id in table customers"""
    logging.basicConfig(filename='logs/detector.log', level=logging.DEBUG)
    # for simplification purposes let
    # shipping address == billing address
    try:
        cName = firstName + ' ' + lastName
    except TypeError:
        cName = 'corrupted'
        logging.debug('This is corrupted getCustomerID name in %s order', o_id)
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id from customers WHERE customer_name=%s AND email=%s""",
        (cName, email))
    try:
        cID = MySQL_c.fetchone()[0]
    except:
        MySQL_c.execute(
            """INSERT INTO customers (customer_name, email, phone_num_id,
            billing_address_id, shipping_address_id)
            VALUES(%s, %s, %s, %s, %s)""",
            (cName, email, shPhid, shAid, shAid))
        cID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return cID


def processOrder(o_id, p_Data):
    """Order products data insertion into OrSys DB"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    for i in p_Data:
        sku, qty_ordered, price, name = i
        pID = getProductID(sku, name)
        MySQL_c.execute(
            """INSERT INTO order_composition (order_id, product_id, price,
            qty) VALUES(%s, %s, %s, %s)""", (o_id, pID, price,
                                             qty_ordered))
    db.commit()
    db.close()
    return True


def getProductID(sku, name):
    """Retrieves product ID by SKU"""
    logging.basicConfig(filename='logs/detector.log', level=logging.DEBUG)
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id FROM products WHERE sku=%s""", (sku,))
    try:
        pID = MySQL_c.fetchone()[0]
        # synonym detection:
        MySQL_c.execute(
            """SELECT item_name FROM products WHERE id=%s""", (pID,))
        itemName = MySQL_c.fetchone()[0]
        if name != itemName:
            msg = "Synonym detecded. Product with id %s have an old \
            name: %s and a new one: %s" % (pID, itemName, name)
            logging.debug(msg)
    except:
        MySQL_c.execute(
            """INSERT INTO products (item_name, sku) VALUES(%s, %s)""",
            (name, sku))
        pID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return pID


# Detector itself:
lastOid = int(getLastOid()) + 1
while check_new_orders(lastOid):  # there is (are) new orders there
    logging.basicConfig(filename='logs/detector.log', level=logging.DEBUG)
    oData, pDataSet = getFreshOrderDataSet(lastOid)
    newOID = insertOrder(oData)
    logging.debug("New order No %s was detected." % (newOID,))
    processOrder(newOID, pDataSet)
    lastOid = lastOid + 1
