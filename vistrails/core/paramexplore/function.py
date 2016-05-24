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
""" This module contains class definitions for:

    * PEFunction
"""
from __future__ import division

from vistrails.db.domain import DBPEFunction, DBPEParameter
from vistrails.core.paramexplore.param import PEParam
import copy

import unittest
from vistrails.db.domain import IdScope

################################################################################

class PEFunction(DBPEFunction):
    """ Stores a function for a parameter exploration """

    ##########################################################################
    # Constructors and copy
    
    def __init__(self, *args, **kwargs):
        DBPEFunction.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        if self.module_id is None:
            self.module_id = -1
        if self.port_name is None:
            self.port_name = ""
        if self.is_alias is None:
            self.is_alias = 0
        self.set_defaults()
        
    def set_defaults(self, other=None):
        pass

    def __copy__(self):
        """ __copy__() -> ModuleFunction - Returns a clone of itself """
        return PEFunction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPEFunction.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = PEFunction
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_function):
        if _function.__class__ == PEFunction:
            return
        _function.__class__ = PEFunction
        for _parameter in _function.db_get_parameters():
            PEParam.convert(_parameter)
        _function.set_defaults()

    ##########################################################################
    # Properties

    id = DBPEFunction.db_id
    module_id = DBPEFunction.db_module_id
    port_name = DBPEFunction.db_port_name
    is_alias = DBPEFunction.db_is_alias

    def _get_params(self):
        self.db_parameters.sort(key=lambda x: x.db_pos)
        return self.db_parameters
    def _set_params(self, params):
        self.db_parameters = params

    parameters = property(_get_params, _set_params)
    params = property(_get_params, _set_params)

    def add_parameter(self, param):
        self.db_add_parameter(param)
    addParameter = add_parameter

    def add_parameters(self, params):
        for p in params:
            self.db_add_parameter(p)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        return ("<PEFunction id=%s module_id=%s port_name='%s' is_alias=%s params=%s)@%X" %
                (self.id,
                 self.module_id,
                 self.port_name,
                 self.is_alias,
                 [str(p) for p in self.params],
                 id(self)))

    def __eq__(self, other):
        """ __eq__(other: ModuleFunction) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.port_name != other.port_name:
            return False
        if self.module_id != other.module_id:
            return False
        if self.is_alias != other.is_alias:
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

class TestModuleFunction(unittest.TestCase):

    def create_function(self, id_scope=IdScope()):
        param = PEParam(id=id_scope.getNewId(PEParam.vtType),
                            pos=2,
                            interpolator='Stepper',
                            dimension=4,
                            value='[1, 2]')
        function = PEFunction(id=id_scope.getNewId(PEFunction.vtType),
                                  module_id=7,
                                  port_name='value',
                                  is_alias=0,
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
        self.assertNotEquals(f1.id, f3.id)

    def testComparisonOperators(self):
        f = self.create_function()
        g = self.create_function()
        self.assertEqual(f, g)
        g.module_id = 1 
        self.assertNotEqual(f, g)
        g.module_id = 7
        g.port_name = "val"
        self.assertNotEqual(f, g)
        g.port_name = "value"
        g.is_alias = 1
        self.assertNotEqual(f, g)

    def test_str(self):
        str(self.create_function())

if __name__ == '__main__':
    unittest.main()
    
