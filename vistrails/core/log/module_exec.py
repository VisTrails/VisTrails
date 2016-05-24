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

from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.log.loop_exec import LoopExec
from vistrails.db.domain import DBModuleExec

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
        
