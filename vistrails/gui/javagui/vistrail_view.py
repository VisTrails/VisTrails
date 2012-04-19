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
from javax.swing import SwingUtilities
from java.awt import Color
from java.awt import Polygon

import core.db.io


PORT_WIDTH = 5
PORT_HEIGHT = 5

SPACING_X = 5
SPACING_Y = 5


class JVistrailView(JPanel):
    """This panel is the main view, that draws a pipeline using Swing.
    """
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
        if (self.current_version == -1 or
                self.current_version > self.vistrail.get_latest_version()):
            self.current_version = self.vistrail.get_latest_version()

        self.controller.current_pipeline = core.db.io.get_workflow(
                self.vistrail, self.current_version)

        for module in self.controller.current_pipeline._get_modules():
            # FIXME : Replaces information panels by providing test values
            # Should be done before each execution!
            if self.controller.current_pipeline.modules[module]._get_module_descriptor().module().__str__() == "<<<class 'core.modules.vistrails_module.String'>>>":
                self.controller.current_pipeline.modules[module]._get_module_descriptor().module().setValue("testString")

    def paintComponent(self, graphics):
        # Compute modules colors
        self.define_modules_color()

        modules = self.controller.current_pipeline.modules
        connections = self.controller.current_pipeline.connections

        # Draw the pipeline using their stored position
        if graphics is not None:
            font = graphics.getFont()
            fontRenderContext = graphics.getFontRenderContext()

            module_geometries = {}

            for id, mod in modules.iteritems():
                name = mod.name
                # These are the position of the center of the text
                x = mod.location.x
                y = -mod.location.y

                fontRect = font.getStringBounds(name, fontRenderContext)
                w = fontRect.getWidth() + 2 * SPACING_X
                h = fontRect.getHeight() + 2 * SPACING_Y

                # These are the position of the upper-right corner of the
                # rectangle
                mod_x = x - w/2
                mod_y = y - h/2

                inputPorts = mod.destinationPorts()
                inputPorts = filter(lambda p: p.name != "self", inputPorts)
                outputPorts = mod.sourcePorts()
                outputPorts = filter(lambda p: p.name != "self", outputPorts)

                if inputPorts:
                    h += SPACING_Y + PORT_HEIGHT
                    mod_y -= SPACING_Y + PORT_HEIGHT
                    n = len(inputPorts) + 1
                    w = max(w, n*(SPACING_X+PORT_WIDTH) + SPACING_X)
                if outputPorts:
                    h += SPACING_Y + PORT_HEIGHT
                    n = len(inputPorts)
                    w = max(w, n*(SPACING_X+PORT_WIDTH) + SPACING_X)

                # Draw the rectangle
                graphics.setColor(self.colorModules[id])
                graphics.fillRect(int(mod_x), int(mod_y), int(w), int(h))

                # Store the geometry to be recalled when drawing connections
                module_geometries[id] = [
                        mod_x, mod_y, w, h,
                        [p.name for p in inputPorts],
                        [p.name for p in outputPorts]]

                # Draw the caption
                graphics.setColor(Color.black)
                graphics.drawString(
                        name,
                        int(x - fontRect.getWidth()/2),
                        int(y - fontRect.getY() - fontRect.getHeight()/2))

                # Draw the ports
                p_x = int(mod_x + SPACING_X)
                p_y = int(mod_y + SPACING_Y)
                for port in inputPorts:
                    graphics.fillRect(
                        p_x, p_y,
                        PORT_WIDTH, PORT_HEIGHT)
                    p_x += PORT_WIDTH + SPACING_X
                p_x = int(mod_x + w - SPACING_X - PORT_WIDTH)
                p_y = int(mod_y + h - SPACING_Y - PORT_HEIGHT)
                for port in outputPorts:
                    graphics.fillRect(
                        p_x, p_y,
                        PORT_WIDTH, PORT_HEIGHT)
                    p_x -= PORT_WIDTH + SPACING_X

                # Draw a triangle in the top-right corner of the module
                p_x = int(mod_x + w - SPACING_X - PORT_WIDTH)
                p_y = int(mod_y + SPACING_Y)
                shape = Polygon(
                        [p_x, p_x + PORT_WIDTH, p_x],
                        [p_y, p_y + PORT_HEIGHT/2, p_y + PORT_HEIGHT],
                        3)
                graphics.fill(shape)

            # Draw the edges
            for id, connection in connections.iteritems():
                source = module_geometries[connection.source.moduleId]
                # Find the source port in the source module's output ports
                iport_num = source[5].index(connection.source.name)
                sx = source[0] + source[2] - (iport_num+1) * (SPACING_X + PORT_WIDTH) + PORT_WIDTH/2
                sy = source[1] + source[3] - SPACING_Y - PORT_WIDTH/2

                destination = module_geometries[connection.destination.moduleId]
                # Find the destination port in the destination module's input
                # ports
                oport_num = destination[4].index(connection.destination.name)
                dx = destination[0] + (oport_num+1) * (SPACING_X + PORT_WIDTH) - PORT_WIDTH/2
                dy = destination[1] + SPACING_Y + PORT_WIDTH/2

                graphics.drawLine(int(sx), int(sy), int(dx), int(dy))


class CustomRunner(Runnable):
    def __init__(self, func):
        self.runner = func;

    def run(self):
        self.runner()
