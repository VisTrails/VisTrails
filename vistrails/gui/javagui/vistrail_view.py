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
from core.data_structures.graph import Graph
from core.vistrails_tree_layout_lw import VistrailsTreeLayoutLW
from core.vistrail.pipeline import Pipeline
from java.awt import Color
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
    
    def set_vistrail(self, vistrail, locator, abstraction_files=None,
                          thumbnail_files=None, version=None):
        self.vistrail = vistrail
        self.locator = locator
        self.controller.set_vistrail(vistrail, locator)
        self.set_graph()
        
    def set_graph(self):

        self._current_graph_layout = VistrailsTreeLayoutLW()
        if (self.current_version == -1 or self.current_version > self.vistrail.get_latest_version()):
            self.current_version = self.vistrail.get_latest_version()
        self.controller.current_pipeline = core.db.io.get_workflow(self.vistrail,
                                                                   self.current_version)

        tersedPipelineGraph = Graph()
        for module in self.controller.current_pipeline._get_modules():
            tersedPipelineGraph.add_vertex(module, self.controller.current_pipeline.modules[module])
        
        edgeId = 0   
        for connection in self.controller.current_pipeline.connections:
            sourceId = self.controller.current_pipeline.connections[connection]._get_sourceId()
            targetId = self.controller.current_pipeline.connections[connection]._get_destinationId()
            tersedPipelineGraph.add_edge(sourceId, targetId, edgeId)
            edgeId = edgeId + 1
        self.pipelineGraph = tersedPipelineGraph    
        self._current_graph_layout.layout_from(self.vistrail,
                                               self.pipelineGraph)
        
    def paintComponent(self, graphics):
        font = Font("FontDialog", Font.PLAIN, 12)
        fontRenderContext = graphics.getFontRenderContext()

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
                if jLabel.getText() != "ERROR NULNODE":
                    graphics.drawRect(xNode, yNode,
                                  int(fontRect.getWidth()), int(fontRect.getHeight()))
                    graphics.drawString(jLabel.getText(), xNode,
                                    yNode + int(fontRect.getHeight()))
                #storing the dimension of the nodes to easily draw edges
                dim = {}
                dim["x"] = xNode
                dim["y"] = yNode
                dim["height"] = int(fontRect.getHeight())
                dim["width"] = int(fontRect.getWidth())
                nodesToDim[node[1].id] = dim
            #drawing edges    
            for connection in self.controller.current_pipeline.connections:
                sourceId = self.controller.current_pipeline.connections[connection]._get_sourceId()
                targetId = self.controller.current_pipeline.connections[connection]._get_destinationId()
                xSource = nodesToDim[sourceId]["x"]
                ySource = nodesToDim[sourceId]["y"]
                xTarget = nodesToDim[targetId]["x"]
                yTarget = nodesToDim[targetId]["y"]
                sourceWidth = nodesToDim[sourceId]["width"]
                sourceHeight = nodesToDim[sourceId]["width"]
                targetWidth = nodesToDim[targetId]["width"]
                targetHeight = nodesToDim[targetId]["width"]
                graphics.drawLine(xSource + sourceWidth/2 ,
                  ySource,
                  xTarget +  targetWidth/2,
                  yTarget)



                           
