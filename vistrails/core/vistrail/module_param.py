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
    * VistrailModuleType
    * ModuleParam

 """
from core.utils import enum

################################################################################

VistrailModuleType = enum('VistrailModuleType',
                          ['Invalid', 'Abstract', 'Filter', 
                           'Object', 'Plugin', 'Module'])

################################################################################
def bool_conv(x):
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False

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
        """ serialize(dom, element) -> None 
        Writes itself in XML 

        """
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
        """  value() -> any type 
        Returns its strValue as a python type.

        """
        if self.strValue == "":
            self.strValue = ModuleParam.defaultValue[self.type][0]
            return ModuleParam.defaultValue[self.type][1]
        return ModuleParam.dispatchValue[self.type](self.strValue)

    dispatchValue = {'Float': float,
                     'Integer': int,
                     'String': str,
                     'Boolean': bool_conv}

    defaultValue = {'Float': ("0", 0.0),
                    'Integer': ("0", 0),
                    'String': ("", ""),
                    'Boolean': ("False", False)}


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
        """ quoteValue() -> str -  Returns its strValue as an quote string."""
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
        """ __str__() -> str - Returns a string representation of itself """
        if self.minValue != "":
            f = (self.name, self.type, self.strValue, 
                 self.minValue, self.maxValue, self.alias)
            return "<<name='%s' type='%s' strValue='%s' minValue='%s' " \
                " maxValue='%s' alias='%s'>>" % f
        else:
            return "<<name='%s' type='%s' strValue='%s' " \
                "alias='%s'>>" % (self.name,
                                  self.type,
                                  self.strValue,
                                  self.alias)

    def __eq__(self, other):
        """ __eq__(other: ModuleParam) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if self.type != other.type:
            return False
        if self.strValue != other.strValue:
            return False
        if self.name != other.name:
            return False
        if self.alias != other.alias:
            return False
        if self.minValue != other.minValue:
            return False
        if self.maxValue != other.maxValue:
            return False
        if self.evaluatedStrValue != other.evaluatedStrValue:
            return False
        return True

    def __ne__(self, other):
        """ __ne__(other: ModuleParam) -> boolean
        Returns True if self and other don't have the same attributes. 
        Used by !=  operator. 
        
        """
        return not self.__eq__(other)

###############################################################################
# Testing

import unittest

class TestModuleParam(unittest.TestCase):
    
    def testValue(self):
        """ Test values returned by value() function """
        p = ModuleParam()
        p.type = "Float"
        assert p.value() == 0.0
        p.strValue = "1.5"
        assert p.value() == 1.5

        p.type = "Integer"
        p.strValue = ""
        assert p.value() == 0
        p.strValue = "2"
        assert p.value() == 2

        p.type = "String"
        p.strValue = ""
        assert p.value() == ""
        p.strValue = "test"
        assert p.value() == "test"

        p.type = "Boolean"
        p.strValue = ""
        assert p.value() == False
        p.strValue = "False"
        assert p.value() == False
        p.strValue = "True"
        assert p.value() == True

    def testComparisonOperators(self):
        """ Test comparison operators """
        p = ModuleParam()
        q = ModuleParam()
        assert p == q
        q.type = "Float"
        assert p != q

if __name__ == '__main__':
    unittest.main()
    

        
