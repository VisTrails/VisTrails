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
        """ Graph() -> Graph
        Initialize an empty graph and return nothing

        """
        self.vertices = {}
        self.adjacencyList = {}
        self.inverseAdjacencyList = {}

    def addVertex(self, id):
        """ addVertex(id: id type) -> None
        Add a vertex to the graph if it is not already in the graph
        and return nothing

        Keyword arguments:
        id -- vertex id
        
        """
        if not self.vertices.has_key(id):
            self.vertices[id] = None
            self.adjacencyList[id] = []
            self.inverseAdjacencyList[id] = []
            
    def inverse(self):
        """inverse() -> Graph
        Inverse all edge directions on the graph and return a Graph

        """
        result = copy.copy(self)
        t = result.adjacencyList
        result.adjacencyList = result.inverseAdjacencyList
        result.inverseAdjacencyList = t
        return result

    def inverse_immutable(self):
        """inverse_immutable() -> Graph
        
Fast version of inverse(), but requires that output not be mutated (it
shares with self.)
        """
        result = Graph()
        result.vertices = self.vertices()
        result.adjacencyList = self.inverseAdjacencyList
        result.inverseAdjacencyList = self.adjacencyList
        return result

    def addEdge(self, froom, to, id=None):
        """ addEdge(froom: id type, to: id type, id: id type) -> None
        Add an edge from vertex 'froom' to vertex 'to' and return nothing

        Keyword arguments:
        froom -- 'immutable' origin vertex id
        to    -- 'immutable' destination vertex id
        id    -- 'immutable' edge id (default None)
          
        """
        self.addVertex(froom)
        self.addVertex(to)
        self.adjacencyList[froom].append((to, id))
        self.inverseAdjacencyList[to].append((froom, id))
        
    def deleteVertex(self, id):
        """ deleteVertex(id: id type) -> None
        Remove a vertex from graph and return nothing

        Keyword arguments:
        -- id : 'immutable' vertex id
          
        """
        self.adjacencyList.pop(id)
        self.inverseAdjacencyList.pop(id)
        self.vertices.pop(id)
        
    def deleteEdge(self, froom, to, id):
        """ deleteEdge(froom: id type, to: id type, id: id type) -> None
        Remove an edge from graph and return nothing

        Keyword arguments:
        froom -- 'immutable' origin vertex id
        to    -- 'immutable' destination vertex id
        id    -- 'immutable' edge id
          
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
        """ outDegree(froom: id type) -> int
        Compute the number of edges leaving 'froom' and return an int

        Keyword arguments:
        froom -- 'immutable' vertex id

        """
        return len(self.adjacencyList[froom])
    
    def inDegree(self, to):
        """ inDegree(to: id type) -> int
        Compute the number of edges entering 'to' and return an int

        Keyword arguments:
        to -- 'immutable' vertex id

        """
        return len(self.inverseAdjacencyList[to])
    
    def sinks(self):
        """ sinks() -> list(id type)
        Find all vertices whose outDegree is zero and return a list of ids

        """
        return [idx for idx in self.vertices.keys() if self.outDegree(idx) == 0]
    
    def sources(self):
        """ sources() -> list(id type)
        Find all vertices whose inDegree is zero and return a list of ids

        """
        return [idx for idx in self.vertices.keys() if self.inDegree(idx) == 0]

    def edgesTo(self, id):
        """ edgesTo(id: id type) -> list(list)
        Find edges entering a vertex id and return a list of tuples (id,id)

        Keyword arguments:
        id : 'immutable' vertex id
        
        """
        return self.inverseAdjacencyList[id]

    def edgesFrom(self, id):
        """ edgesFrom(id: id type) -> list(list)
        Find edges leaving a vertex id and return a list of tuples (id,id)
        
        Keyword arguments:
        id : 'immutable' vertex id

        """
        return self.adjacencyList[id]

    def __str__(self):
        """ __str__() -> str
        Format the graph for serialization and return a string

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
        """ __repr__() -> str
        Similar to __str__ to re-represent the graph and returns a string

        """
        return self.__str__()

    def fromRandom(size):
        """ fromRandom(size:int) -> Graph
        Create a DAG with approximately size/e vertices and 3*|vertex| edges
        and return a Graph

        Keyword arguments:
        size -- the estimated size of the graph to generate

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
        """ __copy__() -> Graph
        Make a copy of the graph and return a Graph

        """
        cp = Graph()
        cp.vertices = copy.deepcopy(self.vertices)
        cp.adjacencyList = copy.deepcopy(self.adjacencyList)
        cp.inverseAdjacencyList = copy.deepcopy(self.inverseAdjacencyList)
        return cp

    def bfs(self, frm):
        """ bfs(frm:id type) -> dict(id type)
        Perform Breadth-First-Search and return a dict of parent id

        Keyword arguments:
        frm -- 'immutable' vertex id

        """
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

    def dfs(self):
        """ dfs(self) -> (discovery, parent, finish)
        Performs a depth-first search on a graph and returns three dictionaries with
        relevant information. See CLRS p. 541. """

        # Ugly ugly python
        # http://mail.python.org/pipermail/python-list/2006-April/378964.html
        class Closure(object):
            pass
        
        # Straight CLRS p.541
        White = 0
        Gray = 1
        Black = 2
        data = Closure()
        data.color = {}
        data.discovery = {} # d in CLRS
        data.parent = {} # \pi in CLRS
        data.finish = {}  # f in CLRS
        data.t = 0

        def visit(u):
            data.color[u] = Gray
            data.t += 1
            data.discovery[u] = data.t
            for (v, edge_id) in self.adjacencyList[u]:
                if data.color[v] == White:
                    data.parent[v] = u
                    visit(v)
            data.color[u] = Black
            data.t += 1
            data.finish[u] = data.t
            
        for vertex in self.vertices:
            data.color[vertex] = White
        for vertex in self.vertices:
            if data.color[vertex] == White:
                visit(vertex)
        return (data.discovery, data.parent, data.finish)
        

    def parent(self, v):
        """ parent(v: id type) -> id type
        Find the parent of vertex v and return an id

        Keyword arguments:
        v -- 'immutable' vertex id

        """
        try:
            l=self.inverseAdjacencyList[v]
        except KeyError:
            return -1
        if len(l):
            (froom, a) = l.pop()
        else: froom=0
        return froom
    
    def vertices_topological_sort(self):
        """ vertices_topological_sort(self) ->
sequence(vertices) Returns an iterator for a sequence of all vertices,
so that they are in reverse topological sort order (every node
traversed is such that their parent nodes have already been traversed)
        """
        (d, p, f) = self.dfs()
        lst = [(v, k) for (k,v) in f.iteritems()]
        lst.sort()
        lst.reverse()
        return [v for (k, v) in lst]
        
        

    fromRandom = staticmethod(fromRandom) 

def edge_cmp(v1, v2):
    """ edge_cmp(v1: id type, v2:id type) -> int
    Defines how the comparison must be done between edges  and return a boolean

    Keyword arguments:
    v1 -- 'sequence' edge information
    v2 -- 'sequence' other edge information
    
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

     def testDFS(self):
         """Test DFS on graph."""
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
         g.dfs()

     def testTopologicalSort(self):
         """Test toposort on graph."""
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
         g.vertices_topological_sort()

if __name__ == '__main__':
    unittest.main()
