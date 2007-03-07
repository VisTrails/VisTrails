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
################################################################################
# This file contains a set of internal Spreadsheet basic classes used
# by others:
#   StandardWidgetHeaderView
#   StandardWidgetItemDelegate
#   StandardWidgetSheet
################################################################################
from PyQt4 import QtCore, QtGui
from spreadsheet_helpers import CellHelpers, CellResizer

################################################################################

class StandardWidgetHeaderView(QtGui.QHeaderView):
    """
    StandardWidgetHeaderView is the standard header view (containing
    column/row labels) inheriting from QHeaderView. The main
    difference between this class and the original one is that it
    allows resizing and stretching at the same time
    
    """
    def __init__(self, orientation, parent=None):
        """ StandardWidgetHeaderView(orientation: QtCore.Qt.Align...,
                                     parent: QWidget)
                                     -> StandardWidgetHeaderView
        Initialize the header view to be like the one in the spreadsheet table
        
        """
        QtGui.QHeaderView.__init__(self, orientation, parent)
        self.setMovable(True)
        self.setFont(QtGui.QFont("Helvetica",12,QtGui.QFont.Bold))
        self.resizeSections(QtGui.QHeaderView.Stretch)
        self.setClickable(True)
        self.setHighlightSections(True)
        self.fitToViewport = False
        if orientation==QtCore.Qt.Vertical:
            self.setDefaultAlignment(QtCore.Qt.AlignHCenter |
                                     QtCore.Qt.AlignVCenter)
        self.minimumSize = 50

    def setFitToViewport(self, fit=True):
        """ setFitToViewport(fit: boolean) -> None        
        Set fit to viewport for have all the sections always stretch
        to the whole viewport

        """
        if self.fitToViewport!=fit:
            self.fitToViewport = fit
            if fit:
                self.connect(self, QtCore.SIGNAL("sectionResized(int,int,int)"),
                             self.fixSize)
            else:
                self.disconnect(self,
                                QtCore.SIGNAL("sectionResized(int,int,int)"),
                                self.fixSize)

    def fixSize(self, logicalIndex, oldSize, newSize):
        """ fixSize(logicalIndex: int, oldSize: int, newSize: int) -> None        
        This slot capture sectionResized signal and makes sure all the
        sections are stretched right. 
        
        """
        if newSize<self.minimumSize:
            self.resizeSection(logicalIndex, self.minimumSize)
            return

        if self.orientation()==QtCore.Qt.Horizontal:
            diff = self.length()-self.maximumViewportSize().width()
        else:
            diff = self.length()-self.maximumViewportSize().height()
        if diff>0:
            self.setFitToViewport(False)
            for i in reversed(range(self.count()-1-logicalIndex)):
                realIndex = i+logicalIndex+1
                oldS = self.sectionSize(realIndex)
                newS = max(oldS-diff, self.minimumSize)
                if newS!=oldS:
                    self.resizeSection(realIndex, newS)
                diff = diff - (oldS-newS)
                if diff==0: break
            newSize = max(newSize-diff, oldSize)
            self.resizeSection(logicalIndex, newSize)
            self.setFitToViewport(True)

    def sizeHint(self):
        """ sizeHint() -> QSize
        Set a default thickness of the bar to 30
        
        """
        size = QtGui.QHeaderView.sizeHint(self)
        if self.orientation()==QtCore.Qt.Vertical:
            size.setWidth(30)
        else:
            size.setHeight(30)
        return size

class StandardWidgetItemDelegate(QtGui.QItemDelegate):
    """
    StandardWidgetItemDelegate will replace the QTableWidget default
    display to have a padding around every cell widget

    """
    def __init__(self, table):
        """ StandardWidgetItemDelegate(table: QTableWidget)
                                       -> StandardWidgetItemDelegate
        Initialize to store a table and padding
        
        """
        self.table = table
        self.padding = 2
        QtGui.QItemDelegate.__init__(self, None)

    def setPadding(self, padding):
        """ setPadding(padding: int) -> None
        Re-set padding to a different value
        
        """
        if self.padding!=padding:
            self.padding = padding

    def updateEditorGeometry(self, editor, option, index):
        """ updateEditorGeometry(editor: QWidget,
                                 option: QStyleOptionViewItem,
                                 index: QModelIndex) -> None
        Make sure the widget only occupied inside the padded area
    
        """
        rect = self.table.visualRect(index)
        rect.adjust(self.padding,self.padding,-self.padding,-self.padding)
        editor.setGeometry(rect)
        editor.setFixedSize(rect.width(), rect.height())
            
class StandardWidgetSheet(QtGui.QTableWidget):
    """
    StandardWidgetSheet is a standard sheet that can contain any type
    of cell widget. Each of them will be put into a separate cell. In
    the case of vtkRenderWindow, where creating each sheet separately
    can end up with a large number of GL contexts, a special type of
    VTK sheet need to be derived from this one

    """
    def __init__(self, rows=0, cols=0, parent=None):
        """ StandardWidgetSheet(rows: int, cols: int, parent: QWidget)
                                -> StandardWidgetSheet
        Construct a sheet with rows x cols cells
        
        """
        QtGui.QTableWidget.__init__(self, 0, 0, parent)
        self.fitToWindow = False
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setHorizontalHeader(StandardWidgetHeaderView(QtCore.Qt.Horizontal,
                                                          self))
        self.horizontalHeader().setSelectionModel(self.selectionModel())
        self.connect(self.horizontalHeader(),
                     QtCore.SIGNAL('sectionCountChanged(int, int)'),
                     self.updateColumnLabels)
        self.connect(self.horizontalHeader(),
                     QtCore.SIGNAL('sectionMoved(int,int,int)'),
                     self.columnMoved)
        self.setVerticalHeader(StandardWidgetHeaderView(QtCore.Qt.Vertical,
                                                        self))
        self.verticalHeader().setSelectionModel(self.selectionModel())
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionCountChanged(int, int)'),
                     self.updateRowLabels)
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionMoved(int,int,int)'),
                     self.rowMoved)
        self.delegate = StandardWidgetItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.helpers = CellHelpers(self, CellResizer(self))
        self.toolBars = {}
        self.blankCellToolBar = None
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setFitToWindow(True)

    def updateRowLabels(self, oldCount, newCount):
        """ updateRowLabels(oldCount: int, newCount: int) -> None
        Update vertical labels when the number of row changed
        
        """
        vLabels = QtCore.QStringList()
        vIdx = self.verticalHeader().visualIndex
        for i in range(newCount):
            vLabels << str(vIdx(i)+1)
        self.setVerticalHeaderLabels(vLabels)

    def rowMoved(self, row, old, new):
        """ rowMove(row: int, old: int, new: int) -> None
        Renumber the vertical header labels when rows moved
        
        """
        self.updateRowLabels(self.rowCount(), self.rowCount())
        
    def updateColumnLabels(self, oldCount, newCount):
        """ updateColumnLabels(oldCount: int, newCount: int) -> None
        Update horizontal labels when the number of column changed
        
        """
        hLabels = QtCore.QStringList()
        vIdx = self.horizontalHeader().visualIndex
        for i in range(newCount):
            hLabels << chr(vIdx(i)+ord('A'))
        self.setHorizontalHeaderLabels(hLabels)

    def columnMoved(self, row, old, new):
        """ columnMoved(row: int, old: int, new: int) -> None
        Renumber the horizontal header labels when columns moved
        
        """
        self.updateColumnLabels(self.columnCount(), self.columnCount())
        
    def setFitToWindow(self, fit=True):
        """ setFitToWindow(fit: boolean) -> None
        Force to fit all cells into the visible area. Set fit=False
        for the scroll mode where hidden cell can be view by scrolling
        the scrollbars.
        
        """
        if fit!=self.fitToWindow:
            self.fitToWindow = fit
            self.horizontalHeader().setFitToViewport(fit)
            self.verticalHeader().setFitToViewport(fit)
            if not fit:
                width = self.columnWidth(self.columnCount()-1)
                height = self.rowHeight(self.rowCount()-1)
            self.horizontalHeader().setStretchLastSection(fit)
            self.verticalHeader().setStretchLastSection(fit)            
            if not fit:
                self.setColumnWidth(self.columnCount()-1, width)
                self.setRowHeight(self.rowCount()-1, height)
            self.stretchCells()

    def showEvent(self, event):
        """ showEvent(event: QShowEvent) -> None
        Make sure to stretch the sheet on the first appearance
        
        """
        self.stretchCells()

    def stretchCells(self):
        """ stretchCells() -> None
        Stretch all the cells with equally spaces to fit in the viewport
        
        """
        if self.fitToWindow:
            self.horizontalHeader().setFitToViewport(False)
            self.horizontalHeader().resizeSections(QtGui.QHeaderView.Stretch)
            self.horizontalHeader().setFitToViewport(True)
            self.verticalHeader().setFitToViewport(False)
            self.verticalHeader().resizeSections(QtGui.QHeaderView.Stretch)
            self.verticalHeader().setFitToViewport(True)
            
    def resizeEvent(self, e):
        """ resizeEvent(e: QResizeEvent) -> None        
        ResizeEvent will make sure all columns/rows stretched right
        when the table get resized
        
        """
        QtGui.QTableWidget.resizeEvent(self, e)
        self.stretchCells()

    def showHelpers(self, ctrl, row, col):
        """ showHelpers(ctrl: boolean, row: int, col: int) -> None        
        Show/hide the helpers (resizer, toolbar) on the current cell
        depending on the status of the Control key and cell location
        
        """
        if ctrl:
            if self.helpers.isInteracting():
                return
            if row>=0 and col>=0:
                self.helpers.snapTo(row, col)
                self.helpers.adjustPosition()
                self.helpers.show()
            else:
                self.helpers.hide()
        else:
            self.helpers.hide()

    def leaveEvent(self, e):
        """ leaveEvent(e: QMouseEvent) -> None
        Hide the helpers when mouse leave the widget
        
        """
        self.showHelpers(False, -1, -1)

    def getCell(self, row, col):
        """ getCell(row: int, col: int) -> QWidget
        Get cell at a specific row and column
        
        """
        return self.cellWidget(row, col)

    def getCellToolBar(self, row, col):
        """ getCellToolBar(row: int, col: int) -> QWidget
        Return the toolbar widget at cell location (row, col)
        
        """
        cell = self.getCell(row, col)
        if cell and hasattr(cell, 'toolBarType'):
            if not self.toolBars.has_key(cell.toolBarType):
                self.toolBars[cell.toolBarType] = cell.toolBarType(self)
            return self.toolBars[cell.toolBarType]
        else:
            return self.blankCellToolBar

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates
        
        """
        idx = self.model().index(row, col)
        return self.visualRect(idx)

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates
        
        """
        rect = self.getCellRect(row, col)
        rect.moveTo(self.viewport().mapToGlobal(rect.topLeft()))
        return rect

    def getFreeCell(self):
        """ getFreeCell() -> tuple
        Get a free cell location (row, col) on the spreadsheet 

        """
        vIdx = self.verticalHeader().logicalIndex
        hIdx = self.horizontalHeader().logicalIndex
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                if self.getCell(vIdx(r), hIdx(c))==None:
                    return (r,c)
        return (0, 0)

    def setCellByType(self, row, col, cellType, inputPorts):
        """ setCellByType(row: int,
                          col: int,
                          cellType: a type inherits from QWidget,
                          inpurPorts: tuple) -> None
        Replace the current location (row, col) with a cell of
        cellType. If the current type of that cell is the same as
        cellType, only the contents is updated with inputPorts.
        
        """
        row = self.verticalHeader().logicalIndex(row)
        col = self.horizontalHeader().logicalIndex(col)
        oldCell = self.getCell(row, col)
        if type(oldCell)!=cellType:
            if cellType:
                newCell = cellType(self)
                self.setCellWidget(row, col, newCell)
                index = self.model().index(row, col)
                self.delegate.updateEditorGeometry(newCell,
                                                   None,
                                                   index)
                newCell.show()
                newCell.updateContents(inputPorts)                
            else:
                self.setCellWidget(row, col, None)
            if hasattr(oldCell, 'deleteLater'):
                oldCell.deleteLater()
            del oldCell
        else:
            oldCell.updateContents(inputPorts)
