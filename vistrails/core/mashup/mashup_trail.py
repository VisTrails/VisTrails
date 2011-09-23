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
from datetime import date, datetime
from time import strptime

from core.mashup import XMLObject
from core.mashup.mashup import Mashup
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

from core import debug
from db.domain import IdScope



class Action(XMLObject):
    
    def __init__(self, id, parent_id, user='', mashup=None, date=None):
        self.id = id
        self.parent_id = parent_id
        self.user = user
        self.mashup = mashup
        self._date = None
        self.date = date
        
    def _getDate(self):
        if self._date is not None:
            return self._date.strftime('%d %b %Y %H:%M:%S')
        return datetime(1900,1,1).strftime('%d %b %Y %H:%M:%S')
    def _setDate(self, date):
        if type(date) == datetime:
            self._date = date
        elif type(date) == type('') and date.strip() != '':
            newDate = datetime(*strptime(date, '%d %b %Y %H:%M:%S')[0:6])
            self._date = newDate
    date = property(_getDate, _setDate)
        
    def __copy__(self):
        return Action.doCopy(self)
    
    def doCopy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Action 
        returns a clone of itself"""
        cp = Action(id=self.id, parent_id=self.parent_id, user=self.user,
                    mashup=None,date=self._date)
        cp.mashup = self.mashup.doCopy(new_ids,id_scope,id_remap)
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId('action')
            if 'action' in id_scope.remap:
                id_remap[(id_scope.remap['action'], self.id)] = new_id
            else:
                id_remap[('action', self.id)] = new_id
            cp.id = new_id
        return cp
    
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
           writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('action')
        
        #set attributes
        node.set('id', self.convert_to_str(self.id,'long'))
        node.set('parent_id', self.convert_to_str(self.parent_id,'long'))
        node.set('user', self.convert_to_str(self.user,'str'))
        node.set('date', self.convert_to_str(self._date,'datetime'))
        mnode = ElementTree.SubElement(node, 'mashup')
        self.mashup.toXml(mnode)
        return node
    
    @staticmethod
    def fromXml(node):
        if node.tag != 'action':
            debug.debug("node.tag != 'action'")
            return None
        #read attributes
        data = node.get('id', None)
        id = Action.convert_from_str(data, 'long')
        data = node.get('parent_id', None)
        parent_id = Action.convert_from_str(data, 'long')
        data = node.get('user', None)
        user = Action.convert_from_str(data, 'str')
        data = node.get('date', None)
        date = Action.convert_from_str(data, 'datetime')
        child = node.getchildren()[0]
        if child.tag == 'mashup':
            mashup = Mashup.fromXml(child)
        return Action(id=id, parent_id=parent_id, mashup=mashup, user=user,
                      date=date)
        
    ##########################################################################
    # Operators
    
    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        
        msg = "<<type='%s' id='%s' parent_id='%s' date='%s' user='%s'>>"
        return msg % (type(self),
                      self.id,
                      self.parent_id,
                      self._date,
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

class ActionAnnotation(XMLObject):
    def __init__(self, id, action_id, key=None, value=None, user=None, date=None):
        self.id = id
        self.action_id = action_id
        self.key = key
        self.value = value
        self.user = user
        self._date = None
        self.date = date
        
    def _getDate(self):
        if self._date is not None:
            return self._date.strftime('%d %b %Y %H:%M:%S')
        return datetime(1900,1,1).strftime('%d %b %Y %H:%M:%S')
    def _setDate(self, date):
        if type(date) == datetime:
            self._date = date
        elif type(date) == type('') and date.strip() != '':
            newDate = datetime(*strptime(date, '%d %b %Y %H:%M:%S')[0:6])
            self._date = newDate
    date = property(_getDate, _setDate)
        
    def __copy__(self):
        return ActionAnnotation.doCopy(self)
    
    def doCopy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Action 
        returns a clone of itself"""
        cp = ActionAnnotation(id=self.id, action_id=self.action_id, key=self.key,
                              value=self.value, user=self.user, date=self._date)
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId('actionAnnotation')
            if 'actionAnnotation' in id_scope.remap:
                id_remap[(id_scope.remap['actionAnnotation'], self.id)] = new_id
            else:
                id_remap[('actionAnnotation', self.id)] = new_id
            cp.id = new_id
        return cp
    
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
           writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('actionAnnotation')
        
        #set attributes
        node.set('id', self.convert_to_str(self.id,'long'))
        node.set('action_id', self.convert_to_str(self.action_id,'long'))
        node.set('user', self.convert_to_str(self.user,'str'))
        node.set('key', self.convert_to_str(self.key,'str'))
        node.set('value', self.convert_to_str(self.value,'str'))
        node.set('date', self.convert_to_str(self._date,'datetime'))
        return node
    
    @staticmethod
    def fromXml(node):
        if node.tag != 'actionAnnotation':
            debug.debug("node.tag != 'actionAnnotation'")
            return None
        #read attributes
        data = node.get('id', None)
        id = Action.convert_from_str(data, 'long')
        data = node.get('action_id', None)
        action_id = Action.convert_from_str(data, 'long')
        data = node.get('key', None)
        key = Action.convert_from_str(data, 'str')
        data = node.get('value', None)
        value = Action.convert_from_str(data, 'str')
        data = node.get('user', None)
        user = Action.convert_from_str(data, 'str')
        data = node.get('date', None)
        date = Action.convert_from_str(data, 'datetime')
        return ActionAnnotation(id=id, action_id=action_id, key=key, value=value,
                      user=user, date=date)
    
    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an
        ActionAnnotation object.

        """
        rep = ("<actionAnnotation id=%s action_id=%s key=%s value=%s "
               "date=%s user=%s</annotation>")
        return  rep % (str(self.id), str(self.action_id), str(self.key), 
                       str(self.value), str(self.date), str(self.user))

    def __eq__(self, other):
        """ __eq__(other: ActionAnnotation) -> boolean
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
    
class Mashuptrail(XMLObject):
    """ MashupTrail is a class that stores versions of Mashups.
    For now it keeps a linear history."""
    def __init__(self, id, vt_version, id_scope=IdScope(1L)):
        self.id = id
        self.actions = []
        self.actionMap = {}
        self.currentVersion = -1
        self.annotations = []
        self.id_scope = id_scope
        self.vtVersion = vt_version
        self.version = ""
        
    def addVersion(self, parent_id, mashup, user, date):
        id = self.getLatestVersion() + 1
        mashup.id_scope = self.id_scope
        mashup.id = id
        mashup.version = self.vtVersion
        action = Action(id=id, parent_id=parent_id, mashup=mashup,
                        user=user, date=date)
        self.actions.append(action)
        self.actionMap[action.id] = action
        return action.id
    
    def __copy__(self):
        return Mashuptrail.doCopy(self)
    
    def doCopy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Mashuptrail 
        returns a clone of itself"""
        cp = Mashuptrail(id=self.id, vt_version=self.vtVersion)
        
        
        cp.actions = []
        cp.actionMap = {}
        for action in self.actions:
            this_action = action.doCopy(new_ids,id_scope,id_remap)
            cp.actions.append(this_action)
            cp.actionMap[this_action.id] = this_action
        cp.annotations = []
        for annotation in self.annotations:
            cp.annotations.append(annotation.doCopy(new_ids, id_scope, id_remap))
        cp.currentVersion = self.currentVersion
        cp.version = self.version
        
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
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
           writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('mashuptrail')
        
        #set attributes
        node.set('id', self.convert_to_str(self.id, 'uuid'))
        node.set('vtVersion', self.convert_to_str(self.vtVersion,'long'))
        node.set('version', self.convert_to_str(self.version, 'str'))
        for action in self.actions:
            child_ = ElementTree.SubElement(node, 'action')
            action.toXml(child_)
        for annot in self.annotations:
            child_ = ElementTree.SubElement(node, 'actionAnnotation')
            annot.toXml(child_)
        return node
    
    @staticmethod
    def fromXml(node):
        if node.tag != 'mashuptrail':
            debug.debug("node.tag != 'mashuptrail'")
            return None
        #read attributes
        data = node.get('id', None)
        id = Mashuptrail.convert_from_str(data, 'uuid')
        data = node.get('vtVersion', None)
        vtVersion = Mashuptrail.convert_from_str(data, 'long')
        data = node.get('version', None)
        version = Mashuptrail.convert_from_str(data, 'str')
        actions = []
        action_map = {}
        annotations = []
        for child in node.getchildren():
            if child.tag == 'action':
                action = Action.fromXml(child)
                actions.append(action)
                action_map[action.id] = action
            elif child.tag == 'actionAnnotation':
                annot = ActionAnnotation.fromXml(child)
                annotations.append(annot)
                
        mtrail = Mashuptrail(id,vtVersion)
        mtrail.version = version
        mtrail.actions = actions
        mtrail.actionMap = action_map
        mtrail.annotations = annotations
        mtrail.currentVersion = mtrail.getLatestVersion()
        mtrail.updateIdScope()
        return mtrail
    
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
           
################################################################################
            
import unittest
from db.domain import IdScope
import copy

class TestAction(unittest.TestCase):
    def create_action(self, id_scope=IdScope()):
        from core.mashup.component import Component
        from core.mashup.alias import Alias
        c1 = Component(id=id_scope.getNewId('component'),
                          vttype='parameter', param_id=15L, 
                          parent_vttype='function', parent_id=3L, mid=4L,
                          type='String', value='test', p_pos=0, pos=1, 
                          strvaluelist='test1,test2', widget="text")
        a1 = Alias(id=id_scope.getNewId('alias'), name='alias1', component=c1)
        
        m = Mashup(id=id_scope.getNewId('mashup'), name='mashup1', vtid='empty.vt', 
                   version=15L, alias_list=[a1])
        action = Action(id=id_scope.getNewId('action'),
                        parent_id=0L,
                        date=datetime(2007,11,18),
                        mashup=m)
        return action
    
    def test_copy(self):
        id_scope = IdScope()
        a1 = self.create_action(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.doCopy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

    def test_serialization(self):
        a1 = self.create_action()
        node = a1.toXml()
        a2 = Action.fromXml(node)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        
    def test_str(self):
        a1 = self.create_action()
        str(a1)
        
class TestActionAnnotation(unittest.TestCase):
    def create_annotation(self, id_scope=IdScope()):

        annotation = \
            ActionAnnotation(id=id_scope.getNewId('actionAnnotation'),
                             key='akey', action_id=1L,
                             value='some value', user='test')
        return annotation

    def test_copy(self):
        id_scope = IdScope()
        a1 = self.create_annotation(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.doCopy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

    def test_serialization(self):
        a1 = self.create_annotation()
        node = a1.toXml()
        a2 = ActionAnnotation.fromXml(node)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)

    def test_str(self):
        a1 = self.create_annotation()
        str(a1)

