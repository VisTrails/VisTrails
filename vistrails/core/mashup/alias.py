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

from vistrails.db.domain import DBMashupAlias
from vistrails.core.mashup.component import Component

import unittest
from vistrails.db.domain import IdScope
import copy

################################################################################
class Alias(DBMashupAlias):
    def __init__(self, id, name, component=None):
        DBMashupAlias.__init__(self, id, name, component)
    
    id = DBMashupAlias.db_id
    name = DBMashupAlias.db_name
    component = DBMashupAlias.db_component
    
    @staticmethod
    def convert(_alias):
        _alias.__class__ = Alias
        Component.convert(_alias.component)
        
    def __copy__(self):
        return Alias.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupAlias.do_copy(self, new_ids, id_scope, id_remap)
        Alias.convert(cp)
        return cp
    
    ##########################################################################
    # Serialization / Unserialization
        
#    def toXml(self, node=None):
#        """toXml(node: ElementTree.Element) -> ElementTree.Element
#            writes itself to xml
#        """
#        if node is None:
#            node = ElementTree.Element('alias')
#
#        #set attributes
#        node.set('id', self.convert_to_str(self.id,'long'))
#        node.set('name', self.convert_to_str(self.name,'str'))
#        child_ = ElementTree.SubElement(node, 'component')
#        self.component.toXml(child_)
#
#        return node
#
#    @staticmethod
#    def fromXml(node):
#        if node.tag != 'alias':
#            return None
#
#        #read attributes
#        data = node.get('id', None)
#        id = Alias.convert_from_str(data, 'long')
#        data = node.get('name', None)
#        name = Alias.convert_from_str(data, 'str')
#        for child in node.getchildren():
#            if child.tag == "component":
#                component = Component.fromXml(child)
#        alias = Alias(id,name,component)
#        return alias
    
    ##########################################################################
    # Operators
    
    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        
        return ("(Alias id='%s' name='%s' component=%s)@%X" %
                    (self.id,
                     self.name,
                     self.component,
                     id(self)))

    def __eq__(self, other):
        """ __eq__(other: Alias) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.name != other.name:
            return False
        if self.component != other.component:
            return False
        return True

    def __ne__(self, other):
        """ __ne__(other: Component) -> boolean
        Returns True if self and other don't have the same attributes. 
        Used by !=  operator. 
        
        """
        return not self.__eq__(other)

################################################################################


class TestAlias(unittest.TestCase):
    def create_alias(self, id_scope=IdScope()):
        c1 = Component(id=id_scope.getNewId('mashup_component'),
                          vttype='parameter', param_id=15L, 
                          parent_vttype='function', parent_id=3L, mid=4L,
                          type='String', value='test', p_pos=0, pos=1, 
                          strvaluelist='test1,test2', widget="text")
        a1 = Alias(id=id_scope.getNewId('mashup_alias'), name='alias1', component=c1)
        return a1
    
    def test_copy(self):
        id_scope = IdScope()
        a1 = self.create_alias(id_scope)
        a2 = copy.copy(a1)
        self.assertEqual(a1,a2)
        self.assertEqual(a1.id, a2.id)
        a3 = a2.do_copy(True, id_scope, {})
        self.assertEqual(a1,a3)
        self.assertNotEqual(a1.id, a3.id)
        
#    def test_serialization(self):
#        a1 = self.create_alias()
#        node = a1.toXml()
#        a2 = Alias.fromXml(node)
#        self.assertEqual(a1, a2)
#        self.assertEqual(a1.id, a2.id)
        
    def test_str(self):
        a1 = self.create_alias()
        str(a1)
