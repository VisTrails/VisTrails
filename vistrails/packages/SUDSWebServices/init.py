###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

import sys
import os.path
import shutil
import hashlib
import vistrails.core.system
import vistrails.core.modules.module_registry
import vistrails.core.modules.basic_modules
import traceback
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.modules.package import Package
from vistrails.core.modules.vistrails_module import Module, ModuleError, new_module
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
from vistrails.core import debug

import suds


package_cache = None

webServicesDict = {}

def toSignature(s):
    """ transform wsdl address to valid package signature """
    # cannot have ':' in package name
    return 'SUDS#' + s.replace(':', '$')

def toAddress(s):
    """ transform package signature to valid wsdl address """
    # look up address for a specific signature
    return s[5:].replace('$', ':')

###############################################################################

wsdlSchemas = ['http://www.w3.org/2001/XMLSchema',
              'http://xml.apache.org/xml-soap',
              'http://schemas.xmlsoap.org/soap/encoding/']
#Dictionary of primitive types
#list extracted from http://www.w3.org/2001/XMLSchema
wsdlTypesDict = { 'string' : vistrails.core.modules.basic_modules.String,
                'float': vistrails.core.modules.basic_modules.Float,
                'decimal': vistrails.core.modules.basic_modules.Float,
                'double': vistrails.core.modules.basic_modules.Float,
                'boolean': vistrails.core.modules.basic_modules.Boolean,
                'anyType': vistrails.core.modules.basic_modules.Variant,
                'anyURI': vistrails.core.modules.basic_modules.String,
                'DataHandler':vistrails.core.modules.basic_modules.String,
                'dateTime': vistrails.core.modules.basic_modules.String,
                'duration': vistrails.core.modules.basic_modules.String,
                'time': vistrails.core.modules.basic_modules.String,
                'date': vistrails.core.modules.basic_modules.String,
                'gYearMonth': vistrails.core.modules.basic_modules.String,
                'gYear': vistrails.core.modules.basic_modules.String,
                'gMonthDay': vistrails.core.modules.basic_modules.String,
                'gDay': vistrails.core.modules.basic_modules.String,
                'gMonth': vistrails.core.modules.basic_modules.String,
                'hexBinary': vistrails.core.modules.basic_modules.String,
                'base64': vistrails.core.modules.basic_modules.String,
                'base64Binary': vistrails.core.modules.basic_modules.String,
                'QName': vistrails.core.modules.basic_modules.String,
                'normalizedString': vistrails.core.modules.basic_modules.String,
                'token': vistrails.core.modules.basic_modules.String,
                'language': vistrails.core.modules.basic_modules.String,
                'IDREFS': vistrails.core.modules.basic_modules.String,
                'ENTITIES': vistrails.core.modules.basic_modules.String,
                'NMTOKEN': vistrails.core.modules.basic_modules.String,
                'NMTOKENS': vistrails.core.modules.basic_modules.String,
                'Name': vistrails.core.modules.basic_modules.String,
                'NCName': vistrails.core.modules.basic_modules.String,
                'ID': vistrails.core.modules.basic_modules.String,
                'IDREF': vistrails.core.modules.basic_modules.String,
                'ENTITY': vistrails.core.modules.basic_modules.String,
                'integer' : vistrails.core.modules.basic_modules.Integer,
                'nonPositiveInteger' : vistrails.core.modules.basic_modules.Integer,
                'negativeInteger' : vistrails.core.modules.basic_modules.Integer,
                'long' : vistrails.core.modules.basic_modules.Integer,
                'int' : vistrails.core.modules.basic_modules.Integer,
                'short' : vistrails.core.modules.basic_modules.Integer,
                'byte' : vistrails.core.modules.basic_modules.Integer,
                'nonNegativeInteger' : vistrails.core.modules.basic_modules.Integer,
                'unsignedLong' : vistrails.core.modules.basic_modules.Integer,
                'unsignedInt' : vistrails.core.modules.basic_modules.Integer,
                'unsignedShort' : vistrails.core.modules.basic_modules.Integer,
                'unsignedByte' : vistrails.core.modules.basic_modules.Integer,
                'positiveInteger' : vistrails.core.modules.basic_modules.Integer,
                'Array': vistrails.core.modules.basic_modules.List,

                # soapenc types
                'arrayCoordinate': vistrails.core.modules.basic_modules.String,
                'Struct': vistrails.core.modules.basic_modules.String,
                'NOTATION': vistrails.core.modules.basic_modules.String                
                }

def initialize(*args, **keywords):
#    import core.packagemanager
    global webServicesDict
    global package_cache

    #Create a directory for the SUDSWebServices package
    location = os.path.join(vistrails.core.system.current_dot_vistrails(),
                            "SUDSWebServices")
    if not os.path.isdir(location):
        try:
            debug.log("Creating SUDS cache directory...")
            os.mkdir(location)
        except OSError, e:
            debug.critical(
"""Could not create SUDS cache directory. Make sure
'%s' does not exist and parent directory is writable""" % location, e)
            sys.exit(1)
    # the number of days to cache wsdl files
    days = 1
    if configuration.check("cache_days"):
        days = configuration.cache_days
    suds.client.ObjectCache.protocol = 0 # windows needs this
    package_cache = suds.client.ObjectCache(location, days=days)

    #reg = core.modules.module_registry.get_module_registry()
    #reg.add_module(SUDSWebService, abstract=True)

    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    else:
        configuration.wsdlList = ''
    for wsdl in wsdlList:
        if not wsdl:
            break
        if not wsdl.startswith('http://'):
            wsdl = 'http://' + wsdl
        if wsdl in webServicesDict:
            debug.warning('Duplicate WSDL entry: '+wsdl)
            continue
        s = Service(wsdl)
        if s.service:
            webServicesDict[wsdl] = s
        
def finalize():
    # unload service packages
    reg = vistrails.core.modules.module_registry.get_module_registry()
    for s in webServicesDict.itervalues():
        if s.package:
            reg.remove_package(s.package)

class WSMethod(object):
    """ A WSDL method
    """
    def __init__(self, qname=('','')):
        self.qname = qname
        "name: (typename, ns)"
        self.inputs = {}
        self.outputs = {}

class WSElement(object):
    """ A part of a WSDL type
    """
    def __init__(self, name='', type=('',''), optional=False, min=0,
                 max='unbounded', enum=False):
        self.name = name
        self.type = type
        self.optional = optional
        self.min = min
        self.max = max
        self.enum = enum

class WSType(object):
    """ A WSDL type definition
    """
    def __init__(self, qname=('',''), enum=False):
        self.qname = qname
        self.enum = enum
        "name: WSElement"
        self.parts = {}
 
class Service(object):
    def __init__(self, address):
        """ Process WSDL and add all Types and Methods
        """
        self.address = address
        self.signature = toSignature(self.address)
        self.wsdlHash = '-1'
        self.modules = []
        self.package = None
        debug.log("Installing Web Service from WSDL: %s"% address)

        options = dict(cachingpolicy=1, cache=package_cache)
        
        proxy_types = ['http']
        for t in proxy_types:
            key = 'proxy_%s'%t
            if configuration.check(key):
                proxy = getattr(configuration, key)
                debug.log("Using proxy: %s" % proxy)
                if len(proxy):
                    options['proxy'] = {t:proxy}
        try:
            self.service = suds.client.Client(address, **options)
            self.backUpCache()
        except Exception:
            self.service = None
            # We may be offline and the cache may have expired,
            # try to use backup
            if self.restoreFromBackup():
                try:
                    self.service = suds.client.Client(address, **options)
                except Exception:
                    self.service = None
                    debug.critical("Could not load WSDL: %s" % address,
                                   traceback.format_exc())
            else:
                debug.critical("Could not load WSDL: %s" % address,
                               traceback.format_exc())
        if self.service:
            try:
                self.createPackage()
                self.setTypes()
                self.setMethods()
                self.createTypeClasses()
                self.createMethodClasses()
            except Exception:
                debug.critical("Could not create Web Service: %s" % address,
                               traceback.format_exc())
                self.service = None
        if self.wsdlHash == '-1':
            # create empty package so that it can be reloaded/deleted
            self.createFailedPackage()
        
    def makeDictType(self, obj):
        """ Create recursive dict from SUDS object
            ignore attributes with None and empty dicts and handle lists
        """
        if not hasattr(obj,'__keylist__'):
            return obj
        if isinstance(obj, list):
            p = [self.makeDictType(i) for i in obj if i is not None]
            return [i for i in p if i is not None and i != {}]
        d = {}
        for o in obj.__keylist__:
            e = getattr(obj, o)
            if e is not None:
                p = self.makeDictType(e)
                if p is not None and p != {}:
                    d[str(o)] = self.makeDictType(e)
        return d
            
    def backUpCache(self):
        """ We back up the cache for situations where the cache is expired and
            the web service can not be reached. This allows working offline.
        """ 
        cached = os.path.join(package_cache.location,
                              "suds-%s-wsdl.px" % abs(hash(self.address)))
        backup = os.path.join(package_cache.location,
                              "suds-%s-wsdl.px" % hashlib.md5(self.address
                                                              ).hexdigest())
        if os.path.exists(cached):
            shutil.copyfile(cached, backup)

    def restoreFromBackup(self):
        """ Restore from backup into cache with reset cache time""" 
        cached = os.path.join(package_cache.location,
                              "suds-%s-wsdl.px" % abs(hash(self.address)))
        backup = os.path.join(package_cache.location,
                              "suds-%s-wsdl.px" % hashlib.md5(self.address
                                                              ).hexdigest())
        if not os.path.exists(cached) and os.path.exists(backup):
            shutil.copyfile(backup, cached)
            return True
        return False

    def createPackage(self):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        if self.signature in reg.packages:
            reg.remove_package(reg.packages[self.signature])

        # create a document hash integer from the cached sax tree
        # "name" is what suds use as the cache key
        name = '%s-%s' % (abs(hash(self.address)), "wsdl")
        wsdl = package_cache.get(name)
        if not wsdl:
            debug.critical("File not found in SUDS cache: '%s'" % name)
            self.wsdlHash = '0'
            return
        self.wsdlHash = str(int(hashlib.md5(str(wsdl.root)).hexdigest(), 16))

        package_id = reg.idScope.getNewId(Package.vtType)
        package = Package(id=package_id,
                          load_configuration=False,
                          name="SUDS#" + self.address,
                          identifier=self.signature,
                          version=self.wsdlHash,
                          )
        suds_package = reg.get_package_by_name(identifier)
        package._module = suds_package.module
        package._init_module = suds_package.init_module
        
        self.package = package
        reg.add_package(package)
        reg.signals.emit_new_package(self.signature)

        self.module = new_module(Module, str(self.signature))
        reg.add_module(self.module, **{'package':self.signature,
                                       'package_version':self.wsdlHash,
                                       'abstract':True})

    def createFailedPackage(self):
        """ Failed package is created so that the user can remove
        it manually using package submenu """
        pm = get_package_manager()
        if pm.has_package(self.signature):
            # do nothing
            return
        reg = vistrails.core.modules.module_registry.get_module_registry()

        # create a document hash integer from the cached sax tree
        # "name" is what suds use as the cache key
        name = '%s-%s' % (abs(hash(self.address)), "wsdl")
        self.wsdlHash = '0'

        package_id = reg.idScope.getNewId(Package.vtType)
        package = Package(id=package_id,
                          load_configuration=False,
                          name="SUDS#" + self.address,
                          identifier=self.signature,
                          version=self.wsdlHash,
                          )
        suds_package = reg.get_package_by_name(identifier)
        package._module = suds_package.module
        package._init_module = suds_package.init_module
        self.package = package
        reg.add_package(package)
        reg.signals.emit_new_package(self.signature)
        self.module = new_module(Module, str(self.signature))
        reg.add_module(self.module, **{'package':self.signature,
                                       'package_version':self.wsdlHash,
                                       'abstract':True})
        self.service = -1

    def setTypes(self):
        """ Return dict containing all exposed types in the service
        """
        self.wstypes = {}
        for sd in self.service.sd:
            for type in sd.types:
                type = type[0]
                # ignore existing types and arrays
                if type.qname[1] in wsdlSchemas or type.qname[0].startswith('Array'):
                    continue
                qname = type.qname
                wstype = WSType(qname, type.enum())
                self.wstypes[qname] = wstype
                # handle enums by adding a "value" port with the possible enums
                if wstype.enum:
                    values = [i[0].name for i in type.children()]
                    wstype.parts["value"] = WSElement("value",
                        ('string', "http://www.w3.org/2001/XMLSchema"),
                        False, 1, 1, values)
                    continue
                # add elements
                for e in type.children():
                    e = e[0]
                    if e.type is None:
                        pass # probably empty type so just ignore
                    elif e.type[0].startswith('Array'):
                        qtype = ('Array', 'http://www.w3.org/2001/XMLSchema')
                        wstype.parts[e.name] = WSElement(e.name, qtype,
                                                   e.optional(), e.min, e.max)
                    else:
                        wstype.parts[e.name] = WSElement(e.name, e.type,
                                                   e.optional(), e.min, e.max)

    def setMethods(self):
        """ Return dict with methods in service
        """
        def isKnownType(qtype):
            return not qtype or str(qtype[1]) in wsdlSchemas or \
            qtype[0].startswith('Array') or qtype in self.wstypes

        def getChildTypes(type):
            schema = self.service.wsdl.schema
            if type in schema.elements:
                if schema.elements[type].type is not None:
                    return [(schema.elements[type].name, schema.elements[type].type)]
                else:
                    return [(c[0].name, c[0].type) for c in schema.elements[type].children()]
            elif type in schema.types:
                return [(c[0].name, c[0].type) for c in schema.types[type].children()]
            debug.critical("Could not resolve type in WSDL:" + str(type))
            return []

        def setMethod(m):
            # create new method
            wsm = WSMethod((m[0], self.address))
            self.wsmethods[wsm.qname] = wsm
            # process inputs
            for param in m[1]:
                name = param[0]
                qtype = (param[1].resolve().name, param[1].resolve().namespace()[1])
                qtype = (str(qtype[0]), str(qtype[1]))
                if qtype is None:
                    qtype = param[1].element
                    qtype = (str(qtype[0]), str(qtype[1]))
                if qtype is not None:
                    if qtype[0].startswith('Array'):
                        qtype = ('Array', 'http://www.w3.org/2001/XMLSchema')
                    wsm.inputs[name] = qtype
            # process outputs - need to look recursively in wsdl
            method = self.service.service.__getattr__(m[0])
            for output in method.method.soap.output.body.parts:
                # get schema definition of method
                if output.type:
                    qtype = output.type
                else:
                    element = self.service.wsdl.schema.elements[output.element]
                    qtype = element.type if element.type else output.element
                # check that it exists
                types = [(output.name, qtype)]
                while qtype is not None and not isKnownType(qtype):
                    types = getChildTypes(qtype)
                    if len(types):
                        qtype = types[0][1]
                    else:
                        break
                for name, qtype in types:
                    if qtype is not None:
                        if qtype[0].startswith('Array'):
                            qtype = ('Array', 'http://www.w3.org/2001/XMLSchema')
                        wsm.outputs[name] = qtype
        # loop through services, ports, and methods
        self.wsmethods = {}
        for sd in self.service.sd:
            for port in sd.ports:
                for m in port[1]:
                    setMethod(m)

    def createTypeClasses(self):
        # first create classes
        reg = vistrails.core.modules.module_registry.get_module_registry()
        self.typeClasses = {}
        for t in self.wstypes.itervalues():
            def compute(self):
                """ 1. use type input as object or create new
                    2. add other inputs to obj
                    3. set obj and parts as outputs
                """
                if self.wstype.enum:
                    # only makes sure the enum is one of the valid values
                    p = self.wstype.parts['value']
                    if self.has_input(p.name):
                        obj = self.get_input(p.name)
                    else:
                        obj = p.enum[0] if len(p.enum) else ''
                    if self.has_input('value'):
                        obj = self.get_input('value')
                    if obj not in p.enum:
                        raise ModuleError(self,
                                 "'%s' is not one of the valid enums: %s" %
                                 (obj, str(p.enum)) )
                    self.set_output(self.wstype.qname[0], obj)
                    self.set_output('value', obj)
                    return
                if self.has_input(self.wstype.qname[0]):
                    obj = self.get_input(self.wstype.qname[0])
                else:
                    obj = {}
                    s = "{%s}%s"%(self.wstype.qname[1],self.wstype.qname[0])
                    try:
                        obj = self.service.service.factory.create(s)
                    except (suds.TypeNotFound, suds.BuildError):
                        raise ModuleError("Type not found: %s" % s)
                for part in self.wstype.parts.itervalues():
                    # 
                    if obj.__class__.__name__ == 'UberClass':
                        # UberClass is a placeholder and its value is assumed
                        # to be the correct attribute value
                        if len(self.wstype.parts) == 1:
                            setattr(obj, part.name, obj.value)
                        else:
                            # update each attribute
                            if hasattr(obj.value, part.name):
                                setattr(obj, part.name, getattr(obj.value, part.name))
                    if self.has_input(part.name):
                        p = self.get_input(part.name)
                        if hasattr(obj, part.name):
                            setattr(obj, part.name, p)
                        else:
                            # do it anyway - assume attribute missing in template
                            setattr(obj, part.name, p)
                    if hasattr(obj, part.name):
                        # 
                        res = getattr(obj, part.name)
                        self.set_output(part.name, res)
                self.set_output(self.wstype.qname[0], obj)

            # create docstring
            parts = ", ".join([i.type[0]+' '+i.name for i in t.parts.itervalues()])
            d = """This module was created using a wrapper for SUDS (fedorahosted.org/suds/)
from the WSDL spec at:
   %s
It is a WSDL type with signature:
   %s(%s)"""%(self.address, t.qname[0], parts)
            M = new_module(self.module, str(t.qname[0]),{"compute":compute,
                                                         "wstype":t,
                                                         "service":self,
                                                         "__doc__":d})
            self.typeClasses[t.qname] = M
            reg.add_module(M, **{'namespace':'Types',
                                 'package':self.signature,
                                 'package_version':self.wsdlHash})

        # then add ports
        for t in self.wstypes:
            wstype = self.wstypes[t]
            # get type module
            if t[1] in wsdlSchemas:
                c = wsdlTypesDict[t[0]]
            elif t in self.typeClasses:
                c = self.typeClasses[t]
            else:
                debug.critical("Cannot find module for type: " + str(t))
                continue
            # add self ports
            reg.add_input_port(self.typeClasses[t], t[0], c)
            reg.add_output_port(self.typeClasses[t], t[0], c)
            for p in wstype.parts:
                part = wstype.parts[p]
                # get type module
                ptype = part.type
                if part.max is not None and (part.max == 'unbounded' or int(part.max)>1):
                    # it can be multiple objects which means we need to make it a list
                    c = vistrails.core.modules.basic_modules.List
                elif ptype[1] in wsdlSchemas:
                    c = wsdlTypesDict[ptype[0]]
                elif ptype in self.typeClasses:
                    c = self.typeClasses[ptype]
                else:
                    debug.critical("Cannot find module for type: " + str(ptype))
                    continue
                # add as both input and output port
                reg.add_input_port(self.typeClasses[t], p, c,
                                   optional=part.optional)
                reg.add_output_port(self.typeClasses[t], p, c,
                                    optional=part.optional)

    def createMethodClasses(self):
        # register modules
        reg = vistrails.core.modules.module_registry.get_module_registry()
        self.methodClasses = {}
        for m in self.wsmethods.itervalues():
            def compute(self):
                # create dict of inputs
                cacheable = False
                if self.has_input('cacheable'):
                    cacheable = self.get_input('cacheable')
                self.is_cacheable = lambda *args, **kwargs: cacheable            
                params = {}
                mname = self.wsmethod.qname[0]
                for name in self.wsmethod.inputs:
                    name = str(name)
                    if self.has_input(name):
                        params[name] = self.get_input(name)
                        if params[name].__class__.__name__ == 'UberClass':
                            params[name] = params[name].value
                        params[name] = self.service.makeDictType(params[name])
                try:
                    #import logging
                    #logging.basicConfig(level=logging.INFO)
                    #logging.getLogger('suds.client').setLevel(logging.DEBUG)
                    #print "params:", str(params)[:400]
                    #self.service.service.set_options(retxml = True)
                    #result = getattr(self.service.service.service, mname)(**params)
                    #print "result:", str(result)[:400]
                    #self.service.service.set_options(retxml = False)
                    result = getattr(self.service.service.service, mname)(**params)
                except Exception, e:
                    debug.unexpected_exception(e)
                    raise ModuleError(self, "Error invoking method %s: %s" % (
                            mname, debug.format_exception(e)))
                for name, qtype in self.wsmethod.outputs.iteritems():
                    if isinstance(result, list):
                        # if result is a list just set the output
                        self.set_output(name, result)
                    elif qtype[0] == 'Array':
                        # if result is a type but type is a list try to extract the correct element
                        if len(result.__keylist__):
                            self.set_output(name, getattr(result, result.__keylist__[0]))
                        else:
                            self.set_output(name, result)
                    elif result.__class__.__name__ == 'Text':
                        # only text returned so we assume each output wants all of it
                        self.set_output(name, str(result.trim()))
                    elif result.__class__.__name__ == qtype[0]:
                        # the return value is this type
                        self.set_output(name, result)
                    elif hasattr(result, name):
                        self.set_output(name, getattr(result, name))
                    else:
                        # nothing matches - assume it is an attribute of the correct class
                        class UberClass(object):
                            def __init__(self, value):
                                self.value = value
                        self.set_output(name, UberClass(result))

            # create docstring
            inputs = ", ".join([t[0]+' '+i for i,t in m.inputs.iteritems()])
            outputs = ", ".join([t[0]+' '+o for o,t in m.outputs.iteritems()])
            d = """This module was created using a wrapper for SUDS (fedorahosted.org/suds/)
from the WSDL spec at:
   %s
It is a WSDL method with signature:
   %s(%s)
Outputs:
   (%s)
"""%(self.address, m.qname[0], inputs, outputs)

            M = new_module(self.module, str(m.qname[0]), {"compute":compute,
                                                          "wsmethod":m,
                                                          "service":self,
                                                           "__doc__":d})
            self.methodClasses[m.qname] = M
            reg.add_module(M, **{'namespace':'Methods',
                                 'package':self.signature,
                                 'package_version':self.wsdlHash})
            reg.add_input_port(self.methodClasses[m.qname], 'cacheable',
                               wsdlTypesDict['boolean'], optional=True)

            # add ports
            for p, ptype in m.inputs.iteritems():
                if ptype[1] in wsdlSchemas:
                    c = wsdlTypesDict[ptype[0]]
                elif ptype in self.typeClasses:
                    c = self.typeClasses[ptype]
                else:
                    # use string as default
                    c = wsdlTypesDict['string']
                reg.add_input_port(M, p, c)
            for p, ptype in m.outputs.iteritems():
                if ptype[1] in wsdlSchemas:
                    c = wsdlTypesDict[ptype[0]]
                elif ptype in self.typeClasses:
                    c = self.typeClasses[ptype]
                else:
                    # use string as default
                    c = wsdlTypesDict['string']
                reg.add_output_port(M, p, c)

def load_from_signature(signature):
    """ Load wsdl from signature and return success status """
    wsdl = toAddress(signature)
    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    if not wsdl in wsdlList:
        try:
            service = Service(wsdl)
        except Exception, e:
            debug.unexpected_exception(e)
            return False
        if not service.service:
            return False
        webServicesDict[wsdl] = service
        wsdlList.append(wsdl)
        configuration.wsdlList = ';'.join(wsdlList)
    return True

def handle_module_upgrade_request(controller, module_id, pipeline):
    old_module = pipeline.modules[module_id]
    # first check package
    # v1.0 types:
    if old_module.package == 'edu.utah.sci.vistrails.sudswebservices':
        wsdl = old_module.namespace.split('|')[0]
        namespace = old_module.namespace.split('|')[1]
    else:
        wsdl = toAddress(old_module.package)
        namespace = old_module.namespace
    name = old_module.name

    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    if not wsdl in wsdlList:
        service = Service(wsdl)
        if not service.service:
            return []
        webServicesDict[wsdl] = service
        wsdlList.append(wsdl)
        configuration.wsdlList = ';'.join(wsdlList)

    if old_module.package == 'edu.utah.sci.vistrails.sudswebservices':
        reg = vistrails.core.modules.module_registry.get_module_registry()
        new_descriptor = reg.get_descriptor_by_name(toSignature(wsdl), name,
                                                    namespace)
        if not new_descriptor:
            return []
        try:
            return UpgradeWorkflowHandler.replace_module(controller, pipeline,
                                                    module_id, new_descriptor)
        except Exception, e:
            import traceback
            traceback.print_exc()
            raise

    return UpgradeWorkflowHandler.attempt_automatic_upgrade(controller, 
                                                            pipeline,
                                                            module_id)

def handle_missing_module(controller, module_id, pipeline):
    global webServicesDict
    global package_cache

    def get_wsdl_from_namespace(m_namespace):
        try:
            wsdl = m_namespace.split("|")
            return wsdl[0]
        except Exception, e:
            debug.unexpected_exception(e)
            return None
    
    m = pipeline.modules[module_id]
    if m.package == identifier:
        # v1.0 old style
        m_namespace = m.namespace
        wsdl = get_wsdl_from_namespace(m_namespace)
    else:
        # v1.1 new style
        wsdl = toAddress(m.package)
    
    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    if wsdl in wsdlList:
        # it is already loaded
        return True

    service = Service(wsdl)
    if not service.service:
        return False

    webServicesDict[wsdl] = service
    wsdlList.append(wsdl)
    configuration.wsdlList = ';'.join(wsdlList)
    return True

def load_from_identifier(service_identifier):
    """ Loads a web service from its package identifier """
    global webServicesDict
    global package_cache

    wsdl = toAddress(service_identifier)
    
    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    if wsdl in wsdlList:
        # it is already loaded
        return True

    service = Service(wsdl)
    if not service.service:
        return False

    webServicesDict[wsdl] = service
    wsdlList.append(wsdl)
    configuration.wsdlList = ';'.join(wsdlList)
    return True

def contextMenuName(signature):
    """ Returns a context menu name that depends on the signature
        should return None if no method is available
    """
    if signature == name:
        return "Add Web Service"
    elif signature.startswith('SUDS#'):
        return "Remove this Web Service"
    return None

def saveVistrailFileHook(vistrail, temp_dir):
    """ This is called when a vistrail is saved
        We should copy all cached Web Services in vistrail to temp_dir
        if they do not exist

    """
    # Skip if this is a DBVistrail
    if not hasattr(vistrail, 'get_used_packages'):
        return
    packages = vistrail.get_used_packages()
    # clear old files
    for name in os.listdir(temp_dir):
        if name.endswith("-wsdl.px"):
            os.remove(os.path.join(temp_dir, name))

    for package in packages:
        if package.startswith("SUDS#"):
            address = toAddress(package)
            name = "suds-%s-wsdl.px" % hashlib.md5(address).hexdigest()
            cached = os.path.join(package_cache.location, name)
            vt_cached = os.path.join(temp_dir, name)
            if os.path.exists(cached):
                shutil.copyfile(cached, vt_cached)

def loadVistrailFileHook(vistrail, temp_dir):
    """ This is called when a vistrail is loaded
        We should copy all used Web Services in temp_dir to .vistrails

        """
    for name in os.listdir(temp_dir):
        src = os.path.join(temp_dir, name)
        dest = os.path.join(package_cache.location, name)
        if name.endswith("-wsdl.px") and not os.path.exists(dest):
            shutil.copyfile(src, dest)
    
def callContextMenu(signature):
    global webServicesDict
    if signature == name:
        from PyQt4 import QtGui 
        wsdl, ret = QtGui.QInputDialog.getText(None, 'Add Web Service',
                                           'Enter the location of the WSDL:')
        wsdl = str(wsdl)
        if not wsdl:
            return
        if not wsdl.startswith('http://'):
            wsdl = 'http://' + wsdl
        if wsdl in webServicesDict:
            debug.critical('WSDL already loaded: '+wsdl)
            return
        s = Service(wsdl)
        if s.service:
            webServicesDict[wsdl] = s
            if configuration.wsdlList:
                configuration.wsdlList += ';' + wsdl
            else:
                configuration.wsdlList = wsdl
    elif signature.startswith('SUDS#'):
        address = toAddress(signature)
        from PyQt4 import QtGui 
        res = QtGui.QMessageBox.question(None,
                           'Remove the following web service from vistrails?',
                           address,
                           buttons=QtGui.QMessageBox.Yes,
                           defaultButton=QtGui.QMessageBox.No)
        if res == QtGui.QMessageBox.Yes:
            # Remove this Web Service
            s = webServicesDict[address]
            del webServicesDict[address]

            reg = vistrails.core.modules.module_registry.get_module_registry()
            reg.remove_package(s.package)
            wsdlList = configuration.wsdlList.split(";")
            wsdlList.remove(address)
            configuration.wsdlList = ';'.join(wsdlList)
