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

from core.log.workflow_exec import WorkflowExec
from core.log.module_exec import ModuleExec
from core.log.loop_exec import LoopExec
from core.log.group_exec import GroupExec
from core.log.machine import Machine
from core.modules.sub_module import Group, Abstraction
from core.vistrail.annotation import Annotation
from core.vistrail.pipeline import Pipeline
from core.vistrail.vistrail import Vistrail
import core.system

class DummyLogController(object):
    """DummyLogger is a class that has the entire interface for a logger
    but simply ignores the calls."""
    def start_workflow_execution(self, *args, **kwargs): pass
    def finish_workflow_execution(self, *args, **kwargs): pass
    def create_module_exec(self, *args, **kwargs): pass
    def create_group_exec(self, *args, **kwargs): pass
    def create_loop_exec(self, *args, **kwargs): pass
    def start_execution(self, *args, **kwargs): pass
    def finish_execution(self, *args, **kwargs): pass
    def start_module_loop_execution(self, *args, **kwargs): pass
    def finish_module_loop_execution(self, *args, **kwargs): pass
    def start_group_loop_execution(self, *args, **kwargs): pass
    def finish_group_loop_execution(self, *args, **kwargs): pass
    def start_module_execution(self, *args, **kwargs): pass
    def finish_module_execution(self, *args, **kwargs): pass
    def start_group_execution(self, *args, **kwargs): pass
    def finish_group_execution(self, *args, **kwargs): pass
    def start_loop_execution(self, *args, **kwargs): pass
    def finish_loop_execution(self, *args, **kwargs): pass
    def insert_module_annotations(self, *args, **kwargs): pass
    def insert_workflow_exec_annotations(self, *args, **kwargs): pass

class LogControllerFactory(object):
    _instance = None
    class LogControllerFactorySingleton(object):
        def __call__(self, *args, **kw):
            if LogControllerFactory._instance is None:
                obj = LogControllerFactory(*args, **kw)
                LogControllerFactory._instance = obj
            return LogControllerFactory._instance
        
    getInstance = LogControllerFactorySingleton()
    
    def __init__(self):
        self.machine = Machine(id=-1,
                               name=core.system.current_machine(),
                               os=core.system.systemType,
                               architecture=core.system.current_architecture(),
                               processor=core.system.current_processor(),
                               ram=core.system.guess_total_memory())
    
    def create_logger(self, log):
        return LogController(log, self.machine)

LogControllerFactory.getInstance()

class LogController(object):
    def __init__(self, log, machine):
        self.log = log
        self.workflow_exec = None
        self.machine = machine
        to_add = True
        for machine in self.log.machine_list:
            if self.machine.equals_no_id(machine):
                to_add = False
                self.machine = machine
        if to_add:
            self.machine.id = self.log.id_scope.getNewId(Machine.vtType)
            self.log.add_machine(self.machine)
            
    def start_workflow_execution(self, vistrail=None, pipeline=None, 
                                 currentVersion=None):
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
        self.workflow_exec = WorkflowExec(id=wf_exec_id,
                                          user=core.system.current_user(),
                                          ip=core.system.current_ip(),
                                          vt_version= \
                                              core.system.vistrails_version(),
                                          ts_start=core.system.current_time(),
                                          parent_type=parent_type,
                                          parent_id=parent_id,
                                          parent_version=currentVersion,
                                          completed=0,
                                          session=session)
        self.log.add_workflow_exec(self.workflow_exec)

    def finish_workflow_execution(self, errors, suspended=False):
        self.workflow_exec.ts_end = core.system.current_time()
        if suspended:
            self.workflow_exec.completed = -2
        elif len(errors) > 0:
            self.workflow_exec.completed = -1
        else:
            self.workflow_exec.completed = 1

    def create_module_exec(self, module, module_id, module_name,
                           cached):
        m_exec_id = self.log.id_scope.getNewId(ModuleExec.vtType)
        module_exec = ModuleExec(id=m_exec_id,
                                 machine_id=self.machine.id,
                                 module_id=module_id,
                                 module_name=module_name,
                                 cached=cached,
                                 ts_start=core.system.current_time(),
                                 completed=0)
        return module_exec

    def create_group_exec(self, group, module_id, group_name, cached):
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
                               ts_start=core.system.current_time(),
                               completed=0)
        return group_exec

    def create_loop_exec(self, iteration):
        l_exec_id = self.log.id_scope.getNewId(LoopExec.vtType)
        loop_exec = LoopExec(id=l_exec_id,
                             iteration=iteration,
                             ts_start=core.system.current_time())
        return loop_exec

    def start_execution(self, module, module_id, module_name, parent_execs,
                        cached=0):
        parent_exec = parent_execs[-1]
        if module.is_fold_operator:
            parent_exec = self.start_loop_execution(module, module_id, 
                                                    module_name, 
                                                    parent_exec, cached,
                                                    module.fold_iteration)
            parent_execs.append(parent_exec)

        if isinstance(module, Group):
            ret = self.start_group_execution(module, module_id, module_name,
                                             parent_exec, cached)
            if ret is not None:
                parent_execs.append(ret)
        else:
            ret = self.start_module_execution(module, module_id, module_name,
                                              parent_exec, cached)
            if ret is not None:
                parent_execs.append(ret)
        
    def finish_execution(self, module, error, parent_execs, errorTrace=None,
                         suspended=False):
        if isinstance(module, Group):
            if self.finish_group_execution(module, error, suspended):
                parent_execs.pop()
        else:
            if self.finish_module_execution(module, error, errorTrace, suspended):
                parent_execs.pop()
        if module.is_fold_operator:
            self.finish_loop_execution(module, error, parent_execs.pop(), suspended)

    def start_module_execution(self, module, module_id, module_name,
                               parent_exec, cached):
        module_exec = self.create_module_exec(module, module_id,
                                              module_name,
                                              cached)
        module.module_exec = module_exec
        if parent_exec:
            parent_exec.add_item_exec(module_exec)
        else:
            self.workflow_exec.add_item_exec(module_exec)
        if module.is_fold_module:
            return module_exec
        return None

    def finish_module_execution(self, module, error, errorTrace=None,
                                suspended=False):
        module.module_exec.ts_end = core.system.current_time()
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
        if module.is_fold_module:
            return True

    def start_group_execution(self, group, module_id, group_name,
                              parent_exec, cached):
        group_exec = self.create_group_exec(group, module_id,
                                            group_name, cached)
        group.group_exec = group_exec
        if parent_exec:
            parent_exec.add_item_exec(group_exec)
        else:
            self.workflow_exec.add_item_exec(group_exec)
        return group_exec

    def finish_group_execution(self, group, error, suspended=False):
        group.group_exec.ts_end = core.system.current_time()
        if suspended:
            group.group_exec.completed = -2
            group.group_exec.error = error
        elif not error:
            group.group_exec.completed = 1
        else:
#             if group.group_exec.module_execs and group.group_exec.\
#                module_execs[-1].error:
#                 error = 'Error in module execution with id %d.'%\
#                         group.group_exec.module_execs[-1].id
#             if group.group_exec.group_execs and group.group_exec.\
#                group_execs[-1].error:
#                 error = 'Error in group execution with id %d.'%\
#                         group.group_exec.group_execs[-1].id
            group.group_exec.completed = -1
            group.group_exec.error = error
        del group.group_exec
        return True

    def start_loop_execution(self, module, module_id, module_name, 
                             parent_exec, cached, iteration):
        loop_exec = self.create_loop_exec(iteration)
        if parent_exec:
            parent_exec.add_loop_exec(loop_exec)
        else:
            self.workflow_exec.add_item_exec(loop_exec)
        return loop_exec

    def finish_loop_execution(self, module, error, loop_exec, suspended=True):
        loop_exec.ts_end = core.system.current_time()
        if suspended:
            loop_exec.completed = -2
            loop_exec.error = error
        elif not error:
            loop_exec.completed = 1
        else:
            loop_exec.completed = -1
            loop_exec.error = error
        return True

#         is_group = isinstance(module, Group)
#         if is_group:
#             module.group_exec.loop_execs[-1].ts_end = core.system.\
#                                                       current_time()
#             if not error:
#                 module.group_exec.loop_execs[-1].completed = 1
#             else:
#                 if module.group_exec.loop_execs[-1].module_execs and\
#                    module.group_exec.loop_execs[-1].module_execs[-1].error:
#                     error = 'Error in module execution with id %d.'%\
#                             module.group_exec.loop_execs[-1].\
#                             module_execs[-1].id
#                 if module.group_exec.loop_execs[-1].group_execs and\
#                    module.group_exec.loop_execs[-1].group_execs[-1].error:
#                     error = 'Error in group execution with id %d.'%\
#                             module.group_exec.loop_execs[-1].\
#                             group_execs[-1].id
#                 module.group_exec.loop_execs[-1].completed = -1
#                 module.group_exec.loop_execs[-1].error = error
#         else:
#             module.module_exec.loop_execs[-1].ts_end = core.system.\
#                                                        current_time()
#             if not error:
#                 module.module_exec.loop_execs[-1].completed = 1
#             else:
#                 module.module_exec.loop_execs[-1].completed = -1
#                 module.module_exec.loop_execs[-1].error = error
#         return True

    def insert_module_annotations(self, module, a_dict):
        for k,v in a_dict.iteritems():
            a_id = self.log.id_scope.getNewId(Annotation.vtType)
            annotation = Annotation(id=a_id,
                                    key=k,
                                    value=v)
            if hasattr(module, 'is_group'):
                module.group_exec.add_annotation(annotation)
            else:
                module.module_exec.add_annotation(annotation)
            
    def insert_workflow_exec_annotations(self, a_dict):
        """insert_workflow_exec_annotations(a_dict)-> None
        This will create an annotation for each pair in a_dict in 
        self.workflow_exec"""
        if self.workflow_exec:
            for k,v in a_dict.iteritems():
                a_id = self.log.id_scope.getNewId(Annotation.vtType)
                annotation = Annotation(id=a_id,
                                        key=k,
                                        value=v)
                self.workflow_exec.add_annotation(annotation)
