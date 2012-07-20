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

from extras.vistrails_tree_layout_lw import VistrailsTreeLayoutLW
import core.db.io

from javax.swing import JPanel
from java.awt.event import MouseListener
from java.awt import Color, Font

from com.vlsolutions.swing.docking import Dockable, DockKey
from utils import FontMetricsImpl


class FontMetrics(object):
    def __init__(self, metrics):
        self._metrics = metrics
        self._height = metrics.getHeight()

    def width(self, string):
        return self._metrics.getStringBounds(string, None).getWidth()

    def height(self):
        return self._height


class VersionNode(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class JVersionView(JPanel, MouseListener, Dockable):

    MARGIN_X = 60
    MARGIN_Y = 35

    HORIZONTAL_POSITION = 300
    VERTICAL_POSITION = 20

    def __init__(self, vistrail, locator, controller, builder_frame,
            abstraction_files=None, thumbnail_files=None,
            version=None):
        self._key = DockKey('version_view')
        self._key.setResizeWeight(1.0)

        self.FONT = Font("Dialog", Font.PLAIN, 15)
        self.FONT_METRICS = FontMetrics(FontMetricsImpl(self.FONT))

        self.full_tree = True
        self.refine = False
        self.controller = controller
        self.builder_frame = builder_frame
        self.idScope = self.controller.id_scope
        self.setBackground(Color.GREEN)
        self.addMouseListener(self)

        self.vistrail = vistrail
        self.locator = locator
        self.set_graph()

    def set_graph(self):
        self.controller.recompute_terse_graph()

        self._current_terse_graph = self.controller._current_terse_graph
        self._current_full_graph = self.controller._current_full_graph
        self._current_graph_layout = VistrailsTreeLayoutLW()
        self._current_graph_layout.layout_from(
                self.vistrail, self._current_terse_graph,
                self.FONT_METRICS,
                self.MARGIN_X,
                self.MARGIN_Y)

        self.controller.current_pipeline = core.db.io.get_workflow(self.vistrail, self.controller.current_version)

    # @Override
    def paintComponent(self, graphics):
        fontRenderContext = graphics.getFontRenderContext()
        graphics.setFont(self.FONT)

        graphics.clearRect(0, 0, self.getWidth(), self.getHeight())
        
        graphics.translate(self.HORIZONTAL_POSITION, self.VERTICAL_POSITION)

        self.nodes = dict()

        vistrail = self.controller.vistrail
        tm = vistrail.get_tagMap()

        for node in self._current_graph_layout.nodes.itervalues():
            v = node.id
            tag = tm.get(v, None)
            description = vistrail.get_description(v)

            if tag is not None:
                label = tag
            elif description is not None:
                label = description
            else:
                label = ''

            fontRect = self.FONT.getStringBounds(label, fontRenderContext)

            graphics.setColor(Color.white)
            w = int(fontRect.getWidth()) + self.MARGIN_X
            h = int(fontRect.getHeight()) + self.MARGIN_Y
            oval = (int(node.p.x) - w/2, int(node.p.y) - h/2,
                    w, h)
            graphics.fillOval(*oval)
            if v == self.controller.current_version:
                graphics.setColor(Color.red)
            else:
                graphics.setColor(Color.black)
            graphics.drawOval(*oval)
            graphics.drawString(
                    label,
                    int(node.p.x - fontRect.getWidth()/2),
                    int(node.p.y -
                            fontRect.getY() - fontRect.getHeight()/2))

            self.nodes[node.id] = VersionNode(
                    int(node.p.x) + self.HORIZONTAL_POSITION,
                    int(node.p.y) + self.VERTICAL_POSITION,
                    w, h)

        # Draw the edges
        graphics.setColor(Color.black)
        alreadyVisitedNode = set()
        for node1 in self._current_graph_layout.nodes.itervalues():
            v1 = node1.id
            for node2 in self._current_graph_layout.nodes.itervalues():
                v2 = node2.id
                if node2 in alreadyVisitedNode:
                    pass
                else:
                    if self._current_terse_graph.has_edge(v1, v2) or self._current_terse_graph.has_edge(v2, v1):
                        # Detecting the top node1 in order to correctly draw edges
                        if node1.p.y < node2.p.y:
                            topNode = node1
                            bottomNode = node2
                        else:
                            topNode = node2
                            bottomNode = node1
                        graphics.drawLine(
                                int(topNode.p.x),
                                int(topNode.p.y) +
                                    self.nodes[topNode.id].height/2,
                                int(bottomNode.p.x),
                                int(bottomNode.p.y) -
                                    self.nodes[bottomNode.id].height/2)
            alreadyVisitedNode.add(v1)

    # @Override
    def mouseClicked(self, event):
        eventX = event.getX()
        eventY = event.getY()
        isClickInsideNode = False
        for nodeID, node in self.nodes.iteritems():
            x = float(eventX - node.x)*2/node.width
            y = float(eventY - node.y)*2/node.height
            if x*x + y*y <= 1.0:
                # TODO : this doesn't actually do anything
                self.builder_frame.currentVersion = nodeID
                self.builder_frame.clickedVersionNodeId = nodeID
                isClickInsideNode = True
                break

        if isClickInsideNode == False:
            self.builder_frame.clickedVersionNodeId = -1

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
