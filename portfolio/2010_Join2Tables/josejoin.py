#!/usr/bin/python
# this script for automatic join two tables in one
# create by Anton Kosinov through algorithm by Jose Paz:
# first of all we need to prepare source file
# then import it into MySQL tables
# join its together in to Giga_Table
# and create final csv file with joined data

##############################################
###             USER MANUAl                ###
##############################################

# Remove an old csv files with the new which had names
# ocn-lata-state-rates.csv and npaxx-ocn-lata-state.csv 
# in folder /data in work directory. 

# In terminal run a python script by typing:
# python /home/test1/josejoin.py
# where /home/test/ is a work_directory
# in which are arrange the folder /data and will be
# created a result.csv file 

# After when the job is done and
# if you'll decide to work by the real power tools
# you can utilise MySQL database and its tables,
# which are especially not deleted and ready to use.

import os
import sys
import MySQLdb

# initial settings block
conn = MySQLdb.connect (host = "localhost",
                           user = "jose",
                           passwd ="5t0len",
                           db = "j_t_t_f")
cursor = conn.cursor ()

work_directory = '/home/antony/job/join/'
source_small_table = open \
    (work_directory+'data/ocn-lata-state-rates.csv', 'r')
small_table = open (work_directory+'data/small_table.csv', 'w')
source_big_table = open \
    (work_directory+'data/npanxx-ocn-lata-state.csv', 'r')
big_table = open (work_directory+'data/big_table.csv', 'w')


small_table.truncate()
big_table.truncate()

# create small table only csv source
for line in source_small_table:
    # delete all parasitic symbols
    line = line.replace ('"', '')
    line = line.replace (';;', ';0;')
    small_table.write (line)

source_small_table.close()
small_table.close()


# create big table only csv source
for line in source_big_table:
    # delete all parasitic symbols
    line = line.replace ('"', '')
    line = line.replace (';;', ';0;')
    big_table.write (line)

source_big_table.close()
big_table.close()

# fresh and clear csv files are ready to import into MySQL
# just do it

cursor.execute ("""create table if not exists companies (NPANXX varchar(10), OCN varchar(4), LATA int(5), STATE varchar(2))""")

cursor.execute ("create table if not exists statistics (OCN varchar(4), LATA int(5), STATE varchar(2), BUY_INTRA decimal(6,5), BUY_INTER decimal(6,5), SELL_INTRA decimal(6,5), SELL_INTER decimal(7,6))")

cursor.execute ("create table if not exists Giga_T (OCN varchar(4), NPANXX varchar(10), STATE varchar(2), LATA int(3),  BUY_INTRA decimal(6,5), BUY_INTER decimal(6,5), SELL_INTRA decimal(6,5), SELL_INTER decimal(7,6))")

cursor.execute ("truncate table companies")
cursor.execute ("truncate table statistics")
cursor.execute ("truncate table Giga_T")

# the tables are exists and let's import data
path_csv_small = work_directory+'data/big_table.csv'# miracle, but it inverse!
path_csv_big = work_directory+'data/small_table.csv'
separator = ';'
cursor.execute ("""load data local infile %s into table statistics fields terminated by %s""", (path_csv_big, separator))
cursor.execute ("""load data local infile %s into table companies fields terminated by %s""", (path_csv_small, separator))


# the data are imported - join it in to Giga_T

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

# on finish we transform our data into csv file
# only MySQL root can do this!

# set up variables:
outfile = work_directory+'result.csv'
os.remove(outfile)
# if full path is non obvious it been saved in
# /var/lib/mysql/DB_name/result.csv
terminator = ','
closer = '"'
new_line = '\n'

# let's Jazz!

cursor.execute ("""SELECT * INTO OUTFILE %s FIELDS TERMINATED BY %s OPTIONALLY ENCLOSED BY %s LINES TERMINATED BY %s FROM Giga_T""", (outfile, terminator, closer, new_line))


print "Job done!"    


cursor.close ()
conn.close ()
