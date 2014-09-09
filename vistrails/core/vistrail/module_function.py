###############################################################################
##
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
""" This module contains class definitions for:

    * ModuleFunction
"""
from vistrails.db.domain import DBFunction
from vistrails.core.modules.utils import create_port_spec_string
from vistrails.core.utils import enum, VistrailsInternalError, all, eprint
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.port_spec import PortSpec
from itertools import izip
import copy

import unittest
import copy
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.db.domain import IdScope
import vistrails.core

################################################################################

class ModuleFunction(DBFunction):
    __fields__ = ['name', 'returnType', 'params']
    """ Stores a function from a vistrail module """

    ##########################################################################
    # Constructors and copy
    
    def __init__(self, *args, **kwargs):
        DBFunction.__init__(self, *args, **kwargs)
        if self.name is None:
            self.name = ""
        if self.real_id is None:
            self.real_id = -1
        if self.pos is None:
            self.pos = -1
        self.set_defaults()
        
    def set_defaults(self, other=None):
        if other is None:
            self.returnType = "void"
            self.is_valid = False
        else:
            self.returnType = other.returnType
            self.is_valid = other.is_valid
        self.parameter_idx = self.db_parameters_id_index

    def __copy__(self):
        """ __copy__() -> ModuleFunction - Returns a clone of itself """
        return ModuleFunction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBFunction.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleFunction
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_function):
        if _function.__class__ == ModuleFunction:
            return
        _function.__class__ = ModuleFunction
        for _parameter in _function.db_get_parameters():
            ModuleParam.convert(_parameter)
        _function.set_defaults()

    ##########################################################################
    # Properties

    id = DBFunction.db_pos
    pos = DBFunction.db_pos
    real_id = DBFunction.db_id
    name = DBFunction.db_name   

    def _get_sigstring(self):
        return create_port_spec_string([p.spec_tuple for p in self.params])
    sigstring = property(_get_sigstring)

    def _get_params(self):
        self.db_parameters.sort(key=lambda x: x.db_pos)
        return self.db_parameters
    def _set_params(self, params):
        self.db_parameters = params
    # If you're mutating the params property, watch out for the sort
    # gotcha: every time you use the params on reading position,
    # they get resorted
    params = property(_get_params, _set_params)
    parameters = property(_get_params, _set_params)

    def add_parameter(self, param):
        self.db_add_parameter(param)
    addParameter = add_parameter

    def add_parameters(self, params):
        for p in params:
            self.db_add_parameter(p)

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

    def get_spec(self, port_type):
        """ get_spec(port_type) -> PortSpec

        Returns a PortSpec corresponding to the function parameter
        types set.  This is useful to make module functions look more
        like they are 'regular' modules and connections (which is what
        they get compiled down to in execution).

        port_type is either 'input' or 'output', as strings, which
        simply gets set on the spec being returned.
        """
        assert port_type == 'input' or port_type == 'output'
        result = PortSpec(sigstring=self.sigstring)
        result.type = port_type
        return result

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
        for p,q in izip(self.params, other.params):
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
        return ("<function id='%s' pos='%s' name='%s' params=%s)@%X" %
                (self.real_id,
                 self.pos,
                 self.name,
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


#TODO add more meaningful tests

class TestModuleFunction(unittest.TestCase):

    def create_function(self, id_scope=IdScope()):
        param = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                            pos=2,
                            type='Int',
                            val='1')
        function = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                  pos=0,
                                  name='value',
                                  parameters=[param])
        return function

    def test_copy(self):        
        id_scope = IdScope()
        f1 = self.create_function(id_scope)
        f2 = copy.copy(f1)
        self.assertEquals(f1, f2)
        self.assertEquals(f1.id, f2.id)
        f3 = f1.do_copy(True, id_scope, {})
        self.assertEquals(f1, f3)
        self.assertNotEquals(f1.real_id, f3.real_id)

    def test_serialization(self):
        import vistrails.core.db.io
        f1 = self.create_function()
        xml_str = vistrails.core.db.io.serialize(f1)
        f2 = vistrails.core.db.io.unserialize(xml_str, ModuleFunction)
        self.assertEquals(f1, f2)
        self.assertEquals(f1.real_id, f2.real_id)
                            
    def testComparisonOperators(self):
        f = ModuleFunction()
        f.name = "value"
        param = ModuleParam()
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        f.addParameter(param)
        g = ModuleFunction()
        g.name = "value"
        param = ModuleParam()
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        g.addParameter(param)
        assert f == g
        param = ModuleParam()
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        g.addParameter(param)
        assert f != g

    def test_str(self):
        f = ModuleFunction(name='value',
                           parameters=[ModuleParam(type='Float',
                                                   val='1.2')],
                           )
        str(f)

if __name__ == '__main__':
    unittest.main()
    
