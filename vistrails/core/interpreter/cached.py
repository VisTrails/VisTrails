###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
import copy
import gc
import cPickle as pickle

from vistrails.core.common import InstanceObject, VistrailsInternalError
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core import debug
import vistrails.core.interpreter.base
from vistrails.core.interpreter.base import AbortExecution
from vistrails.core.interpreter.job import JobMonitor
import vistrails.core.interpreter.utils
from vistrails.core.log.controller import DummyLogController
from vistrails.core.modules.basic_modules import identifier as basic_pkg, \
                                                 Generator
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.vistrails_module import ModuleBreakpoint, \
    ModuleConnector, ModuleError, ModuleErrors, ModuleHadError, \
    ModuleSuspended, ModuleWasSuspended
from vistrails.core.utils import DummyView
import vistrails.core.system
import vistrails.core.vistrail.pipeline

###############################################################################

class ViewUpdatingLogController(object):
    class Loop(object):
        def __init__(self, logger, view):
            self.log = logger
            self.view = view

        def end_loop_execution(self):
            self.log.finish_loop_execution()

        def begin_iteration(self, looped_obj, iteration):
            self.log.start_iteration(looped_obj, iteration)

        def end_iteration(self, looped_obj):
            self.log.finish_iteration(looped_obj)

    def __init__(self, logger, view, remap_id, ids,
                 module_executed_hook=[]):
        self.log = logger
        self.view = view
        self.remap_id = remap_id
        self.ids = set(ids) # modules left to be executed
        self.nb_modules = len(self.ids)
        self.module_executed_hook = module_executed_hook

        self.errors = {}
        self.executed = {}
        self.suspended = {}
        self.cached = {}

    def signalSuccess(self, obj):
        self.executed[obj.id] = True
        for callable_ in self.module_executed_hook:
            callable_(obj.id)

    def signalError(self, obj, error):
        self.errors[obj.id] = error

    def begin_update(self, obj):
        i = self.remap_id(obj.id)
        self.view.set_module_active(i)

    def begin_compute(self, obj):
        i = self.remap_id(obj.id)
        self.view.set_module_computing(i)

        reg = get_module_registry()
        module_name = reg.get_descriptor(obj.__class__).name

        self.log.start_execution(obj, i, module_name)

    def update_progress(self, obj, progress=0.0):
        i = self.remap_id(obj.id)
        self.view.set_module_progress(i, progress)

    def begin_loop_execution(self, obj, total_iterations=None):
        return ViewUpdatingLogController.Loop(
                self.log.start_loop_execution(obj, total_iterations),
                self.view)

    def _handle_suspended(self, obj, error):
        """ _handle_suspended(obj: VistrailsModule, error: ModuleSuspended
            ) -> None
            Report module as suspended
        """
        # update job monitor because this may be an oldStyle job
        jm = JobMonitor.getInstance()
        reg = get_module_registry()
        name = reg.get_descriptor(obj.__class__).name
        i = "%s" % self.remap_id(obj.id)
        iteration = self.log.get_iteration_from_module(obj)
        if iteration is not None:
            name = name + '/' + str(iteration)
            i = i + '/' + str(iteration)
        # add to parent list for computing the module tree later
        error.name = name
        # if signature is not set we use the module identifier
        if not error.signature:
            error.signature = obj.signature
        jm.addParent(error)

    def end_update(self, obj, error=None, errorTrace=None,
            was_suspended=False):
        try:
            i = self.remap_id(obj.id)
        except KeyError:
            # This happens with Groups: we get end_update for modules inside
            # the Group, which we can't remap to the current pipeline
            # It's ok, because that was already logged by the recursive
            # execute_pipeline() call
            return
        if was_suspended:
            self._handle_suspended(obj, error)
            self.suspended[obj.id] = error
            self.view.set_module_suspended(i, error)
            if error.children:
                for child in error.children:
                    self.end_update(child.module, child, was_suspended=True)
        elif error is None:
            self.view.set_module_success(i)
        else:
            self.view.set_module_error(i, error)

        if i in self.ids:
            self.ids.remove(i)
            self.view.set_execution_progress(
                    1.0 - ((len(self.ids) + len(Generator.generators)) * 1.0 /
                           (self.nb_modules + len(Generator.generators))))

        msg = '' if error is None else error.msg
        self.log.finish_execution(obj, msg, errorTrace,
                                  was_suspended)

    def update_cached(self, obj):
        self.cached[obj.id] = True
        i = self.remap_id(obj.id)

        reg = get_module_registry()
        module_name = reg.get_descriptor(obj.__class__).name

        self.log.start_execution(obj, i, module_name,
                                 cached=1)
        self.view.set_module_not_executed(i)
        self.log.finish_execution(obj, '')

    def set_computing(self, obj):
        i = self.remap_id(obj.id)
        self.view.set_module_computing(i)

    def annotate(self, obj, d):
        self.log.insert_module_annotations(obj, d)

    def add_machine(self, machine):
        return self.log.add_machine(machine)

    def add_exec(self, exec_):
        return self.log.add_exec(exec_)

###############################################################################

Variant_desc = None
InputPort_desc = None

class CachedInterpreter(vistrails.core.interpreter.base.BaseInterpreter):

    def __init__(self):
        vistrails.core.interpreter.base.BaseInterpreter.__init__(self)
        self.debugger = None
        self.create()

    def create(self):
        # FIXME moved here because otherwise we hit the registry too early
        from vistrails.core.modules.module_utils import FilePool
        self._file_pool = FilePool()
        self._persistent_pipeline = vistrails.core.vistrail.pipeline.Pipeline()
        self._objects = {}
        self.filePool = self._file_pool
        self._streams = []

    def clear(self):
        self._file_pool.cleanup()
        self._persistent_pipeline.clear()
        for obj in self._objects.itervalues():
            obj.clear()
        self._objects = {}

    def __del__(self):
        self.clear()

    def clean_modules(self, modules_to_clean):
        """clean_modules(modules_to_clean: list of persistent module ids)

        Removes modules from the persistent pipeline, and the modules that
        depend on them."""
        if not modules_to_clean:
            return
        g = self._persistent_pipeline.graph
        modules_to_clean = (set(modules_to_clean) &
                            set(self._persistent_pipeline.modules.iterkeys()))
        dependencies = g.vertices_topological_sort(modules_to_clean)
        for v in dependencies:
            self._persistent_pipeline.delete_module(v)
            del self._objects[v]

    def clean_non_cacheable_modules(self):
        """clean_non_cacheable_modules() -> None

        Removes all modules that are not cacheable from the persistent
        pipeline, and the modules that depend on them.
        """
        non_cacheable_modules = [i for
                                 (i, mod) in self._objects.iteritems()
                                 if not mod.is_cacheable()]
        self.clean_modules(non_cacheable_modules)

    def _clear_package(self, identifier):
        """clear_package(identifier: str) -> None

        Removes all modules from the given package from the persistent
        pipeline.
        """
        modules = [mod.id
                   for mod in self._persistent_pipeline.module_list
                   if mod.module_descriptor.identifier == identifier]
        self.clean_modules(modules)

    def make_connection(self, conn, src, dst):
        """make_connection(self, conn, src, dst)
        Builds a execution-time connection between modules.

        """
        iport = conn.destination.name
        oport = conn.source.name
        src.enable_output_port(oport)
        src.load_type_check_descs()
        if isinstance(src, src.InputPort_desc.module):
            typecheck = [False]
        else:
            typecheck = src.get_type_checks(conn.source.spec)
        dst.set_input_port(iport,
                           ModuleConnector(src, oport, conn.source.spec,
                                           typecheck))

    def setup_pipeline(self, pipeline, **kwargs):
        """setup_pipeline(controller, pipeline, locator, currentVersion,
                          view, aliases, **kwargs)
        Matches a pipeline with the persistent pipeline and creates
        instances of modules that aren't in the cache.
        """
        def fetch(name, default):
            return kwargs.pop(name, default)
        controller = fetch('controller', None)
        locator = fetch('locator', None)
        current_version = fetch('current_version', None)
        view = fetch('view', DummyView())
        vistrail_variables = fetch('vistrail_variables', None)
        aliases = fetch('aliases', None)
        params = fetch('params', None)
        extra_info = fetch('extra_info', None)
        logger = fetch('logger', DummyLogController)
        sinks = fetch('sinks', None)
        reason = fetch('reason', None)
        actions = fetch('actions', None)
        done_summon_hooks = fetch('done_summon_hooks', [])
        module_executed_hook = fetch('module_executed_hook', [])
        stop_on_error = fetch('stop_on_error', True)
        parent_exec = fetch('parent_exec', None)

        reg = get_module_registry()

        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed '
                                         'to setup_pipeline: %s' % kwargs)

        def create_null():
            """Creates a Null value"""
            getter = reg.get_descriptor_by_name
            descriptor = getter(basic_pkg, 'Null')
            return descriptor.module()
        
        def create_constant(param, module):
            """Creates a Constant from a parameter spec"""
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
        if vistrail_variables:
            self.resolve_variables(vistrail_variables,  pipeline)

        self.update_params(pipeline, params)
        
        (tmp_to_persistent_module_map,
         conn_map,
         module_added_set,
         conn_added_set) = self.add_to_persistent_pipeline(pipeline)

        # Create the new objects
        for i in module_added_set:
            persistent_id = tmp_to_persistent_module_map[i]
            module = self._persistent_pipeline.modules[persistent_id]
            obj = self._objects[persistent_id] = module.summon()
            obj.interpreter = self
            obj.id = persistent_id
            obj.signature = module._signature
            
            # Checking if output should be stored
            if module.has_annotation_with_key('annotate_output'):
                annotate_output = module.get_annotation_by_key('annotate_output')
                #print annotate_output
                if annotate_output:
                    obj.annotate_output = True

            for f in module.functions:
                connector = None
                if len(f.params) == 0:
                    connector = ModuleConnector(create_null(), 'value',
                                                f.get_spec('output'))
                elif len(f.params) == 1:
                    p = f.params[0]
                    try:
                        constant = create_constant(p, module)
                        connector = ModuleConnector(constant, 'value',
                                                    f.get_spec('output'))
                    except Exception, e:
                        debug.unexpected_exception(e)
                        err = ModuleError(
                                module,
                                "Uncaught exception creating Constant from "
                                "%r: %s" % (
                                p.strValue,
                                debug.format_exception(e)))
                        errors[i] = err
                        to_delete.append(obj.id)
                else:
                    tupleModule = vistrails.core.interpreter.base.InternalTuple()
                    tupleModule.length = len(f.params)
                    for (j,p) in enumerate(f.params):
                        try:
                            constant = create_constant(p, module)
                            constant.update()
                            connector = ModuleConnector(constant, 'value',
                                                        f.get_spec('output'))
                            tupleModule.set_input_port(j, connector)
                        except Exception, e:
                            debug.unexpected_exception(e)
                            err = ModuleError(
                                    module,
                                    "Uncaught exception creating Constant "
                                    "from %r: %s" % (
                                    p.strValue,
                                    debug.format_exception(e)))
                            errors[i] = err
                            to_delete.append(obj.id)
                    connector = ModuleConnector(tupleModule, 'value',
                                                f.get_spec('output'))
                if connector:
                    obj.set_input_port(f.name, connector, is_method=True)

        # Create the new connections
        for i in conn_added_set:
            persistent_id = conn_map[i]
            conn = self._persistent_pipeline.connections[persistent_id]
            src = self._objects[conn.sourceId]
            dst = self._objects[conn.destinationId]
            self.make_connection(conn, src, dst)

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
            return kwargs.pop(name, default)
        controller = fetch('controller', None)
        locator = fetch('locator', None)
        current_version = fetch('current_version', None)
        view = fetch('view', DummyView())
        vistrail_variables = fetch('vistrail_variables', None)
        aliases = fetch('aliases', None)
        params = fetch('params', None)
        extra_info = fetch('extra_info', None)
        logger = fetch('logger', DummyLogController)
        sinks = fetch('sinks', None)
        reason = fetch('reason', None)
        actions = fetch('actions', None)
        module_executed_hook = fetch('module_executed_hook', [])
        done_summon_hooks = fetch('done_summon_hooks', [])
        clean_pipeline = fetch('clean_pipeline', False)
        stop_on_error = fetch('stop_on_error', True)
        parent_exec = fetch('parent_exec', None)

        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed '
                                         'to execute_pipeline: %s' % kwargs)

        # LOGGING SETUP
        def get_remapped_id(id):
            return persistent_to_tmp_id_map[id]

        logging_obj = ViewUpdatingLogController(
                logger=logger,
                view=view,
                remap_id=get_remapped_id,
                ids=pipeline.modules.keys(),
                module_executed_hook=module_executed_hook)

        # PARAMETER CHANGES SETUP
        parameter_changes = []
        def change_parameter(obj, name, value):
            parameter_changes.append((get_remapped_id(obj.id),
                                      name, value))
        def make_change_parameter(obj):
            return lambda *args: change_parameter(obj, *args)

        # Update **all** modules in the current pipeline
        for i, obj in tmp_id_to_module_map.iteritems():
            obj.in_pipeline = True # set flag to indicate in pipeline
            obj.logging = logging_obj
            obj.change_parameter = make_change_parameter(obj)
            
            # Update object pipeline information
            obj.moduleInfo['locator'] = locator
            obj.moduleInfo['version'] = current_version
            obj.moduleInfo['moduleId'] = i
            obj.moduleInfo['pipeline'] = pipeline
            obj.moduleInfo['controller'] = controller
            if extra_info is not None:
                obj.moduleInfo['extra_info'] = extra_info
            if reason is not None:
                obj.moduleInfo['reason'] = reason
            if actions is not None:
                obj.moduleInfo['actions'] = actions

        ## Checking 'sinks' from kwargs to resolve only requested sinks
        # Note that we accept any module in 'sinks', even if it's not actually
        # a sink in the graph
        if sinks is not None:
            persistent_sinks = [tmp_id_to_module_map[sink]
                                for sink in sinks
                                if sink in tmp_id_to_module_map]
        else:
            persistent_sinks = [tmp_id_to_module_map[sink]
                                for sink in pipeline.graph.sinks()]

        self._streams.append(Generator.generators)
        Generator.generators = []

        # Update new sinks
        for obj in persistent_sinks:
            abort = False
            try:
                obj.update()
                continue
            except ModuleWasSuspended:
                continue
            except ModuleHadError:
                pass
            except AbortExecution:
                break
            except ModuleSuspended, ms:
                ms.module.logging.end_update(ms.module, ms,
                                             was_suspended=True)
                continue
            except ModuleErrors, mes:
                for me in mes.module_errors:
                    me.module.logging.end_update(me.module, me)
                    logging_obj.signalError(me.module, me)
                    abort = abort or me.abort
            except ModuleError, me:
                me.module.logging.end_update(me.module, me, me.errorTrace)
                logging_obj.signalError(me.module, me)
                abort = me.abort
            except ModuleBreakpoint, mb:
                mb.module.logging.end_update(mb.module)
                logging_obj.signalError(mb.module, mb)
                abort = True
            if stop_on_error or abort:
                break

        # execute all generators until inputs are exhausted
        # this makes sure branching and multiple sinks are executed correctly
        if not logging_obj.errors and not logging_obj.suspended and \
                                                          Generator.generators:
            result = True
            abort = False
            while result is not None:
                try:
                    for m in Generator.generators:
                        result = m.generator.next()
                    continue
                except AbortExecution:
                    break
                except ModuleErrors, mes:
                    for me in mes.module_errors:
                        me.module.logging.end_update(me.module, me)
                        logging_obj.signalError(me.module, me)
                        abort = abort or me.abort
                except ModuleError, me:
                    me.module.logging.end_update(me.module, me, me.errorTrace)
                    logging_obj.signalError(me.module, me)
                    abort = me.abort
                except ModuleBreakpoint, mb:
                    mb.module.logging.end_update(mb.module)
                    logging_obj.signalError(mb.module, mb)
                    abort = True
                except Exception, e:
                    import traceback
                    traceback.print_exc()
                    abort = True
                if stop_on_error or abort:
                    break

        Generator.generators = self._streams.pop()

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
            if obj.id in logging_obj.errors:
                errs[tmp_id] = logging_obj.errors[obj.id]
                if not clean_pipeline:
                    to_delete.append(obj.id)
            executed = False
            if obj.id in logging_obj.executed:
                execs[tmp_id] = logging_obj.executed[obj.id]
                executed = True
            if obj.id in logging_obj.suspended:
                suspends[tmp_id] = logging_obj.suspended[obj.id]
                if not clean_pipeline:
                    to_delete.append(obj.id)
                executed = True
            if obj.id in logging_obj.cached:
                caches[tmp_id] = logging_obj.cached[obj.id]
                executed = True
            if not executed:
                # these modules didn't execute
                execs[tmp_id] = False

        return (to_delete, objs, errs, execs, suspends, caches, parameter_changes)

    def finalize_pipeline(self, pipeline, to_delete, objs, errs, execs,
                          suspended, cached, **kwargs):
        def fetch(name, default):
            return kwargs.pop(name, default)
        reset_computed = fetch('reset_computed', True)
        view = fetch('view', None)

        self.clean_modules(to_delete)

        def dict2set(s):
            return set(k for k, v in s.iteritems() if v)
        if view is not None:
            persistent = set(objs) - (dict2set(errs) | dict2set(execs) |
                                      dict2set(suspended) | dict2set(cached))
            for i in persistent:
                view.set_module_persistent(i)

        if reset_computed:
            for module in self._objects.itervalues():
                module.computed = False

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
          logger = fetch('logger', DummyLogController)
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
            new_kwargs[name] = r = kwargs.pop(name, default)
            return r
        controller = fetch('controller', None)
        locator = fetch('locator', None)
        current_version = fetch('current_version', None)
        view = fetch('view', DummyView())
        vistrail_variables = fetch('vistrail_variables', None)
        aliases = fetch('aliases', None)
        params = fetch('params', None)
        extra_info = fetch('extra_info', None)
        logger = fetch('logger', DummyLogController)
        sinks = fetch('sinks', None)
        reason = fetch('reason', None)
        actions = fetch('actions', None)
        done_summon_hooks = fetch('done_summon_hooks', [])
        module_executed_hook = fetch('module_executed_hook', [])
        stop_on_error = fetch('stop_on_error', True)
        parent_exec = fetch('parent_exec', None)

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

        logger = logger.start_workflow_execution(
                parent_exec,
                vistrail, pipeline, current_version)
        new_kwargs['logger'] = logger
        self.annotate_workflow_execution(logger, reason, aliases, params)

        res = self.setup_pipeline(pipeline, **new_kwargs)
        modules_added = res[2]
        conns_added = res[3]
        to_delete = res[4]
        errors = res[5]
        if len(errors) == 0:
            res = self.execute_pipeline(pipeline, *(res[:2]), **new_kwargs)
        else:
            res = (to_delete, res[0], errors, {}, {}, {}, [])
            for (i, error) in errors.iteritems():
                view.set_module_error(i, error)
        self.finalize_pipeline(pipeline, *(res[:-1]), **new_kwargs)

        result = InstanceObject(objects=res[1],
                              errors=res[2],
                              executed=res[3],
                              suspended=res[4],
                              parameter_changes=res[6],
                              modules_added=modules_added,
                              conns_added=conns_added)

        logger.finish_workflow_execution(result.errors, suspended=result.suspended)

        return result

    def annotate_workflow_execution(self, logger, reason, aliases, params):
        """annotate_workflow_Execution(logger: LogController, reason:str,
                                        aliases:dict, params:list)-> None
        It will annotate the workflow execution in logger with the reason,
        aliases and params.
        
        """
        d = {}
        d["__reason__"] = reason
        if aliases is not None and isinstance(aliases, dict):
            d["__aliases__"] = pickle.dumps(aliases)
        if params is not None and isinstance(params, list):
            d["__params__"] = pickle.dumps(params)
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

    @staticmethod
    def clear_package(identifier):
        if CachedInterpreter.__instance:
            CachedInterpreter.__instance._clear_package(identifier)

###############################################################################
# Testing

import unittest


class TestCachedInterpreter(unittest.TestCase):

    def test_cache(self):
        from vistrails.core.modules.basic_modules import StandardOutput
        old_compute = StandardOutput.compute
        StandardOutput.compute = lambda s: None

        try:
            from vistrails.core.db.locator import XMLFileLocator
            from vistrails.core.vistrail.controller import VistrailController
            from vistrails.core.db.io import load_vistrail

            """Test if basic caching is working."""
            locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                                '/tests/resources/dummy.xml')
            (v, abstractions, thumbnails, mashups) = load_vistrail(locator)

            # the controller will take care of upgrades
            controller = VistrailController(v, locator, abstractions,
                                            thumbnails,  mashups)
            p1 = v.getPipeline('int chain')
            n = v.get_version_number('int chain')
            controller.change_selected_version(n)
            controller.flush_delayed_actions()
            p1 = controller.current_pipeline

            view = DummyView()
            interpreter = CachedInterpreter.get()
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
            self.assertEqual(len(result.modules_added), 1)
        finally:
            StandardOutput.compute = old_compute


if __name__ == '__main__':
    unittest.main()
