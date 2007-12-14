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
# def bool_conv(x):
#     s = str(x).upper()
#     if s == 'TRUE':
#         return True
#     if s == 'FALSE':
#         return False

class ModuleParam(DBParameter):
    """ Stores a parameter setting for a vistrail function """

    ##########################################################################
    # Constructor

    def __init__(self, *args, **kwargs):
	DBParameter.__init__(self, *args, **kwargs)
        if self.real_id is None:
            self.real_id = -1
        if self.db_type is None:
            self.db_type = ""
        if self.strValue is None:
            self.strValue = ""
        if self.alias is None:
            self.alias = ""
        if self.pos is None:
            self.pos = -1
        if self.name is None:
            self.name = ""
    
        self.minValue = ""
        self.maxValue = ""
        self.evaluatedStrValue = ""
        self.identifier = ""
        self._type = ""
        self.namespace = ""
        # This is used for visual query and will not get serialized
        self.queryMethod = 0

    def __copy__(self):
        return ModuleParam.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBParameter.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleParam
        cp.minValue = self.minValue
        cp.maxValue = self.maxValue
        cp.evaluatedStrValue = self.evaluatedStrValue
        cp.queryMethod = 0
        cp.identifier = self.identifier
        cp.namespace = self.namespace
        cp._type = self._type
        return cp

    @staticmethod
    def convert(_parameter):
        if _parameter.__class__ == ModuleParam:
            return
	_parameter.__class__ = ModuleParam
        _parameter.queryMethod = 0
        _parameter.minValue = ""
        _parameter.maxValue = ""
        _parameter.evaluatedStrValue = ""
        _parameter.identifier = ""
        _parameter.namespace = ""
        _parameter._type = ""
        _parameter.parse_type_str(_parameter.db_type)
    ##########################################################################

    # id isn't really the id, it's a relative position
    def _get_id(self):
        return self.db_pos
    def _set_id(self, id):
        self.db_pos = id
    id = property(_get_id, _set_id)
    pos = property(_get_id, _set_id)

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
        if not self._type:
            self.parse_type_str(self.db_type)
        return self._type
    def _set_type(self, type):
        self._type = type
        if self._type is not None:
            self.db_type = self.create_type_str()
    type = property(_get_type, _set_type)

    def _get_typeStr(self):
        if self.db_type is None:
            self.db_type = self.create_type_str()
        return self.db_type
    def _set_typeStr(self, typeStr):
        self.db_type = typeStr
    typeStr = property(_get_typeStr, _set_typeStr)
    
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

    def create_type_str(self):
        result = self.identifier + ":" + self._type
        if self.namespace:
            return result + ':' + self.namespace
        else:
            return result

    def parse_type_str(self, type_str):
        if type_str != "":
            data = type_str.split(":")
            if len(data) == 3:
                self.identifier = data[0]
                self.type = data[1]
                self.namespace = data[2]
            if len(data) == 2:
                self.identifier = data[0]
                self.type = data[1]
                self.namespace = ''
            else:
                assert len(data) == 1
                self.identifier = "edu.utah.sci.vistrails.basic"
                self.type = data[0]
                self.namespace = ''
        
    def serialize(self, dom, element):
        """ serialize(dom, element) -> None 
        Writes itself in XML 

        """
        child = dom.createElement('param')
        child.setAttribute('name',self.name)
        ctype = dom.createElement('type')
        cval = dom.createElement('val')
        calias = dom.createElement('alias')
        ttype = dom.createTextNode(self.typeStr)
        tval = dom.createTextNode(self.strValue)        
        talias = dom.createTextNode(self.alias)
        child.appendchild(ctype)
        child.appendChild(cval)
        ctype.appendChild(ttype)
        cval.appendChild(tval)
        calias.appendChild(talias)
        element.appendChild(child)

    def get_default_value(self):
        """ get_default_value() -> any type
        Query the registry for this constant's default value
        
        """
        from core.modules import module_registry
        reg = module_registry.registry
        module = reg.get_module_by_name(self.identifier, self._type, self.namespace)()
        return module.default_value

    def translate_to_python(self):
        """ translate_to_python() -> function or callable
        Query the registry for this constant's conversion function

        """
        #FIXME this seems not to be used anywhere...
        from core.modules import module_registry
        reg = module_registry.registry
        module = reg.get_module_by_name(self.identifier, self._type, self.namespace)()
        return module.translate_to_python
    
    def value(self):
        """  value() -> any type 
        Returns its strValue as a python type.

        """
        if self.strValue == "":
            v = self.get_default_value()
            self.strValue = str(v)
            return v
        return self.translate_to_python()(self.strValue)

#     dispatchValue = {'Float': float,
#                      'Integer': int,
#                      'String': str,
#                      'Boolean': bool_conv}

#     defaultValue = {'Float': ("0", 0.0),
#                     'Integer': ("0", 0),
#                     'String': ("", ""),
#                     'Boolean': ("False", False)}

#     def quoteValue(self):
#         """ quoteValue() -> str -  Returns its strValue as an quote string."""
#         return ModuleParam.dispatchQuoteValue[self.type](self.strValue)
    
#     dispatchQuoteValue = {'float': str,
#                           'double': str,
#                           'int': str,
#                           'vtkIdType': str,
#                           'str': lambda x: "'" + str(x) + "'",
#                           'string': lambda x: "'" + str(x) + "'",
#                           'const char *': lambda x: "'" + str(x) + "'",
#                           'const char*': lambda x: "'" + str(x) + "'",
#                           'char *': lambda x: "'" + str(x) + "'",
#                           'char*': lambda x: "'" + str(x) + "'"}

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(self) != type(other):
            print "type mismatch"
            return
        if self.typeStr != other.typeStr:
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
            return ("(Param '%s' db_type='%s' strValue='%s' real_id='%s' pos='%s' identifier='%s' alias='%s' namespace='%s')@%X" %
                    (self.name,
                     self.db_type,
                     self.strValue,
                     self.real_id,
                     self.pos,
                     self.identifier,
                     self.alias,
                     self.namespace,
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
import copy
from db.domain import IdScope

class TestModuleParam(unittest.TestCase):

    def create_param(self, id_scope=IdScope()):
        param = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                            pos=2,
                            type='Int',
                            val='1')
        return param

    def test_copy(self):        
        id_scope = IdScope()
        p1 = self.create_param(id_scope)
        p2 = copy.copy(p1)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)
        p3 = p1.do_copy(True, id_scope, {})
        self.assertEquals(p1, p3)
        self.assertNotEquals(p1.real_id, p3.real_id)

    def test_serialization(self):
        import core.db.io
        p1 = self.create_param()
        xml_str = core.db.io.serialize(p1)
        p2 = core.db.io.unserialize(xml_str, ModuleParam)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.real_id, p2.real_id)
    
    def testValue(self):
        """ Test values returned by value() function """
        p = ModuleParam()
        p.type = "Float"
        p.identifier = 'edu.utah.sci.vistrails.basic'
        assert p.value() == 0.0
        p.strValue = "1.5"
        assert p.value() == 1.5

        p.type = "Integer"
        p.identifier = 'edu.utah.sci.vistrails.basic'
        p.strValue = ""
        assert p.value() == 0
        p.strValue = "2"
        assert p.value() == 2

        p.type = "String"
        p.identifier = 'edu.utah.sci.vistrails.basic'
        p.strValue = ""
        assert p.value() == ""
        p.strValue = "test"
        assert p.value() == "test"

        p.type = "Boolean"
        p.identifier = 'edu.utah.sci.vistrails.basic'
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

    def test_str(self):
        p = ModuleParam(type='Float', val='1.5')
        str(p)

if __name__ == '__main__':
    unittest.main()
    

        
