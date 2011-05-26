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
from core.mashup.component import Component
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

################################################################################
class Alias(XMLObject):
    def __init__(self, id, name, component=None):
        self.id = id
        self.name = name
        self.component = component

    def __copy__(self):
        return Alias.doCopy(self)
    
    def doCopy(self, new_ids=False, id_scope=None, id_remap=None):
        """doCopy() -> Alias 
        returns a clone of itself"""
        cp = Alias(id=self.id, name=self.name)
        cp.component = self.component.doCopy(new_ids, id_scope, id_remap)
        return cp
        
    def toXml(self, node=None):
        """toXml(node: ElementTree.Element) -> ElementTree.Element
            writes itself to xml
        """
        if node is None:
            node = ElementTree.Element('alias')

        #set attributes
        node.set('id', self.convert_to_str(self.id,'long'))
        node.set('name', self.convert_to_str(self.name,'str'))
        child_ = ElementTree.SubElement(node, 'component')
        self.component.toXml(child_)

        return node

    @staticmethod
    def fromXml(node):
        if node.tag != 'alias':
            return None

        #read attributes
        data = node.get('id', None)
        id = Alias.convert_from_str(data, 'long')
        data = node.get('name', None)
        name = Alias.convert_from_str(data, 'str')
        for child in node.getchildren():
            if child.tag == "component":
                component = Component.fromXml(child)
        alias = Alias(id,name,component)
        return alias

################################################################################