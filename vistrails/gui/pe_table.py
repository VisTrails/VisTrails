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
""" The file describes the parameter exploration table for VisTrails

QParameterExplorationTable
"""


from PyQt4 import QtCore, QtGui
from gui.common_widgets import QPromptWidget
from gui.theme import CurrentTheme

################################################################################
class QParameterExplorationTable(QtGui.QTableWidget):
    """
    QParameterExplorationTable is a grid layout widget having 4
    comlumns corresponding to 4 dimensions of exploration. It accept
    method/alias drops and can be fully configured onto any
    dimension. For each parameter, 3 different approach can be chosen
    to assign the value of that parameter during the exploration:
    linear interpolation (for int, float), list (for int, float and
    string) and user-define function (for int, float, and string)
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationTable(parent: QWidget)
                                      -> QParameterExplorationTable
        Create an grid layout and accept drops
        
        """
        QtGui.QTableWidget.__init__(self, 1, 6, parent)
        self.setAutoFillBackground(True)
        self.setAcceptDrops(True)
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        
        self.setCellWidget(0, 0, QDimensionLabel(None, 'Parameter', self))

        self.setCellWidget(0, 1,
                           QDimensionLabel(CurrentTheme.EXPLORE_COLUMN_PIXMAP,
                                           'Column', self))

        self.setCellWidget(0, 2,
                           QDimensionLabel(CurrentTheme.EXPLORE_ROW_PIXMAP,
                                           'Row', self))

        self.setCellWidget(0, 3,
                           QDimensionLabel(CurrentTheme.EXPLORE_SHEET_PIXMAP,
                                           'Sheet', self))

        self.setCellWidget(0, 4,
                           QDimensionLabel(CurrentTheme.EXPLORE_TIME_PIXMAP,
                                           'Time', self))
        self.setCellWidget(0, 5, QDimensionLabel(None, 'Skip', self))

        self.updateColumnSizes()
        self.verticalHeader().resizeSection(0, 80)

    def updateColumnSizes(self):
        """ updateColumnSizes() -> None
        We resize 4 dimensional columns and fixed the two end ones
        
        """
        nameColumnWidth = 90
        ignoreColumnWidth = 40
        usableWidth = (self.width() - nameColumnWidth - ignoreColumnWidth)
        shares = 3
        self.horizontalHeader().resizeSection(0, 90)
        # Assign the default column width and row height
        for i in range(shares):
            width = usableWidth/shares + int(i<(usableWidth%shares))-1
            self.horizontalHeader().resizeSection(1+i,
                                                  width)
        self.horizontalHeader().resizeSection(4, 10)

    def resizeEvent(self, event):
        """ resizeEvent(event: QResizeEvent) -> None
        Make sure we resize the column appropriately
        
        """
        self.updateColumnSizes()
        QtGui.QTableWidget.resizeEvent(self, event)

    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Make sure to promptly show a message when there is not yet
        any parameter
        
        """
        QtGui.QTableWidget.paintEvent(self, event)
        if self.rowCount()==1:
            painter = QtGui.QPainter(self.viewport())
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            font = QtGui.QFont(self.font())
            font.setItalic(True)
            painter.setFont(font)
            painter.drawText(self.rect(),
                             QtCore.Qt.AlignCenter | QtCore.Qt.TextWrapAnywhere,
                             'Drag aliases/parameters here for a parameter '
                             'exploration')
            painter.end()            

class QDimensionLabel(QtGui.QWidget):
    """
    QDimensionLabel represents the horizontal header item of the
    parameter window. It has a large icon and a small description
    
    """
    def __init__(self, pix, text, parent=None):
        """ QDimensionLabel(pix: QPixmap, text: str, parent: QWidget) -> None
        Initialize the label with an icon and a caption
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setLayout(QtGui.QVBoxLayout(self))
        label = QtGui.QLabel()
        label.setAlignment(QtCore.Qt.AlignCenter)
        if pix:
            label.setPixmap(pix)
        else:
            font = QtGui.QFont(label.font())
            font.setBold(True)
            font.setUnderline(True)
            label.setFont(font)
            label.setText(text)
        self.layout().addWidget(label)

    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Make sure to promptly show a message when there is not yet
        any parameter
        
        """
        # Force to draw the background
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), self.palette().brush(QtGui.QPalette.Window))
        painter.end()
        QtGui.QWidget.paintEvent(self, event)
    

################################################################################

if __name__=="__main__":        
    import sys
    import gui.theme
    app = QtGui.QApplication(sys.argv)
    gui.theme.initializeCurrentTheme()
    vc = QDimensionLabel(CurrentTheme.EXPLORE_SHEET_PIXMAP, 'Hello World')
    vc.show()
    sys.exit(app.exec_())
