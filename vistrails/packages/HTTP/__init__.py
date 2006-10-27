import modules
import modules.module_registry
from modules.vistrails_module import Module, ModuleError

import httplib

class HTTP(Module):
    def compute(self):
        pass

class HTTPGetFile(HTTP):

    def __init__(self):
        cal = {}
        cal['Jan'] = 1
        cal['Feb'] = 2
        cal['Mar'] = 3
        cal['Apr'] = 4
        cal['May'] = 5
        cal['Jun'] = 6
        cal['Jul'] = 7
        cal['Aug'] = 8
        cal['Sep'] = 9
        cal['Oct'] = 10
        cal['Nov'] = 11
        cal['Dec'] = 12
    
    def parseURL(self, url):
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

    def isOutdated(self, remoteHeader, localFile):
        # This return is to account for the vis_application.py
        # and Qt problems discussed in the check-in.  Upon
        # resolution of this, we simply must remove this
        # line and full functionality will be restored.
        return True
        mod = remoteHeader.split()
        day = mod[1]
        mon = self.cal[mod[2]]
        yr = mod[3]
        t = mod[4]
        ltime = time.localtime(os.path.getmtime(localFile))
        if ltime[0] < yr:
            return True
        if ltime[1] < mon:
            return True
        if ltime[2] < day:
            return True
        
        t = t.split(':')
        if ltime[3] < t[0]:
            return True
        if ltime[4] < t[1]:
            return True
        if ltime[5] < t[2]:
            return True

        return False
    
    def compute(self):
        url = self.getInputFromPort("URL")
        self.parseURL(url)
        conn = httplib.HTTPConnection(self.host)
        conn.request("GET", self.filename)
        response = conn.getresponse()
        mod = response.msg.getheader('Last-Modified')
        
        if self.isOutdated(mod, localfile):
            data = response.read()
            f = self.interpreter.filePool.createFile(suffix=self.suffix)
            fn = open(f.name, "w")
            f.write(data)
            f.close()
            conn.close()
            self.setResult("File", f)
            self.setResult("Filename", f.name)
        else:
            result = basic_modules.File()
            result.name = localfile
            result.upToDate = True
            conn.close()
            self.setResult("File", result)
            
        
def initialize(*args, **keywords):
    reg = modules.module_registry
    basic = modes.basic_modules

    reg.addModule(HTTP)

    reg.addModule(HTTPGetFile)
    reg.addInputPort(HTTPGetFile, "URL", (basic.String, 'URL'))
    reg.addOutputPort(HTTPGetFile, "File", (basic.File, 'File'))
