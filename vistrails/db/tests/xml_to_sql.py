# MACOSX binary install stuff
import os
os.environ['EXECUTABLEPATH'] = '/vistrails/VisTrails.app/Contents/MacOS'

from db.services import io

def convert_xml_to_sql(filename):
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

#     config = {'host': 'vistrails.sci.utah.edu', 
#               'port': 3306,
#               'user': 'vistrails',
#               'passwd': 'vtutesdb',
#               'db': 'vistrails'}

    try:
        vistrail = io.openVistrailFromXML(filename)
        dbConnection = io.openDBConnection(config)

        print dbConnection.get_server_info()
        print dbConnection.get_host_info()
        print dbConnection.stat()
        print str(dbConnection)

        io.saveVistrailToDB(vistrail, dbConnection)
        io.closeDBConnection(dbConnection)
        print 'db_id: ', vistrail.db_id

    except Exception, e:
        print e

if __name__ == '__main__':
    # convert_xml_to_sql('/vistrails/vtk_http_new.xml')
    convert_xml_to_sql('/vistrails/examples/head.xml')
    # convert_xml_to_sql('/vistrails/examples/lung.xml')
