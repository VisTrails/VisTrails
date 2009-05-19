############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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

from xml.auto_gen import XMLDAOListBase
from sql.auto_gen import SQLDAOListBase
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

from db import VistrailsDBException
from db.versions.v0_8_0 import version as my_version

class DAOList(dict):
    def __init__(self):
        self['xml'] = XMLDAOListBase()
        self['sql'] = SQLDAOListBase()

    def parse_xml_file(self, filename):
        return ElementTree.parse(filename)

    def write_xml_file(self, filename, tree):
        tree.write(filename)

    def read_xml_object(self, vtType, node):
        return self['xml'][vtType].fromXML(node)

    def write_xml_object(self, obj, node=None):
        res_node = self['xml'][obj.vtType].toXML(obj, node)
        return res_node
        
    def open_from_xml(self, filename, vtType, tree=None):
        """open_from_xml(filename) -> DBVistrail"""
        if tree is None:
            tree = self.parse_xml_file(filename)
        vistrail = self.read_xml_object(vtType, tree.getroot())
        return vistrail

    def save_to_xml(self, obj, filename):
        """save_to_xml(obj, filename: str) -> None
    
        """
        root = self.write_xml_object(obj)
        root.set('version', my_version)
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 'http://www.vistrails.org/vistrail.xsd')
        tree = ElementTree.ElementTree(root)
        self.write_xml_file(filename, tree)

    def serialize(self, object):
        root = self.write_xml_object(object)
        return ElementTree.tostring(root)

    def unserialize(self, str, obj_type):
        try:
            root = ElementTree.fromstring(str)
            return self.read_xml_object(obj_type, root)
        except SyntaxError, e:
            msg = "Invalid VisTrails serialized object %s" % str
            raise VistrailsDBException(msg)
            return None
