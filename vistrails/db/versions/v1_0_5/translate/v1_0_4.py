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

from vistrails.db.versions.v1_0_5.domain import DBVistrail, DBVistrailVariable, \
                                      DBWorkflow, DBLog, DBRegistry, \
                                      DBAdd, DBChange, DBDelete, \
                                      DBPortSpec, DBPortSpecItem, \
                                      DBParameterExploration, \
                                      DBPEParameter, DBPEFunction, \
                                      IdScope, DBAbstraction, \
                                      DBModule, DBGroup, DBAnnotation, \
                                      DBActionAnnotation, DBStartup, \
                                      DBConfigKey, DBConfigBool, DBConfigStr, \
                                      DBConfigInt, DBConfigFloat, \
                                      DBConfiguration, DBStartupPackage, \
                                      DBLoopIteration, DBLoopExec, \
                                      DBModuleExec, DBGroupExec

id_scope = None

def translateVistrail(_vistrail):
    """ Translate old annotation based vistrail variables to new
        DBVistrailVariable class """
    global id_scope

    def update_workflow(old_obj, trans_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         trans_dict, DBWorkflow())

    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    vistrail = DBVistrail()
    id_scope = vistrail.idScope
    vistrail = DBVistrail.update_version(_vistrail, translate_dict, vistrail)

    vistrail.db_version = '1.0.5'
    return vistrail

def translateWorkflow(_workflow):
    global id_scope
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}

    workflow = DBWorkflow()
    id_scope = IdScope(remap={DBAbstraction.vtType: DBModule.vtType, DBGroup.vtType: DBModule.vtType})
    workflow = DBWorkflow.update_version(_workflow, translate_dict, workflow)
    workflow.db_version = '1.0.5'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.5'
    return log

def translateRegistry(_registry):
    global id_scope
    translate_dict = {}
    registry = DBRegistry()
    id_scope = registry.idScope
    registry = DBRegistry.update_version(_registry, translate_dict, registry)
    registry.db_version = '1.0.5'
    return registry

def translateStartup(_startup):
    # format is {<old_name>: <new_name>} or
    # {<old_name>: (<new_name> | None, [conversion_f | None, inner_d | None])
    # conversion_f is a function that mutates the value and
    # inner_d recurses the translation for inner configurations

    translate_dict = {}
    startup = DBStartup()
    startup = DBStartup.update_version(_startup, translate_dict, startup)

    startup.db_version = '1.0.5'
    return startup
