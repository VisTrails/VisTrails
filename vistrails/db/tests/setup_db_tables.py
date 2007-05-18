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
        dbConnection = io.openDBConnection(config)
        io.setupDBTables(dbConnection)
    except Exception, e:
        print e

setup_tables()
