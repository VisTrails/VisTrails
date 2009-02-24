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

from core.log.workflow_exec import WorkflowExec
from core.log.module_exec import ModuleExec
from core.log.loop_exec import LoopExec
from core.log.group_exec import GroupExec
from core.log.machine import Machine
from core.vistrail.annotation import Annotation
from core.vistrail.pipeline import Pipeline
from core.vistrail.vistrail import Vistrail
import core.system

class DummyLogController(object):
    """DummyLogger is a class that has the entire interface for a logger
    but simply ignores the calls."""
    def start_workflow_execution(*args, **kwargs): pass
    def finish_workflow_execution(*args, **kwargs): pass
    def create_module_exec(*args, **kwargs): pass
    def create_group_exec(*args, **kwargs): pass
    def create_loop_exec(*args, **kwargs): pass
    def start_execution(*args, **kwargs): pass
    def finish_execution(*args, **kwargs): pass
    def start_module_loop_execution(*args, **kwargs): pass
    def finish_module_loop_execution(*args, **kwargs): pass
    def start_group_loop_execution(*args, **kwargs): pass
    def finish_group_loop_execution(*args, **kwargs): pass
    def start_module_execution(*args, **kwargs): pass
    def finish_module_execution(*args, **kwargs): pass
    def start_group_execution(*args, **kwargs): pass
    def finish_group_execution(*args, **kwargs): pass
    def start_loop_execution(*args, **kwargs): pass
    def finish_loop_execution(*args, **kwargs): pass
    def insert_module_annotations(*args, **kwargs): pass

class LogController(object):
    def __init__(self, log):
        self.log = log
        self.workflow_exec = None
        self.machine = None

    def start_workflow_execution(self, vistrail=None, pipeline=None, 
                                 currentVersion=None):
        self.machine = Machine(id=-1,
                               name=core.system.current_machine(),
                               os=core.system.systemType,
                               architecture=core.system.current_architecture(),
                               processor=core.system.current_processor(),
                               ram=core.system.guess_total_memory())
        
        to_add = True
        for machine in self.log.machine_list:
            if self.machine.equals_no_id(machine):
                to_add = False
                self.machine = machine
        if to_add:
            self.machine.id = self.log.id_scope.getNewId(Machine.vtType)
            self.log.add_machine(self.machine)

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

    def finish_workflow_execution(self, errors):
        self.workflow_exec.ts_end = core.system.current_time()
        if len(errors) > 0:
            self.workflow_exec.completed = -1
        else:
            self.workflow_exec.completed = 1

    def create_module_exec(self, module, module_id, module_name,
                           abstraction_id, abstraction_version,
                           cached):
        m_exec_id = self.log.id_scope.getNewId(ModuleExec.vtType)
        module_exec = ModuleExec(id=m_exec_id,
                                 machine_id=self.machine.id,
                                 module_id=module_id,
                                 module_name=module_name,
                                 abstraction_id=abstraction_id,
                                 abstraction_version=abstraction_version,
                                 cached=cached,
                                 ts_start=core.system.current_time(),
                                 completed=0)
        return module_exec

    def create_group_exec(self, group, module_id, group_name, cached):
        g_exec_id = self.log.id_scope.getNewId(GroupExec.vtType)
        group_ = group.moduleInfo['pipeline'].\
                 modules[group.moduleInfo['moduleId']]
        is_group = group_.is_group()
        is_abstraction = group_.is_abstraction()
        if is_group:
            group_type = 'Group'
        if is_abstraction:
            group_type = 'SubWorkflow'
        group_exec = GroupExec(id=g_exec_id,
                               machine_id=self.machine.id,
                               module_id=module_id,
                               group_name=group_name,
                               group_type=group_type,
                               cached=cached,
                               ts_start=core.system.current_time(),
                               completed=0)
        return group_exec

    def create_loop_exec(self):
        l_exec_id = self.log.id_scope.getNewId(LoopExec.vtType)
        loop_exec = LoopExec(id = l_exec_id,
                             ts_start = core.system.current_time())
        return loop_exec

    def start_execution(self, module, module_id, module_name, parent_exec,\
                        abstraction_id=None, abstraction_version=None,
                        cached=0):
        is_group = module.moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_group() or module.\
                   moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_abstraction()
        if (module.is_fold_operator):
            if not is_group:
                self.start_module_loop_execution(module, module_id,
                                                 module_name,
                                                 abstraction_id,
                                                 abstraction_version,
                                                 parent_exec,
                                                 cached)
            else:
                self.start_group_loop_execution(module, module_id,
                                                module_name, parent_exec,
                                                cached)
        else:
            if not is_group:
                self.start_module_execution(module, module_id,
                                            module_name,
                                            abstraction_id,
                                            abstraction_version,
                                            parent_exec, cached)
            else:
                self.start_group_execution(module, module_id, module_name,
                                           parent_exec, cached)

    def finish_execution(self, module, error=''):
        is_group = module.moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_group() or module.\
                   moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_abstraction()
        if (module.is_fold_operator):
            if not is_group:
                self.finish_module_loop_execution(module, error)
            else:
                self.finish_group_loop_execution(module, error)
        else:
            if not is_group:
                self.finish_module_execution(module, error)
            else:
                self.finish_group_execution(module, error)

    def start_module_loop_execution(self, module, module_id, module_name,
                                    abstraction_id, abstraction_version,
                                    parent_exec, cached):
        if (not module.first_iteration):
            self.start_loop_execution(module)
        else:
            module_exec = self.create_module_exec(module, module_id,
                                                  module_name,
                                                  abstraction_id,
                                                  abstraction_version,
                                                  cached)
            module.module_exec = module_exec
            if parent_exec:
                if parent_exec.loop_execs:
                    parent_exec.loop_execs[-1].add_module_exec(module_exec)
                else:
                    parent_exec.add_module_exec(module_exec)
            else:
                self.workflow_exec.add_item(module_exec)
            self.start_loop_execution(module)

    def finish_module_loop_execution(self, module, error):
        self.finish_loop_execution(module, error)
        if (module.last_iteration) or (error):
            module.module_exec.ts_end = core.system.current_time()
            if not error:
                module.module_exec.completed = 1
            else:
                if module.module_exec.loop_execs and module.module_exec.\
                   loop_execs[-1].error:
                    error = 'Error in loop execution with id %d.'%\
                            module.module_exec.loop_execs[-1].id
                module.module_exec.completed = -1
                module.module_exec.error = error
            del module.module_exec

    def start_group_loop_execution(self, group, module_id, group_name,
                                   parent_exec, cached):
        if (not group.first_iteration):
            self.start_loop_execution(group)
        else:
            group_exec = self.create_group_exec(group, module_id,
                                                group_name, cached)
            group.group_exec = group_exec
            if parent_exec:
                if parent_exec.loop_execs:
                    parent_exec.loop_execs[-1].add_group_exec(group_exec)
                else:
                    parent_exec.add_group_exec(group_exec)
            else:
                self.workflow_exec.add_item(group_exec)
            self.start_loop_execution(group)

    def finish_group_loop_execution(self, group, error):
        self.finish_loop_execution(group, error)
        if (group.last_iteration) or (error):
            group.group_exec.ts_end = core.system.current_time()
            if not error:
                group.group_exec.completed = 1
            else:
                if group.group_exec.loop_execs and group.group_exec.\
                   loop_execs[-1].error:
                    error = 'Error in loop execution with id %d.'%\
                            group.group_exec.loop_execs[-1].id
                group.group_exec.completed = -1
                group.group_exec.error = error
            del group.group_exec
        
    def start_module_execution(self, module, module_id, module_name,
                               abstraction_id, abstraction_version,
                               parent_exec, cached):
        module_exec = self.create_module_exec(module, module_id,
                                              module_name,
                                              abstraction_id,
                                              abstraction_version,
                                              cached)
        module.module_exec = module_exec
        if parent_exec:
            if parent_exec.loop_execs:
                parent_exec.loop_execs[-1].add_module_exec(module_exec)
            else:
                parent_exec.add_module_exec(module_exec)
        else:
            self.workflow_exec.add_item(module_exec)

    def finish_module_execution(self, module, error):
        module.module_exec.ts_end = core.system.current_time()
        if not error:
            module.module_exec.completed = 1
        else:
            module.module_exec.completed = -1
            module.module_exec.error = error
        del module.module_exec

    def start_group_execution(self, group, module_id, group_name,
                              parent_exec, cached):
        group_exec = self.create_group_exec(group, module_id,
                                            group_name, cached)
        group.group_exec = group_exec
        if parent_exec:
            if parent_exec.loop_execs:
                parent_exec.loop_execs[-1].add_group_exec(group_exec)
            else:
                parent_exec.add_group_exec(group_exec)
        else:
            self.workflow_exec.add_item(group_exec)

    def finish_group_execution(self, group, error):
        group.group_exec.ts_end = core.system.current_time()
        if not error:
            group.group_exec.completed = 1
        else:
            if group.group_exec.module_execs and group.group_exec.\
               module_execs[-1].error:
                error = 'Error in module execution with id %d.'%\
                        group.group_exec.module_execs[-1].id
            if group.group_exec.group_execs and group.group_exec.\
               group_execs[-1].error:
                error = 'Error in group execution with id %d.'%\
                        group.group_exec.group_execs[-1].id
            group.group_exec.completed = -1
            group.group_exec.error = error
        del group.group_exec

    def start_loop_execution(self, module):
        loop_exec = self.create_loop_exec()
        is_group = module.moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_group() or module.\
                   moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_abstraction()
        if is_group:
            module.group_exec.add_loop_exec(loop_exec)
        else:
            module.module_exec.add_loop_exec(loop_exec)

    def finish_loop_execution(self, module, error):
        is_group = module.moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_group() or module.\
                   moduleInfo['pipeline'].modules\
                   [module.moduleInfo['moduleId']].is_abstraction()
        if is_group:
            module.group_exec.loop_execs[-1].ts_end = core.system.\
                                                      current_time()
            if not error:
                module.group_exec.loop_execs[-1].completed = 1
            else:
                if module.group_exec.loop_execs[-1].module_execs and\
                   module.group_exec.loop_execs[-1].module_execs[-1].error:
                    error = 'Error in module execution with id %d.'%\
                            module.group_exec.loop_execs[-1].\
                            module_execs[-1].id
                if module.group_exec.loop_execs[-1].group_execs and\
                   module.group_exec.loop_execs[-1].group_execs[-1].error:
                    error = 'Error in group execution with id %d.'%\
                            module.group_exec.loop_execs[-1].\
                            group_execs[-1].id
                module.group_exec.loop_execs[-1].completed = -1
                module.group_exec.loop_execs[-1].error = error
        else:
            module.module_exec.loop_execs[-1].ts_end = core.system.\
                                                       current_time()
            if not error:
                module.module_exec.loop_execs[-1].completed = 1
            else:
                module.module_exec.loop_execs[-1].completed = -1
                module.module_exec.loop_execs[-1].error = error

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
            
