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
from core.data_structures.bijectivedict import Bidict
from core.modules.module_utils import FilePool
from core.modules.vistrails_module import ModuleConnector, ModuleError
from core.utils import withIndex, InstanceObject, lock_method
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
    def locked_execute(self, pipeline, vistrailName, currentVersion,
                       view, aliases=None, **kwargs):
        return self.unlocked_execute(pipeline, vistrailName,
                                     currentVersion, view, aliases, **kwargs)
    
    def unlocked_execute(self, pipeline, vistrailName, currentVersion,
                         view, aliases=None, **kwargs):

        self.resolveAliases(pipeline, aliases)

        if self._logger:
            self._logger.startWorkflowExecution(vistrailName, currentVersion)

        def addToExecuted(obj):
            executed[obj.id] = True
            if kwargs.has_key('moduleExecutedHook'):
                for callable_ in kwargs['moduleExecutedHook']:
                    callable_(obj.id)
        def beginCompute(obj):
            if view:
                view.setModuleComputing(obj.id)
        def beginUpdate(obj):
            if view:
                view.setModuleActive(obj.id)
            if self._logger:
                reg = modules.module_registry.registry
                name = reg.getDescriptor(obj.__class__).name
                self._logger.startModuleExecution(vistrailName,
                                            currentVersion, obj.id, name)
        def endUpdate(obj, error=''):
            if view:
                if not error:
                    view.setModuleSuccess(obj.id)
                else:
                    view.setModuleError(obj.id, error)
            if self._logger:
                self._logger.finishModuleExecution(vistrailName, 
                                             currentVersion, obj.id)
        def annotate(obj, d):
            if self._logger:
                self._logger.insertAnnotationDB(vistrailName, 
                                          currentVersion, obj.id, d)

        try:
            self.filePool = FilePool()
            objects = {}
            errors = {}
            executed = {}
            logging_obj = InstanceObject(signalSuccess=addToExecuted,
                                         beginUpdate=beginUpdate,
                                         beginCompute=beginCompute,
                                         endUpdate=endUpdate,
                                         annotate=annotate)
            # create objects
            for id, module in pipeline.modules.items():
                objects[id] = module.summon()
                objects[id].interpreter = self
                objects[id].id = id
                if view:
                    objects[id].logging = logging_obj
                objects[id].vistrailName = vistrailName
                objects[id].currentVersion = currentVersion
                reg = modules.module_registry.registry
                for f in module.functions:
                    if len(f.params)==0:
                        nullObject = reg.getDescriptorByName('Null').module()
                        objects[id].setInputPort(f.name, 
                                                 ModuleConnector(nullObject,
                                                                 'value'))
                    if len(f.params)==1:
                        p = f.params[0]
                        constant = reg.getDescriptorByName(p.type).module()
                        constant.setValue(p.evaluatedStrValue)
                        objects[id].setInputPort(f.name, 
                                                 ModuleConnector(constant, 
                                                                 'value'))
                    if len(f.params)>1:
                        tupleModule = reg.getDescriptorByName('Tuple').module()
                        tupleModule.length = len(f.params)
                        for (i,p) in withIndex(f.params):
                            constant = reg.getDescriptorByName(p.type).module()
                            constant.setValue(p.evaluatedStrValue)
                            tupleModule.setInputPort(i, 
                                                     ModuleConnector(constant, 
                                                                     'value'))
                        objects[id].setInputPort(f.name, 
                                                 ModuleConnector(tupleModule,
                                                                 'value'))
            
            # create connections
            for id, conn in pipeline.connections.items():
                src = objects[conn.sourceId]
                dst = objects[conn.destinationId]
                dstModule = pipeline.modules[conn.destinationId]
                conn.makeConnection(src, dst)

            if self.doneSummonHook:
                self.doneSummonHook(pipeline, objects)
            if kwargs.has_key('doneSummonHook'):
                for callable_ in kwargs['doneSummonHook']:
                    callable_(pipeline, objects)

            for v in pipeline.graph.sinks():
                try:
                    objects[v].update()
                except ModuleError, me:
                    me.module.logging.endUpdate(me.module, me.msg)
                    errors[me.module.id] = me
                    
            if self.doneUpdateHook:
                self.doneUpdateHook(pipeline, objects)
                
        finally:
            self.filePool.cleanup()
            del self.filePool

        if self._logger:
            self._logger.finishWorkflowExecution(vistrailName, currentVersion)
        
        return (objects, errors, executed)
        
    def execute(self, pipeline, vistrailName, currentVersion, view,
                useLock=True, **kwargs):
        if useLock:
            method_call = self.locked_execute
        else:
            method_call = self.unlocked_execute

        return method_call(pipeline, vistrailName, currentVersion,
                           view, **kwargs)


    @staticmethod
    def get():
        return Interpreter()

    @staticmethod
    def cleanup():
        pass
        
################################################################################
