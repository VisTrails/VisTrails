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
##TODO Tests
""" This module defines the class Pipeline """

from core.cache.hasher import Hasher
from core.data_structures.bijectivedict import Bidict
from core.data_structures.graph import Graph
from core.debug import DebugPrint
from core.modules.module_registry import registry, ModuleRegistry
from core.utils import VistrailsInternalError
from core.utils import expression, append_to_dict_of_lists
from core.utils.uxml import named_elements
from core.vistrail.connection import Connection
from core.vistrail.module import Module
from core.vistrail.port import Port, PortEndPoint
from core.vistrail.port_spec import PortSpec
from db.domain import DBWorkflow
from types import ListType
import core.vistrail.action
import core.modules.module_registry

from xml.dom.minidom import getDOMImplementation, parseString
import copy
import sha

##############################################################################

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


    def __copy__(self):
        """ __copy__() -> Pipeline - Returns a clone of itself """ 
        return Pipeline.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflow.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Pipeline
        cp.graph = copy.copy(self.graph)
        cp.aliases = Bidict([(k,copy.copy(v))
                           for (k,v)
                           in self.aliases.iteritems()])
        cp._connection_signatures = Bidict([(k,copy.copy(v))
                                            for (k,v)
                                            in self._connection_signatures.iteritems()])
        cp._subpipeline_signatures = Bidict([(k,copy.copy(v))
                                             for (k,v)
                                             in self._subpipeline_signatures.iteritems()])
        cp._module_signatures = Bidict([(k,copy.copy(v))
                                        for (k,v)
                                        in self._module_signatures.iteritems()])
        return cp

    @staticmethod
    def convert(_workflow):
        if _workflow.__class__ == Pipeline:
            return
        # do clear plus get the modules and connections
	_workflow.__class__ = Pipeline
        _workflow.graph = Graph()
        _workflow.aliases = Bidict()
        _workflow._subpipeline_signatures = Bidict()
        _workflow._module_signatures = Bidict()
        _workflow._connection_signatures = Bidict()
	for _module in _workflow.db_modules:
	    Module.convert(_module)
            _workflow.graph.add_vertex(_module.id)
            # FIXME this should be moved to Module.convert stuff...
            for _portSpec in _module.db_portSpecs:
                #  (port, endpoint) = registry.create_port_from_old_spec(_portSpec)
                _workflow.add_port_to_registry(_portSpec, _module.db_id)
	for _connection in _workflow.db_connections:
            Connection.convert(_connection)
            _workflow.graph.add_edge( \
                _connection.source.moduleId,
                _connection.destination.moduleId,
                _connection.db_id)
        #there should be another way to do this
        for _obj in _workflow.objects.itervalues():
            if _obj.vtType == 'function':
                for _par in _obj.parameters:
                    _workflow.change_alias(_par.alias,
                                           _par.vtType,
                                           _par.real_id,
                                           _obj.vtType,
                                           _obj.real_id)

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

    def _get_id(self):
        return self.db_id
    def _set_id(self,id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

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
    
    def perform_action_chain(self, actionChain):
        for action in actionChain:
            self.perform_action(action)

    def perform_action(self, action):
        for operation in action.operations:
            self.perform_operation(operation)

    def perform_operation_chain(self, opChain):
        for op in opChain:
            self.perform_operation(op)

    def perform_operation(self, op):
        # print "doing %s %s" % (op.vtType, op.what)
        opMap = {('add','annotation'): self.perform_add_annotation,
                 ('add','module'): self.perform_add_module,
                 ('add','connection'): self.perform_add_connection,
                 ('add','portSpec'): self.perform_add_port_spec,
                 ('add','parameter'): self.perform_add_parameter,
                 ('add','port'): self.perform_add_port,
                 ('change','annotation'): self.perform_change_annotation,
                 ('change','module'): self.perform_change_module,
                 ('change','connection'): self.perform_change_connection,
                 ('change','portSpec'): self.perform_change_port_spec,
                 ('change','parameter'): self.perform_change_parameter,
                 ('change','port'): self.perform_change_port,
                 ('delete','annotation'): self.perform_delete_annotation,
                 ('delete','module'): self.perform_delete_module,
                 ('delete','connection'): self.perform_delete_connection,
                 ('delete','portSpec'): self.perform_delete_port_spec,
                 ('delete','parameter'): self.perform_delete_parameter,
                 ('delete','port'): self.perform_delete_port,
                 }
        if opMap.has_key((op.vtType, op.what)):
            opMap[(op.vtType, op.what)](op)
        elif op.vtType == 'add':
            self.db_add_object(op.data, op.parentObjType, 
                               op.parentObjId)
        elif op.vtType == 'change':
            # FIXME: change to use old, newId
            self.db_change_object(op.data, op.parentObjType,
                                  op.parentObjId)
        elif op.vtType == 'delete':
            self.db_delete_object(op.objectId, op.what,
                                  op.parentObjType, op.parentObjId)
    def perform_add_module(self, op):
        self.add_module(op.data)
    def perform_change_module(self, op):
        self.delete_module(op.oldObjId)
        self.add_module(op.data)
    def perform_delete_module(self, op):
        self.delete_module(op.objectId)
    def perform_add_connection(self, op):
        self.add_connection(op.data)
    def perform_change_connection(self, op):
        self.delete_connection(op.objObjId)
        self.add_connection(op.data)
    def perform_delete_connection(self, op):
        self.delete_connection(op.objectId)
    def perform_add_port_spec(self, op):
        self.add_module_port(op.data, op.parentObjId)
    def perform_delete_port_spec(self, op):
        self.delete_module_port(op.objectId, op.parentObjId)
    def perform_change_port_spec(self, op):
        self.delete_module_port(op.oldObjId, op.parentObjId)
        self.add_module_port(op.data, op.parentObjId)
    def perform_add_annotation(self, op):
        self.db_add_object(op.data, op.parentObjType, op.parentObjId)
    def perform_delete_annotation(self, op):
        self.db_delete_object(op.objectId, op.what,
                              op.parentObjType, op.parentObjId)
    def perform_change_annotation(self, op):
        op.objectId = op.oldObjId
        self.perform_delete_annotation(op)
        op.objectId = op.newObjId
        self.perform_add_annotation(op)
    def perform_add_parameter(self, op):
        self.db_add_object(op.data, op.parentObjType, 
                           op.parentObjId)
        param = op.data
        if not self.has_alias(param.alias):
            self.change_alias(param.alias, 
                              param.vtType, 
                              param.real_id,
                              op.parentObjType,
                              op.parentObjId)
    def perform_delete_parameter(self, op):
        self.db_delete_object(op.objectId, op.what,
                              op.parentObjType, op.parentObjId)
        self.remove_alias(op.what, op.objectId, op.parentObjType,
                          op.parentObjId)
    def perform_change_parameter(self, op):
        op.objectId = op.oldObjId
        self.perform_delete_parameter(op)
        op.objectId = op.newObjId
        self.perform_add_parameter(op)

    def perform_add_port(self, op):
        self.db_add_object(op.data, op.parentObjType, op.parentObjId)
        connection = self.connections[op.parentObjId]
#         if op.data.db_type == 'source':
#             connection.source = copy.copy(op.data)
#         elif op.data.db_type == 'destination':
#             connection.destination = copy.copy(op.data)
        if connection.source is not None and \
                connection.destination is not None:
            self.graph.add_edge(connection.sourceId, 
                                connection.destinationId, 
                                connection.id)
    def perform_delete_port(self, op):
        connection = self.connections[op.parentObjId]
        if len(connection.ports) >= 2:
            self.graph.delete_edge(connection.sourceId, 
                                   connection.destinationId, 
                                   connection.id)
        self.db_delete_object(op.objectId, op.what,
                              op.parentObjType, op.parentObjId)
        
    def perform_change_port(self, op):
        op.objectId = op.oldObjId
        self.perform_delete_port(op)
        op.objectId = op.newObjId
        self.perform_add_port(op)

    def add_port_to_registry(self, portSpec, moduleId):
        m = self.get_module_by_id(moduleId)
        module = registry.get_descriptor_by_name(m.package, m.name).module
        if m.registry is None:
            m.registry = ModuleRegistry()
            m.registry.add_module(module, package=m.package)

        if portSpec.type == 'input':
            endpoint = PortEndPoint.Destination
        else:
            endpoint = PortEndPoint.Source
        portSpecs = portSpec.spec[1:-1].split(',')
        signature = [registry.get_descriptor_from_name_only(spec).module
                     for spec in portSpecs]
        port = Port()
        port.name = portSpec.name
        port.spec = core.modules.module_registry.PortSpec(signature)
        m.registry.add_port(module, endpoint, port)

    def add_module_port(self, portSpec, moduleId):
        self.db_add_object(portSpec, Module.vtType, moduleId)
        self.add_port_to_registry(portSpec, moduleId)

    def delete_port_from_registry(self, id, moduleId):
        m = self.get_module_by_id(moduleId)
        if not m.port_specs.has_key(id):
            raise VistrailsInternalError("id missing in port_specs")
        portSpec = m.port_specs[id]
        portSpecs = portSpec.spec[1:-1].split(',')
        signature = [registry.get_descriptor_from_name_only(spec).module
                     for spec in portSpecs]
        port = Port(signature)
        port.name = portSpec.name
        port.spec = core.modules.module_registry.PortSpec(signature)

        module = registry.get_descriptor_by_name(m.package, m.name).module
        assert isinstance(m.registry, ModuleRegistry)

        if portSpec.type == 'input':
            m.registry.delete_input_port(module, port.name)
        else:
            m.registry.delete_output_port(module, port.name)

    def delete_module_port(self, id, moduleId):
        self.delete_port_from_registry(id, moduleId)
        self.db_delete_object(id, PortSpec.vtType, Module.vtType, moduleId)

    def delete_module(self, id):
        """delete_module(id:int) -> None 
        Delete a module from pipeline given an id.

        """
        if not self.has_module_with_id(id):
            raise VistrailsInternalError("id missing in modules")

        # we're hiding the necessary operations by doing this!
        adj = copy.copy(self.graph.adjacency_list[id])
        inv_adj = copy.copy(self.graph.inverse_adjacency_list[id])
        for (_, conn_id) in adj:
            self.delete_connection(conn_id)
        for (_, conn_id) in inv_adj:
            self.delete_connection(conn_id)

        # self.modules.pop(id)
        self.db_delete_object(id, 'module')
        self.graph.delete_vertex(id)
        if id in self._module_signatures:
            del self._module_signatures[id]
        if id in self._subpipeline_signatures:
            del self._subpipeline_signatures[id]

    def add_module(self, m):
        """add_module(m: Module) -> None 
        Add new module to pipeline
          
        """
        if self.has_module_with_id(m.id):
            raise VistrailsInternalError("duplicate module id")
#         self.modules[m.id] = copy.copy(m)
        self.db_add_object(m)
        self.graph.add_vertex(m.id)
    
    def add_alias(self, name, type, oId, parentType, parentId):
        """add_alias(name: str, oId: int, parentType:str, parentId: int) -> None 
        Add alias to pipeline
          
        """
        if self.has_alias(name):
            raise VistrailsInternalError("duplicate alias")
        self.aliases[name] = (type, oId, parentType, parentId)

    def remove_alias_by_name(self, name):
        """remove_alias_by_name(name: str) -> None
        Remove alias with given name """
        if self.has_alias(name):
            del self.aliases[name]

    def remove_alias(self, type, oId, parentType, parentId):
        """remove_alias(name: str, type:?, oId: int)-> None
        Remove alias identified by oId """
        if self.aliases.inverse.has_key((type,oId, parentType, parentId)):
            oldname = self.aliases.inverse[(type,oId, parentType, parentId)]
            del self.aliases[oldname]

    def change_alias(self, name, type, oId, parentType, parentId):
        """change_alias(name: str, type:str oId:int, parentType:str,
                        parentId:int)-> None
        Change alias if name is non empty. Else remove alias
        
        """
        if name == "":
            self.remove_alias(type, oId, parentType, parentId)
        else:
            if not self.has_alias(name):
                self.remove_alias(type, oId, parentType, parentId)
                self.add_alias(name, type, oId, parentType, parentId)
                
    def get_alias_str_value(self, name):
        """ get_alias_str_value(name: str) -> str
        returns the strValue of the parameter with alias name

        """
        result = ""
        if self.aliases.has_key(name):
            what, oId, parentType, parentId = self.aliases[name]
            if what == 'parameter':
                parameter = self.db_get_object(what, oId)
                result = parameter.strValue
            else:
                raise VistrailsInternalError("only parameters are supported")
        return result

    def set_alias_str_value(self, name, value):
        """ set_alias_str_value(name: str, value: str) -> None
        sets the strValue of the parameter with alias name 
        
        """
        if self.aliases.has_key(name):
            what, oId, parentType, parentId = self.aliases[name]
            if what == 'parameter':
                #FIXME: check if a change parameter action needs to be generated
                parameter = self.db_get_object(what, oId)
                parameter.strValue = str(value)
            else:
                raise VistrailsInternalError("only parameters are supported")

    def delete_connection(self, id):
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
        if id in self._connection_signatures:
            del self._connection_signatures[id]
        
    def add_connection(self, c):
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
        
    def get_module_by_id(self, id):
        """get_module_by_id(id: int) -> Module
        Accessor. id is the Module id.
        
        """
        result = self.modules[id]
        if result.package is None:
            DebugPrint.critical('module %d is missing package' % id)
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
        return self.modules.has_key(id)
    
    def has_connection_with_id(self, id):
        """has_connection_with_id(id: int) -> boolean 
        Checks whether given connection exists.

        """
        return self.connections.has_key(id)

    def has_alias(self, name):
        """has_alias(name: str) -> boolean 
        Checks whether given alias exists.

        """
        return self.aliases.has_key(name)

    def out_degree(self, id):
        """out_degree(id: int) -> int - Returns the out-degree of a module. """
        return self.graph.out_degree(id)

    def dump_to_XML(self, dom, root, timeAttr=None):
        """dump_to_XML(dom, root, timeAttr=None) -> None - outputs self to xml"""
        node = dom.createElement('pipeline')
        if timeAttr is not None:
            node.setAttribute('time',str(timeAttr))
        for module in self.modules.values():
            module.dumpToXML(dom, node)
        for connection in self.connections.values():
            connection.serialize(dom, node)
        root.appendChild(node)

    def dump_to_string(self):
        """ dump_to_string() -> str
        Serialize this pipeline to an XML string
        
        """
        dom = getDOMImplementation().createDocument(None, 'network', None)
        root = dom.documentElement
        self.dump_to_XML(dom, root)
        return str(dom.toxml())

    @staticmethod
    def load_from_XML(root):
        """ load_from_XML(root) -> Pipeline
        Return the pipeline from the XML elements
        
        """
        p = Pipeline()
        for rootXML in named_elements(root, 'pipeline'):
            for moduleXML in named_elements(rootXML, 'module'):
                p.add_module(Module.loadFromXML(moduleXML))
            for connectXML in named_elements(rootXML, 'connect'):
                p.add_connection(Connection.loadFromXML(connectXML))
        return p

    @staticmethod
    def load_from_string(s):
        """ load_from_string(s: str) -> Pipeline
        Load a pipeline from an XML string
        '
        """
        dom = parseString(s)
        root = dom.documentElement
        return Pipeline.load_from_XML(root)

    ##########################################################################
    # Caching-related

    # Modules

    def module_signature(self, module_id):
        """module_signature(module_id): string
        Returns the signature for the module with given module_id."""
        if not self._module_signatures.has_key(module_id):
            m = self.modules[module_id]
            sig = registry.module_signature(m)
            self._module_signatures[module_id] = sig
        return self._module_signatures[module_id]

    def module_id_from_signature(self, signature):
        """module_id_from_signature(sig): int
        Returns the module_id that corresponds to the given signature.
        This must have been previously computed."""
        return self._module_signatures.inverse[signature]

    def has_module_signature(self, signature):
        return self._module_signatures.inverse.has_key(signature)

    # Subpipelines

    def subpipeline_signature(self, module_id):
        """subpipeline_signature(module_id): string
        Returns the signature for the subpipeline whose sink id is module_id."""
        if not self._subpipeline_signatures.has_key(module_id):
            upstream_sigs = [(self.subpipeline_signature(m) +
                              Hasher.connection_signature(
                                  self.connections[edge_id]))
                             for (m, edge_id) in
                             self.graph.edges_to(module_id)]
            module_sig = self.module_signature(module_id)
            sig = Hasher.subpipeline_signature(module_sig,
                                               upstream_sigs)
            self._subpipeline_signatures[module_id] = sig
        return self._subpipeline_signatures[module_id]

    def subpipeline_id_from_signature(self, signature):
        """subpipeline_id_from_signature(sig): int
        Returns the module_id that corresponds to the given signature.
        This must have been previously computed."""
        return self._subpipeline_signatures.inverse[signature]

    def has_subpipeline_signature(self, signature):
        return self._subpipeline_signatures.inverse.has_key(signature)

    # Connections

    def connection_signature(self, connection_id):
        """connection_signature(id): string
        Returns the signature for the connection with given id."""
        if not self._connection_signatures.has_key(connection_id):
            c = self.connections[connection_id]
            source_sig = self.subpipeline_signature(c.sourceId)
            dest_sig = self.subpipeline_signature(c.destinationId)
            sig = Hasher.connection_subpipeline_signature(c, source_sig,
                                                          dest_sig)
            self._connection_signatures[connection_id] = sig
        return self._connection_signatures[connection_id]

    def connection_id_from_signature(self, signature):
        return self._connection_signatures.inverse[signature]

    def has_connection_signature(self, signature):
        return self._connection_signatures.inverse.has_key(signature)

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
        if type(module_set) == list:
            subgraph = self.graph.subgraph(module_set)
        elif type(module_set) == Graph:
            subgraph = module_set
        else:
            raise Exception("Expected list of ints or graph")
        result = Pipeline()
        for module_id in subgraph.iter_vertices():
            result.add_module(copy.copy(self.modules[module_id]))
        for (conn_from, conn_to, conn_id) in subgraph.iter_all_edges():
            result.add_connection(copy.copy(self.connections[conn_id]))
		# I haven't finished this yet. -cscheid
        raise Exception("Incomplete implementation!")
        return result

    def dump_actions(self):
        """dump_actions() -> [Action].

        Returns a list of actions that can be used to create a copy of the
        pipeline."""

        raise Exception('broken')
#         result = []
#         for m in self.modules:
#             add_module = core.vistrail.action.AddModuleAction()
#             add_module.module = copy.copy(m)
#             result.append(add_module)
#         for c in self.connections:
#             add_connection = core.vistrail.action.AddConnectionAction()
#             add_connection.connection = copy.copy(c)
#             result.append(add_connection)
#         return result

    ##########################################################################
    # Registry-related

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
        def source_spec(port):
            module = self.get_module_by_id(port.moduleId)
            reg = module.registry or registry
            descriptor = reg.get_descriptor_by_name(module.package,
                                                    module.name)
            port_list = []
            def do_it(ports):
                for (_, lst) in ports:
                    port_list.extend([p for p in lst
                                      if p.name == port.name])

            do_it(reg.all_source_ports(descriptor))
            if len(port_list) == 0:
                # The port might still be in the original registry
                d = registry.get_descriptor_by_name(module.package,
                                                    module.name)
                do_it(registry.all_source_ports(d))
            assert len(port_list) > 0
            
            # if port_list has more than one element, then it's an
            # overloaded port. Source (output) port overloads must all
            # be contravariant. This means that the spec of the
            # new port must be a subtype of the spec of the
            # original port. This induces a total ordering on the types,
            # which we use to sort the possible ports, and get the
            # most strict one.
            
            port_list.sort(lambda p1, p2:
                           (p1 != p2 and
                            issubclass(p1.spec.signature[0][0],
                                       p2.spec.signature[0][0])))
            return copy.copy(port_list[0].spec)

        def destination_spec(port):
            module = self.get_module_by_id(port.moduleId)
            reg = module.registry or registry
            descriptor = reg.get_descriptor_by_name(module.package,
                                                    module.name)
            port_list = []
            def do_it(ports):
                for (_, lst) in ports:
                    port_list.extend([p for p in lst
                                      if p.name == port.name])

            do_it(reg.all_destination_ports(descriptor))
            if len(port_list) == 0:
                # The port might still be in the original registry
                d = registry.get_descriptor_by_name(module.package,
                                                    module.name)
                do_it(registry.all_destination_ports(d))
            assert len(port_list) > 0

            # if port_list has more than one element, then it's an
            # overloaded port. Destination (input) port overloads must
            # all be covariant. This means that the spec of the new
            # port must be a supertype of the spec of the original
            # port. This induces a total ordering on the types, which
            # we use to sort the possible ports, and get the most
            # general one.

            port_list.sort(lambda p1, p2:
                           (p1 != p2 and
                            issubclass(p1.spec.signature[0][0],
                                       p2.spec.signature[0][0])))
            return copy.copy(port_list[-1].spec)

        if connection_ids is None:
            connection_ids = self.connections.iterkeys()
        for conn_id in connection_ids:
            conn = self.connections[conn_id]
            if not conn.source.spec:
                conn.source.spec = source_spec(conn.source)
            if not conn.destination.spec:
                conn.destination.spec = destination_spec(conn.destination)

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(other) != type(self):
            print "Type mismatch"
            return
        for m_id, m in self.modules.iteritems():
            if not other.modules.has_key(m_id):
                print "Module",m_id,"missing"
                return
            if m != other.modules[m_id]:
                print "Module",m_id,"mismatch"
                m.show_comparison(other.modules[m_id])
                return
        for c_id, c in self.connections.iteritems():
            if not other.connections.has_key(c_id):
                print "Connection",c_id,"missing"
                return
            if c != other.connections[c_id]:
                print "Connection",c_id,"mismatch"
                c.show_comparison(other.connections[c_id])
                return
        print "pipelines are equal"
        assert self == other

    ##########################################################################
    # Operators

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if len(self.module_list) != len(other.module_list):
            return False
        if len(self.connection_list) != len(other.connection_list):
            return False
        for f, g in zip(self.module_list, other.module_list):
            if f != g:
                return False
        for f, g in zip(self.connection_list, other.connection_list):
            if f != g:
                return False
        return True

    def __str__(self):
        return ("(Pipeline Modules: %s Graph:%s)@%X" %
                ([(m, str(v)) for (m,v) in sorted(self.modules.items())],
                 str(self.graph),
                 id(self)))


################################################################################

import unittest
from core.vistrail.connection import Connection
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.port import Port
from db.domain import IdScope

class TestPipeline(unittest.TestCase):

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
            m = Module()
            m.id = id_scope.getNewId(Module.vtType)
            m.name = 'PythonCalc'
            m.package = 'edu.utah.sci.vistrails.pythoncalc'
            m.functions.append(f1())
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
            m.package = 'edu.utah.sci.vistrails.pythoncalc'
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
        self.assertEquals(p1, p3)
        self.assertNotEquals(p1.id, p3.id)

    def test_serialization(self):
        import core.db.io
        p1 = self.create_default_pipeline()
        xml_str = core.db.io.serialize(p1)
        p2 = core.db.io.unserialize(xml_str, Pipeline)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)        

    def test_aliases(self):
        """ Exercises aliases manipulation """
        import db.services.action
        import core.vistrail.action
        from core.db.locator import XMLFileLocator
        import core.system
        v = XMLFileLocator( \
            core.system.vistrails_root_directory() +
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
                                val=str(v),
                                type=old_param.type)
        action_spec = ('change', old_param, new_param,
                       func.vtType, func.real_id)
        action = db.services.action.create_action([action_spec])
        core.vistrail.action.Action.convert(action)
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
        action2 = db.services.action.create_action([('change',
                                                     old_param2,
                                                     new_param2,
                                                     func2.vtType,
                                                     func2.real_id)
                                                    ])
        core.vistrail.action.Action.convert(action2)
        p2.perform_action(action2)
        self.assertEquals(v1, p2.aliases['v1'])
        
    def test_module_signature(self):
        """Tests signatures for modules with similar (but not equal)
        parameter specs."""
        print "\nPlease ignore the \"Cannot find CacheBug\" errors"
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
                            package='edu.utah.sci.vistrails.console_mode_test',
                            id=3,
                            functions=p1_functions))

        p2 = Pipeline()
        p2_functions = [ModuleFunction(name='i1',
                                       parameters=[ModuleParam(type='Float',
                                                               val='2.0',
                                                               )],
                                       ),
                        ModuleFunction(name='i2',
                                       parameters=[ModuleParam(type='Float',
                                                               val='1.0',
                                                               )],
                                       )]
        p2.add_module(Module(name='CacheBug', 
                            package='edu.utah.sci.vistrails.console_mode_test',
                            id=3,
                            functions=p2_functions))

        self.assertNotEquals(p1.module_signature(3),
                             p2.module_signature(3))
        print "\nPlease ignore the \"Cannot find CacheBug\" errors"

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
                            package='edu.utah.sci.vistrails.console_mode_test',
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
                            package='edu.utah.sci.vistrails.console_mode_test',
                            id=3,
                            functions=p1_functions))
        str(p1)

#     def test_subpipeline(self):
#         p = self.create_default_pipeline()
#         p2 = p.get_subpipeline([0, 1])
#         for m in p2.modules:
#             print m
#         for c in p2.connections:
#             print c

if __name__ == '__main__':
    unittest.main()
