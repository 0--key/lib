#!/usr/bin/python

import sys
import MySQLdb
import time
import string
from mod_python import apache
now = time.gmtime()
displaytime = time.strftime("%A %d %B %Y, %X",now)

conn = MySQLdb.connect (host = "localhost",
                           user = "jose",
                           passwd ="5t0len",
                           db = "join_two_tables")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
str = "server version:", row[0]

# Let's do the html-body of our table:

top = '<html>\n\
<head>\n\
<meta content="text/html; charset=utf-8"\n\
http-equiv="Content-Type">\n\
<title></title>\n\
</head>\n\
'

body_hat = '<body>\n\
<table style="text-align: left; width: 100%;" border="1" cellpadding="0"\n\
cellspacing="0">\n\
<tbody>\n\
<tr>\n\
<th style="text-align: center; vertical-align: middle; width: 5%;">C_name<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 5%;">State<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 5%;">LATA<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 20%;">NITR<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 20%;">NiTR<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 20%;">nNITR<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 20%;">nNiTR<br>\n\
</th>\n\
<th style="text-align: center; vertical-align: middle; width: 5%;">NPANxx<br>\n\
</th>\n\
</tr>\n\
'
body_bottom = '</tbody>\n\
</table>\n\
<br>\n\
</body>\n\
</html>'

# let's do MySQL query and select first row from big table:

cursor.execute ("select * from big_table limit 100")
# create main data array:
rows = cursor.fetchall ()

# Create debug output helpers:
s = string.Template('$that' )
t = string.Template('$this has $variable related rows in small table' )


num_rows = cursor.rowcount
middle = ''

for row in rows:
    # we wanna know how rows in small tables are referenced to this company
    cursor.execute ("""select * from small_table where id=%s""", row[0])
    small_rows = cursor.fetchall ()
    num_small_rows = cursor.rowcount
    # this is begining of output block
    string = ''
    middle = middle + '<tr>'
    for j in range (7):
        st = s.substitute(that=row[j])
        string = string + '\n<td style="text-align: center; vertical-align: middle;">' + st + '</td>'
    # we output referenced data from small table into eight column:
    string = string + '\n<td style="text-align: center; vertical-align: middle;">'
    for s_row in small_rows:
        st = s.substitute(that=s_row[1])
        string = string + st + '<br>'
    string = string + '</td>'
    middle = middle + string + '</tr>'
    # end of string

debug_string = t.safe_substitute(this=row[0], variable=num_small_rows)
page = top + body_hat + middle + debug_string + body_bottom

cursor.close ()
conn.close ()

def index(req):
	return page; #"Test successful", displaytime, raw_table;



