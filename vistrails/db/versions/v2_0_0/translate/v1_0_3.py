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
    DBWorkflow, DBLog, DBRegistry, IdScope

import unittest

# 1. we probably have to worry about groups, right? or not?
# 2. what to do about ids that span log and vistrail??

def translateVistrail(_vistrail):
    """ Translate old annotation based vistrail variables to new
        DBVistrailVariable class """

    id_scope = IdScope()

    id_remap = {}
    old_class = _vistrail.__class__
    _vistrail.__class__ = DBVistrail
    vistrail = DBVistrail.do_copy(_vistrail, True, id_scope, id_remap)
    _vistrail.__class__ = old_class
    vistrail.idScope = id_scope
    for action in vistrail.db_actions:
        if action.db_prevId == 0:
            action.db_prevId = DBVistrail.ROOT_VERSION
    return vistrail

def translateWorkflow(_workflow):
    id_scope = IdScope()
    id_remap = {}
    old_class = _workflow.__class__
    _workflow.__class__ = DBWorkflow
    try:
        workflow = DBWorkflow.do_copy(_workflow, True, id_scope, id_remap)
    finally:
        _workflow.__class__ = old_class
    return workflow
    
def translateLog(_log):
    id_scope = IdScope()
    id_remap = {}
    old_class = _log.__class__
    _log.__class__ = DBLog
    try:
        log = DBLog.do_copy(_log, True, id_scope, id_remap)
    finally:
        _log.__class__ = old_class
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
