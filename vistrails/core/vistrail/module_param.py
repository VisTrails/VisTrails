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
    * ModuleParam

 """
from db.domain import DBParameter
from core.utils import enum

################################################################################
def bool_conv(x):
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False

class ModuleParam(DBParameter):
    """ Stores a parameter setting for a vistrail function """

    ##########################################################################
    # Constructor

    def __init__(self, type_="", strValue="", alias="", name="", pos=-1, id=-1):
	DBParameter.__init__(self,
                             id=id,
                             pos=pos,
                             name=name,
                             alias=alias,
                             val=strValue,
                             type=type_)
        self.minValue = ""
        self.maxValue = ""
        self.evaluatedStrValue = ""

        # This is used for visual query and will not get serialized
        self.queryMethod = 0

    def __copy__(self):
        cp = DBParameter.__copy__(self)
        cp.__class__ = ModuleParam
        cp.minValue = self.minValue
        cp.maxValue = self.maxValue
        cp.evaluatedStrValue = self.evaluatedStrValue
        cp.queryMethod = 0
        return cp

    @staticmethod
    def convert(_parameter):
	_parameter.__class__ = ModuleParam
        _parameter.queryMethod = 0
        _parameter.minValue = ""
        _parameter.maxValue = ""
        _parameter.evaluatedStrValue = ""

    ##########################################################################

    # id isn't really the id, it's a relative position
    def _get_id(self):
        return self.db_pos
    def _set_id(self, id):
        self.db_pos = id
    id = property(_get_id, _set_id)

    def _get_real_id(self):
        return self.db_id
    def _set_real_id(self, id):
        self.db_id = id
    real_id = property(_get_real_id, _set_real_id)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_type(self):
        return self.db_type
    def _set_type(self, type):
        self.db_type = type
    type = property(_get_type, _set_type)

    def _get_strValue(self):
        return self.db_val
    def _set_strValue(self, value):
        self.db_val = value
    strValue = property(_get_strValue, _set_strValue)
    
    def _get_alias(self):
        return self.db_alias
    def _set_alias(self, alias):
        self.db_alias = alias
    alias = property(_get_alias, _set_alias)
        
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

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(self) != type(other):
            print "type mismatch"
            return
        if self.type != other.type:
            print "paramtype mismatch"
            return
        if self.strValue != other.strValue:
            print "strvalue mismatch"
            return
        if self.name != other.name:
            print "name mismatch"
            return
        if self.alias != other.alias:
            print "alias mismatch"
            return
        if self.minValue != other.minValue:
            print "minvalue mismatch"
            return
        if self.maxValue != other.maxValue:
            print "maxvalue mismatch"
            return
        if self.evaluatedStrValue != other.evaluatedStrValue:
            print "evaluatedStrValue mismatch"
            return
        print "no difference found"
        assert self == other
        return
        

    ##########################################################################
    # Operators

    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        if self.minValue != "":
            assert False
        else:
            return ("(Param '%s' type='%s' strValue='%s' alias='%s')@%X" %
                    (self.name,
                     self.type,
                     self.strValue,
                     self.alias,
                     id(self)))

    def __eq__(self, other):
        """ __eq__(other: ModuleParam) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
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

    def test_load_and_dump_param(self):
        """ Check that fromXML and toXML are working properly """
        from core.vistrail import dbservice
        
        p = ModuleParam()
        p.type = "Float"
        assert p.value() == 0.0
        p.strValue = "1.5"
        assert p.value() == 1.5
        
        dom = dbservice.toXML(p)
        pnew = dbservice.fromXML('parameter', dom)
        ModuleParam.convert(pnew)

        assert p == pnew


    def test_str(self):
        p = ModuleParam('Float', '1.5')
        str(p)

if __name__ == '__main__':
    unittest.main()
    

        
