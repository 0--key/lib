import unittest
import psycopg2

from settings import pg_host, pg_db, pg_user, pg_password


class TestAppMethods(unittest.TestCase):

    conn_string = \
            "dbname='%s' user='%s' host='%s' password='%s'" % \
            (pg_db, pg_user, pg_host, pg_password)

    def test_pg_connection(self):
        #
        conn = psycopg2.connect(self.conn_string)
        self.assertTrue(conn)


    def test_source_table_insertion(self):
        # able to insert unique values only:
        name = 'Bing'
        url = 'http://bing.com'
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO sources (s_name, s_url)
            VALUES (%s, %s);""", (name, url))
        cursor.execute("""SELECT LASTVAL();""")
        s_id = int(cursor.fetchone()[0])  # success
        # Second attempt with the same data
        try:
            cursor.execute("""INSERT INTO sources (s_name, s_url)
            VALUES (%s, %s);""", (name, url))
            self.IntegrityTest = False
        except:
            self.IntegrityTest = True
        #
        conn.commit()
        conn.close()
        # 6 7
        self.assertTrue(s_id)
        self.assertTrue(self.IntegrityTest)


if __name__ == '__main__':
    unittest.main()
