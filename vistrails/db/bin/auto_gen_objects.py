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

def capitalizeOne(str):
    result = ''
    strs = str.split('_')
    for a_str in strs:
        result += a_str[0].upper() + a_str[1:]
    return result

class Field(object):
    def __init__(self, params):
        self.params = params

    def getName(self):
        try:
            return self.params['name']
        except KeyError:
            try:
                return self.params['object']
            except KeyError:
                pass
        return None
    
    def getPluralName(self):
        try:
            return self.params['pluralName']
        except KeyError:
            pass
        return "%ss" % Field.getName(self)

    def getIterator(self):
        if Field.getType(self) == 'hash':
            return Field.getFieldName(self) + '.itervalues()'
        return Field.getFieldName(self)

    def getPrivateIterator(self):
        if Field.getType(self) == 'hash':
            return Field.getPrivateName(self) + '.itervalues()'
        return Field.getPrivateName(self)

    def getRegularIterator(self):
        if Field.getType(self) == 'hash':
            return Field.getRegularName(self) + '.itervalues()'
        return Field.getRegularName(self)

    def getSingleName(self):
        return Field.getName(self)
       
    def getRegularName(self):
        if Field.isPlural(self):
            return Field.getPluralName(self)
        return Field.getName(self)

    def getPythonName(self):
        return 'db_' + Field.getName(self)

    def getFieldName(self):
        return 'db_' + Field.getRegularName(self)

    def getDefineAccessor(self):
        return '__get_%s' % Field.getFieldName(self)

    def getDefineMutator(self):
        return '__set_%s' % Field.getFieldName(self)

    def getAccessor(self):
        return 'db_get_%s' % Field.getRegularName(self)

    def getMutator(self):
        return 'db_set_%s' % Field.getRegularName(self)

    def getAppender(self):
        return 'db_add_%s' % Field.getSingleName(self)

    def getLookup(self):
        return 'db_get_%s' % Field.getSingleName(self)

    def getModifier(self):
        return 'db_change_%s' % Field.getSingleName(self)

    def getRemover(self):
        return 'db_delete_%s' % Field.getSingleName(self)

    def getList(self):
        return 'db_get_%s' % Field.getRegularName(self)

    def getListValues(self):
        if Field.getType(self) == 'hash':
            return Field.getPrivateName(self) + '.values()'
        return Field.getPrivateName(self)

    def getPrivateName(self):
        return '_%s' % Field.getFieldName(self)

    def getMapping(self):
        try:
            return self.params['mapping']
        except KeyError:
            pass
        return 'one-to-one'

    def getType(self):
        try:
            return self.params['type']
        except KeyError:
            pass
        return 'str'

    def getPythonType(self):
        return Field.getType(self)

    def getIndices(self):
        try:
            str = self.params['index']
            indices = str.split()
            for i, index in enumerate(indices):
                compound_idx = index.split(':')
                if len(compound_idx) > 1:
                    indices[i] = compound_idx
            return indices
        except KeyError:
            pass
        return []

    def getAllIndices(self):
        indices = []
        if self.isReference():
            if self.isPlural():
                ref_obj = self.getReferencedObject()
                key = ref_obj.getKey()
                if key is not None:
                    indices.append(key.getRegularName())
            for index in self.getIndices():
                if isinstance(index, list):
                    index_field = []
                    for piece in index:
                        ignore_del_err = False
                        if piece[0] == '!':
                            piece = piece[1:]
                            ignore_del_err = True
                        ref_field = ref_obj.getField(piece)
                        if ref_field is not None:
                            if ignore_del_err:
                                index_field.append('!' + ref_field.getRegularName())
                            else:
                                index_field.append(ref_field.getRegularName())
                    if len(index_field) > 1:
                        indices.append(index_field)
                    elif len(index_field) > 0:
                        indices.append(index_field[0])
                else:
                    ignore_del_err = False
                    if index[0] == '!':
                        index = index[1:]
                        ignore_del_err = True
                    index_field = ref_obj.getField(index)
                    if index_field is not None:
                        if ignore_del_err:
                            indices.append('!' + index_field.getRegularName())
                        else:
                            indices.append(index_field.getRegularName())
        return indices

    def isInverse(self):
        try:
            return self.params['inverse'] == 'true'
        except KeyError:
            pass
        return False
    
    def isPlural(self):
        return self.getMapping() == 'one-to-many' or \
            self.getMapping() == 'many-to-many'
 
    def shouldExpand(self):
        return self.params.get('expand','true') == 'true'

    def shouldExpandAction(self):
        return self.params.get('expandAction', 'true') == 'true'

    def hasDiscriminator(self):
        return self.params.has_key('discriminator')

    def getDiscriminator(self):
        try:
            return self.params['discriminator']
        except KeyError:
            pass
        return None

class Choice(Field):
    def __init__(self, params, properties):
        Field.__init__(self, params)
        self.properties = properties

    def __str__(self):
        return 'choice: %s\nparams:\n\t%s\nprops:\n\t%s' % \
            (self.getName(), self.params, self.properties)

    def isReference(self):
        if len(self.properties) > 0:
            return self.properties[0].isReference()
        return False

    def getReference(self):
        if len(self.properties) > 0:
            return self.properties[0].getReference()
        return None

    def getReferencedObject(self):
        if len(self.properties) > 0:
            return self.properties[0].getReferencedObject()

    def isChoice(self):
        return True

class Property(Field):
    def __init__(self, params, specs):
        Field.__init__(self, params)
        self.specs = specs
        self.referencedObject = None

    def __str__(self):
        return 'property: %s\nparams:\n\t%s\nspecs:\n\t%s' % \
            (self.getName(), self.params, self.specs)
    
    def getReference(self):
        try:
            return self.params['object']
        except KeyError:
            pass
        return ''

    def getReferencedObject(self):
        return self.referencedObject
    
    def setReferencedObject(self, obj):
        self.referencedObject = obj

    def isReference(self):
        try:
            return self.params['ref'] == 'true'
        except KeyError:
            pass
        return False

    def isPrimaryKey(self):
        try:
            return self.params['primaryKey'] == 'true'
        except KeyError:
            pass
        return False
    
    def isForeignKey(self):
        try:
            return self.params['foreignKey'] == 'true'
        except KeyError:
            pass
        return False

    def isChoice(self):
        return False

class Object(object):
    def __init__(self, params, properties, layouts, choices):
        self.params = params
        self.properties = properties
        self.layouts = layouts
        self.choices = choices

    def __str__(self):
        propStr = ''
        for property in self.properties:
            propStr += '\t%s\n' % property
        choiceStr = ''
        for choice in self.choices:
            choiceStr += '\t%s\n' % choice
        return 'params:\n\t%s\nlayouts\n\t%s\n' % \
            (self.params, self.layouts) + \
            'properites:\n%s\nchoices:\n%s\n' % \
            (propStr, choiceStr)

    def getName(self):
        try:
            return self.params['name']
        except KeyError:
            pass
        return None

    def getField(self, field_name):
        for property in self.properties:
            if Property.getName(property) == field_name:
                return property
        for choice in self.choices:
            if Choice.getName(choice) == field_name:
                return choice
        return None
            
    def getRegularName(self):
        return Object.getName(self)

    def getPythonName(self):
        return 'db_' + Object.getName(self)

    def getClassName(self):
        try:
            return self.params['className']
        except KeyError:
            pass
        return 'DB%s' % capitalizeOne(Object.getName(self))

    def getChildren(self):
        return 'db_children'

    def getKey(self):
        for property in self.properties:
            if property.isPrimaryKey():
                return property
        return None

    def getSingleProperties(self):
        return [p for p in self.properties if not p.isPlural()]

    def getPluralProperties(self):
        return [p for p in self.properties if p.isPlural and not p.isInverse()]

    def getForeignKeys(self):
        return [p for p in self.properties if p.isForeignKey()]

    def getReferences(self):
        return self.getReferenceProperties() + self.getReferenceChoices()

    def getNonInverseReferences(self):
        return [ref for ref in self.getReferences() if not ref.isInverse()]

    def getReferenceProperties(self):
        return [p for p in self.properties if p.isReference()]

    def getReferenceChoices(self):
        return [c for c in self.choices if c.isReference()]

    def getNonReferenceProperties(self):
        return [p for p in self.properties if not p.isReference()]

    def getInverseProperties(self):
        return [p for p in self.properties if p.isInverse()]

    def getNonInverseProperties(self):
        return [p for p in self.properties if not p.isInverse()]
    
    def getPythonVarNames(self):
        return [field.getRegularName() for field in self.getPythonFields()]

    def getPythonFields(self):
        return [c for c in self.choices if not c.isInverse()] + \
            [p for p in self.properties if not p.isInverse()]

    def getPythonPluralFields(self):
        return [f for f in self.getPythonFields() if f.isPlural()]
    
    def getPythonLists(self):
        return [f for f in self.getPythonPluralFields() 
                if f.getPythonType() != 'hash']

    def getPythonHashes(self):
        return [f for f in self.getPythonPluralFields() 
                if f.getPythonType() == 'hash']

    def getDiscriminatorProperty(self, dName):
        try:
            for property in self.properties:
                if property.getName() == dName:
                    return property
        except KeyError:
            pass
        return None

    def getConstructorNames(self):
        return [f.getRegularName() for f in self.getPythonFields()]

    def getCopyNames(self):
        return [(f.getRegularName(), f.getPrivateName()) 
                for f in self.getPythonFields() 
                if not f.isPlural() and not f.isReference()]
