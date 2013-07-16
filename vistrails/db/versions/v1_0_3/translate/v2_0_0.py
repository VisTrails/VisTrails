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
from vistrails.db.versions.v1_0_3.domain import DBVistrail, \
    DBWorkflow, DBLog, DBRegistry, DBAdd, DBChange, DBDelete, DBAbstraction, \
    DBGroup, DBModule, DBActionAnnotation, DBAnnotation, DBLoopExec, \
    DBModuleExec, DBGroupExec, IdScope

import unittest

def translateVistrail(_vistrail):
    """ Translate old annotation based vistrail variables to new
        DBVistrailVariable class """

    id_scope = IdScope(remap={DBAdd.vtType: 'operation',
                              DBChange.vtType: 'operation',
                              DBDelete.vtType: 'operation',
                              DBAbstraction.vtType: DBModule.vtType,
                              DBGroup.vtType: DBModule.vtType,
                              DBActionAnnotation.vtType: \
                              DBAnnotation.vtType})
    
    id_scope.setBeginId('action', 1)

    id_remap = {}
    old_class = _vistrail.__class__
    _vistrail.__class__ = DBVistrail
    try:
        vistrail = DBVistrail.do_copy(_vistrail, True, id_scope, id_remap)
    finally:
        _vistrail.__class__ = old_class
    vistrail.idScope = id_scope
    return vistrail

def translateWorkflow(_workflow):
    # do we need to do this with negative numbers (see self.tmp_id)?
    id_scope = IdScope(remap={DBAbstraction.vtType: DBModule.vtType,
                              DBGroup.vtType: DBModule.vtType})
    id_remap = {}
    old_class = _workflow.__class__
    _workflow.__class__ = DBWorkflow
    try:
        workflow = DBWorkflow.do_copy(_workflow, True, id_scope, id_remap)
    finally:
        _workflow.__class__ = old_class
    workflow.id_scope = id_scope
    return workflow
    
def translateLog(_log):
    id_scope = IdScope(1,
                       {DBLoopExec.vtType: 'item_exec',
                        DBModuleExec.vtType: 'item_exec',
                        DBGroupExec.vtType: 'item_exec',
                        DBAbstraction.vtType: DBModule.vtType,
                        DBGroup.vtType: DBModule.vtType})
    id_remap = {}
    old_class = _log.__class__
    _log.__class__ = DBLog
    try:
        log = DBLog.do_copy(_log, True, id_scope, id_remap)
    finally:
        _log.__class__ = old_class
    log.idScope = id_scope
    return log

def translateRegistry(_registry):
    id_scope = IdScope()
    id_remap = {}
    old_class = _registry.__class__
    _registry.__class__ = DBRegistry
    try:
        registry = DBRegistry.do_copy(_registry, True, id_scope, id_remap)
    finally:
        _registry.__class__ = old_class
    return registry
