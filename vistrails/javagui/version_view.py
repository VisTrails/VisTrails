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

from gui.vistrails_tree_layout_lw import VistrailsTreeLayoutLW
import core.db.io

from javax.swing import JPanel
from java.awt.event import MouseListener
from java.awt import Rectangle, Color

from com.vlsolutions.swing.docking import Dockable, DockKey

class JVersionVistrailView(JPanel, MouseListener, Dockable):

    def __init__(self, vistrail, locator, controller,
            abstraction_files=None, thumbnail_files=None,
            version=None):
        self._key = DockKey('version_view')
        self._key.setResizeWeight(1.0)

        self.full_tree = True
        self.refine = False
        self.controller = controller
        self.idScope = self.controller.id_scope
        self.setBackground(Color.GREEN)
        self.addMouseListener(self)

        self.vistrail = vistrail
        self.locator = locator
        self.set_graph()

    def set_graph(self):
        return

        self.controller.recompute_terse_graph()

        self._current_terse_graph = self.controller._current_terse_graph
        self._current_full_graph = self.controller._current_full_graph
        self._current_graph_layout = VistrailsTreeLayoutLW()
        self._current_graph_layout.layout_from(
                self.vistrail, self._current_terse_graph)

        self.controller.current_pipeline = core.db.io.get_workflow(self.vistrail, self.controller.current_version)

    def paintComponent(self, graphics):
        return

        if graphics is not None:
            font = graphics.getFont()
            fontRenderContext = graphics.getFontRenderContext()
            self.nodesToDim = {}

            graphics.translate(20, 20)

            # Draw the nodes
            maxWidth = 0
            maxHeight = 0

            for _, node in self._current_graph_layout.nodes.iteritems():
                label = self.vistrail.get_description(node.id) or str(node.id)
                if label is None or label == "":
                    label = "TREE ROOT"

                fontRect = font.getStringBounds(label, fontRenderContext)

                graphics.setColor(Color.white)
                graphics.fillRect(int(node.p.x), int(node.p.y),
                                  int(fontRect.getWidth()), int(fontRect.getHeight()))
                graphics.setColor(Color.black)
                graphics.drawString(label, int(node.p.x),
                    int(node.p.y) + int(fontRect.getHeight()))

                if maxWidth < int(fontRect.getWidth()):
                    maxWidth = int(fontRect.getWidth())
                if maxHeight < int(fontRect.getHeight()):
                    maxHeight = int(fontRect.getHeight())
                dim = {}
                dim["x"] = int(node.p.x)
                dim["y"] = int(node.p.y)
                dim["height"] = int(fontRect.getHeight())
                dim["width"] = int(fontRect.getWidth())
                self.nodesToDim[node.id] = dim

            # Draw the edges
            alreadyVisitedNode = set()
            for _, node in self._current_graph_layout.nodes.iteritems():
                nodeId = node.id
                for _, nodeBis in self._current_graph_layout.nodes.iteritems():
                    nodeBisId = nodeBis.id
                    if nodeBis in alreadyVisitedNode:
                        pass
                    else:
                        if self._current_terse_graph.has_edge(nodeId, nodeBisId) or self._current_terse_graph.has_edge(nodeBisId, nodeId):
                            graphics.setColor(Color.black)
                            # Detecting the top node in order to correctly draw edges
                            if node.p.y < nodeBis.p.y:
                                topNode = node
                                bottomNode = nodeBis
                            else:
                                topNode = nodeBis
                                bottomNode = node
                            graphics.drawLine(int(topNode.p.x) + self.nodesToDim[topNode.id]["width"]/2 ,
                                              int(topNode.p.y) + maxHeight,
                                              int(bottomNode.p.x) + self.nodesToDim[bottomNode.id]["width"]/2,
                                              int(bottomNode.p.y))
                alreadyVisitedNode.add(nodeId)

    def mouseClicked(self, event):
        return

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

    # @Override
    def getDockKey(self):
        return self._key

    # @Override
    def getComponent(self, *args):
        if len(args) == 0:
            return self
        else:
            return JPanel.getComponent(self, *args)
