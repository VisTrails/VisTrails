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
##TODO Tests
""" This module defines the class Pipeline """
from vistrails.core.cache.hasher import Hasher
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core.data_structures.graph import Graph
from vistrails.core import debug
from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.modules.module_registry import get_module_registry, \
    ModuleRegistryException, MissingModuleVersion, MissingPackage, PortMismatch
from vistrails.core.system import get_vistrails_default_pkg_prefix, \
    get_vistrails_basic_pkg_id
from vistrails.core.utils import VistrailsInternalError
from vistrails.core.utils import expression, append_to_dict_of_lists
from vistrails.core.utils.uxml import named_elements
from vistrails.core.vistrail.abstraction import Abstraction
from vistrails.core.vistrail.connection import Connection
from vistrails.core.vistrail.group import Group
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.plugin_data import PluginData
from vistrails.core.vistrail.port import Port, PortEndPoint
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.db.domain import DBWorkflow
import vistrails.core.vistrail.action
from vistrails.core.utils import profile, InvalidPipeline

from xml.dom.minidom import getDOMImplementation, parseString
import copy

import unittest
from vistrails.core.vistrail.abstraction import Abstraction
from vistrails.core.vistrail.connection import Connection
from vistrails.core.vistrail.location import Location
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.port import Port
from vistrails.db.domain import IdScope

##############################################################################

class MissingVistrailVariable(Exception):
    def __init__(self, var_uuid, identifier, name, namespace):
        self._var_uuid = var_uuid
        self._identifier = identifier
        self._name = name
        self._namespace = namespace

    def __str__(self):
        return "Missing Vistrail Variable '%s' of type %s from package %s" % (self._var_uuid,
                self._module_name, self._identifier)
        
    def __eq__(self, other):
        return type(self) == type(other) and \
            self._var_uuid == other._var_uuid and \
            self._identifier == other._identifier and \
            self._name == other._name and \
            self._namespace == other._namespace

    def __hash__(self):
        return (type(self), self._var_uuid, self._identifier,
                self._name, self._namespace).__hash__()

    def _get_module_name(self):
        if self._namespace:
            return "%s|%s" % (self._namespace, self._name)
        return self._name
    _module_name = property(_get_module_name)

class MissingFunction(Exception):
    def __init__(self, name, module_name, module_id=None):
        self.name = name
        self.module_name = module_name
        self.module_id = module_id

    def __str__(self):
        return ("Missing Function '%s' on module '%s'%s" % 
                (self.name, self.module_name, " (id %d)" % self.module_id if
                 self.module_id is not None else ""))

class CycleInPipeline(Exception):
    def __str__(self):
        return "Pipeline contains a cycle"

class Pipeline(DBWorkflow):
    """ A Pipeline is a set of modules and connections between them. """
    
    def __init__(self, *args, **kwargs):
        """ __init__() -> Pipelines
        Initializes modules, connections and graph.

        """
        self.clear()

        DBWorkflow.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = 0
        if self.name is None:
            self.name = 'untitled'
        self.set_defaults()

    def set_defaults(self, other=None):
        if other is None:
            self.is_valid = False
            self.aliases = Bidict()
            self._subpipeline_signatures = Bidict()
            self._module_signatures = Bidict()
            self._connection_signatures = Bidict()
        else:
            self.is_valid = other.is_valid
            self.aliases = Bidict([(k,copy.copy(v))
                                   for (k,v) in other.aliases.iteritems()])
            self._connection_signatures = \
                Bidict([(k,copy.copy(v))
                        for (k,v) in other._connection_signatures.iteritems()])
            self._subpipeline_signatures = \
                Bidict([(k,copy.copy(v))
                        for (k,v) in other._subpipeline_signatures.iteritems()])
            self._module_signatures = \
                Bidict([(k,copy.copy(v))
                        for (k,v) in other._module_signatures.iteritems()])

        self.graph = Graph()
        for module in self.module_list:
            self.graph.add_vertex(module.id)
            # there should be another way to do this
            m_id = module.id
            for fun in module.functions:
                for par in fun.parameters:
                    self.change_alias(par.alias,
                                      par.vtType,
                                      par.real_id,
                                      fun.vtType,
                                      fun.real_id,
                                      m_id)
            module.connected_input_ports = {}
            module.connected_output_ports = {}

        for connection in self.connection_list:
            self.graph.add_edge(connection.source.moduleId,
                                connection.destination.moduleId,
                                connection.id)
            c = connection
            source_name = c.source.name
            output_ports = self.modules[c.sourceId].connected_output_ports
            if source_name not in output_ports:
                output_ports[source_name] = 0
            output_ports[source_name] += 1
                
            dest_name = c.destination.name
            input_ports = self.modules[c.destinationId].connected_input_ports
            if dest_name not in input_ports:
                input_ports[dest_name] = 0
            input_ports[dest_name] += 1
            
    def __copy__(self):
        """ __copy__() -> Pipeline - Returns a clone of itself """ 
        return Pipeline.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflow.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Pipeline
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_workflow):
        if _workflow.__class__ == Pipeline:
            return
        # do clear plus get the modules and connections
        _workflow.__class__ = Pipeline
        for _module in _workflow.db_modules:
            if _module.vtType == Module.vtType:
                Module.convert(_module)
            elif _module.vtType == Abstraction.vtType:
                Abstraction.convert(_module)
            elif _module.vtType == Group.vtType:
                Group.convert(_module)
        for _connection in _workflow.db_connections:
            Connection.convert(_connection)
        for _plugin_data in _workflow.db_plugin_datas:
            PluginData.convert(_plugin_data)
        _workflow.set_defaults()

    ##########################################################################

    def find_method(self, module_id, parameter_name):
        """find_method(module_id, parameter_name) -> int.

        Finds the function_id for a given method name.
        Returns -1 if method name is not there.

        WARNING: Might not work for overloaded methods (where types
        also matter)
        """
        try:
            return [f.name
                    for f
                    in self.get_module_by_id(module_id).functions].index(parameter_name)
        except ValueError:
            return -1

    ##########################################################################
    # Properties

    id = DBWorkflow.db_id
    name = DBWorkflow.db_name
    plugin_datas = DBWorkflow.db_plugin_datas

    def _get_modules(self):
        return self.db_modules_id_index
    modules = property(_get_modules)
    def _get_module_list(self):
        return self.db_modules
    module_list = property(_get_module_list)

    def _get_connections(self):
        return self.db_connections_id_index
    connections = property(_get_connections)
    def _get_connection_list(self):
        return self.db_connections
    connection_list = property(_get_connection_list)

    def clear(self):
        """clear() -> None. Erases pipeline contents."""
        if hasattr(self, 'db_modules'):
            for module in self.db_modules:
                self.db_delete_module(module)
        if hasattr(self, 'db_connections'):
            for connection in self.db_connections:
                self.db_delete_connection(connection)
        self.graph = Graph()
        self.aliases = Bidict()
        self._subpipeline_signatures = Bidict()
        self._module_signatures = Bidict()
        self._connection_signatures = Bidict()

    def get_tmp_id(self, type):
        """get_tmp_id(type: str) -> long
        returns a temporary id for a workflow item.  Use the idScope on the
        vistrail for permanent ids.
        """

        return -self.tmp_id.getNewId(type)

    def fresh_module_id(self):
        return self.get_tmp_id(Module.vtType)
    def fresh_connection_id(self):
        return self.get_tmp_id(Connection.vtType)

    def check_connection(self, c):
        """check_connection(c: Connection) -> boolean 
        Checks semantics of connection
          
        """
        if c.source.endPoint != Port.SourceEndPoint:
            return False
        if c.destination.endPoint != Port.DestinationEndPoint:
            return False
        if not self.has_module_with_id(c.sourceId):
            return False
        if not self.has_module_with_id(c.destinationId):
            return False
        if c.source.type != c.destination.type:
            return False
        return True
    
    def connects_at_port(self, p):
        """ connects_at_port(p: Port) -> list of Connection 
        Returns a list of Connections that connect at port p
        
        """
        result = []
        if p.endPoint == Port.DestinationEndPoint:
            el = self.graph.edges_to(p.moduleId)
            for (edgeto, edgeid) in el:
                dest = self.connection[edgeid].destination
                if VTKRTTI().intrinsicPortEqual(dest, p):
                    result.append(self.connection[edgeid])
        elif p.endPoint == Port.SourceEndPoint:
            el = self.graph.edges_from(p.moduleId)
            for (edgeto, edgeid) in el:
                source = self.connection[edgeid].source
                if VTKRTTI().intrinsicPortEqual(source, p):
                    result.append(self.connection[edgeid])
        else:
            raise VistrailsInternalError("port with bogus information")
        return result

    def connections_to_module(self, moduleId):
        """ connections_to_module(int moduleId) -> list of module ids
        returns a list of module ids that are inputs to the given moduleId

        """

        modules = []
        for edge in self.graph.edges_to(moduleId):
            modules.append(self.modules[edge[0]].id)
        return modules

    def get_inputPort_modules(self, moduleId, portName):
        """ get_inputPort_modules(int moduleId, string portName)-> list of module ids
        returns a list of module ids that are the input to a given port
        on a given module

        """
        modules = []
        for edge in self.graph.edges_to(moduleId):
            if self.connections[edge[1]].destination.name == portName:
                modules.append(self.modules[edge[0]].id)
        return modules

    def get_outputPort_modules(self, moduleId, portName):
        """ get_outputPort_modules(int moduleId, string portName)-> list of module ids
        returns a list of module ids that are the output to a given port
        on a given module
        """
        modules = []
        for edge in self.graph.edges_from(moduleId):
            if self.connections[edge[1]].source.name == portName:
                modules.append(self.modules[edge[0]].id)
        return modules

    def perform_action_chain(self, actionChain):
        # BEWARE: if actionChain is long, you're probably better off
        # going through general_action_chain, because it optimizes
        # away unnecessary operations.
        for action in actionChain:
            self.perform_action(action)

    def perform_action(self, action):
#         print "+++"
#         for operation in action.operations:
#             print operation.vtType, operation.what, operation.old_obj_id, \
#                 operation.new_obj_id, operation.parentObjType, operation.parentObjId
#         print "---"
        for operation in action.operations:
            self.perform_operation(operation)

    def perform_operation_chain(self, opChain):
        for op in opChain:
            self.perform_operation(op)

    def perform_operation(self, op):
        # print "doing %s %s %s" % (op.id, op.vtType, op.what)
        if op.db_what == 'abstraction' or op.db_what == 'group':
            what = 'module'
        else:
            what = op.db_what
        funname = '%s_%s' % (op.vtType, what)
        try:
            f = getattr(self, funname)
        except AttributeError:
            db_funname = 'db_%s_object' % op.vtType
            try:
                f = getattr(self, db_funname)
            except AttributeError:
                msg = "Pipeline cannot execute '%s %s' operation" % \
                    (op.vtType, op.what)
                raise VistrailsInternalError(msg)

        if op.vtType == 'add':
            f(op.data, op.parentObjType, op.parentObjId)
        elif op.vtType == 'delete':
            f(op.objectId, op.what, op.parentObjType, op.parentObjId)
        elif op.vtType == 'change':
            f(op.oldObjId, op.data, op.parentObjType, op.parentObjId)

    def add_module(self, m, *args):
        """add_module(m: Module) -> None 
        Add new module to pipeline
          
        """
        if self.has_module_with_id(m.id):
            raise VistrailsInternalError("duplicate module id: %d" % m.id )
#         self.modules[m.id] = copy.copy(m)
#         if m.vtType == Abstraction.vtType:
#             m.abstraction = self.abstraction_map[m.abstraction_id]
        self.db_add_object(m)
        self.graph.add_vertex(m.id)

    def change_module(self, old_id, m, *args):
        if not self.has_module_with_id(old_id):
            raise VistrailsInternalError("module %s doesn't exist" % old_id)
        self.db_change_object(old_id, m)
        self.graph.delete_vertex(old_id)
        self.graph.add_vertex(m.id)

    def delete_module(self, id, *args):
        """delete_module(id:int) -> None 
        Delete a module from pipeline given an id.

        """
        if not self.has_module_with_id(id):
            raise VistrailsInternalError("id missing in modules")

        # we're hiding the necessary operations by doing this!
        for (_, conn_id) in self.graph.adjacency_list[id][:]:
            self.delete_connection(conn_id)
        for (_, conn_id) in self.graph.inverse_adjacency_list[id][:]:
            self.delete_connection(conn_id)

        # self.modules.pop(id)
        self.db_delete_object(id, Module.vtType)
        self.graph.delete_vertex(id)
        if id in self._module_signatures:
            del self._module_signatures[id]
        if id in self._subpipeline_signatures:
            del self._subpipeline_signatures[id]

    def add_connection(self, c, *args):
        """add_connection(c: Connection) -> None 
        Add new connection to pipeline.
          
        """
        if self.has_connection_with_id(c.id):
            raise VistrailsInternalError("duplicate connection id " + str(c.id))
#         self.connections[c.id] = copy.copy(c)
        self.db_add_object(c)
        if c.source is not None and c.destination is not None:
            assert(c.sourceId != c.destinationId)        
            self.graph.add_edge(c.sourceId, c.destinationId, c.id)
            self.ensure_connection_specs([c.id])

            source_name = c.source.name
            output_ports = self.modules[c.sourceId].connected_output_ports
            if source_name not in output_ports:
                output_ports[source_name] = 0
            output_ports[source_name] += 1
                
            dest_name = c.destination.name
            input_ports = self.modules[c.destinationId].connected_input_ports
            if dest_name not in input_ports:
                input_ports[dest_name] = 0
            input_ports[dest_name] += 1

    def change_connection(self, old_id, c, *args):
        """change_connection(old_id: long, c: Connection) -> None
        Deletes connection identified by old_id and adds connection c

        """
        if not self.has_connection_with_id(old_id):
            raise VistrailsInternalError("connection %s doesn't exist" % old_id)

        old_conn = self.connections[old_id]
        if old_conn.source is not None and old_conn.destination is not None:
            self.graph.delete_edge(old_conn.sourceId, old_conn.destinationId,
                                   old_conn.id)
            if self.graph.out_degree(old_conn.sourceId) < 1:
                self.modules[old_conn.sourceId].connected_output_ports.discard(
                    conn.source.name)
            if self.graph.in_degree(old_conn.destinationId) < 1:
                connected_input_ports = \
                    self.modules[old_conn.destinationId].connected_input_ports
                connected_input_ports.discard(conn.destination.name)

        if old_id in self._connection_signatures:
            del self._connection_signatures[old_id]
        self.db_change_object(old_id, c)        
        if c.source is not None and c.destination is not None:
            assert(c.sourceId != c.destinationId)
            self.graph.add_edge(c.sourceId, c.destinationId, c.id)
            self.ensure_connection_specs([c.id])
            self.modules[c.sourceId].connected_output_ports.add(c.source.name)
            self.modules[c.destinationId].connected_input_ports.add(
                c.destination.name)

    def delete_connection(self, id, *args):
        """ delete_connection(id:int) -> None 
        Delete connection identified by id from pipeline.
           
        """

        if not self.has_connection_with_id(id):
            raise VistrailsInternalError("id %s missing in connections" % id)
        conn = self.connections[id]
        # self.connections.pop(id)
        self.db_delete_object(id, 'connection')
        if conn.source is not None and conn.destination is not None and \
                (conn.destinationId, conn.id) in \
                self.graph.edges_from(conn.sourceId):
            self.graph.delete_edge(conn.sourceId, conn.destinationId, conn.id)

            c = conn
            source_name = c.source.name
            output_ports = self.modules[c.sourceId].connected_output_ports
            output_ports[source_name] -= 1
                
            dest_name = c.destination.name
            input_ports = self.modules[c.destinationId].connected_input_ports
            input_ports[dest_name] -= 1

        if id in self._connection_signatures:
            del self._connection_signatures[id]
        
    def add_parameter(self, param, parent_type, parent_id):
        self.db_add_object(param, parent_type, parent_id)
        if not self.has_alias(param.alias):
            self.change_alias(param.alias, 
                              param.vtType, 
                              param.real_id,
                              parent_type,
                              parent_id,
                              None)

    def delete_parameter(self, param_id, param_type, parent_type, parent_id):
        self.db_delete_object(param_id, ModuleParam.vtType,
                              parent_type, parent_id)
        self.remove_alias(ModuleParam.vtType, param_id, parent_type, 
                          parent_id, None)

    def change_parameter(self, old_param_id, param, parent_type, parent_id):
        self.remove_alias(ModuleParam.vtType, old_param_id, 
                          parent_type, parent_id, None)
        self.db_change_object(old_param_id, param,
                              parent_type, parent_id)
        if not self.has_alias(param.alias):
            self.change_alias(param.alias, 
                              param.vtType, 
                              param.real_id,
                              parent_type,
                              parent_id,
                              None)

    def add_port(self, port, parent_type, parent_id):
        self.db_add_object(port, parent_type, parent_id)
        connection = self.connections[parent_id]
        if connection.source is not None and \
                connection.destination is not None:
            self.graph.add_edge(connection.sourceId, 
                                connection.destinationId, 
                                connection.id)
            c = connection
            source_name = c.source.name
            output_ports = self.modules[c.sourceId].connected_output_ports
            if source_name not in output_ports:
                output_ports[source_name] = 0
            output_ports[source_name] += 1
                
            dest_name = c.destination.name
            input_ports = self.modules[c.destinationId].connected_input_ports
            if dest_name not in input_ports:
                input_ports[dest_name] = 0
            input_ports[dest_name] += 1

    def delete_port(self, port_id, port_type, parent_type, parent_id):
        conn = self.connections[parent_id]
        if len(conn.ports) >= 2:
            self.graph.delete_edge(conn.sourceId, 
                                   conn.destinationId, 
                                   conn.id)
            c = conn
            source_name = c.source.name
            output_ports = self.modules[c.sourceId].connected_output_ports
            output_ports[source_name] -= 1
                
            dest_name = c.destination.name
            input_ports = self.modules[c.destinationId].connected_input_ports
            input_ports[dest_name] -= 1
            
        self.db_delete_object(port_id, Port.vtType, parent_type, parent_id)

    def change_port(self, old_port_id, port, parent_type, parent_id):
        connection = self.connections[parent_id]
        if len(connection.ports) >= 2:
            source_list = self.graph.adjacency_list[connection.sourceId]
            source_list.remove((connection.destinationId, connection.id))
            dest_list = \
                self.graph.inverse_adjacency_list[connection.destinationId]
            dest_list.remove((connection.sourceId, connection.id))
        self.db_change_object(old_port_id, port, parent_type, parent_id)
        if len(connection.ports) >= 2:
            source_list = self.graph.adjacency_list[connection.sourceId]
            source_list.append((connection.destinationId, connection.id))
            dest_list = \
                self.graph.inverse_adjacency_list[connection.destinationId]
            dest_list.append((connection.sourceId, connection.id))

    def add_port_to_registry(self, portSpec, moduleId):
        m = self.get_module_by_id(moduleId)
        m.add_port_spec(portSpec)

    def add_portSpec(self, port_spec, parent_type, parent_id):
        # self.db_add_object(port_spec, parent_type, parent_id)
        self.add_port_to_registry(port_spec, parent_id)
        
    def delete_port_from_registry(self, id, moduleId):
        m = self.get_module_by_id(moduleId)
        portSpec = m.port_specs[id]
        m.delete_port_spec(portSpec)

    def delete_portSpec(self, spec_id, portSpec_type, parent_type, parent_id):
        self.delete_port_from_registry(spec_id, parent_id)
        # self.db_delete_object(spec_id, PortSpec.vtType, parent_type, parent_id)

    def change_portSpec(self, old_spec_id, port_spec, parent_type, parent_id):
        self.delete_port_from_registry(old_spec_id, parent_id)
        # self.db_change_object(old_spec_id, port_spec, parent_type, parent_id)
        self.add_port_to_registry(port_spec, parent_id)

    def add_alias(self, name, type, oId, parentType, parentId, mId):
        """add_alias(name: str, oId: int, parentType:str, parentId: int, 
                     mId: int) -> None 
        Add alias to pipeline
          
        """
        if self.has_alias(name):
            raise VistrailsInternalError("duplicate alias")
        if mId is not None:
            self.aliases[name] = (type, oId, parentType, parentId, mId)
        else:
            mid = None
            for _mod in self.modules.itervalues():
                for _fun in _mod.functions:
                    for _par in _fun.parameters:
                        if (_par.vtType == type and _par.real_id == oId and
                            _fun.vtType == parentType and 
                            _fun.real_id == parentId):
                            mid = _mod.id
                            break
            if mid is not None:
                self.aliases[name] = (type, oId, parentType, parentId, mid)
                
    def remove_alias_by_name(self, name):
        """remove_alias_by_name(name: str) -> None
        Remove alias with given name """
        if self.has_alias(name):
            del self.aliases[name]

    def remove_alias(self, type, oId, parentType, parentId, mId):
        """remove_alias(name: str, type:str, oId: int, parentType: str, 
                        parentId: int, mId: int)-> None
        Remove alias identified by oId """
        if mId is not None:
            try:
                oldname = self.aliases.inverse[(type,oId, parentType, parentId, mId)]
                del self.aliases[oldname]
            except KeyError:
                pass
        else:
            oldname = None
            for aname,(t,o,pt,pid,mid) in self.aliases.iteritems():
                if (t == type and o == oId and pt == parentType and 
                    pid == parentId):
                    oldname = aname
                    break
            if oldname:
                del self.aliases[oldname]

    def change_alias(self, name, type, oId, parentType, parentId, mId):
        """change_alias(name: str, type:str oId:int, parentType:str,
                        parentId:int, mId: int)-> None
        Change alias if name is non empty. Else remove alias
        
        """
        if name == "":
            self.remove_alias(type, oId, parentType, parentId, mId)
        else:
            if not self.has_alias(name):
                self.remove_alias(type, oId, parentType, parentId, mId)
                self.add_alias(name, type, oId, parentType, parentId, mId)
                
    def get_alias_str_value(self, name):
        """ get_alias_str_value(name: str) -> str
        returns the strValue of the parameter with alias name

        """
        try:
            what, oId, parentType, parentId, mId = self.aliases[name]
        except KeyError:
            return ''
        else:
            if what == 'parameter':
                parameter = self.db_get_object(what, oId)
                return parameter.strValue
            else:
                raise VistrailsInternalError("only parameters are supported")

    def set_alias_str_value(self, name, value):
        """ set_alias_str_value(name: str, value: str) -> None
        sets the strValue of the parameter with alias name 
        
        """
        try:
            what, oId, parentType, parentId, mId = self.aliases[name]
        except KeyError:
            pass
        else:
            if what == 'parameter':
                #FIXME: check if a change parameter action needs to be generated
                parameter = self.db_get_object(what, oId)
                parameter.strValue = str(value)
            else:
                raise VistrailsInternalError("only parameters are supported")
        
    def get_module_by_id(self, id):
        """get_module_by_id(id: int) -> Module
        Accessor. id is the Module id.
        
        """
        result = self.modules[id]
        if result.vtType != Abstraction.vtType and \
                result.vtType != Group.vtType and result.package is None:
            registry = get_module_registry()
            debug.critical('module %d is missing package' % id)
            descriptor = registry.get_descriptor_from_name_only(result.name)
            result.package = descriptor.identifier
        return result
    
    def get_connection_by_id(self, id):
        """get_connection_by_id(id: int) -> Connection
        Accessor. id is the Connection id.
        
        """
        self.ensure_connection_specs([id])
        return self.connections[id]
    
    def module_count(self):
        """ module_count() -> int 
        Returns the number of modules in the pipeline.
        
        """
        return len(self.modules)
    
    def connection_count(self):
        """connection_count() -> int 
        Returns the number of connections in the pipeline.
        
        """
        return len(self.connections)
    
    def has_module_with_id(self, id):
        """has_module_with_id(id: int) -> boolean 
        Checks whether given module exists.

        """
        return id in self.modules
    
    def has_connection_with_id(self, id):
        """has_connection_with_id(id: int) -> boolean 
        Checks whether given connection exists.

        """
        return id in self.connections

    def has_alias(self, name):
        """has_alias(name: str) -> boolean 
        Checks whether given alias exists.

        """
        return name in self.aliases

    def out_degree(self, id):
        """out_degree(id: int) -> int - Returns the out-degree of a module. """
        return self.graph.out_degree(id)

    ##########################################################################
    # Caching-related

    # Modules

    def module_signature(self, module_id):
        """module_signature(module_id): string
        Returns the signature for the module with given module_id."""
        try:
            return self._module_signatures[module_id]
        except KeyError:
            registry = get_module_registry()
            m = self.modules[module_id]
            sig = registry.module_signature(self, m)
            self._module_signatures[module_id] = sig
            return sig
    
    def module_id_from_signature(self, signature):
        """module_id_from_signature(sig): int
        Returns the module_id that corresponds to the given signature.
        This must have been previously computed."""
        return self._module_signatures.inverse[signature]

    def has_module_signature(self, signature):
        return signature in self._module_signatures.inverse

    # Subpipelines

    def subpipeline_signature(self, module_id, visited_ids=None):
        """subpipeline_signature(module_id): string
        Returns the signature for the subpipeline whose sink id is module_id."""
        if visited_ids is None:
            visited_ids = set([module_id])
        elif module_id in visited_ids:
            raise CycleInPipeline()
        try:
            return self._subpipeline_signatures[module_id]
        except KeyError:
            upstream_sigs = [(self.subpipeline_signature(
                                      m,
                                      visited_ids | set([module_id])) +
                              Hasher.connection_signature(
                                      self.connections[edge_id]))
                             for (m, edge_id) in
                             self.graph.edges_to(module_id)]
            module_sig = self.module_signature(module_id)
            sig = Hasher.subpipeline_signature(module_sig,
                                               upstream_sigs)
            self._subpipeline_signatures[module_id] = sig
            return sig

    def subpipeline_id_from_signature(self, signature):
        """subpipeline_id_from_signature(sig): int
        Returns the module_id that corresponds to the given signature.
        This must have been previously computed."""
        return self._subpipeline_signatures.inverse[signature]

    def has_subpipeline_signature(self, signature):
        return signature in self._subpipeline_signatures.inverse

    # Connections

    def connection_signature(self, connection_id):
        """connection_signature(id): string
        Returns the signature for the connection with given id."""
        try:
            return self._connection_signatures[connection_id]
        except KeyError:
            c = self.connections[connection_id]
            source_sig = self.subpipeline_signature(c.sourceId)
            dest_sig = self.subpipeline_signature(c.destinationId)
            sig = Hasher.connection_subpipeline_signature(c, source_sig,
                                                          dest_sig)
            self._connection_signatures[connection_id] = sig
            return sig

    def connection_id_from_signature(self, signature):
        return self._connection_signatures.inverse[signature]

    def has_connection_signature(self, signature):
        return signature in self._connection_signatures.inverse

    def refresh_signatures(self):
        self._connection_signatures = {}
        self._subpipeline_signatures = {}
        self._module_signatures = {}
        self.compute_signatures()

    def compute_signatures(self):
        """compute_signatures(): compute all module and subpipeline signatures
        for this pipeline."""
        for i in self.modules.iterkeys():
            self.subpipeline_signature(i)
        for c in self.connections.iterkeys():
            self.connection_signature(c)

    def get_subpipeline(self, module_set):
        """get_subpipeline([module_id] or subgraph) -> Pipeline

        Returns a subset of the current pipeline with the modules passed
        in as module_ids and the internal connections between them."""
        if isinstance(module_set, list):
            subgraph = self.graph.subgraph(module_set)
        elif isinstance(module_set, Graph):
            subgraph = module_set
        else:
            raise TypeError("Expected list of ints or graph")
        result = Pipeline()
        for module_id in subgraph.iter_vertices():
            result.add_module(copy.copy(self.modules[module_id]))
        for (conn_from, conn_to, conn_id) in subgraph.iter_all_edges():
            result.add_connection(copy.copy(self.connections[conn_id]))
                # TODO : I haven't finished this yet. -cscheid
        raise NotImplementedError
        return result

    ##########################################################################
    # Registry-related

    def validate(self, raise_exception=True, vistrail_vars={}):
        # want to check entire pipeline and reconcile it with the
        # registry - if anything fails, generate invalid pipeline with
        # the errors
        exceptions = set()
        try:
            self.ensure_modules_are_on_registry()
        except InvalidPipeline, e:
            exceptions.update(e.get_exception_set())

        # do this before we check connection specs because it is
        # possible that a subpipeline invalidates the module, meaning
        # we shouldn't check the connection specs
        for module in self.modules.itervalues():
            if module.is_valid and (module.is_group() or 
                                    module.is_abstraction()):
                try:
                    subpipeline = module.pipeline
                    if subpipeline is not None:
                        subpipeline.validate()
                except InvalidPipeline, e:
                    module.is_valid = False
                    e._module_id = module.id
                    exceptions.add(e)
                if module.is_abstraction():
                    try:
                        desc = module.module_descriptor
                        if long(module.internal_version) != long(desc.version):
                            exceptions.add(MissingModuleVersion(desc.package, desc.name, desc.namespace, desc.version, desc.package_version, module.id))
                    except Exception:
                        pass
        try:
            self.ensure_port_specs()
        except InvalidPipeline, e:
            exceptions.update(e.get_exception_set())
        try:
            self.ensure_connection_specs()
        except InvalidPipeline, e:
            exceptions.update(e.get_exception_set())
        try:
            self.ensure_functions()
        except InvalidPipeline, e:
            exceptions.update(e.get_exception_set())
        try:
            self.ensure_vistrail_variables(vistrail_vars)
        except InvalidPipeline, e:
            exceptions.update(e.get_exception_set())
        
        self.check_subworkflow_versions()
        
        if len(exceptions) > 0:
            if raise_exception:
                raise InvalidPipeline(exceptions, self)
            else:
                self.is_valid = False
                return False

        self.mark_list_depth()

        self.is_valid = True
        return True

    def ensure_old_modules_have_package_names(self):
        """ensure_old_modules_have_package_names()

        Makes sure each module has a package associated with it.

        """
        for i in self.modules.iterkeys():
            self.get_module_by_id(i)

    def ensure_connection_specs(self, connection_ids=None):
        """ensure_connection_specs(connection_ids=None) -> None.

        Computes the specs for the connections in connection_ids. If
        connection_ids is None, computes it for every connection in the pipeline.
        """
        exceptions = set()

        # print 'ensure_connection_specs:', sorted(self.modules.keys())

        def find_spec(port):
            port.is_valid = False
            module = self.get_module_by_id(port.moduleId)
            port_type_map = PortSpec.port_type_map
            try:
                # print 'running get_port_spec', port.name
                port.spec = module.get_port_spec(port.name, 
                                            port_type_map.inverse[port.type])
                # print 'got spec', spec, spec.sigstring
            except ModuleRegistryException, e:
                # debug.critical('CONNECTION EXCEPTION: %s' % e)
                exceptions.add(e)
            else:
                if port.spec.is_valid:
                    port.is_valid = True
            
        if connection_ids is None:
            connection_ids = self.connections.iterkeys()
        for conn_id in connection_ids:
            conn = self.connections[conn_id]
            # print 'checking connection', conn_id, conn.source.moduleId, conn.source.moduleName, conn.source.name, conn.destination.moduleId, conn.destination.moduleName, conn.destination.name
            src_module = self.modules[conn.source.moduleId]
            if src_module.is_valid:
                # print 'src_module:', src_module.name, src_module.id
                find_spec(conn.source)
            
            dst_module = self.modules[conn.destination.moduleId]
            if dst_module.is_valid:
                # print 'dst_module:', dst_module.name, dst_module.id
                find_spec(conn.destination)

            # if not conn.source.spec:
            # conn.source.spec = find_spec(conn.source)
            # if not conn.destination.spec:
            # conn.destination.spec = find_spec(conn.destination)
            # print 'source spec:', conn.source.spec.sigstring
            # print 'dest spec:', conn.destination.spec.sigstring

        if len(exceptions) > 0:
            raise InvalidPipeline(exceptions, self)

    def ensure_modules_are_on_registry(self, module_ids=None):
        """ensure_modules_are_on_registry(module_ids: optional list of module ids) -> None

        Queries the module registry for the module information in the
        given modules.  The only goal of this function is to trigger
        exceptions in the registry that will be treated somewhere else
        in the calling stack.
        
        If modules are not on registry, the registry will raise
        ModuleRegistryException exceptions that should be caught and handled.

        if no module_ids list is given, we assume every module in the pipeline.
        """
        def find_descriptors(pipeline, module_ids=None):
            registry = get_module_registry()
            conf = get_vistrails_configuration()
            if module_ids == None:
                module_ids = pipeline.modules.iterkeys()
            exceptions = set()
            for mid in module_ids:
                module = pipeline.modules[mid]
                module.is_valid = False
                if not module.version:
                    module.version = '0'
                try:
                    # FIXME check for upgrades, otherwise use similar
                    # descriptor, the old behavior
                    descriptor = module.module_descriptor
                except ModuleRegistryException, e:
                    e._module_id = mid
                    exceptions.add(e)
                else:
                    module.is_valid = True
            return exceptions
        # end find_descriptors

        exceptions = find_descriptors(self, module_ids)
        if len(exceptions) > 0:
            raise InvalidPipeline(exceptions, self)

    def ensure_functions(self):
        exceptions = set()
        reg = get_module_registry()
        for module in self.modules.itervalues():
            for function in module.functions:
                is_valid = True
                if module.is_valid and not module.has_port_spec(function.name, 
                                                                'input'):
                    is_valid = False
                    e = MissingFunction(function.name, module.name, module.id)
                    e._module_id = module.id
                    exceptions.add(e)
                pos_map = {}
                for p in function.parameters:
                    if p.identifier == '':
                        idn = get_vistrails_basic_pkg_id()
                    else:
                        idn = p.identifier

                    try:
                        desc = reg.get_module_by_name(idn,
                                                      p.type,
                                                      p.namespace)
                    except ModuleRegistryException, e:
                        is_valid = False
                        e._module_id = module.id
                        exceptions.add(e)

                    if p.pos in pos_map:
                        is_valid = False
                        e = VistrailsInternalError("Module %d has multiple "
                                                   "values for parameter %d "
                                                   "of function %s (%d)" % \
                                                       (module.id,
                                                        p.pos,
                                                        function.name,
                                                        function.real_id))
                        exceptions.add(e)
                    pos_map[p.pos] = p
                function.is_valid = is_valid
        if len(exceptions) > 0:
            raise InvalidPipeline(exceptions, self)
        
    def ensure_vistrail_variables(self, vistrail_vars):
        var_uuids = [var.uuid for var in vistrail_vars]
        exceptions = set()
        for module in self.modules.itervalues():
            if module.is_vistrail_var():
                # first check if value is already set
                # (used by parameter explorations)
                value_set = False
                for func in module.functions:
                    if func.name == 'value':
                        if func.params[0].strValue:
                            value_set = True
                            continue
                if value_set:
                    continue
                var_uuid = module.get_vistrail_var()
                if var_uuid not in var_uuids:
                    e = MissingVistrailVariable(var_uuid, module.package, 
                                                module.name, module.namespace)
                    exceptions.add(e)
        if len(exceptions) > 0:
            raise InvalidPipeline(exceptions, self)

    def ensure_port_specs(self):
        exceptions = set()
        for module in self.modules.itervalues():
            # if module.is_valid:
            try:
                for port_spec in module.port_specs.itervalues():
                    try:
                        port_spec.descriptors()
                    except MissingPackage, e:
                        port_spec.is_valid = False
                        e._module_id = module.id
                        exceptions.add(e)
                    except ModuleRegistryException, e:
                        e = PortMismatch(module.package, module.name,
                                         module.namespace, port_spec.name,
                                         port_spec.type, port_spec.sigstring)
                        port_spec.is_valid = False
                        e._module_id = module.id
                        exceptions.add(e)
            except ModuleRegistryException, e:
                if module.is_valid:
                    module.is_valid = False
    
        if len(exceptions) > 0:
            raise InvalidPipeline(exceptions, self)

    def check_subworkflow_versions(self):
        reg = get_module_registry()
        for module in self.modules.itervalues():
            if module.is_valid and module.is_abstraction():
                module.check_latest_version()

    def mark_list_depth(self):
        """mark_list_depth() -> list

        Updates list_depth variable on each module according to list depth of
        connecting port specs. This decides at what list depth the module
        needs to be executed.
        List ports have default depth 1
        """
        result = []
        for module_id in self.graph.vertices_topological_sort():
            module = self.get_module_by_id(module_id)
            module.list_depth = 0
            ports = []
            for module_from_id, conn_id in self.graph.edges_to(module_id):
                prev_depth = self.get_module_by_id(module_from_id).list_depth
                conn = self.get_connection_by_id(conn_id)
                source_depth = 0
                from vistrails.core.modules.basic_modules import List, Variant
                if conn.source.spec:
                    source_depth = conn.source.spec.depth
                    src_descs = conn.source.spec.descriptors()
                    # Lists have depth 1 if dest has depth>1 or is a list
                    if len(src_descs) == 1 and src_descs[0].module == List:
                        source_depth += 1
                dest_depth = 0
                if conn.destination.spec:
                    dest_depth = conn.destination.spec.depth
                    dest_descs = conn.destination.spec.descriptors()
                    # Lists have depth 1
                    if len(dest_descs) == 1 and dest_descs[0].module == List:
                        dest_depth += 1
                    # special case: if src is List and dst is Variant
                    # we should treat the Variant as having depth 0
                    if conn.source.spec:
                        if len(src_descs)==1 and src_descs[0].module == List and \
                           len(dest_descs)==1 and dest_descs[0].module == Variant:
                            source_depth -= 1
                        if len(src_descs)==1 and src_descs[0].module == Variant and \
                           len(dest_descs)==1 and dest_descs[0].module == List:
                            dest_depth -= 1
                depth = prev_depth + source_depth - dest_depth
                if depth > 0 and conn.destination.spec.name not in ports:
                    ports.append(conn.destination.spec.name)
                # if dest depth is greater the input will be wrapped in a
                # list to match its depth
                # if source depth is greater this module will be executed
                # once for each input in the (possibly nested) list
                module.list_depth = max(module.list_depth, depth)
            result.append((module_id, module.list_depth))
            module.iterated_ports = ports
        return result


    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(other) != type(self):
            print "type mismatch"
            return
        if len(self.module_list) != len(other.module_list):
            print "module lists of different sizes"
            return
        if len(self.connection_list) != len(other.connection_list):
            print "Connection lists of different sizes"
            return
        for m_id, m in self.modules.iteritems():
            if not m_id in other.modules:
                print "module %d in self but not in other" % m_id
                return
            if m <> other.modules[m_id]:
                print "module %s in self doesn't match module %s in other" % (m,  other.modules[m_id])
                return
        for m_id, m in other.modules.iteritems():
            if not m_id in self.modules:
                print "module %d in other but not in self" % m_id
                return
            # no need to check equality since this was already done before
        for c_id, c in self.connections.iteritems():
            if not c_id in other.connections:
                print "connection %d in self but not in other" % c_id
                return
            if c <> other.connections[c_id]:
                print "connection %s in self doesn't match connection %s in other" % (c,  other.connections[c_id])
                return
        for c_id, c, in other.connections.iteritems():
            if not c_id in self.connections:
                print "connection %d in other but not in self" % c_id
                return
            # no need to check equality since this was already done before
        assert self == other

    ##########################################################################
    # Operators

    def __ne__(self, other):
        return not self.__eq__(other)

# There's a bug in this code that's not easily worked around: if
# modules are in different order in the list, there's no easy way to
# check for equality. The solution is to move to a check that
# takes module and connection ids into account.
#     def __eq__(self, other):
#         if type(other) != type(self):
#             return False
#         if len(self.module_list) != len(other.module_list):
#             return False
#         if len(self.connection_list) != len(other.connection_list):
#             return False
#         for f, g in zip(self.module_list, other.module_list):
#             if f != g:
#                 return False
#         for f, g in zip(self.connection_list, other.connection_list):
#             if f != g:
#                 return False
#         return True

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if len(self.module_list) != len(other.module_list):
            return False
        if len(self.connection_list) != len(other.connection_list):
            return False
        for m_id, m in self.modules.iteritems():
            if not m_id in other.modules:
                return False
            if m <> other.modules[m_id]:
                return False
        for m_id, m in other.modules.iteritems():
            if not m_id in self.modules:
                return False
            # no need to check equality since this was already done before
        for c_id, c in self.connections.iteritems():
            if not c_id in other.connections:
                return False
            if c <> other.connections[c_id]:
                return False
        for c_id, c, in other.connections.iteritems():
            if not c_id in self.connections:
                return False
            # no need to check equality since this was already done before
        return True

    def __str__(self):
        return ("(Pipeline Modules: %s Graph:%s)@%X" %
                ([(m, str(v)) for (m,v) in sorted(self.modules.items())],
                 str(self.graph),
                 id(self)))


################################################################################


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # make sure pythonCalc is loaded
        from vistrails.core.packagemanager import get_package_manager
        pm = get_package_manager()
        if 'pythonCalc' not in pm._package_list: # pragma: no cover # pragma: no branch
            pm.late_enable_package('pythonCalc')

    def create_default_pipeline(self, id_scope=None):
        if id_scope is None:
            id_scope = IdScope()
        
        p = Pipeline()
        p.id = id_scope.getNewId(Pipeline.vtType)

        def module1(p):
            def f1():
                f = ModuleFunction()
                f.real_id = id_scope.getNewId(ModuleFunction.vtType)
                f.name = 'op'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'String'
                param.strValue = '+'
                f.params.append(param)
                return f
            def f2():
                f = ModuleFunction()
                f.real_id = id_scope.getNewId(ModuleFunction.vtType)
                f.name = 'value1'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'Float'
                param.strValue = '2.0'
                f.params.append(param)
                return f
            def f3():
                f = ModuleFunction()
                f.real_id = id_scope.getNewId(ModuleFunction.vtType)
                f.name = 'value2'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'Float'
                param.strValue = '4.0'
                f.params.append(param)
                return f
            def cp1():
                f = ModuleControlParam()
                f.id = id_scope.getNewId(ModuleControlParam.vtType)
                f.name = 'cpname1'
                f.value = 'cpvalue[]'
                return f
            m = Module()
            m.id = id_scope.getNewId(Module.vtType)
            m.name = 'PythonCalc'
            m.package = '%s.pythoncalc' % get_vistrails_default_pkg_prefix()
            m.functions.append(f1())
            m.control_parameters.append(cp1())
            return m
        
        def module2(p):
            def f1():
                f = ModuleFunction()
                f.real_id = id_scope.getNewId(ModuleFunction.vtType)
                f.name = 'op'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'String'
                param.strValue = '+'
                f.params.append(param)
                return f
            m = Module()
            m.id = id_scope.getNewId(Module.vtType)
            m.name = 'PythonCalc'
            m.package = '%s.pythoncalc' % get_vistrails_default_pkg_prefix()
            m.functions.append(f1())
            return m
        m1 = module1(p)
        p.add_module(m1)
        m2 = module1(p)
        p.add_module(m2)
        m3 = module2(p)
        p.add_module(m3)

        c1 = Connection()
        c1.sourceId = m1.id
        c1.destinationId = m3.id
        c1.source.id = id_scope.getNewId(Port.vtType)
        c1.destination.id = id_scope.getNewId(Port.vtType)
        c1.source.name = 'value'
        c1.source.moduleName = 'PythonCalc'
        c1.destination.name = 'value1'
        c1.destination.moduleName = 'PythonCalc'
        c1.id = id_scope.getNewId(Connection.vtType)
        p.add_connection(c1)

        c2 = Connection()
        c2.sourceId = m2.id
        c2.destinationId = m3.id
        c2.source.id = id_scope.getNewId(Port.vtType)
        c2.destination.id = id_scope.getNewId(Port.vtType)
        c2.source.name = 'value'
        c2.source.moduleName = 'PythonCalc'
        c2.destination.name = 'value2'
        c2.destination.moduleName = 'PythonCalc'
        c2.id = id_scope.getNewId(Connection.vtType)

        p.add_connection(c2)
        p.compute_signatures()
        return p

    def create_pipeline2(self, id_scope=None):
        basic_pkg = get_vistrails_basic_pkg_id()
        if id_scope is None:
            id_scope = IdScope(remap={Abstraction.vtType: Module.vtType})

        param1 = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                             type='Int',
                             val='1')
        param2 = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                             type='Float',
                             val='1.3456')
        func1 = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                               name='value',
                               parameters=[param1])
        func2 = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                               name='floatVal',
                               parameters=[param2])
        loc1 = Location(id=id_scope.getNewId(Location.vtType),
                        x=12.342,
                        y=-19.432)
        loc2 = Location(id=id_scope.getNewId(Location.vtType),
                        x=21.34,
                        y=456.234)
        m1 = Module(id=id_scope.getNewId(Module.vtType),
                    package=basic_pkg,
                    name='String',
                    location=loc1,
                    functions=[func1])
        m2 = Abstraction(id=id_scope.getNewId(Abstraction.vtType),
                         internal_version=13,
                         location=loc2,
                         functions=[func2])
        source = Port(id=id_scope.getNewId(Port.vtType),
                      type='source', 
                      moduleId=m1.id, 
                      moduleName='String', 
                      name='value',
                      signature='(%s:String)' % basic_pkg)
        destination = Port(id=id_scope.getNewId(Port.vtType),
                           type='destination',
                           moduleId=m2.id,
                           moduleName='Abstraction',
                           name='self',
                           signature='()')
        c1 = Connection(id=id_scope.getNewId(Connection.vtType),
                        ports=[source, destination])
        pipeline = Pipeline(id=id_scope.getNewId(Pipeline.vtType),
                            modules=[m1, m2],
                            connections=[c1])
        return pipeline

    def setUp(self):
        self.pipeline = self.create_default_pipeline()
        self.sink_id = 2

    def test_create_pipeline_signature(self):
        self.pipeline.subpipeline_signature(self.sink_id)

    def test_delete_signatures(self):
        """Makes sure signatures are deleted when other things are."""
        p = self.create_default_pipeline()
        m_sig_size_before = len(p._module_signatures)
        c_sig_size_before = len(p._connection_signatures)
        p_sig_size_before = len(p._subpipeline_signatures)
        p.delete_connection(0)
        p.delete_module(0)
        m_sig_size_after = len(p._module_signatures)
        c_sig_size_after = len(p._connection_signatures)
        p_sig_size_after = len(p._subpipeline_signatures)
        self.assertNotEquals(m_sig_size_before, m_sig_size_after)
        self.assertNotEquals(c_sig_size_before, c_sig_size_after)
        self.assertNotEquals(p_sig_size_before, p_sig_size_after)

    def test_delete_connections(self):
        p = self.create_default_pipeline()
        p.delete_connection(0)
        p.delete_connection(1)
        p.delete_module(2)
        self.assertEquals(len(p.connections), 0)

    def test_basic(self):
        """Makes sure pipeline can be created, modules and connections
        can be added and deleted."""
        p = self.create_default_pipeline()
    
    def test_copy(self):
        id_scope = IdScope()
        
        p1 = self.create_default_pipeline(id_scope)
        p2 = copy.copy(p1)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)
        p3 = p1.do_copy(True, id_scope, {})
        self.assertNotEquals(p1, p3)
        self.assertNotEquals(p1.id, p3.id)

    def test_copy2(self):
        import vistrails.core.db.io

        # nedd to id modules and abstraction_modules with same counter
        id_scope = IdScope(remap={Abstraction.vtType: Module.vtType})
        
        p1 = self.create_pipeline2(id_scope)
        p2 = copy.copy(p1)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)
        p3 = p1.do_copy(True, id_scope, {})
        self.assertNotEquals(p1, p3)
        self.assertNotEquals(p1.id, p3.id)

    def test_serialization(self):
        import vistrails.core.db.io
        p1 = self.create_default_pipeline()
        xml_str = vistrails.core.db.io.serialize(p1)
        p2 = vistrails.core.db.io.unserialize(xml_str, Pipeline)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)        

    def test_serialization2(self):
        import vistrails.core.db.io
        p1 = self.create_pipeline2()
        xml_str = vistrails.core.db.io.serialize(p1)
        p2 = vistrails.core.db.io.unserialize(xml_str, Pipeline)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)        

    def test_aliases(self):
        """ Exercises aliases manipulation """
        import vistrails.core.db.action
        from vistrails.core.db.locator import XMLFileLocator
        import vistrails.core.system
        v = XMLFileLocator( \
            vistrails.core.system.vistrails_root_directory() +
            '/tests/resources/test_alias.xml').load()

        p1 = v.getPipeline('alias')
        p2 = v.getPipeline('alias')
        
        # testing removing an alias
        old_param = p1.modules[0].functions[0].params[0]
        func = p1.modules[0].functions[0]
        #old_id = p1.modules[0].functions[0].params[0].db_id
        #old_f_id = p1.modules[0].functions[0].db_id
        new_param = ModuleParam(id=-1,
                                pos=old_param.pos,
                                name=old_param.name,
                                alias="",
                                val=str(1.0),
                                type=old_param.type)
        action_spec = ('change', old_param, new_param,
                       func.vtType, func.real_id)
        action = vistrails.core.db.action.create_action([action_spec])
        p1.perform_action(action)
        self.assertEquals(p1.has_alias('v1'),False)
        v1 = p2.aliases['v1']
        old_param2 = p2.modules[0].functions[0].params[0]
        new_param2 = ModuleParam(id=old_param.real_id,
                                pos=old_param.pos,
                                name=old_param.name,
                                alias="v1",
                                val=str(v),
                                type=old_param.type)
        func2 = p2.modules[0].functions[0]
        action2 = vistrails.core.db.action.create_action([('change',
                                                 old_param2,
                                                 new_param2,
                                                 func2.vtType,
                                                 func2.real_id)
                                                ])
        p2.perform_action(action2)
        self.assertEquals(v1, p2.aliases['v1'])
        
    def test_module_signature(self):
        """Tests signatures for modules with similar (but not equal)
        parameter specs."""
        pycalc_pkg = '%s.pythoncalc' % get_vistrails_default_pkg_prefix()
        p1 = Pipeline()
        p1_functions = [ModuleFunction(name='value1',
                                       parameters=[ModuleParam(type='Float',
                                                               val='1.0',
                                                               )],
                                       ),
                        ModuleFunction(name='value2',
                                       parameters=[ModuleParam(type='Float',
                                                               val='2.0',
                                                               )],
                                       )]
        p1.add_module(Module(name='PythonCalc',
                             package=pycalc_pkg,
                             id=3,
                             functions=p1_functions))

        p2 = Pipeline()
        p2_functions = [ModuleFunction(name='value1',
                                       parameters=[ModuleParam(type='Float',
                                                               val='2.0',
                                                               )],
                                       ),
                        ModuleFunction(name='value2',
                                       parameters=[ModuleParam(type='Float',
                                                               val='1.0',
                                                               )],
                                       )]
        p2.add_module(Module(name='PythonCalc', 
                             package=pycalc_pkg,
                             id=3,
                             functions=p2_functions))

        self.assertNotEquals(p1.module_signature(3),
                             p2.module_signature(3))

    def test_find_method(self):
        p1 = Pipeline()
        p1_functions = [ModuleFunction(name='i1',
                                       parameters=[ModuleParam(type='Float',
                                                               val='1.0',
                                                               )],
                                       ),
                        ModuleFunction(name='i2',
                                       parameters=[ModuleParam(type='Float',
                                                               val='2.0',
                                                               )],
                                       )]
        p1.add_module(Module(name='CacheBug', 
                            package='%s.console_mode_test' % \
                             get_vistrails_default_pkg_prefix(),
                            id=3,
                            functions=p1_functions))

        self.assertEquals(p1.find_method(3, 'i1'), 0)
        self.assertEquals(p1.find_method(3, 'i2'), 1)
        self.assertEquals(p1.find_method(3, 'i3'), -1)
        self.assertRaises(KeyError, p1.find_method, 4, 'i1')

    def test_str(self):
        p1 = Pipeline()
        p1_functions = [ModuleFunction(name='i1',
                                       parameters=[ModuleParam(type='Float',
                                                               val='1.0',
                                                               )],
                                       ),
                        ModuleFunction(name='i2',
                                       parameters=[ModuleParam(type='Float',
                                                               val='2.0',
                                                               )],
                                       )]
        p1.add_module(Module(name='CacheBug', 
                            package='%s.console_mode_test' % \
                             get_vistrails_default_pkg_prefix(),
                            id=3,
                            functions=p1_functions))
        str(p1)

    def test_pipeline_equality_module_list_out_of_order(self):
        p1 = Pipeline()
        p1.add_module(Module(name='Foo',
                             package='bar',
                             id=0,
                             functions=[]))
        p1.add_module(Module(name='Foo2',
                             package='bar',
                             id=1,
                             functions=[]))
        p2 = Pipeline()
        p2.add_module(Module(name='Foo2',
                             package='bar',
                             id=1,
                             functions=[]))
        p2.add_module(Module(name='Foo',
                             package='bar',
                             id=0,
                             functions=[]))
        assert p1 == p2

#     def test_subpipeline(self):
#         p = self.create_default_pipeline()
#         p2 = p.get_subpipeline([0, 1])
#         for m in p2.modules:
#             print m
#         for c in p2.connections:
#             print c

    def test_incorrect_port_spec(self):
        import vistrails.core.modules.basic_modules
        p = Pipeline()
        basic_version = vistrails.core.modules.basic_modules.version
        basic_pkg = vistrails.core.modules.basic_modules.identifier
        m1 = Module(name="String",
                    package=basic_pkg,
                    version=basic_version,
                    id=1L)
        m2 = Module(name="String",
                    package=basic_pkg,
                    version=basic_version,
                    id=2L)
        source = Port(id=1L,
                      type='source', 
                      moduleId=m1.id, 
                      moduleName='String', 
                      name='value',
                      signature='(%s:StringBean)' % basic_pkg)
        destination = Port(id=2L,
                           type='destination',
                           moduleId=m2.id,
                           moduleName='String',
                           name='value',
                           signature='(%s:NString)' % basic_pkg)
        c1 = Connection(id=1L,
                        ports=[source, destination])
        p.add_module(m1)
        p.add_module(m2)
        p.add_connection(c1)
        p.ensure_modules_are_on_registry()
        p.ensure_connection_specs()
        p_source = p.connections[c1.id].source
        p_destination = p.connections[c1.id].destination
        self.assertEqual(p_source.signature, '(%s:String)' % basic_pkg)
        self.assertEqual(len(p_source.descriptors()), 1)
        self.assertEqual(p_destination.signature, '(%s:String)' % basic_pkg)
        self.assertEqual(len(p_destination.descriptors()), 1)

if __name__ == '__main__':
    unittest.main()
