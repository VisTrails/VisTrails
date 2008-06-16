# MACOSX binary install stuff
if __name__ != '__main__':
    import tests
    raise tests.NotModule('This should not be imported as a module')
    
import os
os.environ['EXECUTABLEPATH'] = '/vistrails/VisTrails.app/Contents/MacOS'

import MySQLdb

from db.services import io

def convert_sql_to_xml(filename, id):
    config = {'host': 'localhost', 
              'port': 3306,
              'user': 'vistrails',
              'passwd': 'vistrailspwd',
              'db': 'vistrails'}
    try:
        dbConnection = io.open_db_connection(config)        
        vistrail = io.open_vistrail_from_db(dbConnection, id)
        io.setDBParameters(vistrail, config)
        io.save_vistrail_to_xml(vistrail, filename)
        io.close_db_connection(dbConnection)
    except MySQLdb.Error, e:
        print e

if __name__ == '__main__':
    convert_sql_to_xml('/vistrails/vtk_http_from_db.xml', 1)
    # convert_sql_to_xml('/vistrails/head_from_db.xml', 1)
    # convert_sql_to_xml('/vistrails/lung_from_db.xml', 2)
