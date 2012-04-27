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

import base64
from core import modules
from core.common import *
from core.data_structures.bijectivedict import Bidict
import core.db.io
from core.log.controller import DummyLogController
# from core.modules.module_utils import FilePool
from core.modules.vistrails_module import ModuleConnector, ModuleError, \
    ModuleBreakpoint, ModuleErrors
from core.utils import DummyView
from core.vistrail.annotation import Annotation
from core.vistrail.vistrail import Vistrail
import copy
import core.interpreter.base
import core.interpreter.utils
import core.system
import core.vistrail.pipeline
import gc
import cPickle

##############################################################################

class CachedInterpreter(core.interpreter.base.BaseInterpreter):

    def __init__(self):
        core.interpreter.base.BaseInterpreter.__init__(self)
        self.debugger = None
        self.create()

    def create(self):
        # FIXME moved here because otherwise we hit the registry too early
        from core.modules.module_utils import FilePool
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
        pipeline, and the modules that depend on them, and 
        previously suspended modules """
        non_cacheable_modules = [i for
                                 (i, mod) in self._objects.iteritems()
                                 if not mod.is_cacheable() or \
                                 mod.suspended]
        self.clean_modules(non_cacheable_modules)
        

    def setup_pipeline(self, pipeline, **kwargs):
        """setup_pipeline(controller, pipeline, locator, currentVersion,
                          view, aliases, **kwargs)
        Matches a pipeline with the persistent pipeline and creates
        instances of modules that aren't in the cache.
        """
        def fetch(name, default):
            r = kwargs.get(name, default)
            try:
                del kwargs[name]
            except KeyError:
                pass
            return r
        controller = fetch('controller', None)
        locator = fetch('locator', None)
        current_version = fetch('current_version', None)
        view = fetch('view', DummyView())
        aliases = fetch('aliases', None)
        params = fetch('params', None)
        extra_info = fetch('extra_info', None)
        logger = fetch('logger', DummyLogController())
        sinks = fetch('sinks', None)
        reason = fetch('reason', None)
        actions = fetch('actions', None)
        done_summon_hooks = fetch('done_summon_hooks', [])
        module_executed_hook = fetch('module_executed_hook', [])

        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed '
                                         'to setup_pipeline: %s' % kwargs)

        def create_null():
            """Creates a Null value"""
            getter = modules.module_registry.registry.get_descriptor_by_name
            descriptor = getter('edu.utah.sci.vistrails.basic', 'Null')
            return descriptor.module()
        
        def create_constant(param, module):
            """Creates a Constant from a parameter spec"""
            reg = modules.module_registry.get_module_registry()
            getter = reg.get_descriptor_by_name
            desc = getter(param.identifier, param.type, param.namespace)
            constant = desc.module()
            constant.id = module.id
#             if param.evaluatedStrValue:
#                 constant.setValue(param.evaluatedStrValue)
            if param.strValue != '':
                constant.setValue(param.strValue)
            else:
                constant.setValue( \
                    constant.translate_to_string(constant.default_value))
            return constant

        ### BEGIN METHOD ###

#         if self.debugger:
#             self.debugger.update()
        to_delete = []
        errors = {}

        if controller is not None:
            # Controller is none for sub_modules
            controller.validate(pipeline)
        else:
            pipeline.validate()

        self.resolve_aliases(pipeline, aliases)
        if controller is not None:
            # Controller is none for sub_modules, so we can't resolve variables
            self.resolve_variables(controller, pipeline)

        self.update_params(pipeline, params)
        
        (tmp_to_persistent_module_map,
         conn_map,
         module_added_set,
         conn_added_set) = self.add_to_persistent_pipeline(pipeline)

        # Create the new objects
        for i in module_added_set:
            persistent_id = tmp_to_persistent_module_map[i]
            module = self._persistent_pipeline.modules[persistent_id]
            self._objects[persistent_id] = module.summon()
            obj = self._objects[persistent_id]
            obj.interpreter = self
            obj.id = persistent_id
            obj.is_breakpoint = module.is_breakpoint
            obj.signature = module._signature
                
            reg = modules.module_registry.get_module_registry()
            for f in module.functions:
                connector = None
                if len(f.params) == 0:
                    connector = ModuleConnector(create_null(), 'value')
                elif len(f.params) == 1:
                    p = f.params[0]
                    try:
                        constant = create_constant(p, module)
                        connector = ModuleConnector(constant, 'value')
                    except ValueError, e:
                        err = ModuleError(self, 'Cannot convert parameter '
                                          'value "%s"\n' % p.strValue + str(e))
                        errors[i] = err
                        to_delete.append(obj.id)
                    except Exception, e:
                        err = ModuleError(self, 'Uncaught exception: "%s"' % \
                                              p.strValue + str(e))
                        errors[i] = err
                        to_delete.append(obj.id)
                else:
                    tupleModule = core.interpreter.base.InternalTuple()
                    tupleModule.length = len(f.params)
                    for (j,p) in enumerate(f.params):
                        try:
                            constant = create_constant(p, module)
                            constant.update()
                            connector = ModuleConnector(constant, 'value')
                            tupleModule.set_input_port(j, connector)
                        except ValueError, e:
                            err = ModuleError(self, "Cannot convert parameter "
                                              "value '%s'\n" % p.strValue + \
                                                  str(e))
                            errors[i] = err
                            to_delete.append(obj.id)
                        except Exception, e:
                            err = ModuleError(self, 'Uncaught exception: '
                                              '"%s"' % p.strValue + str(e))
                            errors[i] = err
                            to_delete.append(obj.id)
                    connector = ModuleConnector(tupleModule, 'value')
                if connector:
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
        for callable_ in done_summon_hooks:
            callable_(self._persistent_pipeline, self._objects)

        tmp_id_to_module_map = {}
        for i, j in tmp_to_persistent_module_map.iteritems():
            tmp_id_to_module_map[i] = self._objects[j]
        return (tmp_id_to_module_map, tmp_to_persistent_module_map.inverse,
                module_added_set, conn_added_set, to_delete, errors)

    def execute_pipeline(self, pipeline, tmp_id_to_module_map, 
                         persistent_to_tmp_id_map, **kwargs):
        def fetch(name, default):
            r = kwargs.get(name, default)
            try:
                del kwargs[name]
            except KeyError:
                pass
            return r
        controller = fetch('controller', None)
        locator = fetch('locator', None)
        current_version = fetch('current_version', None)
        view = fetch('view', DummyView())
        aliases = fetch('aliases', None)
        params = fetch('params', None)
        extra_info = fetch('extra_info', None)
        logger = fetch('logger', DummyLogController())
        sinks = fetch('sinks', None)
        reason = fetch('reason', None)
        actions = fetch('actions', None)
        module_executed_hook = fetch('module_executed_hook', [])
        module_suspended_hook = fetch('module_suspended_hook', [])
        done_summon_hooks = fetch('done_summon_hooks', [])
        clean_pipeline = fetch('clean_pipeline', False)
        # parent_exec = fetch('parent_exec', None)

        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed '
                                         'to execute_pipeline: %s' % kwargs)

        errors = {}
        executed = {}
        suspended = {}
        cached = {}

        # LOGGING SETUP
        def get_remapped_id(id):
            return persistent_to_tmp_id_map[id]

        # the executed dict works on persistent ids
        def add_to_executed(obj):
            executed[obj.id] = True
            for callable_ in module_executed_hook:
                callable_(obj.id)

        # the suspended dict works on persistent ids
        def add_to_suspended(obj):
            suspended[obj.id] = obj.suspended
            for callable_ in module_suspended_hook:
                callable_(obj.id)

        # views work on local ids
        def begin_compute(obj):
            i = get_remapped_id(obj.id)
            view.set_module_computing(i)

            reg = modules.module_registry.get_module_registry()
            module_name = reg.get_descriptor(obj.__class__).name

            # !!!self.parent_execs is mutated!!!
            logger.start_execution(obj, i, module_name,
                                   parent_execs=self.parent_execs)

        # views and loggers work on local ids
        def begin_update(obj):
            i = get_remapped_id(obj.id)
            view.set_module_active(i)

        def update_cached(obj):
            cached[obj.id] = True
            i = get_remapped_id(obj.id)

            reg = modules.module_registry.get_module_registry()
            module_name = reg.get_descriptor(obj.__class__).name

            # !!!self.parent_execs is mutated!!!
            logger.start_execution(obj, i, module_name,
                                   parent_execs=self.parent_execs,
                                   cached=1)
            num_pops = logger.finish_execution(obj,'', self.parent_execs)

        # views and loggers work on local ids
        def end_update(obj, error='', errorTrace=None, was_suspended = False):
            i = get_remapped_id(obj.id)
            if was_suspended:
                view.set_module_suspended(i, error)
            elif not error:
                view.set_module_success(i)
            else:
                view.set_module_error(i, error)

            # !!!self.parent_execs is mutated!!!
            logger.finish_execution(obj, error, self.parent_execs, errorTrace,
                                    was_suspended)

        # views and loggers work on local ids
        def annotate(obj, d):
            i = get_remapped_id(obj.id)
            logger.insert_module_annotations(obj, d)

        # views and loggers work on local ids
        def update_progress(obj, percentage=0.0):
            i = get_remapped_id(obj.id)
            view.set_module_progress(i, percentage)
            
        logging_obj = InstanceObject(signalSuccess=add_to_executed,
                                     signalSuspended=add_to_suspended,
                                     begin_update=begin_update,
                                     begin_compute=begin_compute,
                                     update_progress=update_progress,
                                     end_update=end_update,
                                     update_cached=update_cached,
                                     annotate=annotate,
                                     log=logger)

        # PARAMETER CHANGES SETUP
        parameter_changes = []
        def change_parameter(obj, name, value):
            parameter_changes.append((get_remapped_id(obj.id),
                                      name, value))
        def make_change_parameter(obj):
            return lambda *args: change_parameter(obj, *args)

        # Update **all** modules in the current pipeline
        for i, obj in tmp_id_to_module_map.iteritems():
            obj.logging = logging_obj
            obj.change_parameter = make_change_parameter(obj)
            
            # Update object pipeline information
            obj.moduleInfo['locator'] = locator
            obj.moduleInfo['version'] = current_version
            obj.moduleInfo['moduleId'] = i
            obj.moduleInfo['pipeline'] = pipeline
            if extra_info is not None:
                obj.moduleInfo['extra_info'] = extra_info
            if reason is not None:
                obj.moduleInfo['reason'] = reason
            if actions is not None:
                obj.moduleInfo['actions'] = actions

        ## Checking 'sinks' from kwargs to resolve only requested sinks
        if sinks is not None:
            requestedSinks = sinks
            persistent_sinks = [tmp_id_to_module_map[sink]
                                for sink in pipeline.graph.sinks()
                                if sink in requestedSinks]
        else:
            persistent_sinks = [tmp_id_to_module_map[sink]
                                for sink in pipeline.graph.sinks()]
                                        
        # Update new sinks
        for obj in persistent_sinks:
            try:
                obj.update()
            except ModuleErrors, mes:
                for me in mes.module_errors:
                    me.module.logging.end_update(me.module, me.msg)
                    errors[me.module.id] = me
                break
            except ModuleError, me:
                me.module.logging.end_update(me.module, me.msg, me.errorTrace)
                errors[me.module.id] = me
                break
            except ModuleBreakpoint, mb:
                mb.module.logging.end_update(mb.module)
                errors[mb.module.id] = mb
                break

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
        suspends = {}
        caches = {}

        to_delete = []
        for (tmp_id, obj) in tmp_id_to_module_map.iteritems():
            if clean_pipeline:
                to_delete.append(obj.id)
            objs[tmp_id] = obj
            if obj.id in errors:
                errs[tmp_id] = errors[obj.id]
                if not clean_pipeline:
                    to_delete.append(obj.id)
            if obj.id in executed:
                execs[tmp_id] = executed[obj.id]
            elif obj.id in suspended:
                suspends[tmp_id] = suspended[obj.id]
            elif obj.id in cached:
                caches[tmp_id] = cached[obj.id]
            else:
                # these modules didn't execute
                execs[tmp_id] = False

        return (to_delete, objs, errs, execs, suspends, caches, parameter_changes)

    def finalize_pipeline(self, pipeline, to_delete, objs, errs, execs,
                          suspended, cached, **kwargs):
        def fetch(name, default):
            r = kwargs.get(name, default)
            try:
                del kwargs[name]
            except KeyError:
                pass
            return r
        view = fetch('view', DummyView())
        reset_computed = fetch('reset_computed', True)
     
        self.clean_modules(to_delete)

        for i in objs:
            if i in errs:
                view.set_module_error(i, errs[i].msg, errs[i].errorTrace)
            elif i in suspended and suspended[i]:
                view.set_module_suspended(i, suspended[i])
            elif i in execs and execs[i]:
                view.set_module_success(i)
            elif i in cached and cached[i]:
                view.set_module_not_executed(i)
            else:
                view.set_module_persistent(i)

        if reset_computed:
            for module in self._objects.itervalues():
                module.computed = False

    def unlocked_execute(self, pipeline, **kwargs):
        """unlocked_execute(pipeline, **kwargs): Executes a pipeline using
        caching. Caching works by reusing pipelines directly.  This
        means that there exists one global pipeline whose parts get
        executed over and over again. This allows nested execution."""

        res = self.setup_pipeline(pipeline, **kwargs)
        modules_added = res[2]
        conns_added = res[3]
        to_delete = res[4]
        errors = res[5]
        if len(errors) == 0:
            res = self.execute_pipeline(pipeline, *(res[:2]), **kwargs)
        else:
            res = (to_delete, res[0], errors, {}, {}, {}, [])
        self.finalize_pipeline(pipeline, *(res[:-1]), **kwargs)
        
        return InstanceObject(objects=res[1],
                              errors=res[2],
                              executed=res[3],
                              suspended=res[4],
                              parameter_changes=res[6],
                              modules_added=modules_added,
                              conns_added=conns_added)

    @lock_method(core.interpreter.utils.get_interpreter_lock())
    def execute(self, pipeline, **kwargs):
        """execute(pipeline, **kwargs):

        kwargs:
          controller = fetch('controller', None)
          locator = fetch('locator', None)
          current_version = fetch('current_version', None)
          view = fetch('view', DummyView())
          aliases = fetch('aliases', None)
          params = fetch('params', None)
          extra_info = fetch('extra_info', None)
          logger = fetch('logger', DummyLogController())
          reason = fetch('reason', None)
          actions = fetch('actions', None)
          done_summon_hooks = fetch('done_summon_hooks', [])
          module_executed_hook = fetch('module_executed_hook', [])

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

        # Setup named arguments. We don't use named parameters so
        # that positional parameter calls fail earlier
        new_kwargs = {}
        def fetch(name, default):
            r = kwargs.get(name, default)
            new_kwargs[name] = r
            try:
                del kwargs[name]
            except KeyError:
                pass
            return r
        controller = fetch('controller', None)
        locator = fetch('locator', None)
        current_version = fetch('current_version', None)
        view = fetch('view', DummyView())
        aliases = fetch('aliases', None)
        params = fetch('params', None)
        extra_info = fetch('extra_info', None)
        logger = fetch('logger', DummyLogController())
        sinks = fetch('sinks', None)
        reason = fetch('reason', None)
        actions = fetch('actions', None)
        done_summon_hooks = fetch('done_summon_hooks', [])
        module_executed_hook = fetch('module_executed_hook', [])

        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed '
                                         'to execute: %s' % kwargs)

        self.clean_non_cacheable_modules()

#         if controller is not None:
#             vistrail = controller.vistrail
#             (pipeline, module_remap) = \
#                 core.db.io.expand_workflow(vistrail, pipeline)
#             new_kwargs['module_remap'] = module_remap
#         else:
#             vistrail = None

        if controller is not None:
            vistrail = controller.vistrail
        else:
            vistrail = None

        self.parent_execs = [None]
        logger.start_workflow_execution(vistrail, pipeline, current_version)
        self.annotate_workflow_execution(logger, reason, aliases, params)
        result = self.unlocked_execute(pipeline, **new_kwargs)
        logger.finish_workflow_execution(result.errors, suspended=result.suspended)
        self.parent_execs = [None]

        return result

    def annotate_workflow_execution(self, logger, reason, aliases, params):
        """annotate_workflow_Execution(logger: LogController, reason:str,
                                        aliases:dict, params:list)-> None
        It will annotate the workflow execution in logger with the reason,
        aliases and params.
        
        """
        d = {}
        d["__reason__"] = reason
        if aliases is not None and type(aliases) == dict:
            d["__aliases__"] = cPickle.dumps(aliases)
        if params is not None and type(params) == list:
            d["__params__"] = cPickle.dumps(params)
        logger.insert_workflow_exec_annotations(d)
        
    def add_to_persistent_pipeline(self, pipeline):
        """add_to_persistent_pipeline(pipeline):
        (module_id_map, connection_id_map, modules_added)
        Adds a pipeline to the persistent pipeline of the cached interpreter
        and adds current logging object to each existing module.

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
                self._persistent_pipeline.modules[persistent_id]._signature = \
                    base64.b16encode(new_sig).lower()
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
        
    def find_persistent_entities(self, pipeline):
        """returns a map from a pipeline to the persistent pipeline, 
        assuming those pieces exist"""
        persistent_p = self._persistent_pipeline
        object_map = {}
        module_id_map = {}
        connection_id_map = {}
        pipeline.refresh_signatures()
        # we must traverse vertices in topological sort order
        verts = pipeline.graph.vertices_topological_sort()
        for module_id in verts:
            sig = pipeline.subpipeline_signature(module_id)
            if persistent_p.has_subpipeline_signature(sig):
                i = persistent_p.subpipeline_id_from_signature(sig)
                module_id_map[module_id] = i
                object_map[module_id] = self._objects[i]
            else:
                module_id_map[module_id] = None
                object_map[module_id] = None
        for connection in pipeline.connections.itervalues():
            sig = pipeline.connection_signature(connection.id)
            if persistent_p.has_connection_signature(sig):
                connection_id_map[connection.id] = \
                    persistent_p.connection_id_from_signature(sig)
            else:
                connection_id_map[connection.id] = None
        return (object_map, module_id_map, connection_id_map)

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
        from core.vistrail.controller import VistrailController
        from core.db.io import load_vistrail
        
        """Test if basic caching is working."""
        locator = XMLFileLocator(core.system.vistrails_root_directory() +
                            '/tests/resources/dummy.xml')
        (v, abstractions, thumbnails, mashups) = load_vistrail(locator)
        
        # the controller will take care of upgrades
        controller = VistrailController()
        controller.set_vistrail(v, locator, abstractions, thumbnails, mashups)
        p1 = v.getPipeline('int chain')
        n = v.get_version_number('int chain')
        controller.change_selected_version(n)
        controller.flush_delayed_actions()
        p1 = controller.current_pipeline
        
        view = DummyView()
        interpreter = core.interpreter.cached.CachedInterpreter.get()
        result = interpreter.execute(p1, 
                                     locator=v,
                                     current_version=n,
                                     view=view,
                                     )
        # to force fresh params
        p2 = v.getPipeline('int chain')
        controller.change_selected_version(n)
        controller.flush_delayed_actions()
        p2 = controller.current_pipeline
        result = interpreter.execute(p2, 
                                     locator=v,
                                     current_version=n,
                                     view=view,
                                     )
        assert len(result.modules_added) == 1


if __name__ == '__main__':
    unittest.main()
