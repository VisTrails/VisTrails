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

from db.domain import DBMashuptrail
from core.mashup.action import Action
from core.mashup.action_annotation import ActionAnnotation 

from db.domain import IdScope

################################################################################
    
class Mashuptrail(DBMashuptrail):
    """ MashupTrail is a class that stores versions of Mashups.
    For now it keeps a linear history."""
    def __init__(self, id, vt_version):
        DBMashuptrail.__init__(self, id, version="", vt_version)
        self.db_actions = []
        self.currentVersion = -1
        self.db_annotations = []
        self.id_scope = IdScope(1L)
        
    id = DBMashuptrail.db_id
    actions = DBMashuptrail.db_actions
    annotations = DBMashuptrail.db_annotations
    
    def _get_actionMap(self):
        return self.db_actions_id_index
    actionMap = property(_get_actionMap)
    
    def addVersion(self, parent_id, mashup, user, date):
        id = self.getLatestVersion() + 1
        mashup.id_scope = self.id_scope
        mashup.id = id
        mashup.version = self.vtVersion
        action = Action(id=id, prevId=parent_id, mashup=mashup,
                        user=user, date=date)
        self.db_add_action(action)
        
        return action.id
    
    def __copy__(self):
        return Mashuptrail.do_copy(self)
    
    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Mashuptrail 
        returns a clone of itself"""
        cp = DBMashuptrail.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Mashuptrail        
        
        cp.currentVersion = self.currentVersion        
        cp.updateIdScope()
        return cp
    
    def getLatestVersion(self):
        try:
            max_ver = max(a.id for a in self.actions)
            return max_ver
        except:
            return 0
        
    def getMashup(self, version):
        if version in self.actionMap.keys():
            return self.actionMap[version].mashup
        else:
            return None
        
    def validateMashupsForPipeline(self, version, pipeline):
        """validateMashupsForPipeline(version:long, pipeline:Pipeline)->None
        This will make sure that the aliases present in all mashups are 
        consistent with the current pipeline. 
        
        """
        for action in self.actions:
            action.mashup.id_scope = self.id_scope
            action.mashup.validateForPipeline(pipeline)
            action.mashup.version = version
    
    ####################################################################
    ## Tag manipulation
    ##    
    def hasTagWithName(self, name):
        for a in self.annotations:
            if a.key == "__tag__":
                if a.value == name:
                    return True
        return False
        
    def hasTagForActionId(self, action_id):
        for a in self.annotations:
            if a.key == "__tag__" and a.action_id == action_id:
                return True
        return False
    
    def getTagForActionId(self, action_id):
        for a in self.annotations:
            if a.key == "__tag__" and a.action_id == action_id:
                return a.value
        return ""
    
    def changeTag(self, action_id, name, user, date):
        if self.hasTagWithName(name):
            return False
        if self.hasTagForActionId(action_id):
            self.removeTagByActionId(action_id)
        return self.addTag(action_id, name, user, date)
            
    def addTag(self, action_id, name, user, date):
        if not self.hasTagWithName(name):
            self.addActionAnnotation(action_id=action_id, key="__tag__", 
                                     value=name, user=user, date=date)
            return True
        return False
    
    def removeTagByActionId(self, action_id):
        found = None
        for a in self.annotations:
            if a.key == "__tag__" and a.action_id == action_id:
                found = a
                break
        if found:
            self.annotations.remove(found)
                   
    def getTagMap(self):
        """getTagMap() -> dict of tag:action_id"""
        tagMap = {}
        for a in self.annotations:
            if a.key == "__tag__":
                tagMap[a.value] = a.action_id
        return tagMap
    
    def addActionAnnotation(self, action_id, key, value, user, date):
        id = self.id_scope.getNewId("actionAnnotation")
        annot = ActionAnnotation(id=id, action_id=action_id, key=key,
                                 value=value, user=user, date=date)
        self.annotations.append(annot)
    
    ######################################################################
    ## Serialization and Unserialization
    ##                
#    def toXml(self, node=None):
#        """toXml(node: ElementTree.Element) -> ElementTree.Element
#           writes itself to xml
#        """
#
#        if node is None:
#            node = ElementTree.Element('mashuptrail')
#        
#        #set attributes
#        node.set('id', self.convert_to_str(self.id, 'uuid'))
#        node.set('vtVersion', self.convert_to_str(self.vtVersion,'long'))
#        node.set('version', self.convert_to_str(self.version, 'str'))
#        for action in self.actions:
#            child_ = ElementTree.SubElement(node, 'action')
#            action.toXml(child_)
#        for annot in self.annotations:
#            child_ = ElementTree.SubElement(node, 'actionAnnotation')
#            annot.toXml(child_)
#        return node
#    
#    @staticmethod
#    def fromXml(node):
#        if node.tag != 'mashuptrail':
#            debug.debug("node.tag != 'mashuptrail'")
#            return None
#        #read attributes
#        data = node.get('id', None)
#        id = Mashuptrail.convert_from_str(data, 'uuid')
#        data = node.get('vtVersion', None)
#        vtVersion = Mashuptrail.convert_from_str(data, 'long')
#        data = node.get('version', None)
#        version = Mashuptrail.convert_from_str(data, 'str')
#        actions = []
#        action_map = {}
#        annotations = []
#        for child in node.getchildren():
#            if child.tag == 'action':
#                action = Action.fromXml(child)
#                actions.append(action)
#                action_map[action.id] = action
#            elif child.tag == 'actionAnnotation':
#                annot = ActionAnnotation.fromXml(child)
#                annotations.append(annot)
#                
#        mtrail = Mashuptrail(id,vtVersion)
#        mtrail.version = version
#        mtrail.actions = actions
#        mtrail.actionMap = action_map
#        mtrail.annotations = annotations
#        mtrail.currentVersion = mtrail.getLatestVersion()
#        mtrail.updateIdScope()
#        return mtrail
    
    ######################################################################
    ## IdScope
    ##      
    def updateIdScope(self):
        for action in self.actions:
            self.id_scope.updateBeginId('action', action.id+1)
            for alias in action.mashup.alias_list:
                self.id_scope.updateBeginId('alias', alias.id+1)
                self.id_scope.updateBeginId('component', alias.component.id+1)
        for annotation in self.annotations:
            self.id_scope.updateBeginId('actionAnnotation', annotation.id+1)
        

