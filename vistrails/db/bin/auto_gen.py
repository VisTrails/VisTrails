############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

"""Document This"""

from auto_gen_objects import Object, Property

PYTHON_SPACES = 4

class AutoGen:
    def __init__(self, objects):
	self.objects = objects
	self.reset()

    def reset(self, spaces = PYTHON_SPACES):
	self.level = 0
	self.output = ''
	self.refObjects = []
	self.numSpaces = spaces

    def indent(self, indent = 1):
	self.level += indent

    def unindent(self, indent = 1):
	self.level -= indent

    def write(self, string):
	self.output += string

    def printLine(self, string):
	spaces = ''
	for idx in range(self.level):
	    for jdx in range(self.numSpaces):
		spaces +=  ' '
	self.output += spaces + string

    def indentLine(self, string):
	self.indent();
	self.printLine(string)

    def unindentLine(self, string):
	self.unindent()
	self.printLine(string)

    def getOutput(self):
	return self.output

    def getSingleProperties(self, object):
	singleProperties = []
	for property in object.properties:
	    if not property.isPlural():
		singleProperties.append(property)
	return singleProperties

    def getPluralProperties(self, object):
	pluralProperties = []
	for property in object.properties:
	    if property.isPlural() and not property.isInverse():
		pluralProperties.append(property)
	return pluralProperties

    def getReferenceProperties(self, object):
	refProperties = []
	for property in object.properties:
	    if property.isReference():
		refProperties.append(property)
	return refProperties

    def getNonReferenceProperties(self, object):
	noRefProperties = []
	for property in object.properties:
	    if not property.isReference():
		noRefProperties.append(property)
	return noRefProperties

    def getInverseProperties(self, object):
	inverseProperties = []
	for property in object.properties:
	    if property.isInverse():
		inverseProperties.append(property)
	return inverseProperties

    def getNonInverseProperties(self, object):
	noInverseProperties = []
	for property in object.properties:
	    if not property.isInverse():
		noInverseProperties.append(property)
	return noInverseProperties
    
    def getPythonVarNames(self, object):
	varNames = []
	for field in self.getPythonFields(object):
	    varNames.append(field.getRegularName())
	return varNames

    def getPythonFields(self, object):
	fields = []
	for property in object.properties:
	    if not property.isInverse():
		fields.append(property)
	for choice in object.choices:
	    if not choice.isInverse():
		fields.append(choice)
	return fields

    def getPythonPluralFields(self, object):
        fields = []
        for field in self.getPythonFields(object):
            if field.isPlural():
                fields.append(field)
	return fields
    
    def getPythonLists(self, object):
	fields = []
	for field in self.getPythonPluralFields(object):
	    if field.getPythonType() != 'hash':
		fields.append(field)
	return fields

    def getPythonHashes(self, object):
	fields = []
	for field in self.getPythonPluralFields(object):
	    if field.getPythonType() == 'hash':
		fields.append(field)
	return fields


    def getReferencedObject(self, refName):
	try:
	    return self.objects[refName]
	except KeyError:
	    pass
	return None

    def getDiscriminatorProperty(self, object, dName):
        try:
            for property in object.properties:
                if property.getName() == dName:
                    return property
        except KeyError:
            pass
        return None

    def generatePythonCode(self):
	self.reset()
	self.printLine('"""generated automatically by auto_dao.py"""\n\n')
        self.printLine('import copy\n\n')
	for obj in self.objects.values():
	    self.generatePythonClass(obj)
	return self.getOutput()

    def generatePythonClass(self, object):
	self.printLine('class %s(object):\n\n' % object.getClassName())

        vars = self.getPythonVarNames(object)
	# create constructor
	varInit = []
	for field in self.getPythonFields(object):
	    varInit.append('%s=None' % field.getRegularName())


	self.indentLine("vtType = '%s'\n\n" % object.getRegularName())
        self.printLine('def __init__(self, %s):\n' % ', '.join(varInit))
	self.indent()

	for field in self.getPythonFields(object):
	    if field.isPlural():
                for index in field.getIndices():
                    self.printLine('self.db_%s_index = {}\n' % index)
		self.printLine('if %s is None:\n' % field.getRegularName())
		if field.getPythonType() == 'hash':
    		    self.indentLine('self.%s = {}\n' % field.getPrivateName())
		else:
		    self.indentLine('self.%s = []\n' % field.getPrivateName())
		self.unindentLine('else:\n')
		self.indentLine('self.%s = %s\n' % (field.getPrivateName(),
						    field.getRegularName()))
                if len(field.getIndices()) > 0:
                    if field.getPythonType() == 'hash':
                        self.printLine('for v in self.%s.itervalues():\n' % \
                                           field.getPrivateName())
                    else:
                        self.printLine('for v in self.%s:\n' % \
                                           field.getPrivateName())
                    self.indent()
                    for index in field.getIndices():
                        self.printLine('self.db_%s_index[v.db_%s] = v\n' % \
                                           (index, index))
                    self.unindent()
                self.unindent()
	    else:
		self.printLine('self.%s = %s\n' % (field.getPrivateName(),
						   field.getRegularName()))
        self.printLine('self.is_dirty = True\n')
	self.unindentLine('\n')

        # create copy constructor
        self.printLine('def __copy__(self):\n')
        self.indentLine('cp = %s()\n' % object.getClassName())
        for field in self.getPythonFields(object):
            if field.isPlural():
                self.printLine('if self.%s is None:\n' % field.getFieldName())
                self.indentLine('cp.%s = None\n' % field.getFieldName())
                self.unindentLine('else:\n')
                if field.getPythonType() == 'hash':
                    self.indentLine('cp.%s = dict([(k,copy.copy(v)) for (k,v) in self.%s.iteritems()])\n' % (field.getFieldName(), field.getFieldName()))
                else:
                    self.indentLine('cp.%s = [copy.copy(v) for v in self.%s]\n' % (field.getFieldName(), field.getFieldName()))

                # recreate indices
                if len(field.getIndices()) > 0:
                    if field.getPythonType() == 'hash':
                        self.printLine('for v in cp.%s.itervalues():\n' % \
                                           field.getPrivateName())
                    else:
                        self.printLine('for v in cp.%s:\n' % \
                                           field.getPrivateName())
                    self.indent()
                    for index in field.getIndices():
                        self.printLine('cp.db_%s_index[v.db_%s] = v\n' % \
                                           (index, index))
                    self.unindent()
                self.unindent()
            else:
                self.printLine('cp.%s = self.%s\n' % (field.getFieldName(),
                                                       field.getFieldName()))
            self.printLine('cp.is_dirty = self.is_dirty\n')
        self.printLine('return cp\n\n')

        # create child methods
        self.unindentLine('def %s(self, parent=(None,None), orphan=False):\n' \
                              % object.getChildren())
        refs = self.getReferenceProperties(object)
        self.indentLine('children = []\n')
        for ref in refs:
            refObj = self.getReferencedObject(ref.getReference())
            if not ref.isPlural():
                self.printLine('children.extend(self.%s.%s(' % \
                                   (ref.getFieldName(), refObj.getChildren())+ \
                                   '(self.vtType, self.db_id), orphan))\n')
                self.printLine('if orphan:\n')
                self.indentLine('self.%s = None\n' % ref.getFieldName())
                self.unindent()
            else:
                if ref.getType() == 'hash':
                    self.printLine('for child in self.%s.itervalues():\n' % \
                                       ref.getFieldName())
                else:
                    self.printLine('for child in self.%s:\n' % \
                                       ref.getFieldName())
                self.indentLine('children.extend(child.%s(' % \
                                    refObj.getChildren() + \
                                    '(self.vtType, self.db_id), orphan))\n')
                self.unindentLine('if orphan:\n')
                if ref.getType() == 'hash':
                    self.indentLine('self.%s = {}\n' % ref.getFieldName())
                else:
                    self.indentLine('self.%s = []\n' % ref.getFieldName())
                self.unindent()
        self.printLine('children.append((self, parent[0], parent[1]))\n')
        self.printLine('return children\n')
        self.unindent()

        # create methods
	for field in self.getPythonFields(object):
	    self.printLine('def %s(self):\n' % \
			      field.getDefineAccessor())
	    self.indentLine('return self.%s\n' % field.getPrivateName())
	    self.unindentLine('def %s(self, %s):\n' % \
			   (field.getDefineMutator(),
			    field.getRegularName()))
	    self.indentLine('self.%s = %s\n' % \
			    (field.getPrivateName(), 
			     field.getRegularName()))
            self.printLine('self.is_dirty = True\n')
	    self.unindentLine('%s = property(%s, %s)\n' % \
			     (field.getFieldName(),
			      field.getDefineAccessor(),
			      field.getDefineMutator()))
	    if not field.isPlural():
		self.printLine('def %s(self, %s):\n' % \
				  (field.getAppender(), field.getName()))
		self.indentLine('self.%s = %s\n' % (field.getPrivateName(),
						  field.getName()))
		self.unindentLine('def %s(self, %s):\n' % \
			       (field.getModifier(), field.getName()))
		self.indentLine('self.%s = %s\n' % (field.getPrivateName(),
						  field.getName()))
		self.unindentLine('def %s(self, %s):\n' % \
			       (field.getRemover(), field.getName()))
		self.indentLine('self.%s = None\n' % field.getPrivateName())
		self.unindent()
	    else:
		self.printLine('def %s(self):\n' % field.getList())
		if field.getPythonType() == 'hash':
		    self.indentLine('return self.%s.values()\n' % \
				    field.getPrivateName())
		else:
		    self.indentLine('return self.%s\n' % \
				    field.getPrivateName())
		self.unindent()
		
		self.printLine('def %s(self, %s):\n' % \
			       (field.getAppender(),
				field.getName()))
                self.indentLine('self.is_dirty = True\n')
		if field.getPythonType() == 'hash':
		    childObj = self.getReferencedObject(field.getReference())
		    self.printLine('self.%s[%s.%s] = %s\n' % \
				    (field.getPrivateName(),
				     field.getName(),
				     childObj.getKey().getPythonName(),
				     field.getName()))
		else:
		    self.printLine('self.%s.append(%s)\n' % \
                                     (field.getPrivateName(), field.getName()))
                for index in field.getIndices():
                    self.printLine('self.db_%s_index[%s.db_%s] = %s\n' % \
                                       (index, field.getName(),
                                        index, field.getName()))
		self.unindent()

		self.printLine('def %s(self, %s):\n' % \
			       (field.getModifier(), field.getName()))
                self.indentLine('self.is_dirty = True\n')
		if field.getPythonType() == 'hash':
		    childObj = self.getReferencedObject(field.getReference())
		    self.printLine('self.%s[%s.%s] = %s\n' % \
				    (field.getPrivateName(),
				     field.getName(),
				     childObj.getKey().getPythonName(),
				     field.getName()))
		else:
		    childObj = self.getReferencedObject(field.getReference())
		    self.printLine('found = False\n')
		    self.printLine('for i in xrange(len(self.%s)):\n' % \
				    field.getPrivateName())
		    self.indentLine('if self.%s[i].%s == %s.%s:\n' % \
				    (field.getPrivateName(),
				     childObj.getKey().getPythonName(),
				     field.getName(),
				     childObj.getKey().getPythonName()))
		    self.indentLine('self.%s[i] = %s\n' % \
				    (field.getPrivateName(),
				     field.getName()))
		    self.printLine('found = True\n')
		    self.printLine('break\n')
		    self.unindent(2)
		    self.printLine('if not found:\n')
		    self.indentLine('self.%s.append(%s)\n' % \
				    (field.getPrivateName(),
				     field.getName()))
		    self.unindent()
                for index in field.getIndices():
                    self.printLine('self.db_%s_index[%s.db_%s] = %s\n' % \
                                       (index, field.getName(),
                                        index, field.getName()))
		self.unindent()

		self.printLine('def %s(self, %s):\n' % \
			       (field.getRemover(), field.getName()))
                self.indentLine('self.is_dirty = True\n')
		if field.getPythonType() == 'hash':
		    childObj = self.getReferencedObject(field.getReference())
		    self.printLine('del self.%s[%s.%s]\n' % \
				    (field.getPrivateName(),
				     field.getName(),
				     childObj.getKey().getPythonName()))
		else:
		    childObj = self.getReferencedObject(field.getReference())
		    self.printLine('for i in xrange(len(self.%s)):\n' % \
				    field.getPrivateName())
		    self.indentLine('if self.%s[i].%s == %s.%s:\n' % \
				    (field.getPrivateName(),
				     childObj.getKey().getPythonName(),
				     field.getName(),
				     childObj.getKey().getPythonName()))
		    self.indentLine('del self.%s[i]\n' % field.getPrivateName())
		    self.printLine('break\n')
		    self.unindent(2)
                for index in field.getIndices():
                    self.printLine('del self.db_%s_index[%s.db_%s]\n' % \
                                       (index, field.getName(), index))
		self.unindent()

		self.printLine('def %s(self, key):\n' % field.getLookup())
		if field.getPythonType() == 'hash':
		    self.indentLine('if self.%s.has_key(key):\n' % \
				    field.getPrivateName())
		    self.indentLine('return self.%s[key]\n' % \
				    field.getPrivateName())
		    self.unindentLine('return None\n')
		else:
		    self.indentLine('for i in xrange(len(self.%s)):\n' % \
				    field.getPrivateName())
		    self.indentLine('if self.%s[i].%s == key:\n' % \
				    (field.getPrivateName(),
				     childObj.getKey().getPythonName()))
		    self.indentLine('return self.%s[i]\n' % \
				    field.getPrivateName())
		    self.unindent(2)
		    self.printLine('return None\n')
		self.unindent()
                for index in field.getIndices():
                    self.printLine('def db_get_%s_by_%s(self, key):\n' % \
                                       (field.getSingleName(), index))
                    self.indentLine('return self.db_%s_index[key]\n' % index)
                    self.unindent()
                                    
	    self.printLine('\n')
	 
	self.printLine('def getPrimaryKey(self):\n')
	self.indentLine('return self.%s' % \
			object.getKey().getPrivateName())
	self.unindent()
	self.unindentLine('\n\n')

