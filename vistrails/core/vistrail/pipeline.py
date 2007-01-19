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
from core.vistrail.port import Port
from core.vistrail.module_param import VistrailModuleType
from core.data_structures import Graph
from core.utils import VistrailsInternalError
from core.utils import expression
from core.cache.hasher import Hasher
import core.modules.module_registry

import copy
from types import ListType
import sha

################################################################################

class Pipeline(object):
    """ A Pipeline is a set of modules and connections between them. """
    
    def __init__(self):
        """ __init__() -> Pipeline
        Initializes modules, connections and graph.

        """
        self.modules = {}
        self.connections = {}
        self.graph = Graph()
        self._subpipeline_signatures = {}
        self._module_signatures = {}
        self._module_signatures_inv = {}

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
            el = self.graph.edgesTo(p.moduleId)
            for (edgeto, edgeid) in el:
                dest = self.connection[edgeid].destination
                if VTKRTTI().intrinsicPortEqual(dest, p):
                    result.append(self.connection[edgeid])
        elif p.endPoint == Port.SourceEndPoint:
            el = self.graph.edgesFrom(p.moduleId)
            for (edgeto, edgeid) in el:
                source = self.connection[edgeid].source
                if VTKRTTI().intrinsicPortEqual(source, p):
                    result.append(self.connection[edgeid])
        else:
            raise VistrailsInternalError("port with bogus information")
        return result
    
    def freshModuleId(self):
        """freshModuleId() -> int 
        Returns an unused module ID. If everyone always calls
        this, it is also the case that this is the smallest unused ID. So
        we can use any other number larger than the one returned, as long
        as they are contiguous.

        """
        # This is dumb and slow
        m = 0
        while self.hasModuleWithId(m):
            m += 1
        return m
    
    def freshConnectionId(self):
        """freshConnectionId() -> int 
        Returns an unused connection ID.
        
        """
        # This is dumb and slow
        c = 0
        while self.hasConnectionWithId(c):
            c += 1
        return c
    
    def deleteModule(self, id):
        """deleteModule(id:int) -> None 
        Delete a module from pipeline given an id.

        """
        if not self.hasModuleWithId(id):
            raise VistrailsInternalError("id missing in modules")
        self.modules.pop(id)
        self.graph.deleteVertex(id)
        
    def addModule(self, m):
        """addModule(m: Module) -> None 
        Add new module to pipeline
          
        """
        if self.hasModuleWithId(m.id):
            raise VistrailsInternalError("duplicate module id")
        self.modules[m.id] = m
        self.graph.addVertex(m.id)
        
    def deleteConnection(self, id):
        """ deleteConnection(id:int) -> None 
        Delete connection identified by id from pipeline.
           
        """
        if not self.hasConnectionWithId(id):
            raise VistrailsInternalError("id %s missing in connections" % id)
        conn = self.connections[id]
        self.connections.pop(id)
        self.graph.deleteEdge(conn.sourceId, conn.destinationId, conn.id)
        
    def addConnection(self, c):
        """addConnection(c: Connection) -> None 
        Add new connection to pipeline.
          
        """
        if self.hasConnectionWithId(c.id):
            raise VistrailsInternalError("duplicate connection id " + str(c.id))
        self.connections[c.id] = c
        assert(c.sourceId != c.destinationId)        
        self.graph.addEdge(c.sourceId, c.destinationId, c.id)
        
    def getModuleById(self, id):
        """getModuleById(id: int) -> Module
        Accessor. id is the Module id.
        
        """
        return self.modules[id]
    
    def getConnectionById(self, id):
        """getConnectionById(id: int) -> Connection
        Accessor. id is the Connection id.
        
        """
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
    
    def outDegree(self, id):
        """outDegree(id: int) -> int - Returns the out-degree of a module. """
        return self.graph.outDegree(id)

    def __copy__(self):
        """ __copy__() -> Pipeline - Returns a clone of itself """ 
        cp = Pipeline()
        cp.modules = dict([(k,copy.copy(v))
                           for (k,v)
                           in self.modules.iteritems()])
        cp.connections = dict([(k,copy.copy(v))
                               for (k,v)
                               in self.connections.iteritems()])
        cp.graph = copy.copy(self.graph)
        return cp

    def getNameDependencies(self, astList):
        """getNameDependencies(astList) -> list of something 
        
        """
        
        result = []
        if astList[0]==1: # NAME token
            result += [astList[1]]
        else:
            for e in astList:
                if type(e) is ListType:
                    result += self.getNameDependencies(e)
        return result

    def buildAliasDictionary(self):
        aliases = {}
        for mid in self.modules:
            for f in self.modules[mid].functions:
                fsig = f.getSignature()
                for pidx in range(len(f.params)):
                    palias = f.params[pidx].alias
                    if palias and palias!='':
                        for f1 in reversed(self.modules[mid].functions):
                            if f1.getSignature()==fsig:
                                p = f1.params[pidx]
                                aliases[palias] = (p.type, expression.parseExpression(str(p.strValue)))
                                break
        return aliases

    def computeEvaluationOrder(self, aliases):
        # Build the dependencies graph
        import parser        
        dp = {}
        for alias,(atype,(base,exp)) in aliases.items():
            edges = []
            for e in exp:
                edges += self.getNameDependencies(parser.expr(e[1]).tolist())
            dp[alias] = edges
            
        # Topological Sort to find the order to compute aliases
        # Just a slow implementation, O(n^3)...
        unordered = copy.copy(list(aliases.keys()))
        ordered = []
        while unordered:
            added = []
            for i in range(len(unordered)):
                ok = True
                u = unordered[i]
                for j in range(len(unordered)):
                    if i!=j:
                        for v in dp[unordered[j]]:
                            if u==v:
                                ok = False
                                break
                        if not ok: break
                if ok: added.append(i)
            if not added:
                print 'Looping dependencies detected!'
                break
            for i in reversed(added):
                ordered.append(unordered[i])
                del unordered[i]
        return ordered

    def evaluateExp(self, atype, base, exps, aliases):
        import datetime        
        for e in exps: base = (base[:e[0]] +
                               str(eval(e[1],
                                        {'datetime':locals()['datetime']},
                                        aliases)) +
                               base[e[0]:])
        if not atype in ['string', 'String']:
            if base=='':
                base = '0'
            base = eval(base,None,None)
        return base

    def resolveAliases(self, customAliases=None):
        # Compute the 'locals' dictionary by evaluating named expressions
        if not customAliases:
            aliases = self.buildAliasDictionary()
        else:
            aliases = copy.copy(customAliases)
        ordered = self.computeEvaluationOrder(aliases)
        casting = {'int': int, 'float': float, 'double': float, 'string': str,
                   'Integer': int, 'Float': float, 'String': str}
        for alias in reversed(ordered):
            (atype,(base,exps)) = aliases[alias]
            value = self.evaluateExp(atype,base,exps,aliases)
            aliases[alias] = casting[atype](value)

        for mid in self.modules:
            for f in self.modules[mid].functions:
                for p in f.params:
                    if p.alias and p.alias!='':
                        p.evaluatedStrValue = str(aliases[p.alias])
                    else:
                        (base,exps) = expression.parseExpression(
                            str(p.strValue))
                        p.evaluatedStrValue = str(
                            self.evaluateExp(p.type,base,exps,aliases))
        return aliases

    def module_signature(self, module_id):
        if not self._module_signatures.has_key(module_id):
            m = self.modules[module_id]
            sig = core.modules.module_registry.registry.module_signature(m)
            self._module_signatures[module_id] = sig
        return self._module_signatures[module_id]

    def subpipeline_signature(self, module_id):
        if not self._subpipeline_signatures.has_key(module_id):
            upstream_sigs = [(self.subpipeline_signature(m) +
                              Hasher.connection_signature(
                                  self.connections[edge_id]))
                             for (m, edge_id) in
                             self.graph.edgesTo(module_id)]
            module_sig = self.module_signature(module_id)
            sig = Hasher.subpipeline_signature(module_sig,
                                               upstream_sigs)
            self._subpipeline_signatures[module_id] = sig
        return self._module_signatures[module_id]
        
        
################################################################################        

import unittest
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.connection import Connection

class TestPipeline(unittest.TestCase):

    def setUp(self):
        
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
            m.id = p.freshModuleId()
            m.name = 'PythonCalc'
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
            m.id = p.freshModuleId()
            m.name = 'PythonCalc'
            m.functions.append(f1())
            return m
        
        self.pipeline = p
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
        c1.destination.name = 'PythonCalc'
        c1.id = p.freshConnectionId()
        p.addConnection(c1)

        c2 = Connection()
        c2.sourceId = m2.id
        c2.destinationId = m3.id
        c2.source.name = 'value'
        c2.source.moduleName = 'PythonCalc'
        c2.destination.name = 'value2'
        c2.destination.name = 'PythonCalc'
        c2.id = p.freshConnectionId()

        p.addConnection(c2)
        self.sink_id = m3.id

    def testCreatePipeline(self):
        self.pipeline.subpipeline_signature(self.sink_id)


if __name__ == '__main__':
    unittest.main()
