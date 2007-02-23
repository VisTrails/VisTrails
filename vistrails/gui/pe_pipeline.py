############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
""" This containing a subclassed QGraphicsView that allows View the
pipeline in a specific way in the parameter exploration window
"""
from PyQt4 import QtCore, QtGui
from gui.common_widgets import QToolWindowInterface
from gui.pipeline_view import QPipelineView, QGraphicsModuleItem
from gui.virtual_cell import QVirtualCellLabel

################################################################################
class QMarkPipelineView(QPipelineView, QToolWindowInterface):
    """
    QMarkPipelineView subclass QPipelineView to perform some overlay
    marking on a pipeline view
    
    """
    def __init__(self, parent=None):
        """ QPipelineView(parent: QWidget) -> QPipelineView
        Initialize the graphics view and its properties
        
        """
        QPipelineView.__init__(self, parent)
        self.setWindowTitle('Annotated Pipeline')

    def sizeHint(self):
        """ sizeHint() -> QSize
        Prefer the view not so large
        
        """
        return QtCore.QSize(256, 256)

    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Paint an overlay annotation on spreadsheet cell modules
        
        """
        QPipelineView.paintEvent(self, event)
        if self.scene():
            painter = QtGui.QPainter(self.viewport())
            id = 1
            for item in self.scene().modules.itervalues():
                if item.isSpreadsheetCell:
                    br = item.sceneBoundingRect().center()
                    rect = QtCore.QRect(QtCore.QPoint(0,0),
                                        self.mapFromScene(br))
                    QVirtualCellLabel.drawId(painter, rect, id, True)
                    id += 1
            painter.end()
