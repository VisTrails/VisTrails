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
    def start_workflow_execution(self, *args, **kwargs): return self
    def finish_workflow_execution(self, *args, **kwargs): pass
    def add_exec(self, *args, **kwargs): pass
    def start_execution(self, *args, **kwargs): pass
    def start_loop_execution(self, *args, **kwargs): pass
    def finish_loop_execution(self, *args, **kwargs): pass
    def finish_execution(self, *args, **kwargs): pass
    def insert_module_annotations(self, *args, **kwargs): pass
    def insert_workflow_exec_annotations(self, *args, **kwargs): pass
    def __call__(self): return self


class LogController(object):
    """The top-level log controller.

    This holds a log.
    """
    local_machine = Machine(
            id=-1,
            name=vistrails.core.system.current_machine(),
            os=vistrails.core.system.systemType,
            architecture=vistrails.core.system.current_architecture(),
            processor=vistrails.core.system.current_processor(),
            ram=vistrails.core.system.guess_total_memory())

    def __init__(self, log):
        self.log = log
        self.machine = copy.copy(self.local_machine)
        for machine in self.log.machine_list:
            if self.machine.equals_no_id(machine):
                self.machine = machine
                break
        else:
            self.machine.id = self.log.id_scope.getNewId(Machine.vtType)
            self.log.add_machine(self.machine)

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

    def start_workflow_execution(self, parent_exec,
                                 vistrail=None, pipeline=None,
                                 currentVersion=None):
        """Signals the start of the execution of a pipeline.
        """
        print "LogController#start_workflow_execution()"
        return LogWorkflowController(self.log, parent_exec,
                                     vistrail, pipeline, currentVersion)


# TODO : store module_exec, parent_exec, children_exec in dicts here instead
# of using Module attributes

class LogWorkflowController(LogController):
    """A log controller for a specific workflow execution.

    You get one of these by calling LogController#start_workflow_execution().
    You can then add execution items through it.

    How does this work:
      * the interpreter sets a 'logging' attribute on summoned Module objects
        before starting the execution. Through it, the module can log events.
      * the interpreter directly uses the logger to record exceptions from the
        pipeline
      * the logger sets the 'module_exec', 'parent_exec' and 'children_exec' on
        modules while they are executing:
         - module_exec is the execution entry for that module
         - parent_exec is set via other modules to remember where the soon-to-
           be-created module_exec should be added (for example, loop modules
           and Group sets parent_exec on their dependent modules). If
           parent_exec is not set, the parent exec or WorkflowExec will be used
         - children_exec is a list of ongoing exec items, children of
           module_exec, such as LoopExec. They are kept their to be marked as
           finished with the same error as the module if it fails before they
           end
    """
    def __init__(self, log, parent_exec, vistrail=None, pipeline=None,
                 currentVersion=None):
        super(LogWorkflowController, self).__init__(log)
        self.parent_exec = parent_exec

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
        print "LogWorkflowController() [self=%r, adding workflow_exec %r %d" % (self, self.workflow_exec, wf_exec_id)
        self.log.add_workflow_exec(self.workflow_exec)

    def finish_workflow_execution(self, errors, suspended=False):
        """Signals the end of the execution of a pipeline.
        """
        print "LogWorkflowController#finish_workflow_execution(errors=%r, suspended=%r)" % (errors, suspended)
        self.workflow_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            self.workflow_exec.completed = -2
        elif len(errors) > 0:
            self.workflow_exec.completed = -1
        else:
            self.workflow_exec.completed = 1

    def start_execution(self, module, module_id, module_name, cached=0):
        """Signals the start of the execution of a module (before compute).
        """
        print "LogWorkflowController#start_execution(module=%r, module_id=%r, module_name=%r, cached=%r)" % (
                module, module_id, module_name, cached)
        if isinstance(module, Group):
            module_exec = self._create_group_exec(module, module_id,
                                                 module_name, cached)
        else:
            module_exec = self._create_module_exec(module, module_id,
                                                   module_name, cached)
        if module.module_exec is not None:
            print "  oops! module already has module_exec %r ; overwriting!" % module.module_exec
        module.module_exec = module_exec
        print "  .module_exec=%r" % module_exec
        for parent_exec in (module.parent_exec, self.parent_exec,
                            self.workflow_exec):
            if parent_exec is not None:
                if parent_exec is module.parent_exec:
                    print "  adding to module's parent_exec %r" % parent_exec
                elif parent_exec is self.parent_exec:
                    print "  adding to controller's parent_exec %r" % parent_exec
                else:
                    print "  adding to workflow_exec %r" % parent_exec
                parent_exec.add_item_exec(module_exec)
                return
        assert False

    def start_loop_execution(self, loop_module, looped_module,
                             iteration, total_iterations=None):
        """Registers a looped module.
        """
        print "LogWorkflowController#start_loop_execution(loop_module=%r, looped_module=%r, %r, %r)" % (
                loop_module, looped_module, iteration, total_iterations)
        loop_exec = self._create_loop_exec(iteration)
        for parent_exec in (loop_module.parent_exec, self.parent_exec):
            if parent_exec is not None:
                if parent_exec is loop_module.parent_exec:
                    print "  adding LoopExec to loop_module's parent_exec %r" % parent_exec
                else:
                    print "  adding LoopExec to controller's parent_exec" % parent_exec
                parent_exec.add_loop_exec(loop_exec)
                break
        else:
            print "  adding to workflow_exec %r" % self.workflow_exec
            self.workflow_exec.add_item_exec(loop_exec)
        looped_module.parent_exec = loop_exec
        loop_module.children_exec.add(loop_exec)

    def finish_loop_execution(self, loop_module, looped_module, error, suspended=False):
        """Signals that we are done looping.
        """
        print "LogWorkflowController#finish_loop_execution(loop_module=%r, looping_module=%r)" % (
                loop_module, looped_module)
        loop_exec = looped_module.parent_exec
        assert loop_exec is not None
        looped_module.parent_exec = None

        loop_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            loop_exec.completed = -2
            loop_exec.error = error
        elif not error:
            loop_exec.completed = 1
        else:
            loop_exec.completed = -1
            loop_exec.error = error
        loop_module.children_exec.remove(loop_exec)

    def finish_execution(self, module, error, errorTrace=None, suspended=False):
        """Signals the end of the execution of a module.

        Called by a module after succeeded of suspended, or called by the
        interpreter after an exception.
        """
        print "LogWorkflowController#finish_execution(module=%r, error=%r, suspended=%r" % (
                module, error, suspended)
        assert (hasattr(module, 'module_exec') and
                module.module_exec is not None)
        module.module_exec.ts_end = vistrails.core.system.current_time()
        if suspended:
            module.module_exec.completed = -2
            module.module_exec.error = error
        elif error:
            module.module_exec.completed = -1
            module.module_exec.error = error
            if errorTrace:
                a_id = self.log.id_scope.getNewId(Annotation.vtType)
                annotation = Annotation(id=a_id,
                                        key="errorTrace",
                                        value=errorTrace)
                module.module_exec.add_annotation(annotation)
        else:
            module.module_exec.completed = 1
        module.module_exec = None

        for child in module.children_exec:
            child.ts_end = vistrails.core.system.current_time()
            if suspended:
                child.completed = -2
                child.error = error
            elif not error:
                child.completed = 1
            else:
                child.completed = -1
                child.error = error

    def insert_module_annotations(self, module, a_dict):
        """Adds an annotation on the execution object for this module.
        """
        for k, v in a_dict.iteritems():
            a_id = self.log.id_scope.getNewId(Annotation.vtType)
            annotation = Annotation(id=a_id,
                                    key=k,
                                    value=v)
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
