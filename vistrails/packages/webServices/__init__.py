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
It requires ZSI library to be installed. Click on
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
from PyQt4 import QtCore, QtGui
from core.modules.constant_configuration import ConstantWidgetMixin
from core.modules.basic_modules import Constant
import enumeration_widget

import subprocess
import platform
import popen2
import cPickle

package_directory = None
#Dictionary that contains the methods and complex types of all the web services
webServicesmodulesDict = {}
complexsdict ={} 

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
       self.namespace = ''
       self.webservice = ''
       self.typeobj = ''   #Enumeration, ComplexType or Method
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
               req = getattr(self.modclient,requestname)()
               #Set the values in the input ports
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
               #Set the value in the response output port
               nameport = str(WBobj.name)
               #This step is to warranty that the name are not going to repeat    
               for ports in WBobj.ports:
                   if str(WBobj.name.strip()) == str(ports[0].strip()):
                       nameport = WBobj.vistrailsname
                       break
               self.setResult(nameport,req)
           else:
               nameport = str(WBobj.name)
               for ports in WBobj.ports:
                   if str(WBobj.name.strip()) == str(ports[0].strip()):
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
                   #Set the value in the response output port
                   nameport = str(WBobj.name)
                   #This step is to warranty that the name are not going to repeat    
                   for ports in WBobj.ports:
                      if str(WBobj.name.strip()) == str(ports[0].strip()):
                         nameport = WBobj.vistrailsname
                         break
                   self.setResult(nameport,self)

   return {'compute':compute}


def webServiceParamsMethodDict(name, server, inparams, outparams):
   """ This will create a correct compute method according to the 
   inparams and outparams. Right now, only the first outparam is used
   for setting the result. """

   reg = core.modules.module_registry

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
                    dictkey = self.webservice + "|Types" 
                    complexsdict = webServicesmodulesDict[dictkey]
                    dictkey = self.webservice + "." + str(ptype)
                    obj = complexsdict[dictkey]
                    visclass = reg.get_module_by_name(identifier = identifier, name = obj.name, namespace = obj.namespace)
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
                vischildclass = reg.get_module_by_name(identifier = identifier, name = obj.name, namespace = obj.namespace)
                vischildobj = vischildclass()
                nameattrib = str(namechild)
                nameattrib = nameattrib[0].upper() + nameattrib[1:]
                #Set the attribute in the vistrail object (Same as in schema but with the first letter uppercase)
                setattr(visobj,nameattrib,vischildobj)  
                visobjchild = getattr(visobj,nameattrib)
                wrapResponseobj(self,resp,visobjchild)

   def compute(self):
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
           if isArray(Type):
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
               try:
                   resp = getattr(port,name)(request)
               except:
                   print "sys.exc_value", sys.exc_value
                   print "sys.exc_traceback", sys.exc_traceback
               #Wrap the ZSI attributes into the vistrails module attributes
               nameclass = str(outparams[0].type[1])
               dictkey = self.webservice + "|Types"
               complexsdict = webServicesmodulesDict[dictkey]
               dictkey = self.webservice + "." + nameclass
               obj = complexsdict[dictkey]
               visclass = reg.get_module_by_name(identifier = identifier, name = obj.name, namespace = obj.namespace)
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

def isArray(Type):            
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
   """ Add complex types specified in the extension base if they are not in the complex types dictionary. """
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
   """ Create a VisTrails module for each complex type specified in webservicesmodulesDict dictionary. """

   reg = core.modules.module_registry
   namespace = w + "|Types"
   complexsdict = webServicesmodulesDict[namespace]
   keys = complexsdict.keys()
   keys.sort()
   for dictkey in keys:
       obj = complexsdict[dictkey]
       obj.namespace = namespace
       if obj.typeobj == 'Enumeration':
           mt = enumeration_widget.initialize(obj.name, namespace,identifier)
       else:
           mt = new_module(WebService,str(obj.name), webServiceTypesDict(obj))
           mt.name = obj.name
           mt.webservice = w
           mt.modclient = modclient
           mt.server = server
           mt.isEnumeration = False
           mt.namespace = namespace
           reg.add_module(mt, namespace= namespace)

def addMethodsModules(w,modclient,server):
   """ Create a VisTrails module for each complex type specified in webservicesmodulesDict dictionary. """

   reg = core.modules.module_registry
   namespace = w + "|Methods"
   complexsdict = webServicesmodulesDict[namespace]
   keys = complexsdict.keys()
   keys.sort()
   for dictkey in keys:
       obj = complexsdict[dictkey]
       obj.namespace = namespace  
       mt = new_module(WebService,str(obj.name), webServiceParamsMethodDict(str(obj.name), server, obj.ports[0], obj.ports[1]))
       mt.name = obj.name
       mt.webservice = w
       mt.modclient = modclient
       mt.server = server
       mt.namespace = namespace
       reg.add_module(mt, namespace= namespace)

def addPortsToTypes(w):
   """ Add input and output ports to the VisTrails complex type modules. """

   reg = core.modules.module_registry
   dictkey = w + "|Types"
   complexsdict = webServicesmodulesDict[dictkey]
   keys = complexsdict.keys()
   for dictkey in keys:
       #Add the Ports that are of the module type
       obj = complexsdict[dictkey]
       if obj.webservice == w:
           objtype = reg.get_module_by_name(identifier = identifier, name = obj.name, namespace = obj.namespace)
           portname = obj.name
           if obj.typeobj != 'Enumeration':
              for ports in obj.ports:
                 #This step is to warranty that the name are not going to repeat
                 if str(portname.strip()) == str(ports[0].strip()):
                    obj.vistrailsname = generatename(obj.name)
                    portname = obj.vistrailsname
                    break
           reg.add_input_port(objtype,portname,(objtype, ''))
           reg.add_output_port(objtype,portname,(objtype, ''))
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

def addPortsToMethods(w):
   """ Add input and output ports to the VisTrails complex type modules. """

   reg = core.modules.module_registry
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
                   Type = reg.get_module_by_name(identifier = identifier, name = typeObj.name, namespace = typeObj.namespace)
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
                   Type = reg.get_module_by_name(identifier = identifier, name = typeObj.name, namespace = typeObj.namespace)
                   reg.add_output_port(objtype,str(port.name),(Type, ''))
               except KeyError:
                   pass        

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
   global webServicesmodulesDict
   global complexsdict

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

   createconfigfile = False
   pathfile = core.system.default_dot_vistrails() + "/webServices/modules.conf"
   if os.path.isfile(pathfile):
       #Verify if there is a need to update the modules configuration file (modules.conf)
       for w in wsdlList:
           s = w.split('/')
           host = s[2]
           location = w
           reader = WSDLTools.WSDLReader()
           load = reader.loadFromURL
           try:
              wsdl = load(location)
           except:
              continue
           directoryname = urllib.quote_plus(w)
           package_subdirectory = core.system.default_dot_vistrails() + "/webServices/" + directoryname
           wsm = WriteServiceModule(wsdl)
           client_mod = wsm.getClientModuleName()
           client_file = join(package_subdirectory, '%s.py' %client_mod)
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
               createconfigfile = True
               break
   else:
       #If the modules configuration file doesn't exist, create it
       createconfigfile = True    
   
   #If the stub files are not updated or there is not information in the header about the modification date
   #of the web service, the stubs files and a modules configuration file will be created otherwise the information
   #of the modules will be obtained from the modules.conf files that contains serialized data of the methods and
   #the complex types of the web services

   if not createconfigfile:
       namefile = core.system.default_dot_vistrails() + "/webServices/modules.conf"
       inf = open(namefile)
       webServicesmodulesDict = cPickle.load(inf)
       inf.close()
       for w in wsdlList:
           complexsdict = {} #Dictionary that contains the methods or the types of a web service
           w = w.strip()
           s = w.split('/')
           host = s[2]
           location = w
           reader = WSDLTools.WSDLReader()
           load = reader.loadFromURL
           try:
              wsdl = load(location)
           except:
              pm.show_error_message(pm.get_package_by_identifier(identifier),"Problem loading web service: %s"%w)
              continue
           
           #create a directory for each webservice if it does not exist
           directoryname = urllib.quote_plus(w)
           package_subdirectory = core.system.default_dot_vistrails() + "/webServices/" + directoryname
           sys.path.append(package_subdirectory)

           wsm = WriteServiceModule(wsdl)
           client_mod = wsm.getClientModuleName()
           types_mod = wsm.getTypesModuleName()

           #import the stub generated files
           modclient = __import__(client_mod)
           modtypes = __import__(types_mod)
           server = ServiceProxy(w, pyclass=True, tracefile=sys.stdout)

           addTypesModules(w,modclient,server)
           addPortsToTypes(w)
           addMethodsModules(w,modclient,server)
           addPortsToMethods(w)
   else:
       for w in wsdlList:
           complexsdict = {} #This dictionary stores the complex types for a webservice w
           w = w.strip()
           #Create the stub files for the webservices that have been modified since the last time
           #they where loaded in VisTrails
           s = w.split('/')
           host = s[2]
           location = w
           reader = WSDLTools.WSDLReader()
           load = reader.loadFromURL
           try:
              wsdl = load(location)
           except:
              pm.show_error_message(pm.get_package_by_identifier(identifier),"Problem loading web service: %s"%w)
              continue
           #create a directory for each webservice if it does not exist
           directoryname = urllib.quote_plus(w)
           package_subdirectory = core.system.default_dot_vistrails() + "/webServices/" + directoryname
           sys.path.append(package_subdirectory)

           wsm = WriteServiceModule(wsdl)
           client_mod = wsm.getClientModuleName()
           types_mod = wsm.getTypesModuleName()
           client_file = join(package_subdirectory, '%s.py' %client_mod)
           types_file = join(package_subdirectory, '%s.py' %types_mod)

           conn = httplib.HTTPConnection(host)
           filename = '/' + '/'.join(s[3:])
           request = conn.request("GET", filename)
           response = conn.getresponse()

           if not os.path.isdir(package_subdirectory):
               try:
                   print "Creating package subdirectory..."
                   os.mkdir(package_subdirectory)
               except:
                   print "Could not create package subdirectory. Make sure"
                   print "'%s' does not exist and parent directory is writable"
                   sys.exit(1)
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
           except:
               print "Error generating the stub files for the webservice: ", w
               continue

           #import the stub generated files
           modclient = __import__(client_mod)
           modtypes = __import__(types_mod)
           server = ServiceProxy(w, pyclass=True, tracefile=sys.stdout)

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
                               #Check if it is an array.  Arrays are python lists,
                               #not complex types though they can contain complex types elements.
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
                               #Check if it is an array.  Arrays are python lists,
                               #not complex types, though they can contain complex types elements.
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
           #get all the service's methods and for each method create a module also create
           #a module for the complex types classes and enumerations.

           #Add the Extensions if there is any in the complex types
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
               reg.add_module(mt, namespace= namespace)
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
                           Type = reg.get_module_by_name(identifier = identifier, name = typeObj.name, namespace = typeObj.namespace)
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
                           Type = reg.get_module_by_name(identifier = identifier, name = typeObj.name, namespace = typeObj.namespace)
                           reg.add_output_port(mt,str(p.name),(Type, ''))
                       except KeyError:
                           pass
               modulekey = w + "." + str(kw)
               complexsdict[modulekey] = objModule
           dictkey = w + "|Methods"
           webServicesmodulesDict[dictkey] = complexsdict        
       #Write modules.conf file that will contain the types and methods dictionary of the web services.
       namefile = core.system.default_dot_vistrails() + "/webServices/modules.conf"
       ouf = open(namefile, 'w')
       cPickle.dump(webServicesmodulesDict,ouf)
       ouf.close()
