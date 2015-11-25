import csv, sqlite3

conn = sqlite3.connect("krak.db")
conn.text_factory = str
cur = conn.cursor()
l = cur.execute("select name from sqlite_master where type = 'table';")
print("This is tables list: %s" % l)
with open('krak_items_07.csv', 'rb') as infile:
    dr = csv.DictReader(infile, delimiter=',')
    to_DB = [(i['company_name'], i['company_site_url'], i['short_description'], i['address'], i['phone'], i['phone_type'], i['gen_description'], i['description_headers'], i['description_paragraphs'], i['tags'], i['category']) for i in dr]
    cur.executemany("INSERT INTO companies_table (company_name, company_site_url, short_description, address, phone, phone_type, gen_description, description_headers, description_paragraphs, tags, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_DB)
    conn.commit()
