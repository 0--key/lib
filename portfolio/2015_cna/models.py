class NewsArticle():
    """Article about some new event
    """

    def __init__(self):
        self.id = 0
        self.c_time = ''  # when the article been published
        self.headline = ''
        self.summary = ''
        self.img_url = ''
        self.url = ''
        self.origin = ''  # the news' source
        self.keywords = []  # list of keywords

    def insert(self, cursor):
        """Inserts data into DB.news
        and returns inserted id
        """
        return True


class DataSource():
    """ Source of data
    """

    def __init__(self, **kwargs):
        self.name = str(kwargs['name'])
        self.url = kwargs['url']

    def smart_insert(self, conn):
        """Inserts or pick up the id in/from to DB.sources
        """
        cursor = conn.cursor()
        cursor.execute("""SELECT id FROM sources WHERE s_name=%s;""",
                       (self.name, ))
        s_id = cursor.fetchone()
        if s_id:  # this name exists in DB
            return int(s_id[0])
        else:
            cursor.execute("""INSERT INTO sources (s_name, s_url)
            VALUES (%s, %s);""", (self.name, self.url))
            cursor.execute("""SELECT LASTVAL();""")
            s_id = int(cursor.fetchone()[0])
            conn.commit()
            return s_id
