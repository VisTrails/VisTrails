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

from xml.auto_gen import XMLDAOListBase
from sql.auto_gen import SQLDAOListBase
from vistrails.core.system import get_elementtree_library

from vistrails.db import VistrailsDBException
from vistrails.db.versions.v1_0_2 import version as my_version
from vistrails.db.versions.v1_0_2.domain import DBGroup, DBWorkflow, DBVistrail, DBLog, \
    DBRegistry

ElementTree = get_elementtree_library()


class DAOList(dict):
    def __init__(self):
        self['xml'] = XMLDAOListBase()
        self['sql'] = SQLDAOListBase()

    def parse_xml_file(self, filename):
        return ElementTree.parse(filename)

    def write_xml_file(self, filename, tree):
        def indent(elem, level=0):
            i = "\n" + level*"  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        indent(tree.getroot())
        tree.write(filename)

    def read_xml_object(self, vtType, node):
        return self['xml'][vtType].fromXML(node)

    def write_xml_object(self, obj, node=None):
        res_node = self['xml'][obj.vtType].toXML(obj, node)
        return res_node
        
    def open_from_xml(self, filename, vtType, tree=None):
        """open_from_xml(filename) -> DBVistrail"""
        if tree is None:
            tree = self.parse_xml_file(filename)
        vistrail = self.read_xml_object(vtType, tree.getroot())
        return vistrail

    def save_to_xml(self, obj, filename, tags, version=None):
        """save_to_xml(obj : object, filename: str, tags: dict,
                       version: str) -> None
    
        """
        root = self.write_xml_object(obj)
        if version is None:
            version = my_version
        root.set('version', version)
        for k, v in tags.iteritems():
            root.set(k, v)
        tree = ElementTree.ElementTree(root)
        self.write_xml_file(filename, tree)

    def open_from_db(self, db_connection, vtType, id=None, lock=False, 
                     global_props=None):
        all_objects = {}
        if global_props is None:
            global_props = {}
        if id is not None:
            global_props['id'] = id
        # print global_props
        res_objects = self['sql'][vtType].get_sql_columns(db_connection, 
                                                          global_props,
                                                          lock)
        if len(res_objects) > 1:
            raise VistrailsDBException("More than object of type '%s' and "
                                       "id '%s' exist in the database" % \
                                           (vtType, id))
        elif len(res_objects) <= 0:
            raise VistrailsDBException("No objects of type '%s' and "
                                       "id '%s' exist in the database" % \
                                           (vtType, id))
        
        all_objects.update(res_objects)
        res = res_objects.values()[0]
        global_props = {'entity_id': res.db_id,
                        'entity_type': res.vtType}

        # collect all commands so that they can be executed together
        # daoList should contain (dao_type, dao, dbCommand) values
        daoList = []
        # dbCommandList should contain dbCommand values
        dbCommandList = []
        
        # generate SELECT statements
        for dao_type, dao in self['sql'].iteritems():
            if (dao_type == DBVistrail.vtType or
                dao_type == DBWorkflow.vtType or
                dao_type == DBLog.vtType or
                dao_type == DBRegistry.vtType):
                continue

            daoList.append([dao_type, dao, None])
            dbCommand = dao.get_sql_select(db_connection, global_props, lock)
            dbCommandList.append(dbCommand)
            
        # Exacute all select statements
        results = self['sql'][vtType].executeSQLGroup(db_connection,
                                                      dbCommandList, True)

        # add result to correct dao
        for i in xrange(len(daoList)):
            daoList[i][2] = results[i]
        
        # process results
        for dao_type, dao, data in daoList:
            current_objs = dao.process_sql_columns(data, global_props)
            all_objects.update(current_objs)

            if dao_type == DBGroup.vtType:
                for key, obj in current_objs.iteritems():
                    new_props = {'parent_id': key[1],
                                 'entity_id': global_props['entity_id'],
                                 'entity_type': global_props['entity_type']}
                    res_obj = self.open_from_db(db_connection, 
                                                DBWorkflow.vtType, 
                                                None, lock, new_props)
                    res_dict = {}
                    res_dict[(res_obj.vtType, res_obj.db_id)] = res_obj
                    all_objects.update(res_dict)

        for key, obj in all_objects.iteritems():
            if key[0] == vtType and key[1] == id:
                continue
            self['sql'][obj.vtType].from_sql_fast(obj, all_objects)
        for obj in all_objects.itervalues():
            obj.is_dirty = False
            obj.is_new = False

        return res

    def open_many_from_db(self, db_connection, vtType, ids, lock=False):
        """ Loads multiple objects. They need to be loaded as one single
            multiple select statement command for performance reasons.
        """

        log_dao = self['sql'][vtType]
        # loop through ids and build SELECT statements
        selects = [log_dao.get_sql_select(db_connection, {'id': id}, lock)
                   for id in ids]
        # Execute all SELECT statements for main objects
        results = log_dao.executeSQLGroup(db_connection, selects, True)

        # list of final objects
        objects = []
        # list of selects
        selects = []
        # list of children id:all_objects_dict
        all_objects_dict = {}
        # process each result and extract child SELECTS
        # daoList should contain (id, dao_type, dao, result) values
        daoList = []
        # selects should contain dbCommand values
        selects = []
        global_props = {}
        for id, data in zip(ids, results):
            res_objects = log_dao.process_sql_columns(data, global_props)
            if len(res_objects) > 1:
                raise VistrailsDBException("More than object of type '%s' and "
                                           "id '%s' exist in the database" % \
                                               (vtType, id))
            elif len(res_objects) <= 0:
                raise VistrailsDBException("No objects of type '%s' and "
                                           "id '%s' exist in the database" % \
                                               (vtType, id))
            all_objects = {}
            all_objects_dict[id] = all_objects
            all_objects.update(res_objects)
            objects.append(res_objects.values()[0])
            # collect all commands so that they can be executed together
        
            # generate SELECT statements for children
            for dao_type, dao in self['sql'].iteritems():
                if (dao_type == DBVistrail.vtType or
                    dao_type == DBWorkflow.vtType or
                    dao_type == DBLog.vtType or
                    dao_type == DBRegistry.vtType):
                    continue
    
                daoList.append([id, dao_type, dao, None])
                dbCommand = dao.get_sql_select(db_connection, global_props, lock)
                selects.append(dbCommand)

        # Execute all child select statements
        results = self['sql'][vtType].executeSQLGroup(db_connection,
                                                      selects, True)
        for i in xrange(len(daoList)):
            daoList[i][3] = results[i]

        # process results
        for id, dao_type, dao, data in daoList:
            all_objects = all_objects_dict[id]
            current_objs = dao.process_sql_columns(data, global_props)
            all_objects.update(current_objs)

            if dao_type == DBGroup.vtType:
                for key, obj in current_objs.iteritems():
                    new_props = {'parent_id': key[1],
                                 'entity_id': global_props['entity_id'],
                                 'entity_type': global_props['entity_type']}
                    res_obj = self.open_from_db(db_connection, 
                                                DBWorkflow.vtType, 
                                                None, lock, new_props)
                    res_dict = {}
                    res_dict[(res_obj.vtType, res_obj.db_id)] = res_obj
                    all_objects.update(res_dict)

        
        for id, all_objects in all_objects_dict.iteritems():
            for key, obj in all_objects.iteritems():
                if key[0] == vtType and key[1] == id:
                    continue
                self['sql'][obj.vtType].from_sql_fast(obj, all_objects)
        for id, dao_type, dao, data in daoList:
            all_objects = all_objects_dict[id]
            for obj in all_objects.itervalues():
                obj.is_dirty = False
                obj.is_new = False
    
        return objects

    def save_to_db(self, db_connection, obj, do_copy=False, global_props=None):
        if do_copy == 'with_ids':
            do_copy = True
        elif do_copy and obj.db_id is not None:
            obj.db_id = None

        children = obj.db_children()
        children.reverse()
        if global_props is None:
            global_props = {'entity_type': obj.vtType}
        # print 'global_props:', global_props

        # assumes not deleting entire thing
        child = children[0][0]
        self['sql'][child.vtType].set_sql_columns(db_connection, child, 
                                                  global_props, do_copy)
        self['sql'][child.vtType].to_sql_fast(child, do_copy)

        global_props = {'entity_id': child.db_id,
                        'entity_type': child.vtType}

        # do deletes
        if not do_copy:
            for (child, _, _) in children:
                for c in child.db_deleted_children(True):
                    self['sql'][c.vtType].delete_sql_column(db_connection,
                                                            c,
                                                            global_props)
        child = children.pop(0)[0]
        child.is_dirty = False
        child.is_new = False
        
        if not len(children):
            return

        # list of all children
        dbCommandList = []
        writtenChildren = []
        # process remaining children
        for (child, _, _) in children:
            dbCommand = self['sql'][child.vtType].set_sql_command(
                            db_connection, child, global_props, do_copy)
            if dbCommand is not None:
                dbCommandList.append(dbCommand)
                writtenChildren.append(child)
            self['sql'][child.vtType].to_sql_fast(child, do_copy)

        # Execute all insert/update statements
        results = self['sql'][children[0][0].vtType].executeSQLGroup(
                                                    db_connection,
                                                    dbCommandList, False)
        resultDict = dict(zip(writtenChildren, results))
        # process remaining children
        for (child, _, _) in children:
            if child in resultDict:
                lastId = resultDict[child]
                self['sql'][child.vtType].set_sql_process(child, 
                                                          global_props,
                                                          lastId)
            self['sql'][child.vtType].to_sql_fast(child, do_copy)
            if child.vtType == DBGroup.vtType:
                if child.db_workflow:
                    # print '*** entity_type:', global_props['entity_type']
                    new_props = {'entity_id': global_props['entity_id'],
                                 'entity_type': global_props['entity_type']}
                    is_dirty = child.db_workflow.is_dirty
                    child.db_workflow.db_entity_type = DBWorkflow.vtType
                    child.db_workflow.is_dirty = is_dirty
                    self.save_to_db(db_connection, child.db_workflow, do_copy,
                                    new_props)

    def save_many_to_db(self, db_connection, objList, do_copy=False):
        if do_copy == 'with_ids':
            do_copy = True
        if not len(objList):
            return
        childrenDict = {}
        global_propsDict = {}
        dbCommandList = []
        writtenChildren = []
        for obj in objList:
            if do_copy and obj.db_id is not None:
                obj.db_id = None

            children = obj.db_children()
            children.reverse()
            global_props = {'entity_type': obj.vtType}

            child = children[0][0]
            dbCommand = self['sql'][child.vtType].set_sql_command(
                db_connection, child, global_props, do_copy)
            if dbCommand is not None:
                dbCommandList.append(dbCommand)
                writtenChildren.append(child)
            
            childrenDict[child] = children
            global_propsDict[child] = global_props

        # Execute all insert/update statements for the main objects
        results = self['sql'][children[0][0].vtType].executeSQLGroup(
                                                    db_connection,
                                                    dbCommandList, False)
        resultDict = dict(zip(writtenChildren, results))
        dbCommandList = []
        writtenChildren = []
        for child, children in childrenDict.iteritems():
            # process objects
            if child in resultDict:
                lastId = resultDict[child]
                self['sql'][child.vtType].set_sql_process(
                    child, global_propsDict[child], lastId)
            self['sql'][child.vtType].to_sql_fast(child, do_copy)

            # process children
            global_props = {'entity_id': child.db_id,
                                       'entity_type': child.vtType}
            global_propsDict[child] = global_props
            # do deletes
            if not do_copy:
                for (child, _, _) in childrenDict[child]:
                    for c in child.db_deleted_children(True):
                        self['sql'][c.vtType].delete_sql_column(db_connection,
                                                                c,
                                                                global_props)
            child = children.pop(0)[0]
            child.is_dirty = False
            child.is_new = False
            
            # list of all children
            # process remaining children
            for (child, _, _) in children:
                dbCommand = self['sql'][child.vtType].set_sql_command(
                                db_connection, child, global_props, do_copy)
                if dbCommand is not None:
                    dbCommandList.append(dbCommand)
                    writtenChildren.append(child)
                self['sql'][child.vtType].to_sql_fast(child, do_copy)
    
        # Execute all child insert/update statements
        results = self['sql'][children[0][0].vtType].executeSQLGroup(
                                                        db_connection,
                                                        dbCommandList, False)
        resultDict = dict(zip(writtenChildren, results))

        for child, children in childrenDict.iteritems():
            global_props = global_propsDict[child]
            # process remaining children
            for (child, _, _) in children:
                if child in resultDict:
                    lastId = resultDict[child]
                    self['sql'][child.vtType].set_sql_process(child, 
                                                              global_props,
                                                              lastId)
                self['sql'][child.vtType].to_sql_fast(child, do_copy)
                if child.vtType == DBGroup.vtType:
                    if child.db_workflow:
                        # print '*** entity_type:', global_props['entity_type']
                        new_props = {'entity_id': global_props['entity_id'],
                                     'entity_type': global_props['entity_type']}
                        is_dirty = child.db_workflow.is_dirty
                        child.db_workflow.db_entity_type = DBWorkflow.vtType
                        child.db_workflow.is_dirty = is_dirty
                        self.save_to_db(db_connection, child.db_workflow, do_copy,
                                        new_props)

    def delete_from_db(self, db_connection, type, obj_id):
        root_set = set([DBVistrail.vtType, DBWorkflow.vtType, 
                        DBLog.vtType, DBRegistry.vtType])
        if type not in root_set:
            raise VistrailsDBException("Cannot delete entity of type '%s'" \
                                           % type)

        id_str = str(obj_id)
        for (dao_type, dao) in self['sql'].iteritems():
            if dao_type not in root_set:
                db_cmd = \
                    self['sql'][type].createSQLDelete(dao.table,
                                                      {'entity_type': type,
                                                       'entity_id': id_str})
                self['sql'][type].executeSQL(db_connection, db_cmd, False)
        db_cmd = self['sql'][type].createSQLDelete(self['sql'][type].table,
                                                   {'id': id_str})
        self['sql'][type].executeSQL(db_connection, db_cmd, False)

    def serialize(self, object):
        root = self.write_xml_object(object)
        return ElementTree.tostring(root)

    def unserialize(self, str, obj_type):
        def set_dirty(obj):
            for child, _, _ in obj.db_children():
                if child.vtType == DBGroup.vtType:
                    if child.db_workflow:
                        set_dirty(child.db_workflow)
                child.is_dirty = True
                child.is_new = True
        try:
            root = ElementTree.fromstring(str)
            obj = self.read_xml_object(obj_type, root)
            set_dirty(obj)
            return obj
        except SyntaxError, e:
            msg = "Invalid VisTrails serialized object %s" % str
            raise VistrailsDBException(msg)
            return None
