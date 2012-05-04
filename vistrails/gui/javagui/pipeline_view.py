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

from java.lang import Runnable
from javax.swing import SwingUtilities, TransferHandler
from java.awt import Color, Polygon, Font, FontMetrics, Point
from java.awt.geom import Rectangle2D
from java.io import IOException
from java.awt.datatransfer import UnsupportedFlavorException

from edu.umd.cs.piccolo import PCanvas, PNode, PLayer
from edu.umd.cs.piccolo.event import PBasicInputEventHandler

from module_palette import moduleData


PORT_WIDTH = 5
PORT_HEIGHT = 5

SPACING_X = 5
SPACING_Y = 5


# FontMetrics is declared abstract even though it has no abstract method
class FontMetricsImpl(FontMetrics):
    pass


# We have to pass something implementing Runnable to invokeLater()
# This class is used to wrap a Python method as a Runnable
class CustomRunner(Runnable):
    def __init__(self, func):
        self.runner = func;

    def run(self):
        self.runner()


class ModuleDraggingEventHandler(PBasicInputEventHandler):
    # @Override
    def mousePressed(self, event):
        event.setHandled(True)

    # @Override
    def mouseDragged(self, event):
        node = event.getPickedNode()
        delta = event.getDeltaRelativeTo(node)
        node.dragBy(delta.width, delta.height)
        event.setHandled(True)

    # @Override
    def mouseReleased(self, event):
        event.setHandled(True)


class PModule(PNode):
    """A module to be shown in the pipeline view.

    This class represent a module. Instances of this class are created from the
    Module's contained in the Controller and are added to a PCanvas to be
    displayed through Piccolo.
    """
    # We use this to measure text in the constructor
    font = Font("Dialog", Font.BOLD, 14)
    fontMetrics = FontMetricsImpl(font)

    def __init__(self, module):
        PNode.__init__(self)

        self.name = module.name

        # These are the position of the center of the text, in the global
        # coordinate system
        self.center_x = module.location.x
        self.center_y = -module.location.y
        self.translate(self.center_x, self.center_y)

        # Compute the size of the module from the text
        self.fontRect = PModule.fontMetrics.getStringBounds(self.name, None)
        w = self.fontRect.getWidth() + 2 * SPACING_X
        h = self.fontRect.getHeight() + 2 * SPACING_Y

        # These are the position of the upper-left corner of the
        # rectangle, in this object's coordinate system
        self.mod_x = int(-w/2)
        self.mod_y = int(-h/2)

        self.inputPorts = module.destinationPorts()
        self.outputPorts = module.sourcePorts()

        # Filter out 'self' ports
        # FIXME : Should we do this?
        self.inputPorts = filter(lambda p: p.name != 'self', self.inputPorts)
        self.outputPorts = filter(lambda p: p.name != 'self', self.outputPorts)

        # Update the module size with the ports
        if self.inputPorts:
            h += SPACING_Y + PORT_HEIGHT
            self.mod_y -= SPACING_Y + PORT_HEIGHT
            n = len(self.inputPorts) + 1
            w = max(w, n*(SPACING_X+PORT_WIDTH) + SPACING_X)
        if self.outputPorts:
            h += SPACING_Y + PORT_HEIGHT
            n = len(self.inputPorts)
            w = max(w, n*(SPACING_X+PORT_WIDTH) + SPACING_X)

        self.module_width = int(w)
        self.module_height = int(h)

        self.setBounds(self.mod_x, self.mod_y,
                       self.module_width, self.module_height)

        self.inputConnections = set()
        self.outputConnections = set()

    # @Override
    def paint(self, paintContext):
        graphics = paintContext.getGraphics()

        # Draw the rectangle
        graphics.setColor(self.color)
        graphics.fillRect(self.mod_x, self.mod_y,
                          self.module_width, self.module_height)

        # Draw the caption
        graphics.setColor(Color.black)
        graphics.drawString(
                self.name,
                int(-self.fontRect.getWidth()/2),
                int(-self.fontRect.getY() - self.fontRect.getHeight()/2))

        # Draw the ports
        p_x = int(self.mod_x + SPACING_X)
        p_y = int(self.mod_y + SPACING_Y)
        for port in self.inputPorts:
            graphics.fillRect(
                p_x, p_y,
                PORT_WIDTH, PORT_HEIGHT)
            p_x += PORT_WIDTH + SPACING_X
        p_x = int(self.mod_x + self.module_width - SPACING_X - PORT_WIDTH)
        p_y = int(self.mod_y + self.module_height - SPACING_Y - PORT_HEIGHT)
        for port in self.outputPorts:
            graphics.fillRect(
                p_x, p_y,
                PORT_WIDTH, PORT_HEIGHT)
            p_x -= PORT_WIDTH + SPACING_X

        # Draw a triangle in the top-right corner of the module
        p_x = int(self.mod_x + self.module_width - SPACING_X - PORT_WIDTH)
        p_y = int(self.mod_y + SPACING_Y)
        shape = Polygon(
                [p_x, p_x + PORT_WIDTH, p_x],
                [p_y, p_y + PORT_HEIGHT/2, p_y + PORT_HEIGHT],
                3)
        graphics.fill(shape)

    def inputport_position(self, iport):
        """Returns the position of one of this module's input port, in the
        global coordinate system.
        """
        if isinstance(iport, str):
            iport = self.inputport_number(iport)
        return (self.center_x + self.mod_x + (iport+1) * (SPACING_X + PORT_WIDTH) - PORT_WIDTH/2,
                self.center_y + self.mod_y + SPACING_Y + PORT_HEIGHT/2)

    def outputport_position(self, oport):
        """Returns the position of one of this module's output port, in the
        global coordinate system.
        """
        if isinstance(oport, str):
            oport = self.outputport_number(oport)
        return (self.center_x + self.mod_x + self.module_width - (oport+1) * (SPACING_X + PORT_WIDTH) + PORT_WIDTH/2,
                self.center_y + self.mod_y + self.module_height - SPACING_Y - PORT_HEIGHT/2)

    def inputport_number(self, iport):
            return [p.name for p in self.inputPorts].index(iport)

    def outputport_number(self, oport):
            return [p.name for p in self.outputPorts].index(oport)

    def dragBy(self, dx, dy):
        self.center_x += dx
        self.center_y += dy
        self.translate(dx, dy)

        for conn in self.inputConnections:
            conn.endpointChanged()
        for conn in self.outputConnections:
            conn.endpointChanged()


class PConnection(PNode):
    def __init__(self, source, oport, destination, iport):
        PNode.__init__(self)

        if isinstance(oport, str):
            oport = source.outputport_number(oport)
        if isinstance(iport, str):
            iport = destination.inputport_number(iport)

        self.source = source
        self.oport = oport
        self.destination = destination
        self.iport = iport

        self.computeBounds()

        source.outputConnections.add(self)
        destination.inputConnections.add(self)

    # @Override
    def paint(self, paintContext):
        graphics = paintContext.getGraphics()

        sx, sy = self.source.outputport_position(self.oport)
        dx, dy = self.destination.inputport_position(self.iport)

        graphics.setColor(Color.black)
        graphics.drawLine(int(sx), int(sy), int(dx), int(dy))

    def computeBounds(self):
        sx, sy = self.source.outputport_position(self.oport)
        dx, dy = self.destination.inputport_position(self.iport)
        b = Rectangle2D.Double(int(sx), int(sy), 1, 1)
        b.add(Point(int(dx), int(dy)))
        self.setBounds(self.globalToLocal(b))

    def endpointChanged(self):
        self.computeBounds()
        self.invalidatePaint()


class TargetTransferHandler(TransferHandler):
    def __init__(self, pipelineview):
        TransferHandler.__init__(self)
        self.view = pipelineview

    # @Override
    def canImport(self, *args):
        if len(args) == 1:
            # canImport(TransferSupport support)
            support = args[0]
            if not support.isDrop():
                return False
            if not support.isDataFlavorSupported(moduleData):
                return False
            if (support.getSourceDropActions() & TransferHandler.COPY) == TransferHandler.COPY:
                support.setDropAction(TransferHandler.COPY)
                return True
            return False
        else:
            # canImport(JComponent comp, DataFlavor[] transferFlavors)
            return TransferHandler.canImport(self, args[0], args[1])

    # @Override
    def importData(self, *args):
        if len(args) == 1:
            # importData(TransferSupport support)
            support = args[0]
            if not self.canImport(support):
                return False

            loc = support.getDropLocation().getDropPoint()

            try:
                module = support.getTransferable().getTransferData(moduleData)
            except UnsupportedFlavorException:
                return False
            except IOException:
                return False

            self.view.droppedModule(module, loc)

            return True
        else:
            # importData(JComponent comp, Transferable t)
            return TransferHandler.importData(self, args[0], args[1])


class JPipelineView(PCanvas):
    """The pipeline view."""
    def __init__(self, vistrail, locator, controller,
            abstraction_files=None, thumbnail_files=None):
        PCanvas.__init__(self)
        self.controller = controller
        self.executed = {} # List of executed modules, useful for coloring
        self.vistrail = vistrail
        self.locator = locator

        # Setup the layers
        module_layer = self.getLayer()
        # We override fullPick() for edge_layer to ensure that nodes are picked
        # first
        class CustomPickingLayer(PLayer):
            # @Override
            def fullPick(self, pickPath):
                return (module_layer.fullPick(pickPath) or
                        PLayer.fullPick(self, pickPath))
        edge_layer = CustomPickingLayer()
        self.getCamera().addLayer(edge_layer)

        module_layer.addInputEventListener(ModuleDraggingEventHandler())

        # Create the scene
        self.setupScene(self.controller.current_pipeline)

        # Compute modules colors
        self.define_modules_color()

        # Setup dropping of modules from the palette
        self.setTransferHandler(TargetTransferHandler(self))

    def execute_workflow(self):
        (results, changed) = self.controller.execute_current_workflow()
        print results[0].__str__()
        self.executed = results[0].executed
        self.define_modules_color()
        SwingUtilities.invokeLater(CustomRunner(self.invalidate))
        SwingUtilities.invokeLater(CustomRunner(self.revalidate))
        SwingUtilities.invokeLater(CustomRunner(self.repaint))

    def define_modules_color(self):
        self.colorModules = {}
        if self.executed == {}:
            for module in self.controller.current_pipeline._get_modules():
                self.modules[module].color = Color.gray
        else:
            for module in self.controller.current_pipeline._get_modules():
                if module in self.executed:
                    if self.executed[module] == True:
                        self.modules[module].color = Color.green
                    else:
                        self.modules[module].color = Color.red
                else:
                    self.modules[module].color = Color.orange

    def setupScene(self, pipeline):
        self.modules = {}

        module_layer = self.getCamera().getLayer(0)
        edge_layer = self.getCamera().getLayer(1)

        # Draw the pipeline using their stored position
        for id, module in pipeline.modules.iteritems():
            pmod = PModule(module)
            self.modules[id] = pmod
            module_layer.addChild(pmod)

        # Draw the edges
        for id, connection in pipeline.connections.iteritems():
            edge_layer.addChild(PConnection(
                    self.modules[connection.source.moduleId],
                    connection.source.name,
                    self.modules[connection.destination.moduleId],
                    connection.destination.name))

    def addModule(self, module):
        pmod = PModule(module)
        pmod.color = Color.gray
        self.modules[module.id] = pmod
        module_layer = self.getCamera().getLayer(0)
        module_layer.addChild(pmod)

    def droppedModule(self, descriptor, location):
        pos = self.getCamera().localToView(location)
        module = self.controller.create_module_from_descriptor(
                descriptor,
                pos.x, -pos.y)
        self.addModule(module)
