import pickle


def pickle_db(object):
    # use binary mode files in 3.X
    dbfile = open('people-pickle.edu', 'wb')
    pickle.dump(object, dbfile)  # data is bytes, not str
    dbfile.close()
    return True
