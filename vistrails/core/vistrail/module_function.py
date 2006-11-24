""" This module contains class definitions for:

    * ModuleFunction
"""

from core.utils import enum, VistrailsInternalError, all, eprint
from core.vistrail.port import PortEndPoint
from core.vistrail.module_param import ModuleParam
import copy
import __builtin__


################################################################################

if __name__ == '__main__':
    import qt
    global app
    app = qt.createBogusQtApp()

PipelineElementType = enum('PipelineElementType',
                           ['Module', 'Connection', 'Function', 'Parameter'])

################################################################################

class ModuleFunction(object):
    __fields__ = ['name', 'returnType', 'params']
    """ Stores a function from a vistrail module """
    
    @staticmethod
    def fromSpec(port, spec):
        """ fromSpec(port, spec) -> ModuleFunction 
        static method that creates a ModuleFunction object given a port and a
        spec.
        
        """
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
        
        if port.endPoint == PortEndPoint.Source:
            return fromSourcePort()
        elif port.endPoint == PortEndPoint.Destination:
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
        """ getNumParams() -> int Returns the number of params. """
        return len(self.params)
    
    def serialize(self, doc, element):
	"""serialize(doc, element) -> None - Writes itself in XML """
	child = doc.createElement('function')
	child.setAttribute('name',self.name)
	child.setAttribute('returnType',self.type)
	for p in self.params:
		p.serialize(doc,child)
	element.appendChild(child)

    def getSignature(self):
        """ getSignature() -> str - Returns the function signature """
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
        """ __str__() -> str - Returns a string representation of itself """
        return "<<name='%s' returnType='%s' params=%s>>" % (self.name,
                                                            self.returnType,
                                                            self.params)

    def stringAsUserSetter(self):
        """ stringAsUserSetter() -> str. 
        Returns a string representation without return type 
        
        """
        s = "<<name='%s' params=" % self.name
        for p in self.params:
            s += ' ' + str(p)
        s += " >>"
        return s

    def __copy__(self):
        """ __copy__() -> ModuleFunction - Returns a clone of itself """
        cp = ModuleFunction()
        cp.name = self.name
        cp.returnType = self.returnType
        cp.params = [copy.copy(p) for p in self.params]
        return cp

    def __eq__(self, other):
        """ __eq__(other: ModuleFunction) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if self.name != other.name:
            return False
        if self.returnType != other.returnType:
            return False
        if len(self.params) != len(other.params):
            return False
        for p,q in zip(self.params, other.params):
            if p != q:
                return False
        return True
            
    def __ne__(self, other):
        """ __ne__(other: ModuleFunction) -> boolean
        Returns True if self and other don't have the same attributes. 
        Used by !=  operator. 
        
        """
        return not self.__eq__(other)

################################################################################
# Testing

import unittest
from core.vistrail.module_param import ModuleParam

#TODO add more meaningful tests

class TestModuleFunction(unittest.TestCase):

    def testComparisonOperators(self):
        f = ModuleFunction()
        f.name = "value"
        param = ModuleParam()
        param.name = "&lt;no description&gt;"
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        f.params.append(param)
        g = ModuleFunction()
        g.name = "value"
        param = ModuleParam()
        param.name = "&lt;no description&gt;"
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        g.params.append(param)
        assert f == g
        param = ModuleParam()
        param.name = "&lt;no description&gt;"
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        g.params.append(param)
        assert f != g
        

if __name__ == '__main__':
    unittest.main()
    
