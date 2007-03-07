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
import gc

##############################################################################

class CachedInterpreter(core.interpreter.base.BaseInterpreter):

    def __init__(self):
        core.interpreter.base.BaseInterpreter.__init__(self)
        self.create()

    def create(self):
        self._file_pool = FilePool()
        self._persistent_pipeline = core.vistrail.pipeline.Pipeline()
        self._objects = {}
        self._executed = {}
        self.filePool = self._file_pool
        
    def clear(self):
        self._file_pool.cleanup()
        self._persistent_pipeline.clear()
        for obj in self._objects.itervalues():
            obj.clear()
        self._objects = {}
        self._executed = {}

    def __del__(self):
        self.clear()

    def clean_non_cacheable_modules(self):
        """clean_non_cacheable_modules() -> None

Removes all modules that are not cacheable from the persistent pipeline,
and the modules that depend on them."""
        non_cacheable_modules = [i for
                                 (i, mod) in self._objects.iteritems()
                                 if not mod.is_cacheable()]
        if non_cacheable_modules == []:
            return
        g = self._persistent_pipeline.graph
        dependencies = g.vertices_topological_sort(non_cacheable_modules)
        for v in dependencies:
            self._persistent_pipeline.deleteModule(v)
            del self._objects[v]

    def unlocked_execute(self, pipeline, vistrailName, currentVersion,
                view, logger, aliases=None, **kwargs):
        """unlocked_execute(pipeline, vistrailName, currentVersion, view, logger):
Executes a pipeline using caching. Caching works by reusing pipelines directly.
This means that there exists one global pipeline whose parts get executed over
and over again. This allows nested execution."""

        (module_map,
         conn_map,
         module_added_set,
         conn_added_set) = self.add_to_persistent_pipeline(pipeline)

        self.resolveAliases(self._persistent_pipeline,aliases)

        # the executed dict works on persistent ids
        def addToExecuted(obj):
            executed[obj.id] = True
            if kwargs.has_key('moduleExecutedHook'):
                for callable_ in kwargs['moduleExecutedHook']:
                    callable_(obj.id)
        # views work on local ids
        def beginCompute(obj):
            i = module_map.inverse[obj.id]
            if view:
                view.setModuleComputing(i)
        # views and loggers work on local ids
        def beginUpdate(obj):
            i = module_map.inverse[obj.id]
            if view:
                view.setModuleActive(i)
            reg = modules.module_registry.registry
            name = reg.getDescriptor(obj.__class__).name
            if logger:
                logger.startModuleExecution(vistrailName, 
                                            currentVersion, i, name)
        # views and loggers work on local ids
        def endUpdate(obj, error=''):
            i = module_map.inverse[obj.id]
            if view:
                if not error:
                    view.setModuleSuccess(i)
                else:
                    view.setModuleError(i, error)
            if logger:
                logger.finishModuleExecution(vistrailName, 
                                             currentVersion, i)
        # views and loggers work on local ids
        def annotate(obj, d):
            i = module_map.inverse[obj.id]
            if logger:
                logger.insertAnnotationDB(vistrailName, 
                                          currentVersion, i, d)

        def createNull():
            """Creates a Null value"""
            reg = modules.module_registry.registry
            return reg.getDescriptorByName('Null').module()
        
        def createConstant(param):
            """Creates a Constant from a parameter spec"""
            reg = modules.module_registry.registry
            constant = reg.getDescriptorByName(param.type).module()
            constant.setValue(p.evaluatedStrValue)
            return constant
                
        persistent_sinks = [module_map[sink]
                            for sink
                            in pipeline.graph.sinks()]
        logging_obj = InstanceObject(signalSuccess=addToExecuted,
                                     beginUpdate=beginUpdate,
                                     beginCompute=beginCompute,
                                     endUpdate=endUpdate,
                                     annotate=annotate)
        errors = {}
        executed = {}
        # Create the new objects
        for i in module_added_set:
            persistent_id = module_map[i]
            module = self._persistent_pipeline.modules[persistent_id]
            self._objects[persistent_id] = module.summon()
            obj = self._objects[persistent_id]
            obj.interpreter = self
            obj.id = persistent_id
            if view:
                obj.logging = logging_obj
            obj.vistrailName = vistrailName
            obj.currentVersion = currentVersion
            reg = modules.module_registry.registry
            for f in module.functions:
                if len(f.params) == 0:
                    connector = ModuleConnector(createNull(), 'value')
                elif len(f.params) == 1:
                    p = f.params[0]
                    connector = ModuleConnector(createConstant(p), 'value')
                else:
                    tupleModule = core.interpreter.base.InternalTuple()
                    tupleModule.length = len(f.params)
                    for (i,p) in withIndex(f.params):
                        constant = createConstant(p)
                        constant.update()
                        connector = ModuleConnector(constant, 'value')
                        tupleModule.setInputPort(i, connector)
                    connector = ModuleConnector(tupleModule, 'value')
                obj.setInputPort(f.name, connector)

        # Create the new connections
        for i in conn_added_set:
            persistent_id = conn_map[i]
            conn = self._persistent_pipeline.connections[persistent_id]
            src = self._objects[conn.sourceId]
            dst = self._objects[conn.destinationId]
            conn.makeConnection(src, dst)

        if self.doneSummonHook:
            self.doneSummonHook(self._persistent_pipeline, self._objects)
        if kwargs.has_key('doneSummonHook'):
            for callable_ in kwargs['doneSummonHook']:
                callable_(self._persistent_pipeline, self._objects)
                
        # Update new sinks
        for v in persistent_sinks:
            try:
                self._objects[v].update()
            except ModuleError, me:
                me.module.logging.endUpdate(me.module, me.msg)
                errors[me.module.id] = me

        if self.doneUpdateHook:
            self.doneUpdateHook(self._persistent_pipeline, self._objects)
                
        # objs, errs, and execs are mappings that use the local ids as keys,
        # as opposed to the persistent ids.
        # They are thus ideal to external consumption.
        objs = {}
        # dict([(i, self._objects[module_map[i]])
        #              for i in module_map.keys()])
        errs = {}
        execs = {}
        for (i, v) in module_map.iteritems():
            objs[i] = self._objects[v]
            if errors.has_key(v):
                errs[i] = errors[v]
            if executed.has_key(v):
                execs[i] = executed[v]
            else:
                execs[i] = False

#         print "objs:", objs
#         print "errs:", errs
#         print "execs:", execs

        if view:
            for i, obj in objs.iteritems():
                if errs.has_key(i):
                    view.setModuleError(i, errs[i].msg)
                elif execs.has_key(i):
                    view.setModuleSuccess(i)
                else:
                    view.setModuleNotExecuted(i)
                    
        return (objs, errs, execs)
        

    @lock_method(core.interpreter.utils.get_interpreter_lock())
    def execute(self, pipeline, vistrailName, currentVersion,
                view, logger,aliases=None, **kwargs):
        """execute(pipeline, vistrailName, currentVersion, view, logger):
Executes a pipeline using caching. Caching works by reusing pipelines directly.
This means that there exists one global pipeline whose parts get executed over
and over again.

This function returns a triple of dictionaries (objs, errs, execs).

objs is a mapping from local ids (the ids in the pipeline) to
objects **in the persistent pipeline**. Notice, these are not the objects
inside the passed pipeline, but the objects they were mapped to in the
persistent pipeline.

errs is a dictionary from local ids to error messages of modules
that might have returns errors.

execs is a dictionary from local ids to boolean values indicating
whether they were executed or not.

If modules have no error associated with but were not executed, it
means they were cached."""
        if logger:
            logger.startWorkflowExecution(vistrailName, currentVersion)

        self.clean_non_cacheable_modules()

        
        (objs, errs, execs) = self.unlocked_execute(pipeline, vistrailName,
                                                    currentVersion,
                                                    view, logger,aliases,
                                                    **kwargs)

        if logger:
            logger.finishWorkflowExecution(vistrailName, currentVersion)

        return (objs, errs, execs)

    def add_to_persistent_pipeline(self, pipeline):
        """add_to_persistent_pipeline(pipeline):
        (module_id_map, connection_id_map, modules_added)
Adds a pipeline to the persistent pipeline of the cached interpreter.

Returns four things: two dictionaries describing the mapping of ids
from the passed pipeline to the persistent one (the first one has the
module id mapping, the second one has the connection id mapping), a
set of all module ids added to the persistent pipeline, and a set of
all connection ids added to the persistent pipeline."""
        module_id_map = Bidict()
        connection_id_map = Bidict()
        modules_added = set()
        connections_added = set()
        pipeline.refresh_signatures()
        # we must traverse vertices in topological sort order
        verts = pipeline.graph.vertices_topological_sort()
        for new_module_id in verts:
            new_sig = pipeline.subpipeline_signature(new_module_id)
            if not self._persistent_pipeline.has_subpipeline_signature(new_sig):
                # Must add module to persistent pipeline
                persistent_module = copy.copy(pipeline.modules[new_module_id])
                persistent_id = self._persistent_pipeline.fresh_module_id()
                persistent_module.id = persistent_id
                self._persistent_pipeline.addModule(persistent_module)
                module_id_map[new_module_id] = persistent_id
                modules_added.add(new_module_id)
            else:
                i = self._persistent_pipeline \
                        .subpipeline_id_from_signature(new_sig)
                module_id_map[new_module_id] = i
        for connection in pipeline.connections.itervalues():
            new_sig = pipeline.connection_signature(connection.id)
            if not self._persistent_pipeline.has_connection_signature(new_sig):
                # Must add connection to persistent pipeline
#                 print connection.id, new_sig
                persistent_connection = copy.copy(connection)
                persistent_id = self._persistent_pipeline.fresh_connection_id()
                persistent_connection.id = persistent_id
                persistent_connection.sourceId = module_id_map[
                    connection.sourceId]
                persistent_connection.destinationId = module_id_map[
                    connection.destinationId]
                self._persistent_pipeline.addConnection(persistent_connection)
                connection_id_map[connection.id] = persistent_id
                connections_added.add(connection.id)
            else:
                i = self._persistent_pipeline \
                        .connection_id_from_signature(new_sig)
                connection_id_map[connection.id] = i
        # update persistent signatures
        self._persistent_pipeline.compute_signatures()
        return (module_id_map, connection_id_map,
                modules_added, connections_added)

    __instance = None
    @staticmethod
    def get():
        if not CachedInterpreter.__instance:
            CachedInterpreter.__instance = CachedInterpreter()
        return CachedInterpreter.__instance

    @staticmethod
    def cleanup():
        if CachedInterpreter.__instance:
            CachedInterpreter.__instance.clear()
        objs = gc.collect()
        print "Number of objects collected:", objs


    @staticmethod
    def flush():
        if CachedInterpreter.__instance:
            CachedInterpreter.__instance.clear()
            CachedInterpreter.__instance.create()
        objs = gc.collect()

##############################################################################
