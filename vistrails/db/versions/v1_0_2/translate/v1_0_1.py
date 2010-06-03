############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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

import copy
from db.versions.v1_0_2.domain import DBVistrail, DBWorkflow, DBLog, \
    DBRegistry, DBGroup, DBActionAnnotation, DBAnnotation, DBAction, IdScope

def translateVistrail(_vistrail):
    tag_annotations = []
    notes_annotations = []
    thumb_annotations = []
    upgrade_annotations = []
    prune_annotations = []

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
                      'DBAction': {'annotations': update_annotations}}
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
