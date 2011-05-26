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
from core.mashup import XMLObject
from core.mashup.alias import Alias
from core.mashup.component import Component
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

class Mashup(XMLObject):
    def __init__(self, id, name, vtid=None, version=None, alias_list=None, 
                 t='vistrail', has_seq=None, layout=None, geometry=None):
        self.id = id
        self.name = name
        self.version = version
        self.alias_list = alias_list
        self.vtid = vtid
        self.type = t
        self.layout = layout
        self.geometry = geometry
        
        if has_seq == None:
            self.has_seq = False
            if type(self.alias_list) == type({}):
                for v in self.alias_list.itervalues():
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
        return cp
    
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
            print "node.tag != 'mashup'"
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
                   
    def getAliasByName(self, name):
        for alias in self.alias_list:
            if alias.name == name:
                return alias
                                          
################################################################################
