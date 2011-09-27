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

from sql_dao import SQLDAO
from db.versions.${version_string}.domain import *

% for obj in objs:
class ${obj.getClassName()}SQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = '${obj.getName()}'

    def getDao(self, dao):
        return self.daoList[dao]

    ## get_sql_columns
    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['${"', '".join(obj.getSQLColumns())}']
        table = '${obj.getName()}'
        whereMap = global_props
        orderBy = '${obj.getKey().getName()}'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, \
                                             lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            % for count, field in enumerate(obj.getSQLFields()):
            ${field.getRegularName()} = \
                self.convertFromDB(row[${count}], '${field.getPythonType()}', \
                                       '${field.getType()}')
            % if field.isGlobal():
            global_props['${field.getGlobalName()}'] = \
                self.convertToDB(${field.getRegularName()}, \
                                      '${field.getPythonType()}', \
                                      '${field.getType()}')
            % endif
            % endfor
            
            ${obj.getRegularName()} = ${obj.getClassName()} \!
                (${',\n'.join('%s=%s' % p 
                              for p in obj.getSQLConstructorPairs())})
            % for field in obj.getSQLInverses():
            ${obj.getRegularName()}.${field.getFieldName()} = \
                ${field.getRegularName()}
            % endfor
            ${obj.getRegularName()}.is_dirty = False
            res[('${obj.getRegularName()}', \
                 ${obj.getKey().getRegularName()})] = ${obj.getRegularName()}
        return res

    ## get_sql_select
    def get_sql_select(self, db, global_props,lock=False):
        columns = ['${"', '".join(obj.getSQLColumns())}']
        table = '${obj.getName()}'
        whereMap = global_props
        orderBy = '${obj.getKey().getName()}'
        return self.createSQLSelect(table, columns, whereMap, orderBy, \
                                             lock)

    ## process_sql_columns
    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            % for count, field in enumerate(obj.getSQLFields()):
            ${field.getRegularName()} = \
                self.convertFromDB(row[${count}], '${field.getPythonType()}', \
                                       '${field.getType()}')
            % if field.isGlobal():
            global_props['${field.getGlobalName()}'] = \
                self.convertToDB(${field.getRegularName()}, \
                                      '${field.getPythonType()}', \
                                      '${field.getType()}')
            % endif
            % endfor
            
            ${obj.getRegularName()} = ${obj.getClassName()} \!
                (${',\n'.join('%s=%s' % p 
                              for p in obj.getSQLConstructorPairs())})
            % for field in obj.getSQLInverses():
            ${obj.getRegularName()}.${field.getFieldName()} = \
                ${field.getRegularName()}
            % endfor
            ${obj.getRegularName()}.is_dirty = False
            res[('${obj.getRegularName()}', \
                 ${obj.getKey().getRegularName()})] = ${obj.getRegularName()}
        return res

    ## from_sql_fast
    def from_sql_fast(self, obj, all_objects):
        % if len(obj.getSQLInverseRefs()) < 1:
        pass
        % endif
        % for backRef in obj.getSQLInverseRefs():
        <% cond = "if" %> \\
        % if backRef.isChoice():
        % for prop in backRef.properties:
        ${cond} obj.${obj.getDiscriminatorProperty( \!
                backRef.getDiscriminator()).getFieldName()} == \
                '${prop.getReferencedObject().getRegularName()}':
            p = all_objects[('${prop.getReferencedObject().getRegularName()}', \
                                 obj.${backRef.getFieldName()})]
            p.${obj.get_sql_referenced(prop.getReferencedObject())[0] \!
                .getAppender()}(obj)
        <% cond = "elif" %> \\
        % endfor
        % else:
        if ('${backRef.getReferencedObject().getRegularName()}', \
                obj.${backRef.getFieldName()}) in all_objects:
            p = all_objects[( \!
                    '${backRef.getReferencedObject().getRegularName()}', \
                        obj.${backRef.getFieldName()})]
            p.${obj.get_sql_referenced(backRef.getReferencedObject())[0]. \!
                getAppender()}(obj)
        % endif
        % endfor
        
    ## set_sql_columns
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['${"', '".join(obj.getSQLColumns())}']
        table = '${obj.getName()}'
        whereMap = {}
        whereMap.update(global_props)
        if obj.${obj.getKey().getFieldName()} is not None:
            keyStr = self.convertToDB(obj.${obj.getKey().getFieldName()}, \
                                          '${obj.getKey().getPythonType()}', \
                                          '${obj.getKey().getType()}')
            whereMap['${obj.getKey().getColumn()}'] = keyStr
        columnMap = {}
        % for field in obj.getSQLFields():
        if hasattr(obj, '${field.getPythonName()}') and \
                obj.${field.getPythonName()} is not None:
            columnMap['${field.getColumn()}'] = \\\
                self.convertToDB(obj.${field.getFieldName()}, \
                                     '${field.getPythonType()}', \
                                     '${field.getType()}')
        % endfor
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        % if obj.getKey().isAutoInc():
        if obj.${obj.getKey().getPythonName()} is None:
            obj.${obj.getKey().getPythonName()} = lastId
            keyStr = self.convertToDB(obj.${obj.getKey().getPythonName()}, \
                                          '${obj.getKey().getPythonType()}', \
                                          '${obj.getKey().getType()}')
        % endif
        % for prop in obj.getNormalSQLColumnsAndKey():
        % if prop.isGlobal():
        if hasattr(obj, '${prop.getPythonName()}') and \
                obj.${prop.getPythonName()} is not None:
            global_props['${prop.getGlobalName()}'] = \
                self.convertToDB(obj.${prop.getPythonName()}, \
                                 '${prop.getPythonType()}', \
                                     '${prop.getType()}')
        % endif
        % endfor
        
    ## set_sql_command
    ## returns the sql command for saving this object or none if already up to date
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['${"', '".join(obj.getSQLColumns())}']
        table = '${obj.getName()}'
        whereMap = {}
        whereMap.update(global_props)
        if obj.${obj.getKey().getFieldName()} is not None:
            keyStr = self.convertToDB(obj.${obj.getKey().getFieldName()}, \
                                          '${obj.getKey().getPythonType()}', \
                                          '${obj.getKey().getType()}')
            whereMap['${obj.getKey().getColumn()}'] = keyStr
        columnMap = {}
        % for field in obj.getSQLFields():
        if hasattr(obj, '${field.getPythonName()}') and \
                obj.${field.getPythonName()} is not None:
            columnMap['${field.getColumn()}'] = \\\
                self.convertToDB(obj.${field.getFieldName()}, \
                                     '${field.getPythonType()}', \
                                     '${field.getType()}')
        % endfor
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    ## set_sql_process
    ## takes the generated id and updates the object
    def set_sql_process(self, obj, global_props, lastId):
        % if obj.getKey().isAutoInc():
        if obj.${obj.getKey().getPythonName()} is None:
            obj.${obj.getKey().getPythonName()} = lastId
            keyStr = self.convertToDB(obj.${obj.getKey().getPythonName()}, \
                                          '${obj.getKey().getPythonType()}', \
                                          '${obj.getKey().getType()}')
        % endif
        % for prop in obj.getNormalSQLColumnsAndKey():
        % if prop.isGlobal():
        if hasattr(obj, '${prop.getPythonName()}') and \
                obj.${prop.getPythonName()} is not None:
            global_props['${prop.getGlobalName()}'] = \
                self.convertToDB(obj.${prop.getPythonName()}, \
                                 '${prop.getPythonType()}', \
                                     '${prop.getType()}')
        % endif
        % endfor
        pass

    ## to_sql_fast
    def to_sql_fast(self, obj, do_copy=True):
        % if len(obj.getSQLReferences()) < 1:
        pass
        % endif
        % for ref in obj.getSQLReferences():
        % if ref.isPlural():
        for child in obj.${ref.getIterator()}:
        % else:
        if obj.${ref.getFieldName()} is not None:
            child = obj.${ref.getFieldName()}
        % endif
            % if obj.get_sql_referenced(ref.getReferencedObject(), True)[1]:
            child.${ref.getReferencedObject().getDiscriminatorProperty( \!
                    obj.get_sql_referenced(ref.getReferencedObject(), \
                                               True)[0].getDiscriminator()). \!
                    getFieldName()} = obj.vtType
            child.${obj.get_sql_referenced(ref.getReferencedObject(), \
                                               True)[0].getFieldName()} = \
                        obj.db_id
            % else:
            child.${obj.get_sql_referenced(ref.getReferencedObject(), \
                                               True)[0].getFieldName()} = \
                        obj.db_id
            % endif
        % endfor
        
    ## delete_sql_column
    def delete_sql_column(self, db, obj, global_props):
        table = '${obj.getName()}'
        whereMap = {}
        whereMap.update(global_props)
        if obj.${obj.getKey().getFieldName()} is not None:
            keyStr = self.convertToDB(obj.${obj.getKey().getFieldName()}, \
                                          '${obj.getKey().getPythonType()}', \
                                          '${obj.getKey().getType()}')
            whereMap['${obj.getKey().getColumn()}'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

% endfor
"""generated automatically by auto_dao.py"""

class SQLDAOListBase(dict):

    def __init__(self, daos=None):
        if daos is not None:
            dict.update(self, daos)

        % for obj in objs:
        if '${obj.getRegularName()}' not in self:
            self['${obj.getRegularName()}'] = \
                ${obj.getClassName()}SQLDAOBase(self)
        % endfor
