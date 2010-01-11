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

from core.log.module_exec import ModuleExec
from core.log.group_exec import GroupExec
from db.domain import DBWorkflowExec

class WorkflowExec(DBWorkflowExec):
    """ Class that stores info for logging a workflow execution. """

    def __init__(self, *args, **kwargs):
        DBWorkflowExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflowExec.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = WorkflowExec
        return cp

    @staticmethod
    def convert(_wf_exec):
        if _wf_exec.__class__ == WorkflowExec:
            return
        _wf_exec.__class__ = WorkflowExec
        for item_exec in _wf_exec.item_execs:
            if item_exec.vtType == ModuleExec.vtType:
                ModuleExec.convert(item_exec)
            elif item_exec.vtType == GroupExec.vtType:
                GroupExec.convert(item_exec)
            elif item_exec.vtType == LoopExec.vtType:
                LoopExec.convert(item_exec)

    ##########################################################################
    # Properties

    id = DBWorkflowExec.db_id
    user = DBWorkflowExec.db_user
    ip = DBWorkflowExec.db_ip
    session = DBWorkflowExec.db_session
    vt_version = DBWorkflowExec.db_vt_version
    ts_start = DBWorkflowExec.db_ts_start
    ts_end = DBWorkflowExec.db_ts_end
    parent_type = DBWorkflowExec.db_parent_type
    parent_id = DBWorkflowExec.db_parent_id
    parent_version = DBWorkflowExec.db_parent_version
    name = DBWorkflowExec.db_name
    completed = DBWorkflowExec.db_completed

    def _get_duration(self):
        if self.db_ts_end is not None:
            return self.db_ts_end - self.db_ts_start
        return None
    duration = property(_get_duration)

    def _get_item_execs(self):
        return self.db_item_execs
    def _set_item_execs(self, item_execs):
        self.db_item_execs = item_execs
    item_execs = property(_get_item_execs, _set_item_execs)
    def add_item_exec(self, item_exec):
        self.db_add_item_exec(item_exec)
