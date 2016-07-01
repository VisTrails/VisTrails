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
    * PEParam

 """
from __future__ import division

from vistrails.db.domain import DBPEParameter

import unittest
import copy
from vistrails.db.domain import IdScope

################################################################################

class PEParam(DBPEParameter):
    """ Stores a parameter setting for a parameter exploration function """

    ##########################################################################
    # Constructor

    def __init__(self, *args, **kwargs):
        DBPEParameter.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        if self.pos is None:
            self.pos = -1
        if self.interpolator is None:
            self.interpolator = ""
        if self.value is None:
            self.value = ""
        if self.dimension is None:
            self.dimension = -1
    
    def __copy__(self):
        return PEParam.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPEParameter.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = PEParam
        return cp

    @staticmethod
    def convert(_parameter):
        if _parameter.__class__ == PEParam:
            return
        _parameter.__class__ = PEParam

    ##########################################################################

    id = DBPEParameter.db_id
    pos = DBPEParameter.db_pos
    interpolator = DBPEParameter.db_interpolator
    value = DBPEParameter.db_value
    dimension = DBPEParameter.db_dimension


    ##########################################################################
    # Operators

    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        return ("(PEParam id=%s pos=%s interpolator='%s' value='%s' dimension=%s)@%X" %
                (self.id,
                 self.pos,
                 self.interpolator,
                 self.value,
                 self.dimension,
                 id(self)))

    def __eq__(self, other):
        """ __eq__(other: PEParam) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.pos != other.pos:
            return False
        if self.interpolator != other.interpolator:
            return False
        if self.value != other.value:
            return False
        if self.dimension != other.dimension:
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


class TestModuleParam(unittest.TestCase):

    def create_param(self, id_scope=IdScope()):
        param = PEParam(id=id_scope.getNewId(PEParam.vtType),
                            pos=1,
                            interpolator='normal-int',
                            value='[1, 2]',
                            dimension=1)
        return param

    def test_copy(self):        
        id_scope = IdScope()
        p1 = self.create_param(id_scope)
        p2 = copy.copy(p1)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)
        p3 = p1.do_copy(True, id_scope, {})
        self.assertEquals(p1, p3)
        self.assertNotEquals(p1.id, p3.id)

    def testComparisonOperators(self):
        """ Test comparison operators """
        p = self.create_param()
        q = self.create_param()
        self.assertEqual(p, q)
        q.pos = 2
        self.assertNotEqual(p, q)
        q.pos = 1
        q.interpolator = 'other-int'
        self.assertNotEqual(p, q)
        q.interpolator = 'normal-int'
        q.value = '[1, 3]'
        self.assertNotEqual(p, q)
        q.value = '[1, 2]'
        q.dimension = 2
        self.assertNotEqual(p, q)

    def test_str(self):
        str(self.create_param())
