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
from core.mashup.mashup import Mashup

from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

class Action(XMLObject):
    
    def __init__(self, id, parent_id, mashup):
        self.id = id
        self.parent_id = id
        self.mashup = mashup
        
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
           writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('action')
        
        #set attributes
        node.set('id', self.convert_to_str(self.id,'long'))
        node.set('parent_id', self.convert_to_str(self.parent_id,'long'))
        mnode = ElementTree.SubElement(node, 'mashup')
        self.mashup.toXml(mnode)
        return node
    
    @staticmethod
    def fromXml(node):
        if node.tag != 'action':
            print "node.tag != 'action'"
            return None
        #read attributes
        data = node.get('id', None)
        id = Action.convert_from_str(data, 'long')
        data = node.get('parent_id', None)
        parent_id = Action.convert_from_str(data, 'long')
        
        child = node.getchildren()[0]
        if child.tag == 'mashup':
            mashup = Mashup.fromXml(child)
        return Action(id, parent_id, mashup)
    
class Mashuptrail(XMLObject):
    """ MashupTrail is a class that stores versions of Mashups.
    For now it keeps a linear history."""
    def __init__(self, id, id_scope):
        self.id = id
        self.actions = []
        self.actionMap = {}
        self.currentVersion = -1
        self.tags = {}
        self.id_scope = id_scope
        
    def addVersion(self, parent_id, mashup):
        id = self.getLatestVersion() + 1
        action = Action(id, parent_id, mashup)
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
        return node
    
    @staticmethod
    def fromXml(node):
        if node.tag != 'mashuptrail':
            print "node.tag != 'mashuptrail'"
            return None
        #read attributes
        data = node.get('id', None)
        id = Mashuptrail.convert_from_str(data, 'uuid')
        actions = []
        action_map = {}
        for child in node.getchildren():
            if child.tag == 'action':
                action = Action.fromXml(child)
                actions.append(action)
                action_map[action.id] = action
        mtrail = Mashuptrail(id)
        mtrail.actions = actions
        mtrail.actionMap = action_map
        mtrail.currentVersion = mtrail.getLatestVersion()
        return mtrail
        