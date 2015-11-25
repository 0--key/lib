-- this file generates initial data structue inside orsys database --

/* primary data section
all tables below are primary */

CREATE TABLE IF NOT EXISTS addresses (-- filled already
       id INT NOT NULL AUTO_INCREMENT,
       line1 TINYTEXT,
       line2 TINYTEXT,
       line3 TINYTEXT,
       city VARCHAR(25),
       province VARCHAR(25),
       zip VARCHAR(8),
       country VARCHAR(25),
       FULLTEXT ( line1, line2, line3 ),
       PRIMARY KEY (id)
       );

CREATE TABLE IF NOT EXISTS phones -- filled
       ( id INT NOT NULL AUTO_INCREMENT,
       /*pprefix VARCHAR(2),
       phone_number VARCHAR(9),
       ppostfix VARCHAR(4),*/
       phone_num VARCHAR(14),
       PRIMARY KEY (id)
       );

CREATE TABLE IF NOT EXISTS faxes -- filled
       ( id INT NOT NULL AUTO_INCREMENT,
       /*fprefix VARCHAR(2),       
       fax_number INT UNSIGNED,
       fpostfix VARCHAR(4),*/
       fax_num VARCHAR(14),
       PRIMARY KEY (id)
       );

CREATE TABLE IF NOT EXISTS products ( -- filled already
       id INT NOT NULL AUTO_INCREMENT,
       item_name TINYTEXT,
       sku VARCHAR(12),
       FULLTEXT ( sku ),
       PRIMARY KEY (id)
       );

CREATE TABLE IF NOT EXISTS authors 
       ( id INT NOT NULL AUTO_INCREMENT,
       nickname VARCHAR(16),
       user_group ENUM('superuser', 'buyer', 'associate'),
       PRIMARY KEY (id)
       );


/* secondary data tables:
   all tables below have references
   to tables at the top*/

-- subjects:
CREATE TABLE IF NOT EXISTS customers ( -- filled by 5 sample rows +
       id INT NOT NULL AUTO_INCREMENT,
       customer_name VARCHAR(25),
       email VARCHAR(50),
       phone_num INT NOT NULL,
       billing_address_id INT NOT NULL,
       shipping_address_id INT NOT NULL,
       PRIMARY KEY (id),
       CONSTRAINT phone FOREIGN KEY (phone_num) REFERENCES phones (id),
       CONSTRAINT b_address FOREIGN KEY (billing_address_id) REFERENCES addresses (id),
       CONSTRAINT s_address FOREIGN KEY (shipping_address_id) REFERENCES addresses (id)
       );

CREATE TABLE IF NOT EXISTS clerks ( -- might be fill later +
       id INT NOT NULL AUTO_INCREMENT,
       first_name VARCHAR(25),
       last_name VARCHAR(25),
       email VARCHAR(50),
       preference ENUM('sms', 'email', 'fax'),
       phone_id INT NOT NULL,
       fax_id INT NOT NULL,
       PRIMARY KEY (id),
       CONSTRAINT cl_phone FOREIGN KEY (phone_id) REFERENCES phones (id),
       CONSTRAINT fax FOREIGN KEY (fax_id) REFERENCES faxes (id)
       );

CREATE TABLE IF NOT EXISTS suppliers ( -- might be fill later +
       id INT NOT NULL AUTO_INCREMENT,
       supplier_name VARCHAR(25),
       address_id INT NOT NULL,
       contact_id INT NOT NULL,
       PRIMARY KEY (id),
       CONSTRAINT sup_address FOREIGN KEY (address_id) REFERENCES addresses (id),
       CONSTRAINT contact FOREIGN KEY (contact_id) REFERENCES clerks (id)
       );

-- objects:
CREATE TABLE IF NOT EXISTS orders ( -- filled by 6 samples +
       id INT NOT NULL AUTO_INCREMENT,
       magento_id INTEGER UNSIGNED,
       customer_id INT NOT NULL,
       shipping_address_id INT NOT NULL,
       shipping_phone_id INT NOT NULL,
       magento_time DATETIME,
       orsys_timestamp TIMESTAMP,
       PRIMARY KEY (id),
       CONSTRAINT customer FOREIGN KEY (customer_id) REFERENCES customers (id),
       CONSTRAINT address FOREIGN KEY (shipping_address_id) REFERENCES addresses (id),
       CONSTRAINT phone_num FOREIGN KEY (shipping_phone_id) REFERENCES phones (id)
       );

CREATE TABLE IF NOT EXISTS order_composition ( -- +
       id INT NOT NULL AUTO_INCREMENT,
       order_id INT NOT NULL,
       product_id INT NOT NULL,
       price DECIMAL(5,2) UNSIGNED, -- 999.99 migh be enough
       qty SMALLINT UNSIGNED, -- < 65535 items
       PRIMARY KEY (id),
       CONSTRAINT _order FOREIGN KEY (order_id) REFERENCES orders (id),
       CONSTRAINT product FOREIGN KEY (product_id) REFERENCES products (id)
       );

CREATE TABLE IF NOT EXISTS order_details ( -- +
       id INT NOT NULL AUTO_INCREMENT,
       order_id INT NOT NULL,
       status ENUM('pending', 'transitional', 'resolved', 'unknown'),
       status_switch TIMESTAMP,
       PRIMARY KEY (id),
       CONSTRAINT order_d FOREIGN KEY (order_id) REFERENCES orders (id)
       );

CREATE TABLE IF NOT EXISTS invoices ( -- +
       id INT NOT NULL AUTO_INCREMENT,
       author_id INT NOT NULL,
       supplier_id INT NOT NULL,
       resolved TIMESTAMP,
       PRIMARY KEY (id),
       CONSTRAINT auth FOREIGN KEY (author_id) REFERENCES authors (id),
       CONSTRAINT supp FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
       );

CREATE TABLE IF NOT EXISTS invoice_composition ( -- +
       id INT NOT NULL AUTO_INCREMENT,
       invoice_id INT NOT NULL,
       product_id INT NOT NULL,
       price DECIMAL(5,2) UNSIGNED, -- 999.99 migh be enough
       qty SMALLINT UNSIGNED, -- < 65535 items
       PRIMARY KEY (id),
       CONSTRAINT inv FOREIGN KEY (invoice_id) REFERENCES invoices (id),
       CONSTRAINT prod FOREIGN KEY (product_id) REFERENCES products (id)
       );






