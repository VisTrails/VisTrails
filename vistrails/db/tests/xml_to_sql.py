############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
# MACOSX binary install stuff
import os
os.environ['EXECUTABLEPATH'] = '/vistrails/VisTrails.app/Contents/MacOS'

from db.services import io

def convert_xml_to_sql(filename):
    config = {'host': 'localhost', 
              'port': 3306,
              'user': 'vistrails',
              'passwd': 'vistrailspwd',
              'db': 'vistrails'}

    try:
        vistrail = io.open_vistrail_from_xml(filename)
        dbConnection = io.open_db_connection(config)

        print dbConnection.get_server_info()
        print dbConnection.get_host_info()
        print dbConnection.stat()
        print str(dbConnection)

        io.save_vistrail_to_db(vistrail, dbConnection)
        io.close_db_connection(dbConnection)
        print 'db_id: ', vistrail.db_id

    except Exception, e:
        print e

if __name__ == '__main__':
    # convert_xml_to_sql('/vistrails/vtk_http_new.xml')
    convert_xml_to_sql('/vistrails/examples/head.xml')
    # convert_xml_to_sql('/vistrails/examples/lung.xml')
