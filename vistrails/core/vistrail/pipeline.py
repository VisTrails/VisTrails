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
	DBWorkflow.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = 0
        if self.name is None:
            self.name = 'untitled'

        self.clear()

    def __copy__(self):
        """ __copy__() -> Pipeline - Returns a clone of itself """ 
        cp = DBWorkflow.__copy__(self)
        cp.__class__ = Pipeline
#         cp.modules = dict([(k,copy.copy(v))
#                            for (k,v)
#                            in self.modules.iteritems()])
#         cp.connections = dict([(k,copy.copy(v))
#                                for (k,v)
#                                in self.connections.iteritems()])
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
	for _module in _workflow.db_modules.itervalues():
	    Module.convert(_module)
            _workflow.graph.add_vertex(_module.id)
            for _portSpec in _module.db_portSpecs.itervalues():
#                 (port, endpoint) = registry.create_port_from_old_spec(_portSpec)
                _workflow.add_module_port(_portSpec, _module.db_id)
	for _connection in _workflow.db_connections.itervalues():
            Connection.convert(_connection)
            _workflow.graph.add_edge( \
                _connection.source.moduleId,
                _connection.destination.moduleId,
                _connection.db_id)

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
                    in self.getModuleById(module_id).functions].index(parameter_name)
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
        return self.db_modules
    def _set_modules(self, modules):
        self.db_modules = modules
    modules = property(_get_modules, _set_modules)

    def _get_connections(self):
        return self.db_connections
    def _set_connections(self, connections):
        self.db_connections = connections
    connections = property(_get_connections, _set_connections)
	
    def clear(self):
        """clear() -> None. Erases pipeline contents."""
        self.graph = Graph()
        self.modules = {}
        self.connections = {}
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

    def checkConnection(self, c):
        """checkConnection(c: Connection) -> boolean 
        Checks semantics of connection
          
        """
        if c.source.endPoint != Port.SourceEndPoint:
            return False
        if c.destination.endPoint != Port.DestinationEndPoint:
            return False
        if not self.hasModuleWithId(c.sourceId):
            return False
        if not self.hasModuleWithId(c.destinationId):
            return False
        if c.source.type != c.destination.type:
            return False
        return True
    
    def connectsAtPort(self, p):
        """ connectsAtPort(p: Port) -> list of Connection 
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
    
    def performActionChain(self, actionChain):
        for action in actionChain:
            self.performAction(action)

    def performAction(self, action):
        for operation in action.operations:
            self.performOperation(operation)

    def performOperationChain(self, opChain):
        for op in opChain:
            self.performOperation(op)

    def performOperation(self, op):
        # print "doing %s %s" % (op.vtType, op.what)
        opMap = {('add','annotation'): self.performAddAnnotation,
                 ('add','module'): self.performAddModule,
                 ('add','connection'): self.performAddConnection,
                 ('add','portSpec'): self.performAddPortSpec,
                 ('add','parameter'): self.performAddParameter,
                 ('add','port'): self.performAddPort,
                 ('add','abstraction_ref'): self.performAddAbstractionRef,
                 ('change','annotation'): self.performChangeAnnotation,
                 ('change','module'): self.performChangeModule,
                 ('change','connection'): self.performChangeConnection,
                 ('change','portSpec'): self.performChangePortSpec,
                 ('change','parameter'): self.performChangeParameter,
                 ('change','port'): self.performChangePort,
                 ('change','abstraction_ref'): self.performChangeAbstractionRef,
                 ('delete','annotation'): self.performDeleteAnnotation,
                 ('delete','module'): self.performDeleteModule,
                 ('delete','connection'): self.performDeleteConnection,
                 ('delete','portSpec'): self.performDeletePortSpec,
                 ('delete','parameter'): self.performDeleteParameter,
                 ('delete','port'): self.performDeletePort,
                 ('delete','abstraction_ref'): self.performDeleteAbstractionRef,
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
    def performAddModule(self, op):
        self.addModule(op.data)
    def performChangeModule(self, op):
        self.deleteModule(op.oldObjId)
        self.addModule(op.data)
    def performDeleteModule(self, op):
        self.deleteModule(op.objectId)
    def performAddAbstractionRef(self, op):
        pass
    def performChangeAbstractionRef(self, op):
        pass
    def performDeleteAbstractionRef(self, op):
        pass
    def performAddConnection(self, op):
        self.addConnection(op.data)
    def performChangeConnection(self, op):
        self.deleteConnection(op.objObjId)
        self.addConnection(op.data)
    def performDeleteConnection(self, op):
        self.deleteConnection(op.objectId)
    def performAddPortSpec(self, op):
        self.add_module_port(op.data, op.parentObjId)
    def performDeletePortSpec(self, op):
        self.delete_module_port(op.objectId, op.parentObjId)
    def performChangePortSpec(self, op):
        self.delete_module_port(op.oldObjId, op.parentObjId)
        self.add_module_port(op.data, op.parentObjId)
    def performAddAnnotation(self, op):
        self.db_add_object(op.data, op.parentObjType, op.parentObjId)
    def performDeleteAnnotation(self, op):
        self.db_delete_object(op.objectId, op.what,
                              op.parentObjType, op.parentObjId)
    def performChangeAnnotation(self, op):
        op.objectId = op.oldObjId
        self.performDeleteAnnotation(op)
        op.objectId = op.newObjId
        self.performAddAnnotation(op)
    def performAddParameter(self, op):
        self.db_add_object(op.data, op.parentObjType, 
                           op.parentObjId)
        param = op.data

# FIXME param ids are unique now
#         if not self.hasAlias(param.alias):
#             self.changeAlias(param.alias, 
#                              param.type, 
#                              op.db_moduleId,
#                              op.db_parentObjId,
#                              param.id)
    
    def performDeleteParameter(self, op):
        self.db_delete_object(op.objectId, op.what,
                              op.parentObjType, op.parentObjId)

# FIXME param ids are unique now
#         self.removeAliases(mId=op.db_moduleId,
#                            fId=op.db_parentObjId)

    def performChangeParameter(self, op):
        op.objectId = op.oldObjId
        self.performDeleteParameter(op)
        op.objectId = op.newObjId
        self.performAddParameter(op)

    def performAddPort(self, op):
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
    def performDeletePort(self, op):
        connection = self.connections[op.parentObjId]
        if len(connection.ports) >= 2:
            self.graph.delete_edge(connection.sourceId, 
                                   connection.destinationId, 
                                   connection.id)
        self.db_delete_object(op.objectId, op.what,
                              op.parentObjType, op.parentObjId)
        
    def performChangePort(self, op):
        op.objectId = op.oldObjId
        self.performDeletePort(op)
        op.objectId = op.newObjId
        self.performAddPort(op)

    def add_module_port(self, portSpec, moduleId):
        self.db_add_object(portSpec, Module.vtType, moduleId)

        m = self.getModuleById(moduleId)
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
        
    def delete_module_port(self, id, moduleId):
        m = self.getModuleById(moduleId)
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

        self.db_delete_object(id, PortSpec.vtType, Module.vtType, moduleId)

    def deleteModule(self, id):
        """deleteModule(id:int) -> None 
        Delete a module from pipeline given an id.

        """
        if not self.hasModuleWithId(id):
            raise VistrailsInternalError("id missing in modules")

        # we're hiding the necessary operations by doing this!
        adj = copy.copy(self.graph.adjacency_list[id])
        inv_adj = copy.copy(self.graph.inverse_adjacency_list[id])
        for (_, conn_id) in adj:
            self.deleteConnection(conn_id)
        for (_, conn_id) in inv_adj:
            self.deleteConnection(conn_id)

        # self.modules.pop(id)
        self.db_delete_object(id, 'module')
        self.graph.delete_vertex(id)
        if id in self._module_signatures:
            del self._module_signatures[id]
        if id in self._subpipeline_signatures:
            del self._subpipeline_signatures[id]
        self.removeAliases(mId=id)

    def addModule(self, m):
        """addModule(m: Module) -> None 
        Add new module to pipeline
          
        """
        if self.hasModuleWithId(m.id):
            raise VistrailsInternalError("duplicate module id")
#         self.modules[m.id] = copy.copy(m)
        self.db_add_object(m)
        self.graph.add_vertex(m.id)
    
    def addAlias(self, name, type, mId, fId, pId):
        """addAlias(name: str, type: str, mId: int, fId: int, pId: int) -> None 
        Add alias to pipeline
          
        """
        if self.hasAlias(name):
            raise VistrailsInternalError("duplicate alias")
        self.aliases[name] = (type,mId,fId,pId)

    def removeAliasByName(self, name):
        """removeAliasByName(name: str) -> None
        Remove alias with given name """
        if self.hasAlias(name):
            del self.aliases[name]

    def removeAlias(self,type, mId, fId, pId):
        """removeAlias(name: str, type: str, mId: int, 
                       fId: int, pId: int)-> None
        Remove alias identified by type, mId, fId, pId """
        if self.aliases.inverse.has_key((type, mId,fId, pId)):
            oldname = self.aliases.inverse[(type, mId,fId, pId)]
            del self.aliases[oldname]

    def removeAliases(self, *args, **keywords):
        """removeAliases(*args, *keywords) -> None
        Batch removal of aliases. Use keywords mId and fId
        For example, 
        remove all aliases of module id 5:
        >>> pipeline.removeAliases(mId=5)
        remove all aliases of module id 5, function id 4:
        >>> pipeline.removeAliases(mId=5,fId=4)

        """
        if keywords.has_key('mId'):
            mId = keywords['mId']
            remove = []
            if keywords.has_key('fId'):
                fId = keywords['fId']
                for k,v in self.aliases.inverse.iteritems():
                    if k[1] == mId and k[2] == fId:
                        remove.append(v)
            else:
                for k,v in self.aliases.inverse.iteritems():
                    if k[1] == mId:
                      remove.append(v)
            for alias in remove:
                del self.aliases[alias]

    def changeAlias(self,name, type, mId, fId, pId):
        """changeAlias(name: str, type: str, mId: int, 
                       fId: int, pId: int)-> None
        Change alias if name is non empty. Else remove alias 
        
        """
        if name == "":
            self.removeAlias(type, mId, fId, pId)
        else:
            if not self.hasAlias(name):
                self.removeAlias(type, mId, fId, pId)
                self.addAlias(name,type,mId,fId,pId)

    def getAliasStrValue(self, name):
        """ getAliasValue(name: str) -> str
        returns the strValue of the parameter with alias name

        """
        result = ""
        if self.aliases.has_key(name):
            info = self.aliases[name]
            module = self.modules[info[1]]
            function = module.functions[info[2]]
            
            parameter = function.params[info[3]]
            result = parameter.strValue
        return result

    def setAliasStrValue(self, name, value):
        """ setAliasStrValue(name: str, value: str) -> None
        sets the strValue of the parameter with alias name 
        
        """
        if self.aliases.has_key(name):
            info = self.aliases[name]
            module = self.modules[info[1]]
            function = module.functions[info[2]]
            parameter = function.params[info[3]]
            parameter.strValue = str(value)

    def deleteConnection(self, id):
        """ deleteConnection(id:int) -> None 
        Delete connection identified by id from pipeline.
           
        """

        if not self.hasConnectionWithId(id):
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
        
    def addConnection(self, c):
        """addConnection(c: Connection) -> None 
        Add new connection to pipeline.
          
        """
        if self.hasConnectionWithId(c.id):
            raise VistrailsInternalError("duplicate connection id " + str(c.id))
#         self.connections[c.id] = copy.copy(c)
        self.db_add_object(c)
        if c.source is not None and c.destination is not None:
            assert(c.sourceId != c.destinationId)        
            self.graph.add_edge(c.sourceId, c.destinationId, c.id)
            self.ensure_connection_specs([c.id])
        
    def getModuleById(self, id):
        """getModuleById(id: int) -> Module
        Accessor. id is the Module id.
        
        """
        result = self.modules[id]
        if result.package is None:
            DebugPrint.critical('module %d is missing package' % id)
            descriptor = registry.get_descriptor_from_name_only(result.name)
            result.package = descriptor.identifier
        return result
    
    def getConnectionById(self, id):
        """getConnectionById(id: int) -> Connection
        Accessor. id is the Connection id.
        
        """
        self.ensure_connection_specs([id])
        return self.connections[id]
    
    def moduleCount(self):
        """ moduleCount() -> int 
        Returns the number of modules in the pipeline.
        
        """
        return len(self.modules)
    
    def connectionCount(self):
        """connectionCount() -> int 
        Returns the number of connections in the pipeline.
        
        """
        return len(self.connections)
    
    def hasModuleWithId(self, id):
        """hasModuleWithId(id: int) -> boolean 
        Checks whether given module exists.

        """
        return self.modules.has_key(id)
    
    def hasConnectionWithId(self, id):
        """hasConnectionWithId(id: int) -> boolean 
        Checks whether given connection exists.

        """
        return self.connections.has_key(id)

    def hasAlias(self, name):
        """hasAlias(name: str) -> boolean 
        Checks whether given alias exists.

        """
        return self.aliases.has_key(name)

    def outDegree(self, id):
        """outDegree(id: int) -> int - Returns the out-degree of a module. """
        return self.graph.out_degree(id)

    def dumpToXML(self, dom, root, timeAttr=None):
        """dumpToXML(dom, root, timeAttr=None) -> None - outputs self to xml"""
        node = dom.createElement('pipeline')
        if timeAttr is not None:
            node.setAttribute('time',str(timeAttr))
        for module in self.modules.values():
            module.dumpToXML(dom, node)
        for connection in self.connections.values():
            connection.serialize(dom, node)
        root.appendChild(node)

    def dumpToString(self):
        """ dumpToString() -> str
        Serialize this pipeline to an XML string
        
        """
        dom = getDOMImplementation().createDocument(None, 'network', None)
        root = dom.documentElement
        self.dumpToXML(dom, root)
        return str(dom.toxml())

    @staticmethod
    def loadFromXML(root):
        """ loadFromXML(root) -> Pipeline
        Return the pipeline from the XML elements
        
        """
        p = Pipeline()
        for rootXML in named_elements(root, 'pipeline'):
            for moduleXML in named_elements(rootXML, 'module'):
                p.addModule(Module.loadFromXML(moduleXML))
            for connectXML in named_elements(rootXML, 'connect'):
                p.addConnection(Connection.loadFromXML(connectXML))
        return p

    @staticmethod
    def loadFromString(s):
        """ loadFromString(s: str) -> Pipeline
        Load a pipeline from an XML string
        '
        """
        dom = parseString(s)
        root = dom.documentElement
        return Pipeline.loadFromXML(root)

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
            result.addModule(copy.copy(self.modules[module_id]))
        for (conn_from, conn_to, conn_id) in subgraph.iter_all_edges():
            result.addConnection(copy.copy(self.connections[conn_id]))
		# I haven't finished this yet. -cscheid
        raise Exception("Incomplete implementation!")
        return result

    def dump_actions(self):
        """dump_actions() -> [Action].

        Returns a list of actions that can be used to create a copy of the
        pipeline."""
        result = []
        for m in self.modules.itervalues():
            add_module = core.vistrail.action.AddModuleAction()
            add_module.module = copy.copy(m)
            result.append(add_module)
        for c in self.connections.itervalues():
            add_connection = core.vistrail.action.AddConnectionAction()
            add_connection.connection = copy.copy(c)
            result.append(add_connection)
        return result

    ##########################################################################
    # Registry-related

    def ensure_old_modules_have_package_names(self):
        """ensure_old_modules_have_package_names()

        Makes sure each module has a package associated with it.

        """
        for i in self.modules.iterkeys():
            self.getModuleById(i)

    def ensure_connection_specs(self, connection_ids=None):
        """ensure_connection_specs(connection_ids=None) -> None.

        Computes the specs for the connections in connection_ids. If
        connection_ids is None, computes it for every connection in the pipeline.
        """
        def source_spec(port):
            module = self.getModuleById(port.moduleId)
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
            module = self.getModuleById(port.moduleId)
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
        for m_id, m in self.modules.iteritems():
            if not other.modules.has_key(m_id):
                return False
            if m != other.modules[m_id]:
                return False
        for c_id, c in self.connections.iteritems():
            if not other.connections.has_key(c_id):
                return False
            if c != other.connections[c_id]:
                return False
        return True

    def __str__(self):
        return ("(Pipeline Modules: %s Graph:%s)@%X" %
                ([(m, str(v)) for (m,v) in sorted(self.modules.items())],
                 str(self.graph),
                 id(self)))


################################################################################

import unittest
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.connection import Connection

class TestPipeline(unittest.TestCase):

    def create_default_pipeline(self):
        
        p = Pipeline()

        def module1(p):
            def f1():
                f = ModuleFunction()
                f.name = 'op'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'String'
                param.strValue = '+'
                f.params.append(param)
                return f
            def f2():
                f = ModuleFunction()
                f.name = 'value1'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'Float'
                param.strValue = '2.0'
                f.params.append(param)
                return f
            def f3():
                f = ModuleFunction()
                f.name = 'value2'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'Float'
                param.strValue = '4.0'
                f.params.append(param)
                return f
            m = Module()
            m.id = p.fresh_module_id()
            m.name = 'PythonCalc'
            m.package = 'edu.utah.sci.vistrails.pythoncalc'
            m.functions.append(f1())
            return m
        
        def module2(p):
            def f1():
                f = ModuleFunction()
                f.name = 'op'
                f.returnType = 'void'
                param = ModuleParam()
                param.type = 'String'
                param.strValue = '+'
                f.params.append(param)
                return f
            m = Module()
            m.id = p.get_tmp_id(Module.vtType)
            m.name = 'PythonCalc'
            m.package = 'edu.utah.sci.vistrails.pythoncalc'
            m.functions.append(f1())
            return m
        m1 = module1(p)
        p.addModule(m1)
        m2 = module1(p)
        p.addModule(m2)
        m3 = module2(p)
        p.addModule(m3)

        c1 = Connection()
        c1.sourceId = m1.id
        c1.destinationId = m3.id
        c1.source.name = 'value'
        c1.source.moduleName = 'PythonCalc'
        c1.destination.name = 'value1'
        c1.destination.moduleName = 'PythonCalc'
        c1.id = p.get_tmp_id(Connection.vtType)
        p.addConnection(c1)

        c2 = Connection()
        c2.sourceId = m2.id
        c2.destinationId = m3.id
        c2.source.name = 'value'
        c2.source.moduleName = 'PythonCalc'
        c2.destination.name = 'value2'
        c2.destination.moduleName = 'PythonCalc'
        c2.id = p.get_tmp_id(Connection.vtType)

        p.addConnection(c2)
        p.compute_signatures()
        return p

    def setUp(self):
        self.pipeline = self.create_default_pipeline()
        self.sink_id = -3

    def test_create_pipeline_signature(self):
        self.pipeline.subpipeline_signature(self.sink_id)

    def test_delete_signatures(self):
        """Makes sure signatures are deleted when other things are."""
        p = self.create_default_pipeline()
        m_sig_size_before = len(p._module_signatures)
        c_sig_size_before = len(p._connection_signatures)
        p_sig_size_before = len(p._subpipeline_signatures)
        p.deleteConnection(-1)
        p.deleteModule(-1)
        m_sig_size_after = len(p._module_signatures)
        c_sig_size_after = len(p._connection_signatures)
        p_sig_size_after = len(p._subpipeline_signatures)
        self.assertNotEquals(m_sig_size_before, m_sig_size_after)
        self.assertNotEquals(c_sig_size_before, c_sig_size_after)
        self.assertNotEquals(p_sig_size_before, p_sig_size_after)

    def test_delete_connections(self):
        p = self.create_default_pipeline()
        p.deleteConnection(-1)
        p.deleteConnection(-2)
        p.deleteModule(-3)
        self.assertEquals(len(p.connections), 0)

    def test_basic(self):
        """Makes sure pipeline can be created, modules and connections
        can be added and deleted."""
        p = self.create_default_pipeline()
    
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
        p1.addModule(Module(name='CacheBug',
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
        p2.addModule(Module(name='CacheBug', 
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
        p1.addModule(Module(name='CacheBug', 
                            package='edu.utah.sci.vistrails.console_mode_test',
                            id=3,
                            functions=p1_functions))

        self.assertEquals(p1.find_method(3, 'i1'), 0)
        self.assertEquals(p1.find_method(3, 'i2'), 1)
        self.assertEquals(p1.find_method(3, 'i3'), -1)
        self.assertRaises(KeyError, p1.find_method, 4, 'i1')

    def test_load_and_dump(self):
        # FIXME write this test
        pass

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
        p1.addModule(Module(name='CacheBug', 
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
