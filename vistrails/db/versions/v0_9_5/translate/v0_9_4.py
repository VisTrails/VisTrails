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

import copy
from vistrails.db.versions.v0_9_5.domain import DBVistrail, DBWorkflow, DBLog, \
    DBRegistry, DBModuleExec

def translateVistrail(_vistrail):
    def update_signature(old_obj, translate_dict):
        return old_obj.db_spec
    def update_optional(old_obj, translate_dict):
        return 0
    def update_sort_key(old_obj, translate_dict):
        return -1
    def update_sigstring(old_obj, translate_dict):
        return old_obj.db_spec
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    translate_dict = {'DBPortSpec': {'sigstring': update_sigstring,
                                     'optional': update_optional,
                                     'sort_key': update_sort_key},
                      'DBPort': {'signature': update_signature},
                      'DBGroup': {'workflow': update_workflow}}

    # pass DBVistrail because domain contains enriched version of the auto_gen
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '0.9.5'
    return vistrail

def translateWorkflow(_workflow):
    def update_signature(old_obj, translate_dict):
        return old_obj.db_spec
    def update_optional(old_obj, translate_dict):
        return 0
    def update_sort_key(old_obj, translate_dict):
        return -1
    def update_sigstring(old_obj, translate_dict):
        return old_obj.db_spec
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    translate_dict = {'DBPortSpec': {'sigstring': update_sigstring,
                                     'optional': update_optional,
                                     'sort_key': update_sort_key},
                      'DBPort': {'signature': update_signature},
                      'DBGroup': {'workflow': update_workflow}}

    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '0.9.5'
    return workflow

def translateLog(_log):
    def update_items(old_obj, translate_dict):
        new_items = []
        for obj in old_obj.db_module_execs:
            new_items.append(DBModuleExec.update_version(obj, translate_dict))
        return new_items
    translate_dict = {'DBWorkflowExec': {'items': update_items}}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '0.9.5'
    return log

def translateRegistry(_registry):
    translate_dict = {}
    registry = DBRegistry.update_version(_registry, translate_dict)
    registry.db_version = '0.9.5'
    return registry
