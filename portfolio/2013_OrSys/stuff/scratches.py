# MySQL unneccesary functions:


def insertNewSupplier(form_data, userID):  # @@
    """All necessary convertations, validations and insertions there"""
    raw_data = {}  # a single dictionary
    # lets prepare data to processing
    iDkeys = [
        'supplier', 'line1', 'city', 'province', 'zip',
        'firstname', 'lastname', 'email', 'phone', 'fax'
        ]  # later add preference & etc.
    for i in iDkeys:
        raw_data.update({i: form_data[i]})
    # now raw_data filled
    # input data validation
    (data_valid, ins_data, msg) = inputDataValidator(raw_data)
    msg.update({'ins': False})
    if data_valid:  # --<insertion case
        db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
        MySQL_c = db.cursor()
        supplier = ins_data['supplier']
        address_id = ins_data['address_id']
        contact_id = ins_data['contact_id']
        try:
            MySQL_c.execute(
                """INSERT INTO suppliers (supplier_name, address_id,
                contact_id) VALUES (%s, %s, %s)""",
                (supplier, address_id, contact_id))
            msg.update({'ins': True})
        except:
            logging.info('Insertions failed, supplier=%s,\
            address_id=%s, contact_id=%s' % (supplier, address_id, contact_id))
            #
        db.commit()
        db.close()
    else:
        logging.info('Data not valid for insertion: %s' % (msg,))
    return msg


def inputDataValidator(raw_data_dict):  # @@
    msg = {}
    data_for_insertion = {}
    val_result = ()
    db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
    MySQL_c = db.cursor()
    data_dict = sanitizer(raw_data_dict)  # sanitize it
    # check up supplier
    supplier = data_dict['supplier']
    if supplier:
        MySQL_c.execute(
            """SELECT id FROM suppliers WHERE supplier_name=%s""",
            (supplier,))
        if MySQL_c.fetchone():  # this supplier is already exists in DB
            msg.update({'s_name': 'already exists'})  # <-- update case
            data_for_insertion.update({'supplier': supplier})
            val_result = False
        else:  # <-- insert case
            data_for_insertion.update({'supplier': supplier})
            val_result = True
    else:  # <-- empty field case:
        msg.update({'s_name': 'empty'})
        val_result = False
    data_for_insertion.update({'address_id': 1})  # address_id})
    data_for_insertion.update({'contact_id': 1})  # clerk_id})
    result = (val_result, data_for_insertion, msg)
    db.commit()
    db.close()
    return result


# order_composition filler:

SQLite3_c.execute(
    'SELECT Order_Number, Item_SKU, Item_Price, Item_Qty_Ordered \
    FROM orders')
raw_item_data = SQLite3_c.fetchall()

prep_data = []
for i in raw_item_data:
    (o_number, sku, price, qty) = i
    MySQL_c.execute("""SELECT id FROM orders WHERE magento_id=%s""",
                    (o_number,))
    o_id = int(MySQL_c.fetchone()[0])
    MySQL_c.execute("""SELECT id FROM products WHERE sku=%s""",
                    (sku,))
    p_id = int(MySQL_c.fetchone()[0])
    prep_data.append((o_id, p_id, price.split('$')[-1], qty))
print prep_data
MySQL_c.executemany(
    """ INSERT INTO order_composition (order_id, product_id,
    price, qty) VALUES (%s, %s, %s, %s)""", prep_data)


# this is orders table filler
SQLite3_c.execute(
    'select Order_Number,Order_Date, Customer_Name, \
    Shipping_Phone_Number, Shipping_Street from orders'
    )
raw_orders = set(SQLite3_c.fetchall())
orders = list(raw_orders)
prepared_data = []
for i in orders:
    (m_num, m_date, c_name, p_num, street) = i
    # lets convert date into MySQL format:
    raw_date, raw_time = m_date.split()
    time = raw_time + ':00'
    date = '-'.join(raw_date.split('/')[::-1])
    m_date = date + ' ' + time
    # lets find foreing keys:
    MySQL_c.execute("""SELECT id FROM customers WHERE customer_name=%s""",
                    (c_name,))
    customer_id = int(MySQL_c.fetchone()[0])
    MySQL_c.execute("""SELECT id FROM phones WHERE phone_num=%s""",
                    (p_num,))
    phone_id = int(MySQL_c.fetchone()[0])
    MySQL_c.execute("""SELECT id FROM addresses WHERE line1=%s""",
                    (street,))
    address_id = int(MySQL_c.fetchone()[0])
    print (
        m_num, m_date, c_name, customer_id, p_num, phone_id,
        street, address_id
        )
    prepared_data.append(
        (int(m_num), customer_id, address_id, phone_id, m_date))
MySQL_c.executemany(
    """INSERT INTO orders (magento_id, customer_id, shipping_address_id,
    shipping_phone_id, magento_time) VALUES (%s, %s, %s, %s, %s)""",
    prepared_data)

#?
def phoneFiller(self, raw_phone):
    # extract significant parts:
    if len(raw_phone) == 8: # it's a bold phone number


# Filling addresses table:
SQLite3_c.execute(
    """SELECT Shipping_Street, Shipping_Zip, Shipping_City, Shipping_State_Name, \
    Shipping_Country_Name FROM orders"""
    )
address_data = set(SQLite3_c.fetchall())
MySQL_c.executemany(
    """INSERT INTO addresses (line1, zip, city, province, country)
    VALUES (%s, %s, %s,%s, %s)""", address_data
    )

# - #


# typical MySQL interaction: filling products table
SQLite3_c.execute('SELECT Item_Name, Item_SKU from orders')
product_data = SQLite3_c.fetchall()
inserted_sku = []
prepared_data = []
for i in product_data:
    if i[1] not in inserted_sku:
        prepared_data.append((None, i[0], i[1]))
        inserted_sku.append(i[1])
print prepared_data
MySQL_c.executemany(
    """INSERT INTO products (id, item_name, sku) VALUES (%s, %s, %s)""",
    prepared_data)

# - #


# this snippet fills data from csv into SQLite3
csv_file = open('orders.csv', 'rU')
o = csv.reader(csv_file)
for i in o:
    c.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
    ?)', tuple(i))

# - #

    # check up address
    line1 = data_dict['line1']  # -- four variables there
    city = data_dict['city']
    province = data_dict['province']
    postal_zip = data_dict['zip']
    #
    if line1:
        MySQL_c.execute(
            """SELECT id FROM addresses WHERE line1=%s""",
            (line1,))
        if MySQL_c.fetchone():  # this address is well known
            address_id = MySQL_c.fetchone()[0]
        else:  # the new one
            msg.update({'line1': 'new insertion'})
            MySQL_c.execute(
                """INSERT INTO addresses (line1, city, province, zip) 
                VALUES (%s, %s, %s, %s)""",
                (line1, city, province, postal_zip))
            address_id = MySQL_c.lastrowid
    else:  # empty line1 case
        msg.update({'line1': 'empty'})
        MySQL_c.execute(
            """INSERT INTO addresses (line1, city, province, zip)
            VALUES (%s, %s, %s, %s)""",
            (line1, city, province, postal_zip))
        address_id = MySQL_c.lastrowid
    # check up clerk
    c_first_name = data_dict['firstname']
    c_last_name = data_dict['lastname']
    email = data_dict['email']
    phone = data_dict['phone']
    fax = data_dict['fax']
    # the main condition:
    if (email or phone) or (email and phone):
        # check it up
        MySQL_c.execute(
            """SELECT id FROM clerks WHERE email=%s""",
            (email,))
        clerk_id = MySQL_c.fetchone()
        if clerk_id:  # this email is well known already
            #
        else:  # it's a new email
            #
    else:  # it's a deviation
        msg.update({'contact': 'unknown communication method'})


# - #
