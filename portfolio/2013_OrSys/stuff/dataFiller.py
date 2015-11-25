import sqlite3
import csv
import MySQLdb
from settings import db_password, db_name

conn = sqlite3.connect('orders.db')
SQLite3_c = conn.cursor()
db = MySQLdb.connect(passwd=db_password, db=db_name, user='orsys')
MySQL_c = db.cursor()

# order_details filler:
MySQL_c.execute("""SELECT id FROM orders""")
ids = MySQL_c.fetchall()
p_data = []
for i in ids:
    print i
    #
    p_data.append((i[0], "pending"))
MySQL_c.executemany(
    """INSERT INTO order_details (order_id, status) \
    VALUES (%s, %s)""", p_data)

# final operators:
db.commit()
db.close()
conn.commit()
conn.close()
