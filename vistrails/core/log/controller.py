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

import copy

from vistrails.core.log.workflow_exec import WorkflowExec
from vistrails.core.log.module_exec import ModuleExec
from vistrails.core.log.loop_exec import LoopExec
from vistrails.core.log.group_exec import GroupExec
from vistrails.core.log.machine import Machine
from vistrails.core.modules.sub_module import Group, Abstraction
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.vistrail import Vistrail
import vistrails.core.system

@apply
class DummyLogController(object):
    """DummyLogger is a class that has the entire interface for a logger
    but simply ignores the calls."""
    def start_workflow_execution(self, *args, **kwargs): pass
    def finish_workflow_execution(self, *args, **kwargs): pass
    def start_execution(self, *args, **kwargs): pass
    def finish_execution(self, *args, **kwargs): pass
    def insert_module_annotations(self, *args, **kwargs): pass
    def insert_workflow_exec_annotations(self, *args, **kwargs): pass
    def add_exec(self, *args, **kwargs): pass
    def __call__(self): return self

class LogController(object):
    local_machine = Machine(
            id=-1,
            name=vistrails.core.system.current_machine(),
            os=vistrails.core.system.systemType,
            architecture=vistrails.core.system.current_architecture(),
            processor=vistrails.core.system.current_processor(),
            ram=vistrails.core.system.guess_total_memory())

    def __init__(self, log):
        self.log = log
        self.workflow_exec = None
        self.machine = copy.copy(self.local_machine)
        for machine in self.log.machine_list:
            if self.machine.equals_no_id(machine):
                self.machine = machine
                break
        else:
            self.machine.id = self.log.id_scope.getNewId(Machine.vtType)
            self.log.add_machine(self.machine)

    def start_workflow_execution(self, vistrail=None, pipeline=None,
                                 currentVersion=None):
        """Signals the start of the execution of a pipeline.
        """
        if vistrail is not None:
            parent_type = Vistrail.vtType
            parent_id = vistrail.id
        else:
            parent_type = Pipeline.vtType
            parent_id = pipeline.id

        wf_exec_id = self.log.id_scope.getNewId(WorkflowExec.vtType)
        if vistrail is not None:
            session = vistrail.current_session
        else:
            session = None
        self.workflow_exec = WorkflowExec(
                id=wf_exec_id,
                user=vistrails.core.system.current_user(),
                ip=vistrails.core.system.current_ip(),
                vt_version=vistrails.core.system.vistrails_version(),
                ts_start=vistrails.core.system.current_time(),
                parent_type=parent_type,
                parent_id=parent_id,
                parent_version=currentVersion,
                completed=0,
                session=session)
        self.log.add_workflow_exec(self.workflow_exec)

    def finish_workflow_execution(self, errors, suspended=False):
        """Signals the end of the execution of a pipeline.
        """
        self.workflow_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            self.workflow_exec.completed = -2
        elif len(errors) > 0:
            self.workflow_exec.completed = -1
        else:
            self.workflow_exec.completed = 1

    def add_exec(self, exec_, parent_execs):
        """Adds an execution object to the log.
        """
        parent_exec = parent_execs[-1]
        if parent_exec:
            parent_exec.add_item_exec(exec_)
        else:
            self.workflow_exec.add_item_exec(exec_)

    def _create_module_exec(self, module, module_id, module_name,
                           cached):
        m_exec_id = self.log.id_scope.getNewId(ModuleExec.vtType)
        module_exec = ModuleExec(id=m_exec_id,
                                 machine_id=self.machine.id,
                                 module_id=module_id,
                                 module_name=module_name,
                                 cached=cached,
                                 ts_start=vistrails.core.system.current_time(),
                                 completed=0)
        return module_exec

    def _create_group_exec(self, group, module_id, group_name, cached):
        g_exec_id = self.log.id_scope.getNewId(GroupExec.vtType)
        if isinstance(group, Abstraction):
            group_type = 'SubWorkflow'
        else:
            group_type = 'Group'
        group_exec = GroupExec(id=g_exec_id,
                               machine_id=self.machine.id,
                               module_id=module_id,
                               group_name=group_name,
                               group_type=group_type,
                               cached=cached,
                               ts_start=vistrails.core.system.current_time(),
                               completed=0)
        return group_exec

    def _create_loop_exec(self, iteration):
        l_exec_id = self.log.id_scope.getNewId(LoopExec.vtType)
        loop_exec = LoopExec(id=l_exec_id,
                             iteration=iteration,
                             ts_start=vistrails.core.system.current_time())
        return loop_exec

    def start_execution(self, module, module_id, module_name, parent_execs,
                        cached=0):
        """Signals the start of the execution of a module (before compute).
        """
        parent_exec = parent_execs[-1]
        if module.is_looping:
            parent_exec = self._start_loop_execution(module, module_id,
                                                    module_name,
                                                    parent_exec, cached,
                                                    module.loop_iteration)
            parent_execs.append(parent_exec)

        if isinstance(module, Group):
            ret = self._start_group_execution(module, module_id, module_name,
                                             parent_exec, cached)
            if ret is not None:
                parent_execs.append(ret)
        else:
            ret = self._start_module_execution(module, module_id, module_name,
                                              parent_exec, cached)
            if ret is not None:
                parent_execs.append(ret)

    def finish_execution(self, module, error, parent_execs, errorTrace=None,
                         suspended=False):
        """Signals the end of the execution of a module.

        Called by a module after succeeded of suspended, or called by the
        interpreter after an exception.
        """
        if isinstance(module, Group):
            if self._finish_group_execution(module, error, suspended):
                parent_execs.pop()
        else:
            if self._finish_module_execution(module, error, errorTrace, suspended):
                parent_execs.pop()
        if module.is_looping:
            self._finish_loop_execution(module, error, parent_execs.pop(), suspended)

    def _start_module_execution(self, module, module_id, module_name,
                               parent_exec, cached):
        """Called by start_execution() for regular modules.
        """
        module_exec = self._create_module_exec(module, module_id,
                                              module_name,
                                              cached)
        module.module_exec = module_exec
        if parent_exec:
            parent_exec.add_item_exec(module_exec)
        else:
            self.workflow_exec.add_item_exec(module_exec)
        if module.is_looping_module:
            return module_exec
        return None

    def _finish_module_execution(self, module, error, errorTrace=None,
                                suspended=False):
        """Called by finish_execution() for regular modules.
        """
        if not hasattr(module, 'module_exec'):
            return False
        module.module_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            module.module_exec.completed = -2
            module.module_exec.error = error
        elif not error:
            module.module_exec.completed = 1
        else:
            module.module_exec.completed = -1
            module.module_exec.error = error
            if errorTrace:
                a_id = self.log.id_scope.getNewId(Annotation.vtType)
                annotation = Annotation(id=a_id,
                                        key="errorTrace",
                                        value=errorTrace)
                module.module_exec.add_annotation(annotation)
        del module.module_exec
        if module.is_looping_module:
            return True

    def _start_group_execution(self, group, module_id, group_name,
                              parent_exec, cached):
        """Called by start_execution() for groups.
        """
        group_exec = self._create_group_exec(group, module_id,
                                            group_name, cached)
        group.group_exec = group_exec
        if parent_exec:
            parent_exec.add_item_exec(group_exec)
        else:
            self.workflow_exec.add_item_exec(group_exec)
        return group_exec

    def _finish_group_execution(self, group, error, suspended=False):
        """Called by finish_execution() for groups.
        """
        if not hasattr(group, 'group_exec'):
            return False
        group.group_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            group.group_exec.completed = -2
            group.group_exec.error = error
        elif not error:
            group.group_exec.completed = 1
        else:
            group.group_exec.completed = -1
            group.group_exec.error = error
        del group.group_exec
        return True

    def _start_loop_execution(self, module, module_id, module_name,
                             parent_exec, cached, iteration):
        """Called by start_execution() for modules on which is_looping is set.

        The module that acts as a loop sets is_looping on the module it's
        executing beforehand, so this method can create a LoopExec object.
        """
        loop_exec = self._create_loop_exec(iteration)
        if parent_exec:
            parent_exec.add_loop_exec(loop_exec)
        else:
            self.workflow_exec.add_item_exec(loop_exec)
        return loop_exec

    def _finish_loop_execution(self, module, error, loop_exec, suspended=True):
        """Called by finish_execution() for modules on which is_looping is set.
        """
        if not loop_exec:
            return False
        loop_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            loop_exec.completed = -2
            loop_exec.error = error
        elif not error:
            loop_exec.completed = 1
        else:
            loop_exec.completed = -1
            loop_exec.error = error
        return True

    def insert_module_annotations(self, module, a_dict):
        """Adds an annotation on the execution object for this module.
        """
        for k, v in a_dict.iteritems():
            a_id = self.log.id_scope.getNewId(Annotation.vtType)
            annotation = Annotation(id=a_id,
                                    key=k,
                                    value=v)
            if hasattr(module, 'is_group'):
                module.group_exec.add_annotation(annotation)
            else:
                module.module_exec.add_annotation(annotation)

    def insert_workflow_exec_annotations(self, a_dict):
        """Adds an annotation on the whole workflow log object.

        The information is not associated with the execution of a specific
        module but of the whole pipeline.
        """
        if self.workflow_exec:
            for k, v in a_dict.iteritems():
                a_id = self.log.id_scope.getNewId(Annotation.vtType)
                annotation = Annotation(id=a_id,
                                        key=k,
                                        value=v)
                self.workflow_exec.add_annotation(annotation)
