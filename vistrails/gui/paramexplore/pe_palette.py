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

from PyQt4 import QtGui, QtCore

from gui.paramexplore.virtual_cell import QVirtualCellWindow
from gui.paramexplore.pe_pipeline import QAnnotatedPipelineView
from gui.vistrails_palette import QVistrailsPaletteInterface
from gui.theme import CurrentTheme

class QParamExplorePalette(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.set_title("Explore Properties")

        layout = QtGui.QVBoxLayout()
        self.pipeline_view = QAnnotatedPipelineView()
        p_view_group = QtGui.QGroupBox(self.pipeline_view.windowTitle())
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.pipeline_view)
        p_view_group.setLayout(g_layout)
        layout.addWidget(p_view_group)
        self.virtual_cell = QVirtualCellWindow()
        v_cell_group = QtGui.QGroupBox(self.virtual_cell.windowTitle())
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.virtual_cell)
        v_cell_group.setLayout(g_layout)
        layout.addWidget(v_cell_group)
        self.setLayout(layout)
        self.addButtonsToToolbar()

    def addButtonsToToolbar(self):
        # Add the open version action
        self.savePEAction = QtGui.QAction(
            CurrentTheme.SAVE_VISTRAIL_ICON,
            'Save Parameter Exploration', None, triggered=self.savePE)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.savePEAction)
        self.toolWindow().toolbar.setToolButtonStyle(
                                           QtCore.Qt.ToolButtonTextBesideIcon)

    def set_controller(self, controller):
        self.controller = controller
        self.set_pipeline(self.controller.current_pipeline)
        self.pipeline_view.setScene(self.controller.current_pipeline_view)

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
        self.pipeline_view.updateAnnotatedIds(pipeline)
        self.virtual_cell.updateVirtualCell(pipeline)

    def savePE(self):
        pe = self.controller.current_parameter_exploration
        if not pe:
            return
        text, ok = QtGui.QInputDialog.getText(self, 'Enter Name',
                 'Enter the name of this Parameter Exploration', text=pe.name)
        if ok and text:
            old_pe = self.controller.vistrail.get_named_paramexp(str(text))
            if old_pe and pe != old_pe:
                # ask to delete old one
                reply = QtGui.QMessageBox.question(self, 'Name already exist',
                 "Replace old Parameter Exploration?", QtGui.QMessageBox.Yes |
                                   QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.No:
                    return
            if old_pe and pe == old_pe:
                # they are the same so ignore
                return
            pe = pe.do_copy()
            pe.name = str(text)
            self.controller.vistrail.set_paramexp(pe)
            self.controller.set_changed(True)
