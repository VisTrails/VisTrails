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
        raise RuntimeError("didn't work", ref_obj.getRegularName(),
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
