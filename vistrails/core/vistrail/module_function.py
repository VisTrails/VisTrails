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

    ##########################################################################
    # Constructors and copy
    
    def __init__(self, name="", params=None):
        self.name = name
        self.returnType = "void"
        if params is not None:
            self.params = [ModuleParam(*param) for param in params]
        else:
            self.params = []
    
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

    def __copy__(self):
        """ __copy__() -> ModuleFunction - Returns a clone of itself """
        cp = ModuleFunction()
        cp.name = self.name
        cp.returnType = self.returnType
        cp.params = [copy.copy(p) for p in self.params]
        return cp
        
    ##########################################################################

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

    def stringAsUserSetter(self):
        """ stringAsUserSetter() -> str. 
        Returns a string representation without return type 
        
        """
        s = "<<name='%s' params=" % self.name
        for p in self.params:
            s += ' ' + str(p)
        s += " >>"
        return s

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(self) != type(other):
            print "type mismatch"
            return
        if self.name != other.name:
            print "name mismatch"
            return
        if self.returnType != other.returnType:
            print "return type mismatch"
            return
        if len(self.params) != len(other.params):
            print "params length mismatch"
            return
        for p,q in zip(self.params, other.params):
            if p != q:
                print "params mismatch"
                p.show_comparison(q)
                return
        print "no difference found"
        assert self == other
        return

    ##########################################################################
    # Operators
    
    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        return ("(ModuleFunction '%s' params=%s)@%X" %
                (self.name,
                 [str(p) for p in self.params],
                 id(self)))

    def __eq__(self, other):
        """ __eq__(other: ModuleFunction) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
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
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        f.params.append(param)
        g = ModuleFunction()
        g.name = "value"
        param = ModuleParam()
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        g.params.append(param)
        assert f == g
        param = ModuleParam()
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        g.params.append(param)
        assert f != g

    def test_str(self):
        f = ModuleFunction('value',
                           [('Float', '1.2')])
        str(f)

if __name__ == '__main__':
    unittest.main()
    
