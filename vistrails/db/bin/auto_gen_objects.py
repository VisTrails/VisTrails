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

def capitalizeOne(str):
    result = ''
    strs = str.split('_')
    for a_str in strs:
        result += a_str[0].upper() + a_str[1:]
    return result

class Field:
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
                if type(index) == type([]):
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

class Object:
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

