############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

