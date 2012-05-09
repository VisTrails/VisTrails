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

from core.log.machine import Machine
from core.log.workflow_exec import WorkflowExec
from db.domain import DBLog

class Log(DBLog):
    """ Class that stores info for logging a workflow execution. """

    def __init__(self, *args, **kwargs):
        DBLog.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLog.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Log
        return cp

    @staticmethod
    def convert(_log):
        if _log.__class__ == Log:
            return
        _log.__class__ = Log
        for machine in _log.machine_list:
            Machine.convert(machine)
        for workflow_exec in _log.workflow_execs:
            WorkflowExec.convert(workflow_exec)


    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_machines(self):
        return self.db_machines_id_index
    machines = property(_get_machines)
    def _get_machine_list(self):
        return self.db_machines
    machine_list = property(_get_machine_list)
    def add_machine(self, machine):
        self.db_add_machine(machine)

    def _get_workflow_execs(self):
        return self.db_workflow_execs
    workflow_execs = property(_get_workflow_execs)
    def add_workflow_exec(self, wf_exec):
        self.db_add_workflow_exec(wf_exec)

    def delete_all_workflow_execs(self):
        for wf_exec in copy.copy(self.workflow_execs):
            self.db_delete_workflow_exec(wf_exec)

    def _get_vistrail_id(self):
        return self.db_vistrail_id
    def _set_vistrail_id(self, id):
        self.db_vistrail_id = id
    vistrail_id = property(_get_vistrail_id, _set_vistrail_id)

    def get_last_workflow_exec_id(self):
        if len(self.workflow_execs) < 1:
            return -1
        return max(wf_exec.id for wf_exec in self.workflow_execs)
