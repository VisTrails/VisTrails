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

from vistrails.db.domain import DBVistrailVariable

import unittest
import copy
import vistrails.core

class VistrailVariable(DBVistrailVariable):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBVistrailVariable.__init__(self, *args, **kwargs)
        
    def __copy__(self):
        return VistrailVariable.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBVistrailVariable.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = VistrailVariable
        return cp

    @staticmethod
    def convert(_vistrailvariable):
        _vistrailvariable.__class__ = VistrailVariable

    ##########################################################################
    # Properties

    name = DBVistrailVariable.db_name
    uuid = DBVistrailVariable.db_uuid
    package = DBVistrailVariable.db_package
    module = DBVistrailVariable.db_module
    namespace = DBVistrailVariable.db_namespace
    value = DBVistrailVariable.db_value

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of a
        VistrailVariable object. 

        """
        rep = "<vistrailvariable name=%s uuid=%s package=%s module=%s \
namespace=%s value=%s</vistrailvariable>"
        return  rep % (str(self.name), str(self.uuid), str(self.package),
                       str(self.module), str(self.namespace), str(self.value))

    def __eq__(self, other):
        """ __eq__(other: VistrailVariable) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.name != other.name:
            return False
        if self.uuid != other.uuid:
            return False
        if self.package != other.package:
            return False
        if self.module != other.module:
            return False
        if self.namespace != other.namespace:
            return False
        if self.value != other.value:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Unit tests


class TestVistrailVariable(unittest.TestCase):

    def create_vv(self):
        var = VistrailVariable('a','false uuid','pack','module',"ns","3.14")
        return var

    def test_copy(self):
        a1 = self.create_vv()
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        a3 = a1.do_copy()
        self.assertEquals(a1, a3)

    def test_serialization(self):
        import vistrails.core.db.io
        a1 = self.create_vv()
        xml_str = vistrails.core.db.io.serialize(a1)
        a2 = vistrails.core.db.io.unserialize(xml_str, VistrailVariable)
        self.assertEquals(a1, a2)

    def test_str(self):
        a1 = self.create_vv()
        str(a1)
