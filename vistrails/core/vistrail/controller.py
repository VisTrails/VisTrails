############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
from itertools import izip
import os
import uuid
import shutil
import tempfile

from core.configuration import get_vistrails_configuration
import core.db.io
import core.db.locator
from core.interpreter.default import get_default_interpreter
from core.log.controller import LogControllerFactory, DummyLogController
from core.log.log import Log
from core.modules.abstraction import identifier as abstraction_pkg
from core.modules.basic_modules import identifier as basic_pkg
import core.modules.module_registry
from core.modules.module_registry import ModuleRegistryException, \
    MissingModuleVersion, MissingModule, MissingPackageVersion
from core.modules.sub_module import new_abstraction, read_vistrail
from core.thumbnails import ThumbnailCache
from core.utils import VistrailsInternalError, PortAlreadyExists, DummyView
from core.vistrail.abstraction import Abstraction
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
from db.domain import IdScope
from db.services.io import create_temp_folder, remove_temp_folder

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
        
    def logging_on(self):
        from core.configuration import get_vistrails_configuration
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
                ThumbnailCache.getInstance().add_entries_from_vtfile(thumbnails)
        self.current_version = -1
        self.current_pipeline = None
        if self.locator != locator and self.locator is not None:
            self.locator.clean_temporaries()
        self.locator = locator
        
    def close_vistrail(self, locator):
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
    
    ##########################################################################
    # Actions, etc
    
    def perform_action(self, action):
        """ performAction(action: Action) -> timestep
        
        Performs given action on current pipeline.
        
        """
        self.current_pipeline.perform_action(action)
        self.current_version = action.db_id
        return action.db_id
    
    def add_new_action(self, action):
        """add_new_action(action) -> None

        Call this function to add a new action to the vistrail being
        controlled by the vistrailcontroller.

        FIXME: In the future, this function should watch the vistrail
        and get notified of the change.

        """
        self.vistrail.add_action(action, self.current_version, 
                                 self.current_session)
        self.set_changed(True)
        self.current_version = action.db_id

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
        return module

    def create_module(self, identifier, name, namespace='', x=0.0, y=0.0,
                      internal_version=-1):
        reg = core.modules.module_registry.get_module_registry()
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
        return module

    def create_connection(self, output_module, output_port_spec,
                          input_module, input_port_spec):
        reg = core.modules.module_registry.get_module_registry()
            
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
        reg = core.modules.module_registry.get_module_registry()
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
                value = values[i]
            else:
                value = None
            param = self.create_param(port_spec, i, value)
            params.append(param)
        return params

    def create_function(self, module, function_name, param_values=[]):
        port_spec = module.get_port_spec(function_name, 'input')
        f_id = self.id_scope.getNewId(ModuleFunction.vtType)
        new_function = ModuleFunction(id=f_id,
                                      pos=module.getNumFunctions(),
                                      name=function_name,
                                      )
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

    def update_port_spec_ops(self, module, deleted_ports, added_ports):
        op_list = []
        deleted_port_info = set()
        changed_port_info = set()
        for p in deleted_ports:
            port_info = (p[1], p[0])
            if module.has_portSpec_with_name(port_info):
                port = module.get_portSpec_by_name(port_info)
                port_sigstring = port.sigstring
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
    
    def get_connections_to(self, pipeline, module_ids):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_to(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids]

    def get_connections_from(self, pipeline, module_ids):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_from(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids]

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
        
        modules = [full_pipeline.modules[m_id] for m_id in module_ids]
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
        # self.emit(QtCore.SIGNAL("flushMoveActions()"))

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
        abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                      long(module_version))

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
                                         'namespace': namespace,
                                         'version': module_version,
                                         'hide_namespace': True,
                                         'hide_descriptor': hide_descriptor,
                                         }))
        reg.auto_add_ports(abstraction)
        if old_desc is not None:
            reg.update_module(old_desc, new_desc)

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
        abs_vistrail = read_vistrail(abs_fname)
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
        desc = self.get_abstraction_desc(abs_name, abstraction_uuid,
                                         module_version)
        if desc is None:
            print "adding", abs_name, "to registry"
            desc = self.add_abstraction_to_registry(abs_vistrail, abs_fname, 
                                                    abs_name, None, 
                                                    module_version, 
                                                    is_global, avail_fnames)
        else:
            print abs_name, "already in registry"
        return desc

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
                         save_dir=None):
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
        if os.path.exists(vt_fname):
            raise VistrailsInternalError("'%s' already exists" % \
                                             vt_fname)
        core.db.io.save_vistrail_to_xml(vistrail, vt_fname)
        return vt_fname

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
        reg = core.modules.module_registry.get_module_registry()
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
        abstractions = []
        for action in vistrail.actions:
            for operation in action.operations:
                if operation.vtType == 'add' or \
                        operation.vtType == 'change':
                    if operation.data.vtType == Abstraction.vtType:
                        abstraction = operation.data
                        if abstraction.package == abstraction_pkg:
                            abstractions.append(abstraction)
        if recurse:
            for abstraction in abstractions:
                try:
                    vistrail = abstraction.vistrail
                except MissingPackageVersion, e:
                    reg = core.modules.module_registry.get_module_registry()
                    abstraction._module_descriptor = \
                        reg.get_similar_descriptor(*abstraction.descriptor_info)
                    vistrail = abstraction.vistrail
                abstractions.extend(self.find_abstractions(vistrail, recurse))
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
                self.load_abstraction(other_desc.module.vt_fname, 
                                      False, descriptor_tuple[1],
                                      descriptor_tuple[4])
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
        for abstraction in abstractions:
            # print 'checking for abstraction "' + str(abstraction.name) + '"'
            descriptor = self.check_abstraction(abstraction.descriptor_info,
                                                lookup)
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
            if action.thumbnail is not None:
                if tags_only and action.timestep not in self.vistrail.tagMap.keys():
                    thumb_cache.remove(action.thumbnail)
                    self.vistrail.change_thumbnail("", action.timestep)
                else:
                    abs_fname = thumb_cache.get_abs_name_entry(action.thumbnail)
                    if abs_fname is not None:
                        thumbnails.append(abs_fname)
                    else:
                        self.vistrail.change_thumbnail("", action.timestep)
        return thumbnails
    
    ##########################################################################
    # Workflow Execution
    
    def execute_workflow_list(self, vistrails):
        """execute_workflow_list(vistrails: list) -> (results, bool)"""
        
        interpreter = get_default_interpreter()
        changed = False
        results = []
        for vis in vistrails:
            (locator, version, pipeline, view, aliases) = vis
            kwargs = {'locator': locator,
                      'current_version': version,
                      'view': view,
                      'logger': self.get_logger(),
                      'controller': self,
                      'aliases': aliases,
                      }
            conf = get_vistrails_configuration()
            temp_folder_used = False
            if not conf.check('spreadsheetDumpCells'):
                conf.spreadsheetDumpCells = create_temp_folder(prefix='vt_thumb')
                temp_folder_used = True
                
            result = interpreter.execute(pipeline, **kwargs)
            
            thumb_cache = ThumbnailCache.getInstance()
            if len(result.errors) == 0 and thumb_cache.conf.autoSave:
                old_thumb_name = self.vistrail.actionMap[version].thumbnail
                fname = thumb_cache.add_entry_from_cell_dump(
                                        conf.spreadsheetDumpCells, 
                                        old_thumb_name)
                if fname is not None: 
                    self.vistrail.change_thumbnail(fname, version)
                    self.set_changed(True)
                    changed = True
                
            if temp_folder_used:
                remove_temp_folder(conf.spreadsheetDumpCells)
                conf.spreadsheetDumpCells = (None, str)
                
            results.append(result)
            
        if self.logging_on():
            self.set_changed(True)
            
        if interpreter.debugger:
            interpreter.debugger.update_values()
        return (results,changed)
    
    def execute_current_workflow(self, custom_aliases=None):
        """ execute_current_workflow() -> (list, bool)
        Execute the current workflow (if exists)
        
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
                                         custom_aliases)])
            
    def change_selected_version(self, new_version):
        """ change_selected_version(new_version: int) -> None        
        Change the current vistrail version into new_version
        
        """
        def switch_version():
            #TODO: This is the simplest thing to do. Maybe we should do the
            #      same optimizations in gui.vistrail_controller
            
            if new_version == self.current_version:
                # we don't even need to check connection specs or
                # registry
                return self.current_pipeline
            else:
                return self.vistrail.getPipeline(new_version)
            
        def handle_missing_packages(e):
            """ handle_missing_packages(exception) -> Boolean

            handle_missing_package tries to fill in missing modules or
            packages in the registry. The 'exception' parameter should
            be the exception raised by the package manager.

            Returns True if changes have been made to the registry,
            which means reloading a pipeline that previously failed
            with missing packages might work now.
            """

            # if package is present, then we first let the package know
            # that the module is missing - this might trigger
            # some new modules.

            def try_to_enable_package(identifier):
                pkg = pm.identifier_is_available(identifier)
                if pkg:
                    # Ok, user wants to late-enable it. Let's give it a shot
                    try:
                        pm.late_enable_package(pkg.codepath)
                    except pkg.InitializationFailed:
                        message = """Package '%s' failed during initialization.
Please contact the developer of that package and report a bug""" % pkg.name
                        debug.critical(message)
                        return False
                    except pkg.MissingDependency, e:
                        for dependency in e.dependencies:
                            if not try_to_enable_package(dependency):
                                return False
                    except Exception, e:
                        msg = "Weird - this exception '%s' shouldn't have happened" % str(e)
                        raise VistrailsInternalError(msg)

                    # there's a new package in the system, so we retry
                    # changing the version by recursing, since other
                    # packages/modules might still be needed.
                    return True

                # Package is not available, let's try to fetch it
                rep = core.packagerepository.get_repository()
                if rep:
                    codepath = rep.find_package(identifier)
                    if codepath:
                        rep.install_package(codepath)
                        return True
                msg = "Cannot find package '%s' in\n \
list of available packages. \n \
Please install it first." % identifier
                debug.critical(msg)
                return False

            pm = get_package_manager()
            for err in e._exception_set:
                if issubclass(err.__class__, ModuleRegistryException):
                    try:
                        pkg = pm.get_package_by_identifier(err._identifier)
                        res = pkg.report_missing_module(err._name, 
                                                        err._namespace)
                        if not res:
                            msg = "Cannot find module '%s' in\n \
loaded package '%s'. A different package \
version\n might be necessary." % (err._name, pkg.name)
                            debug.critical(msg)
                            return False
#                         else:
#                             # package reported success in handling missing
#                             # module, so we retry changing the version by
#                             # recursing, since other packages/modules
#                             # might still be needed.
#                             return True
                    except pm.MissingPackage:
                        pass
                    # Ok, package is missing - let's see if user wants to
                    # late-enable it.
                    if not try_to_enable_package(err._identifier):
                        return False
                    # return try_to_enable_package(e._identifier)
                        
        if new_version == -1:
            new_pipeline = None
        else:
            try:
                new_pipeline = switch_version()
            # except ModuleRegistryException, e:
            except InvalidPipeline, e:
                # we need to rollback the current pipeline. This is
                # sort of slow, but we're going to present a dialog to
                # the user anyway, so we can get away with this
                
                # currentVersion might be -1 and so currentPipeline
                # will be None. We can't call getPipeline with -1
                if self.current_version != -1:
                    self.current_pipeline = self.vistrail.getPipeline(self.current_version)
                else:
                    assert self.current_pipeline is None
                retry = handle_missing_packages(e)
                if retry:
                    # Things changed, try again recursively.
                    return self.change_selected_version(new_version)
                else:
                    new_version = 0
                    new_pipeline = self.vistrail.getPipeline(0)
        # If execution arrives here, we handled all exceptions, so
        # assign values
        self.current_pipeline = new_pipeline
        self.current_version = new_version
        
    def write_temporary(self):
        if self.vistrail and self.changed:
            locator = self.get_locator()
            if locator:
                locator.save_temporary(self.vistrail)
                
    def write_vistrail(self, locator, version=None):
        if self.vistrail and (self.changed or self.locator != locator):
            abs_save_dir = None
            is_abstraction = self.vistrail.is_abstraction
            # FIXME make all locators work with lists of objects
            objs = [(Vistrail.vtType, self.vistrail)]
            if self.log and len(self.log.workflow_execs) > 0:
                objs.append((Log.vtType, self.log))
            abstractions = self.find_abstractions(self.vistrail, True)
            for abstraction in abstractions:
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
                    objs.append(('__file__', abs_fname))
                                                
#             for abs_fname in abstractions:
#                 objs.append(('__file__', abs_fname))
            thumb_cache = ThumbnailCache.getInstance()
            if thumb_cache.conf.autoSave:
                thumbnails = self.find_thumbnails(
                                    tags_only=thumb_cache.conf.tagsOnly)
                for thumbnail in thumbnails:
                    #print "appending: ", thumbnail
                    objs.append(('__thumb__', thumbnail))
            
            # FIXME hack to use db_currentVersion for convenience
            # it's not an actual field
            self.vistrail.db_currentVersion = self.current_version
            if self.locator != locator:
                old_locator = self.get_locator()
                self.locator = locator
                # new_vistrail = self.locator.save_as(self.vistrail)
                if type(self.locator) == core.db.locator.ZIPFileLocator:
                    objs = self.locator.save_as(objs, version)
                    new_vistrail = objs[0][1]
                else:
                    new_vistrail = self.locator.save_as(self.vistrail, version)
                    if type(self.locator) == core.db.locator.DBLocator:
                        new_vistrail.db_log_filename = None
                self.set_file_name(locator.name)
                if old_locator:
                    old_locator.clean_temporaries()
                    old_locator.close()
            else:
                # new_vistrail = self.locator.save(self.vistrail)
                if type(self.locator) == core.db.locator.ZIPFileLocator:
                    objs = self.locator.save(objs)
                    new_vistrail = objs[0][1]
                else:
                    new_vistrail = self.locator.save(self.vistrail)
            # FIXME abstractions only work with FileLocators right now
            if (is_abstraction and 
                (type(self.locator) == core.db.locator.XMLFileLocator or
                 type(self.locator) == core.db.locator.ZIPFileLocator)):
                filename = self.locator.name
                self.load_abstraction(filename, True)
            if id(self.vistrail) != id(new_vistrail):
                new_version = new_vistrail.db_currentVersion
                self.set_vistrail(new_vistrail, locator)
                self.change_selected_version(new_version)
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
            locator.save_as(pipeline)

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
            locator.save_as(log)
