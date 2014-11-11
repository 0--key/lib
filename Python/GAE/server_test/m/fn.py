import logging
from decimal import Decimal
from google.appengine.api import memcache
from google.appengine.ext import ndb
from models import Result


def quremo(a, b):
    """Primitive ariphmetic calculations"""
    qu = Decimal(b) / Decimal(a)
    re = int(qu)
    mo = Decimal(b) % Decimal(a)
    logging.info("It's a log")
    return str(qu), str(re), str(mo)


def get_quremo(a, b):
    """Memcache or DataStore interaction implementation
    with aim to avoid server calculations overload"""
    a_key = a + '&' + b  # an unique key for each pair
    # looking for MemCache value firstly:
    cached_result = memcache.get(key=a_key)
    if cached_result is None:
        # looking for persistent cached value:
        q = Result.query(Result.a_key == a_key)
        if q.get():  # the values are there
            calc_val = tuple(q.fetch(1)[-1].a_value)
            memcache.add(key=a_key, value=calc_val, time=60)
            logging.info("Data was restored out from ndb")
        else:  # values are completely new
            calc_val = quremo(a, b)
            memcache.add(key=a_key, value=calc_val, time=60)
            R = Result()
            R.a_key, R.a_value = a_key, calc_val
            R.put()
            logging.info("Data is new and was cached successfully")
    else:
        calc_val = cached_result
        logging.info("Data was retrieved out from MemCache")
    return calc_val
