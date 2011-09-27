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
""" This contains a customized pipeline view for read-only selection

QReadOnlyPortSelectPipelineView
"""

from PyQt4 import QtCore, QtGui
from gui.pipeline_view import QGraphicsConfigureItem, QGraphicsModuleItem, \
    QGraphicsPortItem, QPipelineScene, QPipelineView
from gui.theme import CurrentTheme

class QReadOnlyPortSelectPipelineView(QPipelineView):
    def __init__(self, parent, scene, single_output=False, include_module_ids=[]):
        """ QReadOnlyPortSelectPipelineView(parent: QPipelineView,
                                            scene: QGraphicsScene,
                                            single_output: bool,
                                            include_module_ids: list)
                                            -> QReadOnlyPortSelectPipelineView
        Create a read only pipeline view that only allows selection of ports from
        the modules in include_module_ids.  If single_output is True, only one
        output port can be selected at a time.
        
        """
        QPipelineView.__init__(self, parent)
        self.single_output = single_output
        self._shown = False
        self._selected_input_ports = []
        self._selected_output_ports = []
        # Create custom scene
        scene_copy = QPipelineScene(self)
        scene_copy.controller = scene.controller
        scene_copy.setupScene(scene.pipeline)
        scene_copy.selectAll()
        if include_module_ids:
            # Remove modules not in the include list and associated connections
            sel_modules, sel_connections = scene_copy.get_selected_item_ids()
            [scene_copy.remove_module(m_id) for m_id in sel_modules if m_id not in include_module_ids]
            [scene_copy.remove_connection(c_id) for c_id in sel_connections if c_id not in scene_copy.get_selected_item_ids()[1]]
        # Hide configure button on modules
        for item in scene_copy.selectedItems():
            if type(item) == QGraphicsModuleItem:
                for c_item in item.childItems():
                    if type(c_item) == QGraphicsConfigureItem:
                        c_item.setVisible(False)
        # Unselect everything and use the newly created scene
        scene_copy.clearSelection()
        scene_copy.updateSceneBoundingRect()
        self.setScene(scene_copy)
    
    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Toggle port selection
        
        """
        buttons = self.translateButton(event)
        if buttons == QtCore.Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            item = self.scene().itemAt(scenePos)
            if type(item) == QGraphicsPortItem:
                is_input = item.port.type == 'input'
                if self.single_output and not is_input and len(self._selected_output_ports) > 0 and item != self._selected_output_ports[0]:
                    # Deselect current output port if another port selected in single output mode
                    self._selected_output_ports[0].setPen(CurrentTheme.PORT_PEN)
                    del self._selected_output_ports[:]
                if is_input:
                    port_set = self._selected_input_ports
                else:
                    port_set = self._selected_output_ports
                if item in port_set:
                    port_set.remove(item)
                else:
                    port_set.append(item)
                self._clicked_port = item
            else:
                self._clicked_port = None
            event.accept()
        else:
            QPipelineView.mousePressEvent(self, event)
            
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Update port highlighting
        
        """
        if event.button() == QtCore.Qt.LeftButton:
            port = self._clicked_port
            if port is not None:
                if port in self._selected_input_ports or port in self._selected_output_ports:
                    port.setPen(CurrentTheme.PORT_SELECTED_PEN)
                else:
                    port.setPen(CurrentTheme.PORT_PEN)
            event.accept()
        else:
            QPipelineView.mouseReleaseEvent(self, event)
        
    def mouseDoubleClickEvent(self, event):
        """ mouseDoubleClickEvent(event: QMouseEvent) -> None
        Disallow left button double clicks
        
        """
        buttons = self.translateButton(event)
        if buttons == QtCore.Qt.LeftButton:
            event.accept()
        else:
            QPipelineView.mouseDoubleClickEvent(self, event)
        
    def mouseMoveEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Disallow left click and drag
        
        """
        buttons = self.translateButton(event)
        if buttons == QtCore.Qt.LeftButton:
            event.accept()
        else:
            QPipelineView.mouseMoveEvent(self, event)
            
    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Disallow key presses
        
        """
        event.accept()
        
    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Fit pipeline to view on first paint
        
        """
        if not self._shown:
            self._shown = True
            self.scene().fitToView(self)
        QPipelineView.paintEvent(self, event)
        
    def sizeHint(self):
        """ sizeHint() -> QSize
        Set smaller pipeline view size

        """
        return QtCore.QSize(512, 512)
    
    def getSelectedInputPorts(self):
        """ getSelectedInputPorts() -> list
        Get list of selected input port (QGraphicsPortItem) objects
        
        """
        return self._selected_input_ports
    
    def getSelectedOutputPorts(self):
        """ getSelectedOutputPorts() -> list
        Get list of selected output port (QGraphicsPortItem) objects
        
        """
        return self._selected_output_ports


