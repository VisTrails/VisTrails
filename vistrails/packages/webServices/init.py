###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from core.bundles import py_import
from core.requirements import MissingRequirement

import sys
import os.path
import types
import httplib
import urllib
import time

ZSI = py_import('ZSI', {'linux-ubuntu': 'python-zsi',
                        'linux-fedora': 'python-ZSI'})

from ZSI.ServiceProxy import ServiceProxy
from ZSI.generate.wsdl2python import WriteServiceModule
from ZSI.wstools import WSDLTools

import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, new_module
from PyQt4 import QtCore, QtGui
from core.modules.constant_configuration import ConstantWidgetMixin
from core.modules.basic_modules import Constant
import enumeration_widget

import platform
import cPickle

package_directory = None
#Dictionary that contains the methods and complex types of all the web services
webServicesmodulesDict = {}
complexsdict ={} 

pm = core.packagemanager.get_package_manager()
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
        self.namespace = ''
        self.webservice = ''
        self.typeobj = ''   #Enumeration, ComplexType or Method.
        self.ports = []   #Have the elements of a complex type and the elements of an enumeration.
        self.attributes = []    #Have the attributes of a complex type
        self.hasAttributes = False
        self.isRequestType = False
        self.isEmptySequence = False
        self.isExtension = False
        self.ExtensionBase = ''
        self.superClass = ''

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

    def unwrapRequestobj(self,libobj,visobj):

        #Find the children for the vistrail type and set the attributes
        #Check to see if the name of the port is repeated
        portname = visobj.name
        dictkey = WBobj.webservice + "." + portname
        complexsdict = webServicesmodulesDict[WBobj.namespace] 
        obj = complexsdict[dictkey]
        for child in obj.ports:
            namechild = child[0]
            typechild = child[1]
            nameattrib = str(namechild)
            nameattrib = nameattrib[0].upper() + nameattrib[1:]
            sentence = "visobj" + "." + nameattrib
            visdata = eval(sentence)
            if visdata != None:
                try:
                    Type = wsdlTypesDict[str(typechild)]
                    setattr(libobj,nameattrib,visdata)
                except KeyError:
                    #Check if the port is an Enumeration Constant
                    keyvalue = WBobj.namespace.replace('|Types','') + "." + str(child[1])
                    childType = complexsdict[keyvalue]
                    if childType.typeobj == 'Enumeration':
                        visobjchild = getattr(visobj,nameattrib)
                        setattr(libobj, nameattrib, visobjchild)
                    else:
                        namemethod = "new_" + namechild
                        libobjchild = getattr(libobj,namemethod)()
                        visobjchild = getattr(visobj,nameattrib)
                        setattr(libobj,nameattrib,libobjchild)
                        unwrapRequestobj(self,libobjchild,visobjchild)
        if obj.hasAttributes:                
            for attributes in obj.attributes:
                nameattrib = str(attributes[0])
                nameattribute = nameattrib[0].upper() + nameattrib[1:]
                sentence = "visobj" + "." + nameattribute
                visdata = eval(sentence)
                if visdata != None:
                    nameattrib = "attribute_typecode_dict[" + nameattrib + "].pname"
                    setattr(libobj,nameattrib,visdata)

    def compute(self):
        reg = core.modules.module_registry.get_module_registry()
        #Check if it is an enumeration
        if WBobj.typeobj == 'Enumeration':
            nameport = str(WBobj.ports[0][0])
            if self.hasInputFromPort(nameport):
                inputport = self.getInputFromPort(nameport)
                self.holder = inputport
                self.setResult(WBobj.name,self)
                self.setResult('self',self)
        else:
            #Check if it is a request type
            modbyname = reg.get_module_by_name(identifier = identifier, name = WBobj.name, namespace = WBobj.namespace)
            porttype = str(modbyname.server._wsdl.portTypes.keys()[0][0][1])
            listoperations = modbyname.server._wsdl.portTypes[porttype].operations.values()
            isrequest = False
            requestname = ''
            modname = WBobj.name
            for element in listoperations:
                parts = modbyname.server._wsdl.messages[element.input.getMessage().name].parts.values()
                for part in parts:
                    if str(part.element[1]).strip() == modname.strip():
                        requestname = element.input.getMessage().name
                        isrequest = True
                        break
            if (isrequest == True):
                WBobj.isRequestType = True
                #Create the request object
                try:
                    req = getattr(self.modclient,requestname)()
                except:
                    print "sys.exc_value: ", sys.exc_value
                #Set the values of the input ports in the resquest object
                for types in WBobj.ports:
                    nameport = str(types[0])
                    if self.hasInputFromPort(nameport):
                        #We need to distinguish between simple and complex types.
                        inputport = self.getInputFromPort(nameport)
                        try:
                            Type = str(types[1])
                            if isArray(Type):
                                Type = 'Array'
                            Type = wsdlTypesDict[Type]
                            namemethod = "set_element_" + nameport
                            try:
                                getattr(req, namemethod)(inputport)
                            except:
                                namemethod = nameport
                                setattr(req, namemethod,inputport)
                        except KeyError:
                            keyvalue = WBobj.namespace.replace('|Types','') + "." + str(types[1])
                            #Check if the port is an Enumeration Constant
                            complexsdict = webServicesmodulesDict[WBobj.namespace]
                            childType = complexsdict[keyvalue]
                            if childType.typeobj == 'Enumeration':
                                namemethod = "set_element_" + nameport
                                getattr(req, namemethod)(inputport)
                            else:
                                namemethod = "new_" + nameport
                                libobj = getattr(req,namemethod)()
                                unwrapRequestobj(self,libobj,inputport)
                                namemethod = "set_element_" + nameport
                                getattr(req, namemethod)(libobj)
                if WBobj.hasAttributes:
                    for types in WBobj.attributes:
                        nameport = str(types[0])
                        if self.hasInputFromPort(nameport):
                            inputport = self.getInputFromPort(nameport)
                            Type = wsdlTypesDict[str(types[1])]
                            nameattrib = "attribute_typecode_dict[" + nameport + "].pname"
                            setattr(req, nameattrib,inputport)

                #Set the value in the response output port
                nameport = str(WBobj.name)
                #This step is to warranty that the name are not going to repeat    
                for ports in WBobj.ports:
                     if str(WBobj.name.strip()) == str(ports[0].strip()):
                         nameport = WBobj.vistrailsname
                         break
                if WBobj.hasAttributes:
                    for attributes in WBobj.attributes:
                        if str(WBobj.name.strip()) == str(attributes[0].strip()):
                            nameport = WBobj.vistrailsname
                            break
                self.setResult(nameport,req)
                self.setResult('self',req)
            else:
                nameport = str(WBobj.name)
                for ports in WBobj.ports:
                    if str(WBobj.name.strip()) == str(ports[0].strip()):
                        nameport = WBobj.vistrailsname
                        break
                if WBobj.hasAttributes:
                    for attributes in WBobj.attributes:
                        if str(WBobj.name.strip()) == str(attributes[0].strip()):
                            nameport = WBobj.vistrailsname
                            break
                if self.hasInputFromPort(nameport):
                    #Output modules
                    inputport = self.getInputFromPort(nameport)
                    for nameport in WBobj.ports:
                        nameattrib = nameport[0][0].upper() + nameport[0][1:]
                        sentence = "inputport" + "." + nameattrib
                        outputport = eval(sentence)
                        self.setResult(nameport[0],outputport)
                    if WBobj.hasAttributes:
                        for attributes in WBobj.attributes:
                            nameattrib = attributes[0][0].upper() + attributes[0][1:]
                            sentence = "inputport" + "." + nameattrib
                            outputport = eval(sentence)
                            self.setResult(attributes[0],outputport)
                elif self.hasInputFromPort('self'):
                    #Now we use the 'self' input port name
                    #we keep the old for backwards compatibility
                    #Output modules
                    inputport = self.getInputFromPort('self')
                    for nameport in WBobj.ports:
                        nameattrib = nameport[0][0].upper() + nameport[0][1:]
                        sentence = "inputport" + "." + nameattrib
                        outputport = eval(sentence)
                        self.setResult(nameport[0],outputport)
                    if WBobj.hasAttributes:
                        for attributes in WBobj.attributes:
                            nameattrib = attributes[0][0].upper() + attributes[0][1:]
                            sentence = "inputport" + "." + nameattrib
                            outputport = eval(sentence)
                            self.setResult(attributes[0],outputport)
                else:    
                    #Set the values in the input ports
                    #Input modules
                    for types in WBobj.ports:
                        nameport = str(types[0])
                        nameattrib = str(nameport)
                        nameattrib = nameattrib[0].upper() + nameattrib[1:]
                        if self.hasInputFromPort(nameport):
                            inputport = self.getInputFromPort(nameport)
                            setattr(self,nameattrib,inputport)
                        else:
                            setattr(self,nameattrib,None)
                    if WBobj.hasAttributes:
                        for types in WBobj.attributes:
                            nameport = str(types[0])
                            nameattrib = str(nameport)
                            nameattrib = nameattrib[0].upper() + nameattrib[1:]
                            if self.hasInputFromPort(nameport):
                                inputport = self.getInputFromPort(nameport)
                                setattr(self,nameattrib,inputport)
                            else:
                                setattr(self,nameattrib,None)
                    #Set the value in the response output port
                    nameport = str(WBobj.name)
                    #This step is to warranty that the name are not going to repeat    
                    for ports in WBobj.ports:
                        if str(WBobj.name.strip()) == str(ports[0].strip()):
                            nameport = WBobj.vistrailsname
                            break
                    if WBobj.hasAttributes:
                        for attributes in WBobj.attributes:
                            if str(WBobj.name.strip()) == str(attributes[0].strip()):
                                nameport = WBobj.vistrailsname
                                break
                    self.setResult(nameport,self)
                    self.setResult('self',self)

    return {'compute':compute}


def webServiceParamsMethodDict(name, server, inparams, outparams):
    """ This will create a correct compute method according to the 
    inparams and outparams. Right now, only the first outparam is used
    for setting the result. """

    reg = core.modules.module_registry.get_module_registry()

    def wrapResponseobj(self,resp,visobj):
        if type(resp)==types.ListType:
            ptype = resp[0].typecode.type[1]
        else:
            if resp.typecode.type[1] == None:
                ptype = resp.typecode.pname
            else:    
                ptype = resp.typecode.type[1]

        #Find the children for the vistrail type and set the attributes
        dictkey =  self.webservice + "|Types"        
        complexsdict = webServicesmodulesDict[dictkey]
        dictkey = self.webservice + "." + str(ptype)
        obj = complexsdict[dictkey]
        for child in obj.ports:
            namechild = child[0]
            typechild = child[1]    
            try:
                Type = wsdlTypesDict[str(typechild)]
                namemethod = "get_element_" + str(namechild)
                try:
                    ans = getattr(resp, namemethod)()
                except:
                    #Some times when there is no complex type in the wsdl
                    #the get and set methods are not generated
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
                        dictkey = self.webservice + "|Types" 
                        complexsdict = webServicesmodulesDict[dictkey]
                        dictkey = self.webservice + "." + str(ptype)
                        obj = complexsdict[dictkey]
                        visclass = reg.get_module_by_name(identifier=identifier,
                                                          name=obj.name,
                                                          namespace=obj.namespace)
                        vischildobj = visclass()
                        wrapResponseobj(self,element,vischildobj)
                        objlist.append(vischildobj)
                    nameattrib = str(namechild)
                    nameattrib = nameattrib[0].upper() + nameattrib[1:]
                    setattr(visobj,nameattrib,objlist)  
                else:
                    ptype = str(typechild)
                    dictkey = self.webservice + "|Types"
                    complexsdict = webServicesmodulesDict[dictkey]
                    dictkey = self.webservice + "." + ptype
                    obj = complexsdict[dictkey]
                    vischildclass = reg.get_module_by_name(identifier=identifier,
                                                           name=obj.name,
                                                           namespace = obj.namespace)
                    vischildobj = vischildclass()
                    nameattrib = str(namechild)
                    nameattrib = nameattrib[0].upper() + nameattrib[1:]
                    #Set the attribute in the vistrail object (Same as in
                    # schema but with the first letter uppercase)
                    setattr(visobj,nameattrib,vischildobj)  
                    visobjchild = getattr(visobj,nameattrib)
                    wrapResponseobj(self,resp,visobjchild)

    def compute(self):
        dirmodule = dir(self.modclient)
        #Get the locator name
        for elemlist in dirmodule:
            if elemlist.find('Locator') != -1:
                namelocator = elemlist
                break
        #Get the port name
        loc = getattr(self.modclient, namelocator)()
        dirloc = dir(loc)
        for elemlist in dirloc:
            if ((elemlist.find('Address') == -1) and
                ((elemlist.find('Port') != -1 and
                  elemlist.find('get') != -1) or
                 (elemlist.find('get') != -1 and
                  elemlist.find('Soap') != -1) or
                 (elemlist.find('get') != -1))):
                portname = elemlist
        port = getattr(loc, portname)()
        try:
            #This part is for the primitive or simple types methods parameters
            Type = str(inparams[0].type[1])
            if isArray(Type):
                Type = 'Array'
            Type = wsdlTypesDict[Type]
            porttype = server._wsdl.portTypes.keys()[0][0][1]
            listoperations = server._wsdl.portTypes[porttype].operations.values()
            for element in listoperations: #list of operations instances
                if str(element.name) == str(name):
                    #get the request method name
                    reqname = element.input.getMessage().name
            try:
                req = getattr(self.modclient,reqname)()
            except:
                print "sys.exc_value: ", sys.exc_value
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
            try:
                resp = getattr(port,name)(req)
            except:
                print "sys.exc_value: ", sys.exc_value
                raise ModuleError(self, str(sys.exc_value))
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
                try:
                    resp = getattr(port,name)(request)
                except:
                    print "sys.exc_value: ", sys.exc_value
                    raise ModuleError(self, str(sys.exc_value))
                #Wrap the ZSI attributes into the vistrails module attributes
                nameclass = str(outparams[0].type[1])
                dictkey = self.webservice + "|Types"
                complexsdict = webServicesmodulesDict[dictkey]
                dictkey = self.webservice + "." + nameclass
                obj = complexsdict[dictkey]
                visclass = reg.get_module_by_name(identifier=identifier,
                                                  name=obj.name,
                                                  namespace=obj.namespace)
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
    # the problem here is that sometimes we are told that complexschema is an
    # array but it is not. So if we get an AttributeError we will consider that
    # complexschema is a regular complex type.
    try:
        contentschema =  complexschema.content.content.attr_content
    except AttributeError:
        print "warning: type is not an array..."
        processType(complexschema,w)
        return
    
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

def isArray(Type):   
    #FIXME: this function not always work!!
    #Just because there's the word Array doesn't mean it will be an array (Emanuele)         
    if len(Type) > 5:
        if Type[0:5] == 'Array':
            return True
        else:
            return False

def generatename(name):
    name = name + "_1"
    return name

def processType(complexschema,w):
    
    contentschema = ''
    modulename = str(complexschema.attributes['name'])
    #print "processType: %s,%s"%(modulename,w)
    try:
        moduletype = str(complexschema.attributes['type'][1])
    except KeyError:
        moduletype = ''
    modulekey = w + "." + modulename
    objModule = WBModule(modulename)
    objModule.superClass = moduletype
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
            if (complexschema.content.content == None or
                complexschema.content.content.content == ()):
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
    try:       
        #Get all the attributes of the complex type
        if complexschema.attr_content != None:
            for attribute in complexschema.attr_content:
                nametype = attribute.getAttributeName()
                Type = 'string'
                objModule.hasAttributes = True
                objModule.attributes.append((nametype,Type))
    except AttributeError:
        pass

    #Get all the child elements of the complex type
    for child in contentschema:
        try:
            nametype = child.attributes['name']
            Type = child.attributes['type'][1]
            if isArray(Type):
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
    complexsdict [modulekey] = objModule

def addExtensionsModules(w, server, extensionbase):
    """ Add complex types specified in the extension base if they are not in
    the complex types dictionary. """
    try:
        dictkey = w + "|Types"
        complexsdict = webServicesmodulesDict[dictkey]
        dictkey = w + "." + extensionbase
        extensionobj = complexsdict[dictkey]
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

def processExtension(w, server):
    dictkey = w + "|Types"
    complexsdict = webServicesmodulesDict[dictkey]
    keys = complexsdict.keys()
    keys.sort()
    for types in keys:
        obj = complexsdict[types]
        if obj.isExtension:
            #Add extensions to modulesDict dictionary
            extensionbase = obj.ExtensionBase
            addExtensionsModules(w, server, extensionbase)
            keys2 = complexsdict.keys()
            keys2.sort()
            for types2 in keys2:
                obj2 = complexsdict[types2]
                if obj2.name == extensionbase:
                    for port in obj2.ports:
                        obj.ports.append(port)
                    break

def addTypesModules(w,modclient,server):
    """ Create a VisTrails module for each complex type specified in
    webservicesmodulesDict dictionary. """
    def addObj(obj, namespace):
        if hasattr(obj,"superClass"):
            SuperType = str(obj.superClass)
        else:
            SuperType = ''
        #print "Adding obj ", obj.name, " ", SuperType
        if SuperType != '':
            try:
                if isArray(SuperType):
                    SuperType = 'Array'
                SuperType = wsdlTypesDict[SuperType]
                mt = new_module(SuperType,str(obj.name), webServiceTypesDict(obj))
                mt.name = obj.name
                mt.webservice = w
                mt.modclient = modclient
                mt.server = server
                mt.isEnumeration = False
                mt.namespace = namespace
                #print "  add to reg: ", mt.name, namespace, identifier
                reg.add_module(mt, namespace=namespace, 
                               package=identifier, package_version=version)
            except KeyError:
                try:
                    modname = SuperType
                    dictkey = w + "|Types"
                    typedict = webServicesmodulesDict[dictkey]
                    dictkey = w + "." + modname
                    typeObj = typedict[dictkey]
                    try:
                        SuperType = reg.get_module_by_name(identifier =identifier,
                                                       name=typeObj.name,
                                                       namespace = typeObj.namespace)
                        mt = new_module(SuperType,str(obj.name), webServiceTypesDict(obj))
                        mt.name = obj.name
                        mt.webservice = w
                        mt.modclient = modclient
                        mt.server = server
                        mt.isEnumeration = False
                        mt.namespace = namespace
                        #print "  add to reg: ", mt.name, namespace, identifier
                        reg.add_module(mt, namespace=namespace, 
                               package=identifier, package_version=version)
                    except:
                        addObj(typeObj,namespace)

                except KeyError:
                    pass
        else:
            mt = new_module(WebService,str(obj.name), webServiceTypesDict(obj))
            mt.name = obj.name
            mt.webservice = w
            mt.modclient = modclient
            mt.server = server
            mt.isEnumeration = False
            mt.namespace = namespace
            #print "  add to reg: ", mt.name, namespace, identifier
            reg.add_module(mt, namespace=namespace, 
                           package=identifier, package_version=version)    
             
    reg = core.modules.module_registry.get_module_registry()
    namespace = w + "|Types"
    complexsdict = webServicesmodulesDict[namespace]
    keys = complexsdict.keys()
    keys.sort()
    for dictkey in keys:
        obj = complexsdict[dictkey]
        #print "key: ", dictkey, " obj: ", obj.name
        obj.namespace = namespace
        if obj.typeobj == 'Enumeration':
            mt = enumeration_widget.initialize(obj.name, namespace,identifier,
                                               version)
        else:
            
            addObj(obj,namespace)
            #mt = new_module(WebService,str(obj.name), webServiceTypesDict(obj))
            #mt.name = obj.name
            #mt.webservice = w
            #mt.modclient = modclient
            #mt.server = server
            #mt.isEnumeration = False
            #mt.namespace = namespace
            #reg.add_module(mt, namespace=namespace, 
            #               package=identifier, package_version=version)

def addMethodsModules(w,modclient,server):
    """ Create a VisTrails module for each complex type specified in
    webservicesmodulesDict dictionary. """

    reg = core.modules.module_registry.get_module_registry()
    namespace = w + "|Methods"
    complexsdict = webServicesmodulesDict[namespace]
    keys = complexsdict.keys()
    keys.sort()
    for dictkey in keys:
        obj = complexsdict[dictkey]
        obj.namespace = namespace  
        mt = new_module(WebService,str(obj.name),
                        webServiceParamsMethodDict(str(obj.name), server,
                                                   obj.ports[0], obj.ports[1]))
        mt.name = obj.name
        mt.webservice = w
        mt.modclient = modclient
        mt.server = server
        mt.namespace = namespace
        reg.add_module(mt, namespace= namespace, package=identifier,
                       package_version=version)

def addPortsToTypes(w):
    """ Add input and output ports to the VisTrails complex type modules. """

    reg = core.modules.module_registry.get_module_registry()
    dictkey = w + "|Types"
    complexsdict = webServicesmodulesDict[dictkey]
    keys = complexsdict.keys()
    for dictkey in keys:
        #Add the Ports that are of the module type
        obj = complexsdict[dictkey]
        if obj.webservice == w:
            objtype = reg.get_module_by_name(identifier=identifier,
                                             name=obj.name,
                                             namespace=obj.namespace)
            #print "Adding ports to ", obj.name
            portname = 'self'
            if obj.typeobj != 'Enumeration':
                for ports in obj.ports:
                    #This step is to warranty that the name are not going
                    #to repeat
                    #print " > ", ports
                    if str(portname.strip()) == str(ports[0].strip()):
                        obj.vistrailsname = generatename(portname)
                        portname = obj.vistrailsname
                        break    
                if obj.hasAttributes:
                    for attributes in obj.attributes:
                        #This step is to warranty that the name are not
                        #going to repeat
                        if str(portname.strip()) == str(attributes[0].strip()):
                            obj.vistrailsname = generatename(portname)
                            portname = obj.vistrailsname
                            break
            reg.add_input_port(objtype,portname,(objtype, ''))
            reg.add_output_port(objtype,portname,(objtype, ''))
            
            # this is to keep compatibility with previous versions
            # we will add as optional ports.
            reg.add_input_port(objtype,obj.name,(objtype, ''), optional=True)
            reg.add_output_port(objtype,obj.name,(objtype, ''), optional=True)
            
            if obj.typeobj != 'Enumeration':
                #Add ports according to the input and output parameters
                for ports in obj.ports:
                    try:
                        Type = wsdlTypesDict[str(ports[1])]
                    except KeyError:
                        portname = str(ports[1])
                        namespace = w + '|Types'
                        Type = reg.get_module_by_name(identifier = identifier, name =portname, namespace = namespace)
                    reg.add_input_port(objtype,str(ports[0]),(Type, ''))
                    reg.add_output_port(objtype,str(ports[0]),(Type, ''))
            if obj.hasAttributes == True:
                for attributes in obj.attributes:
                    Type = wsdlTypesDict[str(attributes[1])]
                    reg.add_input_port(objtype,str(attributes[0]),(Type, ''))
                    reg.add_output_port(objtype,str(attributes[0]),(Type, ''))

def addPortsToMethods(w):
    """ Add input and output ports to the VisTrails complex type modules. """

    reg = core.modules.module_registry.get_module_registry()
    dictkey = w + "|Methods"
    complexsdict = webServicesmodulesDict[dictkey]
    keys = complexsdict.keys()
    for dictkey in keys:
        obj = complexsdict[dictkey]
        objtype = reg.get_module_by_name(identifier = identifier, name = obj.name, namespace = obj.namespace)
        #Add input ports
        for port in obj.ports[0]:
            try:
                nameport = str(port.name)
                Type = str(port.type[1])
                if isArray(Type):
                    Type = 'Array'
                Type = wsdlTypesDict[Type]
                reg.add_input_port(objtype,nameport,(Type, ''))
            except KeyError:
                try:
                    modname = str(port.type[1])
                    dictkey = w + "|Types"
                    typedict = webServicesmodulesDict[dictkey]
                    dictkey = w + "." + modname
                    typeObj = typedict[dictkey]
                    Type = reg.get_module_by_name(identifier=identifier,
                                                  name=typeObj.name,
                                                  namespace=typeObj.namespace)
                    reg.add_input_port(objtype,str(port.name),(Type, ''))
                except KeyError:
                    pass
        #Add output ports        
        for port in obj.ports[1]:
            try:
                nameport = str(port.name)
                Type = str(port.type[1])
                if isArray(Type):
                    Type = 'Array'
                Type = wsdlTypesDict[Type]
                reg.add_output_port(objtype,nameport,(Type, ''))
            except KeyError:
                try:
                    modname = str(port.type[1])
                    dictkey = w + "|Types"
                    typedict = webServicesmodulesDict[dictkey]
                    dictkey = w + "." + modname
                    typeObj = typedict[dictkey]
                    Type = reg.get_module_by_name(identifier=identifier,
                                                  name=typeObj.name,
                                                  namespace=typeObj.namespace)
                    reg.add_output_port(objtype,str(port.name),(Type, ''))
                except KeyError:
                    pass        

#Dictionary of primitive types
#list extracted from http://www.w3.org/2001/XMLSchema
wsdlTypesDict = { 'string' : core.modules.basic_modules.String,
                'float': core.modules.basic_modules.Float,
                'decimal': core.modules.basic_modules.Float,
                'double': core.modules.basic_modules.Float,
                'boolean': core.modules.basic_modules.Boolean,
                'anyType': core.modules.basic_modules.Variant,
                'anyURI': core.modules.basic_modules.String,
                'DataHandler':core.modules.basic_modules.String,
                'dateTime': core.modules.basic_modules.String,
                'duration': core.modules.basic_modules.String,
                'time': core.modules.basic_modules.String,
                'date': core.modules.basic_modules.String,
                'gYearMonth': core.modules.basic_modules.String,
                'gYear': core.modules.basic_modules.String,
                'gMonthDay': core.modules.basic_modules.String,
                'gDay': core.modules.basic_modules.String,
                'gMonth': core.modules.basic_modules.String,
                'hexBinary': core.modules.basic_modules.String,
                'base64Binary': core.modules.basic_modules.String,
                'QName': core.modules.basic_modules.String,
                'normalizedString': core.modules.basic_modules.String,
                'token': core.modules.basic_modules.String,
                'language': core.modules.basic_modules.String,
                'IDREFS': core.modules.basic_modules.String,
                'ENTITIES': core.modules.basic_modules.String,
                'NMTOKEN': core.modules.basic_modules.String,
                'NMTOKENS': core.modules.basic_modules.String,
                'Name': core.modules.basic_modules.String,
                'NCName': core.modules.basic_modules.String,
                'ID': core.modules.basic_modules.String,
                'IDREF': core.modules.basic_modules.String,
                'ENTITY': core.modules.basic_modules.String,
                'integer' : core.modules.basic_modules.Integer,
                'nonPositiveInteger' : core.modules.basic_modules.Integer,
                'negativeInteger' : core.modules.basic_modules.Integer,
                'long' : core.modules.basic_modules.Integer,
                'int' : core.modules.basic_modules.Integer,
                'short' : core.modules.basic_modules.Integer,
                'byte' : core.modules.basic_modules.Integer,
                'nonNegativeInteger' : core.modules.basic_modules.Integer,
                'unsignedLong' : core.modules.basic_modules.Integer,
                'unsignedInt' : core.modules.basic_modules.Integer,
                'unsignedShort' : core.modules.basic_modules.Integer,
                'unsignedByte' : core.modules.basic_modules.Integer,
                'positiveInteger' : core.modules.basic_modules.Integer,
                'Array': core.modules.basic_modules.List}

################################################################################
def load_wsdl_no_config(wsdlList):
    """load_wsdl_no_config(wsdlList: list of urls) -> (bool, errors)
    This loads the wsdl list without creating config files.
    Returns a tuple with two values. The first is a boolean that is True
    in case of success. The second is a list with problematic urls.
    
    """
    global complexsdict
    result = True
    not_loaded = []
    for w in wsdlList:
        # Validation if the user introduces a blank space in the list of web
        # services
        if w == '':
            continue
        complexsdict = {} #Dictionary that contains the methods or the
                          #types of a web service
        w = w.strip()
        numtimes = 0
        for element in wsdlList:
            if w == element.strip():
                numtimes = numtimes + 1
        if numtimes > 1:
            # as this is not a big problem, let's just print on the console
            print "Warning: Web service '%s' is repeated in the list and won't \
be loaded again." % w
            # this is not a problem, we will just ignore it
            continue
        try:
            s = w.split('/')
            host = s[2]
        except:
            msg = "Malformed URL."
            not_loaded.append((w,msg))
            result = False
            continue
        location = w
        try:
            reader = WSDLTools.WSDLReader()
            wsdl = reader.loadFromURL(location)
            
        except Exception, e:
            # we will not show this every time. Just in the end
            # so we can show a single message for everybody
            not_loaded.append((w,str(e)))
            result = False
            continue

        #create a directory for each webservice if it does not exist
        package_directory = os.path.join(core.system.default_dot_vistrails(),
                                        "webServices")
        sys.path.append(package_directory)
        directoryname = urllib.quote_plus(w)
        directoryname = directoryname.replace(".","_")
        directoryname = directoryname.replace("%","_")
        directoryname = directoryname.replace("+","_")
        package_subdirectory = os.path.join(package_directory, directoryname)
        wsm = WriteServiceModule(wsdl)
        client_mod = wsm.getClientModuleName()
        types_mod = wsm.getTypesModuleName()

        #import the stub generated files
        try:
            importpackage = __import__(directoryname)
            modclient = getattr(importpackage,client_mod)
            server = ServiceProxy(w, pyclass=True, tracefile=sys.stdout)
        except Exception, e:
            msg =  "Couldn't load generated stub file: %s"%str(e)
            not_loaded.append((w,msg))
            result = False
            continue
        
        addTypesModules(w,modclient,server)
        addPortsToTypes(w)
        addMethodsModules(w,modclient,server)
        addPortsToMethods(w)
    return (result, not_loaded)

def load_wsdl_with_config(wsdlList):
    """load_wsdl_with_config(wsdlList: list of urls) -> (bool,list)
    This loads the wsdl list creating config files.
    Returns a tuple with two values. The first is a boolean that is True
    in case of success. The second is a list with problematic urls"""
    
    global schema
    global webServicesmodulesDict
    global complexsdict
    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules
    not_loaded = []
    result = True
    for w in wsdlList:
        #Validation if the user introduces a blank space in the list of
        #web services
        if w == '':
            continue
        complexsdict = {} #This dictionary stores the complex types for
                          #a webservice w
        w = w.strip()
        #Check to see if the element is not repeated in the web services list
        numtimes = 0
        for element in wsdlList:
            if w == element.strip():
                numtimes = numtimes + 1
        if numtimes > 1:
            print "The following web service is repeated in the list and won't \
be loaded again: %s"% w
            continue
          
        #Create the stub files for the webservices that have been
        # modified since the last time they where loaded in VisTrails
        try:
            s = w.split('/')
            host = s[2]
        except:
            msg = "Malformed URL."
            not_loaded.append((w,msg))
            result = False
            continue
        location = w
        ok = 0 # Trying to load a few times
               # a couple of times, because sometimes we have timeout
        msg = ''
        while ok < 3:
            try:
                reader = WSDLTools.WSDLReader()
                wsdl = reader.loadFromURL(location)
                ok = 4
                failed = False
            except Exception, e:
                ok += 1
                failed = True
                msg = str(e)

        if failed:
            not_loaded.append((w,msg))
            result = False
            continue
        #create a directory for each webservice if it does not exist
        directoryname = urllib.quote_plus(w)
        directoryname = directoryname.replace(".","_")
        directoryname = directoryname.replace("%","_")
        directoryname = directoryname.replace("+","_")

        package_directory = os.path.join(core.system.default_dot_vistrails(),
                                         "webServices")
        sys.path.append(package_directory)
        package_subdirectory = os.path.join(package_directory,
                                            directoryname)
        
        wsm = WriteServiceModule(wsdl)
        client_mod = wsm.getClientModuleName()
        types_mod = wsm.getTypesModuleName()
        client_file = os.path.join(package_subdirectory, '%s.py' %client_mod)
        types_file = os.path.join(package_subdirectory, '%s.py' %types_mod)
        filename = '__init__'
        init_file = os.path.join(package_subdirectory, '%s.py' %filename)
        conn = httplib.HTTPConnection(host)
        filename = '/' + '/'.join(s[3:])
        request = conn.request("GET", filename)
        response = conn.getresponse()
        if not os.path.isdir(package_subdirectory):
            try:
                print "Creating package subdirectory...",
                os.mkdir(package_subdirectory)
                print "done."
            except:
                msg = "\nCould not create package subdirectory. Make sure \
'%s' does not exist and parent directory is writable." % package_subdirectory
                print "Skipping '%s'" % w
                # We don't need to exit here. Continuing try to load
                # the other files
                not_loaded.append((w,msg))
                result = False
                continue
                
        #generate the stub files
        try:
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
              
            fd = open(init_file, 'w')
            content = 'import ' + client_mod
            fd.write(content)
            fd.close()
        except Exception, e:
            msg = "Couldn't generate stub file: %s"% str(e)
            not_loaded.append((w,msg))
            result = False
            continue
        #import the stub generated files
        try:
            importpackage = __import__(directoryname)
            modclient = getattr(importpackage,client_mod)
            server = ServiceProxy(w, pyclass=True, tracefile=sys.stdout)
        except Exception, e:
            msg = "Problem importing the generated stub files: %s", str(e)
            not_loaded.append((w,msg))
            result = False
            continue

        #Set up the dictionary with all the complex types modules and their ports.
        for schematypes in server._wsdl.types.keys():
            schema = server._wsdl.types[str(schematypes)]
            if len(schema.types.keys()) != 0:
                for schematype in schema.types.keys():
                    try:
                        complex1 = schema.types[str(schematype)]
                        modulename = str(complex1.attributes['name'])
                        try:
                            dictkey = w + "." + modulename
                            typeObj = complexsdict[dictkey]
                        except KeyError:
                            #Check if it is an array.  Arrays are python
                            #lists, not complex types though they can
                            #contain complex types elements.
                            Type = str(schematype)
                            if isArray(Type):
                                processArray(complex1,w)
                            else:
                                processType(complex1,w)
                    except KeyError:
                        pass
            if len(schema.elements.keys()) != 0:
                for schematype in schema.elements.keys():
                    try:
                        complex1 = schema.elements[str(schematype)]
                        modulename = str(complex1.attributes['name'])
                        try:
                            dictkey = w + "." + modulename
                            typeObj = complexsdict[dictkey]
                        except KeyError:
                            #Check if it is an array.  Arrays are python
                            #lists, not complex types, though they can
                            #contain complex types elements.
                            Type = str(schematype)
                            if isArray(Type):
                                processArray(complex1,w)
                            else:
                                processType(complex1,w)
                    except KeyError:
                        pass
        dictkey = w + "|Types"
        webServicesmodulesDict[dictkey] = complexsdict            
        complexsdict = {}
        #get all the service's methods and for each method create a
        #module also create
        # a module for the complex types classes and enumerations.
        
        # Add the Extensions if there is any in the complex types
        processExtension(w,server)

        #Create the VisTrails modules with their ports
        addTypesModules(w,modclient,server)

        addPortsToTypes(w)

        #Open the file with methods
        #Add the Methods
        keys = server._methods.keys()
        keys.sort()
        
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
            mt.namespace = namespace
            
            reg.add_module(mt, namespace= namespace, package=identifier,
                           package_version=version)
            
            objModule = WBModule(kw)
            objModule.namespace = namespace
            objModule.webservice = w
            objModule.typeobj = 'Method'
            objModule.ports.append(inparams)
            objModule.ports.append(outparams)
            #Add the input (ports) parameters to the methods
            for p in inparams:
                try:
                    nameport = str(p.name)
                    Type = str(p.type[1])
                    if isArray(Type):
                        Type = 'Array'
                    Type = wsdlTypesDict[Type]
                    reg.add_input_port(mt,nameport,(Type, ''))
                except KeyError:
                    try:
                        modname = str(p.type[1])
                        dictkey = w + "|Types"
                        typedict = webServicesmodulesDict[dictkey]
                        dictkey = w + "." + modname
                        typeObj = typedict[dictkey]
                        Type = reg.get_module_by_name(identifier =identifier,
                                                      name=typeObj.name,
                                                      namespace = typeObj.namespace)
                        reg.add_input_port(mt,str(p.name),(Type, ''))
                    except KeyError:
                        pass
            #Add the output (ports) parameters to the methods
            for p in outparams:
                try:
                    nameport = str(p.name)
                    Type = str(p.type[1])
                    if isArray(Type):
                        Type = 'Array'
                    Type = wsdlTypesDict[Type]
                    reg.add_output_port(mt,nameport,(Type, ''))
                except KeyError:
                    try:
                        modname = str(p.type[1])
                        dictkey = w + "|Types"
                        typedict = webServicesmodulesDict[dictkey]
                        dictkey = w + "." + modname
                        typeObj = typedict[dictkey]
                        Type = reg.get_module_by_name(identifier=identifier,
                                                      name=typeObj.name,
                                                      namespace = typeObj.namespace)
                        reg.add_output_port(mt,str(p.name),(Type, ''))
                    except KeyError:
                        pass
            modulekey = w + "." + str(kw)
            complexsdict[modulekey] = objModule
        dictkey = w + "|Methods"
        webServicesmodulesDict[dictkey] = complexsdict        
    #Write modules.conf file that will contain the types and methods
    #dictionary of the web services.
    namefile = os.path.join(core.system.default_dot_vistrails(),
                            'webServices',
                            'modules.conf')    
    try:
        ouf = open(namefile, 'w')
        cPickle.dump(webServicesmodulesDict,ouf)
        ouf.close()
    except Exception, e:
        msg = "Error generating web services configuration file %s"%str(e)
        raise Exception(msg)

    return(result,not_loaded)
        
def verify_wsdl(wsdlList):
    """verify_wsdl(wsdlList: list of urls) -> (list,list,list)

    This checks for the wsdls that need to be updated or the files need to be
    generated and splits them in 3 lists: files that are outdated, updated and
    ones that an error was generated.
    
    """
    outdated_list = []
    updated_list = []
    error_list = []
    for w in wsdlList:
        if w == '':
            continue
        try:
            s = w.split('/')
            host = s[2]
        except:
            msg = "Malformed URL."
            error_list.append((w,msg))
            continue
        location = w
        reader = WSDLTools.WSDLReader()
        load = reader.loadFromURL
        try:
            wsdl = load(location)
        except Exception, e:
            msg = "Couldn't load wsdl from the web: %s."%str(e)
            error_list.append((w,msg))
            continue
        directoryname = urllib.quote_plus(w)
        directoryname = directoryname.replace(".","_")
        directoryname = directoryname.replace("%","_")
        directoryname = directoryname.replace("+","_")
        package_subdirectory = os.path.join(core.system.default_dot_vistrails(),
                                            "webServices",
                                            directoryname)
        wsm = WriteServiceModule(wsdl)
        client_mod = wsm.getClientModuleName()
        client_file = os.path.join(package_subdirectory, '%s.py' %client_mod)
        conn = httplib.HTTPConnection(host)
        filename = '/' + '/'.join(s[3:])
        request = conn.request("GET", filename)
        response = conn.getresponse()
        remoteHeader = response.msg.getheader('last-modified')
        isoutdated = False
        if remoteHeader != None:
            localFile = client_file
            reg = core.modules.module_registry.get_module_registry()
            httpfile = reg.get_descriptor_by_name('edu.utah.sci.vistrails.http',
                                                  'HTTPFile').module()
            try:
                isoutdated = httpfile._is_outdated(remoteHeader, localFile)
            except OSError:
                print "File doesn't exist"
                isoutdated = True
        if isoutdated or remoteHeader == None:
            outdated_list.append(w)
        else:
            updated_list.append(w)
    return (outdated_list,updated_list, error_list)
            
def initialize(*args, **keywords):
    import core.packagemanager
    global schema
    global webServicesmodulesDict
    global complexsdict
    wsdlList = []
    if configuration.showWarning == True:
        msg = "The Web Services package is deprecated and will be removed from \
next VisTrails release. Please consider using the new SUDS Web Services package. \
This message will not be shown again."
        pm.show_error_message(pm.get_package_by_identifier(identifier),msg)
        try:
            from gui.application import get_vistrails_application
            if get_vistrails_application() is not None:
                configuration.showWarning = False
                VisTrailsApplication.save_configuration()
        except:
            pass
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")

    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules
    reg.add_module(WebService)

    #Create a directory for the webServices package
    global package_directory
    package_directory = os.path.join(core.system.default_dot_vistrails(),
                                     "webServices")
    if not os.path.isdir(package_directory):
        try:
            print "Creating package directory..."
            os.mkdir(package_directory)
        except:
            print "Could not create package directory. Make sure"
            print "'%s' does not exist and parent directory is writable"
            sys.exit(1)

    pathfile = os.path.join(core.system.default_dot_vistrails(),
                            "webServices",
                            "modules.conf")
    outdated_list = []
    updated_list = []
    error_list = []
    if os.path.isfile(pathfile):
        #Verify if there is a need to update the modules configuration
        #file (modules.conf)
         (outdated_list, updated_list, error_list) = verify_wsdl(wsdlList)
             
    else:
        #If the modules configuration file doesn't exist, create it
        outdated_list = wsdlList 

        #If the stub files are not updated or there is not information in
        # the header about the modification date of the web service, the
        # stubs files and a modules configuration file will be created
        # otherwise the information of the modules will be obtained from
        # the modules.conf files that contains serialized data of the methods
        # and the complex types of the web services
    if os.path.isfile(pathfile):
        try: 
            inf = open(pathfile)
            webServicesmodulesDict = cPickle.load(inf)
            inf.close()
        except Exception, e:
            msg = "Error loading configuration file: ", pathfile
            raise Exception(msg)
    
    #print wsdlList, outdated_list, updated_list
    (res, not_loaded) = load_wsdl_no_config(updated_list)
    if not res:
        #there was a problem when trying to load the stubs
        # let's try creating them again
        for (w,e) in not_loaded:
            outdated_list.append(w)
        print "There were problems loading the webservices %s" % not_loaded
        print "We will try to load them again..."
    (res, not_loaded) = load_wsdl_with_config(outdated_list)
    if not res or len(error_list) > 0:
        msg = """ There were problems loading the webservices.
The following could not be loaded:\n"""
        error_list.extend(not_loaded)
        for (w,e) in error_list:
            msg += "Url: '%s', error: '%s'\n"%(w,e)
        pm.show_error_message(pm.get_package_by_identifier(identifier),msg)

def handle_missing_module(*args, **kwargs):
    global webServicesmodulesDict
    
    #this is the order the arguments are passed to the function
    controller = args[0]
    m_id = args[1]
    pipeline = args[2]
    
    def get_wsdl_from_namespace(m_namespace):
        try:
            wsdl = m_namespace.split("|")
            return wsdl[0]
        except:
            print "invalid namespace"
            return None
    m = pipeline.modules[m_id]
    m_namespace = m.namespace
    
    wsdl = get_wsdl_from_namespace(m_namespace)
    if wsdl:
        outdated_list = []
        updated_list = []
        error_list = []
        print "Downloading %s and adding to the Module list..."%wsdl
        pathfile = os.path.join(core.system.default_dot_vistrails(),
                                "webServices",
                                "modules.conf")
        if os.path.isfile(pathfile):
            #Verify if there is a need to update the modules configuration
            #file (modules.conf)
            (outdated_list, updated_list, error_list) = verify_wsdl([wsdl])
            #print "verified: createconfig file is %s"%createconfigfile
        else:
            #If the modules configuration file doesn't exist, create it
            outdated_list = [wsdl]
        
        #If the stub files are not updated or there is not information in
        # the header about the modification date of the web service, the
        # stubs files and a modules configuration file will be created
        # otherwise the information of the modules will be obtained from
        # the modules.conf files that contains serialized data of the methods
        # and the complex types of the web services
        # print outdated_list, updated_list, error_list
        if os.path.isfile(pathfile):
            try: 
                inf = open(pathfile)
                webServicesmodulesDict = cPickle.load(inf)
                inf.close()
            except:
                print "Error loading configuration file"
                return False
        try:
            (res,not_loaded) = load_wsdl_no_config(updated_list)
            #print "done loading_no_config"
            if not res:
                outdated_list.extend([wsdl])
        
            (res, not_loaded) = load_wsdl_with_config(outdated_list)
            #print "done loading_with_config"
            if res:
                #add new url to package config file
                wsdlList = []
                if configuration.check('wsdlList'):
                    wsdlList = configuration.wsdlList.split(";")
                if wsdl not in wsdlList:
                    wsdlList.append(wsdl)    
                swsdlList = ";".join(wsdlList)
                configuration.wsdlList = swsdlList
                print "done."
                return True
            else:
                msg = """ There were problems loading the webservice.
The following could not be loaded:\n"""
                error_list.extend(not_loaded)
                for (w,e) in error_list:
                    msg += "Url: '%s', error: '%s'\n"%(w,e)
                    pm.show_error_message(pm.get_package_by_identifier(identifier),msg)
        except Exception, e:
            print e
            import traceback
            traceback.print_stack()
    print "An error occurred. Could not add missing wsdl."
    return False
