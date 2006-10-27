import modules
import modules.module_registry
import modules.basic_modules
from modules.vistrails_module import Module, ModuleError, newModule

import xml
import fpconst
import SOAPpy
from SOAPpy import WSDL

############################################################################

class WebService(Module):
    def __init__(self):
        Module.__init__(self)
        
    def compute(self):
        raise vistrails_module.IncompleteImplementation

    def runMethod(self, methodName, *args):
        return getattr(self.server,methodName)(*args)

    def __str__(self):
        return "webservice"

def webServiceNameMethodDict():
    """ This returns the method dictionary for the web service address base
    class. """
    def compute(self):
        raise vistrails_module.IncompleteImplementation
    
    return { 'compute': compute}

def webServiceParamsMethodDict(name, inparams, outparams):
    """ This will create a correct compute method according to the name,
    inparams and outparams. Right now, only the first outparam is used
    for setting the result. """
    def compute(self):
        v = [] #it will store the list of param values
        for i in range(len(inparams)):
            pname = str(inparams[i].name)
            type = str(inparams[i].type)
            v.append(self.getInputFromPort(pname))
        
        r = self.runMethod(name,*(v)) 
        self.inparams = inparams
        self.outparams = outparams
        self.setResult(outparams[0].name,r)
        #print r # just for debugging

    def __str__(self):
        v = self.getOutput(outparams[0].name)
        return str(v)

    return {'compute':compute, 
            '__str__':__str__}

#  wsdlTypesDict will store the correspondence between WSDL basic types and 
# visTrails Modules basic types

wsdlTypesDict = { 'string' : modules.basic_modules.String,
                  'int' : modules.basic_modules.Integer,
                  'float': modules.basic_modules.Float}

################################################################################

def initialize(*args, **keywords):
    wsdlList = keywords['wsdlList']
        
    reg = modules.module_registry
    basic = modules.basic_modules
    reg.addModule(WebService)

    for w in wsdlList:
        #create the base Module
        server = WSDL.Proxy(w)
        #name = str(server.wsdl.name) #better use the url
        m = newModule(WebService,w, webServiceNameMethodDict())
        m.server = server
        reg.addModule(m)
        #get all the service's methods and for each method create a module
        keys = server.methods.keys()
        keys.sort()
        for kw in keys:
            callInfo = server.methods[kw]
            inparams = callInfo.inparams
            outparams = callInfo.outparams
            mt = newModule(m,str(kw), webServiceParamsMethodDict(str(kw),inparams,outparams))
            reg.addModule(mt)
            for p in inparams:
                try:
                    basicType = wsdlTypesDict[str(p.type[1])]
                except KeyError:
                    basicType = basic.String
                reg.addInputPort(mt,str(p.name),(basicType, ''))
            
            for p in outparams:
                try:
                    basicType = wsdlTypesDict[str(p.type[1])]
                except KeyError:
                    basicType = basic.String
                reg.addOutputPort(mt,str(p.name),(basicType, ''))
