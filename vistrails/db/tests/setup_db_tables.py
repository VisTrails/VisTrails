# MACOSX binary install stuff
import os
import sys
sys.path.append("../..")
from db.services import io

def setup_tables(host, port, user, passwd, db):
    config = {'host': host, 
              'port': port,
              'user': user,
              'passwd': passwd,
              'db': db}

    try:
        db_connection = io.open_db_connection(config)
        io.setup_db_tables(db_connection)
    except Exception, e:
        print e

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 4:
        host = str(args[1])
        port = 3306
        user = str(args[2])
        passwd = str(args[3])
        db = str(args[4])
        setup_tables(host, port, user, passwd, db)
    else:
        print "Usage: %s host user passwd db" % args[0]
