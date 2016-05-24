###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

from auto_gen_objects import Object, Property, Choice

XML_TYPE = 'xml'

class XMLObject(Object):
    @staticmethod
    def convert(obj):
        if XML_TYPE in obj.layouts:
            obj.__class__ = XMLObject
            for prop in obj.properties:
                prop.__class__ = XMLProperty
            for choice in obj.choices:
                choice.__class__ = XMLChoice
                for prop in choice.properties:
                    prop.__class__ = XMLProperty

    def getName(self):
        try:
            return self.layouts[XML_TYPE]['name']
        except KeyError:
            pass
        return Object.getName(self)

    def getNodeType(self):
        try:
            return self.layouts[XML_TYPE]['nodeType']
        except KeyError:
            pass
        return 'xs:element'

    def getXMLAttributes(self):
        return [p for p in self.properties if p.hasSpec() and \
                    not p.isInferred() and p.getNodeType() == 'xs:attribute']

    def getXMLElements(self):
        return [p for p in self.properties if p.hasSpec() and \
                    not p.isInferred() and p.getNodeType() == 'xs:element']

    def getXMLChoices(self):
        return [c for c in self.choices if not c.isInverse() and \
                    any([p.hasSpec() for p in c.properties])]

    def isXMLChoice(self):
        return False

    def getXMLInferredProperties(self):
        return [p for p in self.properties if p.isInferred()]

    def getConstructorPairs(self):
        return [(f.getRegularName(), f.getRegularName()) 
                for f in self.getPythonFields() if f.hasSpec()]

class XMLProperty(Property):
    def hasSpec(self):
        return self.specs.has_key(XML_TYPE)

    def getName(self):
        try:
            return self.specs[XML_TYPE]['name']
        except KeyError:
            pass
        return Property.getName(self)

    def getNodeType(self):
        try:
            return self.specs[XML_TYPE]['nodeType']
        except KeyError:
            pass
        return 'xs:attribute'

    def getAttributeType(self):
        try:
            return self.specs[XML_TYPE]['type']
        except KeyError:
            pass
        return 'xs:string'

    def getAttributeUse(self):
        try:
            return self.specs[XML_TYPE]['use']
        except KeyError:
            pass
        return None

    def getAttributeUseText(self):
        if self.getAttributeUse() is not None:
            return ' use=%s' & self.getAttributeUse()
        return ''

    def getChoice(self):
        try:
            return self.specs[XML_TYPE]['choice']
        except KeyError:
            pass
        return None

    def isInferred(self):
        try:
            return self.specs[XML_TYPE]['inferred'] == 'true'
        except KeyError:
            pass
        return False

    def getXMLPropertyName(self):
        if self.isReference():
            refObj = self.getReferencedObject()
            return refObj.getName()
        return self.getName()

    def getMinOccurs(self):
        return '0'

    def getMaxOccurs(self):
        if self.isReference() and self.getMapping() != 'one-to-many':
            return '1'
        return 'unbounded'

class XMLChoice(Choice):
    def hasSpec(self):
        return self.properties[0].hasSpec()

    def getXMLProperties(self):
        return [p for p in self.properties if p.hasSpec()]

    def getXMLAttributes(self):
        return [p for p in self.properties if p.hasSpec() and \
                    not p.isInferred() and p.getNodeType() == 'xs:attribute']

    def getXMLElements(self):
        return [p for p in self.properties if p.hasSpec() and \
                    not p.isInferred() and p.getNodeType() == 'xs:element']

    def getXMLInferredProperties(self):
        return [p for p in self.properties if p.isInferred()]

    def isXMLChoice(self):
        return True

def convert(objects):
    xml_objects = []
    for obj in objects:
        if XML_TYPE in obj.layouts:
            XMLObject.convert(obj)
            xml_objects.append(obj)
    return xml_objects

def convert_schema_order(objects, root_type):
    ref_objects = []
    cur_objects = []
    for obj in objects:
        if obj.getName() == root_type:
            ref_objects = [obj]
            cur_objects = [obj]
            break
    if len(ref_objects) < 1:
        raise ValueError("Cannot find root %s" % root_type)
    while len(cur_objects) > 0:
        next_objects = []
        for obj in cur_objects:
            for prop in obj.getXMLElements():
                if prop.isReference() and \
                        prop.getReferencedObject() not in ref_objects and \
                        prop.getReferencedObject() not in next_objects:
                    next_objects.append(prop.getReferencedObject())
            for choice in obj.getXMLChoices():
                for prop in choice.getXMLElements():
                    if prop.isReference() and \
                            prop.getReferencedObject() not in ref_objects and \
                            prop.getReferencedObject() not in next_objects:
                        next_objects.append(prop.getReferencedObject())
        ref_objects.extend(next_objects)
        cur_objects = next_objects
    return ref_objects
