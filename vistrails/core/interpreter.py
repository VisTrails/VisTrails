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
from core.modules.vistrails_module import ModuleConnector, ModuleError
from core.modules.module_utils import FilePool
from core.utils import withIndex, InstanceObject, lock_method
from core.data_structures import Bidict
import core.vistrail.pipeline
import threading
import copy

################################################################################

_lock = threading.Lock()

class Interpreter(object):
    def __init__(self):
        pass

    typeConversion = {'Float': float,
                      'Integer': int,
                      'String': lambda x: x}

    @lock_method(_lock)
    def locked_execute(self, pipeline, vistrailName, currentVersion,
                       view, logger):
        return self.unlocked_execute(pipeline, vistrailName,
                                     currentVersion, view, logger)
    
    def unlocked_execute(self, pipeline, vistrailName, currentVersion,
                         view, logger):

        def addToExecuted(obj):
            executed[obj.id] = True
        def beginCompute(obj):
            view.setModuleComputing(obj.id)
        def beginUpdate(obj):
            view.setModuleActive(obj.id)
            reg = modules.module_registry.registry
            name = reg.getDescriptor(obj.__class__).name
            if logger:
                logger.startModuleExecution(vistrailName, 
                                            currentVersion, obj.id, name)
        def endUpdate(obj, error=''):
            if not error:
                view.setModuleSuccess(obj.id)
            else:
                view.setModuleError(obj.id, error)
            if logger:
                logger.finishModuleExecution(vistrailName, 
                                             currentVersion, obj.id)
        def annotate(obj, d):
            if logger:
                logger.insertAnnotationDB(vistrailName, 
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
                for f in module.functions:
                    reg = modules.module_registry.registry
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
                conn.makeConnection(src, dst)

            for v in pipeline.graph.sinks():
                try:
                    objects[v].update()
                except ModuleError, me:
                    me.module.logging.endUpdate(me.module, me.msg)
                    errors[me.module.id] = me
        finally:
            self.filePool.cleanup()
            del self.filePool
        
        return (objects, errors, executed)
        
    def execute(self, pipeline, vistrailName, currentVersion, view, 
                logger, useLock=True):
        if useLock:
            method_call = self.locked_execute
        else:
            method_call = self.unlocked_execute

        return method_call(pipeline, vistrailName, currentVersion, view,
                           logger)
        
        
################################################################################

class CachedInterpreter(object):

    def __init__(self):
        self._file_pool = FilePool()
        self._persistent_pipeline = core.vistrail.pipeline.Pipeline()
        self._objects = {}
        self._executed = {}
        self.filePool = self._file_pool

    def clear(self):
        self._file_pool.cleanup()

    def __del__(self):
        self.clear()

    def execute(self, pipeline, vistrailName, currentVersion,
                view, logger):
        """execute(pipeline, vistrailName, currentVersion, view, logger):
Executes a pipeline using caching. Caching works by reusing pipelines directly.
This means that there exists one global pipeline whose parts get executed over
and over again.

This function returns a triple of dictionaries (objs, errs, execs).

objs returns a mapping from local ids (the ids in the pipeline) to
objects **in the persistent pipeline**. Notice, these are not the objects
inside the passed pipeline, but the objects they were mapped to in the
persistent pipeline.

errs returns a dictionary from local ids to error messages of modules
that might have returns errors.

execs returns a dictionary from local ids to boolean values indicating
whether they were executed or not.

If modules have no error associated with but were not executed, it
means they were cached."""
        pipeline.resolveAliases()

        if logger:
            logger.startWorkflowExecution(vistrailName, currentVersion)

        (module_map,
         conn_map,
         module_added_set,
         conn_added_set) = self.add_to_persistent_pipeline(pipeline)

        def addToExecuted(obj):
            i = module_map.inverse[obj.id]
            executed[i] = True
        def beginCompute(obj):
            i = module_map.inverse[obj.id]
            view.setModuleComputing(i)
        def beginUpdate(obj):
            i = module_map.inverse[obj.id]
            view.setModuleActive(i)
            reg = modules.module_registry.registry
            name = reg.getDescriptor(obj.__class__).name
            if logger:
                logger.startModuleExecution(vistrailName, 
                                            currentVersion, i, name)
        def endUpdate(obj, error=''):
            i = module_map.inverse[obj.id]
            if not error:
                view.setModuleSuccess(i)
            else:
                view.setModuleError(i, error)
            if logger:
                logger.finishModuleExecution(vistrailName, 
                                             currentVersion, i)
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
        print "Added modules:",module_added_set
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
            for f in module.functions:
                if len(f.params) == 0:
                    connector = ModuleConnector(createNull(), 'value')
                elif len(f.params) == 1:
                    p = f.params[0]
                    connector = ModuleConnector(createConstant(p), 'value')
                else:
                    reg = modules.module_registry.registry
                    tupleModule = reg.getDescriptorByName('Tuple').module()
                    tupleModule.length = len(f.params)
                    for (i,p) in withIndex(f.params):
                        constant = createConstant(p)
                        connector = ModuleConnector(constant, 'value')
                        tupleModule.setInputPort(i, connector)
                    connector = ModuleConnector(tupleModule, 'value')
                obj.setInputPort(f.name, connector)

        # Create the new connections
        print "Added connections:",conn_added_set
        for i in conn_added_set:
            persistent_id = conn_map[i]
            conn = self._persistent_pipeline.connections[persistent_id]
            src = self._objects[conn.sourceId]
            dst = self._objects[conn.destinationId]
            conn.makeConnection(src, dst)

        # Update new sinks
        for v in persistent_sinks:
            try:
                self._objects[v].update()
            except ModuleError, me:
                me.module.logging.endUpdate(me.module, me.msg)
                errors[me.module.id] = me

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

        print "objs:", objs
        print "errs:", errs
        print "execs:", execs
        
        for i, obj in objs.iteritems():
            if errs.has_key(i):
                view.setModuleError(i, errs[i])
            elif execs.has_key(i):
                view.setModuleSuccess(i)
            else:
                view.setModuleNotExecuted(i)

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
        pipeline.compute_signatures()
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
                print connection.id, new_sig
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
    
##############################################################################
