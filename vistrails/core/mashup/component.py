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
import urllib

from core.mashup import XMLObject
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

################################################################################
class Component(XMLObject):
    def __init__(self, id, vttype, param_id, parent_vttype, parent_id, mid, 
                 type, value, p_pos, pos, strvaluelist, minVal="0",
                 maxVal="1", stepSize="1", parent=None, seq=False, widget="text"):
    
        """Component() 
        widget can be: text, slider, combobox, numericstepper, checkbox

        """
        self.id = id
        self.vttype = vttype
        self.vtid = param_id
        self.vtparent_type = parent_vttype
        self.vtparent_id = parent_id
        self.vtmid = mid
        self.vtpos = p_pos
        self.type = type
        self.pos = pos
        self.val = value
        self.minVal = minVal
        self.maxVal = maxVal
        self.stepSize = stepSize
        self.strvaluelist = strvaluelist
        self.parent = parent
        self.seq = seq
        self.widget = widget

    def _get_valuelist(self):
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

    def __copy__(self):
        return Component.doCopy(self)
    
    def doCopy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Component 
        returns a clone of itself"""
        cp = Component(id=self.id, vttype=self.vttype, param_id=self.vtid, 
                       parent_vttype=self.vtparent_type, 
                       parent_id=self.vtparent_id, mid = self.vtmid, 
                       type = self.type, value = self.val, p_pos = self.vtpos, 
                       pos = self.pos, strvaluelist = self.strvaluelist, 
                       minVal = self.minVal, maxVal= self.maxVal, 
                       stepSize=self.stepSize, parent=self.parent, 
                       seq = self.seq, widget=self.widget)
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId('component')
            if 'component' in id_scope.remap:
                id_remap[(id_scope.remap['component'], self.id)] = new_id
            else:
                id_remap[('component', self.id)] = new_id
            cp.id = new_id
        return cp
    
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
             writes itself to xml
        """
        if node is None:
            node = ElementTree.Element('component')
        #set attributes
        node.set('id', self.convert_to_str(self.id,'long'))
        node.set('vttype', self.convert_to_str(self.vttype,'str'))
        node.set('vtid', self.convert_to_str(self.vtid,'long'))
        node.set('vtparent_type', self.convert_to_str(self.vtparent_type,'str'))
        node.set('vtparent_id', self.convert_to_str(self.vtparent_id,'long'))
        node.set('vtmid', self.convert_to_str(self.vtmid,'long'))
        node.set('vtpos', self.convert_to_str(self.vtpos,'long'))
        
        node.set('pos', self.convert_to_str(self.pos,'long'))
        node.set('type', self.convert_to_str(self.type,'str'))
        
        node.set('val', self.convert_to_str(self.val, 'str'))
        node.set('minVal', self.convert_to_str(self.minVal,'str'))
        node.set('maxVal', self.convert_to_str(self.maxVal,'str'))
        node.set('stepSize', self.convert_to_str(self.stepSize,'str'))
        node.set('valueList',self.convert_to_str(self.strvaluelist,'str'))
        node.set('parent', self.convert_to_str(self.parent,'str'))
        node.set('seq', self.convert_to_str(self.seq,'bool'))
        node.set('widget',self.convert_to_str(self.widget,'str'))
        return node

    @staticmethod
    def fromXml(node):
        if node.tag != 'component':
            return None

        #read attributes
        data = node.get('id', None)
        id = Component.convert_from_str(data, 'long')
        data = node.get('vttype', None)
        vttype = Component.convert_from_str(data, 'str')
        data = node.get('vtid', None)
        vtid = Component.convert_from_str(data, 'long')
        data = node.get('vtparent_type', None)
        vtparent_type = Component.convert_from_str(data, 'str')
        data = node.get('vtparent_id', None)
        vtparent_id = Component.convert_from_str(data, 'long')
        data = node.get('vtmid', None)
        vtmid = Component.convert_from_str(data, 'long')
        data = node.get('vtpos', None)
        vtpos = Component.convert_from_str(data, 'long')
        data = node.get('pos', None)
        pos = Component.convert_from_str(data, 'long')
        data = node.get('type', None)
        type = Component.convert_from_str(data, 'str')
        data = node.get('val', None)
        val = Component.convert_from_str(data, 'str')
        val = val.replace("&lt;", "<")
        val = val.replace("&gt;", ">")
        val = val.replace("&amp;","&")
        data = node.get('minVal', None)
        minVal = Component.convert_from_str(data, 'str')
        data = node.get('maxVal', None)
        maxVal = Component.convert_from_str(data, 'str')
        data = node.get('stepSize', None)
        stepSize = Component.convert_from_str(data, 'str')
        data = node.get('valueList', None)
        values = Component.convert_from_str(data, 'str')
        values = values.replace("&lt;", "<")
        values = values.replace("&gt;", ">")
        values = values.replace("&amp;","&")
        data = node.get('parent', None)
        parent = Component.convert_from_str(data, 'str')
        data = node.get('seq', None)
        seq = Component.convert_from_str(data, 'bool')
        data = node.get('widget', None)
        widget = Component.convert_from_str(data, 'str')
       
        component = Component(id=id, vttype=vttype, param_id=vtid, 
                              parent_vttype=vtparent_type, 
                              parent_id=vtparent_id, mid=vtmid, type=type,
                              value=val, p_pos=vtpos, pos=pos,
                              minVal=minVal,
                              maxVal=maxVal,
                              stepSize=stepSize,
                              strvaluelist=values,
                              parent=parent,
                              seq=seq,
                              widget=widget)
        return component

################################################################################