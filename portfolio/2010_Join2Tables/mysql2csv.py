#!/usr/bin/python

# This script input MySQL table and output it's csv version

import sys
import MySQLdb

# only root can do this!
conn = MySQLdb.connect(host = "localhost", user = "root", passwd ="V1qs1i#q!", db = "j_t_t")
cursor = conn.cursor ()

# set up variables:
outfile = 'result_finish.csv'
# if full path is non obvious - /var/lib/mysql/<DB_name>/result.csv
terminator = ','
closer = '"'
new_line = '\n'

# let's Jazz!

cursor.execute ("""SELECT * INTO OUTFILE %s FIELDS TERMINATED BY %s OPTIONALLY ENCLOSED BY %s LINES TERMINATED BY %s FROM Giga_T""", (outfile, terminator, closer, new_line))

print "Job done!"    

cursor.close ()
conn.close ()

