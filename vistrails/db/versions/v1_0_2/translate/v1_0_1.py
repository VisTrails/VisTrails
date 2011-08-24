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
from db.versions.v1_0_2.domain import DBVistrail, DBWorkflow, DBLog, \
    DBRegistry, DBGroup, DBActionAnnotation, DBAnnotation, DBAction, IdScope

def translateVistrail(_vistrail):
    tag_annotations = []
    notes_annotations = []
    thumb_annotations = []
    upgrade_annotations = []
    prune_annotations = []

    def update_type(old_obj, translate_dict):
        if old_obj.db_type.find('|') >= 0:
            [identifier, m_and_ns] = old_obj.db_type.split(':', 1)
            # this second check is fragile but should be ok
            if m_and_ns.find(':') == -1 or m_and_ns.startswith('http://'):
                # need to move module name
                try:
                    [namespace, module] = m_and_ns.rsplit('|', 1)
                    new_type = ':'.join([identifier, module, namespace])
                    return new_type
                except Exception, e:
                    # just bail for now
                    print e
                    pass
        return old_obj.db_type

    def update_tags(old_obj, translate_dict):
        for tag in old_obj.db_tags:
            tag_annotations.append((tag.db_id, tag.db_name, None))
        return []

    def update_actions(old_obj, translate_dict):
        new_actions = []
        for action in old_obj.db_actions:
            if action.db_prune == 1:
                prune_annotations.append((action.db_id, str(True), None))
            new_actions.append(DBAction.update_version(action, translate_dict))
        return new_actions

    def update_annotations(old_obj, translate_dict):
        same_annotations = []
        for annotation in old_obj.db_annotations:
            if annotation.db_key == '__notes__':
                notes_annotations.append((old_obj.db_id, annotation.db_value,
                                          annotation.db_id))
            elif annotation.db_key == '__thumb__':
                thumb_annotations.append((old_obj.db_id, annotation.db_value,
                                          annotation.db_id))
            elif annotation.db_key == '__upgrade__':
                upgrade_annotations.append((old_obj.db_id, 
                                            annotation.db_value,
                                            annotation.db_id))
            else:
                same_annotations.append(
                    DBAnnotation.update_version(annotation, translate_dict))
        return same_annotations

    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    translate_dict = {'DBGroup': {'workflow': update_workflow},
                      'DBVistrail': {'tags': update_tags,
                                     'actions': update_actions},
                      'DBAction': {'annotations': update_annotations},
                      'DBParameter': {'type': update_type},
                      }
    _vistrail.update_id_scope()
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)

    id_scope = vistrail.idScope
    id_scope.setBeginId('annotation', _vistrail.idScope.getNewId('annotation'))
    key_lists = {'__tag__': tag_annotations,
                 '__notes__': notes_annotations,
                 '__thumb__': thumb_annotations,
                 '__upgrade__': upgrade_annotations,
                 '__prune__': prune_annotations}
    for key, annotations in key_lists.iteritems():
        for action_id, value, new_id in annotations:
            if new_id is None:
                new_id = id_scope.getNewId(DBActionAnnotation.vtType)
            annotation = DBActionAnnotation(id=new_id,
                                            action_id=action_id,
                                            key=key,
                                            value=value)
            annotation.is_new = False
            annotation.is_dirty = False
            vistrail.db_add_actionAnnotation(annotation)

    vistrail.db_version = '1.0.2'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '1.0.2'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.2'
    return log

def translateRegistry(_registry):
    translate_dict = {}
    registry = DBRegistry.update_version(_registry, translate_dict)
    registry.db_version = '1.0.2'
    return registry
