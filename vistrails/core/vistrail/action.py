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

from datetime import datetime
from itertools import izip
import unittest

from vistrails.db.domain import DBAction
from vistrails.core.system import strftime, time_strptime
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.operation import AddOp, ChangeOp, DeleteOp

class Action(DBAction):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAction.__init__(self, *args, **kwargs)
        if self.timestep is None:
            self.timestep = -1
        if self.parent is None:
            self.parent = -1
        if self.user is None:
            self.user = ''
        if self.expand is None:
            self.expand = 0

    def __copy__(self):
        return Action.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAction.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Action
        return cp
    
    ##########################################################################
    # Constants

    ANNOTATION_DESCRIPTION = '__description__'
    ANNOTATION_ANALOGY_INFO = '__analogy_info__'

    ##########################################################################
    # Properties

    id = DBAction.db_id
    timestep = DBAction.db_id
    parent = DBAction.db_prevId
    prevId = DBAction.db_prevId
    session = DBAction.db_session
    user = DBAction.db_user
    expand = 0
    annotations = DBAction.db_annotations
    operations = DBAction.db_operations

    def _get_date(self):
        if self.db_date is not None:
            return strftime(self.db_date, '%d %b %Y %H:%M:%S')
        return strftime(datetime(1900,1,1), '%d %b %Y %H:%M:%S')

    def _set_date(self, date):
        if isinstance(date, datetime):
            self.db_date = date
        elif isinstance(date, basestring) and date.strip() != '':
            newDate = datetime(*time_strptime(date, '%d %b %Y %H:%M:%S')[0:6])
            self.db_date = newDate
    date = property(_get_date, _set_date)

    def has_annotation_with_key(self, key):
        return self.db_has_annotation_with_key(key)
    def get_annotation_by_key(self, key):
        return self.db_get_annotation_by_key(key)
    def add_annotation(self, annotation):
        self.db_add_annotation(annotation)
    def delete_annotation(self, annotation):
        self.db_delete_annotation(annotation)

    def _get_description(self):
        if self.db_has_annotation_with_key(self.ANNOTATION_DESCRIPTION):
            return \
                self.db_get_annotation_by_key(self.ANNOTATION_DESCRIPTION).value
        return None
    description = property(_get_description)

    def _get_analogy_info(self):
        if self.db_has_annotation_with_key(self.ANNOTATION_ANALOGY_INFO):
            ann = self.db_get_annotation_by_key(self.ANNOTATION_ANALOGY_INFO)
            return ann.value
        return None
    analogy_info = property(_get_analogy_info)

    def add_operation(self, operation):
        self.db_operations.db_add_operation(operation)

    ##########################################################################
    # DB Conversion
    
    @staticmethod
    def convert(_action):
        if _action.__class__ == Action:
            return
        _action.__class__ = Action
        for _annotation in _action.annotations:
            Annotation.convert(_annotation)
        for _operation in _action.operations:
            if _operation.vtType == 'add':
                AddOp.convert(_operation)
            elif _operation.vtType == 'change':
                ChangeOp.convert(_operation)
            elif _operation.vtType == 'delete':
                DeleteOp.convert(_operation)
            else:
                raise TypeError("Unknown operation type '%s'" %
                                _operation.vtType)
            
    ##########################################################################
    # Operators

    def __eq__(self, other):
        """ __eq__(other: Module) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if len(self.annotations) != len(other.annotations):
            return False
        if len(self.operations) != len(other.operations):
            return False
        for f,g in zip(self.annotations, other.annotations):
            if f != g:
                return False
        for f,g in zip(self.operations, other.operations):
            if f != g:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        """__str__() -> str 
        Returns a string representation of an action object.

        """
        msg = "<<type='%s' timestep='%s' parent='%s' date='%s'" + \
            "user='%s'>>"
        return msg % (type(self),
                      self.timestep,
                      self.parent,
                      self.date,
                      self.user)

################################################################################
# Unit tests

class TestAction(unittest.TestCase):
    
    def create_action(self, id_scope=None):
        from vistrails.core.modules.basic_modules import identifier as basic_pkg
        from vistrails.core.vistrail.action import Action
        from vistrails.core.vistrail.module import Module
        from vistrails.core.vistrail.module_function import ModuleFunction
        from vistrails.core.vistrail.module_param import ModuleParam
        from vistrails.db.domain import IdScope
        
        if id_scope is None:
            id_scope = IdScope()
        param = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                            type='Integer',
                            val='1')
        function = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                  name='value',
                                  parameters=[param])
        m = Module(id=id_scope.getNewId(Module.vtType),
                   name='Float',
                   package=basic_pkg,
                   functions=[function])

        add_op = AddOp(id=id_scope.getNewId('operation'),
                       what='module',
                       objectId=m.id,
                       data=m)
        action = Action(id=id_scope.getNewId(Action.vtType),
                        prevId=0,
                        date=datetime(2007,11,18),
                        operations=[add_op])
        return action

    def test_copy(self):
        import copy
        from vistrails.db.domain import IdScope
        
        id_scope = IdScope()
        a1 = self.create_action(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.do_copy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

    def test_serialization(self):
        import vistrails.core.db.io
        a1 = self.create_action()
        xml_str = vistrails.core.db.io.serialize(a1)
        a2 = vistrails.core.db.io.unserialize(xml_str, Action)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)

    def test1(self):
        """Exercises aliasing on modules"""
        import vistrails.core.system
        from vistrails.core.db.locator import XMLFileLocator
        v = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                           '/tests/resources/dummy.xml').load()
        p1 = v.getPipeline('final')
        p2 = v.getPipeline('final')
        self.assertEquals(len(p1.modules), len(p2.modules))
        for k in p1.modules.keys():
            if p1.modules[k] is p2.modules[k]:
                self.fail("didn't expect aliases in two different pipelines")

    def test2(self):
        """Exercises aliasing on points"""
        from vistrails.core.db.locator import XMLFileLocator
        import vistrails.core.system
        v = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                            '/tests/resources/dummy.xml').load()
        p1 = v.getPipeline('final')
        v.getPipeline('final')
        p2 = v.getPipeline('final')
        m1s = p1.modules.items()
        m2s = p2.modules.items()
        m1s.sort()
        m2s.sort()
        for ((i1,m1),(i2,m2)) in izip(m1s, m2s):
            self.assertEquals(m1.center.x, m2.center.x)
            self.assertEquals(m1.center.y, m2.center.y)
            
if __name__ == '__main__':
    unittest.main() 
