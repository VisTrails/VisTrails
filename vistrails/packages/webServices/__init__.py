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

import sys
import os.path
from os.path import join
import types
import httplib
import urllib
import time

import ZSI
from ZSI.ServiceProxy import ServiceProxy
from ZSI.generate.wsdl2python import WriteServiceModule
from ZSI.wstools import WSDLTools

import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, new_module
from packages.HTTP import HTTPFile

import subprocess
import platform
import popen2

package_directory = None
modulesDict = {}
visrespobj = None

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

#Class for complex types
class WBModule:
    def __init__(self,name):
        self.name = name
        self.type = '' #Instance of the type
        self.typeobj = ''   #Enumeration or ComplexType
        self.ports = []
        self.isRequestType = False
        self.isEmptySequence = False
        self.isExtension = False
        self.ExtensionBase = ''

def webServiceNameClassifier():
    """  """
    def compute(self):
        raise vistrails_module.IncompleteImplementation
    
    return { 'compute': compute}

def webServiceNameMethodDict():
    """ This returns the method dictionary for the web service address base
    class. """
    def compute(self):
        raise vistrails_module.IncompleteImplementation
    
    return { 'compute': compute}

def webServiceTypesDict(WBobj):
    """ This will create a correct compute method according to the complex type
    or enumeration name. """
    def compute(self):
        reg = core.modules.module_registry
        #Check if it is an enumeration
        if WBobj.typeobj == 'Enumeration':
            nameport = str(WBobj.ports[0][0])
            if self.hasInputFromPort(nameport):
                inputport = self.getInputFromPort(nameport)
                self.holder = inputport
                self.setResult(WBobj.name,self)
        else:        
            #Check if the type is a request type
            porttype = str(WBobj.type.server._wsdl.portTypes.keys()[0][0][1])
            modname = WBobj.name
            listoperations = WBobj.type.server._wsdl.portTypes[porttype].operations.values()
            isrequest = False
            for element in listoperations:
                if modname == element.input.getMessage().name or modname == element.input.getMessage().name.replace('SoapRequest','') or modname == element.input.getMessage().name.replace('SoapIn',''):
                    isrequest = True
                    requestname = element.input.getMessage().name
            if (isrequest == True):
                WBobj.isRequestType = True
                req = getattr(self.modclient,requestname)()
                #req = getattr(WBobj.modclient,requestname)()
                #Set the values in the input ports
                for types in WBobj.ports:
                    nameport = str(types[0])
                    if self.hasInputFromPort(nameport):
                        inputport = self.getInputFromPort(nameport)
                        namemethod = "set_element_" + nameport
                        try:
                            getattr(req, namemethod)(inputport)
                        except:
                            namemethod = nameport
                            setattr(req, namemethod,inputport)
                #Set the value in the response output port
                nameport = str(WBobj.name)
                self.setResult(nameport,req)                        
            else:
                nameport = str(WBobj.name)
                if self.hasInputFromPort(nameport):
                    inputport = self.getInputFromPort(nameport)
                    nameport = str(WBobj.ports[0][0])
                    nameattrib = nameport[0].upper() + nameport[1:]
                    sentence = "inputport" + "." + nameattrib
                    outputport = eval(sentence)
                    self.setResult(nameport,outputport)
    return {'compute':compute}


def webServiceParamsMethodDict(name, server, inparams, outparams):
    """ This will create a correct compute method according to the 
    inparams and outparams. Right now, only the first outparam is used
    for setting the result. """

    reg = core.modules.module_registry
        
    def wrapResponseobj(self,resp,visobj):
     global modulesDict
     global visrespobj
     if type(resp)==types.ListType:
         ptype = resp[0].typecode.type[1]
     else:
         if resp.typecode.type[1] == None:
             ptype = resp.typecode.pname
         else:    
             ptype = resp.typecode.type[1]
        
     #Find the children for the vistrail type and set the attributes
     dictkey = self.webservice + "." + str(ptype)
     
     obj = modulesDict[dictkey]
     for child in obj.ports:
         namechild = child[0]
         typechild = child[1]    
         try:
             Type = wsdlTypesDict[str(typechild)]
             namemethod = "get_element_" + str(namechild)
             try:
                 ans = getattr(resp, namemethod)()
             except:
                 #Some times when there is no complex type in the wsdl the get and set methods are not generated
                 namemethod = str(namechild)
                 sentence = "resp" + "." + namemethod
                 ans = eval(sentence)
             nameattrib = str(namechild)
             nameattrib = nameattrib[0].upper() + nameattrib[1:]
             setattr(visobj,nameattrib,ans)  
         except KeyError:
             if type(resp) != types.ListType:
                 namemethod = "get_element_" + namechild
                 try:
                     resp = getattr(resp, namemethod)()
                 except:
                     namemethod = str(namechild)
                     sentence = "resp" + "." + namemethod
                     resp = eval(sentence)

             if type(resp) == types.ListType:
                 objlist = []
                 for element in resp:
                     ptype = element.typecode.type[1]
                     dictkey = self.webservice + "." + str(ptype)
                     obj = modulesDict[dictkey]
                     visclass = obj.type
                     vischildobj = visclass()
                     wrapResponseobj(self,element,vischildobj)
                     objlist.append(vischildobj)
                 nameattrib = str(namechild)
                 nameattrib = nameattrib[0].upper() + nameattrib[1:]
                 setattr(visobj,nameattrib,objlist)  
             else:
                 ptype = str(typechild)
                 dictkey = self.webservice + "." + ptype
                 obj = modulesDict[dictkey]
                 vischildclass = obj.type
                 vischildobj = vischildclass()
                 nameattrib = str(namechild)
                 nameattrib = nameattrib[0].upper() + nameattrib[1:]
                 #Set the attribute in the vistrail object (Same as in schema but with the first letter uppercase)
                 setattr(visobj,nameattrib,vischildobj)  
                 visobjchild = getattr(visobj,nameattrib)
                 wrapResponseobj(self,resp,visobjchild)
                 
    def compute(self):
        global visrespobj
        dirmodule = dir(self.modclient)
        #Get the locator name
        for elemlist in dirmodule:
            if elemlist.find('Locator') != -1:
                namelocator = elemlist
        #Get the port name
        loc = getattr(self.modclient, namelocator)()
        dirloc = dir(loc)
        
        for elemlist in dirloc:
            if ((elemlist.find('Address') == -1) and ((elemlist.find('Port') != -1 and elemlist.find('get') != -1) or (elemlist.find('get') != -1 and elemlist.find('Soap') != -1) or (elemlist.find('get') != -1))):
                portname = elemlist
        port = getattr(loc, portname)()
        try:
            #This part is for the primitive or simple types methods parameters
            Type = str(inparams[0].type[1])
            if len(Type) > 5:
                if Type[0:5] == 'Array':
                    Type = 'Array'
            Type = wsdlTypesDict[Type]
            porttype = server._wsdl.portTypes.keys()[0][0][1]
            listoperations = server._wsdl.portTypes[porttype].operations.values()
            for element in listoperations: #list of operations instances
                if str(element.name) == str(name):
                    #get the request method name
                    reqname = element.input.getMessage().name
            req = getattr(self.modclient,reqname)()
            for inparam in inparams:
                #Now set all attributes for the request object
                if self.hasInputFromPort(inparam.name):
                    inputport = self.getInputFromPort(inparam.name)
                    namemethod = "set_element_" + inparam.name
                    try:
                        getattr(req, namemethod)(inputport)
                    except:
                        namemethod = inparam.name
                        setattr(req, namemethod,inputport)
            resp = getattr(port,name)(req)
            namemethod = "get_element_" + outparams[0].name
            try:
                result = getattr(resp,namemethod)()
            except:
                namemethod = outparams[0].name
                sentence = "resp" + "." + namemethod
                result = eval(sentence)
            self.setResult(outparams[0].name,result)
        except KeyError:
            #This part is for the complex types methods parameters
            inparam = str(inparams[0].name)
            if self.hasInputFromPort(inparam):
                request = self.getInputFromPort(inparam)
                resp = getattr(port,name)(request)
                #Wrap the ZSI attributes into the vistrails module attributes
                nameclass = str(outparams[0].type[1])
                dictkey = self.webservice + "." + nameclass
                obj = modulesDict[dictkey]
                visclass = obj.type
                visobj = visclass()
                wrapResponseobj(self,resp, visobj)
                self.setResult(outparams[0].name,visobj)
        
    return {'compute':compute}

def processEnumeration(complexschema):
    listenum = []
    Type = complexschema.content.attributes['base'][1]
    for facets in complexschema.content.facets:
        listenum.append(facets.getAttributeDictionary()['value'])
    return (listenum,Type)

def processArray(complexschema,w):
    contentschema =  complexschema.content.content.attr_content
    for child in contentschema:
        nametype = str(child.attributes['http://schemas.xmlsoap.org/wsdl/']['arrayType'])
        index = nametype.find(':')
        nametype = nametype[index+1:]
        #verify if is an array of complex types
        index = nametype.find('[')
        if index != -1:
            Type = nametype[0:index]
        try:
            Type = wsdlTypesDict[str(Type)]
        except KeyError:
            try:
                complex1 = schema.types[str(Type)]
                processType(complex1,w)
            except KeyError:    
                pass

def processType(complexschema,w):
    global modulesDict
    contentschema = ''
    modulename = str(complexschema.attributes['name'])
    modulekey = w + "." + modulename
    objModule = WBModule(modulename)

    if complexschema.isSimple():
        objModule.typeobj = 'Enumeration'
        objModule.ports.append(processEnumeration(complexschema))

    if complexschema.isElement():
        try:
            if complexschema.content.content == None:
                contentschema = []
            else:    
                contentschema = complexschema.content.content.content
            objModule.typeobj = 'ComplexType'
            if complexschema.content.content == None or complexschema.content.content.content == ():
                objModule.isEmptySequence = True
        except AttributeError:
            pass
        
    if complexschema.isComplex():
        try:
            #Extensions in a complex type
            if complexschema.content.content.isExtension():
                objModule = WBModule(modulename)
                objModule.typeobj = 'ComplexType'
                objModule.isExtension = True
                objModule.ExtensionBase = str(complexschema.content.content.attributes['base'][1])
                contentschema = complexschema.content.content.content.content
        except AttributeError:
            contentschema = complexschema.content.content

    for child in contentschema:
        try:
            nametype = child.attributes['name']
            Type = child.attributes['type'][1]
            if len(Type) >= 5:
                if (Type[0:5] == 'Array'):
                    Type = 'Array'
                    objModule.ports.append((nametype,Type))
                    processArray(child,w)
            objModule.ports.append((nametype,Type))
            try:
                Type = wsdlTypesDict[str(Type)]
            except KeyError:
                try:
                    complex1 = schema.types[str(Type)]
                    processType(complex1,w)
                except KeyError:    
                    pass
        except AttributeError:
            pass

    objModule.webservice = str(w)
    modulesDict [modulekey] = objModule


def addExtensionsModules(server, extensionbase):
    """ Add complex types specified in the extension base is they are not in the complex types dictionary. """
    try:
        extensionobj = modulesDict[extensionbase]
    except KeyError:
        for schematypes in server._wsdl.types.keys():
            schema = server._wsdl.types[str(schematypes)]
            if len(schema.types.keys()) != 0:
                try:
                    extensionbasestr = str(extensionbase)
                    complex1 = schema.types[extensionbasestr]
                    processType(complex1,w)
                except KeyError:
                    pass        
            if len(schema.elements.keys()) != 0:
                try:
                    extensionbasestr = str(extensionbase)
                    complex1 = schema.elements[str(extensionbasestr)]
                    processType(complex1,w)
                except KeyError:
                    pass

def processExtension(server):
    global modulesDict
    keys = modulesDict.keys()
    keys.sort()
    for types in keys:
        obj = modulesDict[types]
        if obj.isExtension:
            #Add extensions to modulesDict dictionary
            extensionbase = obj.ExtensionBase
            addExtensionsModules(server, extensionbase)
            keys2 = modulesDict.keys()
            keys2.sort()
            for types2 in keys2:
                obj2 = modulesDict[types2]
                if obj2.name == extensionbase:
                    for port in obj2.ports:
                        obj.ports.append(port)
                    break

def addTypesModules(w,modclient,server):
    """ Create a VisTrails module for each complex type specified in modulesDict dictionary. """
    
    reg = core.modules.module_registry
    global modulesDict
    keys = modulesDict.keys()
    keys.sort()
    for dictkey in keys:
        obj = modulesDict[dictkey]
        if obj.webservice == w:
            mt = new_module(WebService,obj.name, webServiceTypesDict(obj))
            mt.webservice = w
            mt.modclient = modclient
            mt.server = server
            namespace = w + '|Types'
            reg.add_module(mt, namespace= namespace)
            #Add module type to modulesDict
            modbyname = reg.get_module_by_name(identifier = identifier, name = obj.name, namespace = namespace)
            obj.type = modbyname
        

def addPortsToModules(w):
    """ Add input and output ports to the VisTrails complex type modules. """
    
    reg = core.modules.module_registry
    global modulesDict
    keys = modulesDict.keys()
    for dictkey in keys:
        #Add the Ports that are of the module type
        obj = modulesDict[dictkey]
        if obj.webservice == w:
            reg.add_input_port(obj.type,obj.name,(obj.type, ''))
            reg.add_output_port(obj.type,obj.name,(obj.type, ''))
            #Add ports according to the input and output parameters
            for ports in obj.ports:
                try:
                    Type = wsdlTypesDict[str(ports[1])]
                except KeyError:
                    portname = str(ports[1])
                    namespace = w + '|Types'
                    Type = reg.get_module_by_name(identifier = identifier, name =portname, namespace = namespace)
                reg.add_input_port(obj.type,str(ports[0]),(Type, ''))
                reg.add_output_port(obj.type,str(ports[0]),(Type, ''))

#Dictionary of primitive types
wsdlTypesDict = { 'string' : core.modules.basic_modules.String,
                  'int' : core.modules.basic_modules.Integer,
                  'long' : core.modules.basic_modules.Integer,
                  'float': core.modules.basic_modules.Float,
                  'decimal': core.modules.basic_modules.Float,
                  'double': core.modules.basic_modules.Float,
                  'boolean': core.modules.basic_modules.Boolean,
                  'anyType': core.modules.basic_modules.Variant,
                  'dateTime': core.modules.basic_modules.String,
                  'time': core.modules.basic_modules.String,
                  'date': core.modules.basic_modules.String,
                  'gYearMonth': core.modules.basic_modules.String,
                  'gYear': core.modules.basic_modules.String,
                  'gMonthDay': core.modules.basic_modules.String,
                  'gDay': core.modules.basic_modules.String,
                  'gMonth': core.modules.basic_modules.String,
                  'hexBinary': core.modules.basic_modules.String,
                  'base64Binary': core.modules.basic_modules.String,
                  'Array': core.modules.basic_modules.List}

################################################################################

def initialize(*args, **keywords):
    import core.packagemanager
    global schema
    global modclient
    global modulesDict
    pm = core.packagemanager.get_package_manager()
    config = pm.get_package_configuration('webServices')
    wsdlList = []
    if config.check('wsdlList'):
        wsdlList = config.wsdlList.split(";")
        
    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    reg.add_module(WebService)

    #Create a directory for the webServices package
    global package_directory
    package_directory = core.system.default_dot_vistrails() + "/webServices"
    if not os.path.isdir(package_directory):
        try:
            print "Creating package directory..."
            os.mkdir(package_directory)
        except:
                 print "Could not create package directory. Make sure"
                 print "'%s' does not exist and parent directory is writable"
                 sys.exit(1)

    for w in wsdlList:
        #Create the stub files for the webservices that have been modified since the last time
        #they where loaded in VisTrails
        s = w.split('/')
        host = s[2]
        #create a directory for each webservice if it does not exist
        directoryname = urllib.quote_plus(w)
        package_subdirectory = core.system.default_dot_vistrails() + "/webServices/" + directoryname
        sys.path.append(package_subdirectory)

        location = w
        reader = WSDLTools.WSDLReader()
        load = reader.loadFromURL
        try:
            wsdl = load(location)
        except:
            print "Problem loading web service: ", w
            continue
        wsm = WriteServiceModule(wsdl)
        client_mod = wsm.getClientModuleName()
        types_mod = wsm.getTypesModuleName()
        client_file = join(package_subdirectory, '%s.py' %client_mod)
        types_file = join(package_subdirectory, '%s.py' %types_mod)
        
        conn = httplib.HTTPConnection(host)
        filename = '/' + '/'.join(s[3:])
        request = conn.request("GET", filename)
        response = conn.getresponse()
        remoteHeader = response.msg.getheader('last-modified')
        isoutdated = False
            
        if remoteHeader != None:
            localFile = client_file
            httpfile = HTTPFile()
            try:
                isoutdated = httpfile.is_outdated(remoteHeader, localFile)
            except OSError:
                print "File doesn't exist"
                isoutdated = True
        if isoutdated or remoteHeader == None:
            if not os.path.isdir(package_subdirectory):
                try:
                    print "Creating package subdirectory..."
                    os.mkdir(package_subdirectory)
                except:
                    print "Could not create package subdirectory. Make sure"
                    print "'%s' does not exist and parent directory is writable"
                    sys.exit(1)
            #generate the stub files
            from ZSI.generate.containers import ServiceHeaderContainer,\
                 TypecodeContainerBase, TypesHeaderContainer
            kwargs = {'module':'ZSI.generate.pyclass', 
                  'metaclass':'pyclass_type'}
            TypecodeContainerBase.metaclass = kwargs['metaclass']
            TypesHeaderContainer.imports.append(\
                  'from %(module)s import %(metaclass)s' %kwargs
                  )
            ServiceHeaderContainer.imports.append (\
                  'from %(module)s import %(metaclass)s' %kwargs
                  ) 
            fd = open(client_file, 'w+')
            wsm.writeClient(fd)
            fd.close()
        
            fd = open(types_file, 'w+' )
            wsm.writeTypes(fd)
            fd.close()
        
        #import the stub generated files
        modclient = __import__(client_mod)
        modtypes = __import__(types_mod)
        server = ServiceProxy(w, pyclass=True, tracefile=sys.stdout)
        
        #Set up the dictionary with all the complex types modules and their ports.
        keys = server._methods.keys()
        keys.sort()

        #input parameters
        for kw in keys:
            methods = server._methods[kw]
            callInfo = methods[0].callinfo
            inparams = callInfo.inparams
            for p in inparams:
                try:
                    basicType = wsdlTypesDict[str(p.type[1])]
                except KeyError:
                    for schematypes in server._wsdl.types.keys():
                        schema = server._wsdl.types[str(schematypes)]
                        if len(schema.types.keys()) != 0:
                            try:
                                complex1 = schema.types[p.type[1]]
                                modulename = str(complex1.attributes['name'])
                                try:
                                    dictkey = w + "." + modulename
                                    typeObj = modulesDict[dictkey]
                                except KeyError:
                                    #Check if it is an array.  Arrays are python lists,
                                    #not complex types though they can contain complex types elements.
                                    Type = str(p.type[1]) 
                                    if len(Type) >= 5:
                                        if (Type[0:5] != 'Array'):
                                            processType(complex1,w)
                                        else:
                                            processArray(complex1,w)    
                            except KeyError:
                                pass
                        if len(schema.elements.keys()) != 0:
                            try:
                                complex1 = schema.elements[p.type[1]]
                                modulename = str(complex1.attributes['name'])
                                try:
                                    dictkey = w + "." + modulename
                                    typeObj = modulesDict[dictkey]
                                except KeyError:
                                    #Check if it is an array.  Arrays are python lists,
                                    #not complex types, though they can contain complex types elements.
                                    Type = str(p.type[1]) 
                                    if len(Type) >= 5:
                                        if (Type[0:5] != 'Array'):
                                            processType(complex1,w)
                                        else:
                                            processArray(complex1,w)
                            except KeyError:
                                pass

        #output parameters
        for kw in keys:
            methods = server._methods[kw]
            callInfo = methods[0].callinfo
            outparams = callInfo.outparams
            for p in outparams:
                try:
                    basicType = wsdlTypesDict[str(p.type[1])]
                except KeyError:
                    for schematypes in server._wsdl.types.keys():
                        schema = server._wsdl.types[str(schematypes)]
                        if len(schema.types.keys()) != 0:
                            try:
                                complex1 = schema.types[p.type[1]]
                                modulename = str(complex1.attributes['name'])
                                try:
                                    dictkey = w + "." + modulename
                                    typeObj = modulesDict[dictkey]
                                except KeyError:
                                    Type = str(p.type[1])
                                    if len(Type) >= 5:
                                        if (Type[0:5] != 'Array'):
                                            processType(complex1,w)
                                        else:
                                            processArray(complex1,w)
                            except KeyError:
                                pass        
                        if len(schema.elements.keys()) != 0:
                            try:
                                complex1 = schema.elements[p.type[1]]
                                modulename = str(complex1.attributes['name'])
                                try:
                                    dictkey = w + "." + modulename
                                    typeObj = modulesDict[dictkey]
                                except KeyError:
                                    Type = str(p.type[1])
                                    if len(Type) >= 5:
                                        if (Type[0:5] != 'Array'):
                                            processType(complex1,w)
                                        else:
                                            processArray(complex1,w)    
                            except KeyError:
                                pass
        #get all the service's methods and for each method create a module also create
        #a module for the complex types classes and enumerations.

        #Add the Extensions if there is any in the complex types
        processExtension(server)

        #Create the VisTrails modules with their ports
        addTypesModules(w,modclient,server)
        addPortsToModules(w)
        
        #Add the Methods
        for kw in keys:
            methods = server._methods[kw]
            callInfo = methods[0].callinfo
            inparams = callInfo.inparams
            outparams = callInfo.outparams
            mt = new_module(WebService,str(kw), 
                           webServiceParamsMethodDict(str(kw),server,
                                                      inparams,
                                                      outparams))
            mt.webservice = w
            mt.modclient = modclient
            namespace = w + '|Methods'
            reg.add_module(mt, namespace= namespace)
            
            #Add the input (ports) parameters to the methods
            for p in inparams:
                try:
                    nameport = str(p.name)
                    Type = str(p.type[1]) 
                    if len(Type) >= 5:
                        if (Type[0:5] == 'Array'):
                            Type = 'Array'
                    Type = wsdlTypesDict[Type]
                    reg.add_input_port(mt,nameport,(Type, ''))
                except KeyError:
                    try:
                        modname = str(p.type[1])
                        dictkey = w + "." + modname
                        typeObj = modulesDict[dictkey]
                        Type = typeObj.type
                        reg.add_input_port(mt,str(p.name),(Type, ''))
                    except KeyError:
                        pass

            #Add the output (ports) parameters to the methods
            for p in outparams:
                try:
                    nameport = str(p.name)
                    Type = str(p.type[1]) 
                    if len(Type) >= 5:
                        if (Type[0:5] == 'Array'):
                            Type = 'Array'
                    Type = wsdlTypesDict[Type]
                    reg.add_output_port(mt,nameport,(Type, ''))
                except KeyError:
                    try:
                        modname = str(p.type[1])
                        dictkey = w + "." + modname
                        typeObj = modulesDict[dictkey]
                        Type = typeObj.type
                        reg.add_output_port(mt,str(p.name),(Type, ''))
                    except KeyError:
                        pass
