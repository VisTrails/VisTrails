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

    def clean_modules(self, modules_to_clean):
        """clean_modules(modules_to_clean: list of persistent module ids)

        Removes modules from the persistent pipeline, and the modules that
        depend on them."""
        if modules_to_clean == []:
            return
        g = self._persistent_pipeline.graph
        dependencies = g.vertices_topological_sort(modules_to_clean)
        for v in dependencies:
            self._persistent_pipeline.delete_module(v)
            del self._objects[v]

    def clean_non_cacheable_modules(self):
        """clean_non_cacheable_modules() -> None

        Removes all modules that are not cacheable from the persistent
        pipeline, and the modules that depend on them."""
        non_cacheable_modules = [i for
                                 (i, mod) in self._objects.iteritems()
                                 if not mod.is_cacheable()]
        self.clean_modules(non_cacheable_modules)
        

    def unlocked_execute(self, controller,
                         pipeline, locator, currentVersion,
                         view, aliases=None, **kwargs):
        """unlocked_execute(controller, pipeline, locator,
        currentVersion, view): Executes a pipeline using
        caching. Caching works by reusing pipelines directly.  This
        means that there exists one global pipeline whose parts get
        executed over and over again. This allows nested execution."""
        if view == None:
            raise VistrailsInternalError("This shouldn't have happened")
        self.resolve_aliases(pipeline,aliases)
        (tmp_to_persistent_module_map,
         conn_map,
         module_added_set,
         conn_added_set) = self.add_to_persistent_pipeline(pipeline)


        parameter_changes = []
        def change_parameter(obj, name, value):
            parameter_changes.append((tmp_to_persistent_module_map.inverse[obj.id],
                                      name, value))

        # the executed dict works on persistent ids
        def add_to_executed(obj):
            executed[obj.id] = True
            if kwargs.has_key('moduleExecutedHook'):
                for callable_ in kwargs['moduleExecutedHook']:
                    callable_(obj.id)
        # views work on local ids
        def begin_compute(obj):
            i = tmp_to_persistent_module_map.inverse[obj.id]
            view.set_module_computing(i)
        # views and loggers work on local ids
        def begin_update(obj):
            i = tmp_to_persistent_module_map.inverse[obj.id]
            view.set_module_active(i)
            reg = modules.module_registry.registry
            name = reg.get_descriptor(obj.__class__).name
            self._logger.start_module_execution(locator, 
                                                currentVersion, i, name)
        # views and loggers work on local ids
        def end_update(obj, error=''):
            i = tmp_to_persistent_module_map.inverse[obj.id]
            if not error:
                view.set_module_success(i)
            else:
                view.set_module_error(i, error)
            self._logger.finish_module_execution(locator, 
                                                 currentVersion, i)
        # views and loggers work on local ids
        def annotate(obj, d):
            i = tmp_to_persistent_module_map.inverse[obj.id]
            self._logger.insert_annotation_DB(locator, 
                                            currentVersion, i, d)

        def create_null():
            """Creates a Null value"""
            getter = modules.module_registry.registry.get_descriptor_by_name
            descriptor = getter('edu.utah.sci.vistrails.basic', 'Null')
            return descriptor.module()
        
        def create_constant(param):
            """Creates a Constant from a parameter spec"""
            getter = modules.module_registry.registry.get_descriptor_by_name
            constant = getter('edu.utah.sci.vistrails.basic',
                              param.type).module()
            constant.setValue(p.evaluatedStrValue)
            return constant
                
        ## Checking 'sinks' from kwagrs to resolve only requested sinks
        if kwargs.has_key('sinks'):
            requestedSinks = kwargs['sinks']
            persistent_sinks = [tmp_to_persistent_module_map[sink]
                                for sink in pipeline.graph.sinks()
                                if sink in requestedSinks]
        else:
            persistent_sinks = [tmp_to_persistent_module_map[sink]
                                for sink in pipeline.graph.sinks()]
            
        logging_obj = InstanceObject(signalSuccess=add_to_executed,
                                     begin_update=begin_update,
                                     begin_compute=begin_compute,
                                     end_update=end_update,
                                     annotate=annotate)
        errors = {}
        executed = {}
        
        def make_change_parameter(obj):
            return lambda *args: change_parameter(obj, *args)
    
        # Create the new objects
        for i in module_added_set:
            persistent_id = tmp_to_persistent_module_map[i]
            module = self._persistent_pipeline.modules[persistent_id]
            self._objects[persistent_id] = module.summon()
            obj = self._objects[persistent_id]
            obj.interpreter = self
            obj.id = persistent_id
            obj.logging = logging_obj
            obj.change_parameter = make_change_parameter(obj)
            
            # Update object pipeline information
            obj.moduleInfo['locator'] = locator
            obj.moduleInfo['version'] = currentVersion
            obj.moduleInfo['moduleId'] = i
            obj.moduleInfo['pipeline'] = pipeline
            if kwargs.has_key('reason'):
                obj.moduleInfo['reason'] = kwargs['reason']
            if kwargs.has_key('actions'):
                obj.moduleInfo['actions'] = kwargs['actions']
            
            reg = modules.module_registry.registry
            for f in module.functions:
                if len(f.params) == 0:
                    connector = ModuleConnector(create_null(), 'value')
                elif len(f.params) == 1:
                    p = f.params[0]
                    connector = ModuleConnector(create_constant(p), 'value')
                else:
                    tupleModule = core.interpreter.base.InternalTuple()
                    tupleModule.length = len(f.params)
                    for (i,p) in iter_with_index(f.params):
                        constant = create_constant(p)
                        constant.update()
                        connector = ModuleConnector(constant, 'value')
                        tupleModule.set_input_port(i, connector)
                    connector = ModuleConnector(tupleModule, 'value')
                obj.set_input_port(f.name, connector, is_method=True)

        # Create the new connections
        for i in conn_added_set:
            persistent_id = conn_map[i]
            conn = self._persistent_pipeline.connections[persistent_id]
            src = self._objects[conn.sourceId]
            dst = self._objects[conn.destinationId]
            conn.makeConnection(src, dst)

        if self.done_summon_hook:
            self.done_summon_hook(self._persistent_pipeline, self._objects)
        if kwargs.has_key('done_summon_hook'):
            for callable_ in kwargs['done_summon_hook']:
                callable_(self._persistent_pipeline, self._objects)
                
        # Update new sinks
        for v in persistent_sinks:
            try:
                self._objects[v].update()
            except ModuleError, me:
                me.module.logging.end_update(me.module, me.msg)
                errors[me.module.id] = me

        if self.done_update_hook:
            self.done_update_hook(self._persistent_pipeline, self._objects)
                
        # objs, errs, and execs are mappings that use the local ids as keys,
        # as opposed to the persistent ids.
        # They are thus ideal to external consumption.
        objs = {}
        # dict([(i, self._objects[tmp_to_persistent_module_map[i]])
        #              for i in tmp_to_persistent_module_map.keys()])
        errs = {}
        execs = {}

        to_delete = []
        for (tmp_id, pst_id) in tmp_to_persistent_module_map.iteritems():
            objs[tmp_id] = self._objects[pst_id]
            if errors.has_key(pst_id):
                errs[tmp_id] = errors[pst_id]
                to_delete.append(pst_id)
            if executed.has_key(pst_id):
                execs[tmp_id] = executed[pst_id]
            else:
                execs[tmp_id] = False

        # Clean up modules that failed to execute
        self.clean_modules(to_delete)
        #         print "objs:", objs
        #         print "errs:", errs
        #         print "execs:", execs

        for i, obj in objs.iteritems():
            if errs.has_key(i):
                view.set_module_error(i, errs[i].msg)
            elif execs.has_key(i) and execs[i]:
                view.set_module_success(i)
            else:
                view.set_module_not_executed(i)

        return InstanceObject(objects=objs,
                              errors=errs,
                              executed=execs,
                              modules_added=module_added_set,
                              connections_added=conn_added_set,
                              parameter_changes=parameter_changes)

    @lock_method(core.interpreter.utils.get_interpreter_lock())
    def execute(self, controller, pipeline, vistrailLocator,
                currentVersion=-1, view=DummyView(),
                aliases=None, **kwargs):
        """execute(controller, pipeline, vistrailLocator, currentVersion, view):
        Executes a pipeline using caching. Caching works by reusing
        pipelines directly.  This means that there exists one global
        pipeline whose parts get executed over and over again.

        This function returns a triple of dictionaries (objs, errs, execs).

        objs is a mapping from local ids (the ids in the pipeline) to
        objects **in the persistent pipeline**. Notice, these are not
        the objects inside the passed pipeline, but the objects they
        were mapped to in the persistent pipeline.

        errs is a dictionary from local ids to error messages of modules
        that might have returns errors.

        execs is a dictionary from local ids to boolean values indicating
        whether they were executed or not.

        If modules have no error associated with but were not executed, it
        means they were cached."""
        self._logger.start_workflow_execution(vistrailLocator, currentVersion)

        self.clean_non_cacheable_modules()

        result = self.unlocked_execute(controller, pipeline, vistrailLocator,
                                       currentVersion,
                                       view, aliases,
                                       **kwargs)

        self._logger.finish_workflow_execution(vistrailLocator, currentVersion)

        return result

    def add_to_persistent_pipeline(self, pipeline):
        """add_to_persistent_pipeline(pipeline):
        (module_id_map, connection_id_map, modules_added)
        Adds a pipeline to the persistent pipeline of the cached interpreter.

        Returns four things: two dictionaries describing the mapping
        of ids from the passed pipeline to the persistent one (the
        first one has the module id mapping, the second one has the
        connection id mapping), a set of all module ids added to the
        persistent pipeline, and a set of all connection ids added to
        the persistent pipeline."""
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
                self._persistent_pipeline.add_module(persistent_module)
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
                persistent_connection = copy.copy(connection)
                persistent_id = self._persistent_pipeline.fresh_connection_id()
                persistent_connection.id = persistent_id
                persistent_connection.sourceId = module_id_map[
                    connection.sourceId]
                persistent_connection.destinationId = module_id_map[
                    connection.destinationId]
                self._persistent_pipeline.add_connection(persistent_connection)
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


    @staticmethod
    def flush():
        if CachedInterpreter.__instance:
            CachedInterpreter.__instance.clear()
            CachedInterpreter.__instance.create()
        objs = gc.collect()

##############################################################################
# Testing

import unittest
import core.packagemanager

class TestCachedInterpreter(unittest.TestCase):

    def test_cache(self):
        from core.db.locator import XMLFileLocator
        """Test if basic caching is working."""
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                            '/tests/resources/dummy.xml').load()
        p1 = v.getPipeline('int chain')
        n = v.get_version_number('int chain')
        view = DummyView()
        interpreter = core.interpreter.cached.CachedInterpreter.get()
        result = interpreter.execute(None, p1,
                                     'dummy.xml',
                                     n,
                                     view)
        # to force fresh params
        p2 = v.getPipeline('int chain')
        result = interpreter.execute(None, p2,
                                     'dummy.xml',
                                     n,
                                     view)
        assert len(result.modules_added) == 1


if __name__ == '__main__':
    unittest.main()
