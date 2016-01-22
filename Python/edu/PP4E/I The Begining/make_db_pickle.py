import pickle
import glob


def pickle_db(object):
    dbfile = open('people-pickle.edu', 'wb')  # use binary mode files in 3.X
    pickle.dump(object, dbfile)  # data is bytes, not str
    dbfile.close()
    return True


def restore_pickled_obj():
    dbfile = open('people-pickle.edu', 'rb')  # use binary mode files in 3.X
    db = pickle.load(dbfile)
    return db


def find_files():  # seeking for matching filenames
    for filename in glob.glob('*.py'):
        print(filename)
    return True
