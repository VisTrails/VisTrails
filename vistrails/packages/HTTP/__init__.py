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
        url = url.strip('http://')
        split = url.split('/')
        self.host = split[0]
        self.filename = ''
        split[0] = ''
        for i in split:
            if i == '':
                continue
            else:
                self.filename = self.filename + '/' + i

        suf = split[split.__len__() - 1]
        suf = suf.split('.')
        self.suffix = suf[suf.__len__() - 1]

    def is_outdated(self, remoteHeader, localFile):
        """Checks whether local file is up-to-date."""
        # TODO: There's gotta be a time method for this.
        mod = remoteHeader.split()
        day = int(mod[1])
        mon = int(self.cal[mod[2]])
        yr = int(mod[3])
        t = mod[4]
        ltime = time.gmtime(os.path.getmtime(localFile))
        if ltime[0] < yr:
            return True
        if ltime[1] < mon:
            return True
        if ltime[2] < day:
            return True
        
        t = t.split(':')
        if ltime[3] < int(t[0]):
            return True
        if ltime[4] < int(t[1]):
            return True
        if ltime[5] < int(t[2]):
            return True

        return False
    
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
