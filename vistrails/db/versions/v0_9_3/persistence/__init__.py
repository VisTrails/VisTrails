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
from vistrails.db.versions.v0_9_3 import version as my_version
from vistrails.db.versions.v0_9_3.domain import DBVistrail, DBWorkflow, DBLog, \
    DBAbstraction, DBGroup

ElementTree = get_elementtree_library()


class DAOList(dict):
    def __init__(self):
        self['xml'] = XMLDAOListBase()
        self['sql'] = SQLDAOListBase()

    def parse_xml_file(self, filename):
        return ElementTree.parse(filename)

    def write_xml_file(self, filename, tree):
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

    def open_from_db(self, db_connection, vtType, id, lock=False):
        all_objects = {}
        global_props = {'id': id}
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
        del global_props['id']

        for dao in self['sql'].itervalues():
            if (dao == self['sql'][DBVistrail.vtType] or
                # dao == self['sql'][DBWorkflow.vtType] or
                dao == self['sql'][DBLog.vtType] or
                dao == self['sql'][DBAbstraction.vtType]):
                continue
            current_objs = dao.get_sql_columns(db_connection, global_props, 
                                               lock)
            if dao == self['sql'][DBWorkflow.vtType]:
                for key, obj in current_objs.iteritems():
                    if key[0] == vtType and key[1] == id:
                        continue
                    elif key[0] == DBWorkflow.vtType:
                        res_obj = self.open_from_db(db_connection, key[0], 
                                                    key[1], lock)
                        res_dict = {}
                        res_dict[(res_obj.vtType, res_obj.db_id)] = res_obj
                        all_objects.update(res_dict)
            else:
                all_objects.update(current_objs)

        for key, obj in all_objects.iteritems():
            if key[0] == vtType and key[1] == id:
                continue
            self['sql'][obj.vtType].from_sql_fast(obj, all_objects)
        for obj in all_objects.itervalues():
            obj.is_dirty = False
            obj.is_new = False
        return res

    def save_to_db(self, db_connection, obj, do_copy=False, global_props=None):
        if do_copy and obj.db_id is not None:
            obj.db_id = None

        children = obj.db_children() # forSQL=True)
        children.reverse()
        if global_props is None:
            global_props = {'entity_type': obj.vtType}
        # print 'global_props:', global_props

        # assumes not deleting entire thing
        (child, _, _) = children[0]
        self['sql'][child.vtType].set_sql_columns(db_connection, child, 
                                                      global_props, do_copy)
        self['sql'][child.vtType].to_sql_fast(child, do_copy)

        global_props = {'entity_id': child.db_id,
                        'entity_type': child.vtType}

        if not do_copy:
            for (child, _, _) in children:
                for c in child.db_deleted_children(True):
                    self['sql'][c.vtType].delete_sql_column(db_connection,
                                                                c,
                                                                global_props)

        (child, _, _) = children.pop(0)
        child.is_dirty = False
        child.is_new = False
        for (child, _, _) in children:
            # print "child:", child.vtType, child.db_id
            self['sql'][child.vtType].set_sql_columns(db_connection, child, 
                                                          global_props, do_copy)
            self['sql'][child.vtType].to_sql_fast(child, do_copy)
            if child.vtType == DBGroup.vtType:
                if child.db_workflow:
                    # print '*** entity_type:', global_props['entity_type']
                    self.save_to_db(db_connection, child.db_workflow,
                                    do_copy,
                                    {'entity_id': global_props['entity_id'],
                                     'entity_type': \
                                         global_props['entity_type']}
                                    )
                                            
            child.is_dirty = False
            child.is_new = False

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
