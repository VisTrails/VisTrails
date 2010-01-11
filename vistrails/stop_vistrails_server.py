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
""" This script stops VisTrails server. It can only stop with an XML Request """

import xmlrpclib
import sys

def usage():
    return "%s server_url"%sys.argv[0]
    
try:
    uri = sys.argv[1]

except Exception, e:
    print usage()
    sys.exit(1)

proxy = xmlrpclib.ServerProxy(uri)
print proxy.quit()
#print proxy.run_from_db('vistrails.sci.utah.edu', 3306,'vt_test',1,'/tmp/spreadsheet',598)
