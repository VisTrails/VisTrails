""" This module contains class definitions for:

    * VistrailModuleType
    * PipelineElementType
    * VisPort
    * ModuleParam
    * ModuleFunction
"""

from enum import enum
import copy
import __builtin__
import core.modules.module_registry
import core.modules.vistrails_module
from common import VistrailsInternalError, all, eprint

if __name__ == '__main__':
    import qt
    global app
    app = qt.createBogusQtApp()

VistrailModuleType = enum('VistrailModuleType',
                          ['Invalid', 'Abstract', 'Filter', 'Object', 'Plugin', 'Module'])
PipelineElementType = enum('PipelineElementType',
                           ['Module', 'Connection', 'Function', 'Parameter'])
VisPortEndPoint = enum('VisportEndPoint',
                       ['Invalid', 'Source', 'Destination'])

class VisPort(object):
    """ A port denotes one endpoint of a VisConnection.

    self.spec: list of list of (module, str)"""

    def makeSpec(self, specStr, localRegistry=None, loose=True):
        """Parses a string representation of a port spec and returns the spec. Uses
own type to decide between source and destination ports."""
        if specStr[0] != '(' or specStr[-1] != ')':
            raise VistrailsInternalError("invalid port spec")
        specStr = specStr[1:-1]
        descriptor = core.modules.module_registry.registry.getDescriptorByName(self.moduleName)
        if localRegistry:
            localDescriptor = localRegistry.getDescriptorByName(self.moduleName)
        else:
            localDescriptor = None
        if self.endPoint == VisPortEndPoint.Source:
            ports = copy.copy(descriptor.outputPorts)
            if localDescriptor:
                ports.update(localDescriptor.outputPorts)
        elif self.endPoint == VisPortEndPoint.Destination:
            ports = copy.copy(descriptor.inputPorts)
            if localDescriptor:
                ports.update(localDescriptor.inputPorts)
        else:
            raise VistrailsInternalError("Invalid port endpoint")
        values = specStr.split(", ")
        if not ports.has_key(self.name):            
            if loose:
                return [[(core.modules.module_registry.registry.getDescriptorByName(v).module,
                         '<no description>')
                        for v in values]]
            else:
                raise VistrailsInternalError("Port name is inexistent in ModuleDescriptor")
        specs = ports[self.name]
        for spec in specs:
            if all(zip(spec, values),
                   lambda ((klass, descr), name): issubclass(core.modules.module_registry.registry.getDescriptorByName(name).module, klass)):
                return [copy.copy(spec)]
        print self.moduleName
        print self.name
        print specStr
        print specs
        raise VistrailsInternalError("No port spec matches the given string")

    def getSignatures(self):
        """Returns a list of all accepted signatures of this port, by generating
a string representation of each port spec."""
        def getSig(spec):
            if type(spec) == __builtin__.list:
                return "(" + ", ".join([getSig(s) for s in spec]) + ")"
            assert type(spec == __builtin__.tuple)
            spec = spec[0]
            if issubclass(spec, core.modules.vistrails_module.Module):
                return spec.__name__
            raise VistrailsInternalError("getSig Can't handle type %s" % type(spec))
        return [getSig(spec) for spec in self.spec]

    def toolTip(self):
        """Generates an appropriate tooltip for the port."""
        def endPointType():
            d = {VisPortEndPoint.Invalid: "Invalid",
                 VisPortEndPoint.Source: "Output",
                 VisPortEndPoint.Destination: "Input"}
            return d[self.endPoint]
        return "%s port %s\n%s" % (endPointType(), self.name, "; ".join(self.getSignatures()))
    
    def __init__(self):
        self.endPoint = VisPortEndPoint.Invalid
        self.moduleId = 0
        self.connectionId = 0
        self.moduleName = ""
        self.name = ""
        self.type = VistrailModuleType.Module
        self.spec = None
        self.optional = False
    
    def __str__(self):
        """ Returns a string representation of a VisPort object \

        Returns
        -------
        - 'str'
        
        """
        return '<VisPort endPoint="%s" moduleId=%s connectionId=%s name=%s type=Module %s/>' % \
               (self.endPoint,
                self.moduleId,
                self.connectionId,
                self.name,
                self.spec)

class ModuleParam(object):
    __fields__ = ['type', 'strValue', 'name', 'minValue', 'maxValue', 'alias']
    """ Stores a parameter setting for a vistrail function """
    def __init__(self):
        self.type = ""
        self.strValue = ""
        self.name = ""
        self.alias = ""
        self.minValue = ""
        self.maxValue = ""
        self.evaluatedStrValue = ""
        
    def serialize(self, dom, element):
        """ Writes itself in XML """
        child = dom.createElement('param')
        child.setAttribute('name',self.name)
        ctype = dom.createElement('type')
        cval = dom.createElement('val')
        calias = dom.createElement('alias')
        ttype = dom.createTextNode(self.type)
        tval = dom.createTextNode(self.strValue)        
        talias = dom.createTextNode(self.alias)
        child.appendchild(ctype)
        child.appendChild(cval)
        ctype.appendChild(ttype)
        cval.appendChild(tval)
        calias.appendChild(talias)
        element.appendChild(child)

    def value(self):
        """  """
        if self.strValue == "":
            self.strValue = ModuleParam.defaultValue[self.type][0]
            return ModuleParam.defaultValue[self.type][1]
        return ModuleParam.dispatchValue[self.type](self.strValue)

    dispatchValue = {'Float': float,
                     'Integer': int,
                     'String': str,
                     'Boolean': bool}

    defaultValue = {'Float': ("0", 0.0),
                    'Integer': ("0", 0),
                    'String': ("", ""),
                    'Boolean': ("False", "False")}

#     dispatchValue = {'float': float,
#                      'double': float,
#                      'int': int,
#                      'vtkIdType': int,
#                      'string': str,
#                      'str': str,
#                      'const char *': str,
#                      'const char*': str,
#                      'char *': str,
#                      'char*': str}

    def quoteValue(self):
        """ """
        return ModuleParam.dispatchQuoteValue[self.type](self.strValue)
    
    dispatchQuoteValue = {'float': str,
                          'double': str,
                          'int': str,
                          'vtkIdType': str,
                          'str': lambda x: "'" + str(x) + "'",
                          'string': lambda x: "'" + str(x) + "'",
                          'const char *': lambda x: "'" + str(x) + "'",
                          'const char*': lambda x: "'" + str(x) + "'",
                          'char *': lambda x: "'" + str(x) + "'",
                          'char*': lambda x: "'" + str(x) + "'"}

    def __str__(self):
        if self.minValue != "":
            f = (self.name, self.type, self.strValue, self.minValue, self.maxValue, self.alias)
            return "<<name='%s' type='%s' strValue='%s' minValue='%s' maxValue='%s' alias='%s'>>" % f
        else:
            return "<<name='%s' type='%s' strValue='%s' alias='%s'>>" % (self.name,
                                                                         self.type,
                                                                         self.strValue,
                                                                         self.alias)
    

class ModuleFunction(object):
    __fields__ = ['name', 'returnType', 'params']
    """ Stores a function from a vistrail module """
    
    @staticmethod
    def fromSpec(port, spec):
        
        def fromSourcePort():
            f = ModuleFunction()
            f.name = port.name
            f.returnType = spec[0].__name__
            return f
        
        def fromDestinationPort():
            f = ModuleFunction()
            f.name = port.name
            f.returnType = 'void'
            for specitem in spec:
                p = ModuleParam()
                p.type = specitem[0].__name__
                p.name = specitem[1]
                f.params.append(p)
            return f
        
        if port.endPoint == VisPortEndPoint.Source:
            return fromSourcePort()
        elif port.endPoint == VisPortEndPoint.Destination:
            return fromDestinationPort()
        else:
            raise VistrailsInternalError("Wasn't expecting an invalid endpoint")
        
#     @staticmethod
#     def fromSetterSignature(name,sig):
#         """fromSetterSignature(name,sig) -> ModuleFunction
# Creates a ModuleFunction from a vtk_rtti signature."""
#         params = sig[1]
#         f = ModuleFunction()
#         f.name = name
#         f.returnType = 'void'
#         if params == None:
#             return f
#         for param in params:
#             p = ModuleParam()
#             p.name = '(unnamed)'
#             if type(param) == type(()):
#                 p.type = param[0]
#                 p.minValue = param[1]
#                 p.maxValue = param[2]
#             else:
#                 p.type = param
#             f.params.append(p)
#         return f

#     @staticmethod
#     def fromStateSignature(name, state):
#         f = ModuleFunction()
#         f.name = 'Set' + name + 'To' + state
#         f.returnType = 'void'
#         return f

#     @staticmethod
#     def fromToggleSignatures(name):
#         f1 = ModuleFunction()
#         f1.name = 'Set' + name
#         f1.returnType = 'void'
#         p = ModuleParam()
#         p.type = 'int'
#         p.name = '(unnamed)'
#         f1.params.append(p)
#         f2 = ModuleFunction()
#         f2.name = name + 'On'
#         f2.returnType = 'void'
#         f3 = ModuleFunction()
#         f3.name = name + 'Off'
#         f3.returnType = 'void'
#         return [f1,f2,f3]

    def __init__(self):
        self.name = ""
	self.returnType = ""
	self.params = []

    def getNumParams(self):
        """ Returns the number of params
        Returns
        -------

        - 'int'
         the number of params
         
        """
        return len(self.params)
    
    def serialize(self, doc, element):
	""" Writes itself in XML """
	child = doc.createElement('function')
	child.setAttribute('name',self.name)
	child.setAttribute('returnType',self.type)
	for p in self.params:
		p.serialize(doc,child)
	element.appendChild(child)

    def getSignature(self):
        """ Returns its signature

        Returns
        -------

        - 'str'
        
        """
        result = self.returnType + "("
        for p in self.params:
            result = result + p.type + ", "
        if result.rfind(",") != -1:
            result = result[0:result.rfind(",")]
        else:
            result = result + " "
        result = result + ")"
        return result
    
    def __str__(self):
        return "<<name='%s' returnType='%s' params=%s>>" % (self.name,
                                                            self.returnType,
                                                            self.params)

    def stringAsUserSetter(self):
        s = "<<name='%s' params=" % self.name
        for p in self.params:
            s += ' ' + str(p)
        s += " >>"
        return s

    def __copy__(self):
        cp = ModuleFunction()
        cp.name = self.name
        cp.returnType = self.returnType
        cp.params = [copy.copy(p) for p in self.params]
        return cp

################################################################################

import unittest

if __name__ == '__main__':
    import core.modules.basic_modules
    import core.modules.module_registry

class TestVisTypes(unittest.TestCase):
    
    def testPort(self):
        x = VisPort()
        a = str(x)
        x.type = VistrailModuleType.Filter
        a = str(x)
        x.type = VistrailModuleType.Object
        a = str(x)
        
    def testPortSpec(self):
        descriptor = core.modules.module_registry.registry.getDescriptorByName('String')
        ports = core.modules.module_registry.registry.sourcePortsFromDescriptor(descriptor)
        assert all(ports, lambda x: x.moduleName == 'String')
        portRepr = 'value(String)'
        p = registry.portFromRepresentation('String', portRepr, VisPortEndPoint.Source)
        assert p.name == 'value'
        assert p.moduleName == 'String'

    def testPortSpec2(self):
        descriptor = core.modules.module_registry.registry.getDescriptorByName('String')
        ports = core.modules.module_registry.registry.sourcePortsFromDescriptor(descriptor)
        assert all(ports, lambda x: x.moduleName == 'String')
        portRepr = 'value(Float)'
        try:
            p = registry.portFromRepresentation('String', portRepr, VisPortEndPoint.Source)
            self.fail("Expected to fail - passed an incompatible spec representation")
        except VistrailsInternalError:
            pass
        
        
if __name__ == '__main__':
    unittest.main()
