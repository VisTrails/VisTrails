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
from vistrails.db.domain import DBMashupActionAnnotation

class ActionAnnotation(DBMashupActionAnnotation):
    def __init__(self, id, action_id, key=None, value=None, user=None, date=None):
        DBMashupActionAnnotation.__init__(self, id, key, value, action_id, date, 
                                          user)
    id = DBMashupActionAnnotation.db_id
    action_id = DBMashupActionAnnotation.db_action_id
    key = DBMashupActionAnnotation.db_key
    value = DBMashupActionAnnotation.db_value
    user = DBMashupActionAnnotation.db_user
        
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
    def convert(_annotation):
        _annotation.__class__ = ActionAnnotation
        
    def __copy__(self):
        return ActionAnnotation.do_copy(self)
    
    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupActionAnnotation.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ActionAnnotation
        return cp
    
#    def toXml(self, node=None):
#        """toXml(node: ElementTree.Element) -> ElementTree.Element
#           writes itself to xml
#        """
#
#        if node is None:
#            node = ElementTree.Element('actionAnnotation')
#        
#        #set attributes
#        node.set('id', self.convert_to_str(self.id,'long'))
#        node.set('action_id', self.convert_to_str(self.action_id,'long'))
#        node.set('user', self.convert_to_str(self.user,'str'))
#        node.set('key', self.convert_to_str(self.key,'str'))
#        node.set('value', self.convert_to_str(self.value,'str'))
#        node.set('date', self.convert_to_str(self._date,'datetime'))
#        return node
#    
#    @staticmethod
#    def fromXml(node):
#        if node.tag != 'actionAnnotation':
#            debug.debug("node.tag != 'actionAnnotation'")
#            return None
#        #read attributes
#        data = node.get('id', None)
#        id = Action.convert_from_str(data, 'long')
#        data = node.get('action_id', None)
#        action_id = Action.convert_from_str(data, 'long')
#        data = node.get('key', None)
#        key = Action.convert_from_str(data, 'str')
#        data = node.get('value', None)
#        value = Action.convert_from_str(data, 'str')
#        data = node.get('user', None)
#        user = Action.convert_from_str(data, 'str')
#        data = node.get('date', None)
#        date = Action.convert_from_str(data, 'datetime')
#        return ActionAnnotation(id=id, action_id=action_id, key=key, value=value,
#                      user=user, date=date)
    
    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an
        mashup_actionAnnotation object.

        """
        rep = ("<mashup_actionAnnotation id=%s action_id=%s key=%s value=%s "
               "date=%s user=%s</annotation>")
        return  rep % (str(self.id), str(self.action_id), str(self.key), 
                       str(self.value), str(self.date), str(self.user))

    def __eq__(self, other):
        """ __eq__(other: mashup_actionAnnotation) -> boolean
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
import unittest
from vistrails.db.domain import IdScope
import copy

class TestActionAnnotation(unittest.TestCase):
    def create_annotation(self, id_scope=IdScope()):

        annotation = \
            ActionAnnotation(id=id_scope.getNewId('mashup_actionAnnotation'),
                             key='akey', action_id=1L,
                             value='some value', user='test')
        return annotation

    def test_copy(self):
        id_scope = IdScope()
        a1 = self.create_annotation(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.do_copy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

#    def test_serialization(self):
#        a1 = self.create_annotation()
#        node = a1.toXml()
#        a2 = ActionAnnotation.fromXml(node)
#        self.assertEquals(a1, a2)
#        self.assertEquals(a1.id, a2.id)

    def test_str(self):
        a1 = self.create_annotation()
        str(a1)
