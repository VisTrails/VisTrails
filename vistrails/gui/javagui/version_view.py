###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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

from vistrail_controller import JVistrailController

from javax.swing import JPanel
from javax.swing import JLabel
from java.awt import Font
from java.awt import Graphics
from java.awt.event import MouseListener
from java.awt import Rectangle
from core.data_structures.graph import Graph
from gui.vistrails_tree_layout_lw import VistrailsTreeLayoutLW
from core.vistrail.pipeline import Pipeline
from java.awt import Color
import core.db.io

class JVersionVistrailView(JPanel, MouseListener):
    
    def __init__(self, vistrail, locator, builderFrame):
        self.full_tree = True
        self.refine = False
        self.builderFrame = builderFrame
        self.controller = JVistrailController()
        self.idScope = self.controller.id_scope
        self.set_vistrail(vistrail, locator)
        self.setBackground(Color.GREEN)
        self.addMouseListener(self)

    
    def set_vistrail(self, vistrail, locator, abstraction_files=None,
                          thumbnail_files=None, version=None):
        self.vistrail = vistrail
        self.locator = locator
        self.controller.set_vistrail(vistrail, locator)
        self.set_graph()
        
    def set_graph(self):
        """ Directly copied from the Qt branch"""
        fullVersionTree = self.vistrail.tree.getVersionTree()
        # create tersed tree                                                                        
        x = [(0,None)]
        tersedVersionTree = Graph()
        # cache actionMap and tagMap because they're properties, sort of slow                       
        am = self.vistrail.actionMap
        tm = self.vistrail.get_tagMap()
        last_n = self.vistrail.getLastActions(1)
        #last_n = self.vistrail.getLastActions(self.num_versions_always_shown)
        
        while 1:
            try:
                (current,parent)=x.pop()
            except IndexError:
                break

            # mount childs list                                                                     
            if current in am and self.vistrail.is_pruned(current):
                children = []
            else:
                children = \
                    [to for (to, _) in fullVersionTree.adjacency_list[current]
                     if (to in am) and (not self.vistrail.is_pruned(to) or \
                                            to == self.current_version)]

            if (self.full_tree or
                (current == 0) or  # is root                                                        
                (current in tm) or # hasTag:                                                        
                (len(children) <> 1) or # not oneChild:                                             
                (current == self.current_version) or # isCurrentVersion                             
                (am[current].expand) or  # forced expansion                                         
                (current in last_n)): # show latest                                                 
                # yes it will!                                                                      
                # this needs to be here because if we are refining                                  
                # version view receives the graph without the non                                   
                # matching elements                                                                 
                if( (not self.refine) or
                    (self.refine and not self.search) or
                    (current == 0) or
                    (self.refine and self.search and
                     self.search.match(self.vistrail,am[current]) or
                     current == self.current_version)):
                    # add vertex...                                                                 
                    tersedVersionTree.add_vertex(current)

                    # ...and the parent                                                             
                    if parent is not None:
                        tersedVersionTree.add_edge(parent,current,0)

                    # update the parent info that will                                              
                    # be used by the childs of this node                                            
                    parentToChildren = current
                else:
                    parentToChildren = parent
            else:
                parentToChildren = parent

            for child in reversed(children):
                x.append((child, parentToChildren))

        self._current_terse_graph = tersedVersionTree
        self._current_full_graph = self.vistrail.tree.getVersionTree()
        self._current_graph_layout = VistrailsTreeLayoutLW()
        self._current_graph_layout.layout_from(self.vistrail,
                                               self._current_terse_graph)

        self.controller.current_pipeline = core.db.io.get_workflow(self.vistrail, 13)
        
    def paintComponent(self, graphics):
        font = Font("FontDialog", Font.PLAIN, 12)
        fontRenderContext = graphics.getFontRenderContext()
        self.nodesToDim = {}
        #draw nodes for version tree
        maxWidth = 0
        maxHeight = 0
        if graphics is not None:
            for node in self._current_graph_layout.nodes.iteritems():
                jLabel = JLabel(node[1].label)
                if node[1].label is None or node[1].label == "":
                    jLabel = JLabel("TREE ROOT")
                fontRect = font.getStringBounds(jLabel.getText(), fontRenderContext)
                if (self.builderFrame.clickedVersionNodeId == node[1].id):
                    graphics.setColor(Color.red)
                #Hack to restore correct color if not well set...
                if graphics.getColor() != (Color.white and Color.red) :
                    graphics.setColor(Color.white)
                graphics.fillRect(int(node[1].p.x), int(node[1].p.y),
                                  int(fontRect.getWidth()), int(fontRect.getHeight()))
                graphics.setColor(Color.black)
                graphics.drawString(jLabel.getText(), int(node[1].p.x),
                    int(node[1].p.y) + int(fontRect.getHeight()))
                graphics.setColor(Color.white)
                if maxWidth < int(fontRect.getWidth()):
                    maxWidth = int(fontRect.getWidth())
                if maxHeight < int(fontRect.getHeight()):
                    maxHeight = int(fontRect.getHeight())
                dim = {}
                dim["x"] = int(node[1].p.x)
                dim["y"] = int(node[1].p.y)
                dim["height"] = int(fontRect.getHeight())
                dim["width"] = int(fontRect.getWidth())
                self.nodesToDim[node[1].id] = dim
        #draw edges for version tree
            alreadyVisitedNode = []
            for node in self._current_graph_layout.nodes.iteritems():
                nodeId = node[1].id
                for nodeBis in self._current_graph_layout.nodes.iteritems():
                    nodeBisId = nodeBis[1].id
                    if nodeBis in alreadyVisitedNode:
                        pass
                    else:
                        if self._current_terse_graph.has_edge(nodeId, nodeBisId) or self._current_terse_graph.has_edge(nodeBisId, nodeId):
                            jLabel = JLabel(node[1].label)
                            fontRect = font.getStringBounds(jLabel.getText(), fontRenderContext)
                            previousColor = graphics.getColor()
                            graphics.setColor(Color.black)
                            #detecting the top node in order to correctly draw edges
                            if node[1].p.y < nodeBis[1].p.y:
                                topNode = node
                                bottomNode = nodeBis
                            else:
                                topNode = nodeBis
                                bottomNode = node
                            graphics.drawLine(int(topNode[1].p.x) + self.nodesToDim[topNode[1].id]["width"]/2 ,
                                              int(topNode[1].p.y) + maxHeight,
                                              int(bottomNode[1].p.x) + self.nodesToDim[bottomNode[1].id]["width"]/2,
                                              int(bottomNode[1].p.y))
                            graphics.setColor(previousColor)
                alreadyVisitedNode.append(nodeId)

    def mouseClicked(self, event):
        eventX = event.getX()
        eventY = event.getY()
        isClickInsideNode = False
        for node in self.nodesToDim:
            nodeRect = Rectangle(self.nodesToDim[node]["x"], self.nodesToDim[node]["y"],
                                          self.nodesToDim[node]["width"],
                                          self.nodesToDim[node]["height"])
            if nodeRect.contains(eventX, eventY):
                self.builderFrame.currentVersion = node
                self.builderFrame.clickedVersionNodeId = node
                isClickInsideNode = True
        if isClickInsideNode == False:
            self.builderFrame.clickedVersionNodeId = -1
        self.invalidate()
        self.revalidate()
        self.repaint()
            
