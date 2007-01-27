############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
"""HTTP provides packages for HTTP-based file fetching. This provides
a location-independent way of referring to files. This package uses a
local cache of the files, inside the per-user VisTrails
directory. This way, files that haven't been changed do not need
downloading. The check is performed efficiently using the HTTP GET
headers.
"""

from core.modules.vistrails_module import Module, ModuleError
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.system
import httplib
import os.path
import sys
import time
import urllib

package_directory = None

###############################################################################

class HTTP(Module):
    pass

class HTTPFile(HTTP):

    def __init__(self):
        HTTP.__init__(self)
        self.cal = {}
        self.cal['Jan'] = 1
        self.cal['Feb'] = 2
        self.cal['Mar'] = 3
        self.cal['Apr'] = 4
        self.cal['May'] = 5
        self.cal['Jun'] = 6
        self.cal['Jul'] = 7
        self.cal['Aug'] = 8
        self.cal['Sep'] = 9
        self.cal['Oct'] = 10
        self.cal['Nov'] = 11
        self.cal['Dec'] = 12
    
    def parse_url(self, url):
        # TODO: There's gotta be a urllib method for this.
        s = url.split('/')
        self.host = s[2]
        self.filename = '/' + '/'.join(s[3:])

    def is_outdated(self, remoteHeader, localFile):
        """Checks whether local file is outdated."""
        # TODO: There's gotta be a time method for this.
        mod = remoteHeader.split()
        day = int(mod[1])
        mon = int(self.cal[mod[2]])
        yr = int(mod[3])
        t = mod[4]
        ltime = time.gmtime(os.path.getmtime(localFile))

        t = [int(x) for x in t.split(':')]
        remoteTuple = (yr, mon, day, t[0], t[1], t[2])
        localTuple = (ltime[0], ltime[1], ltime[2], ltime[3], ltime[4], ltime[5])
        return remoteTuple > localTuple
    
    def compute(self):
        self.checkInputPort('url')
        url = self.getInputFromPort("url")
        self.parse_url(url)
        conn = httplib.HTTPConnection(self.host)
        conn.request("GET", self.filename)
        response = conn.getresponse()
        mod = response.msg.getheader('last-modified')
        local_filename = package_directory + '/' + urllib.quote_plus(url)
        result = core.modules.basic_modules.File()
        result.name = local_filename
        if (not os.path.isfile(local_filename) or
            not mod or
            self.is_outdated(mod, local_filename)):
            # FIXME: This is bad for large files
            data = response.read()
            try:
                fn = file(local_filename, "w")
            except:
                raise ModuleError(self, ("Could not create local file '%s'" %
                                         local_filename))
            fn.write(data)
            fn.close()
        conn.close()
        self.setResult("file", result)
        self.setResult("local_filename", local_filename)

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    reg.addModule(HTTP)
    reg.addModule(HTTPFile)
    reg.addInputPort(HTTPFile, "url", (basic.String, 'URL'))
    reg.addOutputPort(HTTPFile, "file", (basic.File, 'local File object'))
    reg.addOutputPort(HTTPFile, "local_filename", (basic.String, 'local filename'))

    global package_directory
    package_directory = core.system.defaultDotVistrails() + "/HTTP"

    if not os.path.isdir(package_directory):
        try:
            print "Creating package directory..."
            os.mkdir(package_directory)
        except:
            print "Could not create package directory. Make sure"
            print "'%s' does not exist and parent directory is writable"
            sys.exit(1)
        print "Ok."


##############################################################################

import unittest

class TestHTTPFile(unittest.TestCase):

    def testParseURL(self):
        foo = HTTPFile()
        foo.parse_url('http://www.sci.utah.edu/~cscheid/stuff/vtkdata-5.0.2.zip')
        self.assertEquals(foo.host, 'www.sci.utah.edu')
        self.assertEquals(foo.filename, '/~cscheid/stuff/vtkdata-5.0.2.zip')

if __name__ == '__main__':
    unittest.main()
