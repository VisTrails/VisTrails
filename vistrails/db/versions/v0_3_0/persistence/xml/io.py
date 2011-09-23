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

from xml.parsers.expat import ExpatError
import xml.dom.minidom

from db import VistrailsDBException
from db.versions.v0_3_0 import version as my_version
    
def parse_xml_file(filename):
    try:
        return xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        msg = 'XML parse error at line %s, col %s: %s' % \
            (e.lineno, e.offset, e.code)
        raise VistrailsDBException(msg)

def write_xml_file(filename, dom, prettyprint=True):
    output = file(filename, 'w')
    if prettyprint:
        dom.writexml(output, '','  ','\n')
    else:
        dom.writexml(output)
    output.close()

def read_xml_object(vtType, node, dao_list):
    return dao_list[vtType].fromXML(node)

def write_xml_object(obj, dom, dao_list, node=None):
    res_node = dao_list[obj.vtType].toXML(obj, dom, node)
    return res_node

def open_from_xml(filename, vtType, dao_list):
    """open_from_xml(filename) -> DBVistrail"""
    dom = parse_xml_file(filename)
    vistrail = read_xml_object(vtType, dom.documentElement, dao_list)
    dom.unlink()
    return vistrail

def save_to_xml(obj, filename, dao_list):
    dom = xml.dom.minidom.getDOMImplementation().createDocument(None, None,
                                                                None)
    root = write_xml_object(obj, dom, dao_list)
    dom.appendChild(root)
    if obj.vtType == 'vistrail':
        root.setAttribute('version', my_version)
        root.setAttribute('xmlns:xsi', 
                          'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xsi:schemaLocation', 
                          'http://www.vistrails.org/vistrail.xsd')
    write_xml_file(filename, dom)
    dom.unlink()

def serialize(object, dao_list):
    dom = xml.dom.minidom.getDOMImplementation().createDocument(None, None,
                                                                None)
    root = write_xml_object(object, dom, dao_list)
    dom.appendChild(root)
    return dom.toxml()

def unserialize(str, obj_type):
    dom = xml.dom.minidom.parseString(str)
    return read_xml_object(obj_type, dom.documentElement, dao_list)

