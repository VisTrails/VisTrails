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

from java.lang import Runnable
from javax.swing import JPanel
from javax.swing import JLabel
from javax.swing import SwingUtilities
from java.awt import Font
from java.awt import Graphics
from java.awt import Color
from java.awt import Polygon

from core.data_structures.graph import Graph
from gui.vistrails_tree_layout_lw import VistrailsTreeLayoutLW

import core.db.io

class JVistrailView(JPanel):
    
    def __init__(self, vistrail, locator, builderFrame):
        self.full_tree = True
        self.builderFrame = builderFrame
        self.refine = False
        self.controller = JVistrailController()
        self.idScope = self.controller.id_scope
        self.current_version = self.builderFrame.currentVersion
        self.set_vistrail(vistrail, locator)
        self.executed = {} #list of executed modules
    
    def set_vistrail(self, vistrail, locator, abstraction_files=None,
                          thumbnail_files=None, version=None):
        self.vistrail = vistrail
        self.locator = locator
        self.controller.set_vistrail(vistrail, locator)
        self.set_graph()

    def execute_workflow(self):
        (results, changed) = self.controller.execute_current_workflow()
        print results[0].__str__()
        self.executed = results[0].executed
        SwingUtilities.invokeLater(CustomRunner(self.invalidate))
        SwingUtilities.invokeLater(CustomRunner(self.revalidate))
        SwingUtilities.invokeLater(CustomRunner(self.repaint))
        
    def define_modules_color(self):
        self.colorModules = {}
        if self.executed == {}:
            for module in self.controller.current_pipeline._get_modules():
                self.colorModules[module] = Color.WHITE
        else:
            for module in self.controller.current_pipeline._get_modules():
                if module in self.executed:
                    if self.executed[module] == True:
                        self.colorModules[module] = Color.GREEN
                    else:
                        self.colorModules[module] = Color.RED
                else:
                    self.colorModules[module] = Color.ORANGE
  
    def set_graph(self):

        self._current_graph_layout = VistrailsTreeLayoutLW()
        if (self.current_version == -1 or self.current_version > self.vistrail.get_latest_version()):
            self.current_version = self.vistrail.get_latest_version()
        self.controller.current_pipeline = core.db.io.get_workflow(self.vistrail,
                                                                   self.current_version)

        tersedPipelineGraph = Graph()
        for module in self.controller.current_pipeline._get_modules():
            tersedPipelineGraph.add_vertex(module, self.controller.current_pipeline.modules[module])
            #Not  nice lines, just here to force value of string module while module information panels are not implemented
            if self.controller.current_pipeline.modules[module]._get_module_descriptor().module().__str__() == "<<<class 'core.modules.vistrails_module.String'>>>":
                self.controller.current_pipeline.modules[module]._get_module_descriptor().module().setValue("testString")
        edgeId = 0   
        for connection in self.controller.current_pipeline.connections:
            sourceId = self.controller.current_pipeline.connections[connection]._get_sourceId()
            targetId = self.controller.current_pipeline.connections[connection]._get_destinationId()
            self.controller.current_pipeline.connections[connection].id = edgeId
            tersedPipelineGraph.add_edge(sourceId, targetId, edgeId)
            edgeId = edgeId + 1
        self.pipelineGraph = tersedPipelineGraph    
        self._current_graph_layout.layout_from(self.vistrail,
                                               self.pipelineGraph)
        
    def paintComponent(self, graphics):
        font = Font("FontDialog", Font.PLAIN, 14)
        fontRenderContext = graphics.getFontRenderContext()
        self.define_modules_color() #compute modules colors
        #draw the pipeline tree
        nodesToDim = {}
        if graphics is not None:
            #drawing the nodes
            for node in self._current_graph_layout.nodes.iteritems():
                #Defining name of the module and coordinates
                try:
                    jLabel = JLabel(self.controller.current_pipeline.modules[node[1].id].name)
                except:
                    print "except catch"
                    jLabel = JLabel("ERROR NULNODE")
                if jLabel is None or jLabel == "":
                    jLabel = JLabel("TREE ROOT")
                fontRect = font.getStringBounds(jLabel.getText(), fontRenderContext)
                xNode = int(node[1].p.x)
                yNode = int(node[1].p.y)
                #Checking for overlapping of nodes, if so correct it
                overlapBoolean = True
                while overlapBoolean:
                    overlapBoolean = False
                    for nodeId in nodesToDim:
                        if nodesToDim[nodeId]["x"] == xNode and nodesToDim[nodeId]["y"] == yNode:
                            xNode = xNode + 10 + nodesToDim[nodeId]["width"]
                            overlapBoolean = True
                dim = {}
                if jLabel.getText() != "ERROR NULNODE":
                    graphics.setColor(self.colorModules[node[0]])
                    graphics.fillRect(xNode, yNode,
                                  int(fontRect.getWidth()), 2*int(fontRect.getHeight()))
                    graphics.setColor(Color.black)
                    graphics.drawString(jLabel.getText(), xNode,
                                    yNode + 3 * int(fontRect.getHeight()) / 2)
                    #parameters to draw ports
                    currentPortCount = 0 #
                    offsetDestinationY = 5
                    offsetDestinationX = 15
                    portHeight = 5
                    portWidth = 5
                    #
                    destinationPorts = {}
                    sourcePorts = {}
                    dim["destinationPorts"] = destinationPorts
                    dim["sourcePorts"] = sourcePorts
                    #drawing destination ports
                    for port in self.controller.current_pipeline.modules[node[1].id].destinationPorts():
                        graphics.fillRect(xNode + offsetDestinationY + ((currentPortCount) * offsetDestinationX),
                                          yNode + offsetDestinationY, portWidth, portHeight)
                        port = {}
                        destinationPorts[currentPortCount] = port
                        port["used"] = False
                        port["x"] = xNode + offsetDestinationY + ((currentPortCount) * offsetDestinationX)
                        port["y"] = yNode + offsetDestinationY
                        currentPortCount = currentPortCount + 1
                    #drawing source ports
                    #reset the counter, it nows points to the current number of source ports
                    currentPortCount = 0
                    for port in self.controller.current_pipeline.modules[node[1].id].sourcePorts():
                        if port.name != "self":
                            graphics.fillRect(xNode + int(fontRect.getWidth()) - offsetDestinationY
                                              - ((currentPortCount) * offsetDestinationX),
                                              yNode + 2 * int(fontRect.getHeight()) - offsetDestinationY,
                                              portWidth, portHeight)
                            port = {}
                            sourcePorts[currentPortCount] = port
                            port["used"] = False
                            port["x"] = xNode + int(fontRect.getWidth()) - offsetDestinationY - ((currentPortCount) * offsetDestinationX)
                            port["y"] = yNode + 2 * int(fontRect.getHeight()) - offsetDestinationY
                            currentPortCount = currentPortCount + 1
                    #drawing the triangle on the top right corner of the module
                    shape = Polygon([xNode + int(fontRect.getWidth()) - offsetDestinationY,
                                    xNode + int(fontRect.getWidth()) - offsetDestinationY,
                                    xNode + int(fontRect.getWidth())],
                                    [yNode + offsetDestinationY, yNode + 2 * offsetDestinationY,
                                     yNode + (3 * offsetDestinationY / 2)],
                                    3)
                    graphics.fill(shape)
                #storing the dimension of the nodes to easily draw edges
                dim["x"] = xNode
                dim["y"] = yNode
                dim["height"] = 2 * int(fontRect.getHeight())
                dim["width"] = int(fontRect.getWidth())
                nodesToDim[node[1].id] = dim
            #drawing edges 
            for connection in self.controller.current_pipeline.connections:
                sourceId = self.controller.current_pipeline.connections[connection]._get_sourceId()
                targetId = self.controller.current_pipeline.connections[connection]._get_destinationId() 
                for port in nodesToDim[sourceId]["sourcePorts"]:
                    if nodesToDim[sourceId]["sourcePorts"][port]["used"] == False:
                        xSource = nodesToDim[sourceId]["sourcePorts"][port]["x"]
                        ySource = nodesToDim[sourceId]["sourcePorts"][port]["y"]
                        nodesToDim[sourceId]["sourcePorts"][port]["used"] = True
                        break
                for port in nodesToDim[targetId]["destinationPorts"]:
                    if nodesToDim[targetId]["destinationPorts"][port]["used"] == False:
                        xTarget = nodesToDim[targetId]["destinationPorts"][port]["x"]
                        yTarget = nodesToDim[targetId]["destinationPorts"][port]["y"]
                        nodesToDim[targetId]["destinationPorts"][port]["used"] = True
                        break
                sourceWidth = nodesToDim[sourceId]["width"]
                sourceHeight = nodesToDim[sourceId]["height"]
                targetWidth = nodesToDim[targetId]["width"]
                graphics.drawLine(xSource, # + sourceWidth/2 ,
                  ySource, #+ sourceHeight,
                  xTarget, # +  targetWidth/2,
                  yTarget)


class CustomRunner(Runnable):
    
    def __init__(self, func):
        self.runner = func;
        
    def run(self):
        self.runner()
                           
