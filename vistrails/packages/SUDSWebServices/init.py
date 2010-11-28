############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

import suds

import sys
import os.path
import core.system
import core.modules.module_registry
import core.modules.basic_modules
from core.modules import vistrails_module
from core.modules.vistrails_module import Module, ModuleError, new_module
from core import debug
from core import configuration

package_cache = None

webServicesDict = {}
###############################################################################

class SUDSWebService(Module):
    """ SUDSWebService is the base Module.
     We will create a SUDSWebService Module for each method published by 
     the web service.

    """
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        raise vistrails_module.IncompleteImplementation

wsdlSchemas = ['http://www.w3.org/2001/XMLSchema',
              'http://xml.apache.org/xml-soap',
              'http://schemas.xmlsoap.org/soap/encoding/']
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
                'base64': core.modules.basic_modules.String,
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
                'Array': core.modules.basic_modules.List,

                # soapenc types
                'arrayCoordinate': core.modules.basic_modules.String,
                'Struct': core.modules.basic_modules.String,
                'NOTATION': core.modules.basic_modules.String                
                }

def initialize(*args, **keywords):
#    import core.packagemanager
    global webServicesDict
    global package_cache

    #Create a directory for the SUDSWebServices package
    location = os.path.join(core.system.default_dot_vistrails(),
                                     "SUDSWebServices")
    if not os.path.isdir(location):
        try:
            debug.log("Creating SUDS cache directory...")
            os.mkdir(location)
        except:
            debug.critical(
"""Could not create SUDS cache directory. Make sure
'%s' does not exist and parent directory is writable""" % location)
            sys.exit(1)
    days = 10
    if configuration.check("cache_days"):
        days = configuration.cache_days
    package_cache = suds.client.ObjectCache(location, days=days)    

    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(SUDSWebService, **{'abstract':True})

    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    for wsdl in wsdlList:
        if not wsdl.startswith('http://'):
            wsdl = 'http://' + wsdl
        if wsdl in webServicesDict:
            debug.warning('Duplicate WSDL entry: '+wsdl)
            continue
        s = Service(wsdl)
        webServicesDict[wsdl] = s
        
class WSMethod:
    """ A WSDL method
    """
    def __init__(self, qname=('','')):
        self.qname = qname
        "name: (typename, ns)"
        self.inputs = {}
        self.outputs = {}

class WSElement:
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

class WSType:
    """ A WSDL type definition
    """
    def __init__(self, qname=('',''), enum=False):
        self.qname = qname
        self.enum = enum
        "name: WSElement"
        self.parts = {}
 
class Service:
    def __init__(self, address):
        """ Process WSDL and add all Types and Methods
        """
        self.address = address
        debug.log("Installing Web Service from WSDL: %s"% address)
 #       try:
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
            self.setTypes()
            self.setMethods()
            self.createTypeClasses()
            self.createMethodClasses()
        except Exception, e:
            debug.critical("Could not load WSDL: %s - %s" % (address,str(e)))
            self.service = None
        
    def makeDictType(self, obj):
        """ Create recursive dict from SUDS object
            ignore attributes with None and empty dicts and handle lists """
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
                    d[o] = self.makeDictType(e)
        return d
            
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
        reg = core.modules.module_registry.get_module_registry()
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
                    if self.hasInputFromPort(p.name):
                        obj = self.getInputFromPort(p.name)
                    else:
                        obj = p.enum[0] if len(p.enum) else ''
                    if self.hasInputFromPort('value'):
                        obj = self.getInputFromPort('value')
                    if obj not in p.enum:
                        raise ModuleError(self,
                                 "'%s' is not one of the valid enums: %s" %
                                 (obj, str(p.enum)) )
                    self.setResult(self.wstype.qname[0], obj)
                    self.setResult('value', obj)
                    return
                if self.hasInputFromPort(self.wstype.qname[0]):
                    obj = self.getInputFromPort(self.wstype.qname[0])
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
                        setattr(obj, part.name, obj.value)
                    if self.hasInputFromPort(part.name):
                        p = self.getInputFromPort(part.name)
                        if hasattr(obj, part.name):
                            setattr(obj, part.name, p)
                    if hasattr(obj, part.name):
                        res = getattr(obj, part.name)
                        self.setResult(part.name, res)
                self.setResult(self.wstype.qname[0], obj)

            # create docstring
            parts = ", ".join([i.type[0]+' '+i.name for i in t.parts.itervalues()])
            d = """This module was created using a wrapper for SUDS (fedorahosted.org/suds/)
from the WSDL spec at:
   %s
It is a WSDL type with signature:
   %s(%s)"""%(self.address, t.qname[0], parts)
            M = new_module(SUDSWebService, str(t.qname[0]),{"compute":compute,
                                                         "wstype":t,
                                                         "service":self,
                                                         "__doc__":d})
            self.typeClasses[t.qname] = M
            reg.add_module(M, **{'namespace':self.address+'|Types',
                                 'package':identifier,
                                 'package_version':version})

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
                    c = core.modules.basic_modules.List
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
        reg = core.modules.module_registry.get_module_registry()
        self.methodClasses = {}
        for m in self.wsmethods.itervalues():
            def compute(self):
                # create dict of inputs
                params = {}
                mname = self.wsmethod.qname[0]
                for name in self.wsmethod.inputs:
                    if self.hasInputFromPort(name):
                        params[name] = self.getInputFromPort(name)
                        if params[name].__class__.__name__ == 'UberClass':
                            params[name] = params[name].value
                        params[name] = self.service.makeDictType(params[name])
                try:
                    self.service.service.set_options(retxml = True)
                    result = getattr(self.service.service.service, mname)(**params)
                    import api
                    api.retxml = result
                    self.service.service.set_options(retxml = False)
                    result = getattr(self.service.service.service, mname)(**params)
                    api.retxml = result
                except Exception, e:
                    raise ModuleError(self, "Error invoking method %s: %s"%(name, str(e)))
                for name, qtype in self.wsmethod.outputs.iteritems():
                    if isinstance(result, list):
                        # if result is a list just set the output
                        self.setResult(name, result)
                    elif qtype[0] == 'Array':
                        # if result is a type but type is a list try to extract the correct element
                        if len(result.__keylist__):
                             self.setResult(name, getattr(result, result.__keylist__[0]))
                        else:
                            self.setResult(name, result)
                    elif result.__class__.__name__ == 'Text':
                        # only text returned so we assume each output wants all of it
                        self.setResult(name, str(result.trim()))
                    elif result.__class__.__name__ == qtype[0]:
                        # the return value is this type
                        self.setResult(name, result)
                    elif hasattr(result, name):
                        self.setResult(name, getattr(result, name))
                    else:
                        # nothing matches - assume it is an attribute of the correct class
                        class UberClass:
                            def __init__(self, value):
                                self.value = value
                        self.setResult(name, UberClass(result))

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

            M = new_module(SUDSWebService, str(m.qname[0]), {"compute":compute,
                                                         "wsmethod":m,
                                                         "service":self,
                                                         "__doc__":d})
            self.methodClasses[m.qname] = M
            reg.add_module(M, **{'namespace':self.address+'|Methods',
                                 'package':identifier,
                                 'package_version':version})
            # add ports
            for p, ptype in m.inputs.iteritems():
                if ptype[1] in wsdlSchemas:
                    c = wsdlTypesDict[ptype[0]]
                elif ptype in self.typeClasses:
                    c = self.typeClasses[ptype]
                else:
                    debug.critical("Cannot find module for type: " + str(ptype))
                    continue
                reg.add_input_port(M, p, c)
            for p, ptype in m.outputs.iteritems():
                if ptype[1] in wsdlSchemas:
                    c = wsdlTypesDict[ptype[0]]
                elif ptype in self.typeClasses:
                    c = self.typeClasses[ptype]
                else:
                    debug.critical("Cannot find module for type: %s %s %s" % (str(t.name), str(p), str(ptype)))
                    continue
                reg.add_output_port(M, p, c)

def handle_missing_module(*args, **kwargs):
    global webServicesDict
    global package_cache
    #this is the order the arguments are passed to the function
    controller = args[0]
    m_id = args[1]
    pipeline = args[2]
    
    def get_wsdl_from_namespace(m_namespace):
        try:
            wsdl = m_namespace.split("|")
            return wsdl[0]
        except:
            return None

    m = pipeline.modules[m_id]
    m_namespace = m.namespace
    
    wsdl = get_wsdl_from_namespace(m_namespace)
    if not wsdl:
        debug.critical("'%s' is not a valid namespace" % m_namespace)
        return False

    wsdlList = []
    if configuration.check('wsdlList'):
        wsdlList = configuration.wsdlList.split(";")
    if wsdl in wsdlList:
        debug.warning("'%s' is already loaded." % wsdl)
        return True
        debug.warning("'%s' is already loaded. Fetching latest version..." % wsdl)
        # temporarily disable cache
        tmp_cache = package_cache
        package_cache = None
        webServicesDict[wsdl] = Service(wsdl)
        package_cache = tmp_cache
        return True

    service = Service(wsdl)
    if not service.service:
        return False

    webServicesDict[wsdl] = service
    wsdlList.append(wsdl)
    configuration.wsdlList = ';'.join(wsdlList)
    return True