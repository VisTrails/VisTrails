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

from db.domain import DBTag

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

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)
    time = property(_get_id, _set_id)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

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

import unittest
import copy
from db.domain import IdScope

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
        import core.db.io
        t1 = self.create_tag()
        xml_str = core.db.io.serialize(t1)
        t2 = core.db.io.unserialize(xml_str, Tag)
        self.assertEquals(t1, t2)
        self.assertEquals(t1.id, t2.id)
