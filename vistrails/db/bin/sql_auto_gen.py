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

from auto_gen_objects import Object, Property, Choice
from auto_gen import AutoGen
import string

SQL_TYPE = 'sql'
PYTHON_SPACES = 4
SQL_SPACES = 4

class SQLObject (Object):
    def getName(self):
        try:
	    return self.layouts[SQL_TYPE]['table']
	except KeyError:
	    pass
	return Object.getName(self)
	    
class SQLProperty (Property):
    def hasSpec(self):
	try:
	    sqlSpec = self.specs[SQL_TYPE]
	    return True
	except KeyError:
	    pass
	return False

    def getName(self):
	try:
	    return self.specs[SQL_TYPE]['name']
	except KeyError:
	    pass
	return Property.getName(self)

    def getColumn(self):
	try:
	    return self.specs[SQL_TYPE]['column']
	except KeyError:
	    pass
	return self.getName()
    
    def getType(self):
	try:
	    return self.specs[SQL_TYPE]['type']
	except KeyError:
	    pass
	return 'int'

    def getGlobalName(self):
        try:
            return self.specs[SQL_TYPE]['globalName']
        except KeyError:
            pass
        return ''

    def isText(self):
	if string.find(self.getType().upper(), 'CHAR') != -1 or \
		string.find(self.getType().upper(), 'DATE') != -1:
	    return True
	return False

    def isAutoInc(self):
        try:
            # FIXME include "and isPrimaryKey()" ?
            return self.specs[SQL_TYPE]['autoInc'] == 'true' and \
                self.isPrimaryKey()
        except KeyError:
            pass
        return False

    def isGlobal(self):
        try:
            return self.specs[SQL_TYPE]['global'] == 'true'
        except KeyError:
            pass
        return False

class SQLChoice(Choice):

    def getColumn(self):
        for property in self.properties:
            if property.hasSpec():
                break
	try:
	    return property.specs[SQL_TYPE]['column']
	except KeyError:
	    pass
	return self.getName()
        
class SQLAutoGen(AutoGen):
    def __init__(self, objects):
	AutoGen.__init__(self, objects)
	for obj in self.objects.values():
	    obj.__class__ = SQLObject
	    for property in obj.properties:
		property.__class__ = SQLProperty
            for choice in obj.choices:
                choice.__class__ = SQLChoice
                for property in choice.properties:
                    property.__class__ = SQLProperty

    def reset(self, spaces = SQL_SPACES):
	AutoGen.reset(self, spaces)

    def getSQLPropertiesForChoice(self, choice):
        properties = []
        for property in choice.properties:
            if property.hasSpec():
                properties.append(property)
        return properties

    def getNormalSQLColumns(self, object):
        columns = []
        for property in object.properties:
            if not property.isInverse() and not property.isPrimaryKey() and \
               not property.isReference() and property.hasSpec():
                columns.append(property)
        return columns

    def getNormalSQLColumnsAndKey(self, object):
        columns = self.getNormalSQLColumns(object)
	columns.append(object.getKey())
        return columns

    def getSQLColumnsAndKey(self, object):
	columns = []
	for property in self.getNormalSQLColumnsAndKey(object):
	    columns.append(property.getColumn())
	return columns

    def getSQLReferences(self, object):
	refs = []
	for property in object.properties:
	    if not property.isInverse() and property.isReference():
		refs.append(property)
	return refs

    def getSQLForeignKeys(self, object):
        keys = []
        for property in object.properties:
            if property.isInverse() and property.isForeignKey():
                keys.append(property)
        return keys
    
    def getSQLReferencedField(self, refObj, object):
	if refObj is not None:
	    # find inverse
	    for refProp in refObj.properties:
		if refProp.isReference() and \
			refProp.isInverse() and \
			refProp.getReference() == object.getRegularName():
		    return (refProp, False)
	    for choice in refObj.choices:
		for refProp in self.getSQLPropertiesForChoice(choice):
		    if refProp.isReference() and \
			    refProp.getReference() == object.getRegularName():
			return (choice, True)
	return (None, False)

    def generateSchema(self):
	self.reset(SQL_SPACES)
        self.printLine('-- generated automatically by auto_dao.py\n\n')
        for obj in self.objects.values():
            self.generateTable(obj)
        return self.getOutput()

    def generateTable(self, object):
        self.printLine('CREATE TABLE %s(\n' % object.getName())

        comma = ''
        self.indent();
        for property in object.properties:
            if property.hasSpec():
		self.write(comma)
		self.printLine('%s %s' % \
			       (property.getColumn(), property.getType()))
                if property.isAutoInc():
                    self.write(' not null auto_increment primary key')
		comma = ',\n'
        for choice in object.choices:
            if choice.isInverse():
                for property in choice.properties:
                    if property.hasSpec():
                        break
                self.write(comma)
                self.printLine('%s %s' % \
                               (property.getColumn(), property.getType()))
                comma = ',\n'
	self.unindentLine('\n);\n\n')

    def generateDeleteSchema(self):
	self.reset(SQL_SPACES)
	self.printLine('-- genereated automatically by generate.py\n\n')
        self.printLine('DROP TABLE IF EXISTS')
        comma = ''
	for obj in self.objects.values():
            self.write('%s %s' % (comma, obj.getName()))
            comma = ','
        self.write('\n')
	return self.getOutput()

    def generateDAOList(self):
	self.reset(PYTHON_SPACES)
	self.printLine('"""generated automatically by auto_dao.py"""\n\n')

	self.printLine('class SQLDAOListBase(dict):\n\n')
	self.indentLine('def __init__(self, daos=None):\n')
	self.indentLine('if daos is not None:\n')
	self.indentLine('dict.update(self, daos)\n\n')
	for obj in self.objects.values():
	    self.unindentLine('if \'%s\' not in self:\n' % \
			   obj.getRegularName())
	    self.indentLine('self[\'%s\'] = %sSQLDAOBase(self)\n' % \
			   (obj.getRegularName(), 
			    obj.getClassName()))
	return self.getOutput()

    def generateDAO(self, version):
	self.reset(SQL_SPACES)
	self.printLine('"""generated automatically by auto_dao.py"""\n\n')
	self.printLine('from sql_dao import SQLDAO\n')
	self.printLine('from db.versions.%s.domain import *\n\n' % version)
	for obj in self.objects.values():
	    self.generateDAOClass(obj)
	return self.getOutput()

    def generateDAOClass(self, object):
	self.printLine('class %sSQLDAOBase(SQLDAO):\n\n' % \
		       object.getClassName())
	self.indentLine('def __init__(self, daoList):\n')
	self.indentLine('self.daoList = daoList\n\n')
	self.unindentLine('def getDao(self, dao):\n')
	self.indentLine('return self.daoList[dao]\n\n')

	refs = self.getSQLReferences(object)
	varPairs = []
	for field in self.getPythonFields(object):
            if field.__class__ == SQLChoice or field.isReference() or \
                    field.hasSpec():
                varPairs.append('%s=%s' % (field.getRegularName(),
                                           field.getRegularName()))

	key = object.getKey()
	
	choiceRefs = []
	for choice in object.choices:
	    if not choice.isInverse() and choice.properties[0].isReference():
		choiceRefs.append(choice)

	# fromSQL
	self.unindentLine('def fromSQL(self, db, id=None, foreignKey=None, ' +
                          'globalProps=None):\n')

        self.indentLine("columns = ['%s']\n" % \
                        "', '".join(self.getSQLColumnsAndKey(object)))
        self.printLine("table = '%s'\n" % object.getName())
        self.printLine("whereMap = {}\n")
        self.printLine("orderBy = '%s'\n\n" % key.getName())

	self.printLine('if id is not None:\n')
        self.indentLine("keyStr = self.convertToDB(id, '%s', '%s')\n" % \
                            (key.getPythonType(), key.getType()))
# 	if key.isText():
# 	    keyStr = """'"' + str(id) + '"'"""
# 	else:
# 	    keyStr = 'str(id)'
        self.printLine("whereMap['%s'] = keyStr\n" % key.getColumn())
        self.unindentLine('elif foreignKey is not None:\n')
	self.indentLine('whereMap.update(foreignKey)\n')
        self.unindentLine('elif globalProps is None:\n')
        self.indentLine("print '***ERROR: need to specify id or " + 
			"foreign key info'\n")
        self.unindentLine('if globalProps is not None:\n')
        self.indentLine('whereMap.update(globalProps)\n')


        self.unindentLine('dbCommand = self.createSQLSelect(' +
                          'table, columns, whereMap, orderBy)\n')
        self.printLine('data = self.executeSQL(db, dbCommand, True)\n')

	self.printLine('list = []\n')
	self.printLine('for row in data:\n')
	self.indent()
	count = 0
	for property in self.getNormalSQLColumnsAndKey(object):
	    self.printLine("%s = self.convertFromDB(row[%d], '%s', '%s')\n" % \
			   (property.getRegularName(), count,
                            property.getPythonType(), property.getType()))
            count += 1
            if property.isGlobal():
                self.printLine('if globalProps is None:\n')
                self.indentLine('globalProps = {}\n')
                self.unindentLine("globalProps['%s'] = " % \
                                      property.getGlobalName() +
                                  "self.convertToDB(%s, '%s', '%s')\n" % \
                                      (property.getRegularName(),
                                       property.getPythonType(),
                                       property.getType()))
        
        self.printLine("keyStr = self.convertToDB(%s,'%s','%s')\n\n" % \
                           (key.getRegularName(), key.getPythonType(),
                            key.getType()))
	for property in refs:
            refObj = self.getReferencedObject(property.getReference())
	    (refField, isChoice) = self.getSQLReferencedField(refObj, object)
#             self.printLine("keyStr = self.convertToDB(%s, '%s', '%s')\n" % \
#                                (key.getRegularName(), key.getPythonType(),
#                                 key.getType()))
            if not isChoice:
# 		if key.isText():
# 		    keyStr = """'"' + str(%s) + '"'""" % key.getPythonName()
# 		else:
# 		    keyStr = 'str(%s)' % key.getPythonName()
# 		foreignKey = "{'%s': %s}" % (refField.getColumn(), 
# 					     keyStr)
                if refField.hasSpec():
                    self.printLine("foreignKey = {'%s': keyStr}\n" % \
                                       refField.getColumn())
                else:
                    self.printLine("foreignKey = None\n")
	    else:
		discProp = \
		    self.getDiscriminatorProperty(refObj,
						  refField.getDiscriminator())
# 		if key.isText():
# 		    keyStr = """'"' + str(%s) + '"'""" % key.getPythonName()
# 		else:
# 		    keyStr = 'str(%s)' % key.getPythonName()
                self.printLine("discStr = self.convertToDB('%s','%s','%s')\n" %\
                                   (object.getRegularName(), 
                                    discProp.getPythonType(), 
                                    discProp.getType()))
                self.printLine("foreignKey = {'%s' : keyStr, " % \
                                   refField.getColumn() +
                               "'%s': discStr}\n" % discProp.getColumn())
#                     (refField.getColumn(), keyStr,
#                      discProp.getColumn(), object.getPythonName())

	    self.printLine('res = self.getDao(\'%s\')' % \
			   property.getReference() +
			   ".fromSQL(db, None, foreignKey, globalProps)\n")

	    if not property.isPlural():
                self.printLine('if len(res) > 0:\n')
		self.indentLine('%s = res[0]\n' % property.getRegularName())
                self.unindentLine('else:\n')
                self.indentLine('%s = None\n' % property.getRegularName())
                self.unindent()
	    else:
		if property.getPythonType() == 'hash':
		    childObj = self.getReferencedObject(property.getReference())
		    self.printLine('%s = {}\n' % property.getRegularName())
		    self.printLine('for obj in res:\n')
		    self.indentLine('%s[obj.%s] = obj\n' % \
				    (property.getRegularName(),
				     childObj.getKey().getFieldName()))
		    self.unindent()
		else:
		    self.printLine('%s = res\n' % property.getRegularName())
            self.printLine('\n')
		    
	for choice in choiceRefs:
	    if choice.isPlural():
		if choice.getPythonType() == 'hash':
		    self.printLine('%s = {}\n' % choice.getRegularName())
		else:
		    self.printLine('%s = []\n' % choice.getRegularName())
            else:
               self.printLine('%s = None\n' % choice.getRegularName())

	    discProp = \
		self.getDiscriminatorProperty(object,
					      choice.getDiscriminator())
	    cond = 'if'
	    for property in choice.properties:
		refObj = self.getReferencedObject(property.getReference())
		(refField, isChoice) = \
		    self.getSQLReferencedField(refObj, object)
                if not choice.isPlural() and discProp is not None:
                    self.printLine('%s %s == \'%s\':\n' % \
                                       (cond, discProp.getRegularName(), 
                                        property.getRegularName()))
                    self.indent()
                else:
                    self.printLine('\n')
# 		if key.isText():
# 		    keyStr = """'"' + str(%s) + '"'""" % key.getPythonName()
# 		else:
# 		    keyStr = 'str(%s)' % key.getPythonName()

                if isChoice:
                    choiceDisc = \
                        self.getDiscriminatorProperty(refObj,
                                                      refField.getDiscriminator())
                    self.printLine("discStr = " + 
                                   "self.convertToDB('%s','%s','%s')\n" % \
                                       (object.getRegularName(), 
                                        choiceDisc.getPythonType(), 
                                        choiceDisc.getType()))
                    self.printLine("foreignKey = {'%s' : keyStr, " % \
                                       refField.getColumn() +
                                   "'%s': discStr}\n" % choiceDisc.getColumn())
                else:
                    self.printLine("foreignKey = {'%s': keyStr}\n" % \
                                       refField.getColumn())
		self.printLine('res = self.getDao(\'%s\')' % \
				property.getRegularName() +
				'.fromSQL(db, None, foreignKey, globalProps)\n')

		if not choice.isPlural():
		    self.printLine('%s = res[0]\n' % choice.getRegularName())
                    self.unindent()
		else:
		    if choice.getPythonType() == 'hash':
			self.printLine('for obj in res:\n')
			self.indentLine('%s[obj.%s] = obj\n' % \
					(choice.getRegularName(),
					 refObj.getKey().getFieldName()))
			self.unindent()
		    else:
			self.printLine('%s.extend(res)\n' % \
				       choice.getRegularName())

		cond = 'elif'
            self.printLine('\n')

        assignStr = '%s = %s(' % (object.getRegularName(),
                                  object.getClassName())
        sep = ',\n' + (' ' * (len(assignStr) + 12))
	self.printLine('%s = %s(%s)\n' % (object.getRegularName(), 
                                          object.getClassName(),
                                          sep.join(varPairs)))
        self.printLine('%s.is_dirty = False\n' % object.getRegularName())
	self.printLine('list.append(%s)\n\n' % object.getRegularName())
	self.unindentLine('return list\n\n')

	# toSQL
	self.unindentLine('def toSQL(self, db, obj, foreignKey=None, ' +
                          'globalProps=None):\n')
        self.indentLine("keyStr = self.convertToDB(obj.%s, '%s', '%s')\n" % \
                           (key.getPythonName(), key.getPythonType(),
                            key.getType()))
        self.printLine("if obj.is_dirty:\n")
        self.indentLine("columns = ['%s']\n" % key.getColumn())
        self.printLine("table = '%s'\n" % object.getName())
        self.printLine("whereMap = {}\n")
        self.printLine("columnMap = {}\n\n")

# 	if key.isText():
# 	    keyStr = """'"' + str(obj.%s) + '"'""" % key.getFieldName()
# 	else:
# 	    keyStr = 'str(obj.%s)' % key.getFieldName()
        self.printLine("whereMap['%s'] = keyStr\n" % key.getColumn())
        self.printLine('if globalProps is not None:\n')
        self.indentLine('whereMap.update(globalProps)\n')
        self.unindent()

        for property in self.getNormalSQLColumns(object):
	    self.printLine('if obj.%s is not None:\n' % \
                               property.getPythonName())
            self.indentLine("columnMap['%s'] = \\\n" % property.getColumn())
            self.indentLine("self.convertToDB(obj.%s, '%s', '%s')\n" % \
                                (property.getFieldName(),
                                 property.getPythonType(),
                                 property.getType()))
            self.unindent(2)
        self.printLine('if foreignKey is not None:\n')
	self.indentLine('columnMap.update(foreignKey)\n\n')

        self.unindentLine('dbCommand = ' +
                       'self.createSQLSelect(table, columns, whereMap)\n')
        self.printLine('data = self.executeSQL(db, dbCommand, True)\n')
        
        self.printLine('if len(data) <= 0:\n')
        if key.isAutoInc():
            self.indentLine('if obj.%s is not None:\n' % key.getPythonName())
        self.indentLine("columnMap['%s'] = keyStr\n" % key.getColumn())
        if key.isAutoInc():
            self.unindent()
        self.printLine('if globalProps is not None:\n')
        self.indentLine('columnMap.update(globalProps)\n')

        self.unindentLine('dbCommand = self.createSQLInsert(table, columnMap)\n')
        self.unindentLine('else:\n')
        self.indentLine('dbCommand = ' +
                        'self.createSQLUpdate(table, columnMap, whereMap)\n')
        self.unindentLine('lastId = self.executeSQL(db, dbCommand, False)\n')
        if key.isAutoInc():
            self.printLine('if obj.%s is None:\n' % key.getPythonName())
            self.indentLine('obj.%s = lastId\n' % key.getPythonName())
            self.printLine("keyStr = self.convertToDB(obj.%s, '%s', '%s')\n" % \
                               (key.getPythonName(), key.getPythonType(),
                                key.getType()))
            self.unindent()
        for property in self.getNormalSQLColumnsAndKey(object):
            if property.isGlobal():
                self.printLine('if globalProps is None:\n')
                self.indentLine('globalProps = {}\n')
                self.unindentLine("globalProps['%s'] = " % \
                                      property.getGlobalName() +
                                  "self.convertToDB(obj.%s, '%s', '%s')\n" % \
                                      (property.getPythonName(),
                                       property.getPythonType(),
                                       property.getType()))
        self.unindentLine('\n\n')
        
        count = 0
        for property in refs:
            refObj = self.getReferencedObject(property.getReference())
	    (refField, isChoice) = self.getSQLReferencedField(refObj, object)

            if not isChoice:
# 		if key.isText():
# 		    keyStr = """'"' + str(obj.%s) + '"'""" % key.getFieldName()
# 		else:
# 		    keyStr = 'str(obj.%s)' % key.getFieldName()
                if refField.hasSpec():
                    self.printLine("foreignKey = {'%s': keyStr}\n" % \
                                       refField.getColumn())
                else:
                    self.printLine("foreignKey = None\n")
	    else:
		discProp = \
		    self.getDiscriminatorProperty(refObj,
						  refField.getDiscriminator())
# 		if key.isText():
# 		    keyStr = """'"' + str(obj.%s) + '"'""" % key.getFieldName()
# 		else:
# 		    keyStr = 'str(obj.%s)' % key.getFieldName()
                self.printLine("discStr = self.convertToDB('%s','%s','%s')\n" %\
                                   (object.getRegularName(), 
                                    discProp.getPythonType(), 
                                    discProp.getType()))
                self.printLine("foreignKey = {'%s' : keyStr, " % \
                                   refField.getColumn() +
                               "'%s': discStr}\n" % discProp.getColumn())	
	    if property.isPlural():
		if property.getPythonType() == 'hash':
		    self.printLine('for child in obj.%s.itervalues():\n' % \
				   property.getFieldName())
		else:
		    self.printLine('for child in obj.%s:\n' % \
				   property.getFieldName())
	    else:
		self.printLine('child = obj.%s\n' % \
			       property.getFieldName())
                self.printLine('if child is not None:\n')
            self.indentLine('self.getDao(\'%s\')' % property.getReference() +
			   '.toSQL(db, child, foreignKey, globalProps)\n')
            self.unindentLine('\n')

	for choice in choiceRefs:
	    discProp = \
		self.getDiscriminatorProperty(object,
					      choice.getDiscriminator())
            if choice.isPlural():
                if choice.getPythonType() == 'hash':
                    self.printLine('for child in obj.%s.itervalues():\n'% \
				       choice.getFieldName())
                else:
                    self.printLine('for child in obj.%s:\n' % \
				       choice.getFieldName())
                self.indent()
            else:
                self.printLine('child = obj.%s\n' % \
                                   choice.getFieldName())

	    cond = 'if'
	    for property in choice.properties:
 		refObj = self.getReferencedObject(property.getReference())
 		(refField, isChoice) = \
 		    self.getSQLReferencedField(refObj, object)
#                 if not choice.isPlural() and discProp is not None:
#                     self.printLine('%s obj.%s == \'%s\':\n' % \
#                                        (cond, discProp.getFieldName(), 
#                                         property.getPythonName()))
#                     self.indent()
# 		if key.isText():
# 		    keyStr = """'"' + str(obj.%s) + '"'""" % key.getFieldName()
# 		else:
# 		    keyStr = 'str(obj.%s)' % key.getFieldName()
                self.printLine("%s child.vtType == '%s':\n" % \
                                   (cond, property.getRegularName()))
                if isChoice:
                    choiceDisc = \
                        self.getDiscriminatorProperty(refObj,
                                                      refField.getDiscriminator())
                    self.indentLine("discStr = " +
                                    "self.convertToDB('%s','%s','%s')\n" % \
                                       (object.getRegularName(), 
                                        choiceDisc.getPythonType(), 
                                        choiceDisc.getType()))
                    self.printLine("foreignKey = {'%s' : keyStr, " % \
                                       refField.getColumn() +
                                   "'%s': discStr}\n" % choiceDisc.getColumn())	
                else:
                    self.indentLine("foreignKey = {'%s' : keyStr}\n" % \
                                        refField.getColumn())
# 		foreignKey = "{'%s': %s}" % (refField.getColumn(),
# 					     keyStr)

		self.printLine('self.getDao(\'%s\')' % \
				property.getRegularName() +
				'.toSQL(db, child, foreignKey, globalProps)\n')
                self.unindent()
		cond = 'elif'
            if choice.isPlural():
                self.unindent()
            self.printLine('\n')

        self.unindent(2)
        self.printLine('\n')
