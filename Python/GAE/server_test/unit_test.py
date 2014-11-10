import urllib2
import json
import unittest
from decimal import Decimal


def quremo(a, b):
    """Primitive ariphmetic calculations"""
    qu = Decimal(b) / Decimal(a)
    re = int(qu)
    mo = Decimal(b) % Decimal(a)
    return str(qu), str(re), str(mo)


class LocalServerCase(unittest.TestCase):

    def test_gae_server(self):
        """GAE local server running test"""
        W = True
        url = 'http://localhost:8080'
        try:
            r = urllib2.urlopen(url)
        except:
            W = False
        self.assertTrue(W, "Connection refused by server")


class LocalServerAPICase(unittest.TestCase):

    def test_gae_API(self):
        """Calculations correctness test"""
        test_data = [(4, 10), (5, 12)]
        T = True
        for i, j in test_data:
            url = 'http://localhost:8080/divide/%s/?dividend=%s' % (i, j)
            r = urllib2.urlopen(url)
            json_data = json.load(r)
            if quremo(i, j) != (json_data['quotient'],
                                json_data['result'],
                                json_data['modulus']):
                T = False
        self.assertTrue(T, "Calculations is incorrect")


if __name__ == '__main__':
    unittest.main()
