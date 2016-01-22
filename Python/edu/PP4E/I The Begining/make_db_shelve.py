from initdata import tom
from initdata import bob, sue
import shelve


def put_on_shelve():
    """
    Stores all data on shelve
    """
    db = shelve.open('people-shelve.edu')
    db['bob'] = bob
    db['sue'] = sue
    db.close()
    return True


def get_from_shelve():
    """
    Retrieves data out from shelve
    """
    db = shelve.open('people-shelve.edu')
    return db
    

def update_shelve():
    db = shelve.open('people-shelve.edu')
    sue = db['sue']                       # fetch sue
    sue['pay'] *= 1.50
    db['sue'] = sue                       # update sue
    db['tom'] = tom                       # add a new record
    db.close()
    return True
