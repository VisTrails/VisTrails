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


from core.modules.vistrails_module import ModuleError
import core.modules.vistrails_module
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.system
import httplib
import os.path
import sys
import time
import urllib
import socket

package_directory = None

# TODO: When network is down, HTTPFile should log the fact that it used the
# local cache regardless.
name = 'HTTP'
identifier = 'edu.utah.sci.vistrails.http'
version = '0.9.0'

###############################################################################

class HTTP(core.modules.vistrails_module.Module):
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
        try:
            self.host = s[2]
            self.filename = '/' + '/'.join(s[3:])
        except:
            raise ModuleError(self, "Malformed URL: %s" % url)

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

    def _file_is_in_local_cache(self, local_filename):
        return os.path.isfile(local_filename)
    
    def compute(self):
        self.checkInputPort('url')
        url = self.getInputFromPort("url")
        self.parse_url(url)
        conn = httplib.HTTPConnection(self.host)
        local_filename = package_directory + '/' + urllib.quote_plus(url)
        self.setResult("local_filename", local_filename)
        try:
            conn.request("GET", self.filename)
        except socket.gaierror, e:
            if self._file_is_in_local_cache(local_filename):
                result = core.modules.basic_modules.File()
                result.name = local_filename
                self.setResult("file", result)
            else:
                raise ModuleError(self, e[1])
        else:
            response = conn.getresponse()
            mod_header = response.msg.getheader('last-modified')
            result = core.modules.basic_modules.File()
            result.name = local_filename
            if (not self._file_is_in_local_cache(local_filename) or
                not mod_header or
                self.is_outdated(mod_header, local_filename)):
                # FIXME: This is bad for large files
                data = response.read()
                try:
                    fn = file(local_filename, "wb")
                except:
                    raise ModuleError(self, ("Could not create local file '%s'" %
                                             local_filename))
                fn.write(data)
                fn.close()
            conn.close()
            self.setResult("file", result)

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    reg.add_module(HTTP, abstract=True)
    reg.add_module(HTTPFile)
    reg.add_input_port(HTTPFile, "url", (basic.String, 'URL'))
    reg.add_output_port(HTTPFile, "file", (basic.File, 'local File object'))
    reg.add_output_port(HTTPFile, "local_filename", (basic.String, 'local filename'), optional=True)

    global package_directory
    package_directory = core.system.default_dot_vistrails() + "/HTTP"

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

    class DummyView(object):
        def set_module_active(self, id):
            pass
        def set_module_computing(self, id):
            pass
        def set_module_success(self, id):
            pass
        def set_module_error(self, id, error):
            pass

    def testParseURL(self):
        foo = HTTPFile()
        foo.parse_url('http://www.sci.utah.edu/~cscheid/stuff/vtkdata-5.0.2.zip')
        self.assertEquals(foo.host, 'www.sci.utah.edu')
        self.assertEquals(foo.filename, '/~cscheid/stuff/vtkdata-5.0.2.zip')

    def testIncorrectURL(self):
        import core.vistrail
        from core.vistrail.module import Module
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module_param import ModuleParam
        import core.interpreter
        p = core.vistrail.pipeline.Pipeline()
        m_param = ModuleParam(type='String',
                              val='http://illbetyouthisdoesnotexistohrly',
                              )
        m_function = ModuleFunction(name='url',
                                    parameters=[m_param],
                                    )
        p.add_module(Module(name='HTTPFile',
                           package=identifier,
                           id=0,
                           functions=[m_function],
                           ))
        interpreter = core.interpreter.default.get_default_interpreter()
        interpreter.execute(None, p, 'foo', 1, self.DummyView(), None)

    def testIncorrectURL_2(self):
        import core.vistrail
        from core.vistrail.module import Module
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module_param import ModuleParam
        import core.interpreter
        p = core.vistrail.pipeline.Pipeline()
        m_param = ModuleParam(type='String',
                              val='http://neitherodesthisohrly',
                              )
        m_function = ModuleFunction(name='url',
                                    parameters=[m_param],
                                    )
        p.add_module(Module(name='HTTPFile', 
                           package=identifier,
                           id=0,
                           functions=[m_function],
                           ))
        interpreter = core.interpreter.default.get_default_interpreter()
        interpreter.execute(None, p, 'foo', 1, self.DummyView(), None)


if __name__ == '__main__':
    unittest.main()
