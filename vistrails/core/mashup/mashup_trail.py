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

from datetime import date, datetime
from time import strptime

from core.mashup import XMLObject
from core.mashup.mashup import Mashup

from core.system import get_elementtree_library
from core import debug
ElementTree = get_elementtree_library()

class Action(XMLObject):
    
    def __init__(self, id, parent_id, user=None, mashup=None, date=None):
        self.id = id
        self.parent_id = parent_id
        self.user = user
        self.mashup = mashup
        self._date = date
        
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

################################################################################

class ActionAnnotation(XMLObject):
    def __init__(self, id, action_id, key=None, value=None, user=None, date=None):
        self.id = id
        self.action_id = action_id
        self.key = key
        self.value = value
        self.user = user
        self._date = date
        
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
        return Action(id=id, action_id=action_id, key=key, value=value,
                      user=user, date=date)
        
################################################################################
    
class Mashuptrail(XMLObject):
    """ MashupTrail is a class that stores versions of Mashups.
    For now it keeps a linear history."""
    def __init__(self, id, id_scope):
        self.id = id
        self.actions = []
        self.actionMap = {}
        self.currentVersion = -1
        self.annotations = []
        self.id_scope = id_scope
        
    def addVersion(self, parent_id, mashup, user, date):
        id = self.getLatestVersion() + 1
        
        action = Action(id=id, parent_id=parent_id, mashup=mashup,
                        user=user, date=date)
        self.actions.append(action)
        self.actionMap[action.id] = action
        return action.id
    
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
        if self.hasTagForActionId(action_id):
            self.removeTagByActionId(action_id)
        self.addTag(action_id, name, user, date)
            
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
        node.set('id', self.convert_to_str(self.id, 'str'))
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
                
        mtrail = Mashuptrail(id)
        mtrail.actions = actions
        mtrail.actionMap = action_map
        mtrail.annotations = annotations
        mtrail.currentVersion = mtrail.getLatestVersion()
        return mtrail
        