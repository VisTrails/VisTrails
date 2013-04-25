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
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()
from cdat_domain import CDATAction, CDATModule, CDATOption, CDATPort

class XMLNode:
    def __init__(self):
        pass

    def has_attribute(self, node, attr):
        return node.hasAttribute(attr)

    def get_attribute(self, node, attr):
        try:
            attribute = node.attributes.get(attr)
            if attribute is not None:
                return attribute.value
        except KeyError:
            pass
        return None

    @staticmethod
    def convert_from_str(value, type):
        def bool_conv(x):
            s = str(x).upper()
            if s == 'TRUE':
                return True
            if s == 'FALSE':
                return False

        if value is not None:
            if type == 'str':
                return str(value)
            elif value.strip() != '':
                if type == 'long':
                    return long(value)
                elif type == 'float':
                   return float(value)
                elif type == 'int':
                    return int(value)
                elif type == 'bool':
                    return bool_conv(value)
                elif type == 'date':
                    return date(*strptime(value, '%Y-%m-%d')[0:3])
                elif type == 'datetime':
                    return datetime(*strptime(value, '%Y-%m-%d %H:%M:%S')[0:6])
        return None

class CDATOptionNode(XMLNode):
    @staticmethod
    def from_xml(node):
        tag = node.tag
        data = node.get('default', None)
        default = CDATOptionNode.convert_from_str(data, 'str')
        data = node.get('doc', None)
        doc = CDATOptionNode.convert_from_str(data, 'str')
        data = node.get('instance', None)
        instance = CDATOptionNode.convert_from_str(data, 'str')
        return CDATOption(tag=tag, default=default,doc=doc,instance=instance)

class CDATPortNode(XMLNode):
    """Represents Input or Output nodes"""
    @staticmethod
    def from_xml(node):
        tag = node.tag
        data = node.get('doc', None)
        doc = CDATPortNode.convert_from_str(data, 'str')
        data = node.get('instance', None)
        instance = CDATPortNode.convert_from_str(data, 'str')
        data = node.get('position', None)
        position = CDATPortNode.convert_from_str(data, 'int')
        data = node.get('required', None)
        required = CDATPortNode.convert_from_str(data, 'bool')
        return CDATPort(tag=tag, doc=doc, instance=instance,
                        position=position, required=required)

class CDATActionNode(XMLNode):
    @staticmethod
    def from_xml(node):
        data = node.get('name', None)
        name = CDATActionNode.convert_from_str(data,'str')
        data = node.get('type', None)
        type = CDATActionNode.convert_from_str(data,'str')

        options = []
        inputs = []
        outputs = []

        #read children
        for child in node.getchildren():
            if child.tag == 'options':
                for optnode in child.getchildren():
                    option = CDATOptionNode.from_xml(optnode)
                    options.append(option)
            elif child.tag == 'input':
                for inode in child.getchildren():
                    port = CDATPortNode.from_xml(inode)
                    inputs.insert(port._position,port)
            elif child.tag == 'output':
                for onode in child.getchildren():
                    port = CDATPortNode.from_xml(onode)
                    outputs.insert(port._position,port)
            elif child.tag == 'doc':
                doc = child.text
        return CDATAction(name=name, type=type, options=options, inputs=inputs,
                          outputs=outputs, doc=doc)

class CDATModuleNode(XMLNode):
    @staticmethod
    def from_xml(node):
        data = node.get('author',None)
        author = CDATModuleNode.convert_from_str(data,'str')
        data = node.get('programminglanguage', None)
        language = CDATModuleNode.convert_from_str(data,'str')
        data = node.get('type', None)
        type = CDATModuleNode.convert_from_str(data, 'str')
        data = node.get('url', None)
        url = CDATModuleNode.convert_from_str(data, 'str')
        data = node.get('version', None)
        version = CDATModuleNode.convert_from_str(data, 'str')
        data = node.get('codepath', None)
        codepath = CDATModuleNode.convert_from_str(data, 'str')

        actions = []
        #read actions
        for child in node.getchildren():
            if child.tag == 'action':
                action = CDATActionNode.from_xml(child)
                actions.append(action)

        return CDATModule(author=author,
                              language=language,
                              type=type,
                              url=url,
                              codepath=codepath,
                              version=version,
                              actions=actions)

def parse_cdat_xml_file(filename):
    """ parse_cdat_xml_file(filename:str) -> CDATDiagnostic
    """
    tree = ElementTree.parse(filename)
    module = CDATModuleNode.from_xml(tree.getroot())
    return module