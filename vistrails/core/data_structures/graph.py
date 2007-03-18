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


from itertools import imap, chain, izip

from core.utils import withIndex, iter_with_index, all
from core.data_structures.queue import Queue

################################################################################
# Graph

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

    ##########################################################################
    # Constructor
    
    def __init__(self):
        """ Graph() -> Graph
        Initialize an empty graph and return nothing

        """
        self.vertices = {}
        self.adjacencyList = {}
        self.inverseAdjacencyList = {}

    ##########################################################################
    # Accessors

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
        result.vertices = self.vertices
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
        
        for (origin, edge_id) in self.inverseAdjacencyList[id]:
            t = (id, edge_id)
            self.adjacencyList[origin].remove(t)
        for (dest, edge_id) in self.adjacencyList[id]:
            t = (id, edge_id)
            self.inverseAdjacencyList[dest].remove(t)
        self.adjacencyList.pop(id)
        self.inverseAdjacencyList.pop(id)
        self.vertices.pop(id)
        
    def deleteEdge(self, froom, to, id=None):
        """ deleteEdge(froom: id type, to: id type, id: id type) -> None
        Remove an edge from graph and return nothing

        Keyword arguments:
        froom -- 'immutable' origin vertex id
        to    -- 'immutable' destination vertex id
        id    -- 'immutable' edge id
          
        """
        if id == None:
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

    def get_edge(self, frm, to):
        """ get_edge(frm, to) -> edge_id

        Returns the id from the edge from->to."""
        for (t, e_id) in self.edgesFrom(frm):
            if t == to:
                return e_id

    ##########################################################################
    # Graph algorithms

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

    class GraphContainsCycles(Exception):
        def __init__(self, v1, v2):
            self.back_edge = (v1, v2)
        def __str__(self):
            return ("Graph contains cycles: back edge %s encountered" %
                    self.back_edge)

    def dfs(self,
            vertex_set=None,
            raise_if_cyclic=False,
            enter_vertex=None,
            leave_vertex=None):
        """ dfs(self,vertex_set=None,raise_if_cyclic=False,enter_vertex=None,
                leave_vertex=None) -> (discovery, parent, finish)
        Performs a depth-first search on a graph and returns three dictionaries with
        relevant information. If vertex_set is not None, then it is used as
        the list of ids to perform the DFS on.
        
        See CLRS p. 541.

        enter_vertex, when present, is called just before visiting a vertex
        for the first time (and only once) with the vertex id as a parameter.

        leave_vertex, when present, is called just after visiting a vertex
        for the first time (and only once) with the vertex id as a parameter.
        """

        if not vertex_set:
            vertex_set = self.vertices

        # Ugly ugly python
        # http://mail.python.org/pipermail/python-list/2006-April/378964.html

        # We cannot explicitly "del data":
        # http://www.python.org/dev/peps/pep-0227/
        
        class Closure(object):
            
            def clear(self):
                del self.color
                del self.discovery
                del self.parent
                del self.finish
                del self.t
        
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
                if not v in data.color:
                    data.color[v] = White
                if data.color[v] == White:
                    data.parent[v] = u
                    if enter_vertex: enter_vertex(v)
                    visit(v)
                    if leave_vertex: leave_vertex(v)
                if raise_if_cyclic and data.color[v] == Gray:
                    raise self.GraphContainsCycles(u, v)
            data.color[u] = Black
            data.t += 1
            data.finish[u] = data.t

        for vertex in vertex_set:
            data.color[vertex] = White
        for vertex in vertex_set:
            if data.color[vertex] == White:
                visit(vertex)

        result = (data.discovery, data.parent, data.finish)
        data.clear()
        return result

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
    
    def vertices_topological_sort(self,vertex_set=None):
        """ vertices_topological_sort(self,vertex_set=None) ->
sequence(vertices) Returns a sequence of all vertices, so that they
are in topological sort order (every node traversed is such that their
parent nodes have already been traversed). vertex_set is optionally a
list of vertices on which to perform the topological sort.
        """
        (d, p, f) = self.dfs(vertex_set,raise_if_cyclic=True)
        lst = [(v, k) for (k,v) in f.iteritems()]
        lst.sort()
        lst.reverse()
        return [v for (k, v) in lst]

    def topologically_contractible(self, subgraph):
        """topologically_contractible(subgraph) -> Boolean.

Returns true if contracting the subgraph to a single vertex doesn't create
cycles. This is equivalent to checking whether
a pipeline subgraph forms a legal abstraction."""

        x = copy.copy(self)
        conns_to_subgraph = self.connections_to_subgraph(subgraph)
        conns_from_subgraph = self.connections_from_subgraph(subgraph)
        for v in subgraph.vertices.iterkeys():
            x.deleteVertex(v)
        free_vertex = max(subgraph.vertices.iterkeys()) + 1
        x.addVertex(free_vertex)
        for (edge_from, edge_to, edge_id) in conns_to_subgraph:
            x.addEdge(free_vertex, edge_to)
        for (edge_from, edge_to, edge_id) in conns_from_subgraph:
            x.addEdge(edge_from, free_vertex)
        try:
            x.vertices_topological_sort()
            return True
        except self.GraphContainsCycles:
            return False

    ##########################################################################
    # Subgraphs

    def subgraph(self, vertex_set):
        """ subgraph(vertex_set) -> Graph.

Returns a subgraph of self containing all vertices and connections
between them."""
        result = Graph()
        vertex_set = set(vertex_set)
        # add vertices
        for vertex in vertex_set:
            result.addVertex(vertex)
        # add edges
        for vertex_from in vertex_set:
            for (vertex_to, edge_id) in self.edgesFrom(vertex_from):
                if vertex_to in vertex_set:
                    result.addEdge(vertex_from, vertex_to, edge_id)
        return result

    def connections_to_subgraph(self, subgraph):
        """connections_to_subgraph(subgraph) -> [(vert_from, vert_to, edge_id)]

Returns the list of all edges that connect to a vertex \in subgraph. subgraph
is assumed to be a subgraph of self"""
        vertices_to_traverse = set(self.vertices.iterkeys())
        subgraph_verts = set(subgraph.vertices.iterkeys())
        vertices_to_traverse -= subgraph_verts

        result = []
        for v in vertices_to_traverse:
            for e in self.adjacencyList[v]:
                (v_to, e_id) = e
                if v_to in subgraph_verts:
                    result.append((v, v_to, e_id))
        return result

    def connections_from_subgraph(self, subgraph):
        """connections_from_subgraph(subgraph) -> [(vert_from, vert_to, edge_id)]

Returns the list of all edges that connect from a vertex \in subgraph to a vertex
\not \in subgraph. subgraph is assumed to be a subgraph of self"""
        subgraph_verts = set(subgraph.vertices.iterkeys())
        vertices_to_traverse = subgraph_verts

        result = []
        for v in vertices_to_traverse:
            for e in self.adjacencyList[v]:
                (v_to, e_id) = e
                if v_to not in subgraph_verts:
                    result.append((v, v_to, e_id))
        return result

    ##########################################################################
    # Iterators

    def iter_edges_from(self, vertex):
        """iter_edges_from(self, vertex) -> iterable

        Returns an iterator over all edges in the form
        (vertex, vert_to, edge_id)."""
        def fn(edge):
            (edge_to, edge_id) = edge
            return (vertex, edge_to, edge_id)
        return imap(fn, self.adjacencyList[vertex])

    def iter_edges_to(self, vertex):
        """iter_edges_to(self, vertex) -> iterable

        Returns an iterator over all edges in the form
        (vertex, vert_to, edge_id)."""
        def fn(edge):
            (edge_from, edge_id) = edge
            return (edge_from, vertex, edge_id)
        return imap(fn, self.inverseAdjacencyList[vertex])

    def iter_all_edges(self):
        """iter_all_edges() -> iterable

        Returns an iterator over all edges in the graph in the form
        (vert_from, vert_to, edge_id)."""
        verts = self.iter_vertices()
        edge_itors = imap(self.iter_edges_from, verts)
        return chain(*[v for v in edge_itors])

    def iter_vertices(self):
        """iter_vertices() -> iterable

        Returns an iterator over all vertex ids of the graph."""
        return self.vertices.iterkeys()

    ##########################################################################
    # Special Python methods

    def __str__(self):
        """ __str__() -> str
        Format the graph for serialization and return a string

        """
        vs = self.vertices.keys()
        vs.sort()
        al = []
        for i in [map(lambda (t, i): (f, t, i), l)
                  for (f, l) in self.adjacencyList.items()]:
            al.extend(i)
        al.sort(edge_cmp)
        return "digraph G { " \
               + ";".join([str(s) for s in vs]) + ";" \
               + ";".join(["%s -> %s [label=\"%s\"]" % s for s in al]) + "}"

    def __repr__(self):
        """ __repr__() -> str
        Similar to __str__ to re-represent the graph and returns a string

        """
        return self.__str__()

    def __copy__(self):
        """ __copy__() -> Graph
        Make a copy of the graph and return a Graph

        """
        cp = Graph()
        cp.vertices = copy.deepcopy(self.vertices)
        cp.adjacencyList = copy.deepcopy(self.adjacencyList)
        cp.inverseAdjacencyList = copy.deepcopy(self.inverseAdjacencyList)
        return cp

    ##########################################################################
    # Etc

    @staticmethod
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
# Unit testing

import unittest
import random

class TestGraph(unittest.TestCase):
     """ Class to test Graph

     It tests vertex addition, the outDegree of a sink and inDegree of a source
     consistencies.
    
     """

     def make_complete(self, v):
         """returns a complete graph with v verts."""
         g = Graph()
         for x in xrange(v):
             g.addVertex(x)
         for f in xrange(v):
             for t in xrange(f+1, v):
                 g.addEdge(f, t, f * v + t)
         return g

     def make_linear(self, v, bw=False):
         """returns a linear graph with v verts. if bw=True, add
         backward links."""
         g = Graph()
         for x in xrange(v):
             g.addVertex(x)
         for x,y in izip(xrange(v-1), xrange(1, v)):
             g.addEdge(x, y, x)
             if bw:
                 g.addEdge(y, x, x + v)
         return g

     def get_default_graph(self):
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
         return g
     
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
         g = self.get_default_graph()
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
         sourceResult = [None for i in g.sources() if g.inDegree(i) == 0]
         if len(sinkResult) <> len(g.sinks()):
             assert False
         if len(sourceResult) <> len(g.sources()):
             assert False

     def testRemoveVertices(self):
         g = self.make_linear(5)
         g.deleteVertex(1)
         g.deleteVertex(2)
         
     def testDFS(self):
         """Test DFS on graph."""
         g = self.get_default_graph()
         g.dfs()

     def testTopologicalSort(self):
         """Test toposort on graph."""
         g = self.get_default_graph()
         g.vertices_topological_sort()

     def testLimitedDFS(self):
         """Test DFS on graph using a limited set of starting vertices."""
         g = self.get_default_graph()
         g.dfs(vertex_set=[1])
         g.dfs(vertex_set=[1,3])
         g.dfs(vertex_set=[1,2])

     def testLimitedTopologicalSort(self):
         """Test toposort on graph using a limited set of starting vertices."""
         g = self.get_default_graph()
         g.vertices_topological_sort(vertex_set=[1])
         g.vertices_topological_sort(vertex_set=[1,3])
         g.vertices_topological_sort(vertex_set=[1,2])

     def testPrintEmptyGraph(self):
         """Test print on empty graph"""
         g = Graph()
         g.__str__()

     def testDelete(self):
         """Tests consistency of data structure after deletion."""
         g = Graph()
         g.addVertex(0)
         g.addVertex(1)
         g.addVertex(2)
         g.addEdge(0, 1, 0)
         g.addEdge(1, 2, 1)
         g.deleteVertex(2)
         self.assertEquals(g.adjacencyList[1], [])

     def testRaisingDFS(self):
         """Tests if DFS with cycle-checking will raise exceptions."""
         g = Graph()
         g.addVertex(0)
         g.addVertex(1)
         g.addVertex(2)
         g.addEdge(0, 1)
         g.addEdge(1, 2)
         g.addEdge(2, 0)
         try:
             g.dfs(raise_if_cyclic=True)
         except Graph.GraphContainsCycles, e:
             pass
         else:
             raise Exception("Should have thrown")

     def testCallInverse(self):
         """Test if calling inverse methods work."""
         g = Graph()
         g.addVertex(0)
         g.addVertex(1)
         g.addVertex(2)
         g.addEdge(0, 1)
         g.addEdge(1, 2)
         g.addEdge(2, 0)
         g2 = g.inverse()
         g3 = g.inverse_immutable()
     
     def test_subgraph(self):
         """Test subgraph routines."""
         g = self.make_complete(5)
         sub = g.subgraph([0,1])
         assert sub.vertices.has_key(0)
         assert sub.vertices.has_key(1)
         assert (1,1) in sub.adjacencyList[0]
         assert (0,1) in sub.inverseAdjacencyList[1]

         g = self.make_linear(3)
         sub = g.subgraph([0, 2])
         assert sub.vertices.has_key(0)
         assert sub.vertices.has_key(2)
         assert sub.adjacencyList[0] == []
         assert sub.adjacencyList[2] == []
         
     def test_connections_to_subgraph(self):
         """Test connections_to_subgraph."""
         g = self.make_linear(5)
         sub = g.subgraph([3])
         assert len(g.connections_to_subgraph(sub)) == 1
         g = self.make_linear(5, True)
         sub = g.subgraph([3])
         assert len(g.connections_to_subgraph(sub)) == 2

     def test_connections_from_subgraph(self):
         """Test connections_from_subgraph."""
         g = self.make_linear(5)
         sub = g.subgraph([3])
         assert len(g.connections_from_subgraph(sub)) == 1
         g = self.make_linear(5, True)
         sub = g.subgraph([3])
         assert len(g.connections_from_subgraph(sub)) == 2

     def test_topologically_contractible(self):
         """Test topologically_contractible."""
         g = self.make_linear(5)
         sub = g.subgraph([1, 2])
         assert g.topologically_contractible(sub)
         sub = g.subgraph([1, 3])
         assert not g.topologically_contractible(sub)

         g = Graph()
         g.addVertex(0)
         g.addVertex(1)
         g.addVertex(2)
         g.addVertex(3)
         g.addEdge(0, 1)
         g.addEdge(2, 3)
         for i in xrange(1, 16):
             s = []
             for j in xrange(4):
                 if i & (1 << j): s.append(j)
             assert g.topologically_contractible(g.subgraph(s))

     def test_iter_vertices(self):
         g = self.get_default_graph()
         l = list(g.iter_vertices())
         l.sort()
         assert l == [0,1,2,3,4]

     def test_iter_edges(self):
         g = self.get_default_graph()
         l = [v for v in g.iter_all_edges()]
         l.sort()
         assert l == [(0,1,0), (0,3,2), (1, 2, 1), (2, 4, 4), (3, 2, 3)]

     def test_dfs_before(self):
         g = self.make_linear(10)
         inc = []
         dec = []
         def before(id): inc.append(id)
         def after(id): dec.append(id)
         g.dfs(enter_vertex=before,
               leave_vertex=after)
         assert inc == list(reversed(dec))
         assert all(izip(inc[:-1], inc[1:]),
                    lambda (a, b): a < b)
         assert all(izip(dec[:-1], dec[1:]),
                    lambda (a, b): a > b)

if __name__ == '__main__':
    unittest.main()
