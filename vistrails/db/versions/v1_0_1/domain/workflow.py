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

from auto_gen import DBWorkflow as _DBWorkflow
from auto_gen import DBAbstraction, DBModule, DBGroup
from id_scope import IdScope

import copy

class DBWorkflow(_DBWorkflow):

    def __init__(self, *args, **kwargs):
        _DBWorkflow.__init__(self, *args, **kwargs)
        self.objects = {}
        self.tmp_id = IdScope(1,
                              {DBAbstraction.vtType: DBModule.vtType,
                               DBGroup.vtType: DBModule.vtType})

    def __copy__(self):
        return DBWorkflow.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = _DBWorkflow.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = DBWorkflow
        # need to go through and reset the index to the copied objects
        cp.build_index()
        cp.tmp_id = copy.copy(self.tmp_id)
        return cp        

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBWorkflow()
        new_obj = _DBWorkflow.update_version(old_obj, trans_dict, new_obj)
        new_obj.update_id_scope()
        new_obj.build_index()
        return new_obj
    
    def update_id_scope(self):
        pass

    _vtTypeMap = {DBAbstraction.vtType: DBModule.vtType, 
                  DBGroup.vtType: DBModule.vtType}

    def build_index(self):
        g = self._vtTypeMap.get
        self.objects = dict(((g(o.vtType, o.vtType), o._db_id), o)
                            for (o,_,_) in self.db_children())

    def add_to_index(self, object):
        obj_type = self._vtTypeMap.get(object.vtType, object.vtType)
        self.objects[(obj_type, object.getPrimaryKey())] = object

    def delete_from_index(self, object):
        obj_type = self._vtTypeMap.get(object.vtType, object.vtType)
        del self.objects[(obj_type, object.getPrimaryKey())]

    def capitalizeOne(self, str):
        return str[0].upper() + str[1:]

    def db_print_objects(self):
        for k,v in self.objects.iteritems():
            print '%s: %s' % (k, v)

    def db_has_object(self, type, id):
        return (type, id) in self.objects

    def db_get_object(self, type, id):
        return self.objects[(type, id)]

    def db_add_object(self, object, parent_obj_type=None,
                      parent_obj_id=None, parent_obj=None):
        if parent_obj is None:
            if parent_obj_type is None or parent_obj_id is None:
                parent_obj = self
            else:
                if parent_obj_type == DBAbstraction.vtType or \
                        parent_obj_type == DBGroup.vtType:
                    parent_obj_type = DBModule.vtType
                try:
                    parent_obj = self.objects[(parent_obj_type, parent_obj_id)]
                except KeyError:
                    msg = "Cannot find object of type '%s' with id '%s'" % \
                        (parent_obj_type, parent_obj_id)
                    raise Exception(msg)
        if object.vtType == DBAbstraction.vtType or \
                object.vtType == DBGroup.vtType:
            obj_type = DBModule.vtType
        else:
            obj_type = object.vtType
        funname = 'db_add_' + obj_type
        obj_copy = copy.copy(object)
        getattr(parent_obj, funname)(obj_copy)
        self.add_to_index(obj_copy)

    def db_change_object(self, old_id, object, parent_obj_type=None, 
                         parent_obj_id=None, parent_obj=None):
        if parent_obj is None:
            if parent_obj_type is None or parent_obj_id is None:
                parent_obj = self
            else:
                if parent_obj_type == DBAbstraction.vtType or \
                        parent_obj_type == DBGroup.vtType:
                    parent_obj_type = DBModule.vtType
                try:
                    parent_obj = self.objects[(parent_obj_type, parent_obj_id)]
                except KeyError:
                    msg = "Cannot find object of type '%s' with id '%s'" % \
                        (parent_obj_type, parent_obj_id)
                    raise Exception(msg)

        self.db_delete_object(old_id, object.vtType, None, None, parent_obj)
        self.db_add_object(object, None, None, parent_obj)

    def db_delete_object(self, obj_id, obj_type, parent_obj_type=None, 
                         parent_obj_id=None, parent_obj=None):
        if parent_obj is None:
            if parent_obj_type is None or parent_obj_id is None:
                parent_obj = self
            else:
                if parent_obj_type == DBAbstraction.vtType or \
                        parent_obj_type == DBGroup.vtType:
                    parent_obj_type = DBModule.vtType
                try:
                    parent_obj = self.objects[(parent_obj_type, parent_obj_id)]
                except KeyError:
                    msg = "Cannot find object of type '%s' with id '%s'" % \
                        (parent_obj_type, parent_obj_id)
                    raise Exception(msg)
        if obj_type == DBAbstraction.vtType or obj_type == DBGroup.vtType:
            obj_type = DBModule.vtType
        funname = 'db_get_' + obj_type
        if hasattr(parent_obj, funname):
            object = getattr(parent_obj, funname)(obj_id)
        else:
            attr_name = 'db_' + obj_type
            object = getattr(parent_obj, attr_name)
        funname = 'db_delete_' + obj_type
        getattr(parent_obj, funname)(object)
        self.delete_from_index(object)
