############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

from PyQt4 import QtGui, QtCore

from gui.paramexplore.virtual_cell import QVirtualCellWindow
from gui.paramexplore.pe_pipeline import QAnnotatedPipelineView
from gui.vistrails_palette import QVistrailsPaletteInterface

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

    def set_controller(self, controller):
        self.controller = controller
        self.set_pipeline(self.controller.current_pipeline)
        self.pipeline_view.setScene(self.controller.current_pipeline_view)

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
        self.pipeline_view.updateAnnotatedIds(pipeline)
        self.virtual_cell.updateVirtualCell(pipeline)

