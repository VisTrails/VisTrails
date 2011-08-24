<%text>###############################################################################
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
</%text>
"""generated automatically by auto_dao.py"""

from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

from xml_dao import XMLDAO
from db.versions.${version_string}.domain import *

% for obj in objs:
class ${obj.getClassName()}XMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    ## define fromXML function
    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != '${obj.getName()}':
            return None
        % if len(obj.getXMLAttributes()) > 0:
        
        # read attributes
        % for prop in obj.getXMLAttributes():
        data = node.get('${prop.getName()}', None)
        ${prop.getRegularName()} = \
            self.convertFromStr(data, '${prop.getPythonType()}')
        % endfor
        % endif
        % if len(obj.getXMLElements()) + len(obj.getXMLChoices()) > 0:
        
        % for field in obj.getXMLElements() + obj.getXMLChoices():
        % if not field.isPlural():
        ${field.getRegularName()} = None
        % else:
        % if field.getPythonType() == 'hash':
        ${field.getRegularName()} = {}
        % else:
        ${field.getRegularName()} = []
        % endif
        % endif
        % endfor
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            <% cond = 'if' %> \\
            % for field in obj.getXMLElements() + obj.getXMLChoices():
            % if field.isChoice():
            % for prop in field.getXMLProperties():
            ${cond} child_tag == '${prop.getXMLPropertyName()}':
                % if prop.isReference():
                _data = self.getDao('${prop.getReference()}').fromXML(child)
                % else:
                _data = self.convertFromStr(child.text, \!
                                                '${prop.getPythonType()}')
                % endif
                % if field.isPlural():
                % if field.getPythonType() == 'hash':
                % if not field.isReference():
                raise Exception("Cannot generate hash for non-referenced field")
                % endif
                ${field.getRegularName()}[_data. \!
                    ${field.getReferencedObject().getKey().getFieldName()}] = \
                    _data
                % else:
                ${field.getRegularName()}.append(_data)
                % endif
                % else:
                ${field.getRegularName()} = _data
                % endif
                <% cond = 'elif' %> \\
            % endfor
            % else:
            ${cond} child_tag == '${field.getXMLPropertyName()}':
                % if field.isReference():
                _data = self.getDao('${field.getReference()}').fromXML(child)
                % else:
                _data = self.convertFromStr(child.text, \!
                                                '${field.getPythonType()}')
                % endif
                % if field.isPlural():
                % if field.getPythonType() == 'hash':
                % if not field.isReference():
                raise Exception("Cannot generate hash for non-referenced field")
                % endif
                ${field.getRegularName()}[_data. \!
                    ${field.getReferencedObject().getKey().getFieldName()}] = \
                    _data
                % else:
                ${field.getRegularName()}.append(_data)
                % endif
                % else:
                ${field.getRegularName()} = _data
                % endif
                <% cond = 'elif' %> \\
            % endif
            % endfor
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        % endif
        
        obj = ${obj.getClassName()}( \!
            ${',\n'.join(['%s=%s' % f for f in obj.getConstructorPairs()])})
        obj.is_dirty = False
        return obj
    
    def toXML(self, ${obj.getRegularName()}, node=None):
        ## if not ${obj.getRegularName()}.has_changes():
        ##     return
        if node is None:
            node = ElementTree.Element('${obj.getName()}')
        % if len(obj.getXMLAttributes()) > 0:
        
        # set attributes
        % for prop in obj.getXMLAttributes():
        node.set('${prop.getName()}', \!
                     self.convertToStr(${obj.getRegularName()}. \!
                                        ${prop.getFieldName()}, \
                                            '${prop.getPythonType()}'))
        % endfor
        % endif
        
        % if len(obj.getXMLElements()) + len(obj.getXMLChoices()) > 0:
        # set elements
        % for field in obj.getXMLElements() + obj.getXMLChoices():
        ${field.getRegularName()} = \
            ${obj.getRegularName()}.${field.getFieldName()}
        % if field.isReference():
        % if field.isPlural():
        for ${field.getSingleName()} in ${field.getRegularIterator()}:
        % else:
        if ${field.getSingleName()} is not None:
        % endif
            % if field.isChoice():
            <% cond = 'if' %> \\
            % for prop in field.getXMLProperties():
            ${cond} ${field.getSingleName()}.vtType == '${prop.getReference()}':
                % if prop.isReference():
                childNode = ElementTree.SubElement(node, \
                    '${prop.getReferencedObject().getName()}')
                self.getDao('${prop.getReference()}').toXML( \!
                    ${field.getSingleName()}, childNode)
                % else:
                childNode = ElementTree.SubElement(node, \
                                                   '${prop.getSingleName()}')
                childNode.text = self.convertToStr(${prop.getSingleName()}, \
                                                   '${prop.getPythonType()}')
                % endif
            <% cond = 'elif' %> \\
            % endfor
            % else:
            childNode = ElementTree.SubElement(node, \
                '${field.getReferencedObject().getName()}')
            self.getDao('${field.getReference()}').toXML( \!
                ${field.getSingleName()}, childNode)
            % endif
        % else:
        childNode = ElementTree.SubElement(node, '${field.getSingleName()}')
        childNode.text = self.convertToStr(${field.getSingleName()}, \
                                               '${field.getPythonType()}')
        % endif
        % endfor
        
        % endif
        return node

% endfor
"""generated automatically by auto_dao.py"""

class XMLDAOListBase(dict):

    def __init__(self, daos=None):
        if daos is not None:
            dict.update(self, daos)

        % for obj in objs:
        if '${obj.getRegularName()}' not in self:
            self['${obj.getRegularName()}'] = \
                ${obj.getClassName()}XMLDAOBase(self)
        % endfor
