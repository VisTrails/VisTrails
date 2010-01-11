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

from core.vistrail.annotation import Annotation
from core.log.loop_exec import LoopExec
from db.domain import DBModuleExec

class ModuleExec(DBModuleExec):
    """ Class that stores info for logging a module execution. """

    def __init__(self, *args, **kwargs):
        DBModuleExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModuleExec.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleExec
        return cp

    @staticmethod
    def convert(_module_exec):
        if _module_exec.__class__ == ModuleExec:
            return
        _module_exec.__class__ = ModuleExec
        for annotation in _module_exec.annotations:
            Annotation.convert(annotation)
        for loop_exec in _module_exec.loop_execs:
            LoopExec.convert(loop_exec)

    ##########################################################################
    # Properties

    id = DBModuleExec.db_id
    ts_start = DBModuleExec.db_ts_start
    ts_end = DBModuleExec.db_ts_end
    cached = DBModuleExec.db_cached
    completed = DBModuleExec.db_completed
    module_id = DBModuleExec.db_module_id
    module_name = DBModuleExec.db_module_name
    machine_id = DBModuleExec.db_machine_id
    error = DBModuleExec.db_error

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
        
