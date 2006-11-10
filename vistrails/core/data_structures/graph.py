import math
import random
import copy

from core.data_structures.queue import Queue

################################################################################

class Graph(object):
    """Graph holds a graph with possible multiple edges. The
    datastructures are all dictionary-based, so datatypes more general than ints
    can be used. For example:
    
    >>> import graph
    >>> g = graph.Graph()
    >>> g.addVertex('foo')
    >>> g.addVertex('bar')
    >>> g.addEdge('foo', 'bar', 'edge_foo')
    >>> g.addEdge('foo', 'bar', 'edge_bar')
    >>> g.addEdge('bar', 'foo', 'edge_back')
    >>> g.outDegree('foo')
    2
    >>> g.outDegree('bar')
    1    
    """
    
    def __init__(self):
        """Initialize an empty graph"""
        self.vertices = {}
        self.adjacencyList = {}
        self.inverseAdjacencyList = {}

    def addVertex(self, id):
        """Add a vertex to the graph if it is not already in the graph"""
        if not self.vertices.has_key(id):
            self.vertices[id] = None
            self.adjacencyList[id] = []
            self.inverseAdjacencyList[id] = []
            
    def inverse(self):
        """Inverse all edge directions on the graph"""
        result = copy.copy(self)
        t = result.adjacencyList
        result.adjacencyList = result.inverseAdjacencyList
        result.inverseAdjacencyList = t
        return result

    def addEdge(self, froom, to, id=None):
        """ Add an edge from vertex 'froom' to vertex 'to'

        Parameters
        ----------

        - froom : 'immutable'
          origin vertex
          
        - to : 'immutable'
          destination vertex

        - id : 'immutable'
          edge id
          
        """
        self.addVertex(froom)
        self.addVertex(to)
        self.adjacencyList[froom].append((to, id))
        self.inverseAdjacencyList[to].append((froom, id))
        
    def deleteVertex(self, id):
        """ Remove a vertex from graph

        Parameters
        ----------

        - id : 'immutable'
          vertex id
          
        """
        self.adjacencyList.pop(id)
        self.inverseAdjacencyList.pop(id)
        self.vertices.pop(id)
        
    def deleteEdge(self, froom, to, id):
        """ Remove an edge from graph

        Parameters
        ----------

        - froom : 'immutable'
          origin vertex

        - to : 'immutable'
          destination vertex

        - id : 'immutable'
          edge id
          
        """
        if id == None:
            ids_froom = []
            ids_to = []
            efroom = self.adjacencyList[froom]
            for edge in efroom:
                if edge[0] == to:
                    id = edge[1]
                    break
        self.adjacencyList[froom].remove((to, id))
        self.inverseAdjacencyList[to].remove((froom, id))
        
    def outDegree(self, froom):
        """ Returns the number of edges leaving 'froom'

        Parameters
        ----------

        - froom : 'immutable'
          vertex id

        Returns
        -------

        - 'immutable'
        
        """
        return len(self.adjacencyList[froom])
    
    def inDegree(self, to):
        """ Returns the number of edges entering 'to'

        Parameters
        ----------

        - to : 'immutable'
          vertex id

        Returns
        -------

        - 'immutable'
        
        """
        return len(self.inverseAdjacencyList[to])
    
    def sinks(self):
        """ Returns list of vertex ids which outDegree is zero

        Returns
        -------

        - 'list' of 'immutable'
        
        """
        return [idx for idx in self.vertices.keys() if self.outDegree(idx) == 0]
    
    def sources(self):
        """ Returns list of vertex ids which inDegree is zero

        Returns
        -------

        - 'list' of 'immutable'
        
        """
        return [idx for idx in self.vertices.keys() if self.inDegree(idx) == 0]

    def edgesTo(self, id):
        """ Returns edges entering vertex id
        
        Parameters
        ----------

        - id : 'immutable'
          vertex id

        Returns
        -------

        - 'list' of ('immutable','immutable')
        
        """
        return self.inverseAdjacencyList[id]

    def edgesFrom(self, id):
        """ Returns edges leaving vertex id
        
        Parameters
        ----------

        - id : 'immutable'
          vertex id

        Returns
        -------

        - 'list' of ('immutable','immutable')
        
        """
        return self.adjacencyList[id]

    def __str__(self):
        """ Returns a formatted version of the graph

        Returns
        -------

        - 'str'
        
        """
        vs = self.vertices.keys()
        vs.sort()
        al = reduce(lambda a,b: a + b,
                    [map(lambda (t, i): (f, t, i), l)
                     for (f, l) in self.adjacencyList.items()])
        al.sort(edge_cmp)
        return "digraph G { " \
               + ";".join([str(s) for s in vs]) + ";" \
               + ";".join(["%s -> %s [label=\"%s\"]" % s for s in al]) + "}"

    def __repr__(self):
        """ This function is much like __str__(), it returns a string
        version of the graph

        Returns
        -------

        - 'str'

        """
        return self.__str__()

    def fromRandom(size):
        """ Create a dag with ~ size/e vertices and 3*|vertex| edges
        
        Returns
        -------

        - 'Graph'
        
        """
        result = Graph()
        verts = filter(lambda x: x>0, peckcheck.a_list(peckcheck.an_int)(size))
        for v in verts:
            result.addVertex(v)
        k = size / math.e
        p = (6*k) / ((k+1)*(k+2))
        eid = 0
        for v in verts:
            for k in verts:
                if v < k and random.random() > p:
                    result.addEdge(v, k, eid)
                    eid = eid + 1
        return result

    def __copy__(self):
        """Make a copy of the graph"""
        cp = Graph()
        cp.vertices = copy.deepcopy(self.vertices)
        cp.adjacencyList = copy.deepcopy(self.adjacencyList)
        cp.inverseAdjacencyList = copy.deepcopy(self.inverseAdjacencyList)
        return cp

    def bfs(self, frm):
        """Perform Breadth-First-Search and return a dict of parent"""
        visited = set([frm])
        parent = {}
        q = Queue()
        q.push(frm)
        while len(q):
            current = q.pop()
            efrom = self.edgesFrom(current)
            for (to, eid) in efrom:
                if to not in visited:
                    parent[to] = current
                    q.push(to)
                    visited.add(to)
        return parent

    def parent(self, v):
        """Return the parent of vertex v"""
        try:
            l=self.inverseAdjacencyList[v]
        except KeyError:
            return -1
        if len(l):
            (froom, a) = l.pop()
        else: froom=0
        return froom
    
    fromRandom = staticmethod(fromRandom)

def edge_cmp(v1, v2):
    """ Defines how the comparison must be done between edges 

    Parameters
    ----------
    - v1 : 'sequence'
      edge information
      
    - v2 : 'sequence'
      other edge information
    
    Returns
    -------

    - 'boolean'
    
    """
    (from1, to1, id1) = v1
    (from2, to2, id2) = v2
    c1 = cmp(from1, from2)
    if c1:
        return c1
    c2 = cmp(to1, to2)
    if c2:
        return c2
    else:
        return cmp(id1, id2)

################################################################################

import unittest
import random

class TestGraph(unittest.TestCase):
     """ Class to test Graph

     It tests vertex addition, the outDegree of a sink and inDegree of a source
     consistencies.
    
     """
     
     def test1(self):
         """Test adding edges and vertices"""
         g = Graph()
         g.addVertex('0')
         g.addVertex('1')
         g.addVertex('2')
         g.addVertex('3')
         g.addEdge('0', '1', 0)
         g.addEdge('1', '2', 1)
         g.addEdge('2', '3', 2)
         parent = g.bfs('0')
         self.assertEquals(parent['3'], '2')
         self.assertEquals(parent['2'], '1')
         self.assertEquals(parent['1'], '0')

     def test2(self):
         """Test bread-first-search"""
         g = Graph()
         g.addVertex(0)
         g.addVertex(1)
         g.addVertex(2)
         g.addVertex(3)
         g.addVertex(4)
         g.addEdge(0,1,0)
         g.addEdge(1,2,1)
         g.addEdge(0,3,2)
         g.addEdge(3,2,3)
         g.addEdge(2,4,4)
         p = g.bfs(0)
         k = p.keys()
         k.sort()
         self.assertEquals(k, [1, 2, 3, 4])
         inv = g.inverse()
         p_inv = inv.bfs(4)
         k2 = p_inv.keys()
         k2.sort()
         self.assertEquals(k2, [0, 1, 2, 3])
         
     def test3(self):
         """Test sink and source degree consistency"""
         g = Graph()
         for i in range(100):
             g.addVertex(i);
         for i in range(1000):
             v1 = random.randint(0,99)
             v2 = random.randint(0,99)
             g.addEdge(v1, v2, i)
         sinkResult = [None for i in g.sinks() if g.outDegree(i) == 0]
         sourceResult = [None for i in g.sinks() if g.outDegree(i) == 0]
         assert len(sinkResult) == len(g.sinks())
         assert len(sourceResult) == len(g.sources())

if __name__ == '__main__':
    unittest.main()
