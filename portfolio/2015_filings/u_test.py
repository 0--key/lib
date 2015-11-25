import unittest
import requests
import redis

from worker import FilingItem
from settings import R_HOST, R_PORT


class TestInitialState(unittest.TestCase):

    def setUp(self):
        self.r = redis.StrictRedis(host=R_HOST, port=R_PORT, db=0)

    def test_redis_connection(self):
      self.assertTrue(self.r)

    def tearDown(self):
      pass
      

if __name__ == '__main__':
    unittest.main()
