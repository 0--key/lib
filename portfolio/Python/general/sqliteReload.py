import sqlite3

"""
Updates sqlite3 table with changed file's content
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


def get_cat_tree():
    """
    Extracts categories relations out from DB
    {'first_category': {'child':
    CREATE TABLE categories (id integer primary key autoincrement, category, parent_id, depth, foreign key (parent_id) references categories(id));
    """
    conn = sqlite3.connect('scraped.db')
    cur = conn.cursor()
    cur.execute('SELECT category FROM products_var_data LIMIT 5000')
    raw_categories = cur.fetchall()
    #print set(raw_categories), len(set(raw_categories)), raw_categories, len(raw_categories)
    for i in set(raw_categories):
        categories = i[0].split('/')[1:]
        depth = 1
        p_id = 1
        for j in categories:
            j = j.replace(';', '')
            # does this category exists already:
            cur.execute('SELECT id FROM categories_01 WHERE depth=? \
            AND category=?', (depth, buffer(j)))
            n = cur.fetchone()
            if n:  # skip insertion
                p_id = n[0]
                depth = depth + 1
                continue
            else:
                print j
                #
                cur.execute('INSERT INTO categories_01(category, \
                parent_id, depth) VALUES (?,?,?)', (buffer(j), p_id, depth))
                print (buffer(j), p_id, depth)
                p_id = cur.lastrowid
                depth = depth + 1
                conn.commit()
    conn.close()
