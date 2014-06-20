###############################################################################
##
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

"""generated automatically by auto_dao.py"""

from sql_dao import SQLDAO
from vistrails.db.versions.v1_0_4.domain import *

class DBMashupAliasSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'mashup_alias'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_alias'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            parent = self.convertFromDB(row[2], 'long', 'int')
            entity_id = self.convertFromDB(row[3], 'long', 'int')
            entity_type = self.convertFromDB(row[4], 'str', 'char(16)')
            
            mashup_alias = DBMashupAlias(name=name,
                                         id=id)
            mashup_alias.db_parent = parent
            mashup_alias.db_entity_id = entity_id
            mashup_alias.db_entity_type = entity_type
            mashup_alias.is_dirty = False
            res[('mashup_alias', id)] = mashup_alias
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_alias'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            parent = self.convertFromDB(row[2], 'long', 'int')
            entity_id = self.convertFromDB(row[3], 'long', 'int')
            entity_type = self.convertFromDB(row[4], 'str', 'char(16)')
            
            mashup_alias = DBMashupAlias(name=name,
                                         id=id)
            mashup_alias.db_parent = parent
            mashup_alias.db_entity_id = entity_id
            mashup_alias.db_entity_type = entity_type
            mashup_alias.is_dirty = False
            res[('mashup_alias', id)] = mashup_alias
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('mashup', obj.db_parent) in all_objects:
            p = all_objects[('mashup', obj.db_parent)]
            p.db_add_alias(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_alias'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_alias'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_component is not None:
            child = obj.db_component
            child.db_mashup_alias = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'mashup_alias'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBGroupSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'group_tbl'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_tbl'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            cache = self.convertFromDB(row[1], 'int', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package = self.convertFromDB(row[4], 'str', 'varchar(511)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            group = DBGroup(cache=cache,
                            name=name,
                            namespace=namespace,
                            package=package,
                            version=version,
                            id=id)
            group.db_parentType = parentType
            group.db_entity_id = entity_id
            group.db_entity_type = entity_type
            group.db_parent = parent
            group.is_dirty = False
            res[('group', id)] = group
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_tbl'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            cache = self.convertFromDB(row[1], 'int', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package = self.convertFromDB(row[4], 'str', 'varchar(511)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            group = DBGroup(cache=cache,
                            name=name,
                            namespace=namespace,
                            package=package,
                            version=version,
                            id=id)
            group.db_parentType = parentType
            group.db_entity_id = entity_id
            group.db_entity_type = entity_type
            group.db_parent = parent
            group.is_dirty = False
            res[('group', id)] = group
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_module(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_cache') and obj.db_cache is not None:
            columnMap['cache'] = \
                self.convertToDB(obj.db_cache, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(511)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_cache') and obj.db_cache is not None:
            columnMap['cache'] = \
                self.convertToDB(obj.db_cache, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(511)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_workflow is not None:
            child = obj.db_workflow
            child.db_group = obj.db_id
        if obj.db_location is not None:
            child = obj.db_location
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_functions:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_controlParameters:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'group_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBAddSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'add_tbl'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'add_tbl'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            what = self.convertFromDB(row[1], 'str', 'varchar(255)')
            objectId = self.convertFromDB(row[2], 'long', 'int')
            parentObjId = self.convertFromDB(row[3], 'long', 'int')
            parentObjType = self.convertFromDB(row[4], 'str', 'char(16)')
            action = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            add = DBAdd(what=what,
                        objectId=objectId,
                        parentObjId=parentObjId,
                        parentObjType=parentObjType,
                        id=id)
            add.db_action = action
            add.db_entity_id = entity_id
            add.db_entity_type = entity_type
            add.is_dirty = False
            res[('add', id)] = add
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'add_tbl'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            what = self.convertFromDB(row[1], 'str', 'varchar(255)')
            objectId = self.convertFromDB(row[2], 'long', 'int')
            parentObjId = self.convertFromDB(row[3], 'long', 'int')
            parentObjType = self.convertFromDB(row[4], 'str', 'char(16)')
            action = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            add = DBAdd(what=what,
                        objectId=objectId,
                        parentObjId=parentObjId,
                        parentObjType=parentObjType,
                        id=id)
            add.db_action = action
            add.db_entity_id = entity_id
            add.db_entity_type = entity_type
            add.is_dirty = False
            res[('add', id)] = add
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('action', obj.db_action) in all_objects:
            p = all_objects[('action', obj.db_action)]
            p.db_add_operation(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'add_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_what') and obj.db_what is not None:
            columnMap['what'] = \
                self.convertToDB(obj.db_what, 'str', 'varchar(255)')
        if hasattr(obj, 'db_objectId') and obj.db_objectId is not None:
            columnMap['object_id'] = \
                self.convertToDB(obj.db_objectId, 'long', 'int')
        if hasattr(obj, 'db_parentObjId') and obj.db_parentObjId is not None:
            columnMap['par_obj_id'] = \
                self.convertToDB(obj.db_parentObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjType') and obj.db_parentObjType is not None:
            columnMap['par_obj_type'] = \
                self.convertToDB(obj.db_parentObjType, 'str', 'char(16)')
        if hasattr(obj, 'db_action') and obj.db_action is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'add_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_what') and obj.db_what is not None:
            columnMap['what'] = \
                self.convertToDB(obj.db_what, 'str', 'varchar(255)')
        if hasattr(obj, 'db_objectId') and obj.db_objectId is not None:
            columnMap['object_id'] = \
                self.convertToDB(obj.db_objectId, 'long', 'int')
        if hasattr(obj, 'db_parentObjId') and obj.db_parentObjId is not None:
            columnMap['par_obj_id'] = \
                self.convertToDB(obj.db_parentObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjType') and obj.db_parentObjType is not None:
            columnMap['par_obj_type'] = \
                self.convertToDB(obj.db_parentObjType, 'str', 'char(16)')
        if hasattr(obj, 'db_action') and obj.db_action is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_data is not None:
            child = obj.db_data
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'add_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBGroupExecSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'group_exec'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'group_name', 'group_type', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_exec'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            cached = self.convertFromDB(row[3], 'int', 'int')
            module_id = self.convertFromDB(row[4], 'long', 'int')
            group_name = self.convertFromDB(row[5], 'str', 'varchar(255)')
            group_type = self.convertFromDB(row[6], 'str', 'varchar(255)')
            completed = self.convertFromDB(row[7], 'int', 'int')
            error = self.convertFromDB(row[8], 'str', 'varchar(1023)')
            machine_id = self.convertFromDB(row[9], 'long', 'int')
            parentType = self.convertFromDB(row[10], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[11], 'long', 'int')
            entity_type = self.convertFromDB(row[12], 'str', 'char(16)')
            parent = self.convertFromDB(row[13], 'long', 'long')
            
            group_exec = DBGroupExec(ts_start=ts_start,
                                     ts_end=ts_end,
                                     cached=cached,
                                     module_id=module_id,
                                     group_name=group_name,
                                     group_type=group_type,
                                     completed=completed,
                                     error=error,
                                     machine_id=machine_id,
                                     id=id)
            group_exec.db_parentType = parentType
            group_exec.db_entity_id = entity_id
            group_exec.db_entity_type = entity_type
            group_exec.db_parent = parent
            group_exec.is_dirty = False
            res[('group_exec', id)] = group_exec
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'group_name', 'group_type', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_exec'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            cached = self.convertFromDB(row[3], 'int', 'int')
            module_id = self.convertFromDB(row[4], 'long', 'int')
            group_name = self.convertFromDB(row[5], 'str', 'varchar(255)')
            group_type = self.convertFromDB(row[6], 'str', 'varchar(255)')
            completed = self.convertFromDB(row[7], 'int', 'int')
            error = self.convertFromDB(row[8], 'str', 'varchar(1023)')
            machine_id = self.convertFromDB(row[9], 'long', 'int')
            parentType = self.convertFromDB(row[10], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[11], 'long', 'int')
            entity_type = self.convertFromDB(row[12], 'str', 'char(16)')
            parent = self.convertFromDB(row[13], 'long', 'long')
            
            group_exec = DBGroupExec(ts_start=ts_start,
                                     ts_end=ts_end,
                                     cached=cached,
                                     module_id=module_id,
                                     group_name=group_name,
                                     group_type=group_type,
                                     completed=completed,
                                     error=error,
                                     machine_id=machine_id,
                                     id=id)
            group_exec.db_parentType = parentType
            group_exec.db_entity_id = entity_id
            group_exec.db_entity_type = entity_type
            group_exec.db_parent = parent
            group_exec.is_dirty = False
            res[('group_exec', id)] = group_exec
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow_exec':
            p = all_objects[('workflow_exec', obj.db_parent)]
            p.db_add_item_exec(obj)
        elif obj.db_parentType == 'loop_iteration':
            p = all_objects[('loop_iteration', obj.db_parent)]
            p.db_add_item_exec(obj)
        elif obj.db_parentType == 'group_exec':
            p = all_objects[('group_exec', obj.db_parent)]
            p.db_add_item_exec(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'group_name', 'group_type', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_cached') and obj.db_cached is not None:
            columnMap['cached'] = \
                self.convertToDB(obj.db_cached, 'int', 'int')
        if hasattr(obj, 'db_module_id') and obj.db_module_id is not None:
            columnMap['module_id'] = \
                self.convertToDB(obj.db_module_id, 'long', 'int')
        if hasattr(obj, 'db_group_name') and obj.db_group_name is not None:
            columnMap['group_name'] = \
                self.convertToDB(obj.db_group_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_group_type') and obj.db_group_type is not None:
            columnMap['group_type'] = \
                self.convertToDB(obj.db_group_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_error') and obj.db_error is not None:
            columnMap['error'] = \
                self.convertToDB(obj.db_error, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_machine_id') and obj.db_machine_id is not None:
            columnMap['machine_id'] = \
                self.convertToDB(obj.db_machine_id, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'group_name', 'group_type', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'group_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_cached') and obj.db_cached is not None:
            columnMap['cached'] = \
                self.convertToDB(obj.db_cached, 'int', 'int')
        if hasattr(obj, 'db_module_id') and obj.db_module_id is not None:
            columnMap['module_id'] = \
                self.convertToDB(obj.db_module_id, 'long', 'int')
        if hasattr(obj, 'db_group_name') and obj.db_group_name is not None:
            columnMap['group_name'] = \
                self.convertToDB(obj.db_group_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_group_type') and obj.db_group_type is not None:
            columnMap['group_type'] = \
                self.convertToDB(obj.db_group_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_error') and obj.db_error is not None:
            columnMap['error'] = \
                self.convertToDB(obj.db_error, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_machine_id') and obj.db_machine_id is not None:
            columnMap['machine_id'] = \
                self.convertToDB(obj.db_machine_id, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_item_execs:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'group_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBParameterSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'parameter'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'name', 'type', 'val', 'alias', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'parameter'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            type = self.convertFromDB(row[3], 'str', 'varchar(255)')
            val = self.convertFromDB(row[4], 'str', 'mediumtext')
            alias = self.convertFromDB(row[5], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            parameter = DBParameter(pos=pos,
                                    name=name,
                                    type=type,
                                    val=val,
                                    alias=alias,
                                    id=id)
            parameter.db_parentType = parentType
            parameter.db_entity_id = entity_id
            parameter.db_entity_type = entity_type
            parameter.db_parent = parent
            parameter.is_dirty = False
            res[('parameter', id)] = parameter
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'name', 'type', 'val', 'alias', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'parameter'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            type = self.convertFromDB(row[3], 'str', 'varchar(255)')
            val = self.convertFromDB(row[4], 'str', 'mediumtext')
            alias = self.convertFromDB(row[5], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            parameter = DBParameter(pos=pos,
                                    name=name,
                                    type=type,
                                    val=val,
                                    alias=alias,
                                    id=id)
            parameter.db_parentType = parentType
            parameter.db_entity_id = entity_id
            parameter.db_entity_type = entity_type
            parameter.db_parent = parent
            parameter.is_dirty = False
            res[('parameter', id)] = parameter
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'function':
            p = all_objects[('function', obj.db_parent)]
            p.db_add_parameter(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'pos', 'name', 'type', 'val', 'alias', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_val') and obj.db_val is not None:
            columnMap['val'] = \
                self.convertToDB(obj.db_val, 'str', 'mediumtext')
        if hasattr(obj, 'db_alias') and obj.db_alias is not None:
            columnMap['alias'] = \
                self.convertToDB(obj.db_alias, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'pos', 'name', 'type', 'val', 'alias', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_val') and obj.db_val is not None:
            columnMap['val'] = \
                self.convertToDB(obj.db_val, 'str', 'mediumtext')
        if hasattr(obj, 'db_alias') and obj.db_alias is not None:
            columnMap['alias'] = \
                self.convertToDB(obj.db_alias, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBVistrailSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'vistrail'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified']
        table = 'vistrail'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_type = self.convertFromDB(row[1], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            name = self.convertFromDB(row[3], 'str', 'varchar(255)')
            last_modified = self.convertFromDB(row[4], 'datetime', 'datetime')
            
            vistrail = DBVistrail(entity_type=entity_type,
                                  version=version,
                                  name=name,
                                  last_modified=last_modified,
                                  id=id)
            vistrail.is_dirty = False
            res[('vistrail', id)] = vistrail
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified']
        table = 'vistrail'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_type = self.convertFromDB(row[1], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            name = self.convertFromDB(row[3], 'str', 'varchar(255)')
            last_modified = self.convertFromDB(row[4], 'datetime', 'datetime')
            
            vistrail = DBVistrail(entity_type=entity_type,
                                  version=version,
                                  name=name,
                                  last_modified=last_modified,
                                  id=id)
            vistrail.is_dirty = False
            res[('vistrail', id)] = vistrail
        return res

    def from_sql_fast(self, obj, all_objects):
        pass
    
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified']
        table = 'vistrail'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified']
        table = 'vistrail'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_actions:
            child.db_vistrail = obj.db_id
        for child in obj.db_tags:
            child.db_vistrail = obj.db_id
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_controlParameters:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_vistrailVariables:
            child.db_vistrail = obj.db_id
        for child in obj.db_parameter_explorations:
            child.db_vistrail = obj.db_id
        for child in obj.db_actionAnnotations:
            child.db_vistrail = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'vistrail'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBModuleSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'module'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            cache = self.convertFromDB(row[1], 'int', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package = self.convertFromDB(row[4], 'str', 'varchar(511)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            module = DBModule(cache=cache,
                              name=name,
                              namespace=namespace,
                              package=package,
                              version=version,
                              id=id)
            module.db_parentType = parentType
            module.db_entity_id = entity_id
            module.db_entity_type = entity_type
            module.db_parent = parent
            module.is_dirty = False
            res[('module', id)] = module
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            cache = self.convertFromDB(row[1], 'int', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package = self.convertFromDB(row[4], 'str', 'varchar(511)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            module = DBModule(cache=cache,
                              name=name,
                              namespace=namespace,
                              package=package,
                              version=version,
                              id=id)
            module.db_parentType = parentType
            module.db_entity_id = entity_id
            module.db_entity_type = entity_type
            module.db_parent = parent
            module.is_dirty = False
            res[('module', id)] = module
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_module(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_cache') and obj.db_cache is not None:
            columnMap['cache'] = \
                self.convertToDB(obj.db_cache, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(511)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_cache') and obj.db_cache is not None:
            columnMap['cache'] = \
                self.convertToDB(obj.db_cache, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(511)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_location is not None:
            child = obj.db_location
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_functions:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_controlParameters:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_portSpecs:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'module'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPortSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'port'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'type', 'moduleId', 'moduleName', 'name', 'signature', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            type = self.convertFromDB(row[1], 'str', 'varchar(255)')
            moduleId = self.convertFromDB(row[2], 'long', 'int')
            moduleName = self.convertFromDB(row[3], 'str', 'varchar(255)')
            name = self.convertFromDB(row[4], 'str', 'varchar(255)')
            signature = self.convertFromDB(row[5], 'str', 'varchar(4095)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            port = DBPort(type=type,
                          moduleId=moduleId,
                          moduleName=moduleName,
                          name=name,
                          signature=signature,
                          id=id)
            port.db_parentType = parentType
            port.db_entity_id = entity_id
            port.db_entity_type = entity_type
            port.db_parent = parent
            port.is_dirty = False
            res[('port', id)] = port
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'type', 'moduleId', 'moduleName', 'name', 'signature', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            type = self.convertFromDB(row[1], 'str', 'varchar(255)')
            moduleId = self.convertFromDB(row[2], 'long', 'int')
            moduleName = self.convertFromDB(row[3], 'str', 'varchar(255)')
            name = self.convertFromDB(row[4], 'str', 'varchar(255)')
            signature = self.convertFromDB(row[5], 'str', 'varchar(4095)')
            parentType = self.convertFromDB(row[6], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            parent = self.convertFromDB(row[9], 'long', 'long')
            
            port = DBPort(type=type,
                          moduleId=moduleId,
                          moduleName=moduleName,
                          name=name,
                          signature=signature,
                          id=id)
            port.db_parentType = parentType
            port.db_entity_id = entity_id
            port.db_entity_type = entity_type
            port.db_parent = parent
            port.is_dirty = False
            res[('port', id)] = port
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'connection':
            p = all_objects[('connection', obj.db_parent)]
            p.db_add_port(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'type', 'moduleId', 'moduleName', 'name', 'signature', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_moduleId') and obj.db_moduleId is not None:
            columnMap['moduleId'] = \
                self.convertToDB(obj.db_moduleId, 'long', 'int')
        if hasattr(obj, 'db_moduleName') and obj.db_moduleName is not None:
            columnMap['moduleName'] = \
                self.convertToDB(obj.db_moduleName, 'str', 'varchar(255)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_signature') and obj.db_signature is not None:
            columnMap['signature'] = \
                self.convertToDB(obj.db_signature, 'str', 'varchar(4095)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'type', 'moduleId', 'moduleName', 'name', 'signature', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_moduleId') and obj.db_moduleId is not None:
            columnMap['moduleId'] = \
                self.convertToDB(obj.db_moduleId, 'long', 'int')
        if hasattr(obj, 'db_moduleName') and obj.db_moduleName is not None:
            columnMap['moduleName'] = \
                self.convertToDB(obj.db_moduleName, 'str', 'varchar(255)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_signature') and obj.db_signature is not None:
            columnMap['signature'] = \
                self.convertToDB(obj.db_signature, 'str', 'varchar(4095)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'port'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPEFunctionSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'pe_function'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'module_id', 'port_name', 'is_alias', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_function'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            module_id = self.convertFromDB(row[1], 'long', 'int')
            port_name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            is_alias = self.convertFromDB(row[3], 'long', 'int')
            parentType = self.convertFromDB(row[4], 'str', 'char(32)')
            parameter_exploration = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            pe_function = DBPEFunction(module_id=module_id,
                                       port_name=port_name,
                                       id=id)
            pe_function.db_parentType = parentType
            pe_function.db_parameter_exploration = parameter_exploration
            pe_function.db_entity_id = entity_id
            pe_function.db_entity_type = entity_type
            pe_function.is_dirty = False
            res[('pe_function', id)] = pe_function
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'module_id', 'port_name', 'is_alias', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_function'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            module_id = self.convertFromDB(row[1], 'long', 'int')
            port_name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            is_alias = self.convertFromDB(row[3], 'long', 'int')
            parentType = self.convertFromDB(row[4], 'str', 'char(32)')
            parameter_exploration = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            pe_function = DBPEFunction(module_id=module_id,
                                       port_name=port_name,
                                       id=id)
            pe_function.db_parentType = parentType
            pe_function.db_parameter_exploration = parameter_exploration
            pe_function.db_entity_id = entity_id
            pe_function.db_entity_type = entity_type
            pe_function.is_dirty = False
            res[('pe_function', id)] = pe_function
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('parameter_exploration', obj.db_parameter_exploration) in all_objects:
            p = all_objects[('parameter_exploration', obj.db_parameter_exploration)]
            p.db_add_function(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'module_id', 'port_name', 'is_alias', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_function'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_module_id') and obj.db_module_id is not None:
            columnMap['module_id'] = \
                self.convertToDB(obj.db_module_id, 'long', 'int')
        if hasattr(obj, 'db_port_name') and obj.db_port_name is not None:
            columnMap['port_name'] = \
                self.convertToDB(obj.db_port_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_is_alias') and obj.db_is_alias is not None:
            columnMap['is_alias'] = \
                self.convertToDB(obj.db_is_alias, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_parameter_exploration') and obj.db_parameter_exploration is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parameter_exploration, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'module_id', 'port_name', 'is_alias', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_function'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_module_id') and obj.db_module_id is not None:
            columnMap['module_id'] = \
                self.convertToDB(obj.db_module_id, 'long', 'int')
        if hasattr(obj, 'db_port_name') and obj.db_port_name is not None:
            columnMap['port_name'] = \
                self.convertToDB(obj.db_port_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_is_alias') and obj.db_is_alias is not None:
            columnMap['is_alias'] = \
                self.convertToDB(obj.db_is_alias, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_parameter_exploration') and obj.db_parameter_exploration is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parameter_exploration, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_parameters:
            child.db_pe_function = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'pe_function'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBWorkflowSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'workflow'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'entity_id', 'entity_type', 'name', 'version', 'last_modified', 'vistrail_id', 'parent_id']
        table = 'workflow'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_id = self.convertFromDB(row[1], 'long', 'int')
            entity_type = self.convertFromDB(row[2], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            name = self.convertFromDB(row[3], 'str', 'varchar(255)')
            version = self.convertFromDB(row[4], 'str', 'char(16)')
            last_modified = self.convertFromDB(row[5], 'datetime', 'datetime')
            vistrail_id = self.convertFromDB(row[6], 'long', 'int')
            group = self.convertFromDB(row[7], 'long', 'int')
            
            workflow = DBWorkflow(entity_type=entity_type,
                                  name=name,
                                  version=version,
                                  last_modified=last_modified,
                                  vistrail_id=vistrail_id,
                                  id=id)
            workflow.db_entity_id = entity_id
            workflow.db_group = group
            workflow.is_dirty = False
            res[('workflow', id)] = workflow
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'entity_id', 'entity_type', 'name', 'version', 'last_modified', 'vistrail_id', 'parent_id']
        table = 'workflow'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_id = self.convertFromDB(row[1], 'long', 'int')
            entity_type = self.convertFromDB(row[2], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            name = self.convertFromDB(row[3], 'str', 'varchar(255)')
            version = self.convertFromDB(row[4], 'str', 'char(16)')
            last_modified = self.convertFromDB(row[5], 'datetime', 'datetime')
            vistrail_id = self.convertFromDB(row[6], 'long', 'int')
            group = self.convertFromDB(row[7], 'long', 'int')
            
            workflow = DBWorkflow(entity_type=entity_type,
                                  name=name,
                                  version=version,
                                  last_modified=last_modified,
                                  vistrail_id=vistrail_id,
                                  id=id)
            workflow.db_entity_id = entity_id
            workflow.db_group = group
            workflow.is_dirty = False
            res[('workflow', id)] = workflow
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('group', obj.db_group) in all_objects:
            p = all_objects[('group', obj.db_group)]
            p.db_add_workflow(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'entity_id', 'entity_type', 'name', 'version', 'last_modified', 'vistrail_id', 'parent_id']
        table = 'workflow'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        if hasattr(obj, 'db_vistrail_id') and obj.db_vistrail_id is not None:
            columnMap['vistrail_id'] = \
                self.convertToDB(obj.db_vistrail_id, 'long', 'int')
        if hasattr(obj, 'db_group') and obj.db_group is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_group, 'long', 'int')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'entity_id', 'entity_type', 'name', 'version', 'last_modified', 'vistrail_id', 'parent_id']
        table = 'workflow'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        if hasattr(obj, 'db_vistrail_id') and obj.db_vistrail_id is not None:
            columnMap['vistrail_id'] = \
                self.convertToDB(obj.db_vistrail_id, 'long', 'int')
        if hasattr(obj, 'db_group') and obj.db_group is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_group, 'long', 'int')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_connections:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_plugin_datas:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_others:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_modules:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'workflow'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBMashupActionSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'mashup_action'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'prev_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            prevId = self.convertFromDB(row[1], 'long', 'int')
            date = self.convertFromDB(row[2], 'datetime', 'datetime')
            user = self.convertFromDB(row[3], 'str', 'varchar(255)')
            mashuptrail = self.convertFromDB(row[4], 'long', 'int')
            entity_id = self.convertFromDB(row[5], 'long', 'int')
            entity_type = self.convertFromDB(row[6], 'str', 'char(16)')
            
            mashup_action = DBMashupAction(prevId=prevId,
                                           date=date,
                                           user=user,
                                           id=id)
            mashup_action.db_mashuptrail = mashuptrail
            mashup_action.db_entity_id = entity_id
            mashup_action.db_entity_type = entity_type
            mashup_action.is_dirty = False
            res[('mashup_action', id)] = mashup_action
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'prev_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            prevId = self.convertFromDB(row[1], 'long', 'int')
            date = self.convertFromDB(row[2], 'datetime', 'datetime')
            user = self.convertFromDB(row[3], 'str', 'varchar(255)')
            mashuptrail = self.convertFromDB(row[4], 'long', 'int')
            entity_id = self.convertFromDB(row[5], 'long', 'int')
            entity_type = self.convertFromDB(row[6], 'str', 'char(16)')
            
            mashup_action = DBMashupAction(prevId=prevId,
                                           date=date,
                                           user=user,
                                           id=id)
            mashup_action.db_mashuptrail = mashuptrail
            mashup_action.db_entity_id = entity_id
            mashup_action.db_entity_type = entity_type
            mashup_action.is_dirty = False
            res[('mashup_action', id)] = mashup_action
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('mashuptrail', obj.db_mashuptrail) in all_objects:
            p = all_objects[('mashuptrail', obj.db_mashuptrail)]
            p.db_add_action(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'prev_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_prevId') and obj.db_prevId is not None:
            columnMap['prev_id'] = \
                self.convertToDB(obj.db_prevId, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_mashuptrail') and obj.db_mashuptrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_mashuptrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'prev_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_prevId') and obj.db_prevId is not None:
            columnMap['prev_id'] = \
                self.convertToDB(obj.db_prevId, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_mashuptrail') and obj.db_mashuptrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_mashuptrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_mashup is not None:
            child = obj.db_mashup
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'mashup_action'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBChangeSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'change_tbl'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'what', 'old_obj_id', 'new_obj_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'change_tbl'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            what = self.convertFromDB(row[1], 'str', 'varchar(255)')
            oldObjId = self.convertFromDB(row[2], 'long', 'int')
            newObjId = self.convertFromDB(row[3], 'long', 'int')
            parentObjId = self.convertFromDB(row[4], 'long', 'int')
            parentObjType = self.convertFromDB(row[5], 'str', 'char(16)')
            action = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            change = DBChange(what=what,
                              oldObjId=oldObjId,
                              newObjId=newObjId,
                              parentObjId=parentObjId,
                              parentObjType=parentObjType,
                              id=id)
            change.db_action = action
            change.db_entity_id = entity_id
            change.db_entity_type = entity_type
            change.is_dirty = False
            res[('change', id)] = change
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'what', 'old_obj_id', 'new_obj_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'change_tbl'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            what = self.convertFromDB(row[1], 'str', 'varchar(255)')
            oldObjId = self.convertFromDB(row[2], 'long', 'int')
            newObjId = self.convertFromDB(row[3], 'long', 'int')
            parentObjId = self.convertFromDB(row[4], 'long', 'int')
            parentObjType = self.convertFromDB(row[5], 'str', 'char(16)')
            action = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            change = DBChange(what=what,
                              oldObjId=oldObjId,
                              newObjId=newObjId,
                              parentObjId=parentObjId,
                              parentObjType=parentObjType,
                              id=id)
            change.db_action = action
            change.db_entity_id = entity_id
            change.db_entity_type = entity_type
            change.is_dirty = False
            res[('change', id)] = change
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('action', obj.db_action) in all_objects:
            p = all_objects[('action', obj.db_action)]
            p.db_add_operation(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'what', 'old_obj_id', 'new_obj_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'change_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_what') and obj.db_what is not None:
            columnMap['what'] = \
                self.convertToDB(obj.db_what, 'str', 'varchar(255)')
        if hasattr(obj, 'db_oldObjId') and obj.db_oldObjId is not None:
            columnMap['old_obj_id'] = \
                self.convertToDB(obj.db_oldObjId, 'long', 'int')
        if hasattr(obj, 'db_newObjId') and obj.db_newObjId is not None:
            columnMap['new_obj_id'] = \
                self.convertToDB(obj.db_newObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjId') and obj.db_parentObjId is not None:
            columnMap['par_obj_id'] = \
                self.convertToDB(obj.db_parentObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjType') and obj.db_parentObjType is not None:
            columnMap['par_obj_type'] = \
                self.convertToDB(obj.db_parentObjType, 'str', 'char(16)')
        if hasattr(obj, 'db_action') and obj.db_action is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'what', 'old_obj_id', 'new_obj_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'change_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_what') and obj.db_what is not None:
            columnMap['what'] = \
                self.convertToDB(obj.db_what, 'str', 'varchar(255)')
        if hasattr(obj, 'db_oldObjId') and obj.db_oldObjId is not None:
            columnMap['old_obj_id'] = \
                self.convertToDB(obj.db_oldObjId, 'long', 'int')
        if hasattr(obj, 'db_newObjId') and obj.db_newObjId is not None:
            columnMap['new_obj_id'] = \
                self.convertToDB(obj.db_newObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjId') and obj.db_parentObjId is not None:
            columnMap['par_obj_id'] = \
                self.convertToDB(obj.db_parentObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjType') and obj.db_parentObjType is not None:
            columnMap['par_obj_type'] = \
                self.convertToDB(obj.db_parentObjType, 'str', 'char(16)')
        if hasattr(obj, 'db_action') and obj.db_action is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_data is not None:
            child = obj.db_data
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'change_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPackageSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'package'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'identifier', 'codepath', 'load_configuration', 'version', 'description', 'parent_id', 'entity_id', 'entity_type']
        table = 'package'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            identifier = self.convertFromDB(row[2], 'str', 'varchar(1023)')
            codepath = self.convertFromDB(row[3], 'str', 'varchar(1023)')
            load_configuration = self.convertFromDB(row[4], 'int', 'int')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            description = self.convertFromDB(row[6], 'str', 'varchar(1023)')
            registry = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            package = DBPackage(name=name,
                                identifier=identifier,
                                codepath=codepath,
                                load_configuration=load_configuration,
                                version=version,
                                description=description,
                                id=id)
            package.db_registry = registry
            package.db_entity_id = entity_id
            package.db_entity_type = entity_type
            package.is_dirty = False
            res[('package', id)] = package
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'identifier', 'codepath', 'load_configuration', 'version', 'description', 'parent_id', 'entity_id', 'entity_type']
        table = 'package'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            identifier = self.convertFromDB(row[2], 'str', 'varchar(1023)')
            codepath = self.convertFromDB(row[3], 'str', 'varchar(1023)')
            load_configuration = self.convertFromDB(row[4], 'int', 'int')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            description = self.convertFromDB(row[6], 'str', 'varchar(1023)')
            registry = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            package = DBPackage(name=name,
                                identifier=identifier,
                                codepath=codepath,
                                load_configuration=load_configuration,
                                version=version,
                                description=description,
                                id=id)
            package.db_registry = registry
            package.db_entity_id = entity_id
            package.db_entity_type = entity_type
            package.is_dirty = False
            res[('package', id)] = package
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('registry', obj.db_registry) in all_objects:
            p = all_objects[('registry', obj.db_registry)]
            p.db_add_package(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'identifier', 'codepath', 'load_configuration', 'version', 'description', 'parent_id', 'entity_id', 'entity_type']
        table = 'package'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_identifier') and obj.db_identifier is not None:
            columnMap['identifier'] = \
                self.convertToDB(obj.db_identifier, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_codepath') and obj.db_codepath is not None:
            columnMap['codepath'] = \
                self.convertToDB(obj.db_codepath, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_load_configuration') and obj.db_load_configuration is not None:
            columnMap['load_configuration'] = \
                self.convertToDB(obj.db_load_configuration, 'int', 'int')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_description') and obj.db_description is not None:
            columnMap['description'] = \
                self.convertToDB(obj.db_description, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_registry') and obj.db_registry is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_registry, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'identifier', 'codepath', 'load_configuration', 'version', 'description', 'parent_id', 'entity_id', 'entity_type']
        table = 'package'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_identifier') and obj.db_identifier is not None:
            columnMap['identifier'] = \
                self.convertToDB(obj.db_identifier, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_codepath') and obj.db_codepath is not None:
            columnMap['codepath'] = \
                self.convertToDB(obj.db_codepath, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_load_configuration') and obj.db_load_configuration is not None:
            columnMap['load_configuration'] = \
                self.convertToDB(obj.db_load_configuration, 'int', 'int')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_description') and obj.db_description is not None:
            columnMap['description'] = \
                self.convertToDB(obj.db_description, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_registry') and obj.db_registry is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_registry, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_module_descriptors:
            child.db_package = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'package'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBLoopExecSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'loop_exec'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'loop_exec'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            loop_exec = DBLoopExec(ts_start=ts_start,
                                   ts_end=ts_end,
                                   id=id)
            loop_exec.db_parentType = parentType
            loop_exec.db_entity_id = entity_id
            loop_exec.db_entity_type = entity_type
            loop_exec.db_parent = parent
            loop_exec.is_dirty = False
            res[('loop_exec', id)] = loop_exec
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'loop_exec'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            loop_exec = DBLoopExec(ts_start=ts_start,
                                   ts_end=ts_end,
                                   id=id)
            loop_exec.db_parentType = parentType
            loop_exec.db_entity_id = entity_id
            loop_exec.db_entity_type = entity_type
            loop_exec.db_parent = parent
            loop_exec.is_dirty = False
            res[('loop_exec', id)] = loop_exec
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow_exec':
            p = all_objects[('workflow_exec', obj.db_parent)]
            p.db_add_item_exec(obj)
        elif obj.db_parentType == 'group_exec':
            p = all_objects[('group_exec', obj.db_parent)]
            p.db_add_item_exec(obj)
        elif obj.db_parentType == 'module_exec':
            p = all_objects[('module_exec', obj.db_parent)]
            p.db_add_loop_exec(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'ts_start', 'ts_end', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'loop_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'ts_start', 'ts_end', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'loop_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_loop_iterations:
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'loop_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBConnectionSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'connection_tbl'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'connection_tbl'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            parentType = self.convertFromDB(row[1], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[2], 'long', 'int')
            entity_type = self.convertFromDB(row[3], 'str', 'char(16)')
            parent = self.convertFromDB(row[4], 'long', 'long')
            
            connection = DBConnection(id=id)
            connection.db_parentType = parentType
            connection.db_entity_id = entity_id
            connection.db_entity_type = entity_type
            connection.db_parent = parent
            connection.is_dirty = False
            res[('connection', id)] = connection
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'connection_tbl'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            parentType = self.convertFromDB(row[1], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[2], 'long', 'int')
            entity_type = self.convertFromDB(row[3], 'str', 'char(16)')
            parent = self.convertFromDB(row[4], 'long', 'long')
            
            connection = DBConnection(id=id)
            connection.db_parentType = parentType
            connection.db_entity_id = entity_id
            connection.db_entity_type = entity_type
            connection.db_parent = parent
            connection.is_dirty = False
            res[('connection', id)] = connection
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_connection(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'connection_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'connection_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_ports:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'connection_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBActionSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'action'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'prev_id', 'date', 'session', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            prevId = self.convertFromDB(row[1], 'long', 'int')
            date = self.convertFromDB(row[2], 'datetime', 'datetime')
            session = self.convertFromDB(row[3], 'long', 'int')
            user = self.convertFromDB(row[4], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            action = DBAction(prevId=prevId,
                              date=date,
                              session=session,
                              user=user,
                              id=id)
            action.db_vistrail = vistrail
            action.db_entity_id = entity_id
            action.db_entity_type = entity_type
            action.is_dirty = False
            res[('action', id)] = action
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'prev_id', 'date', 'session', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            prevId = self.convertFromDB(row[1], 'long', 'int')
            date = self.convertFromDB(row[2], 'datetime', 'datetime')
            session = self.convertFromDB(row[3], 'long', 'int')
            user = self.convertFromDB(row[4], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            action = DBAction(prevId=prevId,
                              date=date,
                              session=session,
                              user=user,
                              id=id)
            action.db_vistrail = vistrail
            action.db_entity_id = entity_id
            action.db_entity_type = entity_type
            action.is_dirty = False
            res[('action', id)] = action
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('vistrail', obj.db_vistrail) in all_objects:
            p = all_objects[('vistrail', obj.db_vistrail)]
            p.db_add_action(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'prev_id', 'date', 'session', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_prevId') and obj.db_prevId is not None:
            columnMap['prev_id'] = \
                self.convertToDB(obj.db_prevId, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_session') and obj.db_session is not None:
            columnMap['session'] = \
                self.convertToDB(obj.db_session, 'long', 'int')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'prev_id', 'date', 'session', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_prevId') and obj.db_prevId is not None:
            columnMap['prev_id'] = \
                self.convertToDB(obj.db_prevId, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_session') and obj.db_session is not None:
            columnMap['session'] = \
                self.convertToDB(obj.db_session, 'long', 'int')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_operations:
            child.db_action = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'action'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPortSpecSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'port_spec'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'type', 'optional', 'depth', 'sort_key', 'min_conns', 'max_conns', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port_spec'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            type = self.convertFromDB(row[2], 'str', 'varchar(255)')
            optional = self.convertFromDB(row[3], 'int', 'int')
            depth = self.convertFromDB(row[4], 'int', 'int')
            sort_key = self.convertFromDB(row[5], 'int', 'int')
            min_conns = self.convertFromDB(row[6], 'int', 'int')
            max_conns = self.convertFromDB(row[7], 'int', 'int')
            parentType = self.convertFromDB(row[8], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[9], 'long', 'int')
            entity_type = self.convertFromDB(row[10], 'str', 'char(16)')
            parent = self.convertFromDB(row[11], 'long', 'long')
            
            portSpec = DBPortSpec(name=name,
                                  type=type,
                                  optional=optional,
                                  depth=depth,
                                  sort_key=sort_key,
                                  min_conns=min_conns,
                                  max_conns=max_conns,
                                  id=id)
            portSpec.db_parentType = parentType
            portSpec.db_entity_id = entity_id
            portSpec.db_entity_type = entity_type
            portSpec.db_parent = parent
            portSpec.is_dirty = False
            res[('portSpec', id)] = portSpec
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'type', 'optional', 'depth', 'sort_key', 'min_conns', 'max_conns', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port_spec'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            type = self.convertFromDB(row[2], 'str', 'varchar(255)')
            optional = self.convertFromDB(row[3], 'int', 'int')
            depth = self.convertFromDB(row[4], 'int', 'int')
            sort_key = self.convertFromDB(row[5], 'int', 'int')
            min_conns = self.convertFromDB(row[6], 'int', 'int')
            max_conns = self.convertFromDB(row[7], 'int', 'int')
            parentType = self.convertFromDB(row[8], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[9], 'long', 'int')
            entity_type = self.convertFromDB(row[10], 'str', 'char(16)')
            parent = self.convertFromDB(row[11], 'long', 'long')
            
            portSpec = DBPortSpec(name=name,
                                  type=type,
                                  optional=optional,
                                  depth=depth,
                                  sort_key=sort_key,
                                  min_conns=min_conns,
                                  max_conns=max_conns,
                                  id=id)
            portSpec.db_parentType = parentType
            portSpec.db_entity_id = entity_id
            portSpec.db_entity_type = entity_type
            portSpec.db_parent = parent
            portSpec.is_dirty = False
            res[('portSpec', id)] = portSpec
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'module':
            p = all_objects[('module', obj.db_parent)]
            p.db_add_portSpec(obj)
        elif obj.db_parentType == 'module_descriptor':
            p = all_objects[('module_descriptor', obj.db_parent)]
            p.db_add_portSpec(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'type', 'optional', 'depth', 'sort_key', 'min_conns', 'max_conns', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port_spec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_optional') and obj.db_optional is not None:
            columnMap['optional'] = \
                self.convertToDB(obj.db_optional, 'int', 'int')
        if hasattr(obj, 'db_depth') and obj.db_depth is not None:
            columnMap['depth'] = \
                self.convertToDB(obj.db_depth, 'int', 'int')
        if hasattr(obj, 'db_sort_key') and obj.db_sort_key is not None:
            columnMap['sort_key'] = \
                self.convertToDB(obj.db_sort_key, 'int', 'int')
        if hasattr(obj, 'db_min_conns') and obj.db_min_conns is not None:
            columnMap['min_conns'] = \
                self.convertToDB(obj.db_min_conns, 'int', 'int')
        if hasattr(obj, 'db_max_conns') and obj.db_max_conns is not None:
            columnMap['max_conns'] = \
                self.convertToDB(obj.db_max_conns, 'int', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'type', 'optional', 'depth', 'sort_key', 'min_conns', 'max_conns', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'port_spec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_optional') and obj.db_optional is not None:
            columnMap['optional'] = \
                self.convertToDB(obj.db_optional, 'int', 'int')
        if hasattr(obj, 'db_depth') and obj.db_depth is not None:
            columnMap['depth'] = \
                self.convertToDB(obj.db_depth, 'int', 'int')
        if hasattr(obj, 'db_sort_key') and obj.db_sort_key is not None:
            columnMap['sort_key'] = \
                self.convertToDB(obj.db_sort_key, 'int', 'int')
        if hasattr(obj, 'db_min_conns') and obj.db_min_conns is not None:
            columnMap['min_conns'] = \
                self.convertToDB(obj.db_min_conns, 'int', 'int')
        if hasattr(obj, 'db_max_conns') and obj.db_max_conns is not None:
            columnMap['max_conns'] = \
                self.convertToDB(obj.db_max_conns, 'int', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_portSpecItems:
            child.db_portSpec = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'port_spec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBLogSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'log_tbl'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified', 'vistrail_id']
        table = 'log_tbl'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_type = self.convertFromDB(row[1], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            name = self.convertFromDB(row[3], 'str', 'varchar(255)')
            last_modified = self.convertFromDB(row[4], 'datetime', 'datetime')
            vistrail_id = self.convertFromDB(row[5], 'long', 'int')
            
            log = DBLog(entity_type=entity_type,
                        version=version,
                        name=name,
                        last_modified=last_modified,
                        vistrail_id=vistrail_id,
                        id=id)
            log.is_dirty = False
            res[('log', id)] = log
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified', 'vistrail_id']
        table = 'log_tbl'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_type = self.convertFromDB(row[1], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            name = self.convertFromDB(row[3], 'str', 'varchar(255)')
            last_modified = self.convertFromDB(row[4], 'datetime', 'datetime')
            vistrail_id = self.convertFromDB(row[5], 'long', 'int')
            
            log = DBLog(entity_type=entity_type,
                        version=version,
                        name=name,
                        last_modified=last_modified,
                        vistrail_id=vistrail_id,
                        id=id)
            log.is_dirty = False
            res[('log', id)] = log
        return res

    def from_sql_fast(self, obj, all_objects):
        pass
    
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified', 'vistrail_id']
        table = 'log_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        if hasattr(obj, 'db_vistrail_id') and obj.db_vistrail_id is not None:
            columnMap['vistrail_id'] = \
                self.convertToDB(obj.db_vistrail_id, 'long', 'int')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'entity_type', 'version', 'name', 'last_modified', 'vistrail_id']
        table = 'log_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        if hasattr(obj, 'db_vistrail_id') and obj.db_vistrail_id is not None:
            columnMap['vistrail_id'] = \
                self.convertToDB(obj.db_vistrail_id, 'long', 'int')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_workflow_execs:
            child.db_log = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'log_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBLoopIterationSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'loop_iteration'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'iteration', 'completed', 'error', 'parent_id', 'entity_id', 'entity_type']
        table = 'loop_iteration'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            iteration = self.convertFromDB(row[3], 'int', 'int')
            completed = self.convertFromDB(row[4], 'int', 'int')
            error = self.convertFromDB(row[5], 'str', 'varchar(1023)')
            parent = self.convertFromDB(row[6], 'str', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            loop_iteration = DBLoopIteration(ts_start=ts_start,
                                             ts_end=ts_end,
                                             iteration=iteration,
                                             completed=completed,
                                             error=error,
                                             id=id)
            loop_iteration.db_parent = parent
            loop_iteration.db_entity_id = entity_id
            loop_iteration.db_entity_type = entity_type
            loop_iteration.is_dirty = False
            res[('loop_iteration', id)] = loop_iteration
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'iteration', 'completed', 'error', 'parent_id', 'entity_id', 'entity_type']
        table = 'loop_iteration'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            iteration = self.convertFromDB(row[3], 'int', 'int')
            completed = self.convertFromDB(row[4], 'int', 'int')
            error = self.convertFromDB(row[5], 'str', 'varchar(1023)')
            parent = self.convertFromDB(row[6], 'str', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            loop_iteration = DBLoopIteration(ts_start=ts_start,
                                             ts_end=ts_end,
                                             iteration=iteration,
                                             completed=completed,
                                             error=error,
                                             id=id)
            loop_iteration.db_parent = parent
            loop_iteration.db_entity_id = entity_id
            loop_iteration.db_entity_type = entity_type
            loop_iteration.is_dirty = False
            res[('loop_iteration', id)] = loop_iteration
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('loop_exec', obj.db_parent) in all_objects:
            p = all_objects[('loop_exec', obj.db_parent)]
            p.db_add_loop_iteration(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'ts_start', 'ts_end', 'iteration', 'completed', 'error', 'parent_id', 'entity_id', 'entity_type']
        table = 'loop_iteration'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_iteration') and obj.db_iteration is not None:
            columnMap['iteration'] = \
                self.convertToDB(obj.db_iteration, 'int', 'int')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_error') and obj.db_error is not None:
            columnMap['error'] = \
                self.convertToDB(obj.db_error, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'str', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'ts_start', 'ts_end', 'iteration', 'completed', 'error', 'parent_id', 'entity_id', 'entity_type']
        table = 'loop_iteration'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_iteration') and obj.db_iteration is not None:
            columnMap['iteration'] = \
                self.convertToDB(obj.db_iteration, 'int', 'int')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_error') and obj.db_error is not None:
            columnMap['error'] = \
                self.convertToDB(obj.db_error, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'str', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_item_execs:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'loop_iteration'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPEParameterSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'pe_parameter'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'interpolator', 'value', 'dimension', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_parameter'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            interpolator = self.convertFromDB(row[2], 'str', 'varchar(255)')
            value = self.convertFromDB(row[3], 'str', 'mediumtext')
            dimension = self.convertFromDB(row[4], 'long', 'int')
            parentType = self.convertFromDB(row[5], 'str', 'char(32)')
            pe_function = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            pe_parameter = DBPEParameter(pos=pos,
                                         interpolator=interpolator,
                                         value=value,
                                         dimension=dimension,
                                         id=id)
            pe_parameter.db_parentType = parentType
            pe_parameter.db_pe_function = pe_function
            pe_parameter.db_entity_id = entity_id
            pe_parameter.db_entity_type = entity_type
            pe_parameter.is_dirty = False
            res[('pe_parameter', id)] = pe_parameter
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'interpolator', 'value', 'dimension', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_parameter'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            interpolator = self.convertFromDB(row[2], 'str', 'varchar(255)')
            value = self.convertFromDB(row[3], 'str', 'mediumtext')
            dimension = self.convertFromDB(row[4], 'long', 'int')
            parentType = self.convertFromDB(row[5], 'str', 'char(32)')
            pe_function = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            pe_parameter = DBPEParameter(pos=pos,
                                         interpolator=interpolator,
                                         value=value,
                                         dimension=dimension,
                                         id=id)
            pe_parameter.db_parentType = parentType
            pe_parameter.db_pe_function = pe_function
            pe_parameter.db_entity_id = entity_id
            pe_parameter.db_entity_type = entity_type
            pe_parameter.is_dirty = False
            res[('pe_parameter', id)] = pe_parameter
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('pe_function', obj.db_pe_function) in all_objects:
            p = all_objects[('pe_function', obj.db_pe_function)]
            p.db_add_parameter(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'pos', 'interpolator', 'value', 'dimension', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_interpolator') and obj.db_interpolator is not None:
            columnMap['interpolator'] = \
                self.convertToDB(obj.db_interpolator, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'mediumtext')
        if hasattr(obj, 'db_dimension') and obj.db_dimension is not None:
            columnMap['dimension'] = \
                self.convertToDB(obj.db_dimension, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_pe_function') and obj.db_pe_function is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_pe_function, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'pos', 'interpolator', 'value', 'dimension', 'parent_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'pe_parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_interpolator') and obj.db_interpolator is not None:
            columnMap['interpolator'] = \
                self.convertToDB(obj.db_interpolator, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'mediumtext')
        if hasattr(obj, 'db_dimension') and obj.db_dimension is not None:
            columnMap['dimension'] = \
                self.convertToDB(obj.db_dimension, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_pe_function') and obj.db_pe_function is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_pe_function, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'pe_parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBWorkflowExecSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'workflow_exec'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'user', 'ip', 'session', 'vt_version', 'ts_start', 'ts_end', 'parent_id', 'parent_type', 'parent_version', 'completed', 'name', 'log_id', 'entity_id', 'entity_type']
        table = 'workflow_exec'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            user = self.convertFromDB(row[1], 'str', 'varchar(255)')
            ip = self.convertFromDB(row[2], 'str', 'varchar(255)')
            session = self.convertFromDB(row[3], 'long', 'int')
            vt_version = self.convertFromDB(row[4], 'str', 'varchar(255)')
            ts_start = self.convertFromDB(row[5], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[6], 'datetime', 'datetime')
            parent_id = self.convertFromDB(row[7], 'long', 'int')
            parent_type = self.convertFromDB(row[8], 'str', 'varchar(255)')
            parent_version = self.convertFromDB(row[9], 'long', 'int')
            completed = self.convertFromDB(row[10], 'int', 'int')
            name = self.convertFromDB(row[11], 'str', 'varchar(255)')
            log = self.convertFromDB(row[12], 'long', 'int')
            entity_id = self.convertFromDB(row[13], 'long', 'int')
            entity_type = self.convertFromDB(row[14], 'str', 'char(16)')
            
            workflow_exec = DBWorkflowExec(user=user,
                                           ip=ip,
                                           session=session,
                                           vt_version=vt_version,
                                           ts_start=ts_start,
                                           ts_end=ts_end,
                                           parent_id=parent_id,
                                           parent_type=parent_type,
                                           parent_version=parent_version,
                                           completed=completed,
                                           name=name,
                                           id=id)
            workflow_exec.db_log = log
            workflow_exec.db_entity_id = entity_id
            workflow_exec.db_entity_type = entity_type
            workflow_exec.is_dirty = False
            res[('workflow_exec', id)] = workflow_exec
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'user', 'ip', 'session', 'vt_version', 'ts_start', 'ts_end', 'parent_id', 'parent_type', 'parent_version', 'completed', 'name', 'log_id', 'entity_id', 'entity_type']
        table = 'workflow_exec'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            user = self.convertFromDB(row[1], 'str', 'varchar(255)')
            ip = self.convertFromDB(row[2], 'str', 'varchar(255)')
            session = self.convertFromDB(row[3], 'long', 'int')
            vt_version = self.convertFromDB(row[4], 'str', 'varchar(255)')
            ts_start = self.convertFromDB(row[5], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[6], 'datetime', 'datetime')
            parent_id = self.convertFromDB(row[7], 'long', 'int')
            parent_type = self.convertFromDB(row[8], 'str', 'varchar(255)')
            parent_version = self.convertFromDB(row[9], 'long', 'int')
            completed = self.convertFromDB(row[10], 'int', 'int')
            name = self.convertFromDB(row[11], 'str', 'varchar(255)')
            log = self.convertFromDB(row[12], 'long', 'int')
            entity_id = self.convertFromDB(row[13], 'long', 'int')
            entity_type = self.convertFromDB(row[14], 'str', 'char(16)')
            
            workflow_exec = DBWorkflowExec(user=user,
                                           ip=ip,
                                           session=session,
                                           vt_version=vt_version,
                                           ts_start=ts_start,
                                           ts_end=ts_end,
                                           parent_id=parent_id,
                                           parent_type=parent_type,
                                           parent_version=parent_version,
                                           completed=completed,
                                           name=name,
                                           id=id)
            workflow_exec.db_log = log
            workflow_exec.db_entity_id = entity_id
            workflow_exec.db_entity_type = entity_type
            workflow_exec.is_dirty = False
            res[('workflow_exec', id)] = workflow_exec
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('log', obj.db_log) in all_objects:
            p = all_objects[('log', obj.db_log)]
            p.db_add_workflow_exec(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'user', 'ip', 'session', 'vt_version', 'ts_start', 'ts_end', 'parent_id', 'parent_type', 'parent_version', 'completed', 'name', 'log_id', 'entity_id', 'entity_type']
        table = 'workflow_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_ip') and obj.db_ip is not None:
            columnMap['ip'] = \
                self.convertToDB(obj.db_ip, 'str', 'varchar(255)')
        if hasattr(obj, 'db_session') and obj.db_session is not None:
            columnMap['session'] = \
                self.convertToDB(obj.db_session, 'long', 'int')
        if hasattr(obj, 'db_vt_version') and obj.db_vt_version is not None:
            columnMap['vt_version'] = \
                self.convertToDB(obj.db_vt_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_parent_id') and obj.db_parent_id is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent_id, 'long', 'int')
        if hasattr(obj, 'db_parent_type') and obj.db_parent_type is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parent_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parent_version') and obj.db_parent_version is not None:
            columnMap['parent_version'] = \
                self.convertToDB(obj.db_parent_version, 'long', 'int')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_log') and obj.db_log is not None:
            columnMap['log_id'] = \
                self.convertToDB(obj.db_log, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'user', 'ip', 'session', 'vt_version', 'ts_start', 'ts_end', 'parent_id', 'parent_type', 'parent_version', 'completed', 'name', 'log_id', 'entity_id', 'entity_type']
        table = 'workflow_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_ip') and obj.db_ip is not None:
            columnMap['ip'] = \
                self.convertToDB(obj.db_ip, 'str', 'varchar(255)')
        if hasattr(obj, 'db_session') and obj.db_session is not None:
            columnMap['session'] = \
                self.convertToDB(obj.db_session, 'long', 'int')
        if hasattr(obj, 'db_vt_version') and obj.db_vt_version is not None:
            columnMap['vt_version'] = \
                self.convertToDB(obj.db_vt_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_parent_id') and obj.db_parent_id is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent_id, 'long', 'int')
        if hasattr(obj, 'db_parent_type') and obj.db_parent_type is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parent_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parent_version') and obj.db_parent_version is not None:
            columnMap['parent_version'] = \
                self.convertToDB(obj.db_parent_version, 'long', 'int')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_log') and obj.db_log is not None:
            columnMap['log_id'] = \
                self.convertToDB(obj.db_log, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_machines:
            child.db_workflow_exec = obj.db_id
        for child in obj.db_item_execs:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'workflow_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBLocationSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'location'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'x', 'y', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'location'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            x = self.convertFromDB(row[1], 'float', 'DECIMAL(18,12)')
            y = self.convertFromDB(row[2], 'float', 'DECIMAL(18,12)')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            location = DBLocation(x=x,
                                  y=y,
                                  id=id)
            location.db_parentType = parentType
            location.db_entity_id = entity_id
            location.db_entity_type = entity_type
            location.db_parent = parent
            location.is_dirty = False
            res[('location', id)] = location
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'x', 'y', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'location'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            x = self.convertFromDB(row[1], 'float', 'DECIMAL(18,12)')
            y = self.convertFromDB(row[2], 'float', 'DECIMAL(18,12)')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            location = DBLocation(x=x,
                                  y=y,
                                  id=id)
            location.db_parentType = parentType
            location.db_entity_id = entity_id
            location.db_entity_type = entity_type
            location.db_parent = parent
            location.is_dirty = False
            res[('location', id)] = location
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'module':
            p = all_objects[('module', obj.db_parent)]
            p.db_add_location(obj)
        elif obj.db_parentType == 'abstraction':
            p = all_objects[('abstraction', obj.db_parent)]
            p.db_add_location(obj)
        elif obj.db_parentType == 'group':
            p = all_objects[('group', obj.db_parent)]
            p.db_add_location(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'x', 'y', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'location'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_x') and obj.db_x is not None:
            columnMap['x'] = \
                self.convertToDB(obj.db_x, 'float', 'DECIMAL(18,12)')
        if hasattr(obj, 'db_y') and obj.db_y is not None:
            columnMap['y'] = \
                self.convertToDB(obj.db_y, 'float', 'DECIMAL(18,12)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'x', 'y', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'location'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_x') and obj.db_x is not None:
            columnMap['x'] = \
                self.convertToDB(obj.db_x, 'float', 'DECIMAL(18,12)')
        if hasattr(obj, 'db_y') and obj.db_y is not None:
            columnMap['y'] = \
                self.convertToDB(obj.db_y, 'float', 'DECIMAL(18,12)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'location'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBFunctionSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'function'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'name', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'function'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            function = DBFunction(pos=pos,
                                  name=name,
                                  id=id)
            function.db_parentType = parentType
            function.db_entity_id = entity_id
            function.db_entity_type = entity_type
            function.db_parent = parent
            function.is_dirty = False
            res[('function', id)] = function
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'name', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'function'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            function = DBFunction(pos=pos,
                                  name=name,
                                  id=id)
            function.db_parentType = parentType
            function.db_entity_id = entity_id
            function.db_entity_type = entity_type
            function.db_parent = parent
            function.is_dirty = False
            res[('function', id)] = function
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'module':
            p = all_objects[('module', obj.db_parent)]
            p.db_add_function(obj)
        elif obj.db_parentType == 'abstraction':
            p = all_objects[('abstraction', obj.db_parent)]
            p.db_add_function(obj)
        elif obj.db_parentType == 'group':
            p = all_objects[('group', obj.db_parent)]
            p.db_add_function(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'pos', 'name', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'function'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'pos', 'name', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'function'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_parameters:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'function'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBActionAnnotationSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'action_annotation'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action_annotation'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'varchar(8191)')
            action_id = self.convertFromDB(row[3], 'long', 'int')
            date = self.convertFromDB(row[4], 'datetime', 'datetime')
            user = self.convertFromDB(row[5], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            actionAnnotation = DBActionAnnotation(key=key,
                                                  value=value,
                                                  action_id=action_id,
                                                  date=date,
                                                  user=user,
                                                  id=id)
            actionAnnotation.db_vistrail = vistrail
            actionAnnotation.db_entity_id = entity_id
            actionAnnotation.db_entity_type = entity_type
            actionAnnotation.is_dirty = False
            res[('actionAnnotation', id)] = actionAnnotation
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action_annotation'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'varchar(8191)')
            action_id = self.convertFromDB(row[3], 'long', 'int')
            date = self.convertFromDB(row[4], 'datetime', 'datetime')
            user = self.convertFromDB(row[5], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            actionAnnotation = DBActionAnnotation(key=key,
                                                  value=value,
                                                  action_id=action_id,
                                                  date=date,
                                                  user=user,
                                                  id=id)
            actionAnnotation.db_vistrail = vistrail
            actionAnnotation.db_entity_id = entity_id
            actionAnnotation.db_entity_type = entity_type
            actionAnnotation.is_dirty = False
            res[('actionAnnotation', id)] = actionAnnotation
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('vistrail', obj.db_vistrail) in all_objects:
            p = all_objects[('vistrail', obj.db_vistrail)]
            p.db_add_actionAnnotation(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action_annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['akey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_action_id') and obj.db_action_id is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action_id, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'action_annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['akey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_action_id') and obj.db_action_id is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action_id, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'action_annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBControlParameterSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'control_parameter'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'control_parameter'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'mediumtext')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            controlParameter = DBControlParameter(name=name,
                                                  value=value,
                                                  id=id)
            controlParameter.db_parentType = parentType
            controlParameter.db_entity_id = entity_id
            controlParameter.db_entity_type = entity_type
            controlParameter.db_parent = parent
            controlParameter.is_dirty = False
            res[('controlParameter', id)] = controlParameter
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'control_parameter'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'mediumtext')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            controlParameter = DBControlParameter(name=name,
                                                  value=value,
                                                  id=id)
            controlParameter.db_parentType = parentType
            controlParameter.db_entity_id = entity_id
            controlParameter.db_entity_type = entity_type
            controlParameter.db_parent = parent
            controlParameter.is_dirty = False
            res[('controlParameter', id)] = controlParameter
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'vistrail':
            p = all_objects[('vistrail', obj.db_parent)]
            p.db_add_controlParameter(obj)
        elif obj.db_parentType == 'module':
            p = all_objects[('module', obj.db_parent)]
            p.db_add_controlParameter(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'abstraction':
            p = all_objects[('abstraction', obj.db_parent)]
            p.db_add_controlParameter(obj)
        elif obj.db_parentType == 'group':
            p = all_objects[('group', obj.db_parent)]
            p.db_add_controlParameter(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'control_parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'mediumtext')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'control_parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'mediumtext')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'control_parameter'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPluginDataSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'plugin_data'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'data', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'plugin_data'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            data = self.convertFromDB(row[1], 'str', 'varchar(8191)')
            parentType = self.convertFromDB(row[2], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[3], 'long', 'int')
            entity_type = self.convertFromDB(row[4], 'str', 'char(16)')
            parent = self.convertFromDB(row[5], 'long', 'long')
            
            plugin_data = DBPluginData(data=data,
                                       id=id)
            plugin_data.db_parentType = parentType
            plugin_data.db_entity_id = entity_id
            plugin_data.db_entity_type = entity_type
            plugin_data.db_parent = parent
            plugin_data.is_dirty = False
            res[('plugin_data', id)] = plugin_data
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'data', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'plugin_data'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            data = self.convertFromDB(row[1], 'str', 'varchar(8191)')
            parentType = self.convertFromDB(row[2], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[3], 'long', 'int')
            entity_type = self.convertFromDB(row[4], 'str', 'char(16)')
            parent = self.convertFromDB(row[5], 'long', 'long')
            
            plugin_data = DBPluginData(data=data,
                                       id=id)
            plugin_data.db_parentType = parentType
            plugin_data.db_entity_id = entity_id
            plugin_data.db_entity_type = entity_type
            plugin_data.db_parent = parent
            plugin_data.is_dirty = False
            res[('plugin_data', id)] = plugin_data
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_plugin_data(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'data', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'plugin_data'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_data') and obj.db_data is not None:
            columnMap['data'] = \
                self.convertToDB(obj.db_data, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'data', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'plugin_data'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_data') and obj.db_data is not None:
            columnMap['data'] = \
                self.convertToDB(obj.db_data, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'plugin_data'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBDeleteSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'delete_tbl'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'delete_tbl'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            what = self.convertFromDB(row[1], 'str', 'varchar(255)')
            objectId = self.convertFromDB(row[2], 'long', 'int')
            parentObjId = self.convertFromDB(row[3], 'long', 'int')
            parentObjType = self.convertFromDB(row[4], 'str', 'char(16)')
            action = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            delete = DBDelete(what=what,
                              objectId=objectId,
                              parentObjId=parentObjId,
                              parentObjType=parentObjType,
                              id=id)
            delete.db_action = action
            delete.db_entity_id = entity_id
            delete.db_entity_type = entity_type
            delete.is_dirty = False
            res[('delete', id)] = delete
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'delete_tbl'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            what = self.convertFromDB(row[1], 'str', 'varchar(255)')
            objectId = self.convertFromDB(row[2], 'long', 'int')
            parentObjId = self.convertFromDB(row[3], 'long', 'int')
            parentObjType = self.convertFromDB(row[4], 'str', 'char(16)')
            action = self.convertFromDB(row[5], 'long', 'int')
            entity_id = self.convertFromDB(row[6], 'long', 'int')
            entity_type = self.convertFromDB(row[7], 'str', 'char(16)')
            
            delete = DBDelete(what=what,
                              objectId=objectId,
                              parentObjId=parentObjId,
                              parentObjType=parentObjType,
                              id=id)
            delete.db_action = action
            delete.db_entity_id = entity_id
            delete.db_entity_type = entity_type
            delete.is_dirty = False
            res[('delete', id)] = delete
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('action', obj.db_action) in all_objects:
            p = all_objects[('action', obj.db_action)]
            p.db_add_operation(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'delete_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_what') and obj.db_what is not None:
            columnMap['what'] = \
                self.convertToDB(obj.db_what, 'str', 'varchar(255)')
        if hasattr(obj, 'db_objectId') and obj.db_objectId is not None:
            columnMap['object_id'] = \
                self.convertToDB(obj.db_objectId, 'long', 'int')
        if hasattr(obj, 'db_parentObjId') and obj.db_parentObjId is not None:
            columnMap['par_obj_id'] = \
                self.convertToDB(obj.db_parentObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjType') and obj.db_parentObjType is not None:
            columnMap['par_obj_type'] = \
                self.convertToDB(obj.db_parentObjType, 'str', 'char(16)')
        if hasattr(obj, 'db_action') and obj.db_action is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'what', 'object_id', 'par_obj_id', 'par_obj_type', 'action_id', 'entity_id', 'entity_type']
        table = 'delete_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_what') and obj.db_what is not None:
            columnMap['what'] = \
                self.convertToDB(obj.db_what, 'str', 'varchar(255)')
        if hasattr(obj, 'db_objectId') and obj.db_objectId is not None:
            columnMap['object_id'] = \
                self.convertToDB(obj.db_objectId, 'long', 'int')
        if hasattr(obj, 'db_parentObjId') and obj.db_parentObjId is not None:
            columnMap['par_obj_id'] = \
                self.convertToDB(obj.db_parentObjId, 'long', 'int')
        if hasattr(obj, 'db_parentObjType') and obj.db_parentObjType is not None:
            columnMap['par_obj_type'] = \
                self.convertToDB(obj.db_parentObjType, 'str', 'char(16)')
        if hasattr(obj, 'db_action') and obj.db_action is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'delete_tbl'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBVistrailVariableSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'vistrail_variable'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['name', 'uuid', 'package', 'module', 'namespace', 'value', 'parent_id', 'entity_id', 'entity_type']
        table = 'vistrail_variable'
        whereMap = global_props
        orderBy = 'name'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            name = self.convertFromDB(row[0], 'str', 'varchar(255)')
            uuid = self.convertFromDB(row[1], 'str', 'char(36)')
            package = self.convertFromDB(row[2], 'str', 'varchar(255)')
            module = self.convertFromDB(row[3], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[4], 'str', 'varchar(255)')
            value = self.convertFromDB(row[5], 'str', 'varchar(8191)')
            vistrail = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            vistrailVariable = DBVistrailVariable(uuid=uuid,
                                                  package=package,
                                                  module=module,
                                                  namespace=namespace,
                                                  value=value,
                                                  name=name)
            vistrailVariable.db_vistrail = vistrail
            vistrailVariable.db_entity_id = entity_id
            vistrailVariable.db_entity_type = entity_type
            vistrailVariable.is_dirty = False
            res[('vistrailVariable', name)] = vistrailVariable
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['name', 'uuid', 'package', 'module', 'namespace', 'value', 'parent_id', 'entity_id', 'entity_type']
        table = 'vistrail_variable'
        whereMap = global_props
        orderBy = 'name'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            name = self.convertFromDB(row[0], 'str', 'varchar(255)')
            uuid = self.convertFromDB(row[1], 'str', 'char(36)')
            package = self.convertFromDB(row[2], 'str', 'varchar(255)')
            module = self.convertFromDB(row[3], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[4], 'str', 'varchar(255)')
            value = self.convertFromDB(row[5], 'str', 'varchar(8191)')
            vistrail = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            vistrailVariable = DBVistrailVariable(uuid=uuid,
                                                  package=package,
                                                  module=module,
                                                  namespace=namespace,
                                                  value=value,
                                                  name=name)
            vistrailVariable.db_vistrail = vistrail
            vistrailVariable.db_entity_id = entity_id
            vistrailVariable.db_entity_type = entity_type
            vistrailVariable.is_dirty = False
            res[('vistrailVariable', name)] = vistrailVariable
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('vistrail', obj.db_vistrail) in all_objects:
            p = all_objects[('vistrail', obj.db_vistrail)]
            p.db_add_vistrailVariable(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['name', 'uuid', 'package', 'module', 'namespace', 'value', 'parent_id', 'entity_id', 'entity_type']
        table = 'vistrail_variable'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_name is not None:
            keyStr = self.convertToDB(obj.db_name, 'str', 'varchar(255)')
            whereMap['name'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_uuid') and obj.db_uuid is not None:
            columnMap['uuid'] = \
                self.convertToDB(obj.db_uuid, 'str', 'char(36)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(255)')
        if hasattr(obj, 'db_module') and obj.db_module is not None:
            columnMap['module'] = \
                self.convertToDB(obj.db_module, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['name', 'uuid', 'package', 'module', 'namespace', 'value', 'parent_id', 'entity_id', 'entity_type']
        table = 'vistrail_variable'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_name is not None:
            keyStr = self.convertToDB(obj.db_name, 'str', 'varchar(255)')
            whereMap['name'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_uuid') and obj.db_uuid is not None:
            columnMap['uuid'] = \
                self.convertToDB(obj.db_uuid, 'str', 'char(36)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(255)')
        if hasattr(obj, 'db_module') and obj.db_module is not None:
            columnMap['module'] = \
                self.convertToDB(obj.db_module, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'vistrail_variable'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_name is not None:
            keyStr = self.convertToDB(obj.db_name, 'str', 'varchar(255)')
            whereMap['name'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBModuleDescriptorSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'module_descriptor'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'package', 'namespace', 'package_version', 'version', 'base_descriptor_id', 'parent_id', 'entity_id', 'entity_type']
        table = 'module_descriptor'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            package = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package_version = self.convertFromDB(row[4], 'str', 'varchar(255)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            base_descriptor_id = self.convertFromDB(row[6], 'long', 'int')
            package = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            module_descriptor = DBModuleDescriptor(name=name,
                                                   package=package,
                                                   namespace=namespace,
                                                   package_version=package_version,
                                                   version=version,
                                                   base_descriptor_id=base_descriptor_id,
                                                   id=id)
            module_descriptor.db_package = package
            module_descriptor.db_entity_id = entity_id
            module_descriptor.db_entity_type = entity_type
            module_descriptor.is_dirty = False
            res[('module_descriptor', id)] = module_descriptor
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'package', 'namespace', 'package_version', 'version', 'base_descriptor_id', 'parent_id', 'entity_id', 'entity_type']
        table = 'module_descriptor'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            package = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package_version = self.convertFromDB(row[4], 'str', 'varchar(255)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            base_descriptor_id = self.convertFromDB(row[6], 'long', 'int')
            package = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            module_descriptor = DBModuleDescriptor(name=name,
                                                   package=package,
                                                   namespace=namespace,
                                                   package_version=package_version,
                                                   version=version,
                                                   base_descriptor_id=base_descriptor_id,
                                                   id=id)
            module_descriptor.db_package = package
            module_descriptor.db_entity_id = entity_id
            module_descriptor.db_entity_type = entity_type
            module_descriptor.is_dirty = False
            res[('module_descriptor', id)] = module_descriptor
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('package', obj.db_package) in all_objects:
            p = all_objects[('package', obj.db_package)]
            p.db_add_module_descriptor(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'package', 'namespace', 'package_version', 'version', 'base_descriptor_id', 'parent_id', 'entity_id', 'entity_type']
        table = 'module_descriptor'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package_version') and obj.db_package_version is not None:
            columnMap['package_version'] = \
                self.convertToDB(obj.db_package_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_base_descriptor_id') and obj.db_base_descriptor_id is not None:
            columnMap['base_descriptor_id'] = \
                self.convertToDB(obj.db_base_descriptor_id, 'long', 'int')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_package, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'package', 'namespace', 'package_version', 'version', 'base_descriptor_id', 'parent_id', 'entity_id', 'entity_type']
        table = 'module_descriptor'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package_version') and obj.db_package_version is not None:
            columnMap['package_version'] = \
                self.convertToDB(obj.db_package_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_base_descriptor_id') and obj.db_base_descriptor_id is not None:
            columnMap['base_descriptor_id'] = \
                self.convertToDB(obj.db_base_descriptor_id, 'long', 'int')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_package, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_portSpecs:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'module_descriptor'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBTagSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'tag'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'tag'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[2], 'long', 'int')
            entity_id = self.convertFromDB(row[3], 'long', 'int')
            entity_type = self.convertFromDB(row[4], 'str', 'char(16)')
            
            tag = DBTag(name=name,
                        id=id)
            tag.db_vistrail = vistrail
            tag.db_entity_id = entity_id
            tag.db_entity_type = entity_type
            tag.is_dirty = False
            res[('tag', id)] = tag
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'tag'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[2], 'long', 'int')
            entity_id = self.convertFromDB(row[3], 'long', 'int')
            entity_type = self.convertFromDB(row[4], 'str', 'char(16)')
            
            tag = DBTag(name=name,
                        id=id)
            tag.db_vistrail = vistrail
            tag.db_entity_id = entity_id
            tag.db_entity_type = entity_type
            tag.is_dirty = False
            res[('tag', id)] = tag
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('vistrail', obj.db_vistrail) in all_objects:
            p = all_objects[('vistrail', obj.db_vistrail)]
            p.db_add_tag(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'tag'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'parent_id', 'entity_id', 'entity_type']
        table = 'tag'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'tag'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBPortSpecItemSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'port_spec_item'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'module', 'package', 'namespace', 'label', '_default', '_values', 'entry_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'port_spec_item'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            module = self.convertFromDB(row[2], 'str', 'varchar(255)')
            package = self.convertFromDB(row[3], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[4], 'str', 'varchar(255)')
            label = self.convertFromDB(row[5], 'str', 'varchar(4095)')
            default = self.convertFromDB(row[6], 'str', 'varchar(4095)')
            values = self.convertFromDB(row[7], 'str', 'mediumtext')
            entry_type = self.convertFromDB(row[8], 'str', 'varchar(255)')
            portSpec = self.convertFromDB(row[9], 'long', 'int')
            entity_id = self.convertFromDB(row[10], 'long', 'int')
            entity_type = self.convertFromDB(row[11], 'str', 'char(16)')
            
            portSpecItem = DBPortSpecItem(pos=pos,
                                          module=module,
                                          package=package,
                                          namespace=namespace,
                                          label=label,
                                          default=default,
                                          values=values,
                                          entry_type=entry_type,
                                          id=id)
            portSpecItem.db_portSpec = portSpec
            portSpecItem.db_entity_id = entity_id
            portSpecItem.db_entity_type = entity_type
            portSpecItem.is_dirty = False
            res[('portSpecItem', id)] = portSpecItem
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'pos', 'module', 'package', 'namespace', 'label', '_default', '_values', 'entry_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'port_spec_item'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            pos = self.convertFromDB(row[1], 'long', 'int')
            module = self.convertFromDB(row[2], 'str', 'varchar(255)')
            package = self.convertFromDB(row[3], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[4], 'str', 'varchar(255)')
            label = self.convertFromDB(row[5], 'str', 'varchar(4095)')
            default = self.convertFromDB(row[6], 'str', 'varchar(4095)')
            values = self.convertFromDB(row[7], 'str', 'mediumtext')
            entry_type = self.convertFromDB(row[8], 'str', 'varchar(255)')
            portSpec = self.convertFromDB(row[9], 'long', 'int')
            entity_id = self.convertFromDB(row[10], 'long', 'int')
            entity_type = self.convertFromDB(row[11], 'str', 'char(16)')
            
            portSpecItem = DBPortSpecItem(pos=pos,
                                          module=module,
                                          package=package,
                                          namespace=namespace,
                                          label=label,
                                          default=default,
                                          values=values,
                                          entry_type=entry_type,
                                          id=id)
            portSpecItem.db_portSpec = portSpec
            portSpecItem.db_entity_id = entity_id
            portSpecItem.db_entity_type = entity_type
            portSpecItem.is_dirty = False
            res[('portSpecItem', id)] = portSpecItem
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('portSpec', obj.db_portSpec) in all_objects:
            p = all_objects[('portSpec', obj.db_portSpec)]
            p.db_add_portSpecItem(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'pos', 'module', 'package', 'namespace', 'label', '_default', '_values', 'entry_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'port_spec_item'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_module') and obj.db_module is not None:
            columnMap['module'] = \
                self.convertToDB(obj.db_module, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_label') and obj.db_label is not None:
            columnMap['label'] = \
                self.convertToDB(obj.db_label, 'str', 'varchar(4095)')
        if hasattr(obj, 'db_default') and obj.db_default is not None:
            columnMap['_default'] = \
                self.convertToDB(obj.db_default, 'str', 'varchar(4095)')
        if hasattr(obj, 'db_values') and obj.db_values is not None:
            columnMap['_values'] = \
                self.convertToDB(obj.db_values, 'str', 'mediumtext')
        if hasattr(obj, 'db_entry_type') and obj.db_entry_type is not None:
            columnMap['entry_type'] = \
                self.convertToDB(obj.db_entry_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_portSpec') and obj.db_portSpec is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_portSpec, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'pos', 'module', 'package', 'namespace', 'label', '_default', '_values', 'entry_type', 'parent_id', 'entity_id', 'entity_type']
        table = 'port_spec_item'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_module') and obj.db_module is not None:
            columnMap['module'] = \
                self.convertToDB(obj.db_module, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_label') and obj.db_label is not None:
            columnMap['label'] = \
                self.convertToDB(obj.db_label, 'str', 'varchar(4095)')
        if hasattr(obj, 'db_default') and obj.db_default is not None:
            columnMap['_default'] = \
                self.convertToDB(obj.db_default, 'str', 'varchar(4095)')
        if hasattr(obj, 'db_values') and obj.db_values is not None:
            columnMap['_values'] = \
                self.convertToDB(obj.db_values, 'str', 'mediumtext')
        if hasattr(obj, 'db_entry_type') and obj.db_entry_type is not None:
            columnMap['entry_type'] = \
                self.convertToDB(obj.db_entry_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_portSpec') and obj.db_portSpec is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_portSpec, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'port_spec_item'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBMashupComponentSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'mashup_component'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'vtid', 'vttype', 'vtparent_type', 'vtparent_id', 'vtpos', 'vtmid', 'pos', 'type', 'val', 'minVal', 'maxVal', 'stepSize', 'strvaluelist', 'widget', 'seq', 'parent', 'alias_id', 'entity_id', 'entity_type']
        table = 'mashup_component'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            vtid = self.convertFromDB(row[1], 'long', 'int')
            vttype = self.convertFromDB(row[2], 'str', 'varchar(255)')
            vtparent_type = self.convertFromDB(row[3], 'str', 'char(32)')
            vtparent_id = self.convertFromDB(row[4], 'long', 'int')
            vtpos = self.convertFromDB(row[5], 'long', 'int')
            vtmid = self.convertFromDB(row[6], 'long', 'int')
            pos = self.convertFromDB(row[7], 'long', 'int')
            type = self.convertFromDB(row[8], 'str', 'varchar(255)')
            val = self.convertFromDB(row[9], 'str', 'mediumtext')
            minVal = self.convertFromDB(row[10], 'str', 'varchar(255)')
            maxVal = self.convertFromDB(row[11], 'str', 'varchar(255)')
            stepSize = self.convertFromDB(row[12], 'str', 'varchar(255)')
            strvaluelist = self.convertFromDB(row[13], 'str', 'mediumtext')
            widget = self.convertFromDB(row[14], 'str', 'varchar(255)')
            seq = self.convertFromDB(row[15], 'int', 'int')
            parent = self.convertFromDB(row[16], 'str', 'varchar(255)')
            mashup_alias = self.convertFromDB(row[17], 'long', 'int')
            entity_id = self.convertFromDB(row[18], 'long', 'int')
            entity_type = self.convertFromDB(row[19], 'str', 'char(16)')
            
            mashup_component = DBMashupComponent(vtid=vtid,
                                                 vttype=vttype,
                                                 vtparent_type=vtparent_type,
                                                 vtparent_id=vtparent_id,
                                                 vtpos=vtpos,
                                                 vtmid=vtmid,
                                                 pos=pos,
                                                 type=type,
                                                 val=val,
                                                 minVal=minVal,
                                                 maxVal=maxVal,
                                                 stepSize=stepSize,
                                                 strvaluelist=strvaluelist,
                                                 widget=widget,
                                                 seq=seq,
                                                 parent=parent,
                                                 id=id)
            mashup_component.db_mashup_alias = mashup_alias
            mashup_component.db_entity_id = entity_id
            mashup_component.db_entity_type = entity_type
            mashup_component.is_dirty = False
            res[('mashup_component', id)] = mashup_component
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'vtid', 'vttype', 'vtparent_type', 'vtparent_id', 'vtpos', 'vtmid', 'pos', 'type', 'val', 'minVal', 'maxVal', 'stepSize', 'strvaluelist', 'widget', 'seq', 'parent', 'alias_id', 'entity_id', 'entity_type']
        table = 'mashup_component'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            vtid = self.convertFromDB(row[1], 'long', 'int')
            vttype = self.convertFromDB(row[2], 'str', 'varchar(255)')
            vtparent_type = self.convertFromDB(row[3], 'str', 'char(32)')
            vtparent_id = self.convertFromDB(row[4], 'long', 'int')
            vtpos = self.convertFromDB(row[5], 'long', 'int')
            vtmid = self.convertFromDB(row[6], 'long', 'int')
            pos = self.convertFromDB(row[7], 'long', 'int')
            type = self.convertFromDB(row[8], 'str', 'varchar(255)')
            val = self.convertFromDB(row[9], 'str', 'mediumtext')
            minVal = self.convertFromDB(row[10], 'str', 'varchar(255)')
            maxVal = self.convertFromDB(row[11], 'str', 'varchar(255)')
            stepSize = self.convertFromDB(row[12], 'str', 'varchar(255)')
            strvaluelist = self.convertFromDB(row[13], 'str', 'mediumtext')
            widget = self.convertFromDB(row[14], 'str', 'varchar(255)')
            seq = self.convertFromDB(row[15], 'int', 'int')
            parent = self.convertFromDB(row[16], 'str', 'varchar(255)')
            mashup_alias = self.convertFromDB(row[17], 'long', 'int')
            entity_id = self.convertFromDB(row[18], 'long', 'int')
            entity_type = self.convertFromDB(row[19], 'str', 'char(16)')
            
            mashup_component = DBMashupComponent(vtid=vtid,
                                                 vttype=vttype,
                                                 vtparent_type=vtparent_type,
                                                 vtparent_id=vtparent_id,
                                                 vtpos=vtpos,
                                                 vtmid=vtmid,
                                                 pos=pos,
                                                 type=type,
                                                 val=val,
                                                 minVal=minVal,
                                                 maxVal=maxVal,
                                                 stepSize=stepSize,
                                                 strvaluelist=strvaluelist,
                                                 widget=widget,
                                                 seq=seq,
                                                 parent=parent,
                                                 id=id)
            mashup_component.db_mashup_alias = mashup_alias
            mashup_component.db_entity_id = entity_id
            mashup_component.db_entity_type = entity_type
            mashup_component.is_dirty = False
            res[('mashup_component', id)] = mashup_component
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('mashup_alias', obj.db_mashup_alias) in all_objects:
            p = all_objects[('mashup_alias', obj.db_mashup_alias)]
            p.db_add_component(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'vtid', 'vttype', 'vtparent_type', 'vtparent_id', 'vtpos', 'vtmid', 'pos', 'type', 'val', 'minVal', 'maxVal', 'stepSize', 'strvaluelist', 'widget', 'seq', 'parent', 'alias_id', 'entity_id', 'entity_type']
        table = 'mashup_component'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_vtid') and obj.db_vtid is not None:
            columnMap['vtid'] = \
                self.convertToDB(obj.db_vtid, 'long', 'int')
        if hasattr(obj, 'db_vttype') and obj.db_vttype is not None:
            columnMap['vttype'] = \
                self.convertToDB(obj.db_vttype, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vtparent_type') and obj.db_vtparent_type is not None:
            columnMap['vtparent_type'] = \
                self.convertToDB(obj.db_vtparent_type, 'str', 'char(32)')
        if hasattr(obj, 'db_vtparent_id') and obj.db_vtparent_id is not None:
            columnMap['vtparent_id'] = \
                self.convertToDB(obj.db_vtparent_id, 'long', 'int')
        if hasattr(obj, 'db_vtpos') and obj.db_vtpos is not None:
            columnMap['vtpos'] = \
                self.convertToDB(obj.db_vtpos, 'long', 'int')
        if hasattr(obj, 'db_vtmid') and obj.db_vtmid is not None:
            columnMap['vtmid'] = \
                self.convertToDB(obj.db_vtmid, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_val') and obj.db_val is not None:
            columnMap['val'] = \
                self.convertToDB(obj.db_val, 'str', 'mediumtext')
        if hasattr(obj, 'db_minVal') and obj.db_minVal is not None:
            columnMap['minVal'] = \
                self.convertToDB(obj.db_minVal, 'str', 'varchar(255)')
        if hasattr(obj, 'db_maxVal') and obj.db_maxVal is not None:
            columnMap['maxVal'] = \
                self.convertToDB(obj.db_maxVal, 'str', 'varchar(255)')
        if hasattr(obj, 'db_stepSize') and obj.db_stepSize is not None:
            columnMap['stepSize'] = \
                self.convertToDB(obj.db_stepSize, 'str', 'varchar(255)')
        if hasattr(obj, 'db_strvaluelist') and obj.db_strvaluelist is not None:
            columnMap['strvaluelist'] = \
                self.convertToDB(obj.db_strvaluelist, 'str', 'mediumtext')
        if hasattr(obj, 'db_widget') and obj.db_widget is not None:
            columnMap['widget'] = \
                self.convertToDB(obj.db_widget, 'str', 'varchar(255)')
        if hasattr(obj, 'db_seq') and obj.db_seq is not None:
            columnMap['seq'] = \
                self.convertToDB(obj.db_seq, 'int', 'int')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent'] = \
                self.convertToDB(obj.db_parent, 'str', 'varchar(255)')
        if hasattr(obj, 'db_mashup_alias') and obj.db_mashup_alias is not None:
            columnMap['alias_id'] = \
                self.convertToDB(obj.db_mashup_alias, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'vtid', 'vttype', 'vtparent_type', 'vtparent_id', 'vtpos', 'vtmid', 'pos', 'type', 'val', 'minVal', 'maxVal', 'stepSize', 'strvaluelist', 'widget', 'seq', 'parent', 'alias_id', 'entity_id', 'entity_type']
        table = 'mashup_component'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_vtid') and obj.db_vtid is not None:
            columnMap['vtid'] = \
                self.convertToDB(obj.db_vtid, 'long', 'int')
        if hasattr(obj, 'db_vttype') and obj.db_vttype is not None:
            columnMap['vttype'] = \
                self.convertToDB(obj.db_vttype, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vtparent_type') and obj.db_vtparent_type is not None:
            columnMap['vtparent_type'] = \
                self.convertToDB(obj.db_vtparent_type, 'str', 'char(32)')
        if hasattr(obj, 'db_vtparent_id') and obj.db_vtparent_id is not None:
            columnMap['vtparent_id'] = \
                self.convertToDB(obj.db_vtparent_id, 'long', 'int')
        if hasattr(obj, 'db_vtpos') and obj.db_vtpos is not None:
            columnMap['vtpos'] = \
                self.convertToDB(obj.db_vtpos, 'long', 'int')
        if hasattr(obj, 'db_vtmid') and obj.db_vtmid is not None:
            columnMap['vtmid'] = \
                self.convertToDB(obj.db_vtmid, 'long', 'int')
        if hasattr(obj, 'db_pos') and obj.db_pos is not None:
            columnMap['pos'] = \
                self.convertToDB(obj.db_pos, 'long', 'int')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_val') and obj.db_val is not None:
            columnMap['val'] = \
                self.convertToDB(obj.db_val, 'str', 'mediumtext')
        if hasattr(obj, 'db_minVal') and obj.db_minVal is not None:
            columnMap['minVal'] = \
                self.convertToDB(obj.db_minVal, 'str', 'varchar(255)')
        if hasattr(obj, 'db_maxVal') and obj.db_maxVal is not None:
            columnMap['maxVal'] = \
                self.convertToDB(obj.db_maxVal, 'str', 'varchar(255)')
        if hasattr(obj, 'db_stepSize') and obj.db_stepSize is not None:
            columnMap['stepSize'] = \
                self.convertToDB(obj.db_stepSize, 'str', 'varchar(255)')
        if hasattr(obj, 'db_strvaluelist') and obj.db_strvaluelist is not None:
            columnMap['strvaluelist'] = \
                self.convertToDB(obj.db_strvaluelist, 'str', 'mediumtext')
        if hasattr(obj, 'db_widget') and obj.db_widget is not None:
            columnMap['widget'] = \
                self.convertToDB(obj.db_widget, 'str', 'varchar(255)')
        if hasattr(obj, 'db_seq') and obj.db_seq is not None:
            columnMap['seq'] = \
                self.convertToDB(obj.db_seq, 'int', 'int')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent'] = \
                self.convertToDB(obj.db_parent, 'str', 'varchar(255)')
        if hasattr(obj, 'db_mashup_alias') and obj.db_mashup_alias is not None:
            columnMap['alias_id'] = \
                self.convertToDB(obj.db_mashup_alias, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'mashup_component'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBMashupSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'mashup'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'version', 'type', 'vtid', 'layout', 'geometry', 'has_seq', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            version = self.convertFromDB(row[2], 'long', 'int')
            type = self.convertFromDB(row[3], 'str', 'varchar(255)')
            vtid = self.convertFromDB(row[4], 'long', 'int')
            layout = self.convertFromDB(row[5], 'str', 'mediumtext')
            geometry = self.convertFromDB(row[6], 'str', 'mediumtext')
            has_seq = self.convertFromDB(row[7], 'int', 'int')
            parent = self.convertFromDB(row[8], 'long', 'int')
            entity_id = self.convertFromDB(row[9], 'long', 'int')
            entity_type = self.convertFromDB(row[10], 'str', 'char(16)')
            
            mashup = DBMashup(name=name,
                              version=version,
                              type=type,
                              vtid=vtid,
                              layout=layout,
                              geometry=geometry,
                              has_seq=has_seq,
                              id=id)
            mashup.db_parent = parent
            mashup.db_entity_id = entity_id
            mashup.db_entity_type = entity_type
            mashup.is_dirty = False
            res[('mashup', id)] = mashup
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'version', 'type', 'vtid', 'layout', 'geometry', 'has_seq', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            version = self.convertFromDB(row[2], 'long', 'int')
            type = self.convertFromDB(row[3], 'str', 'varchar(255)')
            vtid = self.convertFromDB(row[4], 'long', 'int')
            layout = self.convertFromDB(row[5], 'str', 'mediumtext')
            geometry = self.convertFromDB(row[6], 'str', 'mediumtext')
            has_seq = self.convertFromDB(row[7], 'int', 'int')
            parent = self.convertFromDB(row[8], 'long', 'int')
            entity_id = self.convertFromDB(row[9], 'long', 'int')
            entity_type = self.convertFromDB(row[10], 'str', 'char(16)')
            
            mashup = DBMashup(name=name,
                              version=version,
                              type=type,
                              vtid=vtid,
                              layout=layout,
                              geometry=geometry,
                              has_seq=has_seq,
                              id=id)
            mashup.db_parent = parent
            mashup.db_entity_id = entity_id
            mashup.db_entity_type = entity_type
            mashup.is_dirty = False
            res[('mashup', id)] = mashup
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('mashup_action', obj.db_parent) in all_objects:
            p = all_objects[('mashup_action', obj.db_parent)]
            p.db_add_mashup(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'version', 'type', 'vtid', 'layout', 'geometry', 'has_seq', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'long', 'int')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vtid') and obj.db_vtid is not None:
            columnMap['vtid'] = \
                self.convertToDB(obj.db_vtid, 'long', 'int')
        if hasattr(obj, 'db_layout') and obj.db_layout is not None:
            columnMap['layout'] = \
                self.convertToDB(obj.db_layout, 'str', 'mediumtext')
        if hasattr(obj, 'db_geometry') and obj.db_geometry is not None:
            columnMap['geometry'] = \
                self.convertToDB(obj.db_geometry, 'str', 'mediumtext')
        if hasattr(obj, 'db_has_seq') and obj.db_has_seq is not None:
            columnMap['has_seq'] = \
                self.convertToDB(obj.db_has_seq, 'int', 'int')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'version', 'type', 'vtid', 'layout', 'geometry', 'has_seq', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'long', 'int')
        if hasattr(obj, 'db_type') and obj.db_type is not None:
            columnMap['type'] = \
                self.convertToDB(obj.db_type, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vtid') and obj.db_vtid is not None:
            columnMap['vtid'] = \
                self.convertToDB(obj.db_vtid, 'long', 'int')
        if hasattr(obj, 'db_layout') and obj.db_layout is not None:
            columnMap['layout'] = \
                self.convertToDB(obj.db_layout, 'str', 'mediumtext')
        if hasattr(obj, 'db_geometry') and obj.db_geometry is not None:
            columnMap['geometry'] = \
                self.convertToDB(obj.db_geometry, 'str', 'mediumtext')
        if hasattr(obj, 'db_has_seq') and obj.db_has_seq is not None:
            columnMap['has_seq'] = \
                self.convertToDB(obj.db_has_seq, 'int', 'int')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_aliases:
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'mashup'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBMachineSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'machine'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'os', 'architecture', 'processor', 'ram', 'vt_id', 'log_id', 'entity_id', 'entity_type']
        table = 'machine'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            os = self.convertFromDB(row[2], 'str', 'varchar(255)')
            architecture = self.convertFromDB(row[3], 'str', 'varchar(255)')
            processor = self.convertFromDB(row[4], 'str', 'varchar(255)')
            ram = self.convertFromDB(row[5], 'int', 'bigint')
            vistrailId = self.convertFromDB(row[6], 'long', 'int')
            workflow_exec = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            machine = DBMachine(name=name,
                                os=os,
                                architecture=architecture,
                                processor=processor,
                                ram=ram,
                                id=id)
            machine.db_vistrailId = vistrailId
            machine.db_workflow_exec = workflow_exec
            machine.db_entity_id = entity_id
            machine.db_entity_type = entity_type
            machine.is_dirty = False
            res[('machine', id)] = machine
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'os', 'architecture', 'processor', 'ram', 'vt_id', 'log_id', 'entity_id', 'entity_type']
        table = 'machine'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'varchar(255)')
            os = self.convertFromDB(row[2], 'str', 'varchar(255)')
            architecture = self.convertFromDB(row[3], 'str', 'varchar(255)')
            processor = self.convertFromDB(row[4], 'str', 'varchar(255)')
            ram = self.convertFromDB(row[5], 'int', 'bigint')
            vistrailId = self.convertFromDB(row[6], 'long', 'int')
            workflow_exec = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            machine = DBMachine(name=name,
                                os=os,
                                architecture=architecture,
                                processor=processor,
                                ram=ram,
                                id=id)
            machine.db_vistrailId = vistrailId
            machine.db_workflow_exec = workflow_exec
            machine.db_entity_id = entity_id
            machine.db_entity_type = entity_type
            machine.is_dirty = False
            res[('machine', id)] = machine
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('workflow_exec', obj.db_workflow_exec) in all_objects:
            p = all_objects[('workflow_exec', obj.db_workflow_exec)]
            p.db_add_machine(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'os', 'architecture', 'processor', 'ram', 'vt_id', 'log_id', 'entity_id', 'entity_type']
        table = 'machine'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_os') and obj.db_os is not None:
            columnMap['os'] = \
                self.convertToDB(obj.db_os, 'str', 'varchar(255)')
        if hasattr(obj, 'db_architecture') and obj.db_architecture is not None:
            columnMap['architecture'] = \
                self.convertToDB(obj.db_architecture, 'str', 'varchar(255)')
        if hasattr(obj, 'db_processor') and obj.db_processor is not None:
            columnMap['processor'] = \
                self.convertToDB(obj.db_processor, 'str', 'varchar(255)')
        if hasattr(obj, 'db_ram') and obj.db_ram is not None:
            columnMap['ram'] = \
                self.convertToDB(obj.db_ram, 'int', 'bigint')
        if hasattr(obj, 'db_vistrailId') and obj.db_vistrailId is not None:
            columnMap['vt_id'] = \
                self.convertToDB(obj.db_vistrailId, 'long', 'int')
        if hasattr(obj, 'db_workflow_exec') and obj.db_workflow_exec is not None:
            columnMap['log_id'] = \
                self.convertToDB(obj.db_workflow_exec, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'os', 'architecture', 'processor', 'ram', 'vt_id', 'log_id', 'entity_id', 'entity_type']
        table = 'machine'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_os') and obj.db_os is not None:
            columnMap['os'] = \
                self.convertToDB(obj.db_os, 'str', 'varchar(255)')
        if hasattr(obj, 'db_architecture') and obj.db_architecture is not None:
            columnMap['architecture'] = \
                self.convertToDB(obj.db_architecture, 'str', 'varchar(255)')
        if hasattr(obj, 'db_processor') and obj.db_processor is not None:
            columnMap['processor'] = \
                self.convertToDB(obj.db_processor, 'str', 'varchar(255)')
        if hasattr(obj, 'db_ram') and obj.db_ram is not None:
            columnMap['ram'] = \
                self.convertToDB(obj.db_ram, 'int', 'bigint')
        if hasattr(obj, 'db_vistrailId') and obj.db_vistrailId is not None:
            columnMap['vt_id'] = \
                self.convertToDB(obj.db_vistrailId, 'long', 'int')
        if hasattr(obj, 'db_workflow_exec') and obj.db_workflow_exec is not None:
            columnMap['log_id'] = \
                self.convertToDB(obj.db_workflow_exec, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'machine'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBOtherSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'other'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'okey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'other'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            other = DBOther(key=key,
                            value=value,
                            id=id)
            other.db_parentType = parentType
            other.db_entity_id = entity_id
            other.db_entity_type = entity_type
            other.db_parent = parent
            other.is_dirty = False
            res[('other', id)] = other
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'okey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'other'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            other = DBOther(key=key,
                            value=value,
                            id=id)
            other.db_parentType = parentType
            other.db_entity_id = entity_id
            other.db_entity_type = entity_type
            other.db_parent = parent
            other.is_dirty = False
            res[('other', id)] = other
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_other(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'okey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'other'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['okey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'okey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'other'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['okey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'other'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBAbstractionSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'abstraction'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'internal_version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'abstraction'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            cache = self.convertFromDB(row[1], 'int', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package = self.convertFromDB(row[4], 'str', 'varchar(511)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            internal_version = self.convertFromDB(row[6], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[7], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            parent = self.convertFromDB(row[10], 'long', 'long')
            
            abstraction = DBAbstraction(cache=cache,
                                        name=name,
                                        namespace=namespace,
                                        package=package,
                                        version=version,
                                        internal_version=internal_version,
                                        id=id)
            abstraction.db_parentType = parentType
            abstraction.db_entity_id = entity_id
            abstraction.db_entity_type = entity_type
            abstraction.db_parent = parent
            abstraction.is_dirty = False
            res[('abstraction', id)] = abstraction
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'internal_version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'abstraction'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            cache = self.convertFromDB(row[1], 'int', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            namespace = self.convertFromDB(row[3], 'str', 'varchar(255)')
            package = self.convertFromDB(row[4], 'str', 'varchar(511)')
            version = self.convertFromDB(row[5], 'str', 'varchar(255)')
            internal_version = self.convertFromDB(row[6], 'str', 'varchar(255)')
            parentType = self.convertFromDB(row[7], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            parent = self.convertFromDB(row[10], 'long', 'long')
            
            abstraction = DBAbstraction(cache=cache,
                                        name=name,
                                        namespace=namespace,
                                        package=package,
                                        version=version,
                                        internal_version=internal_version,
                                        id=id)
            abstraction.db_parentType = parentType
            abstraction.db_entity_id = entity_id
            abstraction.db_entity_type = entity_type
            abstraction.db_parent = parent
            abstraction.is_dirty = False
            res[('abstraction', id)] = abstraction
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_module(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'internal_version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'abstraction'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_cache') and obj.db_cache is not None:
            columnMap['cache'] = \
                self.convertToDB(obj.db_cache, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(511)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_internal_version') and obj.db_internal_version is not None:
            columnMap['internal_version'] = \
                self.convertToDB(obj.db_internal_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'cache', 'name', 'namespace', 'package', 'version', 'internal_version', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'abstraction'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_cache') and obj.db_cache is not None:
            columnMap['cache'] = \
                self.convertToDB(obj.db_cache, 'int', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_namespace') and obj.db_namespace is not None:
            columnMap['namespace'] = \
                self.convertToDB(obj.db_namespace, 'str', 'varchar(255)')
        if hasattr(obj, 'db_package') and obj.db_package is not None:
            columnMap['package'] = \
                self.convertToDB(obj.db_package, 'str', 'varchar(511)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_internal_version') and obj.db_internal_version is not None:
            columnMap['internal_version'] = \
                self.convertToDB(obj.db_internal_version, 'str', 'varchar(255)')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        if obj.db_location is not None:
            child = obj.db_location
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_functions:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_controlParameters:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'abstraction'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBMashuptrailSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'mashuptrail'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'name', 'version', 'vt_version', 'last_modified', 'entity_type']
        table = 'mashuptrail'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'char(36)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            vtVersion = self.convertFromDB(row[3], 'long', 'int')
            last_modified = self.convertFromDB(row[4], 'datetime', 'datetime')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            
            mashuptrail = DBMashuptrail(name=name,
                                        version=version,
                                        vtVersion=vtVersion,
                                        last_modified=last_modified,
                                        id=id)
            mashuptrail.db_entity_type = entity_type
            mashuptrail.is_dirty = False
            res[('mashuptrail', id)] = mashuptrail
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'name', 'version', 'vt_version', 'last_modified', 'entity_type']
        table = 'mashuptrail'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            name = self.convertFromDB(row[1], 'str', 'char(36)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            vtVersion = self.convertFromDB(row[3], 'long', 'int')
            last_modified = self.convertFromDB(row[4], 'datetime', 'datetime')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            
            mashuptrail = DBMashuptrail(name=name,
                                        version=version,
                                        vtVersion=vtVersion,
                                        last_modified=last_modified,
                                        id=id)
            mashuptrail.db_entity_type = entity_type
            mashuptrail.is_dirty = False
            res[('mashuptrail', id)] = mashuptrail
        return res

    def from_sql_fast(self, obj, all_objects):
        pass
    
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'name', 'version', 'vt_version', 'last_modified', 'entity_type']
        table = 'mashuptrail'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'char(36)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_vtVersion') and obj.db_vtVersion is not None:
            columnMap['vt_version'] = \
                self.convertToDB(obj.db_vtVersion, 'long', 'int')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'name', 'version', 'vt_version', 'last_modified', 'entity_type']
        table = 'mashuptrail'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'char(36)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_vtVersion') and obj.db_vtVersion is not None:
            columnMap['vt_version'] = \
                self.convertToDB(obj.db_vtVersion, 'long', 'int')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_actions:
            child.db_mashuptrail = obj.db_id
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_actionAnnotations:
            child.db_mashuptrail = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'mashuptrail'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBRegistrySQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'registry'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'entity_type', 'version', 'root_descriptor_id', 'name', 'last_modified']
        table = 'registry'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_type = self.convertFromDB(row[1], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            root_descriptor_id = self.convertFromDB(row[3], 'long', 'int')
            name = self.convertFromDB(row[4], 'str', 'varchar(255)')
            last_modified = self.convertFromDB(row[5], 'datetime', 'datetime')
            
            registry = DBRegistry(entity_type=entity_type,
                                  version=version,
                                  root_descriptor_id=root_descriptor_id,
                                  name=name,
                                  last_modified=last_modified,
                                  id=id)
            registry.is_dirty = False
            res[('registry', id)] = registry
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'entity_type', 'version', 'root_descriptor_id', 'name', 'last_modified']
        table = 'registry'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            global_props['entity_id'] = self.convertToDB(id, 'long', 'int')
            entity_type = self.convertFromDB(row[1], 'str', 'char(16)')
            global_props['entity_type'] = self.convertToDB(entity_type, 'str', 'char(16)')
            version = self.convertFromDB(row[2], 'str', 'char(16)')
            root_descriptor_id = self.convertFromDB(row[3], 'long', 'int')
            name = self.convertFromDB(row[4], 'str', 'varchar(255)')
            last_modified = self.convertFromDB(row[5], 'datetime', 'datetime')
            
            registry = DBRegistry(entity_type=entity_type,
                                  version=version,
                                  root_descriptor_id=root_descriptor_id,
                                  name=name,
                                  last_modified=last_modified,
                                  id=id)
            registry.is_dirty = False
            res[('registry', id)] = registry
        return res

    def from_sql_fast(self, obj, all_objects):
        pass
    
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'entity_type', 'version', 'root_descriptor_id', 'name', 'last_modified']
        table = 'registry'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_root_descriptor_id') and obj.db_root_descriptor_id is not None:
            columnMap['root_descriptor_id'] = \
                self.convertToDB(obj.db_root_descriptor_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'entity_type', 'version', 'root_descriptor_id', 'name', 'last_modified']
        table = 'registry'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_version') and obj.db_version is not None:
            columnMap['version'] = \
                self.convertToDB(obj.db_version, 'str', 'char(16)')
        if hasattr(obj, 'db_root_descriptor_id') and obj.db_root_descriptor_id is not None:
            columnMap['root_descriptor_id'] = \
                self.convertToDB(obj.db_root_descriptor_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_last_modified') and obj.db_last_modified is not None:
            columnMap['last_modified'] = \
                self.convertToDB(obj.db_last_modified, 'datetime', 'datetime')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        if obj.db_id is None:
            obj.db_id = lastId
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            global_props['entity_type'] = self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            global_props['entity_id'] = self.convertToDB(obj.db_id, 'long', 'int')
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_packages:
            child.db_registry = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'registry'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBAnnotationSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'annotation'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'akey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'annotation'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'mediumtext')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            annotation = DBAnnotation(key=key,
                                      value=value,
                                      id=id)
            annotation.db_parentType = parentType
            annotation.db_entity_id = entity_id
            annotation.db_entity_type = entity_type
            annotation.db_parent = parent
            annotation.is_dirty = False
            res[('annotation', id)] = annotation
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'akey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'annotation'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'mediumtext')
            parentType = self.convertFromDB(row[3], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[4], 'long', 'int')
            entity_type = self.convertFromDB(row[5], 'str', 'char(16)')
            parent = self.convertFromDB(row[6], 'long', 'long')
            
            annotation = DBAnnotation(key=key,
                                      value=value,
                                      id=id)
            annotation.db_parentType = parentType
            annotation.db_entity_id = entity_id
            annotation.db_entity_type = entity_type
            annotation.db_parent = parent
            annotation.is_dirty = False
            res[('annotation', id)] = annotation
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'vistrail':
            p = all_objects[('vistrail', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'workflow':
            p = all_objects[('workflow', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'module':
            p = all_objects[('module', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'workflow_exec':
            p = all_objects[('workflow_exec', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'module_exec':
            p = all_objects[('module_exec', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'group_exec':
            p = all_objects[('group_exec', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'add':
            p = all_objects[('add', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'change':
            p = all_objects[('change', obj.db_parent)]
            p.db_add_data(obj)
        elif obj.db_parentType == 'action':
            p = all_objects[('action', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'abstraction':
            p = all_objects[('abstraction', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'mashuptrail':
            p = all_objects[('mashuptrail', obj.db_parent)]
            p.db_add_annotation(obj)
        elif obj.db_parentType == 'group':
            p = all_objects[('group', obj.db_parent)]
            p.db_add_annotation(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'akey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['akey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'mediumtext')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'akey', 'value', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['akey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'mediumtext')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBParameterExplorationSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'parameter_exploration'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'action_id', 'name', 'date', 'user', 'dims', 'layout', 'parent_id', 'entity_id', 'entity_type']
        table = 'parameter_exploration'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            action_id = self.convertFromDB(row[1], 'long', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            date = self.convertFromDB(row[3], 'datetime', 'datetime')
            user = self.convertFromDB(row[4], 'str', 'varchar(255)')
            dims = self.convertFromDB(row[5], 'str', 'varchar(255)')
            layout = self.convertFromDB(row[6], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            parameter_exploration = DBParameterExploration(action_id=action_id,
                                                           name=name,
                                                           date=date,
                                                           user=user,
                                                           dims=dims,
                                                           layout=layout,
                                                           id=id)
            parameter_exploration.db_vistrail = vistrail
            parameter_exploration.db_entity_id = entity_id
            parameter_exploration.db_entity_type = entity_type
            parameter_exploration.is_dirty = False
            res[('parameter_exploration', id)] = parameter_exploration
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'action_id', 'name', 'date', 'user', 'dims', 'layout', 'parent_id', 'entity_id', 'entity_type']
        table = 'parameter_exploration'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            action_id = self.convertFromDB(row[1], 'long', 'int')
            name = self.convertFromDB(row[2], 'str', 'varchar(255)')
            date = self.convertFromDB(row[3], 'datetime', 'datetime')
            user = self.convertFromDB(row[4], 'str', 'varchar(255)')
            dims = self.convertFromDB(row[5], 'str', 'varchar(255)')
            layout = self.convertFromDB(row[6], 'str', 'varchar(255)')
            vistrail = self.convertFromDB(row[7], 'long', 'int')
            entity_id = self.convertFromDB(row[8], 'long', 'int')
            entity_type = self.convertFromDB(row[9], 'str', 'char(16)')
            
            parameter_exploration = DBParameterExploration(action_id=action_id,
                                                           name=name,
                                                           date=date,
                                                           user=user,
                                                           dims=dims,
                                                           layout=layout,
                                                           id=id)
            parameter_exploration.db_vistrail = vistrail
            parameter_exploration.db_entity_id = entity_id
            parameter_exploration.db_entity_type = entity_type
            parameter_exploration.is_dirty = False
            res[('parameter_exploration', id)] = parameter_exploration
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('vistrail', obj.db_vistrail) in all_objects:
            p = all_objects[('vistrail', obj.db_vistrail)]
            p.db_add_parameter_exploration(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'action_id', 'name', 'date', 'user', 'dims', 'layout', 'parent_id', 'entity_id', 'entity_type']
        table = 'parameter_exploration'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_action_id') and obj.db_action_id is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_dims') and obj.db_dims is not None:
            columnMap['dims'] = \
                self.convertToDB(obj.db_dims, 'str', 'varchar(255)')
        if hasattr(obj, 'db_layout') and obj.db_layout is not None:
            columnMap['layout'] = \
                self.convertToDB(obj.db_layout, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'action_id', 'name', 'date', 'user', 'dims', 'layout', 'parent_id', 'entity_id', 'entity_type']
        table = 'parameter_exploration'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_action_id') and obj.db_action_id is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action_id, 'long', 'int')
        if hasattr(obj, 'db_name') and obj.db_name is not None:
            columnMap['name'] = \
                self.convertToDB(obj.db_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_dims') and obj.db_dims is not None:
            columnMap['dims'] = \
                self.convertToDB(obj.db_dims, 'str', 'varchar(255)')
        if hasattr(obj, 'db_layout') and obj.db_layout is not None:
            columnMap['layout'] = \
                self.convertToDB(obj.db_layout, 'str', 'varchar(255)')
        if hasattr(obj, 'db_vistrail') and obj.db_vistrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_vistrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_functions:
            child.db_parameter_exploration = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'parameter_exploration'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBMashupActionAnnotationSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'mashup_action_annotation'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action_annotation'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'varchar(8191)')
            action_id = self.convertFromDB(row[3], 'long', 'int')
            date = self.convertFromDB(row[4], 'datetime', 'datetime')
            user = self.convertFromDB(row[5], 'str', 'varchar(255)')
            mashuptrail = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            mashup_actionAnnotation = DBMashupActionAnnotation(key=key,
                                                               value=value,
                                                               action_id=action_id,
                                                               date=date,
                                                               user=user,
                                                               id=id)
            mashup_actionAnnotation.db_mashuptrail = mashuptrail
            mashup_actionAnnotation.db_entity_id = entity_id
            mashup_actionAnnotation.db_entity_type = entity_type
            mashup_actionAnnotation.is_dirty = False
            res[('mashup_actionAnnotation', id)] = mashup_actionAnnotation
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action_annotation'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            key = self.convertFromDB(row[1], 'str', 'varchar(255)')
            value = self.convertFromDB(row[2], 'str', 'varchar(8191)')
            action_id = self.convertFromDB(row[3], 'long', 'int')
            date = self.convertFromDB(row[4], 'datetime', 'datetime')
            user = self.convertFromDB(row[5], 'str', 'varchar(255)')
            mashuptrail = self.convertFromDB(row[6], 'long', 'int')
            entity_id = self.convertFromDB(row[7], 'long', 'int')
            entity_type = self.convertFromDB(row[8], 'str', 'char(16)')
            
            mashup_actionAnnotation = DBMashupActionAnnotation(key=key,
                                                               value=value,
                                                               action_id=action_id,
                                                               date=date,
                                                               user=user,
                                                               id=id)
            mashup_actionAnnotation.db_mashuptrail = mashuptrail
            mashup_actionAnnotation.db_entity_id = entity_id
            mashup_actionAnnotation.db_entity_type = entity_type
            mashup_actionAnnotation.is_dirty = False
            res[('mashup_actionAnnotation', id)] = mashup_actionAnnotation
        return res

    def from_sql_fast(self, obj, all_objects):
        if ('mashuptrail', obj.db_mashuptrail) in all_objects:
            p = all_objects[('mashuptrail', obj.db_mashuptrail)]
            p.db_add_actionAnnotation(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action_annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['akey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_action_id') and obj.db_action_id is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action_id, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_mashuptrail') and obj.db_mashuptrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_mashuptrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'akey', 'value', 'action_id', 'date', 'user', 'parent_id', 'entity_id', 'entity_type']
        table = 'mashup_action_annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_key') and obj.db_key is not None:
            columnMap['akey'] = \
                self.convertToDB(obj.db_key, 'str', 'varchar(255)')
        if hasattr(obj, 'db_value') and obj.db_value is not None:
            columnMap['value'] = \
                self.convertToDB(obj.db_value, 'str', 'varchar(8191)')
        if hasattr(obj, 'db_action_id') and obj.db_action_id is not None:
            columnMap['action_id'] = \
                self.convertToDB(obj.db_action_id, 'long', 'int')
        if hasattr(obj, 'db_date') and obj.db_date is not None:
            columnMap['date'] = \
                self.convertToDB(obj.db_date, 'datetime', 'datetime')
        if hasattr(obj, 'db_user') and obj.db_user is not None:
            columnMap['user'] = \
                self.convertToDB(obj.db_user, 'str', 'varchar(255)')
        if hasattr(obj, 'db_mashuptrail') and obj.db_mashuptrail is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_mashuptrail, 'long', 'int')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        pass
    
    def delete_sql_column(self, db, obj, global_props):
        table = 'mashup_action_annotation'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

class DBModuleExecSQLDAOBase(SQLDAO):

    def __init__(self, daoList):
        self.daoList = daoList
        self.table = 'module_exec'

    def getDao(self, dao):
        return self.daoList[dao]

    def get_sql_columns(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'module_name', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module_exec'
        whereMap = global_props
        orderBy = 'id'

        dbCommand = self.createSQLSelect(table, columns, whereMap, orderBy, lock)
        data = self.executeSQL(db, dbCommand, True)
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            cached = self.convertFromDB(row[3], 'int', 'int')
            module_id = self.convertFromDB(row[4], 'long', 'int')
            module_name = self.convertFromDB(row[5], 'str', 'varchar(255)')
            completed = self.convertFromDB(row[6], 'int', 'int')
            error = self.convertFromDB(row[7], 'str', 'varchar(1023)')
            machine_id = self.convertFromDB(row[8], 'long', 'int')
            parentType = self.convertFromDB(row[9], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[10], 'long', 'int')
            entity_type = self.convertFromDB(row[11], 'str', 'char(16)')
            parent = self.convertFromDB(row[12], 'long', 'long')
            
            module_exec = DBModuleExec(ts_start=ts_start,
                                       ts_end=ts_end,
                                       cached=cached,
                                       module_id=module_id,
                                       module_name=module_name,
                                       completed=completed,
                                       error=error,
                                       machine_id=machine_id,
                                       id=id)
            module_exec.db_parentType = parentType
            module_exec.db_entity_id = entity_id
            module_exec.db_entity_type = entity_type
            module_exec.db_parent = parent
            module_exec.is_dirty = False
            res[('module_exec', id)] = module_exec
        return res

    def get_sql_select(self, db, global_props,lock=False):
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'module_name', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module_exec'
        whereMap = global_props
        orderBy = 'id'
        return self.createSQLSelect(table, columns, whereMap, orderBy, lock)

    def process_sql_columns(self, data, global_props):
        res = {}
        for row in data:
            id = self.convertFromDB(row[0], 'long', 'int')
            ts_start = self.convertFromDB(row[1], 'datetime', 'datetime')
            ts_end = self.convertFromDB(row[2], 'datetime', 'datetime')
            cached = self.convertFromDB(row[3], 'int', 'int')
            module_id = self.convertFromDB(row[4], 'long', 'int')
            module_name = self.convertFromDB(row[5], 'str', 'varchar(255)')
            completed = self.convertFromDB(row[6], 'int', 'int')
            error = self.convertFromDB(row[7], 'str', 'varchar(1023)')
            machine_id = self.convertFromDB(row[8], 'long', 'int')
            parentType = self.convertFromDB(row[9], 'str', 'char(32)')
            entity_id = self.convertFromDB(row[10], 'long', 'int')
            entity_type = self.convertFromDB(row[11], 'str', 'char(16)')
            parent = self.convertFromDB(row[12], 'long', 'long')
            
            module_exec = DBModuleExec(ts_start=ts_start,
                                       ts_end=ts_end,
                                       cached=cached,
                                       module_id=module_id,
                                       module_name=module_name,
                                       completed=completed,
                                       error=error,
                                       machine_id=machine_id,
                                       id=id)
            module_exec.db_parentType = parentType
            module_exec.db_entity_id = entity_id
            module_exec.db_entity_type = entity_type
            module_exec.db_parent = parent
            module_exec.is_dirty = False
            res[('module_exec', id)] = module_exec
        return res

    def from_sql_fast(self, obj, all_objects):
        if obj.db_parentType == 'workflow_exec':
            p = all_objects[('workflow_exec', obj.db_parent)]
            p.db_add_item_exec(obj)
        elif obj.db_parentType == 'group_exec':
            p = all_objects[('group_exec', obj.db_parent)]
            p.db_add_item_exec(obj)
        elif obj.db_parentType == 'loop_iteration':
            p = all_objects[('loop_iteration', obj.db_parent)]
            p.db_add_item_exec(obj)
        
    def set_sql_columns(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'module_name', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_cached') and obj.db_cached is not None:
            columnMap['cached'] = \
                self.convertToDB(obj.db_cached, 'int', 'int')
        if hasattr(obj, 'db_module_id') and obj.db_module_id is not None:
            columnMap['module_id'] = \
                self.convertToDB(obj.db_module_id, 'long', 'int')
        if hasattr(obj, 'db_module_name') and obj.db_module_name is not None:
            columnMap['module_name'] = \
                self.convertToDB(obj.db_module_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_error') and obj.db_error is not None:
            columnMap['error'] = \
                self.convertToDB(obj.db_error, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_machine_id') and obj.db_machine_id is not None:
            columnMap['machine_id'] = \
                self.convertToDB(obj.db_machine_id, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        lastId = self.executeSQL(db, dbCommand, False)
        
    def set_sql_command(self, db, obj, global_props, do_copy=True):
        if not do_copy and not obj.is_dirty:
            return None
        columns = ['id', 'ts_start', 'ts_end', 'cached', 'module_id', 'module_name', 'completed', 'error', 'machine_id', 'parent_type', 'entity_id', 'entity_type', 'parent_id']
        table = 'module_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        columnMap = {}
        if hasattr(obj, 'db_id') and obj.db_id is not None:
            columnMap['id'] = \
                self.convertToDB(obj.db_id, 'long', 'int')
        if hasattr(obj, 'db_ts_start') and obj.db_ts_start is not None:
            columnMap['ts_start'] = \
                self.convertToDB(obj.db_ts_start, 'datetime', 'datetime')
        if hasattr(obj, 'db_ts_end') and obj.db_ts_end is not None:
            columnMap['ts_end'] = \
                self.convertToDB(obj.db_ts_end, 'datetime', 'datetime')
        if hasattr(obj, 'db_cached') and obj.db_cached is not None:
            columnMap['cached'] = \
                self.convertToDB(obj.db_cached, 'int', 'int')
        if hasattr(obj, 'db_module_id') and obj.db_module_id is not None:
            columnMap['module_id'] = \
                self.convertToDB(obj.db_module_id, 'long', 'int')
        if hasattr(obj, 'db_module_name') and obj.db_module_name is not None:
            columnMap['module_name'] = \
                self.convertToDB(obj.db_module_name, 'str', 'varchar(255)')
        if hasattr(obj, 'db_completed') and obj.db_completed is not None:
            columnMap['completed'] = \
                self.convertToDB(obj.db_completed, 'int', 'int')
        if hasattr(obj, 'db_error') and obj.db_error is not None:
            columnMap['error'] = \
                self.convertToDB(obj.db_error, 'str', 'varchar(1023)')
        if hasattr(obj, 'db_machine_id') and obj.db_machine_id is not None:
            columnMap['machine_id'] = \
                self.convertToDB(obj.db_machine_id, 'long', 'int')
        if hasattr(obj, 'db_parentType') and obj.db_parentType is not None:
            columnMap['parent_type'] = \
                self.convertToDB(obj.db_parentType, 'str', 'char(32)')
        if hasattr(obj, 'db_entity_id') and obj.db_entity_id is not None:
            columnMap['entity_id'] = \
                self.convertToDB(obj.db_entity_id, 'long', 'int')
        if hasattr(obj, 'db_entity_type') and obj.db_entity_type is not None:
            columnMap['entity_type'] = \
                self.convertToDB(obj.db_entity_type, 'str', 'char(16)')
        if hasattr(obj, 'db_parent') and obj.db_parent is not None:
            columnMap['parent_id'] = \
                self.convertToDB(obj.db_parent, 'long', 'long')
        columnMap.update(global_props)

        if obj.is_new or do_copy:
            dbCommand = self.createSQLInsert(table, columnMap)
        else:
            dbCommand = self.createSQLUpdate(table, columnMap, whereMap)
        return dbCommand

    def set_sql_process(self, obj, global_props, lastId):
        pass

    def to_sql_fast(self, obj, do_copy=True):
        for child in obj.db_annotations:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        for child in obj.db_loop_execs:
            child.db_parentType = obj.vtType
            child.db_parent = obj.db_id
        
    def delete_sql_column(self, db, obj, global_props):
        table = 'module_exec'
        whereMap = {}
        whereMap.update(global_props)
        if obj.db_id is not None:
            keyStr = self.convertToDB(obj.db_id, 'long', 'int')
            whereMap['id'] = keyStr
        dbCommand = self.createSQLDelete(table, whereMap)
        self.executeSQL(db, dbCommand, False)

"""generated automatically by auto_dao.py"""

class SQLDAOListBase(dict):

    def __init__(self, daos=None):
        if daos is not None:
            dict.update(self, daos)

        if 'mashup_alias' not in self:
            self['mashup_alias'] = DBMashupAliasSQLDAOBase(self)
        if 'group' not in self:
            self['group'] = DBGroupSQLDAOBase(self)
        if 'add' not in self:
            self['add'] = DBAddSQLDAOBase(self)
        if 'group_exec' not in self:
            self['group_exec'] = DBGroupExecSQLDAOBase(self)
        if 'parameter' not in self:
            self['parameter'] = DBParameterSQLDAOBase(self)
        if 'vistrail' not in self:
            self['vistrail'] = DBVistrailSQLDAOBase(self)
        if 'module' not in self:
            self['module'] = DBModuleSQLDAOBase(self)
        if 'port' not in self:
            self['port'] = DBPortSQLDAOBase(self)
        if 'pe_function' not in self:
            self['pe_function'] = DBPEFunctionSQLDAOBase(self)
        if 'workflow' not in self:
            self['workflow'] = DBWorkflowSQLDAOBase(self)
        if 'mashup_action' not in self:
            self['mashup_action'] = DBMashupActionSQLDAOBase(self)
        if 'change' not in self:
            self['change'] = DBChangeSQLDAOBase(self)
        if 'package' not in self:
            self['package'] = DBPackageSQLDAOBase(self)
        if 'loop_exec' not in self:
            self['loop_exec'] = DBLoopExecSQLDAOBase(self)
        if 'connection' not in self:
            self['connection'] = DBConnectionSQLDAOBase(self)
        if 'action' not in self:
            self['action'] = DBActionSQLDAOBase(self)
        if 'portSpec' not in self:
            self['portSpec'] = DBPortSpecSQLDAOBase(self)
        if 'log' not in self:
            self['log'] = DBLogSQLDAOBase(self)
        if 'loop_iteration' not in self:
            self['loop_iteration'] = DBLoopIterationSQLDAOBase(self)
        if 'pe_parameter' not in self:
            self['pe_parameter'] = DBPEParameterSQLDAOBase(self)
        if 'workflow_exec' not in self:
            self['workflow_exec'] = DBWorkflowExecSQLDAOBase(self)
        if 'location' not in self:
            self['location'] = DBLocationSQLDAOBase(self)
        if 'function' not in self:
            self['function'] = DBFunctionSQLDAOBase(self)
        if 'actionAnnotation' not in self:
            self['actionAnnotation'] = DBActionAnnotationSQLDAOBase(self)
        if 'controlParameter' not in self:
            self['controlParameter'] = DBControlParameterSQLDAOBase(self)
        if 'plugin_data' not in self:
            self['plugin_data'] = DBPluginDataSQLDAOBase(self)
        if 'delete' not in self:
            self['delete'] = DBDeleteSQLDAOBase(self)
        if 'vistrailVariable' not in self:
            self['vistrailVariable'] = DBVistrailVariableSQLDAOBase(self)
        if 'module_descriptor' not in self:
            self['module_descriptor'] = DBModuleDescriptorSQLDAOBase(self)
        if 'tag' not in self:
            self['tag'] = DBTagSQLDAOBase(self)
        if 'portSpecItem' not in self:
            self['portSpecItem'] = DBPortSpecItemSQLDAOBase(self)
        if 'mashup_component' not in self:
            self['mashup_component'] = DBMashupComponentSQLDAOBase(self)
        if 'mashup' not in self:
            self['mashup'] = DBMashupSQLDAOBase(self)
        if 'machine' not in self:
            self['machine'] = DBMachineSQLDAOBase(self)
        if 'other' not in self:
            self['other'] = DBOtherSQLDAOBase(self)
        if 'abstraction' not in self:
            self['abstraction'] = DBAbstractionSQLDAOBase(self)
        if 'mashuptrail' not in self:
            self['mashuptrail'] = DBMashuptrailSQLDAOBase(self)
        if 'registry' not in self:
            self['registry'] = DBRegistrySQLDAOBase(self)
        if 'annotation' not in self:
            self['annotation'] = DBAnnotationSQLDAOBase(self)
        if 'parameter_exploration' not in self:
            self['parameter_exploration'] = DBParameterExplorationSQLDAOBase(self)
        if 'mashup_actionAnnotation' not in self:
            self['mashup_actionAnnotation'] = DBMashupActionAnnotationSQLDAOBase(self)
        if 'module_exec' not in self:
            self['module_exec'] = DBModuleExecSQLDAOBase(self)
