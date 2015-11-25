import MySQLdb
import logging
import datetime
import sendgrid
from flask import render_template, session
from twilio.rest import TwilioRestClient
from settings import users, db_password, db_name
from settings import TEST_EMAIL_FROM as faxMailFrom
from settings import ACCOUNT_SID as account
from settings import AUTH_TOKEN as token
from settings import TEST_PhN as PhN
from pdfGen import composePDF_PO


logging.basicConfig(filename='logs/func.log', level=logging.DEBUG)


def get_user_id(nick):
    """Initial auth function"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT id FROM authors WHERE nickname=%s""",
                    (nick, ))
    UserID = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return UserID


def setActiveTab(session_a_tab):
    """Determines what tab should be open initially"""
    a_tab = {'orders': True, 'p_agg': False, 'suppliers': False,
             'invoices': False, 'hold': False}  # <-- default value
    if session_a_tab == 'supplier':
        a_tab.update({
            'orders': False, 'p_agg': False, 'suppliers': True,
            'invoices': False, 'hold': False})
    elif session_a_tab == 'p_agg':
        a_tab.update({
            'orders': False, 'p_agg': True, 'suppliers': False,
            'invoices': False, 'hold': False})
    elif session_a_tab == 'invoices':
        a_tab.update({
            'orders': False, 'p_agg': False, 'suppliers': False,
            'invoices': True, 'hold': False})
    elif session_a_tab == 'hold':
        a_tab.update({
            'orders': False, 'p_agg': False, 'suppliers': False,
            'invoices': False, 'hold': True})
    return a_tab


def fetch_pending_orders_data():
    """Extracts data about orders and their products compositon"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT * FROM orders WHERE magento_time >= (CURDATE() -
        INTERVAL 3 DAY) ORDER BY status ASC, magento_time DESC""")
    o_raw_dataset = MySQL_c.fetchall()  # it's list of tuples
    o_dataset = []  # orders empty list
    pii_data = []  # products in order empty list
    for o_raw_data in o_raw_dataset:
        (o_id, mag_id, c_id, sh_id, sh_ph_id,
         mag_time, tS, status) = o_raw_data
        #
        MySQL_c.execute(
            """SELECT customer_name FROM customers WHERE id=%s""", (c_id,))
        c_name = MySQL_c.fetchone()[0]
        # lets calculate the total sum at each order:
        MySQL_c.execute("""SELECT SUM(price * qty) FROM order_composition \
        WHERE order_id=%s""", (o_id,))
        total_s = MySQL_c.fetchone()[0]
        o_composition = []
        MySQL_c.execute("""SELECT product_id, price, qty FROM \
        order_composition WHERE order_id=%s ORDER BY qty DESC""", (o_id,))
        product_in_order_raw_data = MySQL_c.fetchall()
        for (product_id, p_price, qty) in product_in_order_raw_data:
            MySQL_c.execute("""SELECT item_name, sku FROM products WHERE \
            id=%s""", (product_id,))
            (p_name, sku) = MySQL_c.fetchone()
            p_details = {'sku': sku, 'p_name': p_name[:35],
                         'price': p_price, 'qty': qty}
            o_composition.append(p_details)
            if status == 'pending':  # <--- exclude revocated orders and its
                # products out from further processing
                pii_data_row = (sku, p_name[:35], o_id, mag_id, p_price, qty)
                pii_data.append(pii_data_row)
        #
        if status == 'pending':
            pending = True
        else:
            pending = False
        o_data = {
        'id': o_id, 'm_id': mag_id, 'customer': c_name, 'address': sh_id,
        'phone': sh_ph_id, 'time': mag_time, 'stamp': tS,
        'o_c': o_composition, 't_sum': total_s, 'pending': pending}
        o_dataset.append((o_data))
    db.commit()
    db.close()
    return o_dataset, pii_data


def fetch_products_data(product_list):
    """Converts a raw product array into aggregated by similar SKU
    list of dictionaries which might be convenient to pass directly
    to the Jinja2"""
    aggregator = {}  # it should be a dictionary with SKUs as keys
    for (sku, p_name, o_id, mag_id, p_price, qty) in product_list:
        if sku in aggregator:  # this product was aggregated already
            (orders_list, p_name, old_sigma) = aggregator.get(sku)
        else:  # this is a new product
            orders_list = []
            old_sigma = 0
        orders_list.append((mag_id, p_price, qty))
        aggregator.update({sku: (orders_list, p_name, old_sigma + qty)})
    # all rows are iterated already and products was aggregated by their SKU
    # lets convert aggregator from dictionary into list of dictionaries:
    output_list = []
    for j, k in aggregator.iteritems():
        # j - key (sku), k - a tuple of associated values
        # add suppliers into output dictionary
        supp_dataset = getSuppliers(j)
        pInActPail = getPrInOpenPail()
        incProducts = getIncludedProducts()  # <-- already included into
        if j not in set(incProducts + pInActPail):  # pending invoice
            output_list.append({  # + actual pail
                'sku': j, 'order_orig': k[0], 'product': k[1], 'sigma': k[2],
                'suppliers': supp_dataset})
    newlist = sorted(output_list, key=lambda k: k['sigma'], reverse=True)
    return newlist


def fetch_invoices_data(iStatus):
    """Yields dataset about purchase orders accordingly its status"""
    out_list = []
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    if iStatus == 'pending':
        MySQL_c.execute(
            """SELECT id, author_id, supplier_id, initilized FROM invoices
            WHERE initilized IS NOT NULL AND sent IS NULL ORDER BY initilized
            DESC""")
    if iStatus == 'sent':
        MySQL_c.execute(
            """SELECT id, author_id, supplier_id, initilized, sent,
            s_author_id FROM invoices WHERE initilized IS NOT NULL AND
            sent IS NOT NULL ORDER BY sent DESC""")
    open_invoices_raw_dataset = MySQL_c.fetchall()  # it's list of tuples
    if open_invoices_raw_dataset:
        for i in open_invoices_raw_dataset:
            if iStatus == 'pending':
                (invoice_id, invoice_author_id, supplier_id, i_date) = i
            #
            if iStatus == 'sent':
                (invoice_id, invoice_author_id, supplier_id, i_date, s_date,
                 s_author_id) = i
                sent_author = getAuthor(s_author_id)
            invoice_author = getAuthor(invoice_author_id)
            supplierData = getSupplierData(supplier_id)
            MySQL_c.execute(
                """SELECT id, product_id, price, original_order_price, qty,
                author_id, appended FROM invoice_composition WHERE
                invoice_id=%s AND removed IS NULL ORDER BY appended DESC""",
                (invoice_id,))
            productsInInvoice = MySQL_c.fetchall()
            productIIdata = []
            i_sigma = 0
            i_err = False
            for j in productsInInvoice:
                (piID, product_id, price, original_order_price,
                 qty, pIauthor_id, a_date) = j
                pIauthor = getAuthor(pIauthor_id)
                (sku, p_name) = getProduct(product_id)
                k = "{0:.2f}".format((1 - price / original_order_price)
                                     * 100)  # <- correct
                if k[0] == '-':  # benefit check up
                    p_err = True
                    i_err = True
                else:
                    p_err = False
                i_sigma = i_sigma + price * qty
                sigma = price * qty
                PIIDataSet = ({'author': pIauthor, 'product': p_name,
                               'sku': sku, 'price': price, 'pErr': p_err,
                               'o_oprice': original_order_price, 'k': k,
                               'qty': qty, 'a_date': a_date, 'sigma': sigma,
                               'piID': piID})
                productIIdata.append(PIIDataSet)
            if i_sigma > 0:  # <-- exclude out all blank POs
                if iStatus == 'pending':
                    out_list.append({
                        'i_author': invoice_author, 's_d': supplierData,
                        'p_data': productIIdata, 'i_id': invoice_id,
                        'i_date': i_date, 'sigma': i_sigma, 'iErr': i_err})
                if iStatus == 'sent':
                    out_list.append({
                        'i_author': invoice_author, 's_d': supplierData,
                        'p_data': productIIdata, 'i_id': invoice_id,
                        'i_date': i_date, 'sigma': i_sigma, 'iErr': i_err,
                        's_date': s_date, 's_author': sent_author})
    else:  # there are no any purchase order case
        out_list = None
    db.commit()
    db.close()
    p_invoices_tab_data = out_list
    return p_invoices_tab_data


def fetch_suppliers_data():
    """Generates suppliers data array"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id, supplier_name, address_id, contact_id, author_id,
        inserted FROM suppliers ORDER BY inserted DESC""")
    suppliers_dataset = MySQL_c.fetchall()  # it's list of tuples
    supp_tab_data = []
    for (s_id, s_name, address_id, contact_id,
        author_id, inserted) in suppliers_dataset:
        MySQL_c.execute(
            """SELECT line1, city, province, zip, country FROM addresses
            WHERE id=%s""", (address_id,))
        (address_line, city, province, ZIP, country) = MySQL_c.fetchone()
        MySQL_c.execute(
            """SELECT first_name, last_name, email, preference, phone_id,
            fax_id, author_id from clerks WHERE id=%s""", (contact_id,))
        (first_name, last_name, email, preference, phone_id, fax_id,
         author_id) = MySQL_c.fetchone()
        supp_tab_data.append(
            {'s_id': s_id, 's_name': s_name, 'address_line': address_line,
             'city': city, 'province': province, 'zip': ZIP,
             'country': country, 'first_name': first_name,
             'last_name': last_name, 'email': email,
             'preference': preference, 'phone': getPhoneNum(phone_id),
             'fax': getFaxNum(fax_id),
             'author': getAuthor(author_id), 'inserted': inserted})
    db.commit()
    db.close()
    return supp_tab_data


def suppDataCheck(form_data):
    """Pick up and check up input data"""
    raw_data = {}  # a single dictionary
    iDkeys = [
        'supplier', 'line1', 'city', 'province', 'zip',
        'firstname', 'lastname', 'email', 'phone', 'fax',
        'preference']
    for i in iDkeys:
        raw_data.update({i: form_data[i]})
    pure_data = sanitize(raw_data)
    pure_data['country'] = 'Australia'  # it is a tap
    supplier = pure_data['supplier'].title()
    check_up = False
    if 's_id' in form_data:  # this is update case
        pure_data.update({'s_id': form_data['s_id']})
        logging.debug('This is update case!!!')
        check_up = 'update'
    else:
        if supplier:
            db = MySQLdb.connect(
                passwd=db_password, db=db_name, user='orsys')
            MySQL_c = db.cursor()
            MySQL_c.execute(
                """SELECT id FROM suppliers WHERE supplier_name=%s""",
                (supplier,))
            if MySQL_c.fetchone():  # this supplier is already exists in DB
                check_up = 'known'
            else:
                check_up = 'new'
            db.commit()
            db.close()
    return (pure_data, check_up)


def suppDataInsert(pure_data, userID):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    # input data array
    supplier = pure_data['supplier'].title()
    line = pure_data['line1'].title()
    city = pure_data['city'].title()
    province = pure_data['province'].title()
    ZIP = pure_data['zip']
    country = pure_data['country'].title()
    first_name = pure_data['firstname'].title()
    last_name = pure_data['lastname'].title()
    email = pure_data['email']
    phone = pure_data['phone']
    fax = pure_data['fax']
    preference = pure_data['preference']
    # revealed data -->
    address_id = getAddressID(line, city, province, ZIP, country, userID)
    phone_id = getPhoneID(phone, userID)
    fax_id = getFaxID(fax, userID)
    clerk_id = getClerkID(
        first_name, last_name, email, preference, phone_id, fax_id, userID)
    if 's_id' in pure_data:  # update case
        MySQL_c.execute(
            """UPDATE suppliers SET supplier_name=%s,
            address_id=%s, contact_id=%s, author_id=%s
            WHERE id=%s""", (supplier, address_id, clerk_id, userID,
                             pure_data['s_id']))
    else:  # insertion itself -->
        MySQL_c.execute(
            """INSERT INTO suppliers (supplier_name, address_id,
            contact_id, author_id) VALUES (%s, %s, %s, %s)""",
            (supplier, address_id, clerk_id, userID))
    db.commit()
    db.close()
    return True


def suppDataUpdate(pure_data, userID):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    #
    supplier = pure_data['supplier'].title()
    line = pure_data['line1'].title()
    city = pure_data['city'].title()
    province = pure_data['province'].title()
    ZIP = pure_data['zip']
    country = pure_data['country'].title()
    first_name = pure_data['firstname'].title()
    last_name = pure_data['lastname'].title()
    email = pure_data['email']
    phone = pure_data['phone']
    fax = pure_data['fax']
    preference = pure_data['preference']
    # revealed data -->
    address_id = getAddressID(line, city, province, ZIP, country, userID)
    phone_id = getPhoneID(phone, userID)
    fax_id = getFaxID(fax, userID)
    clerk_id = getClerkID(
        first_name, last_name, email, preference, phone_id, fax_id, userID)

    MySQL_c.execute(
            """UPDATE suppliers SET supplier_name=%s,
            address_id=%s, contact_id=%s, author_id=%s
            WHERE id=%s""", (supplier, address_id, clerk_id, userID,
                             pure_data['s_id']))
    logging.debug('This is suppDataUpdate case @@')
    logging.debug('This is suppDataUpdate case %s, %s, %s, %s, %s, %s, %s' % (
    first_name, last_name, email, preference, phone_id, fax_id, userID))
    db.commit()
    db.close()
    return True


def getAddressID(line, city, province, ZIP, country, userID):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id FROM addresses WHERE line1=%s AND city=%s AND
        province=%s AND zip=%s AND country=%s""",
        (line, city, province, ZIP, country))
    addressCheck = MySQL_c.fetchone()
    if addressCheck:
        addressID = addressCheck[0]
    else:
        #logging.debug("%s, %s, %s, %s, %s" %
                      #(line, city, province, ZIP, country, userID))
        MySQL_c.execute(
            """INSERT INTO addresses (line1, city, province, zip,
            country) VALUES (%s, %s, %s, %s, %s)""",
            (line, city, province, ZIP, country))
        addressID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return addressID


def getClerkID(firstname, lastname, email, preference, phone_id,
               fax_id, userID):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id, preference FROM clerks WHERE first_name=%s AND
        last_name=%s AND email=%s AND phone_id=%s AND fax_id=%s""",
        (firstname, lastname, email, phone_id, fax_id))
    clerkCheck = MySQL_c.fetchone()
    if clerkCheck:
        clerkID = clerkCheck[0]
        old_pref = clerkCheck[1]
        if old_pref != preference:
            logging.debug('This is preference update case @@')
            MySQL_c.execute("""UPDATE clerks SET preference=%s WHERE id=%s""",
                            (preference, clerkID))
    else:
        MySQL_c.execute(
            """INSERT INTO clerks (first_name, last_name, email, preference,
            phone_id, fax_id, author_id) VALUES
            (%s, %s, %s, %s, %s, %s, %s)""",
            (firstname, lastname, email, preference, phone_id, fax_id, userID))
        clerkID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return clerkID


def getPhoneID(phoneNum, userID):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    pN = phoneNum.replace(' ', '').replace('-', '')  # <--
    MySQL_c.execute(
        """SELECT id FROM phones WHERE phone_num=%s""", (pN,))
    phoneCheck = MySQL_c.fetchone()
    if phoneCheck:  # existing already
        phID = phoneCheck[0]
    else:  # the new one
        MySQL_c.execute(
            """INSERT INTO phones (phone_num, author_id) VALUES (%s, %s)""",
            (pN, userID))
        phID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return phID


def getFaxID(fax, userID):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    faxN = fax.replace(' ', '').replace('-', '')  # <--primitive normalization
    MySQL_c.execute(
        """SELECT id FROM faxes WHERE fax_num=%s""", (faxN,))
    faxCheck = MySQL_c.fetchone()
    if faxCheck:  # existing already
        faxID = faxCheck[0]
    else:  # the new one
        MySQL_c.execute(
            """INSERT INTO faxes (fax_num, author_id) VALUES (%s, %s)""",
            (faxN, userID))
        faxID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return faxID


def sanitize(dictionary):
    """Iterate and sanitaze eachone item value in the dict"""
    pure_data_dict = {}
    for i in dictionary:
        if dictionary[i]:  # it's not empty
            # this is sanitize function itself
            pure_data_dict.update({i: dictionary[i].replace("'", '')})
        else:
            pure_data_dict.update({i: ''})
    return pure_data_dict


def checkProduct(form_data):
    """Sanitize and check up user input"""
    pure_data = sanitize(form_data)
    supplier_id = pure_data['supplier']
    sku = pure_data['sku']
    price = pure_data['price']
    o_oprice = pure_data['o_oprice']
    sigma = pure_data['sigma']
    if supplier_id and sku and price and sigma:
        check_up = True
    else:
        check_up = False
    try:  # price input validation
        float(price)
    except ValueError:
        check_up = False
    prod_properties = {
        'sku': sku, 'price': price, 'qty': sigma,
        'supplier_id': supplier_id, 'o_oprice': o_oprice}
    return (prod_properties, check_up)


def getInvoiceID(supplierID, authorID):
    """Check up 'not sent' invoice for particular supplier, if it is
    not exists yet - create one"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id FROM invoices WHERE initilized IS NOT NULL AND
        sent IS NULL AND supplier_id=%s""", (supplierID,))
    invoiceCheck = MySQL_c.fetchone()
    if invoiceCheck:  # does it exists already
        invoiceID = invoiceCheck[0]
    else:
        initTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        MySQL_c.execute(
            """INSERT INTO invoices (author_id, supplier_id, initilized)
            VALUES (%s, %s, %s)""", (authorID, supplierID, initTime))
        invoiceID = MySQL_c.lastrowid
    db.commit()
    db.close()
    return invoiceID


def appendProduct(prod_properties, userID):
    """Move products from aggregated tab onto pending invoices one"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    logging.debug("This is output from appendProduct")
    logging.debug(prod_properties)
    (sku, price, qty, supplier_id, o_oprice) = (
        prod_properties['sku'], prod_properties['price'],
        prod_properties['qty'], prod_properties['supplier_id'],
        prod_properties['o_oprice'])
    invoiceID = getInvoiceID(supplier_id, userID)
    productID = getProductID(sku)
    #
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """INSERT INTO invoice_composition (invoice_id, product_id,
        price, original_order_price, qty, author_id) VALUES
        (%s, %s, %s, %s, %s, %s)""",
        (invoiceID, productID, price, o_oprice, qty, userID))
    db.commit()
    db.close()
    if len(getIncludedProducts()) == 1:  # it's a first product in the batch
        newBatchID = genNewBatch(userID)
    return True


def removeProduct(r_id, piI_id):
    """Move aggProduct out from purchase order"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    removeTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    MySQL_c.execute(
        """UPDATE invoice_composition SET removed=%s, remover_id=%s
        WHERE id=%s""", (removeTime, r_id, piI_id))
    db.commit()
    db.close()
    if len(getIncludedProducts()) == 0:  # it's a last product in the batch
        closeBatch(removeTime)
    return True


def getSuppliers(sku):
    """Temporary solving sku--supplier association issue
    which should be corrected when DB will filled by real data"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT id, supplier_name FROM suppliers""")
    supp_dataset = MySQL_c.fetchall()  # it's list of tuples
    db.commit()
    db.close()
    return supp_dataset


def getProductSKU(product_id):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT sku FROM products WHERE id=%s""", (product_id,))
    sku = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return sku


def getProductID(sku):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT id FROM products WHERE sku=%s""", (sku,))
    productID = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return productID


def getIncludedProducts():
    """List of SKU products included already into pending invoices"""
    incProductsList = []
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT id FROM invoices WHERE initilized IS NOT NULL AND
        sent IS NULL""")
    open_invoices = MySQL_c.fetchall()  # it's list of tuples
    if open_invoices:
        for i in open_invoices:
            MySQL_c.execute(
                """SELECT product_id FROM invoice_composition WHERE
                invoice_id=%s AND removed IS NULL""", (i[0],))
            products_ids = MySQL_c.fetchall()
            if products_ids:
                for j in products_ids:
                    incProductsList.append(getProductSKU(j[0]))
    db.commit()
    db.close()
    return incProductsList


def getSupplierData(s_id):
    """Get all data about supplier by their id"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT supplier_name, address_id, contact_id FROM
    suppliers WHERE id=%s""", (s_id,))
    (supplier_name, address_id, contact_id) = MySQL_c.fetchone()
    db.commit()
    db.close()
    s_data = {
        'name': supplier_name, 'address': getAddress(address_id),
        'contact': getClerk(contact_id), 'id': s_id}
    return s_data


def getClerk(c_id):
    """Returns all data about contact person"""
    c_data = {}
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT first_name, last_name, email, preference, phone_id,
        fax_id FROM clerks WHERE id=%s""", (c_id,))
    (c_data['first_name'], c_data['last_name'], c_data['email'],
     c_data['preference'], phone_id, fax_id) = MySQL_c.fetchone()
    c_data['phone'] = getPhoneNum(phone_id)
    c_data['fax'] = getFaxNum(fax_id)
    db.commit()
    db.close()
    return c_data


def getFaxNum(fax_id):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT fax_num FROM faxes WHERE id=%s""", (fax_id,))
    faxN = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return faxN


def getPhoneNum(phone_id):
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT phone_num FROM phones WHERE id=%s""", (phone_id,))
    phoneN = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return phoneN


def getAddress(a_id):
    """Fetches address properties"""
    a_data = {}
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT line1, city, province, zip, country FROM addresses
        WHERE id=%s""", (a_id,))
    (a_data['line1'], a_data['city'], a_data['province'], a_data['zip'],
     a_data['country']) = MySQL_c.fetchone()
    db.commit()
    db.close()
    return a_data


def getAuthor(a_id):
    """Get author nickname by his id"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT nickname FROM authors WHERE id=%s""",
        (a_id,))
    author_nick = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return author_nick


def getProduct(p_id):
    """ Get product's sku and name by its id """
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT sku, item_name FROM products WHERE id=%s""",
        (p_id,))
    p_data = MySQL_c.fetchone()
    db.commit()
    db.close()
    return p_data


def revocateOrder(o_id, username):
    """Toggle pending and revocated order"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT status FROM orders WHERE id=%s""",
        (o_id,))
    o_status = MySQL_c.fetchone()[0]
    if o_status == 'pending':
        new_status = 'revocated'
        # conditionaly exclude products from this order into PP
    elif o_status == 'revocated':
        new_status = 'pending'
        #
        # conditionaly include products from this order into PP
        incProdInPP(o_id, username)
    toggleTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.debug('%s toggle %s order status from %s to %s at %s' %
                  (username, o_id, o_status, new_status, toggleTime))
    MySQL_c.execute("""UPDATE orders SET status=%s WHERE id=%s""",
        (new_status, o_id))
    db.commit()
    db.close()
    return True


def sendPurchaseOrder(iID, uName):
    """send PO to supplier accordiongly with preference method"""
    state = False
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT supplier_id FROM invoices WHERE id=%s""",
                    (iID,))
    sID = MySQL_c.fetchone()[0]
    MySQL_c.execute("""SELECT contact_id FROM suppliers WHERE id=%s""",
                    (sID,))
    cID = MySQL_c.fetchone()[0]
    clerk = getClerk(cID)
    poData = getPO_Data(iID)
    prSet = getPrSet(iID)
    poData['total'] = getTotalPOsum(prSet)
    # Pure emailing
    if clerk['preference'] == 'email':
        sg = sendgrid.SendGridClient('jaketay', 'lemonlime')
        pdf = composePDF_PO(poData, prSet)
        lSub = ("New Purchase Order #%s" % poData['No'])
        letter = render_template(
            'leemunroe.htm', poData=poData, prSet=prSet)
        pdfFilename = "Purchase_order_%s.pdf" % poData['No']
        #
        message = sendgrid.Mail()
        message.add_to(clerk['email'])
        message.set_subject(lSub)
        message.set_html(letter)
        message.set_from('do-not-reply@fastfresh.com.au')
        message.add_attachment_stream(pdfFilename, pdf)
        status, msg = sg.send(message)
        #
        if status == 200:
            state = True
            logging.debug('Email with PO No%s was sent by %s to %s %s' %
                          (iID, uName, clerk['first_name'],
                           clerk['last_name']))
        else:
            logging.debug('Email with PO No%s NOT sent to %s' %
                          (iID, uName))
    # Fax emailing case
    if clerk['preference'] == 'fax':
        sg = sendgrid.SendGridClient('jaketay', 'lemonlime')
        lSub = ("New Purchase Order #%s" % poData['No'])
        #tXt = "<h1>%s</h1>" % lSub
        htmlFilename = "Purchase_order_%s.html" % poData['No']
        faxMail = clerk['fax'] + '@fax.utbox.net'
        letter = render_template(
            'faxmail.htm', poData=poData, prSet=prSet)
        #
        #
        message = sendgrid.Mail()
        message.add_to(faxMail)
        message.set_subject(lSub)
        #message.set_html(tXt)
        message.set_from(faxMailFrom)
        message.add_attachment_stream(htmlFilename, letter)
        status, msg = sg.send(message)
        #
        if status == 200:
            state = True
            logging.debug('FaxMail with PO No%s was sent by %s to %s %s' %
                          (iID, uName, clerk['first_name'],
                           clerk['last_name']))
        else:
            logging.debug('FaxMail with PO No%s NOT sent to %s' %
                          (iID, uName))
    # SMS emailing case
    if clerk['preference'] == 'sms':
        client = TwilioRestClient(account, token)
        sms = genSMS(poData, prSet)
        nOrPhN = checkNo(clerk['phone'])
        if nOrPhN:
            message = client.messages.create(
                to=nOrPhN,  # "+61417617909",
                from_=PhN,
                body=sms)
            state = True
            logging.debug('SMS %s with PO No%s was sent to %s' %
                              (message.sid, iID, uName))
    if state:  # PO was success successfuly sent
        markAsSent(iID, uName)
    db.commit()
    db.close()
    return True


def checkNo(rawPhNum):
    """Convert Australian phone numbers into international view"""
    if len(rawPhNum) == 10:
        phNo = "+61" + rawPhNum[1:]
    else:
        logging.debug('%s NOT VALID for Twilio SMS purposes' % rawPhNum)
        phNo = False
    return phNo


def getPrSet(iID):
    """Returns products in purchase order dictionary list"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """SELECT product_id, price, qty FROM invoice_composition WHERE
        invoice_id=%s AND removed IS NULL ORDER BY qty DESC""", (iID,))
    poPrDataSet = MySQL_c.fetchall()
    prSet = []
    for k, i in enumerate(poPrDataSet, start=1):
        pr = {}
        product_id, price, qty = i
        pr['No'] = k
        pr['price'] = price
        pr['qty'] = qty
        pr['sku'], pr['name'] = getProduct(product_id)
        pr['subtotal'] = float(price) * int(qty)
        prSet.append(pr)
    db.commit()
    db.close()
    return prSet


def getPO_Data(iID):
    """Retrieve purchase order data accordingly its ID"""
    poData = {}
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT author_id, supplier_id, sent, s_author_id
    FROM invoices WHERE id=%s""", (iID,))
    author_id, supplier_id, sent, s_author_id = MySQL_c.fetchone()
    db.commit()
    db.close()
    poData['buyer'] = session['username']
    poData['email'] = users.get(session['username']).get('email')
    poData['phoneNo'] = users.get(session['username']).get('phoneNo')
    poData['No'] = int(iID) * 3 + 140121  # PO No obfuscator
    return poData


def markAsSent(iID, uName):
    """Mark this PO as already sent to supplier"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    sTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uID = get_user_id(uName)
    MySQL_c.execute("""UPDATE invoices SET sent=%s, s_author_id=%s
    WHERE id=%s""", (sTime, uID, iID))
    # and
    db.commit()
    db.close()
    return True


def genSMS(poData, prSet):
    """Generates SMS text body"""
    header = "\nPurchase Order\n#%s\nBuyer: %s\nPhone: %s\n\n" % (
        poData['No'],
        poData['buyer'],
        poData['phoneNo']
    )
    body = ''
    for i, j in enumerate(prSet, start=1):
        prRow = "%s | %s | %s | %s\n%s\n\n" % (
            i, j['sku'], j['qty'], j['price'], j['name'][:15])
        body = body + prRow
    footer = "\n\nTHANK YOU!"
    sms = header + body + footer
    return sms


def getTotalPOsum(prSet):
    """Calculates PO total cost"""
    Ts = 0
    for i in prSet:
        Ts = Ts + i['subtotal']
    return Ts


def getMagID(oID):
    """Retrieve out Magento ID"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT magento_id FROM orders WHERE id=%s""", (oID,))
    mID = MySQL_c.fetchone()[0]
    db.commit()
    db.close()
    return mID

# Pail related functions --->


def get_product_Set(order_batch_id, product_id):
    """Render data about product origin in the pail"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    prSet = []
    #
    MySQL_c.execute(
        """SELECT order_id FROM orders_in_batch WHERE batch_id=%s""",
        (order_batch_id,))
    orders_In_batch = MySQL_c.fetchall()
    for i in orders_In_batch:
        MySQL_c.execute("""SELECT price, qty FROM order_composition
        WHERE order_id=%s AND product_id=%s""", (i[0], product_id))
        try:
            price, qty = MySQL_c.fetchone()
            mID = getMagID(i[0])
            prRow = {'order_id': mID, 'price': price, 'qty': qty}
            prSet.append(prRow)
        except TypeError:
            pass
    db.commit()
    db.close()
    return prSet


def fetch_held_products():
    """Retrieve data about products in the pail"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute("""SELECT id, order_batch_id, product_id, author_id,
    i_date, resolver_id, r_time FROM products_in_pail ORDER BY id DESC""")
    pail_products_dataset = MySQL_c.fetchall()
    #
    HpDataSet = []
    for i in pail_products_dataset:
        (pip_id, order_batch_id, product_id, author_id, i_date, resolver_id,
         r_time) = i
        prSet = get_product_Set(order_batch_id, product_id)
        sku, p_name = getProduct(product_id)
        auth_nick = getAuthor(author_id)
        resolver = ''
        if resolver_id:
            resolver = getAuthor(resolver_id)
        p_row = {'id': pip_id, 'i_date': i_date, 'author': auth_nick, 'sku':
                 sku, 'name': p_name, 'pData': prSet, 'resolver': resolver,
                 'r_date': r_time}
        HpDataSet.append(p_row)
    db.commit()
    db.close()
    return HpDataSet


def grasp_product(p_sku, userID):
    """Absorbs product into the pail"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    pID = getProductID(p_sku)
    iDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Retrieving an acutal open batch there:
    MySQL_c.execute("""SELECT id FROM order_batches WHERE r_time IS NULL ORDER
    BY id DESC LIMIT 1""")
    try:
        bID = MySQL_c.fetchone()[0]
    except TypeError:
        bID = genNewBatch(userID)
    MySQL_c.execute(
        """INSERT INTO products_in_pail (order_batch_id, product_id, author_id,
        i_date) VALUES (%s, %s, %s, %s)""", (bID, pID, userID, iDate))
    db.commit()
    db.close()
    return True


def eliminate_product(p_id, uID):
    """Push product out from the pail"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    #MySQL_c.execute("""UPDATE ppail SET r_time=%s WHERE p_id=%s AND""")
    db.commit()
    db.close()
    return True


def throw_product(p_id, uID):
    """Incorporate product back into aggregated products tab"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    r_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    MySQL_c.execute("""UPDATE products_in_pail SET resolver_id=%s, r_time=%s
    WHERE id=%s""", (uID, r_time, p_id))
    numO_PrInLastBatch = len(getPrInOpenPail()) - 1  # last was deleted ^
    #logging.debug('There are %s in the PAIL' % numO_PrInLastBatch)
    if numO_PrInLastBatch == 0:  # it's a last product in the batch
        closeBatch(r_time)
    db.commit()
    db.close()
    return True


def move_to_pail(p_id):
    """Move product into pail"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    #MySQL_c.execute("""SELECT ppail WHERE p_id=%s AND""")
    db.commit()
    db.close()
    return False


def getPrInOpenPail():
    """List of SKU products included already into last open pail"""
    skuList = []
    if check_last_batch():
        db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
        MySQL_c = db.cursor()
        MySQL_c.execute("""SELECT id FROM order_batches WHERE r_time IS NULL\
        ORDER BY id DESC LIMIT 1""")
        lastBatchID = MySQL_c.fetchone()[0]
        MySQL_c.execute("""SELECT product_id FROM products_in_pail WHERE
        order_batch_id=%s AND r_time IS NULL""", (lastBatchID,))
        productsInLastBatchIDs = MySQL_c.fetchall()
        for i in productsInLastBatchIDs:
            sku, p_name = getProduct(i[0])
            skuList.append(sku)
        db.commit()
        db.close()
    return skuList


def check_last_batch():
    """Is the last batch open?"""
    checkUp = False
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
    """SELECT r_time FROM order_batches ORDER BY id DESC LIMIT 1"""
        )
    try:
        resolved = MySQL_c.fetchone()[0]
    except TypeError:
        resolved = True
    if not resolved:
        checkUp = True
    db.commit()
    db.close()
    return checkUp


def checkOTLock():
    """Does orders tab was locked?"""
    checkUp = False
    PO_sku_list = getIncludedProducts()
    if PO_sku_list:  # or product from the actual batch is in pail
        checkUp = True
    elif check_last_batch():
        checkUp = True
    return checkUp


def genNewBatch(aID):
    """Creates a new pile of orders"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    iTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    MySQL_c.execute(
        """INSERT INTO order_batches (author_id, i_time) VALUES (%s, %s)""",
        (aID, iTime))
    newBatchID = MySQL_c.lastrowid
    MySQL_c.execute("""SELECT id FROM orders WHERE magento_time >= (CURDATE()
    - INTERVAL 3 DAY) AND status = 'pending'""")
    o_id_dataset = MySQL_c.fetchall()
    # lets fill orders in the batch table:
    for i in o_id_dataset:
        MySQL_c.execute("""INSERT INTO orders_in_batch (batch_id, order_id)
        VALUES (%s, %s)""", (newBatchID, i[0]))
    db.commit()
    db.close()
    return newBatchID


def closeBatch(rTime):
    """Close up a last pile of orders"""
    # only open right now thus it will be reconfigured later
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """UPDATE order_batches SET r_time=%s WHERE r_time IS NULL ORDER BY
        id DESC LIMIT 1""", (rTime,)
    )
    db.commit()
    db.close()
    return True


def incProdInPP(o_id, username):
    """Include product into product pail"""
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    MySQL_c.execute(
        """UPDATE order_batches SET r_time=%s WHERE r_time IS NULL ORDER BY
        id DESC LIMIT 1""", (rTime,)
    )
    db.commit()
    db.close()
    return True
