#!/usr/bin/env python
############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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
""" This file describes a workflow component """

import sys
sys.path.append('../../../vistrails')
from core.utils.enum import enum
from core.system import get_elementtree_library
from xml_node import XMLNode

ElementTree = get_elementtree_library()

ComponentType = enum('ComponentType',
                     ['Parameter', 'Module', 'Abstraction', 'Unknown'],
                     'Enumeration of Component Types')

class Component(XMLNode):
    def __init__(self, id=None, oid=None, pipeline=None,
                 ctype=ComponentType.Unknown, type=None, value=None):
        """__init__(id:int, pipeline:Pipeline, ctype: ComponentType,
                    type:Module, value: Module Instance) -> Component
           Creates a component representation given a pipeline, an internal
           component id, a component id oid (in the pipeline), a component type
           ctype (Parameter, Module, Abstraction or Unknown), the type
           (a VisTrails Module) and the value to be bound.

        """
        self._id = id
        self._oid = oid
        self._pipeline = pipeline
        self._ctype = ctype
        self._type = type
        self._value = value

    def to_xml(self, node=None):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
            writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('component')

        #set attributes
        node.set('id', self.convert_to_str(self._id,'long'))
        node.set('oid', self.convert_to_str(self._oid,'long'))
        node.set('ctype', self.convert_to_str(self._ctype,'str'))
        node.set('type', self.convert_to_str(self._type, 'str'))
        node.set('value', self.convert_to_str(self._value,'str'))

        return node

    @staticmethod
    def from_xml(node):
        if node.tag != 'component':
            return None

        #read attributes
        data = node.get('id', None)
        id = Component.convert_from_str(data, 'long')
        data = node.get('oid', None)
        oid = Component.convert_from_str(data, 'long')
        data = node.get('ctype', None)
        ctype = ComponentType.from_str(Component.convert_from_str(data, 'str'))
        data = node.get('type', None)
        type_ = Component.convert_from_str(data, 'str')
        data = node.get('value', None)
        value = Component.convert_from_str(data, 'str')

        component = Component(id=id,
                              oid=oid,
                              ctype=ctype,
                              type=type_,
                              value=value)
        return component

    def __eq__(self, other):
        """ __eq__(other: Bookmark) -> boolean
        Returns True if self and other have the same attributes. Used by ==
        operator.

        """
        if self._id != other._id:
            return False
        if self._oid != other._oid:
            return False
        if self._pipeline != other._pipeline:
            return False
        if self._ctype != other._ctype:
            return False
        if self._type != other._type:
            print "diff _type"
            return False
        if self._value != other._value:
            print "diff _value"
            return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        """ __str__() -> str - Writes itself as a string """
        return """<component id= '%s' oid= '%s' ctype='%s' type='%s'
pipeline='%s' value='%s'>""" %  (self._id,
                                 self._oid,
                                 self._ctype,
                                 self._type,
                                 self._pipeline,
                                 self._value)

###############################################################################

import unittest

class TestComponentClass(unittest.TestCase):

    def test_from_to_xml(self):
        component = Component(id=-1,
                              oid=-1,
                              pipeline=None,
                              ctype=ComponentType.Parameter,
                              type='core.modules.vistrails_module.Integer',
                              value='2')
        node = component.to_xml()
        s_component = ElementTree.tostring(node)

        node2 = ElementTree.fromstring(s_component)
        component2 = Component.from_xml(node2)

        self.assertEqual(component,component2)

if __name__ == '__main__':
    unittest.main()
