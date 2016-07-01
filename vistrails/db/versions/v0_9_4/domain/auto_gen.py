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

"""generated automatically by auto_dao.py"""

from __future__ import division

import copy

class DBPortSpec(object):

    vtType = 'portSpec'

    def __init__(self, id=None, name=None, type=None, spec=None):
        self._db_id = id
        self._db_name = name
        self._db_type = type
        self._db_spec = spec
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPortSpec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpec(id=self._db_id,
                        name=self._db_name,
                        type=self._db_type,
                        spec=self._db_spec)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPortSpec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'spec' in class_dict:
            res = class_dict['spec'](old_obj, trans_dict)
            new_obj.db_spec = res
        elif hasattr(old_obj, 'db_spec') and old_obj.db_spec is not None:
            new_obj.db_spec = old_obj.db_spec
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_spec(self):
        return self._db_spec
    def __set_db_spec(self, spec):
        self._db_spec = spec
        self.is_dirty = True
    db_spec = property(__get_db_spec, __set_db_spec)
    def db_add_spec(self, spec):
        self._db_spec = spec
    def db_change_spec(self, spec):
        self._db_spec = spec
    def db_delete_spec(self, spec):
        self._db_spec = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBModule(object):

    vtType = 'module'

    def __init__(self, id=None, cache=None, name=None, namespace=None, package=None, version=None, tag=None, location=None, functions=None, annotations=None, portSpecs=None):
        self._db_id = id
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_tag = tag
        self.db_deleted_location = []
        self._db_location = location
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        self.db_annotations_key_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
                self.db_annotations_key_index[v.db_key] = v
        self.db_deleted_portSpecs = []
        self.db_portSpecs_id_index = {}
        self.db_portSpecs_name_index = {}
        if portSpecs is None:
            self._db_portSpecs = []
        else:
            self._db_portSpecs = portSpecs
            for v in self._db_portSpecs:
                self.db_portSpecs_id_index[v.db_id] = v
                self.db_portSpecs_name_index[(v.db_name,v.db_type)] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBModule.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModule(id=self._db_id,
                      cache=self._db_cache,
                      name=self._db_name,
                      namespace=self._db_namespace,
                      package=self._db_package,
                      version=self._db_version,
                      tag=self._db_tag)
        if self._db_location is not None:
            cp._db_location = self._db_location.do_copy(new_ids, id_scope, id_remap)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_portSpecs is None:
            cp._db_portSpecs = []
        else:
            cp._db_portSpecs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_portSpecs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        cp.db_portSpecs_id_index = dict((v.db_id, v) for v in cp._db_portSpecs)
        cp.db_portSpecs_name_index = dict(((v.db_name,v.db_type), v) for v in cp._db_portSpecs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBModule()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'cache' in class_dict:
            res = class_dict['cache'](old_obj, trans_dict)
            new_obj.db_cache = res
        elif hasattr(old_obj, 'db_cache') and old_obj.db_cache is not None:
            new_obj.db_cache = old_obj.db_cache
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'tag' in class_dict:
            res = class_dict['tag'](old_obj, trans_dict)
            new_obj.db_tag = res
        elif hasattr(old_obj, 'db_tag') and old_obj.db_tag is not None:
            new_obj.db_tag = old_obj.db_tag
        if 'location' in class_dict:
            res = class_dict['location'](old_obj, trans_dict)
            new_obj.db_location = res
        elif hasattr(old_obj, 'db_location') and old_obj.db_location is not None:
            obj = old_obj.db_location
            new_obj.db_add_location(DBLocation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_location') and hasattr(new_obj, 'db_deleted_location'):
            for obj in old_obj.db_deleted_location:
                n_obj = DBLocation.update_version(obj, trans_dict)
                new_obj.db_deleted_location.append(n_obj)
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        if 'portSpecs' in class_dict:
            res = class_dict['portSpecs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_portSpec(obj)
        elif hasattr(old_obj, 'db_portSpecs') and old_obj.db_portSpecs is not None:
            for obj in old_obj.db_portSpecs:
                new_obj.db_add_portSpec(DBPortSpec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_portSpecs') and hasattr(new_obj, 'db_deleted_portSpecs'):
            for obj in old_obj.db_deleted_portSpecs:
                n_obj = DBPortSpec.update_version(obj, trans_dict)
                new_obj.db_deleted_portSpecs.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_portSpecs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_portSpec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_portSpecs)
        if remove:
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
            self.db_deleted_portSpecs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_location is not None and self._db_location.has_changes():
            return True
        for child in self._db_functions:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_portSpecs:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_cache(self):
        return self._db_cache
    def __set_db_cache(self, cache):
        self._db_cache = cache
        self.is_dirty = True
    db_cache = property(__get_db_cache, __set_db_cache)
    def db_add_cache(self, cache):
        self._db_cache = cache
    def db_change_cache(self, cache):
        self._db_cache = cache
    def db_delete_cache(self, cache):
        self._db_cache = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_tag(self):
        return self._db_tag
    def __set_db_tag(self, tag):
        self._db_tag = tag
        self.is_dirty = True
    db_tag = property(__get_db_tag, __set_db_tag)
    def db_add_tag(self, tag):
        self._db_tag = tag
    def db_change_tag(self, tag):
        self._db_tag = tag
    def db_delete_tag(self, tag):
        self._db_tag = None
    
    def __get_db_location(self):
        return self._db_location
    def __set_db_location(self, location):
        self._db_location = location
        self.is_dirty = True
    db_location = property(__get_db_location, __set_db_location)
    def db_add_location(self, location):
        self._db_location = location
    def db_change_location(self, location):
        self._db_location = location
    def db_delete_location(self, location):
        if not self.is_new:
            self.db_deleted_location.append(self._db_location)
        self._db_location = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
        del self.db_annotations_key_index[annotation.db_key]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    def db_get_annotation_by_key(self, key):
        return self.db_annotations_key_index[key]
    def db_has_annotation_with_key(self, key):
        return key in self.db_annotations_key_index
    
    def __get_db_portSpecs(self):
        return self._db_portSpecs
    def __set_db_portSpecs(self, portSpecs):
        self._db_portSpecs = portSpecs
        self.is_dirty = True
    db_portSpecs = property(__get_db_portSpecs, __set_db_portSpecs)
    def db_get_portSpecs(self):
        return self._db_portSpecs
    def db_add_portSpec(self, portSpec):
        self.is_dirty = True
        self._db_portSpecs.append(portSpec)
        self.db_portSpecs_id_index[portSpec.db_id] = portSpec
        self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)] = portSpec
    def db_change_portSpec(self, portSpec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == portSpec.db_id:
                self._db_portSpecs[i] = portSpec
                found = True
                break
        if not found:
            self._db_portSpecs.append(portSpec)
        self.db_portSpecs_id_index[portSpec.db_id] = portSpec
        self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)] = portSpec
    def db_delete_portSpec(self, portSpec):
        self.is_dirty = True
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == portSpec.db_id:
                if not self._db_portSpecs[i].is_new:
                    self.db_deleted_portSpecs.append(self._db_portSpecs[i])
                del self._db_portSpecs[i]
                break
        del self.db_portSpecs_id_index[portSpec.db_id]
        del self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)]
    def db_get_portSpec(self, key):
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == key:
                return self._db_portSpecs[i]
        return None
    def db_get_portSpec_by_id(self, key):
        return self.db_portSpecs_id_index[key]
    def db_has_portSpec_with_id(self, key):
        return key in self.db_portSpecs_id_index
    def db_get_portSpec_by_name(self, key):
        return self.db_portSpecs_name_index[key]
    def db_has_portSpec_with_name(self, key):
        return key in self.db_portSpecs_name_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBTag(object):

    vtType = 'tag'

    def __init__(self, id=None, name=None):
        self._db_id = id
        self._db_name = name
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBTag.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBTag(id=self._db_id,
                   name=self._db_name)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('action', self._db_id) in id_remap:
                cp._db_id = id_remap[('action', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBTag()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBPort(object):

    vtType = 'port'

    def __init__(self, id=None, type=None, moduleId=None, moduleName=None, name=None, spec=None):
        self._db_id = id
        self._db_type = type
        self._db_moduleId = moduleId
        self._db_moduleName = moduleName
        self._db_name = name
        self._db_spec = spec
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPort.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPort(id=self._db_id,
                    type=self._db_type,
                    moduleId=self._db_moduleId,
                    moduleName=self._db_moduleName,
                    name=self._db_name,
                    spec=self._db_spec)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_moduleId') and ('module', self._db_moduleId) in id_remap:
                cp._db_moduleId = id_remap[('module', self._db_moduleId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPort()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'moduleId' in class_dict:
            res = class_dict['moduleId'](old_obj, trans_dict)
            new_obj.db_moduleId = res
        elif hasattr(old_obj, 'db_moduleId') and old_obj.db_moduleId is not None:
            new_obj.db_moduleId = old_obj.db_moduleId
        if 'moduleName' in class_dict:
            res = class_dict['moduleName'](old_obj, trans_dict)
            new_obj.db_moduleName = res
        elif hasattr(old_obj, 'db_moduleName') and old_obj.db_moduleName is not None:
            new_obj.db_moduleName = old_obj.db_moduleName
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'spec' in class_dict:
            res = class_dict['spec'](old_obj, trans_dict)
            new_obj.db_spec = res
        elif hasattr(old_obj, 'db_spec') and old_obj.db_spec is not None:
            new_obj.db_spec = old_obj.db_spec
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_moduleId(self):
        return self._db_moduleId
    def __set_db_moduleId(self, moduleId):
        self._db_moduleId = moduleId
        self.is_dirty = True
    db_moduleId = property(__get_db_moduleId, __set_db_moduleId)
    def db_add_moduleId(self, moduleId):
        self._db_moduleId = moduleId
    def db_change_moduleId(self, moduleId):
        self._db_moduleId = moduleId
    def db_delete_moduleId(self, moduleId):
        self._db_moduleId = None
    
    def __get_db_moduleName(self):
        return self._db_moduleName
    def __set_db_moduleName(self, moduleName):
        self._db_moduleName = moduleName
        self.is_dirty = True
    db_moduleName = property(__get_db_moduleName, __set_db_moduleName)
    def db_add_moduleName(self, moduleName):
        self._db_moduleName = moduleName
    def db_change_moduleName(self, moduleName):
        self._db_moduleName = moduleName
    def db_delete_moduleName(self, moduleName):
        self._db_moduleName = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_spec(self):
        return self._db_spec
    def __set_db_spec(self, spec):
        self._db_spec = spec
        self.is_dirty = True
    db_spec = property(__get_db_spec, __set_db_spec)
    def db_add_spec(self, spec):
        self._db_spec = spec
    def db_change_spec(self, spec):
        self._db_spec = spec
    def db_delete_spec(self, spec):
        self._db_spec = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBGroup(object):

    vtType = 'group'

    def __init__(self, id=None, workflow=None, cache=None, name=None, namespace=None, package=None, version=None, tag=None, location=None, functions=None, annotations=None):
        self._db_id = id
        self.db_deleted_workflow = []
        self._db_workflow = workflow
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_tag = tag
        self.db_deleted_location = []
        self._db_location = location
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        self.db_annotations_key_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
                self.db_annotations_key_index[v.db_key] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBGroup.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBGroup(id=self._db_id,
                     cache=self._db_cache,
                     name=self._db_name,
                     namespace=self._db_namespace,
                     package=self._db_package,
                     version=self._db_version,
                     tag=self._db_tag)
        if self._db_workflow is not None:
            cp._db_workflow = self._db_workflow.do_copy()
        if self._db_location is not None:
            cp._db_location = self._db_location.do_copy(new_ids, id_scope, id_remap)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBGroup()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'workflow' in class_dict:
            res = class_dict['workflow'](old_obj, trans_dict)
            new_obj.db_workflow = res
        elif hasattr(old_obj, 'db_workflow') and old_obj.db_workflow is not None:
            obj = old_obj.db_workflow
            new_obj.db_add_workflow(DBWorkflow.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_workflow') and hasattr(new_obj, 'db_deleted_workflow'):
            for obj in old_obj.db_deleted_workflow:
                n_obj = DBWorkflow.update_version(obj, trans_dict)
                new_obj.db_deleted_workflow.append(n_obj)
        if 'cache' in class_dict:
            res = class_dict['cache'](old_obj, trans_dict)
            new_obj.db_cache = res
        elif hasattr(old_obj, 'db_cache') and old_obj.db_cache is not None:
            new_obj.db_cache = old_obj.db_cache
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'tag' in class_dict:
            res = class_dict['tag'](old_obj, trans_dict)
            new_obj.db_tag = res
        elif hasattr(old_obj, 'db_tag') and old_obj.db_tag is not None:
            new_obj.db_tag = old_obj.db_tag
        if 'location' in class_dict:
            res = class_dict['location'](old_obj, trans_dict)
            new_obj.db_location = res
        elif hasattr(old_obj, 'db_location') and old_obj.db_location is not None:
            obj = old_obj.db_location
            new_obj.db_add_location(DBLocation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_location') and hasattr(new_obj, 'db_deleted_location'):
            for obj in old_obj.db_deleted_location:
                n_obj = DBLocation.update_version(obj, trans_dict)
                new_obj.db_deleted_location.append(n_obj)
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_workflow)
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        if remove:
            self.db_deleted_workflow = []
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_workflow is not None and self._db_workflow.has_changes():
            return True
        if self._db_location is not None and self._db_location.has_changes():
            return True
        for child in self._db_functions:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_workflow(self):
        return self._db_workflow
    def __set_db_workflow(self, workflow):
        self._db_workflow = workflow
        self.is_dirty = True
    db_workflow = property(__get_db_workflow, __set_db_workflow)
    def db_add_workflow(self, workflow):
        self._db_workflow = workflow
    def db_change_workflow(self, workflow):
        self._db_workflow = workflow
    def db_delete_workflow(self, workflow):
        if not self.is_new:
            self.db_deleted_workflow.append(self._db_workflow)
        self._db_workflow = None
    
    def __get_db_cache(self):
        return self._db_cache
    def __set_db_cache(self, cache):
        self._db_cache = cache
        self.is_dirty = True
    db_cache = property(__get_db_cache, __set_db_cache)
    def db_add_cache(self, cache):
        self._db_cache = cache
    def db_change_cache(self, cache):
        self._db_cache = cache
    def db_delete_cache(self, cache):
        self._db_cache = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_tag(self):
        return self._db_tag
    def __set_db_tag(self, tag):
        self._db_tag = tag
        self.is_dirty = True
    db_tag = property(__get_db_tag, __set_db_tag)
    def db_add_tag(self, tag):
        self._db_tag = tag
    def db_change_tag(self, tag):
        self._db_tag = tag
    def db_delete_tag(self, tag):
        self._db_tag = None
    
    def __get_db_location(self):
        return self._db_location
    def __set_db_location(self, location):
        self._db_location = location
        self.is_dirty = True
    db_location = property(__get_db_location, __set_db_location)
    def db_add_location(self, location):
        self._db_location = location
    def db_change_location(self, location):
        self._db_location = location
    def db_delete_location(self, location):
        if not self.is_new:
            self.db_deleted_location.append(self._db_location)
        self._db_location = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
        del self.db_annotations_key_index[annotation.db_key]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    def db_get_annotation_by_key(self, key):
        return self.db_annotations_key_index[key]
    def db_has_annotation_with_key(self, key):
        return key in self.db_annotations_key_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBLog(object):

    vtType = 'log'

    def __init__(self, id=None, entity_type=None, version=None, name=None, last_modified=None, workflow_execs=None, machines=None, vistrail_id=None):
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_version = version
        self._db_name = name
        self._db_last_modified = last_modified
        self.db_deleted_workflow_execs = []
        self.db_workflow_execs_id_index = {}
        if workflow_execs is None:
            self._db_workflow_execs = []
        else:
            self._db_workflow_execs = workflow_execs
            for v in self._db_workflow_execs:
                self.db_workflow_execs_id_index[v.db_id] = v
        self.db_deleted_machines = []
        self.db_machines_id_index = {}
        if machines is None:
            self._db_machines = []
        else:
            self._db_machines = machines
            for v in self._db_machines:
                self.db_machines_id_index[v.db_id] = v
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBLog.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLog(id=self._db_id,
                   entity_type=self._db_entity_type,
                   version=self._db_version,
                   name=self._db_name,
                   last_modified=self._db_last_modified,
                   vistrail_id=self._db_vistrail_id)
        if self._db_workflow_execs is None:
            cp._db_workflow_execs = []
        else:
            cp._db_workflow_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_workflow_execs]
        if self._db_machines is None:
            cp._db_machines = []
        else:
            cp._db_machines = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_machines]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_vistrail_id') and ('vistrail', self._db_vistrail_id) in id_remap:
                cp._db_vistrail_id = id_remap[('vistrail', self._db_vistrail_id)]
        
        # recreate indices and set flags
        cp.db_workflow_execs_id_index = dict((v.db_id, v) for v in cp._db_workflow_execs)
        cp.db_machines_id_index = dict((v.db_id, v) for v in cp._db_machines)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBLog()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'entity_type' in class_dict:
            res = class_dict['entity_type'](old_obj, trans_dict)
            new_obj.db_entity_type = res
        elif hasattr(old_obj, 'db_entity_type') and old_obj.db_entity_type is not None:
            new_obj.db_entity_type = old_obj.db_entity_type
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'last_modified' in class_dict:
            res = class_dict['last_modified'](old_obj, trans_dict)
            new_obj.db_last_modified = res
        elif hasattr(old_obj, 'db_last_modified') and old_obj.db_last_modified is not None:
            new_obj.db_last_modified = old_obj.db_last_modified
        if 'workflow_execs' in class_dict:
            res = class_dict['workflow_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_workflow_exec(obj)
        elif hasattr(old_obj, 'db_workflow_execs') and old_obj.db_workflow_execs is not None:
            for obj in old_obj.db_workflow_execs:
                new_obj.db_add_workflow_exec(DBWorkflowExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_workflow_execs') and hasattr(new_obj, 'db_deleted_workflow_execs'):
            for obj in old_obj.db_deleted_workflow_execs:
                n_obj = DBWorkflowExec.update_version(obj, trans_dict)
                new_obj.db_deleted_workflow_execs.append(n_obj)
        if 'machines' in class_dict:
            res = class_dict['machines'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_machine(obj)
        elif hasattr(old_obj, 'db_machines') and old_obj.db_machines is not None:
            for obj in old_obj.db_machines:
                new_obj.db_add_machine(DBMachine.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_machines') and hasattr(new_obj, 'db_deleted_machines'):
            for obj in old_obj.db_deleted_machines:
                n_obj = DBMachine.update_version(obj, trans_dict)
                new_obj.db_deleted_machines.append(n_obj)
        if 'vistrail_id' in class_dict:
            res = class_dict['vistrail_id'](old_obj, trans_dict)
            new_obj.db_vistrail_id = res
        elif hasattr(old_obj, 'db_vistrail_id') and old_obj.db_vistrail_id is not None:
            new_obj.db_vistrail_id = old_obj.db_vistrail_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_workflow_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_workflow_exec(child)
        to_del = []
        for child in self.db_machines:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_machine(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_workflow_execs)
        children.extend(self.db_deleted_machines)
        if remove:
            self.db_deleted_workflow_execs = []
            self.db_deleted_machines = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_workflow_execs:
            if child.has_changes():
                return True
        for child in self._db_machines:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_entity_type(self):
        return self._db_entity_type
    def __set_db_entity_type(self, entity_type):
        self._db_entity_type = entity_type
        self.is_dirty = True
    db_entity_type = property(__get_db_entity_type, __set_db_entity_type)
    def db_add_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_change_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_delete_entity_type(self, entity_type):
        self._db_entity_type = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_last_modified(self):
        return self._db_last_modified
    def __set_db_last_modified(self, last_modified):
        self._db_last_modified = last_modified
        self.is_dirty = True
    db_last_modified = property(__get_db_last_modified, __set_db_last_modified)
    def db_add_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_change_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_delete_last_modified(self, last_modified):
        self._db_last_modified = None
    
    def __get_db_workflow_execs(self):
        return self._db_workflow_execs
    def __set_db_workflow_execs(self, workflow_execs):
        self._db_workflow_execs = workflow_execs
        self.is_dirty = True
    db_workflow_execs = property(__get_db_workflow_execs, __set_db_workflow_execs)
    def db_get_workflow_execs(self):
        return self._db_workflow_execs
    def db_add_workflow_exec(self, workflow_exec):
        self.is_dirty = True
        self._db_workflow_execs.append(workflow_exec)
        self.db_workflow_execs_id_index[workflow_exec.db_id] = workflow_exec
    def db_change_workflow_exec(self, workflow_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_workflow_execs)):
            if self._db_workflow_execs[i].db_id == workflow_exec.db_id:
                self._db_workflow_execs[i] = workflow_exec
                found = True
                break
        if not found:
            self._db_workflow_execs.append(workflow_exec)
        self.db_workflow_execs_id_index[workflow_exec.db_id] = workflow_exec
    def db_delete_workflow_exec(self, workflow_exec):
        self.is_dirty = True
        for i in xrange(len(self._db_workflow_execs)):
            if self._db_workflow_execs[i].db_id == workflow_exec.db_id:
                if not self._db_workflow_execs[i].is_new:
                    self.db_deleted_workflow_execs.append(self._db_workflow_execs[i])
                del self._db_workflow_execs[i]
                break
        del self.db_workflow_execs_id_index[workflow_exec.db_id]
    def db_get_workflow_exec(self, key):
        for i in xrange(len(self._db_workflow_execs)):
            if self._db_workflow_execs[i].db_id == key:
                return self._db_workflow_execs[i]
        return None
    def db_get_workflow_exec_by_id(self, key):
        return self.db_workflow_execs_id_index[key]
    def db_has_workflow_exec_with_id(self, key):
        return key in self.db_workflow_execs_id_index
    
    def __get_db_machines(self):
        return self._db_machines
    def __set_db_machines(self, machines):
        self._db_machines = machines
        self.is_dirty = True
    db_machines = property(__get_db_machines, __set_db_machines)
    def db_get_machines(self):
        return self._db_machines
    def db_add_machine(self, machine):
        self.is_dirty = True
        self._db_machines.append(machine)
        self.db_machines_id_index[machine.db_id] = machine
    def db_change_machine(self, machine):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_machines)):
            if self._db_machines[i].db_id == machine.db_id:
                self._db_machines[i] = machine
                found = True
                break
        if not found:
            self._db_machines.append(machine)
        self.db_machines_id_index[machine.db_id] = machine
    def db_delete_machine(self, machine):
        self.is_dirty = True
        for i in xrange(len(self._db_machines)):
            if self._db_machines[i].db_id == machine.db_id:
                if not self._db_machines[i].is_new:
                    self.db_deleted_machines.append(self._db_machines[i])
                del self._db_machines[i]
                break
        del self.db_machines_id_index[machine.db_id]
    def db_get_machine(self, key):
        for i in xrange(len(self._db_machines)):
            if self._db_machines[i].db_id == key:
                return self._db_machines[i]
        return None
    def db_get_machine_by_id(self, key):
        return self.db_machines_id_index[key]
    def db_has_machine_with_id(self, key):
        return key in self.db_machines_id_index
    
    def __get_db_vistrail_id(self):
        return self._db_vistrail_id
    def __set_db_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
    db_vistrail_id = property(__get_db_vistrail_id, __set_db_vistrail_id)
    def db_add_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
    def db_change_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
    def db_delete_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBMachine(object):

    vtType = 'machine'

    def __init__(self, id=None, name=None, os=None, architecture=None, processor=None, ram=None):
        self._db_id = id
        self._db_name = name
        self._db_os = os
        self._db_architecture = architecture
        self._db_processor = processor
        self._db_ram = ram
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMachine.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMachine(id=self._db_id,
                       name=self._db_name,
                       os=self._db_os,
                       architecture=self._db_architecture,
                       processor=self._db_processor,
                       ram=self._db_ram)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_vistrailId') and ('vistrail', self._db_vistrailId) in id_remap:
                cp._db_vistrailId = id_remap[('vistrail', self._db_vistrailId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBMachine()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'os' in class_dict:
            res = class_dict['os'](old_obj, trans_dict)
            new_obj.db_os = res
        elif hasattr(old_obj, 'db_os') and old_obj.db_os is not None:
            new_obj.db_os = old_obj.db_os
        if 'architecture' in class_dict:
            res = class_dict['architecture'](old_obj, trans_dict)
            new_obj.db_architecture = res
        elif hasattr(old_obj, 'db_architecture') and old_obj.db_architecture is not None:
            new_obj.db_architecture = old_obj.db_architecture
        if 'processor' in class_dict:
            res = class_dict['processor'](old_obj, trans_dict)
            new_obj.db_processor = res
        elif hasattr(old_obj, 'db_processor') and old_obj.db_processor is not None:
            new_obj.db_processor = old_obj.db_processor
        if 'ram' in class_dict:
            res = class_dict['ram'](old_obj, trans_dict)
            new_obj.db_ram = res
        elif hasattr(old_obj, 'db_ram') and old_obj.db_ram is not None:
            new_obj.db_ram = old_obj.db_ram
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_os(self):
        return self._db_os
    def __set_db_os(self, os):
        self._db_os = os
        self.is_dirty = True
    db_os = property(__get_db_os, __set_db_os)
    def db_add_os(self, os):
        self._db_os = os
    def db_change_os(self, os):
        self._db_os = os
    def db_delete_os(self, os):
        self._db_os = None
    
    def __get_db_architecture(self):
        return self._db_architecture
    def __set_db_architecture(self, architecture):
        self._db_architecture = architecture
        self.is_dirty = True
    db_architecture = property(__get_db_architecture, __set_db_architecture)
    def db_add_architecture(self, architecture):
        self._db_architecture = architecture
    def db_change_architecture(self, architecture):
        self._db_architecture = architecture
    def db_delete_architecture(self, architecture):
        self._db_architecture = None
    
    def __get_db_processor(self):
        return self._db_processor
    def __set_db_processor(self, processor):
        self._db_processor = processor
        self.is_dirty = True
    db_processor = property(__get_db_processor, __set_db_processor)
    def db_add_processor(self, processor):
        self._db_processor = processor
    def db_change_processor(self, processor):
        self._db_processor = processor
    def db_delete_processor(self, processor):
        self._db_processor = None
    
    def __get_db_ram(self):
        return self._db_ram
    def __set_db_ram(self, ram):
        self._db_ram = ram
        self.is_dirty = True
    db_ram = property(__get_db_ram, __set_db_ram)
    def db_add_ram(self, ram):
        self._db_ram = ram
    def db_change_ram(self, ram):
        self._db_ram = ram
    def db_delete_ram(self, ram):
        self._db_ram = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBAdd(object):

    vtType = 'add'

    def __init__(self, data=None, id=None, what=None, objectId=None, parentObjId=None, parentObjType=None):
        self.db_deleted_data = []
        self._db_data = data
        self._db_id = id
        self._db_what = what
        self._db_objectId = objectId
        self._db_parentObjId = parentObjId
        self._db_parentObjType = parentObjType
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAdd.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAdd(id=self._db_id,
                   what=self._db_what,
                   objectId=self._db_objectId,
                   parentObjId=self._db_parentObjId,
                   parentObjType=self._db_parentObjType)
        if self._db_data is not None:
            cp._db_data = self._db_data.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_objectId') and (self._db_what, self._db_objectId) in id_remap:
                cp._db_objectId = id_remap[(self._db_what, self._db_objectId)]
            if hasattr(self, 'db_parentObjId') and (self._db_parentObjType, self._db_parentObjId) in id_remap:
                cp._db_parentObjId = id_remap[(self._db_parentObjType, self._db_parentObjId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAdd()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'data' in class_dict:
            res = class_dict['data'](old_obj, trans_dict)
            new_obj.db_data = res
        elif hasattr(old_obj, 'db_data') and old_obj.db_data is not None:
            obj = old_obj.db_data
            if obj.vtType == 'module':
                new_obj.db_add_data(DBModule.update_version(obj, trans_dict))
            elif obj.vtType == 'location':
                new_obj.db_add_data(DBLocation.update_version(obj, trans_dict))
            elif obj.vtType == 'annotation':
                new_obj.db_add_data(DBAnnotation.update_version(obj, trans_dict))
            elif obj.vtType == 'function':
                new_obj.db_add_data(DBFunction.update_version(obj, trans_dict))
            elif obj.vtType == 'connection':
                new_obj.db_add_data(DBConnection.update_version(obj, trans_dict))
            elif obj.vtType == 'port':
                new_obj.db_add_data(DBPort.update_version(obj, trans_dict))
            elif obj.vtType == 'parameter':
                new_obj.db_add_data(DBParameter.update_version(obj, trans_dict))
            elif obj.vtType == 'portSpec':
                new_obj.db_add_data(DBPortSpec.update_version(obj, trans_dict))
            elif obj.vtType == 'abstraction':
                new_obj.db_add_data(DBAbstraction.update_version(obj, trans_dict))
            elif obj.vtType == 'group':
                new_obj.db_add_data(DBGroup.update_version(obj, trans_dict))
            elif obj.vtType == 'other':
                new_obj.db_add_data(DBOther.update_version(obj, trans_dict))
            elif obj.vtType == 'plugin_data':
                new_obj.db_add_data(DBPluginData.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_data') and hasattr(new_obj, 'db_deleted_data'):
            for obj in old_obj.db_deleted_data:
                if obj.vtType == 'module':
                    n_obj = DBModule.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'location':
                    n_obj = DBLocation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'annotation':
                    n_obj = DBAnnotation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'function':
                    n_obj = DBFunction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'connection':
                    n_obj = DBConnection.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'port':
                    n_obj = DBPort.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'parameter':
                    n_obj = DBParameter.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'portSpec':
                    n_obj = DBPortSpec.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'abstraction':
                    n_obj = DBAbstraction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'group':
                    n_obj = DBGroup.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'other':
                    n_obj = DBOther.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'plugin_data':
                    n_obj = DBPluginData.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'what' in class_dict:
            res = class_dict['what'](old_obj, trans_dict)
            new_obj.db_what = res
        elif hasattr(old_obj, 'db_what') and old_obj.db_what is not None:
            new_obj.db_what = old_obj.db_what
        if 'objectId' in class_dict:
            res = class_dict['objectId'](old_obj, trans_dict)
            new_obj.db_objectId = res
        elif hasattr(old_obj, 'db_objectId') and old_obj.db_objectId is not None:
            new_obj.db_objectId = old_obj.db_objectId
        if 'parentObjId' in class_dict:
            res = class_dict['parentObjId'](old_obj, trans_dict)
            new_obj.db_parentObjId = res
        elif hasattr(old_obj, 'db_parentObjId') and old_obj.db_parentObjId is not None:
            new_obj.db_parentObjId = old_obj.db_parentObjId
        if 'parentObjType' in class_dict:
            res = class_dict['parentObjType'](old_obj, trans_dict)
            new_obj.db_parentObjType = res
        elif hasattr(old_obj, 'db_parentObjType') and old_obj.db_parentObjType is not None:
            new_obj.db_parentObjType = old_obj.db_parentObjType
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_data is not None:
            children.extend(self._db_data.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_data = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_data)
        if remove:
            self.db_deleted_data = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_data is not None and self._db_data.has_changes():
            return True
        return False
    def __get_db_data(self):
        return self._db_data
    def __set_db_data(self, data):
        self._db_data = data
        self.is_dirty = True
    db_data = property(__get_db_data, __set_db_data)
    def db_add_data(self, data):
        self._db_data = data
    def db_change_data(self, data):
        self._db_data = data
    def db_delete_data(self, data):
        if not self.is_new:
            self.db_deleted_data.append(self._db_data)
        self._db_data = None
    
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_what(self):
        return self._db_what
    def __set_db_what(self, what):
        self._db_what = what
        self.is_dirty = True
    db_what = property(__get_db_what, __set_db_what)
    def db_add_what(self, what):
        self._db_what = what
    def db_change_what(self, what):
        self._db_what = what
    def db_delete_what(self, what):
        self._db_what = None
    
    def __get_db_objectId(self):
        return self._db_objectId
    def __set_db_objectId(self, objectId):
        self._db_objectId = objectId
        self.is_dirty = True
    db_objectId = property(__get_db_objectId, __set_db_objectId)
    def db_add_objectId(self, objectId):
        self._db_objectId = objectId
    def db_change_objectId(self, objectId):
        self._db_objectId = objectId
    def db_delete_objectId(self, objectId):
        self._db_objectId = None
    
    def __get_db_parentObjId(self):
        return self._db_parentObjId
    def __set_db_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
        self.is_dirty = True
    db_parentObjId = property(__get_db_parentObjId, __set_db_parentObjId)
    def db_add_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_change_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_delete_parentObjId(self, parentObjId):
        self._db_parentObjId = None
    
    def __get_db_parentObjType(self):
        return self._db_parentObjType
    def __set_db_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
        self.is_dirty = True
    db_parentObjType = property(__get_db_parentObjType, __set_db_parentObjType)
    def db_add_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_change_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_delete_parentObjType(self, parentObjType):
        self._db_parentObjType = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBOther(object):

    vtType = 'other'

    def __init__(self, id=None, key=None, value=None):
        self._db_id = id
        self._db_key = key
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOther.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOther(id=self._db_id,
                     key=self._db_key,
                     value=self._db_value)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOther()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'key' in class_dict:
            res = class_dict['key'](old_obj, trans_dict)
            new_obj.db_key = res
        elif hasattr(old_obj, 'db_key') and old_obj.db_key is not None:
            new_obj.db_key = old_obj.db_key
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_key(self):
        return self._db_key
    def __set_db_key(self, key):
        self._db_key = key
        self.is_dirty = True
    db_key = property(__get_db_key, __set_db_key)
    def db_add_key(self, key):
        self._db_key = key
    def db_change_key(self, key):
        self._db_key = key
    def db_delete_key(self, key):
        self._db_key = None
    
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        self._db_value = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBLocation(object):

    vtType = 'location'

    def __init__(self, id=None, x=None, y=None):
        self._db_id = id
        self._db_x = x
        self._db_y = y
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBLocation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLocation(id=self._db_id,
                        x=self._db_x,
                        y=self._db_y)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBLocation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'x' in class_dict:
            res = class_dict['x'](old_obj, trans_dict)
            new_obj.db_x = res
        elif hasattr(old_obj, 'db_x') and old_obj.db_x is not None:
            new_obj.db_x = old_obj.db_x
        if 'y' in class_dict:
            res = class_dict['y'](old_obj, trans_dict)
            new_obj.db_y = res
        elif hasattr(old_obj, 'db_y') and old_obj.db_y is not None:
            new_obj.db_y = old_obj.db_y
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_x(self):
        return self._db_x
    def __set_db_x(self, x):
        self._db_x = x
        self.is_dirty = True
    db_x = property(__get_db_x, __set_db_x)
    def db_add_x(self, x):
        self._db_x = x
    def db_change_x(self, x):
        self._db_x = x
    def db_delete_x(self, x):
        self._db_x = None
    
    def __get_db_y(self):
        return self._db_y
    def __set_db_y(self, y):
        self._db_y = y
        self.is_dirty = True
    db_y = property(__get_db_y, __set_db_y)
    def db_add_y(self, y):
        self._db_y = y
    def db_change_y(self, y):
        self._db_y = y
    def db_delete_y(self, y):
        self._db_y = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBParameter(object):

    vtType = 'parameter'

    def __init__(self, id=None, pos=None, name=None, type=None, val=None, alias=None):
        self._db_id = id
        self._db_pos = pos
        self._db_name = name
        self._db_type = type
        self._db_val = val
        self._db_alias = alias
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBParameter.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBParameter(id=self._db_id,
                         pos=self._db_pos,
                         name=self._db_name,
                         type=self._db_type,
                         val=self._db_val,
                         alias=self._db_alias)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBParameter()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'val' in class_dict:
            res = class_dict['val'](old_obj, trans_dict)
            new_obj.db_val = res
        elif hasattr(old_obj, 'db_val') and old_obj.db_val is not None:
            new_obj.db_val = old_obj.db_val
        if 'alias' in class_dict:
            res = class_dict['alias'](old_obj, trans_dict)
            new_obj.db_alias = res
        elif hasattr(old_obj, 'db_alias') and old_obj.db_alias is not None:
            new_obj.db_alias = old_obj.db_alias
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_val(self):
        return self._db_val
    def __set_db_val(self, val):
        self._db_val = val
        self.is_dirty = True
    db_val = property(__get_db_val, __set_db_val)
    def db_add_val(self, val):
        self._db_val = val
    def db_change_val(self, val):
        self._db_val = val
    def db_delete_val(self, val):
        self._db_val = None
    
    def __get_db_alias(self):
        return self._db_alias
    def __set_db_alias(self, alias):
        self._db_alias = alias
        self.is_dirty = True
    db_alias = property(__get_db_alias, __set_db_alias)
    def db_add_alias(self, alias):
        self._db_alias = alias
    def db_change_alias(self, alias):
        self._db_alias = alias
    def db_delete_alias(self, alias):
        self._db_alias = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBPluginData(object):

    vtType = 'plugin_data'

    def __init__(self, id=None, data=None):
        self._db_id = id
        self._db_data = data
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPluginData.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPluginData(id=self._db_id,
                          data=self._db_data)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPluginData()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'data' in class_dict:
            res = class_dict['data'](old_obj, trans_dict)
            new_obj.db_data = res
        elif hasattr(old_obj, 'db_data') and old_obj.db_data is not None:
            new_obj.db_data = old_obj.db_data
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_data(self):
        return self._db_data
    def __set_db_data(self, data):
        self._db_data = data
        self.is_dirty = True
    db_data = property(__get_db_data, __set_db_data)
    def db_add_data(self, data):
        self._db_data = data
    def db_change_data(self, data):
        self._db_data = data
    def db_delete_data(self, data):
        self._db_data = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBFunction(object):

    vtType = 'function'

    def __init__(self, id=None, pos=None, name=None, parameters=None):
        self._db_id = id
        self._db_pos = pos
        self._db_name = name
        self.db_deleted_parameters = []
        self.db_parameters_id_index = {}
        if parameters is None:
            self._db_parameters = []
        else:
            self._db_parameters = parameters
            for v in self._db_parameters:
                self.db_parameters_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBFunction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBFunction(id=self._db_id,
                        pos=self._db_pos,
                        name=self._db_name)
        if self._db_parameters is None:
            cp._db_parameters = []
        else:
            cp._db_parameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_parameters]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_parameters_id_index = dict((v.db_id, v) for v in cp._db_parameters)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBFunction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'parameters' in class_dict:
            res = class_dict['parameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_parameter(obj)
        elif hasattr(old_obj, 'db_parameters') and old_obj.db_parameters is not None:
            for obj in old_obj.db_parameters:
                new_obj.db_add_parameter(DBParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_parameters') and hasattr(new_obj, 'db_deleted_parameters'):
            for obj in old_obj.db_deleted_parameters:
                n_obj = DBParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_parameters.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_parameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_parameter(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_parameters)
        if remove:
            self.db_deleted_parameters = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_parameters:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_parameters(self):
        return self._db_parameters
    def __set_db_parameters(self, parameters):
        self._db_parameters = parameters
        self.is_dirty = True
    db_parameters = property(__get_db_parameters, __set_db_parameters)
    def db_get_parameters(self):
        return self._db_parameters
    def db_add_parameter(self, parameter):
        self.is_dirty = True
        self._db_parameters.append(parameter)
        self.db_parameters_id_index[parameter.db_id] = parameter
    def db_change_parameter(self, parameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == parameter.db_id:
                self._db_parameters[i] = parameter
                found = True
                break
        if not found:
            self._db_parameters.append(parameter)
        self.db_parameters_id_index[parameter.db_id] = parameter
    def db_delete_parameter(self, parameter):
        self.is_dirty = True
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == parameter.db_id:
                if not self._db_parameters[i].is_new:
                    self.db_deleted_parameters.append(self._db_parameters[i])
                del self._db_parameters[i]
                break
        del self.db_parameters_id_index[parameter.db_id]
    def db_get_parameter(self, key):
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == key:
                return self._db_parameters[i]
        return None
    def db_get_parameter_by_id(self, key):
        return self.db_parameters_id_index[key]
    def db_has_parameter_with_id(self, key):
        return key in self.db_parameters_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBAbstraction(object):

    vtType = 'abstraction'

    def __init__(self, id=None, cache=None, name=None, namespace=None, package=None, version=None, internal_version=None, tag=None, location=None, functions=None, annotations=None):
        self._db_id = id
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_internal_version = internal_version
        self._db_tag = tag
        self.db_deleted_location = []
        self._db_location = location
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        self.db_annotations_key_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
                self.db_annotations_key_index[v.db_key] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAbstraction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAbstraction(id=self._db_id,
                           cache=self._db_cache,
                           name=self._db_name,
                           namespace=self._db_namespace,
                           package=self._db_package,
                           version=self._db_version,
                           internal_version=self._db_internal_version,
                           tag=self._db_tag)
        if self._db_location is not None:
            cp._db_location = self._db_location.do_copy(new_ids, id_scope, id_remap)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAbstraction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'cache' in class_dict:
            res = class_dict['cache'](old_obj, trans_dict)
            new_obj.db_cache = res
        elif hasattr(old_obj, 'db_cache') and old_obj.db_cache is not None:
            new_obj.db_cache = old_obj.db_cache
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'internal_version' in class_dict:
            res = class_dict['internal_version'](old_obj, trans_dict)
            new_obj.db_internal_version = res
        elif hasattr(old_obj, 'db_internal_version') and old_obj.db_internal_version is not None:
            new_obj.db_internal_version = old_obj.db_internal_version
        if 'tag' in class_dict:
            res = class_dict['tag'](old_obj, trans_dict)
            new_obj.db_tag = res
        elif hasattr(old_obj, 'db_tag') and old_obj.db_tag is not None:
            new_obj.db_tag = old_obj.db_tag
        if 'location' in class_dict:
            res = class_dict['location'](old_obj, trans_dict)
            new_obj.db_location = res
        elif hasattr(old_obj, 'db_location') and old_obj.db_location is not None:
            obj = old_obj.db_location
            new_obj.db_add_location(DBLocation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_location') and hasattr(new_obj, 'db_deleted_location'):
            for obj in old_obj.db_deleted_location:
                n_obj = DBLocation.update_version(obj, trans_dict)
                new_obj.db_deleted_location.append(n_obj)
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        if remove:
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_location is not None and self._db_location.has_changes():
            return True
        for child in self._db_functions:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_cache(self):
        return self._db_cache
    def __set_db_cache(self, cache):
        self._db_cache = cache
        self.is_dirty = True
    db_cache = property(__get_db_cache, __set_db_cache)
    def db_add_cache(self, cache):
        self._db_cache = cache
    def db_change_cache(self, cache):
        self._db_cache = cache
    def db_delete_cache(self, cache):
        self._db_cache = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_internal_version(self):
        return self._db_internal_version
    def __set_db_internal_version(self, internal_version):
        self._db_internal_version = internal_version
        self.is_dirty = True
    db_internal_version = property(__get_db_internal_version, __set_db_internal_version)
    def db_add_internal_version(self, internal_version):
        self._db_internal_version = internal_version
    def db_change_internal_version(self, internal_version):
        self._db_internal_version = internal_version
    def db_delete_internal_version(self, internal_version):
        self._db_internal_version = None
    
    def __get_db_tag(self):
        return self._db_tag
    def __set_db_tag(self, tag):
        self._db_tag = tag
        self.is_dirty = True
    db_tag = property(__get_db_tag, __set_db_tag)
    def db_add_tag(self, tag):
        self._db_tag = tag
    def db_change_tag(self, tag):
        self._db_tag = tag
    def db_delete_tag(self, tag):
        self._db_tag = None
    
    def __get_db_location(self):
        return self._db_location
    def __set_db_location(self, location):
        self._db_location = location
        self.is_dirty = True
    db_location = property(__get_db_location, __set_db_location)
    def db_add_location(self, location):
        self._db_location = location
    def db_change_location(self, location):
        self._db_location = location
    def db_delete_location(self, location):
        if not self.is_new:
            self.db_deleted_location.append(self._db_location)
        self._db_location = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
        del self.db_annotations_key_index[annotation.db_key]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    def db_get_annotation_by_key(self, key):
        return self.db_annotations_key_index[key]
    def db_has_annotation_with_key(self, key):
        return key in self.db_annotations_key_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBWorkflow(object):

    vtType = 'workflow'

    def __init__(self, modules=None, id=None, entity_type=None, name=None, version=None, last_modified=None, connections=None, annotations=None, plugin_datas=None, others=None, vistrail_id=None):
        self.db_deleted_modules = []
        self.db_modules_id_index = {}
        if modules is None:
            self._db_modules = []
        else:
            self._db_modules = modules
            for v in self._db_modules:
                self.db_modules_id_index[v.db_id] = v
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_name = name
        self._db_version = version
        self._db_last_modified = last_modified
        self.db_deleted_connections = []
        self.db_connections_id_index = {}
        if connections is None:
            self._db_connections = []
        else:
            self._db_connections = connections
            for v in self._db_connections:
                self.db_connections_id_index[v.db_id] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
        self.db_deleted_plugin_datas = []
        self.db_plugin_datas_id_index = {}
        if plugin_datas is None:
            self._db_plugin_datas = []
        else:
            self._db_plugin_datas = plugin_datas
            for v in self._db_plugin_datas:
                self.db_plugin_datas_id_index[v.db_id] = v
        self.db_deleted_others = []
        self.db_others_id_index = {}
        if others is None:
            self._db_others = []
        else:
            self._db_others = others
            for v in self._db_others:
                self.db_others_id_index[v.db_id] = v
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBWorkflow.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflow(id=self._db_id,
                        entity_type=self._db_entity_type,
                        name=self._db_name,
                        version=self._db_version,
                        last_modified=self._db_last_modified,
                        vistrail_id=self._db_vistrail_id)
        if self._db_modules is None:
            cp._db_modules = []
        else:
            cp._db_modules = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_modules]
        if self._db_connections is None:
            cp._db_connections = []
        else:
            cp._db_connections = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_connections]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_plugin_datas is None:
            cp._db_plugin_datas = []
        else:
            cp._db_plugin_datas = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_plugin_datas]
        if self._db_others is None:
            cp._db_others = []
        else:
            cp._db_others = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_others]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_vistrail_id') and ('vistrail', self._db_vistrail_id) in id_remap:
                cp._db_vistrail_id = id_remap[('vistrail', self._db_vistrail_id)]
        
        # recreate indices and set flags
        cp.db_modules_id_index = dict((v.db_id, v) for v in cp._db_modules)
        cp.db_connections_id_index = dict((v.db_id, v) for v in cp._db_connections)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_plugin_datas_id_index = dict((v.db_id, v) for v in cp._db_plugin_datas)
        cp.db_others_id_index = dict((v.db_id, v) for v in cp._db_others)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBWorkflow()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'modules' in class_dict:
            res = class_dict['modules'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_module(obj)
        elif hasattr(old_obj, 'db_modules') and old_obj.db_modules is not None:
            for obj in old_obj.db_modules:
                if obj.vtType == 'module':
                    new_obj.db_add_module(DBModule.update_version(obj, trans_dict))
                elif obj.vtType == 'abstraction':
                    new_obj.db_add_module(DBAbstraction.update_version(obj, trans_dict))
                elif obj.vtType == 'group':
                    new_obj.db_add_module(DBGroup.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_modules') and hasattr(new_obj, 'db_deleted_modules'):
            for obj in old_obj.db_deleted_modules:
                if obj.vtType == 'module':
                    n_obj = DBModule.update_version(obj, trans_dict)
                    new_obj.db_deleted_modules.append(n_obj)
                elif obj.vtType == 'abstraction':
                    n_obj = DBAbstraction.update_version(obj, trans_dict)
                    new_obj.db_deleted_modules.append(n_obj)
                elif obj.vtType == 'group':
                    n_obj = DBGroup.update_version(obj, trans_dict)
                    new_obj.db_deleted_modules.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'entity_type' in class_dict:
            res = class_dict['entity_type'](old_obj, trans_dict)
            new_obj.db_entity_type = res
        elif hasattr(old_obj, 'db_entity_type') and old_obj.db_entity_type is not None:
            new_obj.db_entity_type = old_obj.db_entity_type
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'last_modified' in class_dict:
            res = class_dict['last_modified'](old_obj, trans_dict)
            new_obj.db_last_modified = res
        elif hasattr(old_obj, 'db_last_modified') and old_obj.db_last_modified is not None:
            new_obj.db_last_modified = old_obj.db_last_modified
        if 'connections' in class_dict:
            res = class_dict['connections'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_connection(obj)
        elif hasattr(old_obj, 'db_connections') and old_obj.db_connections is not None:
            for obj in old_obj.db_connections:
                new_obj.db_add_connection(DBConnection.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_connections') and hasattr(new_obj, 'db_deleted_connections'):
            for obj in old_obj.db_deleted_connections:
                n_obj = DBConnection.update_version(obj, trans_dict)
                new_obj.db_deleted_connections.append(n_obj)
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        if 'plugin_datas' in class_dict:
            res = class_dict['plugin_datas'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_plugin_data(obj)
        elif hasattr(old_obj, 'db_plugin_datas') and old_obj.db_plugin_datas is not None:
            for obj in old_obj.db_plugin_datas:
                new_obj.db_add_plugin_data(DBPluginData.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_plugin_datas') and hasattr(new_obj, 'db_deleted_plugin_datas'):
            for obj in old_obj.db_deleted_plugin_datas:
                n_obj = DBPluginData.update_version(obj, trans_dict)
                new_obj.db_deleted_plugin_datas.append(n_obj)
        if 'others' in class_dict:
            res = class_dict['others'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_other(obj)
        elif hasattr(old_obj, 'db_others') and old_obj.db_others is not None:
            for obj in old_obj.db_others:
                new_obj.db_add_other(DBOther.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_others') and hasattr(new_obj, 'db_deleted_others'):
            for obj in old_obj.db_deleted_others:
                n_obj = DBOther.update_version(obj, trans_dict)
                new_obj.db_deleted_others.append(n_obj)
        if 'vistrail_id' in class_dict:
            res = class_dict['vistrail_id'](old_obj, trans_dict)
            new_obj.db_vistrail_id = res
        elif hasattr(old_obj, 'db_vistrail_id') and old_obj.db_vistrail_id is not None:
            new_obj.db_vistrail_id = old_obj.db_vistrail_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_connections:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_connection(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_plugin_datas:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_plugin_data(child)
        to_del = []
        for child in self.db_others:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_other(child)
        to_del = []
        for child in self.db_modules:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_module(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_connections)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_plugin_datas)
        children.extend(self.db_deleted_others)
        children.extend(self.db_deleted_modules)
        if remove:
            self.db_deleted_connections = []
            self.db_deleted_annotations = []
            self.db_deleted_plugin_datas = []
            self.db_deleted_others = []
            self.db_deleted_modules = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_connections:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_plugin_datas:
            if child.has_changes():
                return True
        for child in self._db_others:
            if child.has_changes():
                return True
        for child in self._db_modules:
            if child.has_changes():
                return True
        return False
    def __get_db_modules(self):
        return self._db_modules
    def __set_db_modules(self, modules):
        self._db_modules = modules
        self.is_dirty = True
    db_modules = property(__get_db_modules, __set_db_modules)
    def db_get_modules(self):
        return self._db_modules
    def db_add_module(self, module):
        self.is_dirty = True
        self._db_modules.append(module)
        self.db_modules_id_index[module.db_id] = module
    def db_change_module(self, module):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_modules)):
            if self._db_modules[i].db_id == module.db_id:
                self._db_modules[i] = module
                found = True
                break
        if not found:
            self._db_modules.append(module)
        self.db_modules_id_index[module.db_id] = module
    def db_delete_module(self, module):
        self.is_dirty = True
        for i in xrange(len(self._db_modules)):
            if self._db_modules[i].db_id == module.db_id:
                if not self._db_modules[i].is_new:
                    self.db_deleted_modules.append(self._db_modules[i])
                del self._db_modules[i]
                break
        del self.db_modules_id_index[module.db_id]
    def db_get_module(self, key):
        for i in xrange(len(self._db_modules)):
            if self._db_modules[i].db_id == key:
                return self._db_modules[i]
        return None
    def db_get_module_by_id(self, key):
        return self.db_modules_id_index[key]
    def db_has_module_with_id(self, key):
        return key in self.db_modules_id_index
    
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_entity_type(self):
        return self._db_entity_type
    def __set_db_entity_type(self, entity_type):
        self._db_entity_type = entity_type
        self.is_dirty = True
    db_entity_type = property(__get_db_entity_type, __set_db_entity_type)
    def db_add_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_change_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_delete_entity_type(self, entity_type):
        self._db_entity_type = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_last_modified(self):
        return self._db_last_modified
    def __set_db_last_modified(self, last_modified):
        self._db_last_modified = last_modified
        self.is_dirty = True
    db_last_modified = property(__get_db_last_modified, __set_db_last_modified)
    def db_add_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_change_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_delete_last_modified(self, last_modified):
        self._db_last_modified = None
    
    def __get_db_connections(self):
        return self._db_connections
    def __set_db_connections(self, connections):
        self._db_connections = connections
        self.is_dirty = True
    db_connections = property(__get_db_connections, __set_db_connections)
    def db_get_connections(self):
        return self._db_connections
    def db_add_connection(self, connection):
        self.is_dirty = True
        self._db_connections.append(connection)
        self.db_connections_id_index[connection.db_id] = connection
    def db_change_connection(self, connection):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_connections)):
            if self._db_connections[i].db_id == connection.db_id:
                self._db_connections[i] = connection
                found = True
                break
        if not found:
            self._db_connections.append(connection)
        self.db_connections_id_index[connection.db_id] = connection
    def db_delete_connection(self, connection):
        self.is_dirty = True
        for i in xrange(len(self._db_connections)):
            if self._db_connections[i].db_id == connection.db_id:
                if not self._db_connections[i].is_new:
                    self.db_deleted_connections.append(self._db_connections[i])
                del self._db_connections[i]
                break
        del self.db_connections_id_index[connection.db_id]
    def db_get_connection(self, key):
        for i in xrange(len(self._db_connections)):
            if self._db_connections[i].db_id == key:
                return self._db_connections[i]
        return None
    def db_get_connection_by_id(self, key):
        return self.db_connections_id_index[key]
    def db_has_connection_with_id(self, key):
        return key in self.db_connections_id_index
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    
    def __get_db_plugin_datas(self):
        return self._db_plugin_datas
    def __set_db_plugin_datas(self, plugin_datas):
        self._db_plugin_datas = plugin_datas
        self.is_dirty = True
    db_plugin_datas = property(__get_db_plugin_datas, __set_db_plugin_datas)
    def db_get_plugin_datas(self):
        return self._db_plugin_datas
    def db_add_plugin_data(self, plugin_data):
        self.is_dirty = True
        self._db_plugin_datas.append(plugin_data)
        self.db_plugin_datas_id_index[plugin_data.db_id] = plugin_data
    def db_change_plugin_data(self, plugin_data):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_plugin_datas)):
            if self._db_plugin_datas[i].db_id == plugin_data.db_id:
                self._db_plugin_datas[i] = plugin_data
                found = True
                break
        if not found:
            self._db_plugin_datas.append(plugin_data)
        self.db_plugin_datas_id_index[plugin_data.db_id] = plugin_data
    def db_delete_plugin_data(self, plugin_data):
        self.is_dirty = True
        for i in xrange(len(self._db_plugin_datas)):
            if self._db_plugin_datas[i].db_id == plugin_data.db_id:
                if not self._db_plugin_datas[i].is_new:
                    self.db_deleted_plugin_datas.append(self._db_plugin_datas[i])
                del self._db_plugin_datas[i]
                break
        del self.db_plugin_datas_id_index[plugin_data.db_id]
    def db_get_plugin_data(self, key):
        for i in xrange(len(self._db_plugin_datas)):
            if self._db_plugin_datas[i].db_id == key:
                return self._db_plugin_datas[i]
        return None
    def db_get_plugin_data_by_id(self, key):
        return self.db_plugin_datas_id_index[key]
    def db_has_plugin_data_with_id(self, key):
        return key in self.db_plugin_datas_id_index
    
    def __get_db_others(self):
        return self._db_others
    def __set_db_others(self, others):
        self._db_others = others
        self.is_dirty = True
    db_others = property(__get_db_others, __set_db_others)
    def db_get_others(self):
        return self._db_others
    def db_add_other(self, other):
        self.is_dirty = True
        self._db_others.append(other)
        self.db_others_id_index[other.db_id] = other
    def db_change_other(self, other):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_others)):
            if self._db_others[i].db_id == other.db_id:
                self._db_others[i] = other
                found = True
                break
        if not found:
            self._db_others.append(other)
        self.db_others_id_index[other.db_id] = other
    def db_delete_other(self, other):
        self.is_dirty = True
        for i in xrange(len(self._db_others)):
            if self._db_others[i].db_id == other.db_id:
                if not self._db_others[i].is_new:
                    self.db_deleted_others.append(self._db_others[i])
                del self._db_others[i]
                break
        del self.db_others_id_index[other.db_id]
    def db_get_other(self, key):
        for i in xrange(len(self._db_others)):
            if self._db_others[i].db_id == key:
                return self._db_others[i]
        return None
    def db_get_other_by_id(self, key):
        return self.db_others_id_index[key]
    def db_has_other_with_id(self, key):
        return key in self.db_others_id_index
    
    def __get_db_vistrail_id(self):
        return self._db_vistrail_id
    def __set_db_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
    db_vistrail_id = property(__get_db_vistrail_id, __set_db_vistrail_id)
    def db_add_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
    def db_change_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
    def db_delete_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBAnnotation(object):

    vtType = 'annotation'

    def __init__(self, id=None, key=None, value=None):
        self._db_id = id
        self._db_key = key
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAnnotation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAnnotation(id=self._db_id,
                          key=self._db_key,
                          value=self._db_value)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAnnotation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'key' in class_dict:
            res = class_dict['key'](old_obj, trans_dict)
            new_obj.db_key = res
        elif hasattr(old_obj, 'db_key') and old_obj.db_key is not None:
            new_obj.db_key = old_obj.db_key
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_key(self):
        return self._db_key
    def __set_db_key(self, key):
        self._db_key = key
        self.is_dirty = True
    db_key = property(__get_db_key, __set_db_key)
    def db_add_key(self, key):
        self._db_key = key
    def db_change_key(self, key):
        self._db_key = key
    def db_delete_key(self, key):
        self._db_key = None
    
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        self._db_value = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBChange(object):

    vtType = 'change'

    def __init__(self, data=None, id=None, what=None, oldObjId=None, newObjId=None, parentObjId=None, parentObjType=None):
        self.db_deleted_data = []
        self._db_data = data
        self._db_id = id
        self._db_what = what
        self._db_oldObjId = oldObjId
        self._db_newObjId = newObjId
        self._db_parentObjId = parentObjId
        self._db_parentObjType = parentObjType
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBChange.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBChange(id=self._db_id,
                      what=self._db_what,
                      oldObjId=self._db_oldObjId,
                      newObjId=self._db_newObjId,
                      parentObjId=self._db_parentObjId,
                      parentObjType=self._db_parentObjType)
        if self._db_data is not None:
            cp._db_data = self._db_data.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_oldObjId') and (self._db_what, self._db_oldObjId) in id_remap:
                cp._db_oldObjId = id_remap[(self._db_what, self._db_oldObjId)]
            if hasattr(self, 'db_newObjId') and (self._db_what, self._db_newObjId) in id_remap:
                cp._db_newObjId = id_remap[(self._db_what, self._db_newObjId)]
            if hasattr(self, 'db_parentObjId') and (self._db_parentObjType, self._db_parentObjId) in id_remap:
                cp._db_parentObjId = id_remap[(self._db_parentObjType, self._db_parentObjId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBChange()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'data' in class_dict:
            res = class_dict['data'](old_obj, trans_dict)
            new_obj.db_data = res
        elif hasattr(old_obj, 'db_data') and old_obj.db_data is not None:
            obj = old_obj.db_data
            if obj.vtType == 'module':
                new_obj.db_add_data(DBModule.update_version(obj, trans_dict))
            elif obj.vtType == 'location':
                new_obj.db_add_data(DBLocation.update_version(obj, trans_dict))
            elif obj.vtType == 'annotation':
                new_obj.db_add_data(DBAnnotation.update_version(obj, trans_dict))
            elif obj.vtType == 'function':
                new_obj.db_add_data(DBFunction.update_version(obj, trans_dict))
            elif obj.vtType == 'connection':
                new_obj.db_add_data(DBConnection.update_version(obj, trans_dict))
            elif obj.vtType == 'port':
                new_obj.db_add_data(DBPort.update_version(obj, trans_dict))
            elif obj.vtType == 'parameter':
                new_obj.db_add_data(DBParameter.update_version(obj, trans_dict))
            elif obj.vtType == 'portSpec':
                new_obj.db_add_data(DBPortSpec.update_version(obj, trans_dict))
            elif obj.vtType == 'abstraction':
                new_obj.db_add_data(DBAbstraction.update_version(obj, trans_dict))
            elif obj.vtType == 'group':
                new_obj.db_add_data(DBGroup.update_version(obj, trans_dict))
            elif obj.vtType == 'other':
                new_obj.db_add_data(DBOther.update_version(obj, trans_dict))
            elif obj.vtType == 'plugin_data':
                new_obj.db_add_data(DBPluginData.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_data') and hasattr(new_obj, 'db_deleted_data'):
            for obj in old_obj.db_deleted_data:
                if obj.vtType == 'module':
                    n_obj = DBModule.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'location':
                    n_obj = DBLocation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'annotation':
                    n_obj = DBAnnotation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'function':
                    n_obj = DBFunction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'connection':
                    n_obj = DBConnection.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'port':
                    n_obj = DBPort.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'parameter':
                    n_obj = DBParameter.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'portSpec':
                    n_obj = DBPortSpec.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'abstraction':
                    n_obj = DBAbstraction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'group':
                    n_obj = DBGroup.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'other':
                    n_obj = DBOther.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'plugin_data':
                    n_obj = DBPluginData.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'what' in class_dict:
            res = class_dict['what'](old_obj, trans_dict)
            new_obj.db_what = res
        elif hasattr(old_obj, 'db_what') and old_obj.db_what is not None:
            new_obj.db_what = old_obj.db_what
        if 'oldObjId' in class_dict:
            res = class_dict['oldObjId'](old_obj, trans_dict)
            new_obj.db_oldObjId = res
        elif hasattr(old_obj, 'db_oldObjId') and old_obj.db_oldObjId is not None:
            new_obj.db_oldObjId = old_obj.db_oldObjId
        if 'newObjId' in class_dict:
            res = class_dict['newObjId'](old_obj, trans_dict)
            new_obj.db_newObjId = res
        elif hasattr(old_obj, 'db_newObjId') and old_obj.db_newObjId is not None:
            new_obj.db_newObjId = old_obj.db_newObjId
        if 'parentObjId' in class_dict:
            res = class_dict['parentObjId'](old_obj, trans_dict)
            new_obj.db_parentObjId = res
        elif hasattr(old_obj, 'db_parentObjId') and old_obj.db_parentObjId is not None:
            new_obj.db_parentObjId = old_obj.db_parentObjId
        if 'parentObjType' in class_dict:
            res = class_dict['parentObjType'](old_obj, trans_dict)
            new_obj.db_parentObjType = res
        elif hasattr(old_obj, 'db_parentObjType') and old_obj.db_parentObjType is not None:
            new_obj.db_parentObjType = old_obj.db_parentObjType
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_data is not None:
            children.extend(self._db_data.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_data = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_data)
        if remove:
            self.db_deleted_data = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_data is not None and self._db_data.has_changes():
            return True
        return False
    def __get_db_data(self):
        return self._db_data
    def __set_db_data(self, data):
        self._db_data = data
        self.is_dirty = True
    db_data = property(__get_db_data, __set_db_data)
    def db_add_data(self, data):
        self._db_data = data
    def db_change_data(self, data):
        self._db_data = data
    def db_delete_data(self, data):
        if not self.is_new:
            self.db_deleted_data.append(self._db_data)
        self._db_data = None
    
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_what(self):
        return self._db_what
    def __set_db_what(self, what):
        self._db_what = what
        self.is_dirty = True
    db_what = property(__get_db_what, __set_db_what)
    def db_add_what(self, what):
        self._db_what = what
    def db_change_what(self, what):
        self._db_what = what
    def db_delete_what(self, what):
        self._db_what = None
    
    def __get_db_oldObjId(self):
        return self._db_oldObjId
    def __set_db_oldObjId(self, oldObjId):
        self._db_oldObjId = oldObjId
        self.is_dirty = True
    db_oldObjId = property(__get_db_oldObjId, __set_db_oldObjId)
    def db_add_oldObjId(self, oldObjId):
        self._db_oldObjId = oldObjId
    def db_change_oldObjId(self, oldObjId):
        self._db_oldObjId = oldObjId
    def db_delete_oldObjId(self, oldObjId):
        self._db_oldObjId = None
    
    def __get_db_newObjId(self):
        return self._db_newObjId
    def __set_db_newObjId(self, newObjId):
        self._db_newObjId = newObjId
        self.is_dirty = True
    db_newObjId = property(__get_db_newObjId, __set_db_newObjId)
    def db_add_newObjId(self, newObjId):
        self._db_newObjId = newObjId
    def db_change_newObjId(self, newObjId):
        self._db_newObjId = newObjId
    def db_delete_newObjId(self, newObjId):
        self._db_newObjId = None
    
    def __get_db_parentObjId(self):
        return self._db_parentObjId
    def __set_db_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
        self.is_dirty = True
    db_parentObjId = property(__get_db_parentObjId, __set_db_parentObjId)
    def db_add_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_change_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_delete_parentObjId(self, parentObjId):
        self._db_parentObjId = None
    
    def __get_db_parentObjType(self):
        return self._db_parentObjType
    def __set_db_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
        self.is_dirty = True
    db_parentObjType = property(__get_db_parentObjType, __set_db_parentObjType)
    def db_add_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_change_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_delete_parentObjType(self, parentObjType):
        self._db_parentObjType = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBWorkflowExec(object):

    vtType = 'workflow_exec'

    def __init__(self, id=None, user=None, ip=None, session=None, vt_version=None, ts_start=None, ts_end=None, parent_id=None, parent_type=None, parent_version=None, completed=None, name=None, module_execs=None):
        self._db_id = id
        self._db_user = user
        self._db_ip = ip
        self._db_session = session
        self._db_vt_version = vt_version
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self._db_parent_id = parent_id
        self._db_parent_type = parent_type
        self._db_parent_version = parent_version
        self._db_completed = completed
        self._db_name = name
        self.db_deleted_module_execs = []
        self.db_module_execs_id_index = {}
        if module_execs is None:
            self._db_module_execs = []
        else:
            self._db_module_execs = module_execs
            for v in self._db_module_execs:
                self.db_module_execs_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBWorkflowExec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflowExec(id=self._db_id,
                            user=self._db_user,
                            ip=self._db_ip,
                            session=self._db_session,
                            vt_version=self._db_vt_version,
                            ts_start=self._db_ts_start,
                            ts_end=self._db_ts_end,
                            parent_id=self._db_parent_id,
                            parent_type=self._db_parent_type,
                            parent_version=self._db_parent_version,
                            completed=self._db_completed,
                            name=self._db_name)
        if self._db_module_execs is None:
            cp._db_module_execs = []
        else:
            cp._db_module_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_module_execs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_module_execs_id_index = dict((v.db_id, v) for v in cp._db_module_execs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBWorkflowExec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        if 'ip' in class_dict:
            res = class_dict['ip'](old_obj, trans_dict)
            new_obj.db_ip = res
        elif hasattr(old_obj, 'db_ip') and old_obj.db_ip is not None:
            new_obj.db_ip = old_obj.db_ip
        if 'session' in class_dict:
            res = class_dict['session'](old_obj, trans_dict)
            new_obj.db_session = res
        elif hasattr(old_obj, 'db_session') and old_obj.db_session is not None:
            new_obj.db_session = old_obj.db_session
        if 'vt_version' in class_dict:
            res = class_dict['vt_version'](old_obj, trans_dict)
            new_obj.db_vt_version = res
        elif hasattr(old_obj, 'db_vt_version') and old_obj.db_vt_version is not None:
            new_obj.db_vt_version = old_obj.db_vt_version
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'parent_id' in class_dict:
            res = class_dict['parent_id'](old_obj, trans_dict)
            new_obj.db_parent_id = res
        elif hasattr(old_obj, 'db_parent_id') and old_obj.db_parent_id is not None:
            new_obj.db_parent_id = old_obj.db_parent_id
        if 'parent_type' in class_dict:
            res = class_dict['parent_type'](old_obj, trans_dict)
            new_obj.db_parent_type = res
        elif hasattr(old_obj, 'db_parent_type') and old_obj.db_parent_type is not None:
            new_obj.db_parent_type = old_obj.db_parent_type
        if 'parent_version' in class_dict:
            res = class_dict['parent_version'](old_obj, trans_dict)
            new_obj.db_parent_version = res
        elif hasattr(old_obj, 'db_parent_version') and old_obj.db_parent_version is not None:
            new_obj.db_parent_version = old_obj.db_parent_version
        if 'completed' in class_dict:
            res = class_dict['completed'](old_obj, trans_dict)
            new_obj.db_completed = res
        elif hasattr(old_obj, 'db_completed') and old_obj.db_completed is not None:
            new_obj.db_completed = old_obj.db_completed
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'module_execs' in class_dict:
            res = class_dict['module_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_module_exec(obj)
        elif hasattr(old_obj, 'db_module_execs') and old_obj.db_module_execs is not None:
            for obj in old_obj.db_module_execs:
                new_obj.db_add_module_exec(DBModuleExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_module_execs') and hasattr(new_obj, 'db_deleted_module_execs'):
            for obj in old_obj.db_deleted_module_execs:
                n_obj = DBModuleExec.update_version(obj, trans_dict)
                new_obj.db_deleted_module_execs.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_module_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_module_exec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_module_execs)
        if remove:
            self.db_deleted_module_execs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_module_execs:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
    def __get_db_ip(self):
        return self._db_ip
    def __set_db_ip(self, ip):
        self._db_ip = ip
        self.is_dirty = True
    db_ip = property(__get_db_ip, __set_db_ip)
    def db_add_ip(self, ip):
        self._db_ip = ip
    def db_change_ip(self, ip):
        self._db_ip = ip
    def db_delete_ip(self, ip):
        self._db_ip = None
    
    def __get_db_session(self):
        return self._db_session
    def __set_db_session(self, session):
        self._db_session = session
        self.is_dirty = True
    db_session = property(__get_db_session, __set_db_session)
    def db_add_session(self, session):
        self._db_session = session
    def db_change_session(self, session):
        self._db_session = session
    def db_delete_session(self, session):
        self._db_session = None
    
    def __get_db_vt_version(self):
        return self._db_vt_version
    def __set_db_vt_version(self, vt_version):
        self._db_vt_version = vt_version
        self.is_dirty = True
    db_vt_version = property(__get_db_vt_version, __set_db_vt_version)
    def db_add_vt_version(self, vt_version):
        self._db_vt_version = vt_version
    def db_change_vt_version(self, vt_version):
        self._db_vt_version = vt_version
    def db_delete_vt_version(self, vt_version):
        self._db_vt_version = None
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_parent_id(self):
        return self._db_parent_id
    def __set_db_parent_id(self, parent_id):
        self._db_parent_id = parent_id
        self.is_dirty = True
    db_parent_id = property(__get_db_parent_id, __set_db_parent_id)
    def db_add_parent_id(self, parent_id):
        self._db_parent_id = parent_id
    def db_change_parent_id(self, parent_id):
        self._db_parent_id = parent_id
    def db_delete_parent_id(self, parent_id):
        self._db_parent_id = None
    
    def __get_db_parent_type(self):
        return self._db_parent_type
    def __set_db_parent_type(self, parent_type):
        self._db_parent_type = parent_type
        self.is_dirty = True
    db_parent_type = property(__get_db_parent_type, __set_db_parent_type)
    def db_add_parent_type(self, parent_type):
        self._db_parent_type = parent_type
    def db_change_parent_type(self, parent_type):
        self._db_parent_type = parent_type
    def db_delete_parent_type(self, parent_type):
        self._db_parent_type = None
    
    def __get_db_parent_version(self):
        return self._db_parent_version
    def __set_db_parent_version(self, parent_version):
        self._db_parent_version = parent_version
        self.is_dirty = True
    db_parent_version = property(__get_db_parent_version, __set_db_parent_version)
    def db_add_parent_version(self, parent_version):
        self._db_parent_version = parent_version
    def db_change_parent_version(self, parent_version):
        self._db_parent_version = parent_version
    def db_delete_parent_version(self, parent_version):
        self._db_parent_version = None
    
    def __get_db_completed(self):
        return self._db_completed
    def __set_db_completed(self, completed):
        self._db_completed = completed
        self.is_dirty = True
    db_completed = property(__get_db_completed, __set_db_completed)
    def db_add_completed(self, completed):
        self._db_completed = completed
    def db_change_completed(self, completed):
        self._db_completed = completed
    def db_delete_completed(self, completed):
        self._db_completed = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_module_execs(self):
        return self._db_module_execs
    def __set_db_module_execs(self, module_execs):
        self._db_module_execs = module_execs
        self.is_dirty = True
    db_module_execs = property(__get_db_module_execs, __set_db_module_execs)
    def db_get_module_execs(self):
        return self._db_module_execs
    def db_add_module_exec(self, module_exec):
        self.is_dirty = True
        self._db_module_execs.append(module_exec)
        self.db_module_execs_id_index[module_exec.db_id] = module_exec
    def db_change_module_exec(self, module_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_module_execs)):
            if self._db_module_execs[i].db_id == module_exec.db_id:
                self._db_module_execs[i] = module_exec
                found = True
                break
        if not found:
            self._db_module_execs.append(module_exec)
        self.db_module_execs_id_index[module_exec.db_id] = module_exec
    def db_delete_module_exec(self, module_exec):
        self.is_dirty = True
        for i in xrange(len(self._db_module_execs)):
            if self._db_module_execs[i].db_id == module_exec.db_id:
                if not self._db_module_execs[i].is_new:
                    self.db_deleted_module_execs.append(self._db_module_execs[i])
                del self._db_module_execs[i]
                break
        del self.db_module_execs_id_index[module_exec.db_id]
    def db_get_module_exec(self, key):
        for i in xrange(len(self._db_module_execs)):
            if self._db_module_execs[i].db_id == key:
                return self._db_module_execs[i]
        return None
    def db_get_module_exec_by_id(self, key):
        return self.db_module_execs_id_index[key]
    def db_has_module_exec_with_id(self, key):
        return key in self.db_module_execs_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBConnection(object):

    vtType = 'connection'

    def __init__(self, id=None, ports=None):
        self._db_id = id
        self.db_deleted_ports = []
        self.db_ports_id_index = {}
        self.db_ports_type_index = {}
        if ports is None:
            self._db_ports = []
        else:
            self._db_ports = ports
            for v in self._db_ports:
                self.db_ports_id_index[v.db_id] = v
                self.db_ports_type_index[v.db_type] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConnection.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConnection(id=self._db_id)
        if self._db_ports is None:
            cp._db_ports = []
        else:
            cp._db_ports = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_ports]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_ports_id_index = dict((v.db_id, v) for v in cp._db_ports)
        cp.db_ports_type_index = dict((v.db_type, v) for v in cp._db_ports)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBConnection()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ports' in class_dict:
            res = class_dict['ports'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_port(obj)
        elif hasattr(old_obj, 'db_ports') and old_obj.db_ports is not None:
            for obj in old_obj.db_ports:
                new_obj.db_add_port(DBPort.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_ports') and hasattr(new_obj, 'db_deleted_ports'):
            for obj in old_obj.db_deleted_ports:
                n_obj = DBPort.update_version(obj, trans_dict)
                new_obj.db_deleted_ports.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_ports:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_port(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_ports)
        if remove:
            self.db_deleted_ports = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_ports:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_ports(self):
        return self._db_ports
    def __set_db_ports(self, ports):
        self._db_ports = ports
        self.is_dirty = True
    db_ports = property(__get_db_ports, __set_db_ports)
    def db_get_ports(self):
        return self._db_ports
    def db_add_port(self, port):
        self.is_dirty = True
        self._db_ports.append(port)
        self.db_ports_id_index[port.db_id] = port
        self.db_ports_type_index[port.db_type] = port
    def db_change_port(self, port):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_ports)):
            if self._db_ports[i].db_id == port.db_id:
                self._db_ports[i] = port
                found = True
                break
        if not found:
            self._db_ports.append(port)
        self.db_ports_id_index[port.db_id] = port
        self.db_ports_type_index[port.db_type] = port
    def db_delete_port(self, port):
        self.is_dirty = True
        for i in xrange(len(self._db_ports)):
            if self._db_ports[i].db_id == port.db_id:
                if not self._db_ports[i].is_new:
                    self.db_deleted_ports.append(self._db_ports[i])
                del self._db_ports[i]
                break
        del self.db_ports_id_index[port.db_id]
        del self.db_ports_type_index[port.db_type]
    def db_get_port(self, key):
        for i in xrange(len(self._db_ports)):
            if self._db_ports[i].db_id == key:
                return self._db_ports[i]
        return None
    def db_get_port_by_id(self, key):
        return self.db_ports_id_index[key]
    def db_has_port_with_id(self, key):
        return key in self.db_ports_id_index
    def db_get_port_by_type(self, key):
        return self.db_ports_type_index[key]
    def db_has_port_with_type(self, key):
        return key in self.db_ports_type_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBAction(object):

    vtType = 'action'

    def __init__(self, operations=None, id=None, prevId=None, date=None, session=None, user=None, prune=None, annotations=None):
        self.db_deleted_operations = []
        self.db_operations_id_index = {}
        if operations is None:
            self._db_operations = []
        else:
            self._db_operations = operations
            for v in self._db_operations:
                self.db_operations_id_index[v.db_id] = v
        self._db_id = id
        self._db_prevId = prevId
        self._db_date = date
        self._db_session = session
        self._db_user = user
        self._db_prune = prune
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        self.db_annotations_key_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
                self.db_annotations_key_index[v.db_key] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAction(id=self._db_id,
                      prevId=self._db_prevId,
                      date=self._db_date,
                      session=self._db_session,
                      user=self._db_user,
                      prune=self._db_prune)
        if self._db_operations is None:
            cp._db_operations = []
        else:
            cp._db_operations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_operations]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prevId') and ('action', self._db_prevId) in id_remap:
                cp._db_prevId = id_remap[('action', self._db_prevId)]
        
        # recreate indices and set flags
        cp.db_operations_id_index = dict((v.db_id, v) for v in cp._db_operations)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'operations' in class_dict:
            res = class_dict['operations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_operation(obj)
        elif hasattr(old_obj, 'db_operations') and old_obj.db_operations is not None:
            for obj in old_obj.db_operations:
                if obj.vtType == 'add':
                    new_obj.db_add_operation(DBAdd.update_version(obj, trans_dict))
                elif obj.vtType == 'delete':
                    new_obj.db_add_operation(DBDelete.update_version(obj, trans_dict))
                elif obj.vtType == 'change':
                    new_obj.db_add_operation(DBChange.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_operations') and hasattr(new_obj, 'db_deleted_operations'):
            for obj in old_obj.db_deleted_operations:
                if obj.vtType == 'add':
                    n_obj = DBAdd.update_version(obj, trans_dict)
                    new_obj.db_deleted_operations.append(n_obj)
                elif obj.vtType == 'delete':
                    n_obj = DBDelete.update_version(obj, trans_dict)
                    new_obj.db_deleted_operations.append(n_obj)
                elif obj.vtType == 'change':
                    n_obj = DBChange.update_version(obj, trans_dict)
                    new_obj.db_deleted_operations.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'prevId' in class_dict:
            res = class_dict['prevId'](old_obj, trans_dict)
            new_obj.db_prevId = res
        elif hasattr(old_obj, 'db_prevId') and old_obj.db_prevId is not None:
            new_obj.db_prevId = old_obj.db_prevId
        if 'date' in class_dict:
            res = class_dict['date'](old_obj, trans_dict)
            new_obj.db_date = res
        elif hasattr(old_obj, 'db_date') and old_obj.db_date is not None:
            new_obj.db_date = old_obj.db_date
        if 'session' in class_dict:
            res = class_dict['session'](old_obj, trans_dict)
            new_obj.db_session = res
        elif hasattr(old_obj, 'db_session') and old_obj.db_session is not None:
            new_obj.db_session = old_obj.db_session
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        if 'prune' in class_dict:
            res = class_dict['prune'](old_obj, trans_dict)
            new_obj.db_prune = res
        elif hasattr(old_obj, 'db_prune') and old_obj.db_prune is not None:
            new_obj.db_prune = old_obj.db_prune
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_operations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_operation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_operations)
        if remove:
            self.db_deleted_annotations = []
            self.db_deleted_operations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_operations:
            if child.has_changes():
                return True
        return False
    def __get_db_operations(self):
        return self._db_operations
    def __set_db_operations(self, operations):
        self._db_operations = operations
        self.is_dirty = True
    db_operations = property(__get_db_operations, __set_db_operations)
    def db_get_operations(self):
        return self._db_operations
    def db_add_operation(self, operation):
        self.is_dirty = True
        self._db_operations.append(operation)
        self.db_operations_id_index[operation.db_id] = operation
    def db_change_operation(self, operation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_operations)):
            if self._db_operations[i].db_id == operation.db_id:
                self._db_operations[i] = operation
                found = True
                break
        if not found:
            self._db_operations.append(operation)
        self.db_operations_id_index[operation.db_id] = operation
    def db_delete_operation(self, operation):
        self.is_dirty = True
        for i in xrange(len(self._db_operations)):
            if self._db_operations[i].db_id == operation.db_id:
                if not self._db_operations[i].is_new:
                    self.db_deleted_operations.append(self._db_operations[i])
                del self._db_operations[i]
                break
        del self.db_operations_id_index[operation.db_id]
    def db_get_operation(self, key):
        for i in xrange(len(self._db_operations)):
            if self._db_operations[i].db_id == key:
                return self._db_operations[i]
        return None
    def db_get_operation_by_id(self, key):
        return self.db_operations_id_index[key]
    def db_has_operation_with_id(self, key):
        return key in self.db_operations_id_index
    
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_prevId(self):
        return self._db_prevId
    def __set_db_prevId(self, prevId):
        self._db_prevId = prevId
        self.is_dirty = True
    db_prevId = property(__get_db_prevId, __set_db_prevId)
    def db_add_prevId(self, prevId):
        self._db_prevId = prevId
    def db_change_prevId(self, prevId):
        self._db_prevId = prevId
    def db_delete_prevId(self, prevId):
        self._db_prevId = None
    
    def __get_db_date(self):
        return self._db_date
    def __set_db_date(self, date):
        self._db_date = date
        self.is_dirty = True
    db_date = property(__get_db_date, __set_db_date)
    def db_add_date(self, date):
        self._db_date = date
    def db_change_date(self, date):
        self._db_date = date
    def db_delete_date(self, date):
        self._db_date = None
    
    def __get_db_session(self):
        return self._db_session
    def __set_db_session(self, session):
        self._db_session = session
        self.is_dirty = True
    db_session = property(__get_db_session, __set_db_session)
    def db_add_session(self, session):
        self._db_session = session
    def db_change_session(self, session):
        self._db_session = session
    def db_delete_session(self, session):
        self._db_session = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
    def __get_db_prune(self):
        return self._db_prune
    def __set_db_prune(self, prune):
        self._db_prune = prune
        self.is_dirty = True
    db_prune = property(__get_db_prune, __set_db_prune)
    def db_add_prune(self, prune):
        self._db_prune = prune
    def db_change_prune(self, prune):
        self._db_prune = prune
    def db_delete_prune(self, prune):
        self._db_prune = None
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
        del self.db_annotations_key_index[annotation.db_key]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    def db_get_annotation_by_key(self, key):
        return self.db_annotations_key_index[key]
    def db_has_annotation_with_key(self, key):
        return key in self.db_annotations_key_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBDelete(object):

    vtType = 'delete'

    def __init__(self, id=None, what=None, objectId=None, parentObjId=None, parentObjType=None):
        self._db_id = id
        self._db_what = what
        self._db_objectId = objectId
        self._db_parentObjId = parentObjId
        self._db_parentObjType = parentObjType
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBDelete.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBDelete(id=self._db_id,
                      what=self._db_what,
                      objectId=self._db_objectId,
                      parentObjId=self._db_parentObjId,
                      parentObjType=self._db_parentObjType)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_objectId') and (self._db_what, self._db_objectId) in id_remap:
                cp._db_objectId = id_remap[(self._db_what, self._db_objectId)]
            if hasattr(self, 'db_parentObjId') and (self._db_parentObjType, self._db_parentObjId) in id_remap:
                cp._db_parentObjId = id_remap[(self._db_parentObjType, self._db_parentObjId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBDelete()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'what' in class_dict:
            res = class_dict['what'](old_obj, trans_dict)
            new_obj.db_what = res
        elif hasattr(old_obj, 'db_what') and old_obj.db_what is not None:
            new_obj.db_what = old_obj.db_what
        if 'objectId' in class_dict:
            res = class_dict['objectId'](old_obj, trans_dict)
            new_obj.db_objectId = res
        elif hasattr(old_obj, 'db_objectId') and old_obj.db_objectId is not None:
            new_obj.db_objectId = old_obj.db_objectId
        if 'parentObjId' in class_dict:
            res = class_dict['parentObjId'](old_obj, trans_dict)
            new_obj.db_parentObjId = res
        elif hasattr(old_obj, 'db_parentObjId') and old_obj.db_parentObjId is not None:
            new_obj.db_parentObjId = old_obj.db_parentObjId
        if 'parentObjType' in class_dict:
            res = class_dict['parentObjType'](old_obj, trans_dict)
            new_obj.db_parentObjType = res
        elif hasattr(old_obj, 'db_parentObjType') and old_obj.db_parentObjType is not None:
            new_obj.db_parentObjType = old_obj.db_parentObjType
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_what(self):
        return self._db_what
    def __set_db_what(self, what):
        self._db_what = what
        self.is_dirty = True
    db_what = property(__get_db_what, __set_db_what)
    def db_add_what(self, what):
        self._db_what = what
    def db_change_what(self, what):
        self._db_what = what
    def db_delete_what(self, what):
        self._db_what = None
    
    def __get_db_objectId(self):
        return self._db_objectId
    def __set_db_objectId(self, objectId):
        self._db_objectId = objectId
        self.is_dirty = True
    db_objectId = property(__get_db_objectId, __set_db_objectId)
    def db_add_objectId(self, objectId):
        self._db_objectId = objectId
    def db_change_objectId(self, objectId):
        self._db_objectId = objectId
    def db_delete_objectId(self, objectId):
        self._db_objectId = None
    
    def __get_db_parentObjId(self):
        return self._db_parentObjId
    def __set_db_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
        self.is_dirty = True
    db_parentObjId = property(__get_db_parentObjId, __set_db_parentObjId)
    def db_add_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_change_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_delete_parentObjId(self, parentObjId):
        self._db_parentObjId = None
    
    def __get_db_parentObjType(self):
        return self._db_parentObjType
    def __set_db_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
        self.is_dirty = True
    db_parentObjType = property(__get_db_parentObjType, __set_db_parentObjType)
    def db_add_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_change_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_delete_parentObjType(self, parentObjType):
        self._db_parentObjType = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBVistrail(object):

    vtType = 'vistrail'

    def __init__(self, id=None, entity_type=None, version=None, name=None, last_modified=None, actions=None, tags=None, annotations=None):
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_version = version
        self._db_name = name
        self._db_last_modified = last_modified
        self.db_deleted_actions = []
        self.db_actions_id_index = {}
        if actions is None:
            self._db_actions = []
        else:
            self._db_actions = actions
            for v in self._db_actions:
                self.db_actions_id_index[v.db_id] = v
        self.db_deleted_tags = []
        self.db_tags_id_index = {}
        self.db_tags_name_index = {}
        if tags is None:
            self._db_tags = []
        else:
            self._db_tags = tags
            for v in self._db_tags:
                self.db_tags_id_index[v.db_id] = v
                self.db_tags_name_index[v.db_name] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        self.db_annotations_key_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
                self.db_annotations_key_index[v.db_key] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBVistrail.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBVistrail(id=self._db_id,
                        entity_type=self._db_entity_type,
                        version=self._db_version,
                        name=self._db_name,
                        last_modified=self._db_last_modified)
        if self._db_actions is None:
            cp._db_actions = []
        else:
            cp._db_actions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_actions]
        if self._db_tags is None:
            cp._db_tags = []
        else:
            cp._db_tags = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_tags]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_actions_id_index = dict((v.db_id, v) for v in cp._db_actions)
        cp.db_tags_id_index = dict((v.db_id, v) for v in cp._db_tags)
        cp.db_tags_name_index = dict((v.db_name, v) for v in cp._db_tags)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBVistrail()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'entity_type' in class_dict:
            res = class_dict['entity_type'](old_obj, trans_dict)
            new_obj.db_entity_type = res
        elif hasattr(old_obj, 'db_entity_type') and old_obj.db_entity_type is not None:
            new_obj.db_entity_type = old_obj.db_entity_type
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'last_modified' in class_dict:
            res = class_dict['last_modified'](old_obj, trans_dict)
            new_obj.db_last_modified = res
        elif hasattr(old_obj, 'db_last_modified') and old_obj.db_last_modified is not None:
            new_obj.db_last_modified = old_obj.db_last_modified
        if 'actions' in class_dict:
            res = class_dict['actions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_action(obj)
        elif hasattr(old_obj, 'db_actions') and old_obj.db_actions is not None:
            for obj in old_obj.db_actions:
                new_obj.db_add_action(DBAction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_actions') and hasattr(new_obj, 'db_deleted_actions'):
            for obj in old_obj.db_deleted_actions:
                n_obj = DBAction.update_version(obj, trans_dict)
                new_obj.db_deleted_actions.append(n_obj)
        if 'tags' in class_dict:
            res = class_dict['tags'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_tag(obj)
        elif hasattr(old_obj, 'db_tags') and old_obj.db_tags is not None:
            for obj in old_obj.db_tags:
                new_obj.db_add_tag(DBTag.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_tags') and hasattr(new_obj, 'db_deleted_tags'):
            for obj in old_obj.db_deleted_tags:
                n_obj = DBTag.update_version(obj, trans_dict)
                new_obj.db_deleted_tags.append(n_obj)
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_actions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_action(child)
        to_del = []
        for child in self.db_tags:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_tag(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_actions)
        children.extend(self.db_deleted_tags)
        children.extend(self.db_deleted_annotations)
        if remove:
            self.db_deleted_actions = []
            self.db_deleted_tags = []
            self.db_deleted_annotations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_actions:
            if child.has_changes():
                return True
        for child in self._db_tags:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_entity_type(self):
        return self._db_entity_type
    def __set_db_entity_type(self, entity_type):
        self._db_entity_type = entity_type
        self.is_dirty = True
    db_entity_type = property(__get_db_entity_type, __set_db_entity_type)
    def db_add_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_change_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_delete_entity_type(self, entity_type):
        self._db_entity_type = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_last_modified(self):
        return self._db_last_modified
    def __set_db_last_modified(self, last_modified):
        self._db_last_modified = last_modified
        self.is_dirty = True
    db_last_modified = property(__get_db_last_modified, __set_db_last_modified)
    def db_add_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_change_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_delete_last_modified(self, last_modified):
        self._db_last_modified = None
    
    def __get_db_actions(self):
        return self._db_actions
    def __set_db_actions(self, actions):
        self._db_actions = actions
        self.is_dirty = True
    db_actions = property(__get_db_actions, __set_db_actions)
    def db_get_actions(self):
        return self._db_actions
    def db_add_action(self, action):
        self.is_dirty = True
        self._db_actions.append(action)
        self.db_actions_id_index[action.db_id] = action
    def db_change_action(self, action):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_actions)):
            if self._db_actions[i].db_id == action.db_id:
                self._db_actions[i] = action
                found = True
                break
        if not found:
            self._db_actions.append(action)
        self.db_actions_id_index[action.db_id] = action
    def db_delete_action(self, action):
        self.is_dirty = True
        for i in xrange(len(self._db_actions)):
            if self._db_actions[i].db_id == action.db_id:
                if not self._db_actions[i].is_new:
                    self.db_deleted_actions.append(self._db_actions[i])
                del self._db_actions[i]
                break
        del self.db_actions_id_index[action.db_id]
    def db_get_action(self, key):
        for i in xrange(len(self._db_actions)):
            if self._db_actions[i].db_id == key:
                return self._db_actions[i]
        return None
    def db_get_action_by_id(self, key):
        return self.db_actions_id_index[key]
    def db_has_action_with_id(self, key):
        return key in self.db_actions_id_index
    
    def __get_db_tags(self):
        return self._db_tags
    def __set_db_tags(self, tags):
        self._db_tags = tags
        self.is_dirty = True
    db_tags = property(__get_db_tags, __set_db_tags)
    def db_get_tags(self):
        return self._db_tags
    def db_add_tag(self, tag):
        self.is_dirty = True
        self._db_tags.append(tag)
        self.db_tags_id_index[tag.db_id] = tag
        self.db_tags_name_index[tag.db_name] = tag
    def db_change_tag(self, tag):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_tags)):
            if self._db_tags[i].db_id == tag.db_id:
                self._db_tags[i] = tag
                found = True
                break
        if not found:
            self._db_tags.append(tag)
        self.db_tags_id_index[tag.db_id] = tag
        self.db_tags_name_index[tag.db_name] = tag
    def db_delete_tag(self, tag):
        self.is_dirty = True
        for i in xrange(len(self._db_tags)):
            if self._db_tags[i].db_id == tag.db_id:
                if not self._db_tags[i].is_new:
                    self.db_deleted_tags.append(self._db_tags[i])
                del self._db_tags[i]
                break
        del self.db_tags_id_index[tag.db_id]
        del self.db_tags_name_index[tag.db_name]
    def db_get_tag(self, key):
        for i in xrange(len(self._db_tags)):
            if self._db_tags[i].db_id == key:
                return self._db_tags[i]
        return None
    def db_get_tag_by_id(self, key):
        return self.db_tags_id_index[key]
    def db_has_tag_with_id(self, key):
        return key in self.db_tags_id_index
    def db_get_tag_by_name(self, key):
        return self.db_tags_name_index[key]
    def db_has_tag_with_name(self, key):
        return key in self.db_tags_name_index
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
        del self.db_annotations_key_index[annotation.db_key]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    def db_get_annotation_by_key(self, key):
        return self.db_annotations_key_index[key]
    def db_has_annotation_with_key(self, key):
        return key in self.db_annotations_key_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBModuleExec(object):

    vtType = 'module_exec'

    def __init__(self, id=None, ts_start=None, ts_end=None, cached=None, module_id=None, module_name=None, completed=None, error=None, abstraction_id=None, abstraction_version=None, machine_id=None, annotations=None):
        self._db_id = id
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self._db_cached = cached
        self._db_module_id = module_id
        self._db_module_name = module_name
        self._db_completed = completed
        self._db_error = error
        self._db_abstraction_id = abstraction_id
        self._db_abstraction_version = abstraction_version
        self._db_machine_id = machine_id
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBModuleExec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModuleExec(id=self._db_id,
                          ts_start=self._db_ts_start,
                          ts_end=self._db_ts_end,
                          cached=self._db_cached,
                          module_id=self._db_module_id,
                          module_name=self._db_module_name,
                          completed=self._db_completed,
                          error=self._db_error,
                          abstraction_id=self._db_abstraction_id,
                          abstraction_version=self._db_abstraction_version,
                          machine_id=self._db_machine_id)
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_module_id') and ('module', self._db_module_id) in id_remap:
                cp._db_module_id = id_remap[('module', self._db_module_id)]
            if hasattr(self, 'db_machine_id') and ('machine', self._db_machine_id) in id_remap:
                cp._db_machine_id = id_remap[('machine', self._db_machine_id)]
        
        # recreate indices and set flags
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBModuleExec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'cached' in class_dict:
            res = class_dict['cached'](old_obj, trans_dict)
            new_obj.db_cached = res
        elif hasattr(old_obj, 'db_cached') and old_obj.db_cached is not None:
            new_obj.db_cached = old_obj.db_cached
        if 'module_id' in class_dict:
            res = class_dict['module_id'](old_obj, trans_dict)
            new_obj.db_module_id = res
        elif hasattr(old_obj, 'db_module_id') and old_obj.db_module_id is not None:
            new_obj.db_module_id = old_obj.db_module_id
        if 'module_name' in class_dict:
            res = class_dict['module_name'](old_obj, trans_dict)
            new_obj.db_module_name = res
        elif hasattr(old_obj, 'db_module_name') and old_obj.db_module_name is not None:
            new_obj.db_module_name = old_obj.db_module_name
        if 'completed' in class_dict:
            res = class_dict['completed'](old_obj, trans_dict)
            new_obj.db_completed = res
        elif hasattr(old_obj, 'db_completed') and old_obj.db_completed is not None:
            new_obj.db_completed = old_obj.db_completed
        if 'error' in class_dict:
            res = class_dict['error'](old_obj, trans_dict)
            new_obj.db_error = res
        elif hasattr(old_obj, 'db_error') and old_obj.db_error is not None:
            new_obj.db_error = old_obj.db_error
        if 'abstraction_id' in class_dict:
            res = class_dict['abstraction_id'](old_obj, trans_dict)
            new_obj.db_abstraction_id = res
        elif hasattr(old_obj, 'db_abstraction_id') and old_obj.db_abstraction_id is not None:
            new_obj.db_abstraction_id = old_obj.db_abstraction_id
        if 'abstraction_version' in class_dict:
            res = class_dict['abstraction_version'](old_obj, trans_dict)
            new_obj.db_abstraction_version = res
        elif hasattr(old_obj, 'db_abstraction_version') and old_obj.db_abstraction_version is not None:
            new_obj.db_abstraction_version = old_obj.db_abstraction_version
        if 'machine_id' in class_dict:
            res = class_dict['machine_id'](old_obj, trans_dict)
            new_obj.db_machine_id = res
        elif hasattr(old_obj, 'db_machine_id') and old_obj.db_machine_id is not None:
            new_obj.db_machine_id = old_obj.db_machine_id
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_annotations)
        if remove:
            self.db_deleted_annotations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_cached(self):
        return self._db_cached
    def __set_db_cached(self, cached):
        self._db_cached = cached
        self.is_dirty = True
    db_cached = property(__get_db_cached, __set_db_cached)
    def db_add_cached(self, cached):
        self._db_cached = cached
    def db_change_cached(self, cached):
        self._db_cached = cached
    def db_delete_cached(self, cached):
        self._db_cached = None
    
    def __get_db_module_id(self):
        return self._db_module_id
    def __set_db_module_id(self, module_id):
        self._db_module_id = module_id
        self.is_dirty = True
    db_module_id = property(__get_db_module_id, __set_db_module_id)
    def db_add_module_id(self, module_id):
        self._db_module_id = module_id
    def db_change_module_id(self, module_id):
        self._db_module_id = module_id
    def db_delete_module_id(self, module_id):
        self._db_module_id = None
    
    def __get_db_module_name(self):
        return self._db_module_name
    def __set_db_module_name(self, module_name):
        self._db_module_name = module_name
        self.is_dirty = True
    db_module_name = property(__get_db_module_name, __set_db_module_name)
    def db_add_module_name(self, module_name):
        self._db_module_name = module_name
    def db_change_module_name(self, module_name):
        self._db_module_name = module_name
    def db_delete_module_name(self, module_name):
        self._db_module_name = None
    
    def __get_db_completed(self):
        return self._db_completed
    def __set_db_completed(self, completed):
        self._db_completed = completed
        self.is_dirty = True
    db_completed = property(__get_db_completed, __set_db_completed)
    def db_add_completed(self, completed):
        self._db_completed = completed
    def db_change_completed(self, completed):
        self._db_completed = completed
    def db_delete_completed(self, completed):
        self._db_completed = None
    
    def __get_db_error(self):
        return self._db_error
    def __set_db_error(self, error):
        self._db_error = error
        self.is_dirty = True
    db_error = property(__get_db_error, __set_db_error)
    def db_add_error(self, error):
        self._db_error = error
    def db_change_error(self, error):
        self._db_error = error
    def db_delete_error(self, error):
        self._db_error = None
    
    def __get_db_abstraction_id(self):
        return self._db_abstraction_id
    def __set_db_abstraction_id(self, abstraction_id):
        self._db_abstraction_id = abstraction_id
        self.is_dirty = True
    db_abstraction_id = property(__get_db_abstraction_id, __set_db_abstraction_id)
    def db_add_abstraction_id(self, abstraction_id):
        self._db_abstraction_id = abstraction_id
    def db_change_abstraction_id(self, abstraction_id):
        self._db_abstraction_id = abstraction_id
    def db_delete_abstraction_id(self, abstraction_id):
        self._db_abstraction_id = None
    
    def __get_db_abstraction_version(self):
        return self._db_abstraction_version
    def __set_db_abstraction_version(self, abstraction_version):
        self._db_abstraction_version = abstraction_version
        self.is_dirty = True
    db_abstraction_version = property(__get_db_abstraction_version, __set_db_abstraction_version)
    def db_add_abstraction_version(self, abstraction_version):
        self._db_abstraction_version = abstraction_version
    def db_change_abstraction_version(self, abstraction_version):
        self._db_abstraction_version = abstraction_version
    def db_delete_abstraction_version(self, abstraction_version):
        self._db_abstraction_version = None
    
    def __get_db_machine_id(self):
        return self._db_machine_id
    def __set_db_machine_id(self, machine_id):
        self._db_machine_id = machine_id
        self.is_dirty = True
    db_machine_id = property(__get_db_machine_id, __set_db_machine_id)
    def db_add_machine_id(self, machine_id):
        self._db_machine_id = machine_id
    def db_change_machine_id(self, machine_id):
        self._db_machine_id = machine_id
    def db_delete_machine_id(self, machine_id):
        self._db_machine_id = None
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    
    def getPrimaryKey(self):
        return self._db_id

