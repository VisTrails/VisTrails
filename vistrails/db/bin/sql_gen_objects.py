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

from auto_gen_objects import Object, Property, Choice

SQL_TYPE = 'sql'

class SQLObject(Object):
    @staticmethod
    def convert(obj):
        if SQL_TYPE in obj.layouts:
            obj.__class__ = SQLObject
            for prop in obj.properties:
                prop.__class__ = SQLProperty
            for choice in obj.choices:
                choice.__class__ = SQLChoice
                for prop in choice.properties:
                    prop.__class__ = SQLProperty
        
    def getName(self):
        try:
	    return self.layouts[SQL_TYPE]['table']
	except KeyError:
	    pass
	return Object.getName(self)

    def getSQLFields(self):
        return self.getSQLProperties() + self.getSQLChoices()

    def getSQLProperties(self):
        return [p for p in self.properties if p.hasSpec()]

    def getSQLChoices(self):
        return [c for c in self.choices if c.hasSpec()]

    def getSQLInverses(self):
        return [f for f in self.getSQLFields() if f.isInverse()]

    def getSQLInverseRefs(self):
        return [f for f in self.getSQLFields() 
                if f.isInverse() and f.isReference()]

    def getSQLColumns(self):
        return [f.getColumn() for f in self.getSQLFields()]

    def getSQLReferences(self):
        return ([p for p in self.properties 
                 if p.isReference() and not p.isInverse()] + 
                [c for c in self.choices 
                 if c.isReference() and not c.isInverse()])

    def getNormalSQLColumns(self):
        return [p for p in self.properties if not p.isInverse() and \
                    not p.isPrimaryKey() and not p.isReference() and \
                    p.hasSpec()]

    def getNormalSQLColumnsAndKey(self):
        return self.getNormalSQLColumns() + [self.getKey()]

    def getSQLConstructorPairs(self):
        return [(f.getRegularName(), f.getRegularName()) 
                for f in self.getNormalSQLColumnsAndKey()]

    def getSQLColumnsAndKey(self):
        return [p.getColumnn() for p in self.getNormalSQLColumnsAndKey()]

    def getSQLReferenceProperties(self):
        return [p for p in self.properties 
                if not p.isInverse() and p.isReference()]

    def getSQLForeignKeys(self):
        return [p for p in self.properties 
                if p.isInverse() and p.isForeignKey()]
  
    def getSQLReferencedField(self, refObj):
	if refObj is not None:
	    # find inverse
	    for refProp in refObj.properties:
		if refProp.isReference() and \
			refProp.isInverse() and \
			refProp.getReference() == self.getRegularName():
		    return (refProp, False)
	    for choice in refObj.choices:
		for refProp in self.getSQLPropertiesForChoice(choice):
		    if refProp.isReference() and \
			    refProp.getReference() == self.getRegularName():
			return (choice, True)
	return (None, False)

    def get_sql_referenced(self, ref_obj, inverse=False):
        if ref_obj is not None:
            for ref_prop in ref_obj.properties:
                if not (inverse ^ ref_prop.isInverse()) and \
                        ref_prop.isReference() and \
                        ref_prop.getReference() == self.getRegularName():
                    return (ref_prop, False)
            for choice in ref_obj.choices:
                if inverse ^ choice.isInverse():
                    continue
                for ref_prop in choice.properties:
                    if ref_prop.isReference() and \
                            ref_prop.getReference() == self.getRegularName():
                        return (choice, True)
        raise Exception("didn't work", ref_obj.getRegularName(), 
                        self.getRegularName())
	    
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
    def hasSpec(self):
        if self.properties[0].hasSpec():
            return True
        return False

    def getSpec(self):
        if self.hasSpec():
            return self.properties[0]
        return None

    def getColumn(self):
        for property in self.properties:
            if property.hasSpec():
                break
	try:
	    return property.specs[SQL_TYPE]['column']
	except KeyError:
	    pass
	return self.getName()
      
    def isGlobal(self):
        try:
            return self.properties[0].specs[SQL_TYPE]['global'] == 'true'
        except KeyError:
            pass
        return False

    def getGlobalName(self):
        try:
            return self.properties[0].specs[SQL_TYPE]['globalName']
        except KeyError:
            pass
        return ''
  
    def getSQLProperties(self):
        return [p for p in self.properties if p.hasSpec()]

def convert(objects):
    sql_objects = []
    for obj in objects:
        if SQL_TYPE in obj.layouts:
            SQLObject.convert(obj)
            sql_objects.append(obj)
    return sql_objects
