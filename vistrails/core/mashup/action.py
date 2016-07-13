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

from vistrails.core.system import strftime, time_strptime
from vistrails.db.domain import DBMashupAction
from vistrails.core.mashup.mashup import Mashup

class Action(DBMashupAction):
    
    def __init__(self, id, prevId, user='', mashup=None, date=None):
        DBMashupAction.__init__(self, id, prevId, date, user, mashup)
        
    id = DBMashupAction.db_id
    prevId = DBMashupAction.db_prevId
    parent_id = DBMashupAction.db_prevId
    user = DBMashupAction.db_user
    mashup = DBMashupAction.db_mashup
        
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
        
    @staticmethod
    def convert(_action):
        if _action.__class__ == Action:
            return
        _action.__class__ = Action
        Mashup.convert(_action.mashup)
         
    def __copy__(self):
        return Action.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupAction.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Action
        Mashup.convert(cp.mashup)
        return cp
    
#    def toXml(self, node=None):
#        """toXml(node: ElementTree.Element) -> ElementTree.Element
#           writes itself to xml
#        """
#
#        if node is None:
#            node = ElementTree.Element('action')
#        
#        #set attributes
#        node.set('id', self.convert_to_str(self.id,'long'))
#        node.set('parent_id', self.convert_to_str(self.parent_id,'long'))
#        node.set('user', self.convert_to_str(self.user,'str'))
#        node.set('date', self.convert_to_str(self._date,'datetime'))
#        mnode = ElementTree.SubElement(node, 'mashup')
#        self.mashup.toXml(mnode)
#        return node
#    
#    @staticmethod
#    def fromXml(node):
#        if node.tag != 'action':
#            debug.debug("node.tag != 'action'")
#            return None
#        #read attributes
#        data = node.get('id', None)
#        id = Action.convert_from_str(data, 'long')
#        data = node.get('parent_id', None)
#        parent_id = Action.convert_from_str(data, 'long')
#        data = node.get('user', None)
#        user = Action.convert_from_str(data, 'str')
#        data = node.get('date', None)
#        date = Action.convert_from_str(data, 'datetime')
#        child = node.getchildren()[0]
#        if child.tag == 'mashup':
#            mashup = Mashup.fromXml(child)
#        return Action(id=id, parent_id=parent_id, mashup=mashup, user=user,
#                      date=date)
        
    ##########################################################################
    # Operators
    
    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        
        msg = "<<type='%s' id='%s' parent_id='%s' date='%s' user='%s'>>"
        return msg % (type(self),
                      self.id,
                      self.prevId,
                      self.db_date,
                      self.user)
        
    def __eq__(self, other):
        """ __eq__(other: Alias) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.mashup != other.mashup:
            return False
        return True

    def __ne__(self, other):
        """ __ne__(other: Component) -> boolean
        Returns True if self and other don't have the same attributes. 
        Used by !=  operator. 
        
        """
        return not self.__eq__(other)
################################################################################
            
import unittest
from vistrails.db.domain import IdScope
import copy

class TestAction(unittest.TestCase):
    def create_action(self, id_scope=IdScope()):
        from vistrails.core.mashup.component import Component
        from vistrails.core.mashup.alias import Alias
        from vistrails.core.mashup.mashup import Mashup
        c1 = Component(id=id_scope.getNewId('mashup_component'),
                          vttype='parameter', param_id=15L, 
                          parent_vttype='function', parent_id=3L, mid=4L,
                          type='String', value='test', p_pos=0, pos=1, 
                          strvaluelist='test1,test2', widget="text")
        a1 = Alias(id=id_scope.getNewId('mashup_alias'), name='alias1', component=c1)
        
        m = Mashup(id=id_scope.getNewId('mashup'), name='mashup1', vtid='empty.vt', 
                   version=15L, alias_list=[a1])
        action = Action(id=id_scope.getNewId('mashup_action'),
                        prevId=0L,
                        date=datetime(2007,11,18),
                        mashup=m)
        return action
    
    def test_copy(self):
        id_scope = IdScope()
        a1 = self.create_action(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.do_copy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

#    def test_serialization(self):
#        a1 = self.create_action()
#        node = a1.toXml()
#        a2 = Action.fromXml(node)
#        self.assertEquals(a1, a2)
#        self.assertEquals(a1.id, a2.id)
        
    def test_str(self):
        a1 = self.create_action()
        str(a1)
