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

from core.vistrail.annotation import Annotation
from db.domain import DBModuleExec

class ModuleExec(DBModuleExec):
    """ Class that stores info for logging a module execution. """

    def __init__(self, *args, **kwargs):
        DBModuleExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self):
        cp = DBModuleExec.__copy__(self)
        cp.__class__ = ModuleExec
        return cp

    @staticmethod
    def convert(_module_exec):
        if _module_exec.__class__ == ModuleExec:
            return
        _module_exec.__class__ = ModuleExec
        for annotation in _module_exec.annotations:
            Annotation.convert(annotation)

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

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

    def _get_cached(self):
        return self.db_cached
    def _set_cached(self, cached):
        self.db_cached = cached
    cached = property(_get_cached, _set_cached)

    def _get_abstraction_id(self):
        return self.db_abstraction_id
    def _set_abstraction_id(self, id):
        self.db_abstraction_id = id
    abstraction_id = property(_get_abstraction_id, _set_abstraction_id)
    
    def _get_abstraction_version(self):
        return self.db_abstraction_version
    def _set_abstraction_version(self, version):
        self.db_abstraction_version = version
    abstraction_version = property(_get_abstraction_version, 
                                   _set_abstraction_version)

    def _get_duration(self):
        if self.db_ts_end is not None:
            return self.db_ts_end - self.db_ts_start
        return None
    duration = property(_get_duration)

    def _get_module_id(self):
        return self.db_module_id
    def _set_module_id(self, module_id):
        self.db_module_id = module_id
    module_id = property(_get_module_id, _set_module_id)

    def _get_module_name(self):
        return self.db_module_name
    def _set_module_name(self, module_name):
        self.db_module_name = module_name
    module_name = property(_get_module_name, _set_module_name)

    def _get_machine(self):
        return self.db_machine
    def _set_machine(self, machine):
        self.db_machine = machine
    machine = property(_get_machine, _set_machine)

    def _get_annotations(self):
        return self.db_annotations
    def _set_annotations(self, annotations):
        self.db_annotations = annotations
    annotations = property(_get_annotations, _set_annotations)
    def add_annotation(self, annotation):
        self.db_add_annotation(annotation)

    
