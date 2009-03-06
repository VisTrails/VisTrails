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
from core.log.loop_exec import LoopExec
from core.vistrail.annotation import Annotation
from db.domain import DBGroupExec

class GroupExec(DBGroupExec):
    """ Class that stores info for logging a group/abstraction execution. """

    def __init__(self, *args, **kwargs):
        DBGroupExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self):
        cp = DBGroupExec.__copy__(self)
        cp.__class__ = GroupExec
        return cp

    @staticmethod
    def convert(_group_exec):
        if _group_exec.__class__ == GroupExec:
            return
        _group_exec.__class__ = GroupExec
        for annotation in _group_exec.annotations:
            Annotation.convert(annotation)
        for loop_exec in _group_exec.loop_execs:
            LoopExec.convert(loop_exec)
        for module_exec in _group_exec.module_execs:
            ModuleExec.convert(module_exec)
        for group_exec in _group_exec.group_execs:
            GroupExec.convert(group_exec)
            

    ##########################################################################
    # Properties

    id = DBGroupExec.db_id
    ts_start = DBGroupExec.db_ts_start
    ts_end = DBGroupExec.db_ts_end
    cached = DBGroupExec.db_cached
    module_id = DBGroupExec.db_module_id
    group_name = DBGroupExec.db_group_name
    group_type = DBGroupExec.db_group_type
    completed = DBGroupExec.db_completed
    error = DBGroupExec.db_error
    machine_id = DBGroupExec.db_machine_id

    def _get_duration(self):
        if self.db_ts_end is not None:
            return self.db_ts_end - self.db_ts_start
        return None
    duration = property(_get_duration)

    def _get_annotations(self):
        return self.db_annotations
    def _set_annotations(self, annotations):
        self.db_annotations = annotations
    annotations = property(_get_annotations, _set_annotations)
    def add_annotation(self, annotation):
        self.db_add_annotation(annotation)

    def _get_loop_execs(self):
        return self.db_loop_execs
    def _set_loop_execs(self, loop_execs):
        self.db_loop_execs = loop_execs
    loop_execs = property(_get_loop_execs, _set_loop_execs)
    def add_loop_exec(self, loop_exec):
        self.db_add_loop_exec(loop_exec)

    def _get_module_execs(self):
        return self.db_module_execs
    def _set_module_execs(self, module_execs):
        self.db_module_execs = module_execs
    module_execs = property(_get_module_execs, _set_module_execs)
    def add_module_exec(self, module_exec):
        self.db_add_module_exec(module_exec)

    def _get_group_execs(self):
        return self.db_group_execs
    def _set_group_execs(self, group_execs):
        self.db_group_execs = group_execs
    group_execs = property(_get_group_execs, _set_group_execs)
    def add_group_exec(self, group_exec):
        self.db_add_group_exec(group_exec)
