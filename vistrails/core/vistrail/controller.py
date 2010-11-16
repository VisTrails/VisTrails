############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
from core.modules.sub_module import new_abstraction, read_vistrail
from core.packagemanager import PackageManager, get_package_manager
import core.packagerepository
from core.thumbnails import ThumbnailCache
from core.upgradeworkflow import UpgradeWorkflowHandler, UpgradeWorkflowError
from core.utils import VistrailsInternalError, PortAlreadyExists, DummyView, \
    InvalidPipeline
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
from db.domain import IdScope
from db.services.io import create_temp_folder, remove_temp_folder
from db.services.io import SaveBundle
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
    def __init__(self, vistrail=None, id_scope=None):
        self.vistrail = vistrail
        self.id_scope = id_scope
        self.current_session = -1
        self.log = Log()
        if vistrail is not None:
            self.id_scope = vistrail.idScope
            self.current_session = vistrail.idScope.getNewId('session')
            vistrail.current_session = self.current_session
            vistrail.log = self.log
        self.current_pipeline = None
        self.locator = None
        self.current_version = -1
        self.changed = False

        # if _cache_pipelines is True, cache pipelines to speed up
        # version switching
        self._cache_pipelines = True
        self._pipelines = {0: Pipeline()}
        self._current_full_graph = None
        self._current_terse_graph = None
        self._asked_packages = set()
        self._delayed_actions = []
        self._loaded_abstractions = {}

    def logging_on(self):
        return not get_vistrails_configuration().check('nologger')
            
    def get_logger(self):
        if self.logging_on():
            return LogControllerFactory.getInstance().create_logger(self.log)
        else:
            return DummyLogController()
        
    def get_locator(self):
        return self.locator
    
    def set_vistrail(self, vistrail, locator, abstractions=None, thumbnails=None):
        self.vistrail = vistrail
        if self.vistrail is not None:
            self.id_scope = self.vistrail.idScope
            self.current_session = self.vistrail.idScope.getNewId("session")
            self.vistrail.current_session = self.current_session
            self.vistrail.log = self.log
            if abstractions is not None:
                self.ensure_abstractions_loaded(self.vistrail, abstractions)
            if thumbnails is not None:
                ThumbnailCache.getInstance().add_entries_from_files(thumbnails)
        self.current_version = -1
        self.current_pipeline = None
        if self.locator != locator and self.locator is not None:
            self.locator.clean_temporaries()
        self.locator = locator
        self.recompute_terse_graph()
        
    def close_vistrail(self, locator):
        self.unload_abstractions()
        if locator is not None:
            locator.close()
            
    def set_id_scope(self, id_scope):
        self.id_scope = id_scope

    def set_changed(self, changed):
        """ set_changed(changed: bool) -> None
        Set the current state of changed and emit signal accordingly
        
        """
        if changed!=self.changed:
            self.changed = changed
        
    def check_alias(self, name):
        """check_alias(alias) -> Boolean 
        Returns True if current pipeline has an alias named name """
        # FIXME Why isn't this call on the pipeline?
        return self.current_pipeline.has_alias(name)
    
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

    def flush_delayed_actions(self):
        start_version = self.current_version
        desc_key = Action.ANNOTATION_DESCRIPTION
        for action in self._delayed_actions:
            self.vistrail.add_action(action, start_version, 
                                     self.current_session)
            # HACK to populate upgrade information
            if (action.has_annotation_with_key(desc_key) and
                action.get_annotation_by_key(desc_key).value == 'Upgrade'):
                self.vistrail.set_upgrade(start_version, str(action.id))
            self.current_version = action.id
            start_version = action.id

        # We have to do moves after the delayed actions because the pipeline
        # may have been updated
        self.flush_move_actions()
        self._delayed_actions = []

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

    def create_module_from_descriptor(self, descriptor, x=0.0, y=0.0, 
                                      internal_version=-1):
        reg = core.modules.module_registry.get_module_registry()
        package = reg.get_package_by_name(descriptor.identifier)
        loc_id = self.id_scope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=x, 
                            y=y,
                            )
        if internal_version > -1:
            abstraction_id = self.id_scope.getNewId(Abstraction.vtType)
            module = Abstraction(id=abstraction_id,
                                 name=descriptor.name,
                                 package=descriptor.identifier,
                                 namespace=descriptor.namespace,
                                 version=package.version,
                                 location=location,
                                 internal_version=internal_version,
                                 )
        elif descriptor.identifier == basic_pkg and \
                descriptor.name == 'Group':
            group_id = self.id_scope.getNewId(Group.vtType)
            module = Group(id=group_id,
                           name=descriptor.name,
                           package=descriptor.identifier,
                           namespace=descriptor.namespace,
                           version=package.version,
                           location=location,
                           )
        else:
            module_id = self.id_scope.getNewId(Module.vtType)
            module = Module(id=module_id,
                            name=descriptor.name,
                            package=descriptor.identifier,
                            namespace=descriptor.namespace,
                            version=package.version,
                            location=location,
                            )
        module.is_valid = True
        return module

    def create_module(self, identifier, name, namespace='', x=0.0, y=0.0,
                      internal_version=-1):
        loc_id = self.id_scope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=x, 
                            y=y,
                            )
        if internal_version > -1:
            abstraction_id = self.id_scope.getNewId(Abstraction.vtType)
            module = Abstraction(id=abstraction_id,
                                 name=name,
                                 package=identifier,
                                 location=location,
                                 namespace=namespace,
                                 internal_version=internal_version,
                                 )
        elif identifier == basic_pkg and name == 'Group':
            group_id = self.id_scope.getNewId(Group.vtType)
            module = Group(id=group_id,
                           name=name,
                           package=identifier,
                           location=location,
                           namespace=namespace,
                           )
        else:
            module_id = self.id_scope.getNewId(Module.vtType)
            module = Module(id=module_id,
                            name=name,
                            package=identifier,
                            location=location,
                            namespace=namespace,
                            )
        module.is_valid = True
        return module

    def create_connection_from_ids(self, output_id, output_port_spec,
                                       input_id, input_port_spec):
        output_module = self.current_pipeline.modules[output_id]
        input_module = self.current_pipeline.modules[input_id]
        return self.create_connection(output_module, output_port_spec, 
                                      input_module, input_port_spec)

    def create_connection(self, output_module, output_port_spec,
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
        output_port_id = self.id_scope.getNewId(Port.vtType)
        output_port = Port(id=output_port_id,
                           spec=output_port_spec,
                           moduleId=output_module.id,
                           moduleName=output_module.name)
        input_port_id = self.id_scope.getNewId(Port.vtType)
        input_port = Port(id=input_port_id,
                           spec=input_port_spec,
                           moduleId=input_module.id,
                           moduleName=input_module.name)
        conn_id = self.id_scope.getNewId(Connection.vtType)
        connection = Connection(id=conn_id,
                                ports=[input_port, output_port])
        return connection

    def create_param(self, port_spec, pos, value):
        param_id = self.id_scope.getNewId(ModuleParam.vtType)
        descriptor = port_spec.descriptors()[pos]
        param_type = descriptor.sigstring
        # FIXME add/remove description
        # FIXME make ModuleParam constructor accept port_spec
        new_param = ModuleParam(id=param_id,
                                pos=pos,
                                name='<no description>',
                                alias='',
                                val=value,
                                type=param_type,
                                )
        return new_param

    def create_params(self, port_spec, values):
        params = []
        for i in xrange(len(port_spec.descriptors())):
            if i < len(values):
                value = str(values[i])
            else:
                value = None
            param = self.create_param(port_spec, i, value)
            params.append(param)
        return params

    def create_function(self, module, function_name, param_values=[]):
        port_spec = module.get_port_spec(function_name, 'input')
        if len(param_values) <= 0 and port_spec.defaults is not None:
            param_values = port_spec.defaults

        f_id = self.id_scope.getNewId(ModuleFunction.vtType)
        new_function = ModuleFunction(id=f_id,
                                      pos=module.getNumFunctions(),
                                      name=function_name,
                                      )
        new_function.is_valid = True
        new_params = self.create_params(port_spec, param_values)
        new_function.add_parameters(new_params)        
        return new_function

    def create_functions(self, module, functions):
        """create_functions(module: Module,
                            functions: [function_name: str,
                                        param_values: [str]]) 
            -> [ModuleFunction]
        
        """
        new_functions = []
        for f in functions:
            new_functions.append(self.create_function(module, *f))
        return new_functions
    
    def create_port_spec(self, module, port_type, port_name, port_sigstring,
                         port_sort_key=-1):
        p_id = self.id_scope.getNewId(PortSpec.vtType)
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
                            old_id=-1L, should_replace=True, aliases=[]):
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
            for i, new_param_value in enumerate(param_values):
                old_param = function.params[i]
                if (len(aliases) > i and old_param.alias != aliases[i]) or \
                        (old_param.strValue != new_param_value):
                    new_param = self.create_param(port_spec, i, 
                                                  new_param_value)
                    if len(aliases) > i:
                        new_param.alias = aliases[i]
                    op_list.append(('change', old_param, new_param,
                                    function.vtType, function.real_id))
        else:
            new_function = self.create_function(module, function_name,
                                                param_values)
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

    def update_parameter(self, old_param, new_value):
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

    def create_group(self, full_pipeline, module_ids, connection_ids):
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

    def create_abstraction(self, full_pipeline, module_ids, connection_ids, 
                           name):
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
        namespace = abs_vistrail.get_annotation('__abstraction_uuid__').value
        (avg_x, avg_y) = self.get_avg_location([full_pipeline.modules[m_id]
                                                for m_id in module_ids])
        abstraction = self.create_module(abstraction_pkg, name, namespace, 
                                         avg_x, avg_y, 1L)
        connections = self.get_connections_to_subpipeline(abstraction, 
                                                          outside_connections)
        return (abstraction, connections)

    def create_abstraction_from_group(self, full_pipeline, group_id, name):
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
        namespace = abs_vistrail.get_annotation('__abstraction_uuid__').value
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

    def get_abstraction_desc(self, name, namespace, module_version=None):
        reg = core.modules.module_registry.get_module_registry()
        if reg.has_descriptor_with_name(abstraction_pkg, name, namespace,
                                        None, module_version):
            return reg.get_descriptor_by_name(abstraction_pkg, name,
                                              namespace, None, module_version)
        return None

    def parse_abstraction_name(self, filename):
        # assume only 1 possible prefix or suffix
        prefixes = ["abstraction_"]
        suffixes = [".vt", ".xml"]
        name = os.path.basename(filename)
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        return name

    def add_abstraction_to_registry(self, abs_vistrail, abs_fname, name, 
                                    namespace=None, module_version=None,
                                    is_global=True, avail_fnames=[]):
        reg = core.modules.module_registry.get_module_registry()
        if namespace is None:
            namespace = \
                abs_vistrail.get_annotation('__abstraction_uuid__').value

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
                self.handle_invalid_pipeline(e, long(module_version), 
                                             abs_vistrail, False)
            core.db.io.save_vistrail_to_xml(abs_vistrail, abs_fname)
            self.set_changed(True)
            self.id_scope = vistrail_id_scope
            abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                          new_version, new_pipeline)
            module_version = str(new_version)

        old_desc = None
        if is_global:
            try:
                old_desc = reg.get_similar_descriptor(abstraction_pkg,
                                                      name,
                                                      namespace)
                # print "found old_desc", old_desc.name, old_desc.version
            except ModuleRegistryException, e:
                pass

        hide_descriptor = not is_global or old_desc is not None
        new_desc = reg.auto_add_module((abstraction, 
                                        {'package': abstraction_pkg,
                                         'package_version': abstraction_ver,
                                         'namespace': namespace,
                                         'version': module_version,
                                         'hide_namespace': True,
                                         'hide_descriptor': hide_descriptor,
                                         }))
        reg.auto_add_ports(abstraction)
        if old_desc is not None:
            reg.update_module(old_desc, new_desc)
        return new_desc

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
        abstraction_uuid = \
            abs_vistrail.get_annotation('__abstraction_uuid__').value
        if abstraction_uuid is None:
            abstraction_uuid = str(uuid.uuid1())
            abs_vistrail.set_annotation('__abstraction_uuid__', 
                                        abstraction_uuid)
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
        
        desc = self.get_abstraction_desc(abs_name, abstraction_uuid,
                                         module_version)
        if desc is None:
            print "adding version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "to registry"
            desc = self.add_abstraction_to_registry(abs_vistrail, abs_fname, 
                                                    abs_name, None, 
                                                    module_version, 
                                                    is_global, avail_fnames)
            if desc.version != module_version:
                print "upgraded version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "to version", desc.version
        else:
            if upgrade_version is not None:
                print "version", old_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "already in registry as upgraded version", module_version
            else:
                print "version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "already in registry"
        return desc
    
    def unload_abstractions(self):
        for abs_fname, abs_vistrail in self._loaded_abstractions.iteritems():
            abs_name = self.parse_abstraction_name(abs_fname)
            abs_namespace = abs_vistrail.get_annotation('__abstraction_uuid__').value
            try:
                descriptor = self.get_abstraction_descriptor(abs_name, abs_namespace)
                print "removing all versions of ", abs_name, "from registry (namespace: %s)"%abs_namespace
                while descriptor is not None:
                    reg = core.modules.module_registry.get_module_registry()
                    reg.delete_module(abstraction_pkg, abs_name, abs_namespace)
                    descriptor = self.get_abstraction_descriptor(abs_name, abs_namespace)
            except:
                # No versions of the abstraction exist in the registry now
                pass

    def update_abstraction(self, abstraction, new_actions):
        module_version = abstraction.internal_version
        if type(module_version) == type(""):
            module_version = int(module_version)
        abstraction_uuid = \
            abstraction.vistrail.get_annotation('__abstraction_uuid__').value
        upgrade_action = self.create_upgrade_action(new_actions) 
        
        a = (abstraction.vistrail, 
             module_version)
        
        desc = self.get_abstraction_desc(abstraction.name, abstraction_uuid,
                                         new_version)
        if desc is None:
            # desc = self.add_abstraction_to_registry(abstraction.vistrail,
            # abstraction.
            pass
        # FIXME finish this!
                                         
                                         
        

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
        if vistrail.get_annotation('__abstraction_uuid__') is None:            
            abstraction_uuid = str(uuid.uuid1())
            vistrail.set_annotation('__abstraction_uuid__', abstraction_uuid)

        if save_dir is None:
            save_dir = self.get_abstraction_dir()
        vt_fname = os.path.join(save_dir, name + '.xml')
        if not overwrite and os.path.exists(vt_fname):
            raise VistrailsInternalError("'%s' already exists" % \
                                             vt_fname)
        core.db.io.save_vistrail_to_xml(vistrail, vt_fname)
        return vt_fname

    def upgrade_abstraction_module(self, module_id, test_only=False):
        """upgrade_abstraction_module(module_id, test_only) -> None or (preserved: bool, missing_ports: list)

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
        failed = True
        src_ports_gone = {}
        dst_ports_gone = {}
        fns_gone = {}
        missing_ports = []
        while failed:
            try:
                upgrade_action = UpgradeWorkflowHandler.attempt_automatic_upgrade(self, self.current_pipeline, module_id, function_remap=fns_gone, src_port_remap=src_ports_gone, dst_port_remap=dst_ports_gone)[0]
                if test_only:
                    return (len(missing_ports) == 0, missing_ports)
                failed = False
            except UpgradeWorkflowError, e:
                if test_only:
                    missing_ports.append((e._port_type, e._port_name))
                if e._module is None or e._port_type is None or e._port_name is None:
                    raise e
                # Remove the offending connection/function by remapping to None
                if e._port_type == 'output':
                    src_ports_gone[e._port_name] = None
                elif e._port_type == 'input':
                    dst_ports_gone[e._port_name] = None
                    fns_gone[e._port_name] = None
                else:
                    raise e
        self.flush_delayed_actions()
        self.add_new_action(upgrade_action)
        self.perform_action(upgrade_action)
        self.vistrail.change_description("Upgrade Subworkflow", self.current_version)

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
            
    def unload_abstraction(self, name, namespace):
        if self.abstraction_exists(name):
            descriptor = self.get_abstraction_descriptor(name, namespace)
            descriptor._abstraction_refs -= 1
            # print 'unload ref_count:', descriptor.abstraction_refs
            if descriptor._abstraction_refs < 1:
                # unload abstraction
                print "deleting module:", name, namespace
                reg = core.modules.module_registry.get_module_registry()
                reg.delete_module(abstraction_pkg, name, namespace)

    def import_abstraction(self, new_name, name, namespace, 
                           module_version=None):
        # copy from a local namespace to local.abstractions
        reg = core.modules.module_registry.get_module_registry()
        descriptor = self.get_abstraction_desc(name, namespace, module_version)
        if descriptor is None:
            # if not self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction %s|%s not on registry" %\
                                             (name, namespace))
        # FIXME have save_abstraction take abs_fname as argument and do
        # shutil copy
        # abs_fname = descriptor.module.vt_fname
        abs_vistrail = descriptor.module.vistrail
        abs_fname = self.save_abstraction(abs_vistrail, new_name)
        if new_name == name:
            reg.show_module(descriptor)
            descriptor.module.vt_fname = abs_fname
        else:
            self.add_abstraction_to_registry(abs_vistrail, abs_fname, new_name,
                                             None, module_version)

    def export_abstraction(self, new_name, pkg_name, dir, name, namespace, 
                           module_version):
        descriptor = self.get_abstraction_desc(name, namespace, module_version)
        if descriptor is None:
            raise VistrailsInternalError("Abstraction %s|%s not on registry" %\
                                             (name, namespace))
        
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
            if descriptor_tuple[1] not in lookup:
                raise
            abs_fname = lookup[descriptor_tuple[1]]
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
            abs_name = self.parse_abstraction_name(abs_fname)
            # abs_name = os.path.basename(abs_fname)[12:-4]
            lookup[abs_name] = abs_fname
            
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
            
    def create_ungroup(self, full_pipeline, module_id):

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
                     for (m, n) in neighbors]
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
            (locator, version, pipeline, view, aliases, extra_info) = vis
            
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
    
    def execute_current_workflow(self, custom_aliases=None, extra_info=None):
        """ execute_current_workflow(custo_aliases: dict, extra_info: dict) -> (list, bool)
        Execute the current workflow (if exists)
        extra_info is a dictionary containing extra information for execution.
        As we want to make the executions thread safe, we will pass information
        specific to each pipeline through this parameter
        As, an example, this will be useful for telling the spreadsheet where
        to dump the images.
        """
        if self.current_pipeline:
            locator = self.get_locator()
            if locator:
                locator.clean_temporaries()
                locator.save_temporary(self.vistrail)
            view = DummyView()
            return self.execute_workflow_list([(self.locator,
                                                self.current_version,
                                                self.current_pipeline,
                                                view,
                                                custom_aliases,
                                                extra_info)])

    def recompute_terse_graph(self):
        """recomputes just the full graph, gui.VistrailController
        does more

        """
        self._current_full_graph = self.vistrail.tree.getVersionTree()

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

        # print 'TRYING TO ENABLE:', identifier
        pm = get_package_manager()
        pkg = pm.identifier_is_available(identifier)
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
                                report_all_errors=False):
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
                    inner_actions = \
                        process_package_exceptions(new_exception_set,
                                                   new_pipeline)
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
                debug.warning('** Trying to fix errors in %s' % identifier)
                for t in ['  ' + str(e) for e in err_list]:
                    debug.warning(t)
                if pkg.can_handle_all_errors():
                    debug.warning('  handle_all_errors')
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
            if get_vistrails_configuration().check('upgradeDelay'):
                self._delayed_actions.append(upgrade_action)
            else:
                vistrail.add_action(upgrade_action, new_version, 
                                    self.current_session)
                vistrail.set_upgrade(new_version, str(upgrade_action.id))
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
        for left in left_exceptions:
            debug.critical('--> %s' % left)
        if len(left_exceptions) > 0 or len(new_exceptions) > 0:
            raise InvalidPipeline(left_exceptions + new_exceptions, 
                                  cur_pipeline, new_version)
        return (new_version, cur_pipeline)

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
            if version != self.current_pipeline:
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
                            result.validate()
                        except InvalidPipeline:
                            if not allow_fail:
                                raise
                        else:
                            self._pipelines[version] = copy.copy(result)
                    else:
                        self._pipelines[version] = copy.copy(result)
            if do_validate:
                try:
                    result.validate()
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
                        pipeline.validate()
                    # this means that there was a new exception after handling 
                    # the invalid pipeline and we should handle it again.    
                    except InvalidPipeline, e:
                        (new_version, pipeline) = \
                                 self.handle_invalid_pipeline(e, new_version,
                                                              self.vistrail,
                                                              report_all_errors)
                        # check that we handled the invalid pipeline
                        # correctly
                    pipeline.validate()
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
            debug.critical(str(e))

    def write_temporary(self):
        if self.vistrail and self.changed:
            locator = self.get_locator()
            if locator:
                locator.save_temporary(self.vistrail)
                
    def write_vistrail(self, locator, version=None):
        """write_vistrail(locator,version) -> Boolean
        It will return a boolean that tells if the tree needs to be 
        invalidated"""
        result = False
        if self.vistrail and (self.changed or self.locator != locator):
            abs_save_dir = None
            is_abstraction = self.vistrail.is_abstraction
            save_bundle = SaveBundle(self.vistrail.vtType)
            save_bundle.vistrail = self.vistrail
            if self.log and len(self.log.workflow_execs) > 0:
                save_bundle.log = self.log
            abstractions = self.find_abstractions(self.vistrail, True)
            for abstraction_list in abstractions.itervalues():
                for abstraction in abstraction_list:
                    abs_module = abstraction.module_descriptor.module
                    if abs_module is not None:
                        abs_fname = abs_module.vt_fname
                        if not os.path.exists(abs_fname):
                            if abs_save_dir is None:
                                abs_save_dir = tempfile.mkdtemp(prefix='vt_abs')
                            abs_fname = os.path.join(abs_save_dir, 
                                                     abstraction.name + '.xml')
                            core.db.io.save_vistrail_to_xml(abstraction.vistrail,
                                                            abs_fname)
                        save_bundle.abstractions.append(abs_fname)

            thumb_cache = ThumbnailCache.getInstance()
            if thumb_cache.conf.autoSave:
                save_bundle.thumbnails = self.find_thumbnails(
                                           tags_only=thumb_cache.conf.tagsOnly)
            
            # FIXME hack to use db_currentVersion for convenience
            # it's not an actual field
            self.vistrail.db_currentVersion = self.current_version
            if self.locator != locator:
                old_locator = self.get_locator()
                self.locator = locator
                save_bundle = self.locator.save_as(save_bundle, version)
                new_vistrail = save_bundle.vistrail
                if type(self.locator) == core.db.locator.DBLocator:
                    new_vistrail.db_log_filename = None
                self.set_file_name(locator.name)
                if old_locator:
                    old_locator.clean_temporaries()
                    old_locator.close()
            else:
                save_bundle = self.locator.save(save_bundle)
                new_vistrail = save_bundle.vistrail
            # FIXME abstractions only work with FileLocators right now
            if is_abstraction:
                new_vistrail.is_abstraction = True
                if ( type(self.locator) == core.db.locator.XMLFileLocator or
                     type(self.locator) == core.db.locator.ZIPFileLocator ):
                    filename = self.locator.name
                    self.load_abstraction(filename, True)
            if id(self.vistrail) != id(new_vistrail):
                new_version = new_vistrail.db_currentVersion
                self.set_vistrail(new_vistrail, locator)
                self.change_selected_version(new_version)
                result = True
            if self.log:
                self.log.delete_all_workflow_execs()
            self.set_changed(False)
            if abs_save_dir is not None:
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

    def write_expanded_workflow(self, locator):
        if self.current_pipeline:
            (workflow, _) = core.db.io.expand_workflow(self.vistrail, 
                                                       self.current_pipeline)
            locator.save_as(workflow)
        
    
    def write_log(self, locator):
        if self.log:
            if self.vistrail.db_log_filename is not None:
                log = core.db.io.merge_logs(self.log, 
                                            self.vistrail.db_log_filename)
            else:
                log = self.log
            print log
            save_bundle = SaveBundle(log.vtType,log=log)
            locator.save_as(save_bundle)

    def write_registry(self, locator):
        registry = core.modules.module_registry.get_module_registry()
        save_bundle = SaveBundle(registry.vtType, registry=registry)
        locator.save_as(save_bundle)

    def update_checkout_version(self, app=''):
        self.vistrail.update_checkout_version(app)
