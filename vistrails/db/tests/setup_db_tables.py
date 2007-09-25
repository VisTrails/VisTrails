# MACOSX binary install stuff
import os
os.environ['EXECUTABLEPATH'] = '/vistrails/VisTrails.app/Contents/MacOS'

from db.services import io

def setup_tables():
    config = {'host': 'localhost', 
              'port': 3306,
              'user': 'vistrails',
              'passwd': 'vistrailspwd',
              'db': 'vistrails'}

    try:
        db_connection = io.open_db_connection(config)
        io.setup_db_tables(db_connection)
    except Exception, e:
        print e

if __name__ == '__main__':
    setup_tables()
