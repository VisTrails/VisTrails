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

from xml.auto_gen import XMLDAOListBase
from sql.auto_gen import SQLDAOListBase
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

from db import VistrailsDBException
from db.versions.v0_9_5 import version as my_version
from db.versions.v0_9_5.domain import DBGroup, DBWorkflow, DBVistrail, DBLog, \
    DBRegistry

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

        for dao_type, dao in self['sql'].iteritems():
#             if (dao == self['sql'][DBVistrail.vtType] or
#                 # dao == self['sql'][DBWorkflow.vtType] or
#                 dao == self['sql'][DBLog.vtType] or
#                 # dao == self['sql'][DBAbstraction.vtType]):
#                 continue
            if (dao_type == DBVistrail.vtType or
                dao_type == DBLog.vtType or
                dao_type == DBRegistry.vtType):
                continue
                
            current_objs = dao.get_sql_columns(db_connection, global_props, 
                                               lock)
            if dao_type == DBWorkflow.vtType:
                for key, obj in current_objs.iteritems():
                    if key[0] == vtType and key[1] == id:
                        continue
                    elif key[0] == DBWorkflow.vtType:
                        res_objs = \
                            self.open_from_db(db_connection, key[0], key[1], 
                                              lock, version)
                        res_dict = {}
                        for res_obj in res_objs:
                            res_dict[(res_obj.db_id, res_obj.vtType)] = res_obj
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

        children = obj.db_children()
        children.reverse()
        if global_props is None:
            global_props = {'entity_type': "'" + obj.vtType + "'"}
        # print 'global_props:', global_props

        # assumes not deleting entire thing
        (child, _, _) = children.pop(0)
        self['sql'][child.vtType].set_sql_columns(db_connection, child, 
                                                  global_props, do_copy)
        self['sql'][child.vtType].to_sql_fast(child, do_copy)
        child.is_dirty = False
        child.is_new = False

        # do deletes
        if not do_copy:
            for (c, _, _) in children:
                for child in c.db_deleted_children(True):
                    self['sql'][c.vtType].delete_sql_column(db_connection,
                                                            c,
                                                            global_props)

        # process remaining children
        for (child, _, _) in children:
            # print "child:", child.vtType, child.db_id
            self['sql'][child.vtType].set_sql_columns(db_connection, child, 
                                                      global_props, do_copy)
            self['sql'][child.vtType].to_sql_fast(child, do_copy)
            if child.vtType == DBGroup.vtType:
                if child.db_workflow:
                    # print '*** entity_type:', global_props['entity_type']
                    self.save_to_db(db_connection, [child.db_workflow], do_copy,
                                    {'entity_id': global_props['entity_id'],
                                     'entity_type': global_props['entity_type']}
                                    )
                                            
            child.is_dirty = False
            child.is_new = False

    def serialize(self, object):
        root = self.write_xml_object(object)
        return ElementTree.tostring(root)

    def unserialize(self, str, obj_type):
        try:
            root = ElementTree.fromstring(str)
            return self.read_xml_object(obj_type, root)
        except SyntaxError, e:
            msg = "Invalid VisTrails serialized object %s" % str
            raise VistrailsDBException(msg)
            return None
