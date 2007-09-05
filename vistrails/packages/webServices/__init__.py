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
""" This package defines a set of methods to deal with web services.
It requires pyXML, fpconst and SOAPpy modules to be installed. Click on
configure to add wsdl urls to the package (use a ; to separate the urls).

"""
from core.configuration import ConfigurationObject
from core.bundles import py_import
from core.requirements import MissingRequirement

import xml
try:
    # python-soappy installs fpconst for us.
    SOAPpy = py_import('SOAPpy', {'linux-ubuntu': 'python-soappy'})
except:
    raise MissingRequirement('SOAPpy')

# try:
#     import fpconst
# except:
#     raise MissingRequirement('fpconst')

try:
    SOAPpy = py_import('SOAPpy', {'linux-ubuntu': 'python-soappy'})
except:
    raise MissingRequirement('SOAPpy')

from SOAPpy import WSDL

import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, new_module

configuration = ConfigurationObject(wsdlList=(None, str))
identifier = 'edu.utah.sci.vistrails.webservices'
version = '0.9.0'
name = 'Web Services'

###############################################################################

class WebService(Module):
    """ WebService is the base Module.
     We will create a WebService Module for each method published by 
     the web service.

    """
    def __init__(self):
        Module.__init__(self)
        
    def compute(self):
        raise vistrails_module.IncompleteImplementation

    def runMethod(self, methodName, *args):
        return getattr(self.server,methodName)(*args)

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
        for i in xrange(len(inparams)):
            pname = str(inparams[i].name)
            type = str(inparams[i].type)
            v.append(self.getInputFromPort(pname))
        try:
            r = self.runMethod(name,*(v)) 
        except SOAPpy.Errors.HTTPError, e:
            raise ModuleError(self, """The server couldn't fulfill the request.
            Error Message: '%s'""" % e)
        self.inparams = inparams
        self.outparams = outparams
        self.setResult(outparams[0].name,r)
        #print r # just for debugging

    return {'compute':compute}

# wsdlTypesDict will store the correspondence between WSDL basic types and 
# visTrails Modules basic types

wsdlTypesDict = { 'string' : core.modules.basic_modules.String,
                  'int' : core.modules.basic_modules.Integer,
                  'long' : core.modules.basic_modules.Integer,
                  'float': core.modules.basic_modules.Float,
                  'double': core.modules.basic_modules.Float,
                  'boolean': core.modules.basic_modules.Boolean}

################################################################################

def initialize(*args, **keywords):
    import core.packagemanager
    pm = core.packagemanager.get_package_manager()
    config = pm.get_package_configuration('webServices')
    wsdlList = []
    if config.check('wsdlList'):
        wsdlList = config.wsdlList.split(";")
        
    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    reg.add_module(WebService)

    for w in wsdlList:
        #create the base Module
        server = WSDL.Proxy(w)
        #name = str(server.wsdl.name) #better use the url
        m = new_module(WebService,w, webServiceNameMethodDict())
        m.server = server
        reg.add_module(m)
        #get all the service's methods and for each method create a module
        keys = server.methods.keys()
        keys.sort()
        for kw in keys:
            callInfo = server.methods[kw]
            inparams = callInfo.inparams
            outparams = callInfo.outparams
            mt = new_module(m,str(kw), 
                           webServiceParamsMethodDict(str(kw),
                                                      inparams,
                                                      outparams))
            reg.add_module(mt)
            for p in inparams:
                try:
                    basicType = wsdlTypesDict[str(p.type[1])]
                except KeyError:
                    basicType = basic.String
                reg.add_input_port(mt,str(p.name),(basicType, ''))
            
            for p in outparams:
                try:
                    basicType = wsdlTypesDict[str(p.type[1])]
                except KeyError:
                    basicType = basic.String
                reg.add_output_port(mt,str(p.name),(basicType, ''))
