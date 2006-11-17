from core.vis_types import VisPort, VistrailModuleType
from core.data_structures import Graph
from core.utils import VistrailsInternalError
import copy

################################################################################

class VisPipeline(object):
    """ A VisPipeline is a set of modules and connections between them. """
    
    def __init__(self):
        self.modules = {}
        self.connections = {}
        self.graph = Graph()

    def checkConnection(self, c):
        """ Checks semantics of connection

        Parameters
        ----------
        - c : 'VisConnection'

          The connection object to be checked
          
        """
        if c.source.endPoint != VisPort.SourceEndPoint:
            return False
        if c.destination.endPoint != VisPort.DestinationEndPoint:
            return False
        if not self.hasModuleWithId(c.sourceId):
            return False
        if not self.hasModuleWithId(c.destinationId):
            return False
        if c.source.type != c.destination.type:
            return False
        return True
    
    def connectsAtPort(self, p):
        """ Returns a list of VisConnections that connect at port p

        Parameters
        ----------
        - p : 'VistrailPort'

          The port object.

        Returns
        -------
        - 'list' of 'VisConnection'
        
        """
        result = []
        if p.endPoint == VisPort.DestinationEndPoint:
            el = self.graph.edgesTo(p.moduleId)
            for (edgeto, edgeid) in el:
                dest = self.connection[edgeid].destination
                if VTKRTTI().intrinsicPortEqual(dest, p):
                    result.append(self.connection[edgeid])
        elif p.endPoint == VisPort.SourceEndPoint:
            el = self.graph.edgesFrom(p.moduleId)
            for (edgeto, edgeid) in el:
                source = self.connection[edgeid].source
                if VTKRTTI().intrinsicPortEqual(source, p):
                    result.append(self.connection[edgeid])
        else:
            raise VistrailsInternalError("port with bogus information")
        return result
    
    def freshModuleId(self):
        """ Returns an unused module ID. If everyone always calls
        this, it is also the case that this is the smallest unused ID. So
        we can use any other number larger than the one returned, as long
        as they are contiguous.

        Returns
        -------

        - 'int'

        """
        # This is dumb and slow
        m = 0
        while self.hasModuleWithId(m):
            m += 1
        return m
    
    def freshConnectionId(self):
        """ Returns an unused connection ID

        Returns
        -------

        - 'int'
        
        """
        # This is dumb and slow
        c = 0
        while self.hasConnectionWithId(c):
            c += 1
        return c
    
    def deleteModule(self, id):
        """ Delete a module from pipeline

        Parameters
        ----------

        - id : 'int'

          Module identifier.
          
        """
        if not self.hasModuleWithId(id):
            raise VistrailsInternalError("id missing in modules")
        self.modules.pop(id)
        self.graph.deleteVertex(id)
        
    def addModule(self, m):
        """ Add new module to pipeline

        Parameters
        ----------

        - m : 'VisModule'
        
          The VisModule object to be added
          
        """
        if self.hasModuleWithId(m.id):
            raise VistrailsInternalError("duplicate module id")
        self.modules[m.id] = m
        self.graph.addVertex(m.id)
        
    def deleteConnection(self, id):
        """ Delete connection from pipeline

        Parameters
        ----------

        - id : 'int'

           The connection identifier.
           
        """
    
        if not self.hasConnectionWithId(id):
            raise VistrailsInternalError("id %s missing in connections" % id)
        conn = self.connections[id]
        self.connections.pop(id)
        self.graph.deleteEdge(conn.sourceId, conn.destinationId, conn.id)
        
    def addConnection(self, c):
        """ Add new connection to pipeline

        Parameters
        ----------

        - c : 'VisConnection'

          The connection to be added
          
        """
        if self.hasConnectionWithId(c.id):
            raise VistrailsInternalError("duplicate connection id " + str(c.id))
        self.connections[c.id] = c
        assert(c.sourceId != c.destinationId)        
        self.graph.addEdge(c.sourceId, c.destinationId, c.id)
        
    def getModuleById(self, id):
        """ Accessor. id is the VisModule id

        Parameters
        ----------

        - id : 'int'

          VisModule id

        Returns
        -------

        - 'VisModule'
        
        """
        return self.modules[id]
    
    def getConnectionById(self, id):
        """ Accessor. id is the VisConnection id

        Parameters
        ----------

        - id : 'int'

          VisConnection id

        Returns
        -------

        - 'VisConnection'
        
        """
        return self.connections[id]
    
    def moduleCount(self):
        """ Returns the number of modules in the pipeline

        Returns
        -------

        - 'int'
        
        """
        return len(self.modules)
    
    def connectionCount(self):
        """ Returns rhe number of connections in the pipeline

        Returns
        -------

        - 'int'
        
        """
        return len(self.connections)
    
    def hasModuleWithId(self, id):
        """ Checks whether given module exists

        Parameters
        ----------

        - id : 'int'

          VisModule id

        Returns
        -------

        - 'Boolean'

        """
        return self.modules.has_key(id)
    
    def hasConnectionWithId(self, id):
        """ Checks whether given connection exists

        Parameters
        ----------

        - id : 'int'

          VisConnection id

        Returns
        -------

        - 'boolean'

        """
        return self.connections.has_key(id)
    
    def outDegree(self, id):
        """ p.outDegree(id) - Returns the out-degree of a module

        Parameters
        ----------

        - id : 'int'
          the module id

        Returns
        -------

        - 'int'
        
        """
        return self.graph.outDegree(id)

    def __copy__(self):
        cp = VisPipeline()
        cp.modules = dict([(k,copy.copy(v))
                           for (k,v)
                           in self.modules.iteritems()])
        cp.connections = dict([(k,copy.copy(v))
                               for (k,v)
                               in self.connections.iteritems()])
        cp.graph = copy.copy(self.graph)
        return cp

    def getNameDependencies(self,astList):
        from types import ListType
        result = []
        if astList[0]==1: # NAME token
            result += [astList[1]]
        else:
            for e in astList:
                if type(e) is ListType:
                    result += self.getNameDependencies(e)
        return result

    def buildAliasDictionary(self):
        # TODO: Fix this.
        from gui.qmodulefunctiongroupbox import QPythonValueLineEdit
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
                                aliases[palias] = (p.type, QPythonValueLineEdit.parseExpression(str(p.strValue)))
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
        
        for e in exps: base = base[:e[0]] + str(eval(e[1],
                                                     {'datetime':locals()['datetime']},
                                                     aliases)) + base[e[0]:]
        if not atype in ['string', 'String']: base = eval(base,None,None)
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
            aliases[alias] = casting[atype](self.evaluateExp(atype,base,exps,aliases))

        # Evaluate all expressions
        # TODO: Fix this
        from gui.qmodulefunctiongroupbox import QPythonValueLineEdit
        for mid in self.modules:
            for f in self.modules[mid].functions:
                for p in f.params:
                    if p.alias and p.alias!='':
                        p.evaluatedStrValue = str(aliases[p.alias])
                    else:
                        (base,exps) = QPythonValueLineEdit.parseExpression(str(p.strValue))
                        p.evaluatedStrValue = str(self.evaluateExp(p.type,base,exps,aliases))
        return aliases

################################################################################        
