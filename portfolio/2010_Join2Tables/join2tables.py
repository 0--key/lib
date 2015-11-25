#!/usr/bin/python
# this script join two tables in one
# annihilate all foreign keys
# put result data into MySQL table


import sys
import MySQLdb
import string

conn = MySQLdb.connect (host = "localhost",
                           user = "jose",
                           passwd ="5t0len",
                           db = "join_two_tables")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
str = "server version:", row[0]

# let's do MySQL query and select first row from big table:

cursor.execute ("select * from OCNNPANXX")
# create main data array:
# NPANXX data IS unique (!!!)
rows = cursor.fetchall ()


# iterate every row and make relation query to another table
for small_row in rows:
#    print small_row[0], small_row[1]
    # let's create relation query to another table:
    cursor.execute ("""select * from QuikvoipV2 where OCN=%s""", small_row[0])
    tall_rows = cursor.fetchall ()
    rel_rows = cursor.rowcount
#    print "   OCN %s have %s relation" % (small_row[0], rel_rows)
    # let's iterate every related row:
    
    for t_row in tall_rows:
#        print t_row[0], small_row[1], t_row[1], t_row[2], t_row[3], t_row[4], t_row[5],\
 #       t_row[6], type (t_row[4]), t_row[4]+2
        # this is inserting verify data into MySQL table:
        cursor.execute ("""insert into Giga_T values (%s,%s,%s,%s,%s,%s,%s,%s)""",\
                        (t_row[0], small_row[1], t_row[1], t_row[2], float(t_row[3]),\
                         float(t_row[4]), float(t_row[5]), float(t_row[6]))) 
    

cursor.close ()
conn.close ()

