############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

from db.domain import DBActionAnnotation

class ActionAnnotation(DBActionAnnotation):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBActionAnnotation.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        return ActionAnnotation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBActionAnnotation.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ActionAnnotation
        return cp

    @staticmethod
    def convert(_annotation):
        _annotation.__class__ = ActionAnnotation

    ##########################################################################
    # Properties

    id = DBActionAnnotation.db_id
    key = DBActionAnnotation.db_key
    value = DBActionAnnotation.db_value
    action_id = DBActionAnnotation.db_action_id
    date = DBActionAnnotation.db_date
    user = DBActionAnnotation.db_user

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an
        ActionAnnotation object.

        """
        rep = ("<actionAnnotation id=%s action_id=%s key=%s value=%s "
               "date=%s user=%s</annotation>")
        return  rep % (str(self.id), str(self.action_id), str(self.key), 
                       str(self.value), str(self.date), str(self.user))

    def __eq__(self, other):
        """ __eq__(other: ActionAnnotation) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.key != other.key:
            return False
        if self.value != other.value:
            return False
        if self.action_id != other.action_id:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Unit tests

import unittest
import copy

class TestActionAnnotation(unittest.TestCase):

    def create_annotation(self, id_scope=None):
        from db.domain import IdScope

        if id_scope is None:
            id_scope = IdScope()
        annotation = \
            ActionAnnotation(id=id_scope.getNewId(ActionAnnotation.vtType),
                             key='akey', action_id=1L,
                             value='some value', user='test')
        return annotation

    def test_copy(self):
        from db.domain import IdScope
        id_scope = IdScope()

        a1 = self.create_annotation(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.do_copy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

    def test_serialization(self):
        import core.db.io
        a1 = self.create_annotation()
        xml_str = core.db.io.serialize(a1)
        a2 = core.db.io.unserialize(xml_str, ActionAnnotation)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)

    def test_str(self):
        a1 = self.create_annotation()
        str(a1)
