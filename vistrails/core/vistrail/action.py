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

from datetime import date, datetime
from time import strptime

from core.vistrail.operation import AddOp, ChangeOp, DeleteOp
from db.domain import DBAction

class Action(DBAction):

    ##########################################################################
    # Constructors and copy

    def __init__(self, timestep=0, parent=0, date=None, user=None, notes=None, 
                 operations=None):
        """ __init__(timestep=0, parent=0, date=None, user=None, 
                     notes=None) -> Action
        Action constructor. 
        Keyword Arguments:
         - timestep: int
         - parent: int
         - date: str or datetime
         - user: str
         - notes: str

        """

        if date is not None and type(date) == type(''):
            if date.strip() != '':
                date = datetime(*strptime(date, '%d %b %Y %H:%M:%S')[0:6])
            else:
                date = None

        if operations is None:
            operations = []
        DBAction.__init__(self,
                          id=timestep,
                          prevId=parent,
                          date=date,
                          user=user,
                          operations=operations)
        # FIXME notes should be an anontation on the action?
        self.notes = notes

    def __copy__(self):
        cp = DBAction.__copy__(self)
        cp.__class__ = Action
        cp.notes = self.notes
        return cp
    
    ##########################################################################
    # Properties
    
    def _get_timestep(self):
	return self.db_id
    def _set_timestep(self, timestep):
	self.db_id = timestep
    timestep = property(_get_timestep, _set_timestep)

    def _get_parent(self):
	return self.db_prevId
    def _set_parent(self, parent):
        self.db_prevId = parent
    parent = property(_get_parent, _set_parent)

    def _get_date(self):
	if self.db_date is not None:
	    return self.db_date.strftime('%d %b %Y %H:%M:%S')
	return datetime(1900,1,1).strftime('%d %b %Y %H:%M:%S')

    def _set_date(self, date):
	if date is not None and date.strip() != '':
            newDate = datetime(*strptime(date, '%d %b %Y %H:%M:%S')[0:6])
	    self.db_date = newDate
    date = property(_get_date, _set_date)

    def _get_user(self):
        return self.db_user
    def _set_user(self, user):
        self.db_user = user
    user = property(_get_user, _set_user)
    
    # FIXME DAK figure out where to put these
    #  annotations on actions?
    def _get_notes(self):
        return None
    def _set_notes(self, notes):
        self._notes = notes
    notes = property(_get_notes, _set_notes)

    def _get_operations(self):
        return self.db_operations
    def _set_operations(self, operations):
        self.db_operations = operations
    operations = property(_get_operations, _set_operations)
    def add_operation(self, operation):
        self.db_operations.db_add_operation(operation)

    ##########################################################################
    # DB Conversion
    
    @staticmethod
    def convert(_action):
        _action.__class__ = Action
        for _operation in _action.operations:
            if _operation.vtType == 'add':
                AddOp.convert(_operation)
            elif _operation.vtType == 'change':
                ChangeOp.convert(_operation)
            elif _operation.vtType == 'delete':
                DeleteOp.convert(_operation)
            else:
                raise Exception("Unknown operation type '%s'" % \
                                    _operation.vtType)
            
    ##########################################################################
    # Operators

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: Module) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        """__str__() -> str 
        Returns a string representation of an action object.

        """
        msg = "<<type='%s' timestep='%s' parent='%s' date='%s'" + \
            "user='%s' notes='%s'>>"
        return msg % (type(self),
                      self.timestep,
                      self.parent,
                      self.date,
                      self.user,
                      self.notes)

################################################################################
# Unit tests

import unittest

class TestAction(unittest.TestCase):
    
    def test1(self):
        """Exercises aliasing on modules"""
        import core.vistrail
        import core.xml_parser
        parser = core.xml_parser.XMLParser()
        parser.openVistrail(core.system.vistrails_root_directory() +
                            '/tests/resources/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        p1 = v.getPipeline('final')
        p2 = v.getPipeline('final')
        self.assertEquals(len(p1.modules), len(p2.modules))
        for k in p1.modules.keys():
            if p1.modules[k] is p2.modules[k]:
                self.fail("didn't expect aliases in two different pipelines")

    def test2(self):
        """Exercises aliasing on points"""
        import core.vistrail
        import core.xml_parser
        import core.system
        parser = core.xml_parser.XMLParser()
        parser.openVistrail(core.system.vistrails_root_directory() +
                            '/tests/resources/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        p1 = v.getPipeline('final')
        v.getPipeline('final')
        p2 = v.getPipeline('final')
        m1s = p1.modules.items()
        m2s = p2.modules.items()
        m1s.sort()
        m2s.sort()
        for ((i1,m1),(i2,m2)) in zip(m1s, m2s):
            self.assertEquals(m1.center.x, m2.center.x)
            self.assertEquals(m1.center.y, m2.center.y)

# FIXME aliases need to be fixed (see core.vistrail.pipeline)
    def test3(self):
        """ Exercises aliases manipulation """
        import core.vistrail
        import core.xml_parser
        parser = core.xml_parser.XMLParser()
        parser.openVistrail(core.system.vistrails_root_directory() +
                            '/tests/resources/test_alias.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        p1 = v.getPipeline('alias')
        p2 = v.getPipeline('alias')
        
        # testing removing an alias
        old_id = p1.modules[0].functions[0].params[0].db_id
        old_f_id = p1.modules[0].functions[0].db_id
        params = [(old_id, "2.0", "Float", "")]
        action = v.chg_params_action(parent=-1,
                                     params=params,
                                     function_id=old_f_id)
        p1.performAction(action)
        self.assertEquals(p1.hasAlias('v1'),False)
        v1 = p2.aliases['v1']
        
        old_id2 = p2.modules[2].functions[0].params[0].db_id
        old_f_id2 = p2.modules[2].functions[0].db_id
        params2 = [(old_id2, "2.0", "Float", "v1")]
        action2 = v.chg_params_action(parent=-1,
                                      params=params2,
                                      function_id=old_f_id2)
        p2.performAction(action2)
        self.assertEquals(v1, p2.aliases['v1'])
            
if __name__ == '__main__':
    unittest.main() 
