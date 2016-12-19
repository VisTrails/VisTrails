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

from vistrails.db.domain import DBTag

import unittest
import copy
from vistrails.db.domain import IdScope
import vistrails.core

class Tag(DBTag):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBTag.__init__(self, *args, **kwargs)
        
    def __copy__(self):
        return Tag.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBTag.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Tag
        return cp

    @staticmethod
    def convert(_tag):
        _tag.__class__ = Tag
    
    ##########################################################################
    # Properties

    id = DBTag.db_id
    time = DBTag.db_id
    name = DBTag.db_name

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of a Tag
        object. 

        """
        rep = "<tag name=%s time=%s />"
        return  rep % (str(self.name), str(self.time))

    def __eq__(self, other):
        """ __eq__(other: Annotation) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Testing


class TestTag(unittest.TestCase):

    def create_tag(self, id_scope=IdScope()):
        tag = Tag(id=id_scope.getNewId(Tag.vtType),
                  name='blah')
        return tag

    def test_copy(self):
        id_scope = IdScope()
        
        t1 = self.create_tag(id_scope)
        t2 = copy.copy(t1)
        self.assertEquals(t1, t2)
        self.assertEquals(t1.id, t2.id)
        t3 = t1.do_copy(True, id_scope, {})
        self.assertEquals(t1, t3)
        self.assertNotEquals(t1.id, t3.id)

    def test_serialization(self):
        import vistrails.core.db.io
        t1 = self.create_tag()
        xml_str = vistrails.core.db.io.serialize(t1)
        t2 = vistrails.core.db.io.unserialize(xml_str, Tag)
        self.assertEquals(t1, t2)
        self.assertEquals(t1.id, t2.id)
