###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
from vistrails.db.versions.v2_0_0.domain import DBVistrail, \
    DBWorkflow, DBLog, DBRegistry, DBStartup, DBMashuptrail, DBAction, \
    DBAdd, DBChange, DBDelete, DBAbstraction, DBGroup, DBActionAnnotation, \
    DBModule, DBAnnotation, IdScope

import copy
import unittest

# 1. we probably have to worry about groups, right? or not?
# 2. what to do about ids that span log and vistrail??

# id_scope = None

def translateVistrail(_vistrail, external_data=None):
    if external_data is not None and "id_remap" in external_data:
        id_remap = external_data["id_remap"]
    else:
        id_remap = {}
    if external_data is not None and "group_remaps" in external_data:
        group_remaps = external_data["group_remaps"]
    else:
        group_remaps = {}
    if external_data is not None and "translate_dict" in external_data:
        translate_dict = copy.copy(external_data["translate_dict"])
    else:
        translate_dict = {}

    if (DBAction.vtType, 0) not in id_remap:
        id_remap[(DBAction.vtType, 0)] = DBVistrail.ROOT_VERSION

    def update_workflow(old_obj, trans_dict):
        if old_obj.db_id in group_remaps:
            group_remap = group_remaps[old_obj.db_id]
        else:
            group_remap = {}

        group_data = {"translate_dict": trans_dict,
                      "id_remap": group_remap}
        workflow = translateWorkflow(old_obj.db_workflow, group_data)
        group_remaps[old_obj.db_id] = group_data["id_remap"]
        return workflow

    if 'DBGroup' not in translate_dict:
        translate_dict['DBGroup'] = {'workflow': update_workflow}
    vistrail = DBVistrail()
    id_scope = vistrail.idScope
    vistrail = DBVistrail.update_version(_vistrail, translate_dict, vistrail)
    # FIXME have to eventually expand the inner workflows and update their ids
    vistrail = vistrail.do_copy(True, id_scope, id_remap)

    # remap upgrade annotations
    for ann in vistrail.db_actionAnnotations[:]:
        if ann.db_key == "__upgrade__": # vistrails.core.vistrail.vistrail.Vistrail.UPDATE_ANNOTATION
            vistrail.db_delete_actionAnnotation(ann)
            ann.db_value = "%s" % id_remap[(DBAction.vtType, long(ann.db_value))]
            vistrail.db_add_actionAnnotation(ann)

    vistrail.db_version = '2.0.0'
    return vistrail

def translateWorkflow(_workflow, external_data=None):
    if external_data is not None and "id_remap" in external_data:
        id_remap = external_data["id_remap"]
    else:
        id_remap = {}
    if external_data is not None and "group_remaps" in external_data:
        group_remaps = external_data["group_remaps"]
    else:
        group_remaps = {}
    if external_data is not None and "translate_dict" in external_data:
        translate_dict = external_data["translate_dict"]
    else:
        translate_dict = {}

    def update_workflow(old_obj, trans_dict):
        if old_obj.db_id in group_remaps:
            group_remap = group_remaps[old_obj.db_id]
        else:
            group_remap = {}

        group_data = {"translate_dict": trans_dict,
                      "id_remap": group_remap}
        workflow = translateWorkflow(old_obj.db_workflow, group_data)
        group_remaps[old_obj.db_id] = group_data["id_remap"]
        return workflow

    if 'DBGroup' not in translate_dict:
        translate_dict['DBGroup'] = {'workflow': update_workflow}

    workflow = DBWorkflow()
    id_scope = IdScope(remap={DBAbstraction.vtType: DBModule.vtType, DBGroup.vtType: DBModule.vtType})
    workflow = DBWorkflow.update_version(_workflow, translate_dict, workflow)
    workflow = workflow.do_copy(True, id_scope, id_remap)
    workflow.db_version = '2.0.0'
    return workflow

def translateLog(_log, external_data=None):
    if external_data is not None and "id_remap" in external_data:
        id_remap = external_data["id_remap"]
    else:
        id_remap = {}
    if external_data is not None and "translate_dict" in external_data:
        translate_dict = external_data["translate_dict"]
    else:
        translate_dict = {}

    log = DBLog()
    id_scope = log.id_scope
    log = DBLog.update_version(_log, translate_dict, log)
    log = log.do_copy(True, id_scope, id_remap)
    log.db_version = '2.0.0'
    return log

def translateRegistry(_registry, external_data=None):
    if external_data is not None and "id_remap" in external_data:
        id_remap = external_data["id_remap"]
    else:
        id_remap = {}
    if external_data is not None and "translate_dict" in external_data:
        translate_dict = external_data["translate_dict"]
    else:
        translate_dict = {}

    registry = DBRegistry()
    id_scope = registry.id_scope
    registry = DBRegistry.update_version(_registry, translate_dict, registry)
    registry = registry.do_copy(True, id_scope, id_remap)
    registry.db_version = '2.0.0'
    return registry

def translateMashup(_mashup, external_data=None):
    #FIXME check if this is correct
    if external_data is not None and "id_remap" in external_data:
        id_remap = external_data["id_remap"]
    else:
        id_remap = {}

    translate_dict = {}
    mashup = DBMashuptrail()
    id_scope = mashup.id_scope
    mashup = DBMashuptrail.update_version(_mashup, translate_dict, mashup)
    mashup = mashup.do_copy(True, id_scope, id_remap)
    mashup.db_version = '2.0.0'
    return mashup

def translateStartup(_startup, external_data=None):
    startup = DBStartup()
    translate_dict = {}
    startup = DBStartup.update_version(_startup, translate_dict, startup)

    startup.db_version = '2.0.0'
    return startup