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

import urllib
from vistrails.core.mashup import conv_from_bool, conv_to_bool, convert_symbols
from vistrails.db.domain import DBMashupComponent

import unittest
from vistrails.db.domain import IdScope
import copy

################################################################################
class Component(DBMashupComponent):
    def __init__(self, id, vttype, param_id, parent_vttype, parent_id, mid, 
                 type, value, p_pos, pos, strvaluelist, minVal="0",
                 maxVal="1", stepSize="1", parent='', seq=0, widget="text"):
    
        """Component() 
        widget can be: text, slider, combobox, numericstepper, checkbox

        """
        DBMashupComponent.__init__(self, id, param_id, vttype, parent_vttype, 
                                   parent_id, p_pos, mid, pos, type, value, 
                                   minVal, maxVal, stepSize, strvaluelist, 
                                   widget, seq, parent)
        if isinstance(seq, bool):
            self.seq = seq

    id = DBMashupComponent.db_id
    vttype = DBMashupComponent.db_vttype
    vtid = DBMashupComponent.db_vtid
    vtparent_type = DBMashupComponent.db_vtparent_type
    vtparent_id = DBMashupComponent.db_vtparent_id
    vtmid = DBMashupComponent.db_vtmid
    vtpos = DBMashupComponent.db_vtpos
    pos = DBMashupComponent.db_pos
    type = DBMashupComponent.db_type
    minVal = DBMashupComponent.db_minVal
    maxVal = DBMashupComponent.db_maxVal
    stepSize = DBMashupComponent.db_stepSize
    parent = DBMashupComponent.db_parent
    widget = DBMashupComponent.db_widget
    strvaluelist = DBMashupComponent.db_strvaluelist
    
    def _get_seq(self):
        return conv_to_bool(self.db_seq)
    def _set_seq(self, s):
        self.db_seq = conv_from_bool(s)
    seq = property(_get_seq,_set_seq)
     
    def _get_val(self):
        self.db_val = convert_symbols(self.db_val)
        return self.db_val
    def _set_val(self, v):
        self.db_val = v
    val = property(_get_val,_set_val)
    
    def _get_valuelist(self):
        self.strvaluelist = convert_symbols(self.strvaluelist)
        data = self.strvaluelist.split(',')
        result = []
        for d in data:
            result.append(urllib.unquote_plus(d))
        return result
    def _set_valuelist(self, valuelist):
        q = []
        for v in valuelist:
            q.append(urllib.quote_plus(v))
        self.strvaluelist = ",".join(q)
    valueList = property(_get_valuelist,_set_valuelist)

    @staticmethod
    def convert(_component):
        _component.__class__ = Component
        
    def __copy__(self):
        return Component.do_copy(self)
    
    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        """do_copy() -> Component 
        returns a clone of itself"""
        cp = DBMashupComponent.do_copy(self, new_ids, id_scope, id_remap)      
        Component.convert(cp)
        return cp
    
    ##########################################################################
    # Serialization / Unserialization
    
#    def toXml(self, node=None):
#        """toXml(node: ElementTree.Element) -> ElementTree.Element
#             writes itself to xml
#        """
#        if node is None:
#            node = ElementTree.Element('component')
#        #set attributes
#        node.set('id', self.convert_to_str(self.id,'long'))
#        node.set('vttype', self.convert_to_str(self.vttype,'str'))
#        node.set('vtid', self.convert_to_str(self.vtid,'long'))
#        node.set('vtparent_type', self.convert_to_str(self.vtparent_type,'str'))
#        node.set('vtparent_id', self.convert_to_str(self.vtparent_id,'long'))
#        node.set('vtmid', self.convert_to_str(self.vtmid,'long'))
#        node.set('vtpos', self.convert_to_str(self.vtpos,'long'))
#        
#        node.set('pos', self.convert_to_str(self.pos,'long'))
#        node.set('type', self.convert_to_str(self.type,'str'))
#        
#        node.set('val', self.convert_to_str(self.val, 'str'))
#        node.set('minVal', self.convert_to_str(self.minVal,'str'))
#        node.set('maxVal', self.convert_to_str(self.maxVal,'str'))
#        node.set('stepSize', self.convert_to_str(self.stepSize,'str'))
#        node.set('valueList',self.convert_to_str(self.strvaluelist,'str'))
#        node.set('parent', self.convert_to_str(self.parent,'str'))
#        node.set('seq', self.convert_to_str(self.seq,'bool'))
#        node.set('widget',self.convert_to_str(self.widget,'str'))
#        return node
#
#    @staticmethod
#    def fromXml(node):
#        if node.tag != 'component':
#            return None
#
#        #read attributes
#        data = node.get('id', None)
#        id = Component.convert_from_str(data, 'long')
#        data = node.get('vttype', None)
#        vttype = Component.convert_from_str(data, 'str')
#        data = node.get('vtid', None)
#        vtid = Component.convert_from_str(data, 'long')
#        data = node.get('vtparent_type', None)
#        vtparent_type = Component.convert_from_str(data, 'str')
#        data = node.get('vtparent_id', None)
#        vtparent_id = Component.convert_from_str(data, 'long')
#        data = node.get('vtmid', None)
#        vtmid = Component.convert_from_str(data, 'long')
#        data = node.get('vtpos', None)
#        vtpos = Component.convert_from_str(data, 'long')
#        data = node.get('pos', None)
#        pos = Component.convert_from_str(data, 'long')
#        data = node.get('type', None)
#        type = Component.convert_from_str(data, 'str')
#        data = node.get('val', None)
#        val = Component.convert_from_str(data, 'str')
#        val = val.replace("&lt;", "<")
#        val = val.replace("&gt;", ">")
#        val = val.replace("&amp;","&")
#        data = node.get('minVal', None)
#        minVal = Component.convert_from_str(data, 'str')
#        data = node.get('maxVal', None)
#        maxVal = Component.convert_from_str(data, 'str')
#        data = node.get('stepSize', None)
#        stepSize = Component.convert_from_str(data, 'str')
#        data = node.get('valueList', None)
#        values = Component.convert_from_str(data, 'str')
#        values = values.replace("&lt;", "<")
#        values = values.replace("&gt;", ">")
#        values = values.replace("&amp;","&")
#        data = node.get('parent', None)
#        parent = Component.convert_from_str(data, 'str')
#        data = node.get('seq', None)
#        seq = Component.convert_from_str(data, 'bool')
#        data = node.get('widget', None)
#        widget = Component.convert_from_str(data, 'str')
#       
#        component = Component(id=id, vttype=vttype, param_id=vtid, 
#                              parent_vttype=vtparent_type, 
#                              parent_id=vtparent_id, mid=vtmid, type=type,
#                              value=val, p_pos=vtpos, pos=pos,
#                              minVal=minVal,
#                              maxVal=maxVal,
#                              stepSize=stepSize,
#                              strvaluelist=values,
#                              parent=parent,
#                              seq=seq,
#                              widget=widget)
#        return component

    ##########################################################################
    # Operators

    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        
        return ("(Component id='%s' vttype='%s' vtid='%s' vtparent_type='%s' \
vtparent_id='%s' vtmid='%s' vtpos='%s' type='%s' pos='%s' val='%s' minVal='%s' \
maxVal='%s' stepSize='%s' strvaluelist='%s' parent='%s' seq='%s' widget='%s')@%X" %
                    (self.id,
                     self.vttype,
                     self.vtid,
                     self.vtparent_type,
                     self.vtparent_id,
                     self.vtmid,
                     self.vtpos,
                     self.type,
                     self.pos,
                     self.val,
                     self.minVal,
                     self.maxVal,
                     self.stepSize,
                     self.strvaluelist,
                     self.parent,
                     self.seq,
                     self.widget,
                     id(self)))

    def __eq__(self, other):
        """ __eq__(other: Component) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.vttype != other.vttype:
            return False
        if self.vtid != other.vtid:
            return False
        if self.vtparent_type != other.vtparent_type:
            return False
        if self.vtparent_id != other.vtparent_id:
            return False
        if self.vtmid != other.vtmid:
            return False
        if self.vtpos != other.vtpos:
            return False
        if self.type != other.type:
            return False
        if self.pos != other.pos:
            return False
        if self.val != other.val:
            return False
        if self.minVal != other.minVal:
            return False
        if self.maxVal != other.maxVal:
            return False
        if self.stepSize != other.stepSize:
            return False
        if self.strvaluelist != other.strvaluelist:
            return False
        if self.parent != other.parent:
            return False
        if self.seq != other.seq:
            return False
        if self.widget != other.widget:
            return False
        return True

    def __ne__(self, other):
        """ __ne__(other: Component) -> boolean
        Returns True if self and other don't have the same attributes. 
        Used by !=  operator. 
        
        """
        return not self.__eq__(other)
    
################################################################################


class TestComponent(unittest.TestCase):
    def create_component(self, id_scope=IdScope()):
        c = Component(id=id_scope.getNewId('mashup_component'),
                          vttype='parameter', param_id=15L, 
                          parent_vttype='function', parent_id=3L, mid=4L,
                          type='String', value='test', p_pos=0, pos=1, 
                          strvaluelist='test1,test2', widget="text")
        return c
    
    def test_copy(self):
        id_scope = IdScope()
        c1 = self.create_component(id_scope)
        c2 = copy.copy(c1)
        self.assertEqual(c1, c2)
        self.assertEqual(c1.id, c2.id)
        c3 = c2.do_copy(True, id_scope, {})
        self.assertEqual(c1,c3)
        self.assertNotEqual(c1.id, c3.id)
        
    def test_valuelist(self):
        c1 = self.create_component()
        c1.strvaluelist = "1,2,3"
        self.assertEqual(['1','2','3'], c1.valueList)
        c1.valueList = ['1','2','3']
        self.assertEqual(c1.strvaluelist,"1,2,3")
        
#        #testing values with , after serialization
#        c1.valueList = ['a,b,c', '123', ',as']
#        c2 = Component.fromXml(c1.toXml())
#        self.assertEqual(c1.strvaluelist, c2.strvaluelist)
#        self.assertEqual(c1.valueList, c2.valueList)
#        self.assertEqual(c2.valueList, ['a,b,c', '123', ',as'])
        
    def test_str(self):
        c1 = self.create_component()
        str(c1)
        