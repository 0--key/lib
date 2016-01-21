from initdata import db
import pickle
# use binary mode files in 3.X
dbfile = open('people-pickle.edu', 'wb')
pickle.dump(db, dbfile)                            # data is bytes, not str
dbfile.close()
