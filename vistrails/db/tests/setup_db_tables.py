# MACOSX binary install stuff
import os
os.environ['EXECUTABLEPATH'] = '/vistrails/VisTrails.app/Contents/MacOS'

from db.services import io

def setup_tables():
#     config = {'host': 'localhost', 
#               'port': 3306,
#               'user': 'vistrails',
#               'passwd': 'vistrailspwd',
#               'db': 'vistrails'}

    config = {'host': 'vistrails.sci.utah.edu', 
              'port': 3306,
              'user': 'visadmin',
              'passwd': 'uvgc07',
              'db': 'vistrails'}

    try:
        dbConnection = io.openDBConnection(config)
        io.setupDBTables(dbConnection)
    except Exception, e:
        print e

if __name__ == '__main__':
    setup_tables()
