###############################################################################
##
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
""" 
Interface Vistrails - TreeLayoutLW to align version trees

"""

from core.tree_layout_lw import TreeLW, NodeLW, TreeLayoutLW
from core.data_structures.point import Point

################################################################################

class NodeVistrailsTreeLayoutLW(object):
    """
    Preserving the interface that version_view 
    expects with the DotNode.
    
    """
    def __init__(self):
        """ DotNode() -> DotNode
        Initialize DotNode as a data structure holding geometry info
        
        """
        self.p = Point(0,0)
        self.height = 0.0        
        self.width = 0.0
        self.id = 0

    def move(self, x, y):
        """ move(x: float, y: float) -> None

        """
        self.p.x = self.p.x + x
        self.p.y = self.p.y + y

class VistrailsTreeLayoutLW(object):
    """
    DotLayout is the graph outputed from Dotty which will be used and
    parsed by version tree view
    
    """
    def __init__(self):
        """ DotLayout() -> DotLayout()
        Initialize DotNode as a data structure holding graph structure
        
        """
        self.nodes = {}
        self.height = 0.0
        self.scale = 0.0
        self.width = 0.0

    def generateTreeLW(self, vistrail, graph):
        """ output_vistrail_graph(f: str) -> None
        Using vistrail and graph to prepare a dotty graph input
        
        """
        
        # create list of nodes
        X = set()

        # include the root manually
        nodes = [(0,"")]
        X.add(0)

        # include the tagged nodes
        for id, tag_name in vistrail.get_tagMap().iteritems():
            if id in graph.vertices:
                nodes.append((id, tag_name))
                X.add(id)

        # mount list of edges (parent, child).
        # preserving the order given by
        # "graph.edges_from()".
        edges = []
        for id in graph.vertices:
            froom = graph.edges_from(id)
            for (first,second) in froom:
                # print "arc %d -> %d" % (id, first)                
                edges.append((id,first))
                if id not in X:
#                    nodes.append((id," "))
                    nodes.append((id, vistrail.get_description(id)))
                    X.add(id)
                if first not in X:
#                    nodes.append((first," "))
                    nodes.append((first, vistrail.get_description(first)))
                    X.add(first)

        # get widths and heights for the nodes
        from gui.theme import CurrentTheme
        fontMetrics = CurrentTheme.VERSION_FONT_METRIC
        text_horizontal_margin = CurrentTheme.VERSION_LABEL_MARGIN[0]
        text_vertical_margin = CurrentTheme.VERSION_LABEL_MARGIN[1]
        empty_width = text_horizontal_margin + fontMetrics.width(" "*5)
        
        # default height for all nodes
        height = fontMetrics.height() + text_vertical_margin

        # create an empty tree
        tree = TreeLW()

        # create map from id to tree node
        mapTreeNodes = {}

        # add the remaining nodes
        for id, tag in nodes:
            width = text_horizontal_margin + fontMetrics.width(tag)
            width = max(width, empty_width)
            # print "add node to the tree %d %s" % (id, tag)
            mapTreeNodes[id] = tree.addNode(None,width,height,(id,tag))

        # preserve the order of the edges
        # to add the childs to their parents
        for (parentId, childId) in edges:
            # print "add arc into tree %d -> %d" % (parentId, childId)
            parent = mapTreeNodes[parentId]
            child = mapTreeNodes[childId]
#             if child.parent != None:
#                 print "child already has a parent!!! %d -> %d" % (parentId, childId)
#                 raise Exception()
            tree.changeParentOfNodeWithNoParent(parent, child)

        # return the tree
        return tree

    def layout_from(self, vistrail, graph):
        """ layout_from(vistrail: VisTrail, graph: Graph) -> None
        Take a graph from VisTrail version and use Dotty to lay it out
        
        """

        tree = self.generateTreeLW(vistrail, graph)

        min_horizontal_separation = 20
        min_vertical_separation = 50

        layout = TreeLayoutLW(tree,TreeLayoutLW.TOP,min_horizontal_separation,min_vertical_separation)

        # prepare the result
        self.nodes = {}
        for v in tree.nodes:
            id, tag = v.object
            newNode = NodeVistrailsTreeLayoutLW()
            newNode.p = Point(v.x, v.y)
            newNode.width = v.width
            newNode.height = v.height
            newNode.id = id
            # newNode.label = tag 
            self.nodes[id] = newNode

        # keep track of the bounding box 
        # of the whole tree
        (minx, miny, width, height) = tree.boundingBox()
        self.scale = 0.0
        self.width = width
        self.height = height

    def move_node(self, id, x, y):
        """ move_node(id: int, x: float, y: float) -> None

        """
        self.nodes[id].move(x,y)

    def add_node(self, id, node):
        """ add_node(id: int, node: NodeVistrailsTreeLayoutLW) -> None
        
        """
        self.nodes[id] = node
