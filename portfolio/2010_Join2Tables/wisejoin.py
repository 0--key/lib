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
                           db = "j_t_t")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
str = "server version:", row[0]

cursor.execute ("select * from companies")
InitData = cursor.fetchall ()

rel_rows3 = rel_rows5 = l1 = l2 = l3 = l4 = l5 = 0
for row in InitData:
    #l = len (str (i))
    l = row[2]
    OCN = row[1]
    NPANXX = row[0]
    STATE = row[3]
    
    if l<10:
        l1 = l1+1
    elif l<100:
        l2 = l2+1
    elif l<1000:
        l3 = l3+1
        # this main block when LATA is 3-digit
        cursor.execute ("""select * from statistics where OCN=%s and LATA=%s""",
                        (OCN, l))
        rel_rows3 = rel_rows3+cursor.rowcount
        #print rel_rows3
        if rel_rows3>0:
            rel_row = cursor.fetchall ()
            for r_row in rel_row:
                cursor.execute ("""insert into Giga_T values
                (%s,%s,%s,%s,%s,%s,%s,%s)""",
                                (OCN, NPANXX, STATE, l, float(r_row[3]),
                                 float(r_row[4]), float(r_row[5]),
                                 float(r_row[6])))
    elif l<10000:
        l4 = l4+1
    elif l<100000:
        l5 = l5+1
        # this is helper when LATA is 5-digit
        l = int (l/100)
        cursor.execute ("""select * from statistics where OCN=%s and LATA=%s""",
                        (OCN, l))
        rel_rows5 = rel_rows5+cursor.rowcount
        if rel_rows5>0:
            rel_row = cursor.fetchall ()
            for r_row in rel_row:
                cursor.execute ("""insert into Giga_T values
                (%s,%s,%s,%s,%s,%s,%s,%s)""",
                                (OCN, NPANXX, STATE, l, float(r_row[3]),
                                 float(r_row[4]), float(r_row[5]),
                                 float(r_row[6])))


print str, l1, l2, l3, l4, l5, rel_rows3, rel_rows5

cursor.close ()
conn.close ()
