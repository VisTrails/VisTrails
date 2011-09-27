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
from db.versions.v1_0_1.domain import DBVistrail, DBWorkflow, DBLog, \
    DBRegistry, DBGroup, DBTag, DBAnnotation, DBAction, IdScope

def translateVistrail(_vistrail):
    tag_annotations = {}
    notes_annotations = {}
    thumb_annotations = {}
    upgrade_annotations = {}
    prune_annotations = {}

    del_tag_annotations = {}
    del_notes_annotations = {}
    del_thumb_annotations = {}
    del_upgrade_annotations = {}
    del_prune_annotations = {}

    key_lists = {'__tag__': tag_annotations,
                 '__notes__': notes_annotations,
                 '__thumb__': thumb_annotations,
                 '__upgrade__': upgrade_annotations,
                 '__prune__': prune_annotations}

    del_key_lists = {'__tag__': del_tag_annotations,
                     '__notes__': del_notes_annotations,
                     '__thumb__': del_thumb_annotations,
                     '__upgrade__': del_upgrade_annotations,
                     '__prune__': del_prune_annotations}

    _vistrail.update_id_scope()
    id_scope = _vistrail.idScope

    def update_tags(old_obj, translate_dict):
        new_tags = []
        for (id, (_, tag, is_new, is_dirty)) in tag_annotations.iteritems():
            new_tag = DBTag(id=id, name=tag)
            new_tag.is_new = is_new
            new_tag.is_dirty = is_dirty
            new_tags.append(new_tag)
        return new_tags

    def update_prune(old_obj, translate_dict):
        if old_obj.db_id in prune_annotations:
            (_, prune_val, _, _) = prune_annotations[old_obj.db_id]
            if prune_val == str(True):
                return 1
            elif prune_val == str(False):
                return 0
        return None

    def update_annotations(old_obj, translate_dict):
        new_annotations = [DBAnnotation.update_version(a, translate_dict)
                           for a in old_obj.db_annotations]
        if old_obj.db_id in notes_annotations:
            (id, notes, is_new, is_dirty) = notes_annotations[old_obj.db_id]
            ann = DBAnnotation(id=id,
                               key='__notes__',
                               value=notes)
            ann.is_new = is_new
            ann.is_dirty = is_dirty
            new_annotations.append(ann)
        if old_obj.db_id in upgrade_annotations:
            (id, upgrade, is_new, is_dirty) = \
                upgrade_annotations[old_obj.db_id]
            ann =  DBAnnotation(id=id,
                                key='__upgrade__',
                                value=upgrade)
            ann.is_new = is_new
            ann.is_dirty = is_dirty
            new_annotations.append(ann)
        if old_obj.db_id in thumb_annotations:
            (id, thumb, is_new, is_dirty) = thumb_annotations[old_obj.db_id]
            ann = DBAnnotation(id=id,
                               key='__thumb__',
                               value=thumb)
            ann.is_new = is_new
            ann.is_dirty = is_dirty
            new_annotations.append(ann)
        return new_annotations

    def update_actions(old_obj, translate_dict):
        new_actions = []
        for action in old_obj.db_actions:
            if action.db_id in del_notes_annotations:
                (id, notes, is_new, is_dirty) = \
                    del_notes_annotations[action.db_id]
                ann = DBAnnotation(id=id,
                                   key='__notes__',
                                   value=notes)
                ann.is_new = is_new
                ann.is_dirty = is_dirty
                action.db_deleted_annotations.append(ann)
            if action.db_id in del_upgrade_annotations:
                (id, upgrade, is_new, is_dirty) = \
                    del_upgrade_annotations[action.db_id]
                ann = DBAnnotation(id=id,
                                   key='__upgrade__',
                                   value=upgrade)
                ann.is_new = is_new
                ann.is_dirty = is_dirty
                action.db_deleted_annotations.append(ann)
            if action.db_id in del_thumb_annotations:
                (id, thumb, is_new, is_dirty) = \
                    del_thumb_annotations[action.db_id]
                ann = DBAnnotation(id=id,
                                   key='__thumb__',
                                   value=thumb)
                ann.is_new = is_new
                ann.is_dirty = is_dirty
                action.db_deleted_annotations.append(ann)                
            new_actions.append(DBAction.update_version(action, translate_dict))
        return new_actions

    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    for a in _vistrail.db_actionAnnotations:
        if a.db_key in key_lists:
            key_lists[a.db_key][a.db_action_id] = \
                (a.db_id, a.db_value, a.is_new, a.is_dirty)
    for a in _vistrail.db_deleted_actionAnnotations:
        if a.db_key in del_key_lists:
            del_key_lists[a.db_key][a.db_action_id] = \
                (a.db_id, a.db_value, a.is_new, a.is_dirty)

    translate_dict = {'DBGroup': {'workflow': update_workflow},
                      'DBVistrail': {'tags': update_tags,
                                     'actions': update_actions},
                      'DBAction': {'annotations': update_annotations,
                                   'prune': update_prune}}
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    for (id, (_, tag, is_new, is_dirty)) in del_tag_annotations.iteritems():
        new_tag = DBTag(id=id, name=tag)
        new_tag.is_new = is_new
        new_tag.is_dirty = is_dirty
        vistrail.db_deleted_tags.append(new_tag)
    
    vistrail.db_version = '1.0.1'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '1.0.1'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.1'
    return log

def translateRegistry(_registry):
    translate_dict = {}
    registry = DBRegistry.update_version(_registry, translate_dict)
    registry.db_version = '1.0.1'
    return registry
