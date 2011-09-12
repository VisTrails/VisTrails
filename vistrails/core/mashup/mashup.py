###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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

from db.domain import IdScope
from core.mashup import XMLObject
from core.mashup.alias import Alias
from core.mashup.component import Component
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

class Mashup(XMLObject):
    def __init__(self, id, name, vtid=None, version=None, alias_list=None, 
                 t='vistrail', has_seq=None, layout='', geometry='', id_scope=IdScope()):
        self.id = id
        self.name = name
        self.version = version
        self.alias_list = alias_list
        self.vtid = vtid
        self.type = t
        self.layout = layout
        self.geometry = geometry
        self.id_scope = id_scope
        if has_seq == None:
            self.has_seq = False
            if type(self.alias_list) == list:
                for v in self.alias_list:
                    if v.component.seq == True:
                        self.has_seq = True
        else:
            self.has_seq = has_seq
            
    def __copy__(self):
        return Mashup.doCopy(self)
    
    def doCopy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Mashup 
        returns a clone of itself"""
        cp = Mashup(id=self.id, name=self.name, vtid=self.vtid,
                    version=self.version,t=self.type)
        cp.alias_list = []
        for alias in self.alias_list:
            cp.alias_list.append(alias.doCopy(new_ids,id_scope,id_remap))
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId('mashup')
            if 'mashup' in id_scope.remap:
                id_remap[(id_scope.remap['mashup'], self.id)] = new_id
            else:
                id_remap[('mashup', self.id)] = new_id
            cp.id = new_id
        return cp
    
    ##########################################################################
    # Serialization / Unserialization
    
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
           writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('mashup')

        #set attributes
        node.set('id', self.convert_to_str(self.id,'long'))
        node.set('version', self.convert_to_str(self.version,'long'))
        node.set('vtid', self.convert_to_str(self.vtid,'str'))
        node.set('name', self.convert_to_str(self.name,'str'))
        node.set('type', self.convert_to_str(self.type,'str'))
        node.set('has_seq', self.convert_to_str(self.has_seq,'bool'))
        for v in self.alias_list:
            child_ = ElementTree.SubElement(node, 'alias')
            v.toXml(child_)
        
        layoutnode = ElementTree.SubElement(node,'layout')
        layoutnode.text = str(self.layout)
        
        geomnode = ElementTree.SubElement(node,'geometry')
        geomnode.text = str(self.geometry)
        
        return node

    @staticmethod
    def fromXml(node):
        if node.tag != 'mashup':
            #print "node.tag != 'mashup'"
            return None
        #read attributes
        data = node.get('id', None)
        id = Mashup.convert_from_str(data, 'long')
        data = node.get('name', None)
        name = Mashup.convert_from_str(data, 'str')
        data = node.get('version', None)
        version = Mashup.convert_from_str(data, 'long')
        data = node.get('vtid', None)
        vtid = Mashup.convert_from_str(data, 'str')
        data = node.get('type', None)
        type = Mashup.convert_from_str(data, 'str')
        data = node.get('has_seq', None)
        seq = Component.convert_from_str(data, 'bool')
        alias_list = []
        layout = None
        geometry = None
        for child in node.getchildren():
            if child.tag == "alias":
                alias = Alias.fromXml(child)
                alias_list.append(alias)
            if child.tag == "layout":
                layout = str(child.text).strip(" \n\t")
            if child.tag == "geometry":
                geometry = str(child.text).strip(" \n\t")
        return Mashup(id=id, name=name, vtid=vtid, version=version, 
                               alias_list=alias_list, t=type, has_seq=seq,
                               layout=layout, geometry=geometry)
        
    def loadAliasesFromPipeline(self, pipeline, id_scope):
        """loadAliasesFromPipelines(pipeline: Pipeline) -> None 
        This will replace current aliases with the ones present in Pipeline
        
        """
        
        if pipeline:
            self.alias_list = []
            if len(pipeline.aliases) > 0:
                pos = 0
                for aname,info in pipeline.aliases.iteritems():
                    parameter = pipeline.db_get_object(info[0],info[1])
                    cid = id_scope.getNewId('component')
                    aid = id_scope.getNewId('alias')
                    component = Component(cid, parameter.vtType, 
                                          parameter.real_id, info[2], info[3],
                                          info[4], parameter.type, 
                                          parameter.strValue, parameter.pos, 
                                          pos, "")
                    alias = Alias(aid, aname, component)
                    self.alias_list.append(alias)
                    pos += 1 
                  
    def remapPipelineObjects(self, id_remap):
        for alias in self.alias_list:
            try:
                new_pid = id_remap[(alias.component.vtparent_type,
                                    alias.component.vtparent_id)]
                alias.component.vtparent_id = new_pid
                new_id = id_remap[(alias.component.vttype,alias.component.vtid)]
                alias.component.vtid = new_id
            except:
                pass
            
    def validateForPipeline(self, pipeline):
        """validateForPipeline(pipeline) -> None
        This will make sure that the parameters in the alias list are present
        in the pipeline. If they were removed, the aliases pointing to it will 
        be removed. This changes the mashup in place """
        to_remove = []
        for alias in self.alias_list:
            try:
                param = pipeline.db_get_object(alias.component.vttype,
                                               alias.component.vtid)
            except:
                to_remove.append(alias)
        for a in to_remove:
            self.alias_list.remove(a)    
        pos = 0
        mashup_aliases = []
        for a in self.alias_list:
            mashup_aliases.append(a.name)
            a.component.pos = pos
            pos+=1
            
        for a, info in pipeline.aliases.iteritems():
            if a not in mashup_aliases:
                parameter = pipeline.db_get_object(info[0],info[1])
                cid = self.id_scope.getNewId('component')
                aid = self.id_scope.getNewId('alias')
                component = Component(cid, parameter.vtType, 
                                      parameter.real_id, info[2], info[3],
                                      info[4], parameter.type, 
                                      parameter.strValue, parameter.pos, 
                                      pos, "")
                newalias = Alias(aid, a, component) 
                self.alias_list.append(newalias)
                pos +=1      
                   
    def getAliasByName(self, name):
        for alias in self.alias_list:
            if alias.name == name:
                return alias
                        
    ##########################################################################
    # Operators

    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        
        return ("(Mashup id='%s' name='%s' version='%s' vtid='%s' type='%s' \
layout='%s' geometry='%s' alias_list='%s')@%X" %
                    (self.id,
                     self.name,
                     self.version,
                     self.vtid,
                     self.type,
                     self.layout,
                     self.geometry,
                     self.alias_list,
                     id(self)))

    def __eq__(self, other):
        """ __eq__(other: Mashup) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.name != other.name:
            return False
        if self.vtid != other.vtid:
            return False
        if self.version != other.version:
            return False
        if self.type != other.type:
            return False
        if self.layout != other.layout:
            return False
        if self.geometry != other.geometry:
            return False
        if len(self.alias_list) != len(other.alias_list):
            return False
        for p,q in zip(self.alias_list, other.alias_list):
            if p != q:
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
from db.domain import IdScope
import copy

class TestMashup(unittest.TestCase):
    def create_mashup(self, id_scope=IdScope()):
        c1 = Component(id=id_scope.getNewId('component'),
                          vttype='parameter', param_id=15L, 
                          parent_vttype='function', parent_id=3L, mid=4L,
                          type='String', value='test', p_pos=0, pos=1, 
                          strvaluelist='test1,test2', widget="text")
        a1 = Alias(id=id_scope.getNewId('alias'), name='alias1', component=c1)
        
        m = Mashup(id=id_scope.getNewId('mashup'), name='mashup1', vtid='empty.vt', 
                   version=15L, alias_list=[a1])
        return m
    
    def test_copy(self):
        id_scope = IdScope()
        m1 = self.create_mashup(id_scope)
        m2 = copy.copy(m1)
        self.assertEqual(m1, m2)
        self.assertEqual(m1.id, m2.id)
        m3 = m2.doCopy(True, id_scope, {})
        self.assertEqual(m1, m3)
        self.assertNotEqual(m1.id, m3.id)
        
    def test_serialization(self):
        m1 = self.create_mashup()
        node = m1.toXml()
        m2 = Mashup.fromXml(node)
        self.assertEqual(m1, m2)
        self.assertEqual(m1.id, m2.id)
        
    def test_str(self):
        m1 = self.create_mashup()
        str(m1)
    