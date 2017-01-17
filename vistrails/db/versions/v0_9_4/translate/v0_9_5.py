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
from vistrails.core import debug
from vistrails.db.versions.v0_9_4.domain import DBVistrail, DBWorkflow, DBLog, DBGroup, DBModuleExec

def translateVistrail(_vistrail):
    def update_port_spec_spec(new_obj, translate_dict):
        return new_obj.db_sigstring
    def update_port_spec(new_obj, translate_dict):
        return new_obj.db_signature
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    translate_dict = {'DBPortSpec': {'spec': update_port_spec_spec},
                      'DBPort': {'spec': update_port_spec},
                      'DBGroup': {'workflow': update_workflow}}

    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '0.9.4'
    return vistrail

def translateWorkflow(_workflow):
    def update_port_spec_spec(new_obj, translate_dict):
        return new_obj.db_sigstring
    def update_port_spec(new_obj, translate_dict):
        return new_obj.db_signature
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    translate_dict = {'DBPortSpec': {'spec': update_port_spec_spec},
                      'DBPort': {'spec': update_port_spec},
                      'DBGroup': {'workflow': update_workflow}}

    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '0.9.4'
    return workflow

def translateLog(_log):
    def update_module_execs(old_obj, translate_dict):
        new_module_execs = []
        for obj in old_obj.db_items:
            if obj.vtType == 'module_exec':
                new_module_execs.append(DBModuleExec.update_version(obj, 
                                                            translate_dict))
            elif obj.vtType == 'group_exec':
                # cannot handle group execs
                debug.warning('Cannot translate group exec')
            elif obj.vtType == 'loop_exec':
                debug.warning('Cannot translate loop exec')
        return new_module_execs
    translate_dict = {'DBWorkflowExec': {'module_execs': update_module_execs}}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '0.9.4'
    return log
