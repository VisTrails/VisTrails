# MACOSX binary install stuff
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
        dbConnection = io.openDBConnection(config)        
        vistrail = io.openVistrailFromDB(dbConnection, id)
        io.setDBParameters(vistrail, config)
        io.saveVistrailToXML(vistrail, filename)
        io.closeDBConnection(dbConnection)
    except MySQLdb.Error, e:
        print e

convert_sql_to_xml('/vistrails/vtk_http_from_db.xml', 1)
# convert_sql_to_xml('/vistrails/head_from_db.xml', 1)
# convert_sql_to_xml('/vistrails/lung_from_db.xml', 2)
