import sqlite3

"""
Updates sqlite table with changed file's content
"""

conn = sqlite3.connect('server/mhn.db')
ds_file = open('scripts/deploy_snort.sh', 'r')
script = ds_file.read()
u = (script,)
conn.execute('UPDATE deploy_scripts SET script=? WHERE id=2', u)
conn.commit()
