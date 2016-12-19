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
from vistrails.db.versions.v0_9_4.domain import DBVistrail, DBAction, DBTag, DBModule, \
    DBConnection, DBPortSpec, DBFunction, DBParameter, DBLocation, DBAdd, \
    DBChange, DBDelete, DBAnnotation, DBPort, DBGroup, \
    DBWorkflow, DBLog, DBAbstraction

def update_workflow(old_obj, translate_dict):
    return DBWorkflow.update_version(old_obj.db_workflow, 
                                     translate_dict, DBWorkflow())

def update_modules(old_obj, trans_dict):
    new_modules = []
    for obj in old_obj.db_modules:
        if obj.vtType == 'module':
            new_modules.append(DBModule.update_version(obj, trans_dict))
        elif obj.vtType == 'abstractionRef':
            new_modules.append(DBAbstraction.update_version(obj,
                                                               trans_dict))
        elif obj.vtType == 'group':
            new_modules.append(DBGroup.update_version(obj, trans_dict))
    return new_modules

def translateVistrail(_vistrail):
    def update_operations(old_obj, trans_dict):
        def update_abstractionRef(old_obj, trans_dict):
            def get_internal_version(old_obj, trans_dict):
                return str(old_obj.db_version)
            def get_version(old_obj, trans_dict):
                return ''
            new_dict = {'DBAbstraction':
                        {'internal_version': get_internal_version,
                         'version': get_version}}
            new_dict.update(trans_dict)
            return DBAbstraction.update_version(old_obj.db_data, new_dict)
        new_ops = []
        for obj in old_obj.db_operations:
            if obj.vtType == 'add':
                if obj.db_what == 'abstractionRef':
                    trans_dict['DBAdd'] = {'data': update_abstractionRef}
                    new_op = DBAdd.update_version(obj, trans_dict)
                    new_op.db_what = 'abstraction'
                    new_ops.append(new_op)
                    del trans_dict['DBAdd']
                else:
                    new_op = DBAdd.update_version(obj, trans_dict)
                    if obj.db_parentObjType == 'abstractionRef':
                        new_op.db_parentObjType = 'abstraction'
                    new_ops.append(new_op)
            elif obj.vtType == 'delete':
                new_ops.append(DBDelete.update_version(obj, trans_dict))
            elif obj.vtType == 'change':
                if obj.db_what == 'abstractionRef':
                    trans_dict['DBChange'] = {'data': update_abstractionRef}
                    new_op = DBChange.update_version(obj, trans_dict)
                    new_op.db_what = 'abstraction'
                    new_ops.append(new_op)
                    del trans_dict['DBChange']
                else:
                    new_op = DBChange.update_version(obj, trans_dict)
                    if obj.db_parentObjType == 'abstractionRef':
                        new_op.db_parentObjType = 'abstraction'
                    new_ops.append(new_op)
        return new_ops

    translate_dict = {'DBGroup': {'workflow': update_workflow},
                      'DBAction': {'operations': update_operations},
                      'DBWorkflow': {'modules': update_modules}}
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '0.9.4'
    return vistrail

def translateWorkflow(_workflow):
    translate_dict = {'DBGroup': {'workflow': update_workflow},
                      'DBWorkflow': {'modules': update_modules}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '0.9.4'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '0.9.4'
    return log
