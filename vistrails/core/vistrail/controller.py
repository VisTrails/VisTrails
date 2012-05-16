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

import copy
import os
import uuid
import shutil
import tempfile

from core.configuration import get_vistrails_configuration
import core.db.action
import core.db.io
import core.db.locator
from core import debug
from core.data_structures.graph import Graph
from core.interpreter.default import get_default_interpreter
from core.log.controller import LogControllerFactory, DummyLogController
from core.log.log import Log
from core.modules.abstraction import identifier as abstraction_pkg, \
    version as abstraction_ver
from core.modules.basic_modules import identifier as basic_pkg
import core.modules.module_registry
from core.modules.module_registry import ModuleRegistryException, \
    MissingModuleVersion, MissingModule, MissingPackageVersion, MissingPort, \
    MissingPackage
from core.modules.package import Package
from core.modules.sub_module import new_abstraction, read_vistrail, \
    get_all_abs_namespaces, get_cur_abs_namespace, get_cur_abs_annotation_key, \
    get_next_abs_annotation_key, save_abstraction
from core.packagemanager import PackageManager, get_package_manager
import core.packagerepository
from core.thumbnails import ThumbnailCache
from core.upgradeworkflow import UpgradeWorkflowHandler, UpgradeWorkflowError
from core.utils import VistrailsInternalError, PortAlreadyExists, DummyView, \
    InvalidPipeline
from core.system import vistrails_default_file_type
from core.vistrail.abstraction import Abstraction
from core.vistrail.action import Action
from core.vistrail.annotation import Annotation
from core.vistrail.connection import Connection
from core.vistrail.group import Group
from core.vistrail.location import Location
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.pipeline import Pipeline
from core.vistrail.port import Port
from core.vistrail.port_spec import PortSpec
from core.vistrail.vistrail import Vistrail
from db import VistrailsDBException
from db.domain import IdScope, DBWorkflowExec
from db.services.io import create_temp_folder, remove_temp_folder
from db.services.io import SaveBundle, open_vt_log_from_db

from db.services.vistrail import getSharedRoot
from core.utils import any

def vt_action(f):
    def new_f(self, *args, **kwargs):
        self.flush_delayed_actions()
        action = f(self, *args, **kwargs)
        if action is not None:
            self.add_new_action(action)
            self.perform_action(action)
        return action
    return new_f

class VistrailController(object):
    def __init__(self, vistrail=None, id_scope=None, auto_save=True):
        self.vistrail = vistrail
        self.id_scope = id_scope
        self.current_session = -1
        self.log = Log()
        self._auto_save = auto_save
        if vistrail is not None:
            self.id_scope = vistrail.idScope
            self.current_session = vistrail.idScope.getNewId('session')
            vistrail.current_session = self.current_session
            vistrail.log = self.log
        self._current_pipeline = None
        self.locator = None
        self.name = ''
        self.file_name = ''
        self._current_version = -1
        self.changed = False

        # if _cache_pipelines is True, cache pipelines to speed up
        # version switching
        self._cache_pipelines = True
        self.flush_pipeline_cache()
        self._current_full_graph = None
        self._current_terse_graph = None
        self.num_versions_always_shown = 1

        # if self.search is True, vistrail is currently being searched
        self.search = None
        self.search_str = None
        # If self.refine is True, search mismatches are hidden instead                              
        # of ghosted                                                                                
        self.refine = False
        self.full_tree = False

        self._asked_packages = set()
        self._delayed_actions = []
        self._loaded_abstractions = {}
        
        # This will just store the mashups in memory and send them to SaveBundle
        # when writing the vistrail
        self._mashups = []

        # the redo stack stores the undone action ids 
        # (undo is automatic with us, through the version tree)
        self.redo_stack = []
        
    # allow gui.vistrail_controller to reference individual views
    def _get_current_version(self):
        return self._current_version
    def _set_current_version(self, version):
        self._current_version = version
    current_version = property(_get_current_version, _set_current_version)

    def _get_current_pipeline(self):
        return self._current_pipeline
    def _set_current_pipeline(self, pipeline):
        self._current_pipeline = pipeline
    current_pipeline = property(_get_current_pipeline, _set_current_pipeline)

    def flush_pipeline_cache(self):
        self._pipelines = {0: Pipeline()}

    def logging_on(self):
        return not get_vistrails_configuration().check('nologger')
            
    def get_logger(self):
        if self.logging_on():
            return LogControllerFactory.getInstance().create_logger(self.log)
        else:
            return DummyLogController()
        
    def get_locator(self):
        return self.locator
    
    def set_vistrail(self, vistrail, locator, abstractions=None, 
                     thumbnails=None, mashups=None, set_log_on_vt=True):
        self.vistrail = vistrail
        if self.vistrail is not None:
            self.id_scope = self.vistrail.idScope
            self.current_session = self.vistrail.idScope.getNewId("session")
            self.vistrail.current_session = self.current_session
            if set_log_on_vt:
                self.vistrail.log = self.log
            if abstractions is not None:
                self.ensure_abstractions_loaded(self.vistrail, abstractions)
            if thumbnails is not None:
                ThumbnailCache.getInstance().add_entries_from_files(thumbnails)
            if mashups is not None:
                self._mashups = mashups
        self.current_version = -1
        self.current_pipeline = Pipeline()
        if self.locator != locator and self.locator is not None:
            self.locator.clean_temporaries()
        self.locator = locator
        self.recompute_terse_graph()
        
    def close_vistrail(self, locator):
        if not self.vistrail.is_abstraction:
            self.unload_abstractions()
        if locator is not None:
            locator.clean_temporaries()
            locator.close()
            
    def set_id_scope(self, id_scope):
        self.id_scope = id_scope

    def set_changed(self, changed):
        """ set_changed(changed: bool) -> None
        Set the current state of changed and emit signal accordingly
        
        """
        if changed!=self.changed:
            self.changed = changed
        
    def set_file_name(self, file_name):
        """ set_file_name(file_name: str) -> None
        Change the controller file name
        
        """
        if file_name == None:
            file_name = ''
        if self.file_name!=file_name:
            self.file_name = file_name
            self.name = os.path.split(file_name)[1]
            if self.name=='':
                self.name = 'untitled%s'%vistrails_default_file_type()
                
    def check_alias(self, name):
        """check_alias(alias) -> Boolean 
        Returns True if current pipeline has an alias named name """
        # FIXME Why isn't this call on the pipeline?
        return self.current_pipeline.has_alias(name)
    
    def check_vistrail_variable(self, name):
        """check_vistrail_variable(var) -> Boolean
        Returns True if vistrail has a variable named name """
        if self.vistrail:
            return self.vistrail.has_vistrail_var(name)
        return False
    
    def set_vistrail_variable(self, name, value):
        """set_vistrail_variable(var) -> Boolean
        Returns True if vistrail variable was changed """
        if self.vistrail:
            changed = self.vistrail.set_vistrail_var(name, value)
            if changed:
                self.set_changed(changed)
            return changed
        return False
    
    def get_vistrail_variables(self):
        """get_vistrail_variables() -> dict
        Returns the dictionary of vistrail variables """
        if self.vistrail:
            return self.vistrail.vistrail_vars
        return {}
    
    def get_vistrail_variable_name_by_uuid(self, uuid):
        """def get_vistrail_variable_name_by_uuid(uuid: str) -> dict
        Returns the var name for vistrail variable with uuid """
        vars = self.get_vistrail_variables()
        for var_name, var_info in vars.iteritems():
            var_uuid, descriptor_info, var_strValue = var_info
            if var_uuid == uuid:
                return var_name
    
    def invalidate_version_tree(self, *args, **kwargs):
        """ invalidate_version_tree(self, *args, **kwargs) -> None
        Does nothing, gui/vistrail_controller.py does, though
        """
        pass

    ##########################################################################
    # Actions, etc

    def has_move_actions(self):
        return False
    
    def flush_move_actions(self):
        return False

    def migrate_tags(self, from_version, to_version, vistrail=None):
        if vistrail is None:
            vistrail = self.vistrail
        tag = vistrail.get_tag(from_version)
        if tag:
            vistrail.set_tag(from_version, "")
            vistrail.set_tag(to_version, tag)
        notes = vistrail.get_notes(from_version)
        if notes:
            vistrail.set_notes(from_version, "")
            vistrail.set_notes(to_version, notes)

    def flush_delayed_actions(self):
        start_version = self.current_version
        desc_key = Action.ANNOTATION_DESCRIPTION
        added_upgrade = False
        should_migrate_tags = get_vistrails_configuration().check("migrateTags")
        for action in self._delayed_actions:
            self.vistrail.add_action(action, start_version, 
                                     self.current_session)
            # HACK to populate upgrade information
            if (action.has_annotation_with_key(desc_key) and
                action.get_annotation_by_key(desc_key).value == 'Upgrade'):
                self.vistrail.set_upgrade(start_version, str(action.id))
            if should_migrate_tags:
                self.migrate_tags(start_version, action.id)
            self.current_version = action.id
            start_version = action.id
            added_upgrade = True

        # We have to do moves after the delayed actions because the pipeline
        # may have been updated
        added_moves = self.flush_move_actions()
        self._delayed_actions = []
        if added_upgrade or added_moves:
            self.recompute_terse_graph()
            self.invalidate_version_tree(False)

    def perform_action(self, action):
        """ performAction(action: Action) -> timestep
        
        Performs given action on current pipeline.
        
        """
        if action is not None:
            self.current_pipeline.perform_action(action)
            self.current_version = action.db_id
            return action.db_id
        return None

    def add_new_action(self, action):
        """add_new_action(action) -> None

        Call this function to add a new action to the vistrail being
        controlled by the vistrailcontroller.

        FIXME: In the future, this function should watch the vistrail
        and get notified of the change.

        """
        if action is not None:
            self.vistrail.add_action(action, self.current_version, 
                                     self.current_session)
            self.set_changed(True)
            self.current_version = action.db_id
            self.recompute_terse_graph()
            
    def create_module_from_descriptor(self, *args, **kwargs):
        return self.create_module_from_descriptor_static(self.id_scope,
                                                         *args, **kwargs)

    @staticmethod
    def create_module_from_descriptor_static(id_scope, descriptor, 
                                             x=0.0, y=0.0, 
                                             internal_version=-1):
        reg = core.modules.module_registry.get_module_registry()
        package = reg.get_package_by_name(descriptor.identifier)
        loc_id = id_scope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=x, 
                            y=y,
                            )
        if internal_version > -1:
            # only get the current namespace if this is a local subworkflow
            if package == abstraction_pkg:
                namespace = get_cur_abs_namespace(descriptor.module.vistrail)
            else:
                namespace = descriptor.namespace
            abstraction_id = id_scope.getNewId(Abstraction.vtType)
            module = Abstraction(id=abstraction_id,
                                 name=descriptor.name,
                                 package=descriptor.identifier,
                                 namespace=namespace,
                                 version=package.version,
                                 location=location,
                                 internal_version=internal_version,
                                 )
        elif descriptor.identifier == basic_pkg and \
                descriptor.name == 'Group':
            group_id = id_scope.getNewId(Group.vtType)
            module = Group(id=group_id,
                           name=descriptor.name,
                           package=descriptor.identifier,
                           namespace=descriptor.namespace,
                           version=package.version,
                           location=location,
                           )
        else:
            module_id = id_scope.getNewId(Module.vtType)
            module = Module(id=module_id,
                            name=descriptor.name,
                            package=descriptor.identifier,
                            namespace=descriptor.namespace,
                            version=package.version,
                            location=location,
                            )
        module.is_valid = True
        return module

    def create_module(self, *args, **kwargs):
        return self.create_module_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_module_static(id_scope, identifier, name, namespace='', 
                             x=0.0, y=0.0, internal_version=-1):
        reg = core.modules.module_registry.get_module_registry()
        d = reg.get_descriptor_by_name(identifier, name, namespace)
        static_call = VistrailController.create_module_from_descriptor_static
        return static_call(id_scope, d, x, y, internal_version)

    def create_connection_from_ids(self, output_id, output_port_spec,
                                       input_id, input_port_spec):
        output_module = self.current_pipeline.modules[output_id]
        input_module = self.current_pipeline.modules[input_id]
        return self.create_connection(output_module, output_port_spec, 
                                      input_module, input_port_spec)

    def create_connection(self, *args, **kwargs):
        return self.create_connection_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_connection_static(id_scope, output_module, output_port_spec,
                                 input_module, input_port_spec):     
        if type(output_port_spec) == type(""):
            output_port_spec = \
                output_module.get_port_spec(output_port_spec, 'output')
        if type(input_port_spec) == type(""):
            input_port_spec = \
                input_module.get_port_spec(input_port_spec, 'input')            
        if output_port_spec is None:
            raise VistrailsInternalError("output port spec is None")
        if input_port_spec is None:
            raise VistrailsInternalError("input port spec is None")
        output_port_id = id_scope.getNewId(Port.vtType)
        output_port = Port(id=output_port_id,
                           spec=output_port_spec,
                           moduleId=output_module.id,
                           moduleName=output_module.name)
        input_port_id = id_scope.getNewId(Port.vtType)
        input_port = Port(id=input_port_id,
                           spec=input_port_spec,
                           moduleId=input_module.id,
                           moduleName=input_module.name)
        conn_id = id_scope.getNewId(Connection.vtType)
        connection = Connection(id=conn_id,
                                ports=[input_port, output_port])
        return connection

    def create_param(self, *args, **kwargs):
        return self.create_param_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_param_static(id_scope, port_spec, pos, value, alias='', 
                            query_method=None):
        param_id = id_scope.getNewId(ModuleParam.vtType)
        descriptor = port_spec.descriptors()[pos]
        param_type = descriptor.sigstring
        # FIXME add/remove description
        # FIXME make ModuleParam constructor accept port_spec
        new_param = ModuleParam(id=param_id,
                                pos=pos,
                                name='<no description>',
                                alias=alias,
                                val=value,
                                type=param_type,
                                )

        # FIXME probably should put this in the ModuleParam constructor
        new_param.queryMethod = query_method
        return new_param

    def create_params(self, *args, **kwargs):
        return self.create_params_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_params_static(id_scope, port_spec, values, aliases=[], 
                             query_methods=[]):
        params = []
        for i in xrange(len(port_spec.descriptors())):
            if i < len(values):
                value = str(values[i])
            else:
                value = None
            if i < len(aliases):
                alias = str(aliases[i])
            else:
                alias = ''
            if i < len(query_methods):
                query_method = query_methods[i]
            else:
                query_method = None
            param = VistrailController.create_param_static(id_scope, port_spec,
                                                           i, value, alias,
                                                           query_method)
            params.append(param)
        return params

    def create_function(self, *args, **kwargs):
        return self.create_function_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_function_static(id_scope, module, function_name, 
                               param_values=[], aliases=[], query_methods=[]):
        port_spec = module.get_port_spec(function_name, 'input')
        if len(param_values) <= 0 and port_spec.defaults is not None:
            param_values = port_spec.defaults

        f_id = id_scope.getNewId(ModuleFunction.vtType)
        new_function = ModuleFunction(id=f_id,
                                      pos=module.getNumFunctions(),
                                      name=function_name,
                                      )
        new_function.is_valid = True
        new_params = \
            VistrailController.create_params_static(id_scope, port_spec, 
                                                    param_values, aliases,
                                                    query_methods)
        new_function.add_parameters(new_params)        
        return new_function

    def create_functions(self, *args, **kwargs):
        return self.create_functions_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_functions_static(id_scope, module, functions):
        """create_functions(module: Module,
                            functions: [function_name: str,
                                        param_values: [str]]) 
            -> [ModuleFunction]
        
        """
        new_functions = []
        static_call = VistrailController.create_function_static
        for f in functions:
            new_functions.append(static_call(id_scope, module, *f))
        return new_functions

    def create_port_spec(self, *args, **kwargs):
        return self.create_port_spec_static(self.id_scope, *args, **kwargs)
    
    @staticmethod
    def create_port_spec_static(id_scope, module, port_type, port_name, 
                                port_sigstring, port_sort_key=-1):
        p_id = id_scope.getNewId(PortSpec.vtType)
        port_spec = PortSpec(id=p_id,
                             type=port_type,
                             name=port_name,
                             sigstring=port_sigstring,
                             sort_key=port_sort_key,
                             )
        return port_spec

    def get_module_connection_ids(self, module_ids, graph):
        connection_ids = set()
        for module_id in module_ids:
            for v, id in graph.edges_from(module_id):
                connection_ids.add(id)
            for v, id in graph.edges_to(module_id):
                connection_ids.add(id)
        return connection_ids

    def delete_module_list_ops(self, pipeline, module_ids):
        graph = pipeline.graph
        connect_ids = self.get_module_connection_ids(module_ids, graph)
        ops = []
        for c_id in connect_ids:
            ops.append(('delete', pipeline.connections[c_id]))
        for m_id in module_ids:
            ops.append(('delete', pipeline.modules[m_id]))
        return ops

    def update_port_spec_ops(self, module, deleted_ports, added_ports):
        op_list = []
        deleted_port_info = set()
        changed_port_info = set()
        for p in deleted_ports:
            port_info = (p[1], p[0])
            if module.has_portSpec_with_name(port_info):
                port = module.get_portSpec_by_name(port_info)
                deleted_port_info.add(port_info + (port.sigstring,))
        for p in added_ports:
            port_info = (p[1], p[0], p[2])
            if port_info in deleted_port_info:
                changed_port_info.add(port_info[:2])
            
        # Remove any connections related to deleted ports
        for c in self.current_pipeline.connections.itervalues():
            if ((c.sourceId == module.id and
                 any(c.source.name == p[1] for p in deleted_ports
                     if (p[1], p[0]) not in changed_port_info)) or
                (c.destinationId == module.id and
                 any(c.destination.name == p[1] for p in deleted_ports
                     if (p[1], p[0]) not in changed_port_info))):
                op_list.append(('delete', c))

        # Remove any functions related to deleted ports
        for p in deleted_ports:
            if (p[1], p[0]) not in changed_port_info:
                for function in module.functions:
                    if function.name == p[1]:
                        op_list.append(('delete', function, 
                                        Module.vtType, module.id))

        # Remove all deleted ports
        # !! Reset delted_port_info to not store sigstring
        deleted_port_info = set()
        for p in deleted_ports:
            port_info = (p[1], p[0])
            if module.has_portSpec_with_name(port_info):
                port_spec = module.get_portSpec_by_name(port_info)
                op_list.append(('delete', port_spec, Module.vtType, module.id))
                deleted_port_info.add(port_info)

        # Add all added ports
        for p in added_ports:
            if (p[1], p[0]) not in deleted_port_info and \
                    module.has_port_spec(p[1], p[0]):
                raise PortAlreadyExists(module.package, module.name, p[0], p[1])
            port_spec = self.create_port_spec(module, *p)
            op_list.append(('add', port_spec, Module.vtType, module.id))
        return op_list

    def update_function_ops(self, module, function_name, param_values=[],
                            old_id=-1L, should_replace=True, aliases=[],
                            query_methods=[]):
        """NOTE: aliases will be removed in the future!"""
        op_list = []
        port_spec = module.get_port_spec(function_name, 'input')

        if should_replace and old_id < 0:
            for old_function in module.functions:
                if old_function.name == function_name:
                    old_id = old_function.real_id

        # ensure that replacements don't happen for functions that
        # shouldn't be replaced
        if should_replace and old_id >= 0:
            function = module.function_idx[old_id]
            if param_values is None:
                op_list.append(('delete', function, module.vtType, module.id))
            else:
                for i, new_param_value in enumerate(param_values):
                    old_param = function.params[i]
                    if ((len(aliases) > i and old_param.alias != aliases[i]) or
                        (len(query_methods) > i and 
                         old_param.queryMethod != query_methods[i]) or
                        (old_param.strValue != new_param_value)):
                        if len(aliases) > i:
                            alias = aliases[i]
                        else:
                            alias = ''
                        if len(query_methods) > i:
                            query_method = query_methods[i]
                        else:
                            query_method = None
                        new_param = self.create_param(port_spec, i, 
                                                      new_param_value, alias,
                                                      query_method)
                        op_list.append(('change', old_param, new_param,
                                        function.vtType, function.real_id))
        elif param_values is not None:
            new_function = self.create_function(module, function_name,
                                                param_values, aliases,
                                                query_methods)
            op_list.append(('add', new_function,
                            module.vtType, module.id))        
        return op_list

    def update_functions_ops(self, module, functions):
        """update_functions_ops(module: Module, 
                                functions: [function_name: str,
                                            param_values: [str],
                                            old_id: long (-1)
                                            should_replace: bool (True)])
            -> [Op]
        Returns a list of operations that will create and update the
        functions of the specified module with new values.

        """
        op_list = []
        for f in functions:
            op_list.extend(self.update_function_ops(module, *f))
        return op_list

    def create_updated_parameter(self, old_param, new_value):
        """update_parameter(old_param: ModuleParam, new_value: str)
              -> ModuleParam
        Generates a change parameter action if the value is different

        """
        if old_param.strValue == new_value:
            return None

        param_id = self.id_scope.getNewId(ModuleParam.vtType)
        new_param = ModuleParam(id=param_id,
                                pos=old_param.pos,
                                name=old_param.name,
                                alias=old_param.alias,
                                val=new_value,
                                type=old_param.typeStr,
                                )
        return new_param

    def update_annotation_ops(self, module, annotations):
        """update_annotation_ops(module: Module, annotations: [(str, str)])
              -> [operation_list]
        
        """
        op_list = []
        for (key, value) in annotations:
            a_id = self.id_scope.getNewId(Annotation.vtType)
            annotation = Annotation(id=a_id,
                                    key=key, 
                                    value=value,
                                    )
            if module.has_annotation_with_key(key):
                old_annotation = module.get_annotation_by_key(key)
                op_list.append(('change', old_annotation, annotation,
                                module.vtType, module.id))
            else:
                op_list.append(('add', annotation, module.vtType, module.id))
        return op_list

    def check_subworkflow_versions(self, changed_subworkflow_desc):
        if self.current_pipeline is not None:
            self.current_pipeline.check_subworkflow_versions()

    @vt_action
    def add_module_action(self, module):
        if not self.current_pipeline:
            raise Exception("No version is selected")
        action = core.db.action.create_action([('add', module)])
        return action

    def add_module_from_descriptor(self, descriptor, x=0.0, y=0.0, 
                                   internal_version=-1):
        module = self.create_module_from_descriptor(descriptor, x, y, 
                                                    internal_version)
        action = self.add_module_action(module)
        return module


    def add_module(self, identifier, name, namespace='', x=0.0, y=0.0, 
                   internal_version=-1):
        """ addModule(x: int, y: int, identifier, name: str, namespace='') 
               -> Module
        Add a new module into the current pipeline
        
        """
        module = self.create_module(identifier, name, namespace, x, y,
                                    internal_version)
        action = self.add_module_action(module)
        return module
            
    def delete_module(self, module_id):
        """ delete_module(module_id: int) -> version id
        Delete a module from the current pipeline
        
        """
        return self.delete_module_list([module_id])

    def create_module_list_deletion_action(self, pipeline, module_ids):
        """ create_module_list_deletion_action(
               pipeline: Pipeline,
               module_ids: [int]) -> Action
        Create action that will delete multiple modules from the given pipeline.

        """
        ops = self.delete_module_list_ops(pipeline, module_ids)
        return core.db.action.create_action(ops)

    @vt_action
    def delete_module_list(self, module_ids):
        """ delete_module_list(module_ids: [int]) -> [version id]
        Delete multiple modules from the current pipeline
        
        """
        action = self.create_module_list_deletion_action(self.current_pipeline,
                                                         module_ids)
        return action

    def move_module_list(self, move_list):
        """ move_module_list(move_list: [(id,x,y)]) -> [version id]        
        Move all modules to a new location. No flushMoveActions is
        allowed to to emit to avoid recursive actions
        
        """
        action_list = []
        for (id, x, y) in move_list:
            module = self.current_pipeline.get_module_by_id(id)
            loc_id = self.vistrail.idScope.getNewId(Location.vtType)
            location = Location(id=loc_id,
                                x=x, 
                                y=y,
                                )
            if module.location and module.location.id != -1:
                old_location = module.location
                action_list.append(('change', old_location, location,
                                    module.vtType, module.id))
            else:
                # probably should be an error
                action_list.append(('add', location, module.vtType, module.id))
        action = core.db.action.create_action(action_list)
        self.add_new_action(action)
        return self.perform_action(action)

    @vt_action
    def add_connection_action(self, connection):
        action = core.db.action.create_action([('add', connection)])
        return action

    def add_connection(self, output_id, output_port_spec, 
                       input_id, input_port_spec):
        """ add_connection(output_id: long,
                           output_port_spec: PortSpec | str,
                           input_id: long,
                           input_port_spec: PortSpec | str) -> Connection
        Add a new connection into Vistrail
        
        """
        connection = \
            self.create_connection_from_ids(output_id, output_port_spec, 
                                            input_id, input_port_spec)
        action = self.add_connection_action(connection)
        return connection
    
    def delete_connection(self, id):
        """ delete_connection(id: int) -> version id
        Delete a connection with id 'id'
        
        """
        return self.delete_connection_list([id])

    @vt_action
    def delete_connection_list(self, connect_ids):
        """ delete_connection_list(connect_ids: list) -> version id
        Delete a list of connections
        
        """
        action_list = []
        for c_id in connect_ids:
            action_list.append(('delete', 
                                self.current_pipeline.connections[c_id]))
        action = core.db.action.create_action(action_list)
        return action

    @vt_action
    def add_function_action(self, module, function):
        action = core.db.action.create_action([('add', function, 
                                                module.vtType, module.id)])
        return action

    def add_function(self, module, function_name):
        function = self.create_function(module, function_name)
        action = self.add_function_action(module, function)
        return function

    @vt_action
    def update_function(self, module, function_name, param_values, old_id=-1L,
                        aliases=[], query_methods=[], should_replace=True):
        op_list = self.update_function_ops(module, function_name, param_values,
                                           old_id, aliases=aliases,
                                           query_methods=query_methods,
                                           should_replace=should_replace)
        action = core.db.action.create_action(op_list)
        return action

    @vt_action
    def update_parameter(self, function, old_param_id, new_value):
        old_param = function.parameter_idx[old_param_id]
        new_param = self.create_updated_parameter(old_param, new_value)
        if new_param is None:
            return None
        op = ('change', old_param, new_param, 
              function.vtType, function.real_id)
        action = core.db.action.create_action([op])
        return action

    @vt_action
    def delete_method(self, function_pos, module_id):
        """ delete_method(function_pos: int, module_id: int) -> version id
        Delete a method with function_pos from module module_id

        """

        module = self.current_pipeline.get_module_by_id(module_id)
        function = module.functions[function_pos]
        action = core.db.action.create_action([('delete', function,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def delete_function(self, real_id, module_id):
        module = self.current_pipeline.get_module_by_id(module_id)
        function = module.get_function_by_real_id(real_id)
        action = core.db.action.create_action([('delete', function,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def delete_annotation(self, key, module_id):
        """ delete_annotation(key: str, module_id: long) -> version_id
        Deletes an annotation from a module
        
        """
        module = self.current_pipeline.get_module_by_id(module_id)
        annotation = module.get_annotation_by_key(key)
        action = core.db.action.create_action([('delete', annotation,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def add_annotation(self, pair, module_id):
        """ add_annotation(pair: (str, str), moduleId: int)        
        Add/Update a key/value pair annotation into the module of
        moduleId
        
        """
        assert type(pair[0]) == type('')
        assert type(pair[1]) == type('')
        if pair[0].strip()=='':
            return

        module = self.current_pipeline.get_module_by_id(module_id)
        a_id = self.vistrail.idScope.getNewId(Annotation.vtType)
        annotation = Annotation(id=a_id,
                                key=pair[0], 
                                value=pair[1],
                                )
        if module.has_annotation_with_key(pair[0]):
            old_annotation = module.get_annotation_by_key(pair[0])
            action = \
                core.db.action.create_action([('change', old_annotation,
                                                   annotation,
                                                   module.vtType, module.id)])
        else:
            action = core.db.action.create_action([('add', annotation,
                                                        module.vtType, 
                                                        module.id)])
        return action

    def update_functions_ops_from_ids(self, module_id, functions):
        module = self.current_pipeline.modules[module_id]
        return self.update_functions_ops(module, functions)

    def update_port_spec_ops_from_ids(self, module_id, deleted_ports, 
                                      added_ports):
        module = self.current_pipeline.modules[module_id]
        return self.update_port_spec_ops(module, deleted_ports, added_ports)

    @vt_action
    def update_functions(self, module, functions):
        op_list = self.update_functions_ops(module, functions)
        if len(op_list) > 0:
            action = core.db.action.create_action(op_list)
        else:
            action = None
        return action

    @vt_action
    def update_ports_and_functions(self, module_id, deleted_ports, added_ports,
                                   functions):
        op_list = self.update_port_spec_ops_from_ids(module_id, deleted_ports, 
                                                     added_ports)
        op_list.extend(self.update_functions_ops_from_ids(module_id, functions))
        action = core.db.action.create_action(op_list)
        return action

    @vt_action
    def update_ports(self, module_id, deleted_ports, added_ports):
        op_list = self.update_port_spec_ops_from_ids(module_id, deleted_ports, 
                                                     added_ports)
        action = core.db.action.create_action(op_list)
        return action

    def has_module_port(self, module_id, port_tuple):
        """ has_module_port(module_id: int, port_tuple: (str, str)): bool
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName)

        Returns true if there exists a module port in this module with given params

        """
        (type, name) = port_tuple
        module = self.current_pipeline.get_module_by_id(module_id)
        return len([x for x in module.db_portSpecs
                    if x.name == name and x.type == type]) > 0

    @vt_action
    def add_module_port(self, module_id, port_tuple):
        """ add_module_port(module_id: int, port_tuple: (str, str, list)
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName, portSpec)
        
        """
        module = self.current_pipeline.get_module_by_id(module_id)
        p_id = self.vistrail.idScope.getNewId(PortSpec.vtType)
        port_spec = PortSpec(id=p_id,
                             type=port_tuple[0],
                             name=port_tuple[1],
                             sigstring=port_tuple[2],
                             )
        action = core.db.action.create_action([('add', port_spec,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def delete_module_port(self, module_id, port_tuple):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        - port_tuple : (portType, portName, portSpec)
        
        """
        spec_id = -1
        module = self.current_pipeline.get_module_by_id(module_id)
        port_spec = module.get_portSpec_by_name((port_tuple[1], port_tuple[0]))
        action_list = [('delete', port_spec, module.vtType, module.id)]
        for function in module.functions:
            if function.name == port_spec.name:
                action_list.append(('delete', function, 
                                    module.vtType, module.id))
        action = core.db.action.create_action(action_list)
        return action

    def create_group(self, module_ids, connection_ids):
        self.flush_delayed_actions()
        (group, connections) = \
            self.build_group(self.current_pipeline, 
                             module_ids, connection_ids)
        op_list = []
        op_list.extend(('delete', self.current_pipeline.connections[c_id])
                       for c_id in connection_ids)
        op_list.extend(('delete', self.current_pipeline.modules[m_id]) 
                       for m_id in module_ids)
        op_list.append(('add', group))
        op_list.extend(('add', c) for c in connections)
        action = core.db.action.create_action(op_list)
        self.add_new_action(action)
#         for op in action.operations:
#             print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        result = self.perform_action(action)
        return group
    
    def create_abstraction(self, module_ids, connection_ids, name):
        self.flush_delayed_actions()
        (abstraction, connections) = \
            self.build_abstraction(self.current_pipeline, 
                                   module_ids, connection_ids, name)
        op_list = []
        op_list.extend(('delete', self.current_pipeline.connections[c_id])
                       for c_id in connection_ids)
        op_list.extend(('delete', self.current_pipeline.modules[m_id]) 
                       for m_id in module_ids)
        op_list.append(('add', abstraction))
        op_list.extend(('add', c) for c in connections)
        action = core.db.action.create_action(op_list)
        self.add_new_action(action)
        result = self.perform_action(action)
        return abstraction

    def create_abstractions_from_groups(self, group_ids):
        for group_id in group_ids:
            self.create_abstraction_from_group(group_id)

    def create_abstraction_from_group(self, group_id, name=""):
        self.flush_delayed_actions()
        name = self.get_abstraction_name(name)
        
        (abstraction, connections) = \
            self.build_abstraction_from_group(self.current_pipeline, 
                                              group_id, name)

        op_list = []
        getter = self.get_connections_to_and_from
        op_list.extend(('delete', c)
                       for c in getter(self.current_pipeline, [group_id]))
        op_list.append(('delete', self.current_pipeline.modules[group_id]))
        op_list.append(('add', abstraction))
        op_list.extend(('add', c) for c in connections)
        action = core.db.action.create_action(op_list)
        self.add_new_action(action)
        result = self.perform_action(action)
        return abstraction


    def ungroup_set(self, module_ids):
        self.flush_delayed_actions()
        for m_id in module_ids:
            self.create_ungroup(m_id)

    def create_ungroup(self, module_id):
        (modules, connections) = \
            self.build_ungroup(self.current_pipeline, module_id)
        pipeline = self.current_pipeline
        old_conn_ids = self.get_module_connection_ids([module_id], 
                                                      pipeline.graph)
        op_list = []
        op_list.extend(('delete', pipeline.connections[c_id]) 
                       for c_id in old_conn_ids)
        op_list.append(('delete', pipeline.modules[module_id]))
        op_list.extend(('add', m) for m in modules)
        op_list.extend(('add', c) for c in connections)
        action = core.db.action.create_action(op_list)
        self.add_new_action(action)
        res = self.perform_action(action)
        self.validate(self.current_pipeline, False)
        return res



    ##########################################################################
    # Methods to access/find pipeline information
    
    def get_connections_to(self, pipeline, module_ids, port_name=None):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_to(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids
                if port_name is None or \
                    pipeline.connections[c_id].destination.name == port_name]

    def get_connections_from(self, pipeline, module_ids, port_name=None):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_from(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids
                if port_name is None or \
                    pipeline.connections[c_id].source.name == port_name]

    def get_connections_to_and_from(self, pipeline, module_ids):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_from(m_id):
                connection_ids.add(id)
            for _, id in graph.edges_to(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids]
        
    ##########################################################################
    # Grouping/abstraction

    def get_avg_location(self, modules):
        if len(modules) < 1:
            return (0.0, 0.0)

        sum_x = 0.0
        sum_y = 0.0
        for module in modules:
            sum_x += module.location.x
            sum_y += module.location.y
        return (sum_x / len(modules), sum_y / len(modules))

    def translate_modules(self, modules, x, y):
        for module in modules:
            module.location.x -= x
            module.location.y -= y

    def center_modules(self, modules):
        (avg_x, avg_y) = self.get_avg_location(modules)
        self.translate_modules(modules, avg_x, avg_y)

    @staticmethod
    def get_neighbors(pipeline, module, upstream=True):
#         for i, m in pipeline.modules.iteritems():
#             print i, m.name
#         for j, c in pipeline.connections.iteritems():
#             print j, c.source.moduleId, c.destination.moduleId

        neighbors = []
        if upstream:
            get_edges = pipeline.graph.edges_to
            get_port_name = \
                lambda x: pipeline.connections[x].source.name
        else:
            get_edges = pipeline.graph.edges_from
            get_port_name = \
                lambda x: pipeline.connections[x].destination.name
        for (m_id, conn_id) in get_edges(module.id):
            neighbors.append((pipeline.modules[m_id], get_port_name(conn_id)))
        return neighbors

    @staticmethod
    def get_upstream_neighbors(pipeline, module):
        return VistrailController.get_neighbors(pipeline, module, True)
    @staticmethod
    def get_downstream_neighbors(pipeline, module):
        return VistrailController.get_neighbors(pipeline, module, False)

    def check_subpipeline_port_names(self):
        def create_name(base_name, names):
            if base_name in names:
                port_name = base_name + '_' + str(names[base_name])
                names[base_name] += 1
            else:
                port_name = base_name
                names[base_name] = 2
            return port_name

        in_names = {}
        out_names = {}
        in_cur_names = []
        out_cur_names = []
        in_process_list = []
        out_process_list = []
        pipeline = self.current_pipeline
        for m in pipeline.module_list:
            if m.package == basic_pkg and (m.name == 'InputPort' or
                                           m.name == 'OutputPort'):
                if m.name == 'InputPort':
                    neighbors = self.get_downstream_neighbors(pipeline, m)
                    names = in_names
                    cur_names = in_cur_names
                    process_list = in_process_list
                elif m.name == 'OutputPort':
                    neighbors = self.get_upstream_neighbors(pipeline, m)
                    names = out_names
                    cur_names = out_cur_names
                    
                if len(neighbors) < 1:
                    # print "not adding, no neighbors"
                    # don't add it!
                    continue

                name_function = None
                base_name = None
                for function in m.functions:
                    if function.name == 'name':
                        name_function = function
                        if len(function.params) > 0:
                            base_name = function.params[0].strValue
                if base_name is not None:
                    cur_names.append(base_name)
                else:
                    base_name = neighbors[0][1]
                    if base_name == 'self':
                        base_name = neighbors[0][0].name
                    process_list.append((m, base_name))

        op_list = []
        for (port_type, names, cur_names, process_list) in \
                [("input", in_names, in_cur_names, in_process_list), \
                     ("output", out_names, out_cur_names, out_process_list)]:
            cur_names.sort()
            last_name = None
            for name in cur_names:
                if name == last_name:
                    msg = 'Cannot assign the name "%s" to more ' \
                        'than one %s port' % (name, port_type)
                    raise Exception(msg)
                last_name = name
                idx = name.rfind("_")
                if idx < 0:
                    names[name] = 2
                else:
                    base_name = None
                    try:
                        val = int(name[idx+1:])
                        base_name = name[:idx]
                    except ValueError:
                        pass
                    if base_name is not None and base_name in names:
                        cur_val = names[base_name]
                        if val >= cur_val:
                            names[base_name] = val + 1
                    else:
                        names[name] = 2

            for (m, base_name) in process_list:
                port_name = create_name(base_name, names)
                # FIXME use update_function when it is moved to
                # core (see core_no_gui branch)
                ops = self.update_function_ops(m, 'name', 
                                               [port_name])
                op_list.extend(ops)
        self.flush_delayed_actions()
        action = core.db.action.create_action(op_list)
        if action is not None:
            self.add_new_action(action)
            self.perform_action(action)
        return action

    def create_subpipeline(self, full_pipeline, module_ids, connection_ids, 
                           id_remap, id_scope=None):
        if not id_scope:
            id_scope = IdScope(1, {Group.vtType: Module.vtType,
                                   Abstraction.vtType: Module.vtType})
        old_id_scope = self.id_scope
        self.set_id_scope(id_scope)
        
        connections = [full_pipeline.connections[c_id] 
                       for c_id in connection_ids]

        pipeline = Pipeline()
        pipeline.id = None # get rid of id so that sql saves correctly

        in_names = {}
        out_names = {}
        def create_name(base_name, names):
            if base_name in names:
                port_name = base_name + '_' + str(names[base_name])
                names[base_name] += 1
            else:
                port_name = base_name
                names[base_name] = 2
            return port_name

        for m in full_pipeline.module_list:
            if m.id not in module_ids:
                continue
            if m.package == basic_pkg and (m.name == 'InputPort' or
                                           m.name == 'OutputPort'):
                if m.name == 'InputPort':
                    neighbors = self.get_downstream_neighbors(full_pipeline, m)
                    names = in_names
                elif m.name == 'OutputPort':
                    neighbors = self.get_upstream_neighbors(full_pipeline, m)
                    names = out_names
                if len(neighbors) < 1:
                    # print "not adding, no neighbors"
                    # don't add it!
                    continue

                m = m.do_copy(True, id_scope, id_remap)
                name_function = None
                for function in m.functions:
                    if function.name == 'name':
                        name_function = function
                        base_name = function.params[0].strValue
                if name_function is None:
                    base_name = neighbors[0][1]
                if base_name == 'self':
                    base_name = neighbors[0][0].name
                port_name = create_name(base_name, names)
                if name_function is not None:
                    name_function.params[0].strValue = port_name
                else:
                    functions = [('name', [port_name])]
                    for f in self.create_functions(m, functions):
                        m.add_function(f)
                pipeline.add_module(m)
            else:
                pipeline.add_module(m.do_copy(True, id_scope, id_remap))

        # translate group to center
        (avg_x, avg_y) = self.get_avg_location(pipeline.module_list)
        self.translate_modules(pipeline.module_list, avg_x, avg_y)
        module_index = dict([(m.id, m) for m in pipeline.module_list])

        def create_port(port_type, other_port, other_module, old_module, names):
            x = old_module.location.x
            y = old_module.location.y
            module_name = port_type.capitalize() + 'Port'
            base_name = other_port.name
            if base_name == 'self':
                base_name = other_module.name
            port_name = create_name(base_name, names)
            module = self.create_module(basic_pkg, module_name, '', 
                                        x - avg_x, y - avg_y)
            functions = [('name', [port_name])]
            for f in self.create_functions(module, functions):
                module.add_function(f)
            
            return (module, 'InternalPipe', port_name)

        def add_to_pipeline(port_type, port, other_port, names):
            old_module = full_pipeline.modules[port.moduleId]
            old_port_name = port.name
            port_name = other_port.name
            module_id = id_remap[(Module.vtType, other_port.moduleId)]
            module = module_index[module_id]
            key = (module_id, port_name, port_type)
            if key in existing_ports:
                (new_module, new_port, new_name) = existing_ports[key]
            else:
                (new_module, new_port, new_name) = \
                    create_port(port_type, other_port, module, 
                                old_module, names)
                existing_ports[key] = (new_module, new_port, new_name)
                pipeline.add_module(new_module)
                if port_type == 'input':
                    # print "output:", new_module.name, new_module.id, new_name
                    # print "input:", module.name, module.id, port_name
                    new_conn = self.create_connection(new_module, new_port,
                                                      module, port_name)
                elif port_type == 'output':
                    # print "output:", module.name, module.id, port_name  
                    # print "input:", new_module.name, new_module.id, new_name
                    new_conn = self.create_connection(module, port_name,
                                                      new_module, new_port)
                else:
                    raise VistrailsInternalError("port_type incorrect")
                pipeline.add_connection(new_conn)
            return (old_module, old_port_name, new_name)
            

        outside_connections = []
        existing_ports = {}
        for connection in connections:
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if not (Module.vtType, port.moduleId) in id_remap:
                    all_inside = False
                else:
                    all_outside = False

            # if a connection has an "external" connection, we need to
            # create an input port or output port module
            if all_inside:
                pipeline.add_connection(connection.do_copy(True, id_scope,
                                                           id_remap))
            else:
                old_in_module = None
                old_out_module = None
                if (Module.vtType, connection.source.moduleId) not in id_remap:
                    (old_out_module, old_out_port, old_in_port) = \
                        add_to_pipeline('input', connection.source, 
                                        connection.destination, in_names)
                elif (Module.vtType, connection.destination.moduleId) \
                        not in id_remap:
                    (old_in_module, old_in_port, old_out_port) = \
                        add_to_pipeline('output', connection.destination, 
                                        connection.source, out_names)
                outside_connections.append((old_out_module, old_out_port,
                                            old_in_module, old_in_port))

        self.set_id_scope(old_id_scope)
        return (pipeline, outside_connections)

    def get_connections_to_subpipeline(self, module, partial_connections):
        connections = []
        for (out_module, out_port, in_module, in_port) in partial_connections:
            if out_module is None:
                out_module = module
            if in_module is None:
                in_module = module
            connections.append(self.create_connection(out_module, out_port,
                                                      in_module, in_port))
        return connections

    def build_group(self, full_pipeline, module_ids, connection_ids):
        id_remap = {}
        (pipeline, outside_connections) = \
            self.create_subpipeline(full_pipeline, module_ids, connection_ids,
                                    id_remap)

        # now group to vistrail
        (avg_x, avg_y) = self.get_avg_location([full_pipeline.modules[m_id]
                                                for m_id in module_ids])
        group = self.create_module(basic_pkg, 'Group', '', avg_x, avg_y)
        group.pipeline = pipeline

        connections = \
            self.get_connections_to_subpipeline(group, outside_connections)

        return (group, connections)

    def build_abstraction(self, full_pipeline, module_ids, 
                          connection_ids, name):
        id_remap = {}
        (pipeline, outside_connections) = \
            self.create_subpipeline(full_pipeline, module_ids, connection_ids, 
                                    id_remap)
        
        # save vistrail
        abs_vistrail = self.create_vistrail_from_pipeline(pipeline)
        abs_vistrail.name = name
        abs_vistrail.change_description("Copied from pipeline", 1L)
        abs_fname = self.save_abstraction(abs_vistrail)

        # need to late enable stuff on the abstraction_pkg package
        self.add_abstraction_to_registry(abs_vistrail, abs_fname, name, 
                                         None, "1")
        namespace = get_cur_abs_namespace(abs_vistrail)
        (avg_x, avg_y) = self.get_avg_location([full_pipeline.modules[m_id]
                                                for m_id in module_ids])
        abstraction = self.create_module(abstraction_pkg, name, namespace, 
                                         avg_x, avg_y, 1L)
        connections = self.get_connections_to_subpipeline(abstraction, 
                                                          outside_connections)
        return (abstraction, connections)

    def build_abstraction_from_group(self, full_pipeline, group_id, name):
        if name is None:
            return
        group = self.current_pipeline.modules[group_id]
        abs_vistrail = self.create_vistrail_from_pipeline(group.pipeline)
        abs_vistrail.name = name
        abs_vistrail.change_description("Created from group", 1L)
        abs_fname = self.save_abstraction(abs_vistrail)

        group_connections = self.get_connections_to_and_from(full_pipeline,
                                                             [group_id])
        outside_connections = []
        for c in group_connections:
            out_module = full_pipeline.modules[c.source.moduleId]
            out_port = c.source.name
            in_module = full_pipeline.modules[c.destination.moduleId]
            in_port = c.destination.name
            if c.source.moduleId == group_id:
                out_module = None
            if c.destination.moduleId == group.id:
                in_module = None
            outside_connections.append((out_module, out_port, 
                                        in_module, in_port))

        # need to late enable stuff on the 'local.abstractions' package
        self.add_abstraction_to_registry(abs_vistrail, abs_fname, name,
                                         None, "1")
        namespace = get_cur_abs_namespace(abs_vistrail)
        abstraction = self.create_module(abstraction_pkg, name, namespace, 
                                         group.location.x, group.location.y, 
                                         1L)
        connections = self.get_connections_to_subpipeline(abstraction, 
                                                          outside_connections)
        return (abstraction, connections)

    def create_vistrail_from_pipeline(self, pipeline):
        abs_vistrail = Vistrail()
        
        id_remap = {}
        action = core.db.action.create_paste_action(pipeline, 
                                                    abs_vistrail.idScope,
                                                    id_remap)
        abs_vistrail.add_action(action, 0L, 0)
        return abs_vistrail
        
    def get_abstraction_dir(self):
        conf = get_vistrails_configuration()
        if conf.check('abstractionsDirectory'):
            abstraction_dir = conf.abstractionsDirectory
            if not os.path.exists(abstraction_dir):
                raise VistrailsInternalError("Cannot find %s" % \
                                                 abstraction_dir)
            return abstraction_dir
        else:
            raise VistrailsInternalError("'abstractionsDirectory' not"
                                         " specified in configuration")
        return None

    def get_abstraction_desc(self, package, name, namespace, module_version=None):
        reg = core.modules.module_registry.get_module_registry()
        if reg.has_descriptor_with_name(package, name, namespace,
                                        None, module_version):
            return reg.get_descriptor_by_name(package, name,
                                              namespace, None, module_version)
        return None

    def parse_abstraction_name(self, filename, get_all_parts=False):
        # assume only 1 possible prefix or suffix
        import re
        prefixes = ["abstraction_"]
        suffixes = [".vt", ".xml"]
        path, fname = os.path.split(filename)
        hexpat = '[a-fA-F0-9]'
        uuidpat = hexpat + '{8}-' + hexpat + '{4}-' + hexpat + '{4}-' + hexpat + '{4}-' + hexpat + '{12}'
        prepat = '|'.join(prefixes).replace('.','\\.')
        sufpat = '|'.join(suffixes).replace('.','\\.')
        pattern = re.compile("(" + prepat + ")?(.+?)(\(" + uuidpat + "\))?(" + sufpat + ")", re.DOTALL)
        matchobj = pattern.match(fname)
        prefix, absname, uuid, suffix = [matchobj.group(x) or '' for x in xrange(1,5)]
        if get_all_parts:
            return (path, prefix, absname, uuid[1:-1], suffix)
        return absname

    def add_abstraction_to_registry(self, abs_vistrail, abs_fname, name, 
                                    namespace=None, module_version=None,
                                    is_global=True, avail_fnames=[]):
        reg = core.modules.module_registry.get_module_registry()
        cur_namespace = get_cur_abs_namespace(abs_vistrail)
        if namespace is None:
            namespace = cur_namespace
        if module_version is None:
            module_version = -1L

        self.ensure_abstractions_loaded(abs_vistrail, avail_fnames)
        try:
            abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                          long(module_version))
        except InvalidPipeline, e:
            # handle_invalid_pipeline will raise it's own InvalidPipeline
            # exception if it fails
            vistrail_id_scope = self.id_scope
            self.id_scope = abs_vistrail.idScope
            (new_version, new_pipeline) = \
                self.handle_invalid_pipeline(e, long(module_version), \
                                                 abs_vistrail, False)
            save_abstraction(abs_vistrail, abs_fname)
            self.set_changed(True)
            self.id_scope = vistrail_id_scope
            abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                          new_version, new_pipeline)
            module_version = str(new_version)

        all_namespaces = get_all_abs_namespaces(abs_vistrail)

        old_desc = None
        for ns in all_namespaces:
            try:
                desc = reg.get_similar_descriptor(abstraction_pkg,
                                                  name,
                                                  ns)
                if not desc.is_hidden:
                    old_desc = desc
                    # print "found old_desc", old_desc.name, old_desc.version
                    break
            except ModuleRegistryException, e:
                pass
            
        global_hide = not is_global or old_desc is not None
        newest_desc = None
        requested_desc = None
        for ns in all_namespaces:
            hide_descriptor = (ns != cur_namespace) or global_hide
            # print '()()() adding abstraction', namespace
            if reg.has_descriptor_with_name(abstraction_pkg, 
                                            name, 
                                            ns,
                                            abstraction_ver, 
                                            str(module_version)):
                # don't add something twice
                continue
            new_desc = reg.auto_add_module((abstraction, 
                                            {'package': abstraction_pkg,
                                             'package_version': abstraction_ver,
                                             'namespace': ns,
                                             'version': str(module_version),
                                             'hide_namespace': True,
                                             'hide_descriptor': hide_descriptor,
                                             }))
            if ns == cur_namespace:
                newest_desc = new_desc
            if ns == namespace:
                requested_desc = new_desc
            reg.auto_add_ports(abstraction)
        if old_desc is not None:
            # print '$$$ calling update_module'
            reg.update_module(old_desc, newest_desc)
        return requested_desc

#         package = reg.get_package_by_name(abstraction_pkg)
#         for desc in package.descriptor_versions.itervalues():
#             print desc.package, desc.name, desc.namespace, desc.version

    def abstraction_exists(self, name):
        # FIXME need to check directory in case abstraction was not
        # loaded due to dependencies.
        # FIXME, also need to check this for groups, probably
        abstraction_dir = self.get_abstraction_dir()
        vt_fname = os.path.join(abstraction_dir, name + '.xml')
        return os.path.exists(vt_fname)

    def load_abstraction(self, abs_fname, is_global=True, abs_name=None,
                         module_version=None, avail_fnames=[]):
        if abs_name is None:
            abs_name = self.parse_abstraction_name(abs_fname)
        if abs_fname in self._loaded_abstractions:
            abs_vistrail = self._loaded_abstractions[abs_fname]
        else:
            abs_vistrail = read_vistrail(abs_fname)
            self._loaded_abstractions[abs_fname] = abs_vistrail
        
        # print "LOAD_VT NAMESPACES:", get_all_abs_namespaces(abs_vistrail)

        abstraction_uuid = get_cur_abs_namespace(abs_vistrail)
        if abstraction_uuid is None:
            # No current uuid exists - generate one
            abstraction_uuid = str(uuid.uuid1())
            abs_vistrail.set_annotation('__abstraction_uuid__', abstraction_uuid)
        origin_uuid = abs_vistrail.get_annotation('__abstraction_origin_uuid__')
        if origin_uuid is None:
            # No origin uuid exists - set to current uuid (for backwards compatibility)
            origin_uuid = abstraction_uuid
            abs_vistrail.set_annotation('__abstraction_origin_uuid__', origin_uuid)
        else:
            origin_uuid = origin_uuid.value
            
        if module_version is None:
            module_version = str(abs_vistrail.get_latest_version())
        elif type(module_version) == type(1):
            module_version = str(module_version)
        # If an upgraded version has already been created, we want to use that rather than loading the old version.
        # This step also avoid duplication of abstraction upgrades.  Otherwise, when we try to add the old version
        # to the registry, it raises an InvalidPipeline exception and automatically tries to handle it by creating
        # another upgrade for the old version.
        upgrade_version = abs_vistrail.get_upgrade(long(module_version))
        if upgrade_version is not None:
            old_version = module_version
            module_version = str(upgrade_version)
        
        desc = self.get_abstraction_desc(abstraction_pkg, abs_name, 
                                         abstraction_uuid, module_version)
        if desc is None:
            #print "adding version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "to registry"
            desc = self.add_abstraction_to_registry(abs_vistrail, abs_fname, 
                                                    abs_name, None, 
                                                    module_version, 
                                                    is_global, avail_fnames)
            #if desc.version != module_version:
                #print "upgraded version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "to version", desc.version, "and namespace", desc.namespace
#        else:
#            if upgrade_version is not None:
#                print "version", old_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "already in registry as upgraded version", module_version
#            else:
#                print "version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "already in registry"
        return desc
    
    def unload_abstractions(self):
        reg = core.modules.module_registry.get_module_registry()
        for abs_fname, abs_vistrail in self._loaded_abstractions.iteritems():
            abs_name = self.parse_abstraction_name(abs_fname)
            # FIXME? do we need to remove all versions (call
            # delete_module over and over?)
            for namespace in get_all_abs_namespaces(abs_vistrail):
                try:
                    reg.delete_module(abstraction_pkg, abs_name, namespace)
                except:
                    pass
        self._loaded_abstractions.clear()

        # for abs_fname, abs_vistrail in self._loaded_abstractions.iteritems():
        #     abs_desc_info = abs_vistrail.get_annotation('__abstraction_descriptor_info__')
        #     if abs_desc_info is not None:
        #         abs_desc_info = eval(abs_desc_info.value)
        #         # Don't unload package abstractions that have been
        #         # upgraded by this controller (during a manual version
        #         # upgrade) because that would also unload the version
        #         # in the module palette
        #         if abs_desc_info[2] == abs_vistrail.get_annotation('__abstraction_uuid__').value:
        #             continue
        #     abs_name = self.parse_abstraction_name(abs_fname)
        #     abs_namespace = abs_vistrail.get_annotation('__abstraction_uuid__').value
        #     try:
        #         descriptor = self.get_abstraction_descriptor(abs_name, abs_namespace)
        #         print "removing all versions of", abs_name, "from registry (namespace: %s)"%abs_namespace
        #         while descriptor is not None:
        #             reg = core.modules.module_registry.get_module_registry()
        #             reg.delete_module(abstraction_pkg, abs_name, abs_namespace)
        #             descriptor = self.get_abstraction_descriptor(abs_name, abs_namespace)
        #     except:
        #         # No versions of the abstraction exist in the registry now
        #         pass
        # self._loaded_abstractions.clear()

#    def update_abstraction(self, abstraction, new_actions):
#        module_version = abstraction.internal_version
#        if type(module_version) == type(""):
#            module_version = int(module_version)
#        abstraction_uuid = \
#            abstraction.vistrail.get_annotation('__abstraction_uuid__').value
#        upgrade_action = self.create_upgrade_action(new_actions) 
#        
#        a = (abstraction.vistrail, 
#             module_version)
#        
#        desc = self.get_abstraction_desc(abstraction.name, abstraction_uuid,
#                                         new_version)
#        if desc is None:
#            # desc = self.add_abstraction_to_registry(abstraction.vistrail,
#            # abstraction.
#            pass
#        # FIXME finish this!
                                         
                                         
        

    def manage_package_names(self, vistrail, package):
        vistrail = copy.copy(vistrail)
        dependencies = []
        for action in vistrail.actions:
            for operation in action.operations:
                if (operation.vtType == 'add' or 
                    operation.vtType == 'change'):
                    if (operation.what == 'abstraction' and 
                        operation.data.package == abstraction_pkg):
                        operation.data.package = package
                    elif (operation.what == 'abstraction' or
                          operation.what == 'module' or
                          operation.what == 'group'):
                        dependencies.append(operation.data.package)
                    
        return (vistrail, dependencies)

    def save_abstraction(self, vistrail, name=None, package=None, 
                         save_dir=None, overwrite=False):
        if (package is None) != (save_dir is None):
            raise VistrailsInternalError("Must set both package and "
                                         "save_dir or neither")
        if name is None:
            name = vistrail.name

        if package is None and self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction with name '%s' already "
                                         "exists" % name)
        
        # Set uuid's (this is somewhat tricky because of backwards
        # compatibility - there was originally only
        # '__abstraction_uuid__' and no origin, so we have to handle
        # cases where a uuid is set, but hasn't been set as the origin
        # yet).
        new_uuid = str(uuid.uuid1())
        if vistrail.get_annotation('__abstraction_origin_uuid__') is None:
            # No origin uuid exists
            current_uuid = vistrail.get_annotation('__abstraction_uuid__')
            if current_uuid is None:
                # No current uuid exists - generate one and use it as
                # origin and current uuid
                vistrail.set_annotation('__abstraction_origin_uuid__', new_uuid)
                # vistrail.set_annotation('__abstraction_uuid__', new_uuid)
            else:
                # A current uuid exists - set it as origin and
                # generate a new current uuid
                vistrail.set_annotation('__abstraction_origin_uuid__', 
                                        current_uuid.value)
                # vistrail.set_annotation('__abstraction_uuid__', str(uuid.uuid1()))
        # else:
        #     # Origin uuid exists - just generate a new current uuid
        #     vistrail.set_annotation('__abstraction_uuid__', str(uuid.uuid1()))
        annotation_key = get_next_abs_annotation_key(vistrail)
        vistrail.set_annotation(annotation_key, new_uuid)

        if save_dir is None:
            save_dir = self.get_abstraction_dir()
        vt_fname = os.path.join(save_dir, name + '.xml')
        if not overwrite and os.path.exists(vt_fname):
            raise VistrailsInternalError("'%s' already exists" % \
                                             vt_fname)
        core.db.io.save_vistrail_to_xml(vistrail, vt_fname)
        return vt_fname

    def upgrade_abstraction_module(self, module_id, test_only=False):
        """upgrade_abstraction_module(module_id, test_only) -> None or
        (preserved: bool, missing_ports: list)

        If test_only is False, attempts to automatically upgrade an
        abstraction by adding a new abstraction with the current package
        version, and recreates all connections and functions.  If any
        of the ports/functions used are not available, they are not
        reconnected/readded to the new abstraction.
        
        If test_only is True, (preserved: bool, missing_ports: list)
        is returned, where 'preserved' is a boolean that is True
        if the abstraction can be replaced with all functions and
        connections preserved.  If 'preserved' is True, then
        'missing_ports' is an empty list, otherwise it contains a
        list of tuples (port_type: str, port_name: str) of all
        ports that have been removed.
        
        """
        # get the new descriptor first
        invalid_module = self.current_pipeline.modules[module_id]
        # make sure that we don't get an obselete descriptor
        invalid_module._module_descriptor = None
        abs_fname = invalid_module.module_descriptor.module.vt_fname
        #print "&&& abs_fname", abs_fname
        (path, prefix, abs_name, abs_namespace, suffix) = \
            self.parse_abstraction_name(abs_fname, True)
        # abs_vistrail = invalid_module.vistrail
        abs_vistrail = read_vistrail(abs_fname)
        abs_namespace = get_cur_abs_namespace(abs_vistrail)
        lookup = {(abs_name, abs_namespace): abs_fname}
        descriptor_info = invalid_module.descriptor_info
        newest_version = str(abs_vistrail.get_latest_version())
        #print '&&& check_abstraction', abs_namespace, newest_version
        d = self.check_abstraction((descriptor_info[0],
                                    descriptor_info[1],
                                    abs_namespace,
                                    descriptor_info[3],
                                    newest_version),
                                   lookup)

        failed = True
        src_ports_gone = {}
        dst_ports_gone = {}
        fns_gone = {}
        missing_ports = []
        check_upgrade = UpgradeWorkflowHandler.check_upgrade
        while failed:
            try:
                check_upgrade(self.current_pipeline, module_id, d, 
                              function_remap=fns_gone, 
                              src_port_remap=src_ports_gone, 
                              dst_port_remap=dst_ports_gone)
                if test_only:
                    return (len(missing_ports) == 0, missing_ports)
                failed = False
            except UpgradeWorkflowError, e:
                if test_only:
                    missing_ports.append((e._port_type, e._port_name))
                if e._module is None or e._port_type is None or \
                        e._port_name is None:
                    raise e
                # Remove the offending connection/function by remapping to None
                if e._port_type == 'output':
                    src_ports_gone[e._port_name] = None
                elif e._port_type == 'input':
                    dst_ports_gone[e._port_name] = None
                    fns_gone[e._port_name] = None
                else:
                    raise e
        upgrade_action = \
            UpgradeWorkflowHandler.replace_module(self, self.current_pipeline,
                                                  module_id, d, 
                                                  fns_gone,
                                                  src_ports_gone,
                                                  dst_ports_gone)[0]
        self.flush_delayed_actions()
        self.add_new_action(upgrade_action)
        self.perform_action(upgrade_action)
        self.vistrail.change_description("Upgrade Subworkflow", 
                                         self.current_version)

    def get_abstraction_descriptor(self, name, namespace=None):
        reg = core.modules.module_registry.get_module_registry()
        return reg.get_descriptor_by_name(abstraction_pkg, name, namespace)

#     def load_abstraction(self, abs_fname, abs_name=None):
#         if abs_name is None:
#             abs_name = os.path.basename(abs_fname)[12:-4]
#         abs_vistrail = read_vistrail(abs_fname)
#         abstraction_uuid = \
#             abs_vistrail.get_annotation('__abstraction_uuid__').value
#         if self.abstraction_exists(abs_name):
#             descriptor = self.get_abstraction_descriptor(abs_name)
#             if descriptor.module.uuid == abstraction_uuid:
#                 return
#         if self.abstraction_exists(abs_name, abstraction_uuid):
#             descriptor = \
#                 self.get_abstraction_descriptor(abs_name, abstraction_uuid)
#             descriptor._abstraction_refs += 1
#             # print 'load ref_count:', descriptor.abstraction_refs
#             return
            
#         self.add_abstraction(abs_vistrail, abs_fname, abs_name, 
#                              abstraction_uuid)
            
#    def unload_abstraction(self, name, namespace):
#        if self.abstraction_exists(name):
#            descriptor = self.get_abstraction_descriptor(name, namespace)
#            descriptor._abstraction_refs -= 1
#            # print 'unload ref_count:', descriptor.abstraction_refs
#            if descriptor._abstraction_refs < 1:
#                # unload abstraction
#                print "deleting module:", name, namespace
#                reg = core.modules.module_registry.get_module_registry()
#                reg.delete_module(abstraction_pkg, name, namespace)

    def import_abstraction(self, new_name, package, name, namespace, 
                           module_version=None):
        # copy from a local namespace to local.abstractions
        reg = core.modules.module_registry.get_module_registry()
        descriptor = self.get_abstraction_desc(package, name, namespace, str(module_version))
        if descriptor is None:
            # if not self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction %s|%s (package: %s) not on registry" %\
                                             (name, namespace, package))
        # FIXME have save_abstraction take abs_fname as argument and do
        # shutil copy
        # abs_fname = descriptor.module.vt_fname
        abs_vistrail = descriptor.module.vistrail
        # Strip the descriptor info annotation before saving so the imported version will be editable
        abs_desc_info = abs_vistrail.get_annotation('__abstraction_descriptor_info__')
        if abs_desc_info is not None:
            abs_vistrail.set_annotation('__abstraction_descriptor_info__', None)
        abs_fname = self.save_abstraction(abs_vistrail, new_name)
        # Duplicate the vistrail and set the uuid and descriptor annotation back on the original vistrail
        imported_vistrail = read_vistrail(abs_fname)
        annotation_key = get_next_abs_annotation_key(abs_vistrail)
        abs_vistrail.set_annotation(annotation_key, namespace)
        if abs_desc_info is not None:
            abs_vistrail.set_annotation('__abstraction_descriptor_info__', abs_desc_info.value)
        #if new_name == name and package == abstraction_pkg:
        #    reg.show_module(descriptor)
        #    descriptor.module.vt_fname = abs_fname
        #else:
        new_desc = self.add_abstraction_to_registry(imported_vistrail, abs_fname, new_name,
                                                    None, str(module_version))
        reg.show_module(new_desc)

    def export_abstraction(self, new_name, pkg_name, dir, package, name, namespace, 
                           module_version):
        descriptor = self.get_abstraction_desc(package, name, namespace, module_version)
        if descriptor is None:
            raise VistrailsInternalError("Abstraction %s|%s (package: %s) not on registry" %\
                                             (name, namespace, package))
        
        abs_vistrail = descriptor.module.vistrail
        (abs_vistrail, dependencies) = self.manage_package_names(abs_vistrail, 
                                                                 pkg_name)
        abs_fname = self.save_abstraction(abs_vistrail, new_name, pkg_name,
                                          dir)
        return (os.path.basename(abs_fname), dependencies)
    
    def find_abstractions(self, vistrail, recurse=False):
        abstractions = {}
        for action in vistrail.actions:
            for operation in action.operations:
                if operation.vtType == 'add' or \
                        operation.vtType == 'change':
                    if operation.data is not None and operation.data.vtType == Abstraction.vtType:
                        abstraction = operation.data
                        if abstraction.package == abstraction_pkg:
                            key = abstraction.descriptor_info
                            if key not in abstractions:
                                abstractions[key] = []
                            abstractions[key].append(abstraction)
        if recurse:
            for abstraction_list in abstractions.itervalues():
                for abstraction in abstraction_list:
                    try:
                        vistrail = abstraction.vistrail
                    except MissingPackageVersion, e:
                        reg = core.modules.module_registry.get_module_registry()
                        abstraction._module_descriptor = \
                            reg.get_similar_descriptor(*abstraction.descriptor_info)
                        vistrail = abstraction.vistrail
                    r_abstractions = self.find_abstractions(vistrail, recurse)
                    for k,v in r_abstractions.iteritems():
                        if k not in abstractions:
                            abstractions[k] = []
                        abstractions[k].extend(v)
        return abstractions

    def check_abstraction(self, descriptor_tuple, lookup):
        reg = core.modules.module_registry.get_module_registry()
        try:
            descriptor = reg.get_descriptor_by_name(*descriptor_tuple)
            if not os.path.exists(descriptor.module.vt_fname):
                # print "abstraction path doesn't exist"
                reg.delete_descriptor(descriptor)
                raise MissingModule(descriptor_tuple[0],
                                    descriptor_tuple[1],
                                    descriptor_tuple[2],
                                    descriptor_tuple[4])
            return descriptor
        except MissingPackageVersion, e:
            if descriptor_tuple[3] != '':
                new_desc = (descriptor_tuple[0],
                            descriptor_tuple[1],
                            descriptor_tuple[2],
                            '',
                            descriptor_tuple[4])
                return self.check_abstraction(new_desc, lookup)
            else:
                raise
        except MissingModuleVersion, e:
            if descriptor_tuple[4] != '':
                other_desc = reg.get_descriptor_by_name(descriptor_tuple[0],
                                                        descriptor_tuple[1],
                                                        descriptor_tuple[2],
                                                        descriptor_tuple[3],
                                                        '')
                new_desc = \
                    self.load_abstraction(other_desc.module.vt_fname, 
                                          False, descriptor_tuple[1],
                                          descriptor_tuple[4])
                descriptor_tuple = (new_desc.package, new_desc.name, 
                                    new_desc.namespace, new_desc.package_version,
                                    str(new_desc.version))
                return self.check_abstraction(descriptor_tuple, lookup)
            else:
                raise
        except MissingModule, e:
            if (descriptor_tuple[1], descriptor_tuple[2]) not in lookup:
                if (descriptor_tuple[1], '') not in lookup:
                    raise
                abs_fname = lookup[(descriptor_tuple[1], '')]
            else:
                abs_fname = lookup[(descriptor_tuple[1], descriptor_tuple[2])]
            new_desc = \
                self.load_abstraction(abs_fname, False, 
                                      descriptor_tuple[1],
                                      descriptor_tuple[4],
                                      lookup.values())
            descriptor_tuple = (new_desc.package, new_desc.name, 
                                new_desc.namespace, new_desc.package_version,
                                str(new_desc.version))
            return self.check_abstraction(descriptor_tuple, lookup)
        return None
        
    def ensure_abstractions_loaded(self, vistrail, abs_fnames):
        lookup = {}
        for abs_fname in abs_fnames:
            path, prefix, abs_name, abs_namespace, suffix = self.parse_abstraction_name(abs_fname, True)
            # abs_name = os.path.basename(abs_fname)[12:-4]
            lookup[(abs_name, abs_namespace)] = abs_fname
            
        # we're going to recurse manually (see
        # add_abstraction_to_regsitry) because we can't call
        # abstraction.vistrail until the module is loaded.
        abstractions = self.find_abstractions(vistrail)
        for descriptor_info, abstraction_list in abstractions.iteritems():
            # print 'checking for abstraction "' + str(abstraction.name) + '"'
            descriptor = self.check_abstraction(descriptor_info,
                                                lookup)
            for abstraction in abstraction_list:
                abstraction.module_descriptor = descriptor
            
    def build_ungroup(self, full_pipeline, module_id):

        group = full_pipeline.modules[module_id]
        if group.vtType == Group.vtType:
            pipeline = group.pipeline
        elif group.vtType == Abstraction.vtType:
            pipeline = group.summon().pipeline
        else:
            print 'not a group or abstraction?'
            return
      
        pipeline.ensure_connection_specs()

        modules = []
        connections = []
        id_remap = {}
        for module in pipeline.module_list:
            # FIXME have better checks for this
            if module.package != basic_pkg or (module.name != 'InputPort' and
                                               module.name != 'OutputPort'):
                modules.append(module.do_copy(True, self.id_scope, id_remap))
        self.translate_modules(modules, -group.location.x, -group.location.y)
        module_index = dict([(m.id, m) for m in modules])

        open_ports = {}
        for connection in pipeline.connection_list:
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if (Module.vtType, port.moduleId) not in id_remap:
                    all_inside = False
                else:
                    all_outside = False
            
            if all_inside:
                connections.append(connection.do_copy(True, self.id_scope, 
                                                      id_remap))
            else:
                if (Module.vtType, connection.source.moduleId) not in id_remap:
                    port_module = \
                        pipeline.modules[connection.source.moduleId]
                    port_type = 'input'
                elif (Module.vtType, connection.destination.moduleId) \
                        not in id_remap:
                    port_module = \
                        pipeline.modules[connection.destination.moduleId]
                    port_type = 'output'
                else:
                    continue

                (port_name, _, _, neighbors) = \
                    group.get_port_spec_info(port_module)
                new_neighbors = \
                    [(module_index[id_remap[(Module.vtType, m.id)]], n)
                     for (m, n) in neighbors
                     if (Module.vtType, m.id) in id_remap]
                open_ports[(port_name, port_type)] = new_neighbors        

        for connection in full_pipeline.connection_list:
            if connection.source.moduleId == group.id:
                key = (connection.source.name, 'output')
                if key not in open_ports:
                    continue
                neighbors = open_ports[key]
                input_module = \
                    full_pipeline.modules[connection.destination.moduleId]
                input_port = connection.destination.name
                for (output_module, output_port) in neighbors:
                    connections.append(self.create_connection(output_module,
                                                              output_port,
                                                              input_module,
                                                              input_port))
            elif connection.destination.moduleId == group.id:
                key = (connection.destination.name, 'input')
                if key not in open_ports:
                    continue
                neighbors = open_ports[key]
                output_module = \
                    full_pipeline.modules[connection.source.moduleId]
                output_port = connection.source.name
                for (input_module, input_port) in neighbors:
                    connections.append(self.create_connection(output_module, 
                                                              output_port,
                                                              input_module, 
                                                              input_port))
        # end for

        return (modules, connections)

    def find_thumbnails(self, tags_only=True):
        thumbnails = []
        thumb_cache = ThumbnailCache.getInstance()
        for action in self.vistrail.actions:
            if self.vistrail.has_thumbnail(action.id):
                thumbnail = self.vistrail.get_thumbnail(action.id)
                if tags_only and not self.vistrail.has_tag(action.timestep):
                    thumb_cache.remove(thumbnail)
                    self.vistrail.set_thumbnail(action.timestep, "")
                else:
                    abs_fname = thumb_cache.get_abs_name_entry(thumbnail)
                    if abs_fname is not None:
                        thumbnails.append(abs_fname)
                    else:
                        self.vistrail.set_thumbnail(action.timestep, "")
        return thumbnails
    
    def add_parameter_changes_from_execution(self, pipeline, version,
                                             parameter_changes):
        """add_parameter_changes_from_execution(pipeline, version,
        parameter_changes) -> int.

        Adds new versions to the current vistrail as a result of an
        execution. Returns the version number of the new version."""

        current_pipeline = self.current_pipeline
        current_version = self.current_version

        self.current_pipeline = pipeline
        self.current_version = version

        op_list = []
        for (m_id, function_name, param_values) in parameter_changes:
            try:
                param_values_len = len(param_values)
            except TypeError:
                param_values = [param_values]
            # FIXME should use registry to determine parameter types
            # and then call the translate_to_string method on each
            # parameter
            param_values = [str(x) for x in param_values]
            module = self.current_pipeline.modules[m_id]
            # FIXME remove this code when aliases move
            old_id = -1
            for old_function in module.functions:
                if old_function.name == function_name:
                    old_id = old_function.real_id

            # ensure that replacements don't happen for functions that
            # shouldn't be replaced
            aliases = []
            if old_id >= 0:
                function = module.function_idx[old_id]
                for i in xrange(len(param_values)):
                    aliases.append(function.params[i].alias)
                    
            op_list.extend(self.update_function_ops(module, function_name, 
                                                    param_values,
                                                    should_replace=True, 
                                                    aliases=aliases))

        action = core.db.action.create_action(op_list)
        self.add_new_action(action)

        self.current_pipeline = current_pipeline
        self.current_version = current_version
        
        return action.id
    
    ##########################################################################
    # Workflow Execution
    
    def execute_workflow_list(self, vistrails):
        """execute_workflow_list(vistrails: list) -> (results, bool)"""
        
        interpreter = get_default_interpreter()
        changed = False
        results = []
        for vis in vistrails:
            (locator, version, pipeline, view, aliases, params, reason, extra_info) = vis
            
            temp_folder_used = False
            if (not extra_info or not extra_info.has_key('pathDumpCells') or 
                not extra_info['pathDumpCells']):
                if extra_info is None:
                    extra_info = {}
                extra_info['pathDumpCells'] = create_temp_folder(prefix='vt_thumb')
                temp_folder_used = True
#           
            kwargs = {'locator': locator,
                      'current_version': version,
                      'view': view,
                      'logger': self.get_logger(),
                      'controller': self,
                      'aliases': aliases,
                      'params': params,
                      'reason': reason,
                      'extra_info': extra_info,
                      }    
            result = interpreter.execute(pipeline, **kwargs)
            
            thumb_cache = ThumbnailCache.getInstance()
            
            if len(result.errors) == 0 and thumb_cache.conf.autoSave:
                old_thumb_name = self.vistrail.get_thumbnail(version)
                fname = thumb_cache.add_entry_from_cell_dump(
                                        extra_info['pathDumpCells'], 
                                        old_thumb_name)
                if fname is not None: 
                    self.vistrail.set_thumbnail(version, fname)
                    changed = True
              
            if temp_folder_used:
                remove_temp_folder(extra_info['pathDumpCells'])
            
            if result.parameter_changes:
                l = result.parameter_changes
                self.add_parameter_changes_from_execution(pipeline, version, l)
                changed = True
            
            results.append(result)
            
        if self.logging_on():
            self.set_changed(True)
            
        if interpreter.debugger:
            interpreter.debugger.update_values()
        return (results,changed)
    
    def execute_current_workflow(self, custom_aliases=None, custom_params=None,
                                 extra_info=None, reason='Pipeline Execution'):
        """ execute_current_workflow(custom_aliases: dict, 
                                     custom_params: list,
                                     extra_info: dict) -> (list, bool)
        Execute the current workflow (if exists)
        custom_params is a list of tuples (vttype, oId, newval) with new values
        for parameters
        extra_info is a dictionary containing extra information for execution.
        As we want to make the executions thread safe, we will pass information
        specific to each pipeline through extra_info
        As, an example, this will be useful for telling the spreadsheet where
        to dump the images.
        """
        self.flush_delayed_actions()
        if self.current_pipeline:
            locator = self.get_locator()
            if locator:
                locator.clean_temporaries()
                if self._auto_save:
                    locator.save_temporary(self.vistrail)
            view = DummyView()
            return self.execute_workflow_list([(self.locator,
                                                self.current_version,
                                                self.current_pipeline,
                                                view,
                                                custom_aliases,
                                                custom_params,
                                                reason,
                                                extra_info)])

    def recompute_terse_graph(self):
        # get full version tree (including pruned nodes) this tree is
        # kept updated all the time. This data is read only and should
        # not be updated!
        fullVersionTree = self.vistrail.tree.getVersionTree()

        # create tersed tree
        x = [(0,None)]
        tersedVersionTree = Graph()

        # cache actionMap and tagMap because they're properties, sort
        # of slow
        am = self.vistrail.actionMap
        tm = self.vistrail.get_tagMap()
        last_n = self.vistrail.getLastActions(self.num_versions_always_shown)

        while 1:
            try:
                (current,parent)=x.pop()
            except IndexError:
                break

            # mount childs list
            if current in am and self.vistrail.is_pruned(current):
                children = []
            else:
                children = \
                    [to for (to, _) in fullVersionTree.adjacency_list[current]
                     if (to in am) and (not self.vistrail.is_pruned(to) or \
                                            to == self.current_version)]

            if (self.full_tree or
                (current == 0) or  # is root
                (current in tm) or # hasTag:
                (len(children) <> 1) or # not oneChild:
                (current == self.current_version) or # isCurrentVersion
                (am[current].expand) or  # forced expansion
                (current in last_n)): # show latest

                # yes it will!  this needs to be here because if we
                # are refining version view receives the graph without
                # the non matching elements
                if( (not self.refine) or
                    (self.refine and not self.search) or
                    (current == 0) or
                    (self.refine and self.search and
                     self.search.match(self.vistrail,am[current]) or
                     current == self.current_version)):
                    # add vertex...
                    tersedVersionTree.add_vertex(current)

                    # ...and the parent
                    if parent is not None:
                        tersedVersionTree.add_edge(parent,current,0)

                    # update the parent info that will be used by the
                    # childs of this node
                    parentToChildren = current
                else:
                    parentToChildren = parent
            else:
                parentToChildren = parent

            for child in reversed(children):
                x.append((child, parentToChildren))

        self._current_terse_graph = tersedVersionTree
        self._current_full_graph = self.vistrail.tree.getVersionTree()
        
    # def refine_graph(self, step=1.0):
    #     """ refine_graph(step: float in [0,1]) -> (Graph, Graph)
    #     Refine the graph of the current vistrail based the search
    #     status of the controller. It also return the full graph as a
    #     reference
                     
    #     """
        
    #     if self._current_full_graph is None:
    #         self.recompute_terse_graph()
    #     return (self._current_terse_graph, self._current_full_graph,
    #             self._current_graph_layout)

    def get_latest_version_in_graph(self):
        if not self._current_terse_graph:
            # DAK do we want refine_graph here?
            # (current, full, layout) = self.refine_graph()
            self.recompute_terse_graph()
        if self._current_terse_graph:
            return max(self._current_terse_graph.iter_vertices())
        return max(self.actions)

    def select_latest_version(self):
        """ select_latest_version() -> None
        Try to select the latest visible version on the tree
        
        """
        self.change_selected_version(self.get_latest_version_in_graph())

    def enable_missing_package(self, identifier, deps):
        """callback for try_to_enable_package"""
        return True

    def install_missing_package(self, identifier):
        """callback for try_to_enable_package"""
        return True
       
    def handleMissingSUDSWebServicePackage(self, identifier):
        pm = get_package_manager()
        suds_i = 'edu.utah.sci.vistrails.sudswebservices'
        pkg = pm.identifier_is_available(suds_i)
        if pkg:
            pm.late_enable_package(pkg.codepath)
        package = pm.get_package_by_identifier(suds_i)
        if not package or \
           not hasattr(package._init_module, 'load_from_signature'):
            return False
        return package._init_module.load_from_signature(identifier)

    def try_to_enable_package(self, identifier, dep_graph, confirmed=False):
        """try_to_enable_package(identifier: str,
                                 dep_graph: Graph,
                                 confirmed: boolean)
        Returns True if changes have been made to the registry, which
        means reloading a pipeline that previously failed with missing
        packages might work now.  dep_graph will enable any
        dependencies.  Setting confirmed to True will bypass prompts
        for later enables.
        """

        pm = get_package_manager()
        pkg = pm.identifier_is_available(identifier)
        if not pkg and identifier.startswith('SUDS#'):
            return self.handleMissingSUDSWebServicePackage(identifier)
        if not pm.has_package(identifier) and pkg:
            deps = pm.all_dependencies(identifier, dep_graph)[:-1]
            if identifier in self._asked_packages:
                return False
            if not confirmed and \
                    not self.enable_missing_package(identifier, deps):
                self._asked_packages.add(identifier)
                return False
            # Ok, user wants to late-enable it. Let's give it a shot
            try:
                pm.late_enable_package(pkg.codepath)
            except pkg.MissingDependency, e:
                for dependency in e.dependencies:
                    print 'MISSING DEPENDENCY:', dependency
                    if not self.try_to_enable_package(dependency[0], dep_graph,
                                                      True):
                        return False
                return self.try_to_enable_package(identifier, dep_graph, True)
            except pkg.InitializationFailed:
                self._asked_packages.add(identifier)
                raise
            # there's a new package in the system, so we retry
            # changing the version by recursing, since other
            # packages/modules might still be needed.
            self._asked_packages.add(identifier)
            return True

        # Package is not available, let's try to fetch it
        rep = core.packagerepository.get_repository()
        if rep:
            codepath = rep.find_package(identifier)
            if codepath and self.install_missing_package(identifier):
                rep.install_package(codepath)
                return self.try_to_enable_package(identifier, dep_graph, True)
        self._asked_packages.add(identifier)
        return False

    def set_action_annotation(self, action, key, value, id_scope=None):
        if id_scope is None:
            id_scope = self.id_scope
        if action.has_annotation_with_key(key):
            old_annotation = action.get_annotation_by_key(key)
            if old_annotation.value == value:
                return False
            action.delete_annotation(old_annotation)
        if value.strip() != '':
            annotation = \
                Annotation(id=id_scope.getNewId(Annotation.vtType),
                           key=key,
                           value=value,
                           )
            action.add_annotation(annotation)
        
    def create_upgrade_action(self, actions):
        new_action = core.db.action.merge_actions(actions)
        self.set_action_annotation(new_action, Action.ANNOTATION_DESCRIPTION, 
                                   "Upgrade")
        return new_action

    def handle_invalid_pipeline(self, e, new_version, vistrail=None,
                                report_all_errors=False, force_no_delay=False):
        load_other_versions = False
        # print 'running handle_invalid_pipeline'
        if vistrail is None:
            vistrail = self.vistrail
        pm = get_package_manager()
        root_exceptions = e.get_exception_set()
        missing_packages = {}
        def process_missing_packages(exception_set):
            for err in exception_set:
                err._was_handled = False
                # print '--- trying to fix', str(err)
                # FIXME need to get module_id from these exceptions
                # when possible!  need to integrate
                # report_missing_module and handle_module_upgrade
                if isinstance(err, InvalidPipeline):
                    process_missing_packages(err.get_exception_set())
                elif isinstance(err, MissingPackage):
                    #check if the package was already installed before (because
                    #it was in the dependency list of a previous package
                    if err._identifier not in missing_packages:
                        missing_packages[err._identifier] = []
                    missing_packages[err._identifier].append(err)

        process_missing_packages(root_exceptions)
        new_exceptions = []
        
        dep_graph = pm.build_dependency_graph(missing_packages)
        # for identifier, err_list in missing_packages.iteritems():
        for identifier in pm.get_ordered_dependencies(dep_graph):
            # print 'testing identifier', identifier
            if not pm.has_package(identifier):
                try:
                    # print 'trying to enable package'
                    if not self.try_to_enable_package(identifier, dep_graph):
                        pass
                        # print 'failed to enable package'
                        # if not report_all_errors:
                        #     raise err
                    else:
                        for err in missing_packages[identifier]:
                            err._was_handled = True
                except Exception, new_e:
                    print '&&& hit other exception'
                    new_exceptions.append(new_e)
                    if not report_all_errors:
                        raise new_e
            else:
                if identifier in missing_packages:
                    for err in missing_packages[identifier]:
                        err._was_handled = True
            # else assume the package was already enabled

        if len(new_exceptions) > 0:
            # got new exceptions
            pass

        def process_package_versions(exception_set):
            for err in exception_set:
                if err._was_handled:
                    continue
                if isinstance(err, InvalidPipeline):
                    process_package_versions(err.get_exception_set())
                if isinstance(err, MissingPackageVersion):
                    # try and load other version of package?
                    err._was_handled = True
                    pass
        
        # instead of upgrading, may wish to load the old version of
        # the package if possible
        if load_other_versions:
            process_package_versions(root_exceptions)

        def process_package_exceptions(exception_set, pipeline):
            new_actions = []
            package_errs = {}
            for err in exception_set:
                if err._was_handled:
                    continue
                # print '+++ trying to fix', str(err)
                if isinstance(err, InvalidPipeline):
                    id_scope = IdScope(1, {Group.vtType: Module.vtType,
                                           Abstraction.vtType: Module.vtType})
                    id_remap = {}
                    new_pipeline = err._pipeline.do_copy(True, id_scope, 
                                                         id_remap)
                    new_exception_set = []
                    for sub_err in err.get_exception_set():
                        key = (Module.vtType, sub_err._module_id)
                        if key in id_remap:
                            sub_err._module_id = id_remap[key]
                            new_exception_set.append(sub_err)
                        else:
                            new_exception_set.append(sub_err)
                            
                    # set id to None so db saves correctly
                    new_pipeline.id = None
                    old_id_scope = self.id_scope
                    self.id_scope = id_scope
                    inner_actions = \
                        process_package_exceptions(new_exception_set,
                                                   new_pipeline)
                    self.id_scope = old_id_scope
                    if len(inner_actions) > 0:
                        # create action that recreates group/subworkflow
                        old_module = pipeline.modules[err._module_id]
                        if old_module.is_group():
                            my_actions = \
                                UpgradeWorkflowHandler.replace_group(
                                self, pipeline, old_module.id, new_pipeline)
                            for action in my_actions:
                                pipeline.perform_action(action)
                            new_actions.extend(my_actions)
# This code shouldn't ever be reachable because invalid abstraction pipelines are handled when they're initially loaded.
#                        elif old_module.is_abstraction():
#                            # add new version to the abstraction
#                            # then update the current pipeline by replacing
#                            # abstraction module
#
#                            # FIXME finish this code
#                            my_actions = \
#                                UpgradeWorkflowHandler.replace_abstraction(
#                                self, pipeline, old_module.id, inner_actions)
#                            for action in my_actions:
#                                pipeline.perform_action(action)
#                            new_actions.extend(my_actions)
                        
                elif (isinstance(err, MissingModule) or 
                      isinstance(err, MissingPackageVersion) or 
                      isinstance(err, MissingModuleVersion)):
                    if err._identifier not in package_errs:
                        package_errs[err._identifier] = []
                    package_errs[err._identifier].append(err)

            for identifier, err_list in package_errs.iteritems():
                try:
                    pkg = pm.get_package_by_identifier(identifier)
                except Exception, e:
                    # cannot get the package we need
                    continue
                details = '\n'.join(str(e) for e in err_list)
                debug.log('Processing upgrades in package "%s"' %
                          identifier, details)
                if pkg.can_handle_all_errors():
                    try:
                        actions = pkg.handle_all_errors(self, err_list, 
                                                        pipeline)
                        if actions is not None:
                            for action in actions:
                                pipeline.perform_action(action)
                            new_actions.extend(actions)
                            for err in err_list:
                                err._was_handled = True
                    except Exception, new_e:
                        new_exceptions.append(new_e)
                        if not report_all_errors:
                            return new_actions
#                 elif pkg.can_handle_upgrades():
#                     print '  handle upgrades'
#                     for err in err_list:
#                         try:
#                             actions = pkg.handle_module_upgrade_request(
#                                 self, err._module_id, pipeline)
#                             if actions is not None:
#                                 print 'handled', pipeline.modules[err._module_id].name
#                                 for action in actions:
#                                     pipeline.perform_action(action)
#                                 new_actions.extend(actions)
#                                 print 'OK'
#                                 err._was_handled = True
#                         except Exception, new_e:
#                             new_exceptions.append(new_e)
#                             if not report_all_errors:
#                                 return
                else:
                    # print '  default upgrades'
                    # process default upgrades
                    # handler = UpgradeWorkflowHandler(self, pipeline)
                    for err in err_list:
                        try:
                            actions = UpgradeWorkflowHandler.dispatch_request(
                                self, err._module_id, pipeline)
                            if actions is not None:
                                for action in actions:
                                    pipeline.perform_action(action)
                                new_actions.extend(actions)
                                err._was_handled = True
                        except Exception, new_e:
                            import traceback
                            traceback.print_exc()
                            new_exceptions.append(new_e)

                if pkg.can_handle_missing_modules():
                    for err in err_list + new_exceptions:
                        if hasattr(err, '_was_handled') and err._was_handled:
                            continue
                        if isinstance(err, MissingModule):
                            try:
                                res = pkg.handle_missing_module(self, 
                                                                err._module_id,
                                                                pipeline)
                                # need backward compatibility
                                if res is True:
                                    err._was_handled = True
                                elif res is False:
                                    pass
                                else:
                                    actions = res
                                    if actions is not None:
                                        for action in actions:
                                            pipeline.perform_action(action)
                                        new_actions.extend(actions)
                                        err._was_handled = True
                            except Exception, new_e:
                                new_exceptions.append(new_e)
                                if not report_all_errors:
                                    return new_actions
            return new_actions

        if get_vistrails_configuration().check('upgradeOn'):
            cur_pipeline = copy.copy(e._pipeline)
            # note that cur_pipeline is modified to be the result of
            # applying the actions in new_actions
            new_actions = process_package_exceptions(root_exceptions, 
                                                     cur_pipeline)
        else:
            new_actions = []
            cur_pipeline = e._pipeline

        if len(new_actions) > 0:
            upgrade_action = self.create_upgrade_action(new_actions)
            if get_vistrails_configuration().check('upgradeDelay') and not force_no_delay:
                self._delayed_actions.append(upgrade_action)
            else:
                vistrail.add_action(upgrade_action, new_version, 
                                    self.current_session)
                vistrail.set_upgrade(new_version, str(upgrade_action.id))
                if get_vistrails_configuration().check("migrateTags"):
                    self.migrate_tags(new_version, upgrade_action.id, vistrail)
                new_version = upgrade_action.id
                self.set_changed(True)
                self.recompute_terse_graph()

        def check_exceptions(exception_set):
            unhandled_exceptions = []
            for err in exception_set:
                if isinstance(err, InvalidPipeline):
                    sub_exceptions = check_exceptions(err.get_exception_set())
                    if len(sub_exceptions) > 0:
                        new_err = InvalidPipeline(sub_exceptions, 
                                                  err._pipeline,
                                                  err._version)
                        unhandled_exceptions.append(new_err)
                else:
                    if not err._was_handled:
                        unhandled_exceptions.append(err)
            return unhandled_exceptions

        left_exceptions = check_exceptions(root_exceptions)
        if len(left_exceptions) > 0 or len(new_exceptions) > 0:
            details = '\n'.join(set(str(e) for e in left_exceptions + \
                                    new_exceptions))
            # debug.critical("Some exceptions could not be handled", details)
            raise InvalidPipeline(left_exceptions + new_exceptions, 
                                  cur_pipeline, new_version)
        return (new_version, cur_pipeline)

    def validate(self, pipeline, raise_exception=True):
        vistrail_vars = self.get_vistrail_variables()
        pipeline.validate(raise_exception, vistrail_vars)
    
    def do_version_switch(self, new_version, report_all_errors=False, 
                          do_validate=True, from_root=False):
        """ do_version_switch(new_version: int,
                              resolve_all_errors: boolean) -> None        
        Change the current vistrail version into new_version, reporting
        either the first error or all errors.
        
        """

        # This is tricky code, so watch carefully before you change
        # it.  The biggest problem is that we want to perform state
        # changes only after all exceptions have been handled, but
        # creating a pipeline every time is too slow. The solution
        # then is to mutate currentPipeline, and in case exceptions
        # are thrown, we roll back by rebuilding the pipeline from
        # scratch as the first thing on the exception handler, so to
        # the rest of the exception handling code, things look
        # stateless.

        def get_cost(descendant, ancestor):
            cost = 0
            am = self.vistrail.actionMap
            if descendant == -1:
                descendant = 0
            while descendant != ancestor:
                descendant = am[descendant].parent
                cost += 1
            return cost
        
        def switch_version(version, allow_fail=False):
            if self.current_version != -1 and not self.current_pipeline:
                debug.warning("current_version is not -1 and "
                              "current_pipeline is None")
            if version != self.current_version:
                # clear delayed actions
                # FIXME: invert the delayed actions and integrate them into
                # the general_action_chain?
                if len(self._delayed_actions) > 0:
                    self._delayed_actions = []
                    self.current_pipeline = Pipeline()
                    self.current_version = 0
            if version == -1:
                return None

            # now we reuse some existing pipeline, even if it's the
            # empty one for version zero
            #
            # The available pipelines are in self._pipelines, plus
            # the current pipeline.
            # Fast check: do we have to change anything?
            if from_root:
                result = self.vistrail.getPipeline(version)
            elif version == self.current_version:
                # we don't even need to check connection specs or
                # registry
                return self.current_pipeline
            # Fast check: if target is cached, copy it and we're done.
            elif version in self._pipelines:
                result = copy.copy(self._pipelines[version])
            else:
                # Find the closest upstream pipeline to the current one
                cv = self._current_full_graph.inverse_immutable().closest_vertex
                closest = cv(version, self._pipelines)
                cost_to_closest_version = get_cost(version, closest)
                # Now we have to decide between the closest pipeline
                # to version and the current pipeline
                shared_parent = getSharedRoot(self.vistrail, 
                                              [self.current_version, 
                                               version])
                cost_common_to_old = get_cost(self.current_version, 
                                              shared_parent)
                cost_common_to_new = get_cost(version, shared_parent)
                cost_to_current_version = cost_common_to_old + \
                    cost_common_to_new
                # FIXME I'm assuming copying the pipeline has zero cost.
                # Formulate a better cost model
                if cost_to_closest_version < cost_to_current_version:
                    if closest == 0:
                        result = self.vistrail.getPipeline(version)
                    else:
                        result = copy.copy(self._pipelines[closest])
                        action = self.vistrail.general_action_chain(closest, 
                                                                    version)
                        result.perform_action(action)
                else:
                    action = \
                        self.vistrail.general_action_chain(self.current_version,
                                                           version)
                    if self.current_version == -1 or self.current_version == 0:
                        result = Pipeline()
                    else:
                        result = copy.copy(self.current_pipeline)
                    result.perform_action(action)
                if self._cache_pipelines and \
                        self.vistrail.has_tag(long(version)):
                    # stash a copy for future use
                    if do_validate:
                        try:
                            self.validate(result)
                        except InvalidPipeline:
                            if not allow_fail:
                                raise
                        else:
                            self._pipelines[version] = copy.copy(result)
                    else:
                        self._pipelines[version] = copy.copy(result)
            if do_validate:
                try:
                    self.validate(result)
                except InvalidPipeline:
                    if not allow_fail:
                        raise
            return result
        # end switch_version

        try:
            self.current_pipeline = switch_version(new_version)
            self.current_version = new_version
        except InvalidPipeline, e:
            # print 'EXCEPTION'
            # print e
            new_error = None

            # DAK !!! don't need to rollback anymore!!!!
            # we don't update self.current_pipeline until we actually
            # get the result back

            start_version = new_version
            upgrade_version = self.vistrail.get_upgrade(new_version)
            was_upgraded = False
            if upgrade_version is not None:
                try:
                    upgrade_version = int(upgrade_version)
                    if (upgrade_version in self.vistrail.actionMap and \
                            not self.vistrail.is_pruned(upgrade_version)):
                        self.current_pipeline = switch_version(upgrade_version)
                        new_version = upgrade_version
                        self.current_version = new_version
                        # print 'self.current_version:', self.current_version
                        was_upgraded = True
                except InvalidPipeline:
                    # try to handle using the handler and create
                    # new upgrade
                    pass
            if not was_upgraded:
                try:
                    try:
                        (new_version, pipeline) = \
                            self.handle_invalid_pipeline(e, new_version,
                                                         self.vistrail,
                                                         report_all_errors)
                    except InvalidPipeline, e:
                        pipeline = e._pipeline
                    # check that we handled the invalid pipeline
                    # correctly
                    try:
                        self.validate(pipeline)
                    # this means that there was a new exception after handling 
                    # the invalid pipeline and we should handle it again.    
                    except InvalidPipeline, e:
                        (new_version, pipeline) = \
                                 self.handle_invalid_pipeline(e, new_version,
                                                              self.vistrail,
                                                              report_all_errors)
                        # check that we handled the invalid pipeline
                        # correctly
                    self.validate(pipeline)
                    self.current_pipeline = pipeline
                    self.current_version = new_version
                except InvalidPipeline, e:
                    # display invalid pipeline?
                    # import traceback
                    # traceback.print_exc()
                    new_error = e
                    
                    # just do the version switch, anyway, but alert the
                    # user to the remaining issues
                    self.current_pipeline = e._pipeline
                    new_version = e._version
                    self.current_version = new_version

            if new_version != start_version:
                self.invalidate_version_tree(False)
            if new_error is not None:
                raise new_error

    def change_selected_version(self, new_version, report_all_errors=True,
                                do_validate=True, from_root=False):
        try:
            self.do_version_switch(new_version, report_all_errors, 
                                   do_validate, from_root)
        except InvalidPipeline, e:
            # FIXME: do error handling through central switch that produces gui
            # or core.debug messages as specified
            def process_err(err):
                if isinstance(err, Package.InitializationFailed):
                    msg = ('Package "%s" failed during initialization. '
                           'Please contact the developer of that package '
                           'and report a bug.' % err.package.name)
                    debug.critical(msg)
                elif isinstance(err, PackageManager.MissingPackage):
                    msg = ('Cannot find package "%s" in '
                           'list of available packages. '
                           'Please install it first.' % err._identifier)
                    debug.critical(msg)
                elif issubclass(err.__class__, MissingPort):
                    msg = ('Cannot find %s port "%s" for module "%s" '
                           'in loaded package "%s". A different package '
                           'version might be necessary.') % \
                           (err._port_type, err._port_name, 
                            err._module_name, err._package_name)
                    debug.critical(msg)
                else:
                    debug.critical(str(err))                

            if report_all_errors:
                for err in e._exception_set:
                    process_err(err)
            elif len(e._exception_set) > 0:
                process_err(e._exception_set.__iter__().next())
        except Exception, e:
            import traceback
            debug.critical(str(e), traceback.format_exc())

    def write_temporary(self):
        if self.vistrail and self.changed:
            locator = self.get_locator()
            if locator:
                locator.save_temporary(self.vistrail)

    def write_abstractions(self, locator, save_bundle, abstractions, 
                           abs_save_dir):
        def make_abstraction_path_unique(abs_fname, namespace):
            # Constructs the abstraction name using the namespace to
            # prevent conflicts and copies the abstraction to the new
            # path so save_bundle has a valid file
            path, prefix, absname, old_ns, suffix = \
                self.parse_abstraction_name(abs_fname, True)
            new_abs_fname = os.path.join(abs_save_dir, 
                                         '%s%s(%s)%s' % (prefix, absname, 
                                                         namespace, suffix))
            # print " $@$@$ new_abs_fname:", new_abs_fname
            shutil.copy(abs_fname, new_abs_fname)
            return new_abs_fname

        included_abstractions = {}
        for abstraction_list in abstractions.itervalues():
            for abstraction in abstraction_list:
                abs_module = abstraction.module_descriptor.module
                namespaces = set(get_all_abs_namespaces(abstraction.vistrail))
                if abs_module is not None:
                    abs_fname = abs_module.vt_fname
                    path, prefix, abs_name, old_ns, suffix = \
                        self.parse_abstraction_name(abs_fname, True)
                    # do our indexing by abstraction name
                    # we know that abstractions with different names
                    # cannot overlap, but those that have the same
                    # name may or may not
                    if abs_name not in included_abstractions:
                        included_abstractions[abs_name] = [(abstraction, 
                                                            namespaces)]
                    else:
                        # only keep abstractions that don't repeat what
                        # others already cover
                        new_list = []
                        found = False
                        for (i_abs, i_namespaces) in \
                                included_abstractions[abs_name]:
                            if not (i_namespaces < namespaces):
                                new_list.append((i_abs, i_namespaces))
                            if i_namespaces >= namespaces:
                                found = True
                        # only add new one once
                        if not found:
                            new_list.append((abstraction, namespaces))
                        included_abstractions[abs_name] = new_list

        for abs_name, abstraction_list in included_abstractions.iteritems():
            for (abstraction, _) in abstraction_list:
                abs_module = abstraction.module_descriptor.module
                if abs_module is None:
                    continue
                abs_fname = abs_module.vt_fname
                if not os.path.exists(abs_fname):
                    # Write vistrail to disk if the file no longer
                    # exists (if temp file was deleted)
                    if abs_save_dir is None:
                        abs_save_dir = \
                            tempfile.mkdtemp(prefix='vt_abs')
                    abs_fname = os.path.join(abs_save_dir, 
                                             abstraction.name + '.xml')
                    save_abstraction(abstraction.vistrail, abs_fname)
                namespace = get_cur_abs_namespace(abstraction.vistrail)
                abs_unique_name = make_abstraction_path_unique(abs_fname,
                                                               namespace)
                save_bundle.abstractions.append(abs_unique_name)
                                
    def write_vistrail(self, locator, version=None, export=False):
        """write_vistrail(locator,version) -> Boolean
        It will return a boolean that tells if the tree needs to be 
        invalidated
        export=True means you should not update the current controller"""
        result = False 
        if self.vistrail and (self.changed or self.locator != locator):
            # FIXME create this on-demand?
            abs_save_dir = tempfile.mkdtemp(prefix='vt_abs')
            is_abstraction = self.vistrail.is_abstraction
            if is_abstraction and self.changed:
                # first update any names if necessary
                self.check_subpipeline_port_names()
                new_namespace = str(uuid.uuid1())
                annotation_key = get_next_abs_annotation_key(self.vistrail)
                self.vistrail.set_annotation(annotation_key, new_namespace)
            save_bundle = SaveBundle(self.vistrail.vtType)
            if export:
                save_bundle.vistrail = self.vistrail.do_copy()
                if type(locator) == core.db.locator.DBLocator:
                    save_bundle.vistrail.db_log_filename = None
            else:
                save_bundle.vistrail = self.vistrail
            if self.log and len(self.log.workflow_execs) > 0:
                save_bundle.log = self.log
            abstractions = self.find_abstractions(self.vistrail, True)
            self.write_abstractions(locator, save_bundle, abstractions, 
                                    abs_save_dir)
            thumb_cache = ThumbnailCache.getInstance()
            if thumb_cache.conf.autoSave:
                save_bundle.thumbnails = self.find_thumbnails(
                                           tags_only=thumb_cache.conf.tagsOnly)
            
            #mashups
            save_bundle.mashups = self._mashups
            # FIXME hack to use db_currentVersion for convenience
            # it's not an actual field
            self.vistrail.db_currentVersion = self.current_version
            if self.locator != locator:
                # check for db log
                log = Log()
                if type(self.locator) == core.db.locator.DBLocator:
                    connection = self.locator.get_connection()
                    db_log = open_vt_log_from_db(connection, 
                                                 self.vistrail.db_id)
                    Log.convert(db_log)
                    for workflow_exec in db_log.workflow_execs:
                        workflow_exec.db_id = \
                            log.id_scope.getNewId(DBWorkflowExec.vtType)
                        log.db_add_workflow_exec(workflow_exec)
                # add recent log entries
                if self.log and len(self.log.workflow_execs) > 0:
                    for workflow_exec in self.log.db_workflow_execs:
                        workflow_exec = copy.copy(workflow_exec)
                        workflow_exec.db_id = \
                            log.id_scope.getNewId(DBWorkflowExec.vtType)
                        log.db_add_workflow_exec(workflow_exec)
                if len(log.workflow_execs) > 0:
                    save_bundle.log = log
                old_locator = self.get_locator()
                if not export:
                    self.locator = locator
                save_bundle = locator.save_as(save_bundle, version)
                new_vistrail = save_bundle.vistrail
                if type(locator) == core.db.locator.DBLocator:
                    new_vistrail.db_log_filename = None
                    locator.kwargs['obj_id'] = new_vistrail.db_id
                if not export:
                    # DAK don't think is necessary since we have a new
                    # namespace for an abstraction on each save
                    # Unload abstractions from old namespace
                    # self.unload_abstractions() 
                    # Load all abstractions from new namespaces
                    self.ensure_abstractions_loaded(new_vistrail, 
                                                    save_bundle.abstractions) 
                    self.set_file_name(locator.name)
                    if old_locator and not export:
                        old_locator.clean_temporaries()
                        old_locator.close()
                    self.flush_pipeline_cache()
                    self.change_selected_version(new_vistrail.db_currentVersion, 
                                                 from_root=True)
            else:
                save_bundle = self.locator.save(save_bundle)
                new_vistrail = save_bundle.vistrail
                # Load any abstractions that were given new namespaces
                self.ensure_abstractions_loaded(new_vistrail, 
                                                save_bundle.abstractions)
            # FIXME abstractions only work with FileLocators right now
            if is_abstraction:
                new_vistrail.is_abstraction = True
                if ( type(self.locator) == core.db.locator.XMLFileLocator or
                     type(self.locator) == core.db.locator.ZIPFileLocator ):
                    filename = self.locator.name
                    if filename in self._loaded_abstractions:
                        del self._loaded_abstractions[filename]
                    # we don't know if the subworkflow should be shown
                    # if it doesn't currently exist, we don't want to add it
                    # if it does, we will replace it via upgrade module
                    # so it is not global
                    self.load_abstraction(filename, False)
                    
                    # reg = core.modules.module_registry.get_module_registry()
                    # for desc in reg.get_package_by_name('local.abstractions').descriptor_list:
                    #     print desc.name, desc.namespace, desc.version
            if not export:
                if id(self.vistrail) != id(new_vistrail):
                    new_version = new_vistrail.db_currentVersion
                    self.set_vistrail(new_vistrail, locator)
                    self.change_selected_version(new_version)
                    result = True
                if self.log:
                    self.log.delete_all_workflow_execs()
                self.set_changed(False)
                locator.clean_temporaries()

            # delete any temporary subworkflows
                try:
                    for root, _, files in os.walk(abs_save_dir, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                    os.rmdir(abs_save_dir)
                except OSError, e:
                    raise VistrailsDBException("Can't remove %s: %s" % \
                                                   (abs_save_dir, str(e)))
            return result


    def write_workflow(self, locator):
        if self.current_pipeline:
            pipeline = Pipeline()
            # pipeline.set_abstraction_map(self.vistrail.abstractionMap)
            for module in self.current_pipeline.modules.itervalues():
                # if module.vtType == AbstractionModule.vtType:
                #     abstraction = \
                #         pipeline.abstraction_map[module.abstraction_id]
                #     pipeline.add_abstraction(abstraction)
                pipeline.add_module(module)
            for connection in self.current_pipeline.connections.itervalues():
                pipeline.add_connection(connection)
            save_bundle = SaveBundle(pipeline.vtType,workflow=pipeline)
            locator.save_as(save_bundle)

    def write_log(self, locator):
        if self.log:
            if self.vistrail.db_log_filename is not None:
                log = core.db.io.merge_logs(self.log, 
                                            self.vistrail.db_log_filename)
            else:
                log = self.log
            #print log
            save_bundle = SaveBundle(log.vtType,log=log)
            locator.save_as(save_bundle)

    def read_log(self):
        """ Returns the saved log from zip or DB
        
        """
        return self.vistrail.get_persisted_log()
 
    def write_registry(self, locator):
        registry = core.modules.module_registry.get_module_registry()
        save_bundle = SaveBundle(registry.vtType, registry=registry)
        locator.save_as(save_bundle)

    def update_checkout_version(self, app=''):
        self.vistrail.update_checkout_version(app)

    def reset_redo_stack(self):
        self.redo_stack = []

    def undo(self):
        """Performs one undo step, moving up the version tree."""
        action_map = self.vistrail.actionMap
        old_action = action_map.get(self.current_version, None)
        self.redo_stack.append(self.current_version)
        self.show_parent_version()
        new_action = action_map.get(self.current_version, None)
        return (old_action, new_action)
        # self.set_pipeline_selection(old_action, new_action, 'undo')
        # return self.current_version

    def redo(self):
        """Performs one redo step if possible, moving down the version tree."""
        action_map = self.vistrail.actionMap
        old_action = action_map.get(self.current_version, None)
        if len(self.redo_stack) < 1:
            debug.critical("Redo on an empty redo stack. Ignoring.")
            return
        next_version = self.redo_stack[-1]
        self.redo_stack = self.redo_stack[:-1]
        self.show_child_version(next_version)
        new_action = action_map[self.current_version]
        return (old_action, new_action)
        # self.set_pipeline_selection(old_action, new_action, 'redo')
        # return next_version

    def can_redo(self):
        return (len(self.redo_stack) > 0)

    def can_undo(self):
        return self.current_version > 0
