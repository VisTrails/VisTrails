###############################################################################
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

import copy
import hashlib
from auto_gen import DBVistrail as _DBVistrail
from auto_gen import DBAdd, DBChange, DBDelete, DBAbstraction, DBGroup, \
    DBModule, DBAnnotation, DBActionAnnotation
from id_scope import IdScope

class DBVistrail(_DBVistrail):
    def __init__(self, *args, **kwargs):
	_DBVistrail.__init__(self, *args, **kwargs)
        self.idScope = IdScope(remap={DBAdd.vtType: 'operation',
                                      DBChange.vtType: 'operation',
                                      DBDelete.vtType: 'operation',
                                      DBAbstraction.vtType: DBModule.vtType,
                                      DBGroup.vtType: DBModule.vtType,
                                      DBActionAnnotation.vtType: \
                                          DBAnnotation.vtType})

        self.idScope.setBeginId('action', 1)
        self.db_objects = {}

        # keep a reference to the current logging information here
        self.db_log_filename = None
        self.log = None

    def __copy__(self):
        return DBVistrail.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = _DBVistrail.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = DBVistrail
        
        cp.idScope = copy.copy(self.idScope)
        cp.db_objects = copy.copy(self.db_objects)
        cp.db_log_filename = self.db_log_filename
        if self.log is not None:
            cp.log = copy.copy(self.log)
        else:
            cp.log = None
        
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBVistrail()
        new_obj = _DBVistrail.update_version(old_obj, trans_dict, new_obj)
        new_obj.update_id_scope()
        if hasattr(old_obj, 'db_log_filename'):
            new_obj.db_log_filename = old_obj.db_log_filename
        if hasattr(old_obj, 'log'):
            new_obj.log = old_obj.log
        return new_obj

    def update_id_scope(self):
        def getOldObjId(operation):
            if operation.vtType == 'change':
                return operation.db_oldObjId
            return operation.db_objectId

        def getNewObjId(operation):
            if operation.vtType == 'change':
                return operation.db_newObjId
            return operation.db_objectId

        for action in self.db_actions:
            self.idScope.updateBeginId('action', action.db_id+1)
            if action.db_session is not None:
                self.idScope.updateBeginId('session', action.db_session + 1)
            for operation in action.db_operations:
                self.idScope.updateBeginId('operation', operation.db_id+1)
                if operation.vtType == 'add' or operation.vtType == 'change':
                    # update ids of data
                    self.idScope.updateBeginId(operation.db_what, 
                                               getNewObjId(operation)+1)
                    if operation.db_data is None:
                        if operation.vtType == 'change':
                            operation.db_objectId = operation.db_oldObjId
                    self.db_add_object(operation.db_data)
            for annotation in action.db_annotations:
                self.idScope.updateBeginId('annotation', annotation.db_id+1)
        
        for annotation in self.db_annotations:
            self.idScope.updateBeginId('annotation', annotation.db_id+1)
        for annotation in self.db_actionAnnotations:
            self.idScope.updateBeginId('annotation', annotation.db_id+1)

    def db_add_object(self, obj):
        self.db_objects[(obj.vtType, obj.db_id)] = obj

    def db_get_object(self, type, id):
        return self.db_objects.get((type, id), None)

    def db_update_object(self, obj, **kwargs):
        # want to swap out old object with a new version
        # need this for updating aliases...
        # hack it using setattr...
        real_obj = self.db_objects[(obj.vtType, obj.db_id)]
        for (k, v) in kwargs.iteritems():
            if hasattr(real_obj, k):
                setattr(real_obj, k, v)

    def update_checkout_version(self, app=''):
        checkout_key = "__checkout_version_"
        action_key = checkout_key + app
        annotation_key = action_key + '_annotationhash'
        action_annotation_key = action_key + '_actionannotationhash'

        # delete previous checkout annotations
        deletekeys = [action_key,annotation_key,action_annotation_key]
        for key in deletekeys:
            while self.db_has_annotation_with_key(key):
                a = self.db_get_annotation_by_key(key)
                self.db_delete_annotation(a)
        
        # annotation hash - requires annotations to be clean
        value = self.hashAnnotations()
        if self.db_has_annotation_with_key(annotation_key):
            annotation = self.db_get_annotation_by_key(annotation_key)
            annotation.db_value = value
        else:
            annotation=DBAnnotation(self.idScope.getNewId(DBAnnotation.vtType), 
                                  annotation_key, value)
            self.db_add_annotation(annotation)
        # action annotation hash
        value = self.hashActionAnnotations()
        if self.db_has_annotation_with_key(action_annotation_key):
            annotation = self.db_get_annotation_by_key(action_annotation_key)
            annotation.db_value = value
        else:
            annotation=DBAnnotation(self.idScope.getNewId(DBAnnotation.vtType), 
                                    action_annotation_key, value)
            self.db_add_annotation(annotation)
        # last action id hash
        if len(self.db_actions) == 0:
            value = 0
        else:
            value = max(v.db_id for v in self.db_actions)
        if self.db_has_annotation_with_key(action_key):
            annotation = self.db_get_annotation_by_key(action_key)
            annotation.db_value = str(value)
        else:
            annotation=DBAnnotation(self.idScope.getNewId(DBAnnotation.vtType), 
                                    action_key, str(value))
            self.db_add_annotation(annotation)

    def hashAnnotations(self):
        annotations = {}
        for annotation in self.db_annotations:
            if annotation._db_key not in annotations:
                annotations[annotation._db_key] = []
            if annotation._db_value not in annotations[annotation._db_key]:
                annotations[annotation._db_key].append(annotation._db_value)
        keys = annotations.keys()
        keys.sort()
        m = hashlib.md5()
        for k in keys:
            m.update(str(k))
            annotations[k].sort()
            for v in annotations[k]:
                m.update(v)
        return m.hexdigest()

    def hashActionAnnotations(self):
        action_annotations = {}
        for action_id, key, value in [[aa.db_action_id, aa.db_key, 
                         aa.db_value] for aa in self.db_actionAnnotations]:
            index = (str(action_id), key)
            if index not in action_annotations:
                action_annotations[index] = []
            if value not in action_annotations[index]:
                action_annotations[index].append(value)
        keys = action_annotations.keys()
        keys.sort()
        m = hashlib.md5()
        for k in keys:
            m.update(k[0] + k[1])
            action_annotations[k].sort()
            for v in action_annotations[k]:
                m.update(v)
        return m.hexdigest()
