############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
from db.domain import DBWorkflowExec

class WorkflowExec(DBWorkflowExec):
    """ Class that stores info for logging a workflow execution. """

    def __init__(self, *args, **kwargs):
        DBWorkflowExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self):
        cp = DBWorkflowExec.__copy__(self)
        cp.__class__ = WorkflowExec
        return cp

    @staticmethod
    def convert(_wf_exec):
        if _wf_exec.__class__ == WorkflowExec:
            return
        _wf_exec.__class__ = WorkflowExec
        for module_exec in _wf_exec.module_execs:
            ModuleExec.convert(module_exec)
            

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_user(self):
        return self.db_user
    def _set_user(self, user):
        self.db_user = user
    user = property(_get_user, _set_user)

    def _get_ip(self):
        return self.db_ip
    def _set_ip(self, ip):
        self.db_ip = ip
    ip = property(_get_ip, _set_ip)

    def _get_session(self):
        return self.db_session
    def _set_session(self, session):
        self.db_session = session
    session = property(_get_session, _set_session)
    
    def _get_vt_version(self):
        return self.db_vt_version
    def _set_vt_version(self, version):
        self.db_vt_version = version
    vt_version = property(_get_vt_version, _set_vt_version)

    def _get_ts_start(self):
        return self.db_ts_start
    def _set_ts_start(self, ts_start):
        self.db_ts_start = ts_start
    ts_start = property(_get_ts_start, _set_ts_start)

    def _get_ts_end(self):
        return self.db_ts_end
    def _set_ts_end(self, ts_end):
        self.db_ts_end = ts_end
    ts_end = property(_get_ts_end, _set_ts_end)

    def _get_duration(self):
        if self.db_ts_end is not None:
            return self.db_ts_end - self.db_ts_start
        return None
    duration = property(_get_duration)

    def _get_parent_type(self):
        return self.db_parent_type
    def _set_parent_type(self, parent_type):
        self.db_parent_type = parent_type
    parent_type = property(_get_parent_type, _set_parent_type)

    def _get_parent_id(self):
        return self.db_parent_id
    def _set_parent_id(self, parent_id):
        self.db_parent_id = parent_id
    parent_id = property(_get_parent_id, _set_parent_id)

    def _get_parent_version(self):
        return self.db_parent_version
    def _set_parent_version(self, parent_version):
        self.db_parent_version = parent_version
    parent_version = property(_get_parent_version, _set_parent_version)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_module_execs(self):
        return self.db_module_execs
    module_execs = property(_get_module_execs)
    def add_module_exec(self, module_exec):
        self.db_add_module_exec(module_exec)
