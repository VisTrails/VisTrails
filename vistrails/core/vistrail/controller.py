############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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

from core.configuration import get_vistrails_configuration
import core.db.io
from core.modules.abstraction import identifier as abstraction_pkg
from core.modules.basic_modules import identifier as basic_pkg
import core.modules.module_registry
from core.modules.module_registry import ModuleRegistryException, \
    MissingModuleVersion, MissingModule
from core.modules.sub_module import new_abstraction, read_vistrail
from core.utils import VistrailsInternalError, PortAlreadyExists
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

class VistrailController(object):
    def __init__(self, vistrail=None, id_scope=None):
        self.vistrail = vistrail
        self.id_scope = id_scope
        if vistrail is not None:
            self.id_scope = vistrail.idScope

    def set_vistrail(self, vistrail):
        self.vistrail = vistrail
        if vistrail is not None:
            self.id_scope = vistrail.idScope

    def set_id_scope(self, id_scope):
        self.id_scope = id_scope

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
                abstractions.extend(
                    self.find_abstractions(abstraction.vistrail, recurse))
        return abstractions
        
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
            try:
                print abstraction.package, abstraction.name, \
                    abstraction.namespace, abstraction.internal_version
                descriptor = abstraction.module_descriptor
            except MissingModuleVersion, e:
                # just change the version...
                reg = core.modules.module_registry.get_module_registry()
                other_desc = reg.get_descriptor_by_name(e._identifier,
                                                        e._name,
                                                        e._namespace,
                                                        e._package_version)
                self.load_abstraction(other_desc.module.vt_fname, 
                                      False, abstraction.name, 
                                      abstraction.internal_version)
            except MissingModule, e:
                # missing the whole module
                if abstraction.name not in lookup:
                    raise
                abs_fname = lookup[abstraction.name]
                self.load_abstraction(abs_fname, False, abstraction.name,
                                      abstraction.internal_version, abs_fnames)
                descriptor = abstraction.module_descriptor                
            except ModuleRegistryException, e:
                # shouldn't get here...
                raise
            
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
                neighbors = open_ports[(connection.source.name, 'output')]
                input_module = \
                    full_pipeline.modules[connection.destination.moduleId]
                input_port = connection.destination.name
                for (output_module, output_port) in neighbors:
                    connections.append(self.create_connection(output_module,
                                                              output_port,
                                                              input_module,
                                                              input_port))
            elif connection.destination.moduleId == group.id:
                neighbors = open_ports[(connection.destination.name, 'input')]
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
