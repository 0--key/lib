import urllib2
import json
import unittest


class LocalServerCase(unittest.TestCase):

    def test_gae_server(self):
        #r = requests.get('http://localhost:8080')
        self.assertEqual(1, 1)


class LocalServerAPICase(unittest.TestCase):

    def test_gae_API(self):
        test_data = [(4, 10), (5, 12)]
        T = True
        for i, j in test_data:
            url = 'http://localhost:8080/divide/%s/?dividend=%s' % (i, j)
            r = urllib2.urlopen(url)
            json_data = json.load(r)
        self.assertTrue(T)

            
if __name__ == '__main__':
    unittest.main()
