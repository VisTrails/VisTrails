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
""" This file is used for VisTrails to interact with Graphviz Dotty to
use its graph for version tree layout"""

from core.data_structures.point import Point
import core.system
import os
import tokenize
import time

################################################################################

class DotNode(object):
    """
    DotNode holding a node in the Dotty output graph
    
    """
    def __init__(self):
        """ DotNode() -> DotNode
        Initialize DotNode as a data structure holding geometry info
        
        """
        self.p = Point(0,0)
        self.height = 0.0        
        self.width = 0.0
        self.id = 0

class DotLayout(object):
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

    def parseDottyOutput(self, file, scale=120.0):
        """ parseDottyOutput(file: str, scale: float) -> None
        Parse dotty output file into this DotLayout object
        
        """
        src = tokenize.generate_tokens(file.readline)
        token = src.next()
        while token[0] is not tokenize.ENDMARKER:
            if token[0] is tokenize.NAME:
                # read the first line, which is something like
                # graph scale width height
                if token[1] == 'graph':
                    token = src.next()
                    self.scale = float(token[1])
                    token = src.next()
                    self.width = float(token[1])
                    token = src.next()
                    self.height = float(token[1]) 
                elif token[1] == 'node':
                    n = DotNode()
                    token = src.next()
                    n.id = int(token[1])
                    token = src.next()
                    x = float(token[1])*scale
                    token = src.next()
                    y = float(token[1])*scale*2.0
                    n.p = Point(x,y)
                    token = src.next()
                    n.width = float(token[1])*scale
                    token = src.next()
                    n.height = float(token[1])*scale
                    self.nodes[n.id] = n
                elif token[1] == 'stop':
                    break
            token = src.next()

    def outputVistrailGraph(self, f, vistrail, graph ):
        """ outputVistrailGraph(f: str) -> None
        Using vistrail and graph to prepare a dotty graph input
        
        """
        for v,t in vistrail.inverseTagMap.items():
            if v in graph.vertices.keys():
                f.write('  %s [label="%s"];\n' % (v, t))

        f.write('  0;\n')
        self.maxId = 0
        self.minid = 0
        for id in graph.vertices.keys():
            froom = graph.edges_from(id)
            for (first,second) in froom:
                f.write('%s -> %s;\n' % (id, first))

    def layoutFrom(self, vistrail, graph):
        """ layoutFrom(vistrail: VisTrail, graph: Graph) -> None
        Take a graph from VisTrail version and use Dotty to lay it out
        
        """
        # Create VisTrail graph input
        tmpGraphFile = file(core.system.temporaryDirectory() +
                            'dot_tmp_vistrails.txt', 'w')
        tmpGraphFile.write('digraph G {\n')
        self.outputVistrailGraph(tmpGraphFile, vistrail, graph)
        tmpGraphFile.write('}\n')
        tmpGraphFile.close()

        # Run Dotty
        tempDir = core.system.temporaryDirectory()
        cmdline = (core.system.graphVizDotCommandLine() +
                   tempDir + 'dot_output_vistrails.txt ' +
                   tempDir + 'dot_tmp_vistrails.txt')
        os.system(cmdline)

        dtty_file = tempDir + 'dot_output_vistrails.txt'

        if not os.path.exists(dtty_file) :
            print ""
            print "Could not find %s" % dtty_file
            print "Is GraphViz installed and is dotty in your PATH?"
            print ""
            
        fileIn = open(dtty_file)

        # Parse Dotty's output
        self.parseDottyOutput(fileIn)
        core.system.removeGraphvizTemporaries()
