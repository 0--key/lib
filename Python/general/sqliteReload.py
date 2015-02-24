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


def get_catalogue():
    """
    Extracts catalogue metadata
    catalogue_data = ({'name': 'cosmetics', 'count': 127, 'depth': 1}, ...)
    """
    conn = sqlite3.connect('scraped.db')
    cur = conn.cursor()
    # Prepare paginator data:
    cur.execute('SELECT category FROM products_var_data')
    raw_categories = cur.fetchall()
    catalogue_data = ()
    for i in raw_categories:
        categories = i[0].split('/')[1:]
        #print cat_list
        d = 0  # deepth counter
        for j in categories:  # fullfill the catalogue tree
            for k in catalogue_data:
                if k['name'] == j:  # this categore is already exists
                    k['count'] = k['count'] + 1
                    break
            new_category = {'name': j, 'depth': d, 'count': 1}
            catalogue_data = catalogue_data + (new_category,)
            d = d + 1
    conn.close()
    return catalogue_data
