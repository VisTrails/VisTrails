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

from core import modules
from core.common import *
from core.data_structures.bijectivedict import Bidict
from core.modules.module_utils import FilePool
from core.modules.vistrails_module import ModuleConnector, ModuleError
from core.utils import DummyView
import copy
import core.interpreter.base
import core.interpreter.utils
import core.vistrail.pipeline

################################################################################

class Interpreter(core.interpreter.base.BaseInterpreter):
    def __init__(self):
        core.interpreter.base.BaseInterpreter.__init__(self)

    typeConversion = {'Float': float,
                      'Integer': int,
                      'String': lambda x: x}

    @lock_method(core.interpreter.utils.get_interpreter_lock())
    def locked_execute(self, controller, pipeline, vistrailName,
                       currentVersion, view, aliases=None, **kwargs):
        return self.unlocked_execute(controller, pipeline, vistrailName,
                                     currentVersion, view, aliases, **kwargs)
    
    def unlocked_execute(self, controller, pipeline,
                         vistrailName, currentVersion,
                         view, aliases=None, **kwargs):
        if view == None:
            raise VistrailsInternalError("Must pass a view object")

        self.resolve_aliases(pipeline, aliases)

        self._logger.startWorkflowExecution(vistrailName, currentVersion)

        def add_to_executed(obj):
            executed[obj.id] = True
            if kwargs.has_key('moduleExecutedHook'):
                for callable_ in kwargs['moduleExecutedHook']:
                    callable_(obj.id)
        def begin_compute(obj):
            view.setModuleComputing(obj.id)
        def begin_update(obj):
            view.setModuleActive(obj.id)
            reg = modules.module_registry.registry
            name = reg.getDescriptor(obj.__class__).name
            self._logger.startModuleExecution(vistrailName,
                                              currentVersion, obj.id, name)
        def end_update(obj, error=''):
            if not error:
                view.setModuleSuccess(obj.id)
            else:
                view.setModuleError(obj.id, error)
            self._logger.finishModuleExecution(vistrailName, 
                                               currentVersion, obj.id)
        def annotate(obj, d):
            self._logger.insertAnnotationDB(vistrailName, 
                                            currentVersion, obj.id, d)

        try:
            self.filePool = FilePool()
            objects = {}
            errors = {}
            executed = {}
            logging_obj = InstanceObject(signalSuccess=add_to_executed,
                                         begin_update=begin_update,
                                         begin_compute=begin_compute,
                                         end_update=end_update,
                                         annotate=annotate)
            # create objects
            for id, module in pipeline.modules.items():
                objects[id] = module.summon()
                objects[id].interpreter = self
                objects[id].id = id
                objects[id].logging = logging_obj
                
                # Update object pipeline information
                obj = objects[id]
                obj.moduleInfo['vistrailName'] = vistrailName
                obj.moduleInfo['version'] = currentVersion
                obj.moduleInfo['moduleId'] = id
                obj.moduleInfo['pipeline'] = pipeline
                if kwargs.has_key('reason'):
                    obj.moduleInfo['reason'] = kwargs['reason']
                if kwargs.has_key('actions'):
                    obj.moduleInfo['actions'] = kwargs['actions']
                
                reg = modules.module_registry.registry
                for f in module.functions:
                    if len(f.params)==0:
                        nullObject = reg.getDescriptorByName('Null').module()
                        objects[id].set_input_port(f.name, 
                                                 ModuleConnector(nullObject,
                                                                 'value'))
                    if len(f.params)==1:
                        p = f.params[0]
                        constant = reg.getDescriptorByName(p.type).module()
                        constant.setValue(p.evaluatedStrValue)
                        objects[id].set_input_port(f.name, 
                                                 ModuleConnector(constant, 
                                                                 'value'))
                    if len(f.params)>1:
                        tupleModule = core.interpreter.base.InternalTuple()
                        tupleModule.length = len(f.params)
                        for (i,p) in iter_with_index(f.params):
                            constant = reg.getDescriptorByName(p.type).module()
                            constant.setValue(p.evaluatedStrValue)
                            tupleModule.set_input_port(i, 
                                                     ModuleConnector(constant, 
                                                                     'value'))
                        objects[id].set_input_port(f.name, 
                                                 ModuleConnector(tupleModule,
                                                                 'value'))
            
            # create connections
            for id, conn in pipeline.connections.items():
                src = objects[conn.sourceId]
                dst = objects[conn.destinationId]
                dstModule = pipeline.modules[conn.destinationId]
                conn.makeConnection(src, dst)

            if self.done_summon_hook:
                self.done_summon_hook(pipeline, objects)
            if kwargs.has_key('done_summon_hook'):
                for callable_ in kwargs['done_summon_hook']:
                    callable_(pipeline, objects)

            if kwargs.has_key('sinks'):
                requestedSinks = kwargs['sinks']
                allSinks = [sink
                            for sink in pipeline.graph.sinks()
                            if sink in requestedSinks]
            else:
                allSinks = pipeline.graph.sinks()
            
            for v in allSinks:
                try:
                    objects[v].update()
                    
                except ModuleError, me:
                    me.module.logging.end_update(me.module, me.msg)
                    errors[me.module.id] = me
        
            if self.done_update_hook:
                self.done_update_hook(pipeline, objects)
        

        finally:
            self.filePool.cleanup()
            del self.filePool

        self._logger.finishWorkflowExecution(vistrailName, currentVersion)
        
        return InstanceObject(objects=objects,
                              errors=errors,
                              executed=executed)
        
    def execute(self, controller, pipeline, vistrailName,
                currentVersion=-1, view=DummyView(),
                useLock=True, **kwargs):
        if useLock:
            method_call = self.locked_execute
        else:
            method_call = self.unlocked_execute

        return method_call(controller, pipeline, vistrailName,
                           currentVersion, view, **kwargs)


    @staticmethod
    def get():
        return Interpreter()

    @staticmethod
    def cleanup():
        pass
        
################################################################################
