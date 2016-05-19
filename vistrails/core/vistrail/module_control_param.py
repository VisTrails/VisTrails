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

from vistrails.db.domain import DBControlParameter

import unittest
import copy

class ModuleControlParam(DBControlParameter):

    # Valid control parameters should be put here
    LOOP_KEY = 'loop_type' # How input lists are combined
    WHILE_COND_KEY = 'while_cond' # Run module in a while loop
    WHILE_INPUT_KEY = 'while_input' # input port for forwarded value
    WHILE_OUTPUT_KEY = 'while_output' # output port for forwarded value
    WHILE_MAX_KEY = 'while_max' # Max iterations
    WHILE_DELAY_KEY = 'while_delay' # delay between iterations
    CACHE_KEY = 'cache' # Turn caching on/off for this module (not implemented)
    JOB_CACHE_KEY = 'job_cache' # Always persist output values to disk

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBControlParameter.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        return ModuleControlParam.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBControlParameter.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleControlParam
        return cp

    @staticmethod
    def convert(_control_parameter):
        _control_parameter.__class__ = ModuleControlParam

    ##########################################################################
    # Properties

    id = DBControlParameter.db_id
    name = DBControlParameter.db_name
    value = DBControlParameter.db_value

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an ModuleControlParam
        object. 

        """
        rep = "<controlParameter id=%s name=%s value=%s</controlParameter>"
        return  rep % (str(self.id), str(self.name), str(self.value))

    def __eq__(self, other):
        """ __eq__(other: ModuleControlParam) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.name != other.name:
            return False
        if self.value != other.value:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Unit tests


class TestModuleControlParam(unittest.TestCase):

    def create_control_parameter(self, id_scope=None):
        from vistrails.db.domain import IdScope

        if id_scope is None:
            id_scope = IdScope()
        control_parameter = ModuleControlParam(id=id_scope.getNewId(ModuleControlParam.vtType),
                                name='name %s',
                                value='some value %s')
        return control_parameter

    def test_copy(self):
        from vistrails.db.domain import IdScope
        id_scope = IdScope()

        a1 = self.create_control_parameter(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.do_copy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

    def test_serialization(self):
        import vistrails.core.db.io
        a1 = self.create_control_parameter()
        xml_str = vistrails.core.db.io.serialize(a1)
        a2 = vistrails.core.db.io.unserialize(xml_str, ModuleControlParam)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)

    def test_str(self):
        a1 = self.create_control_parameter()
        str(a1)
