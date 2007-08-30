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
            for i in reversed(xrange(self.count()-1-logicalIndex)):
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
        self.padding = 4
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

    def paint(self, painter, option, index):
        """ paint(painter: QPainter, option: QStyleOptionViewItem,
                  index: QModelIndex) -> None                  
        Paint the current cell with a ring outside
        
        """
        QtGui.QItemDelegate.paint(self, painter, option, index)
        if ((index.row(), index.column())==self.table.activeCell):
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QBrush(
                QtGui.QColor(0.8549*255, 0.6971*255, 0.2255*255)), self.padding))
            r = self.table.visualRect(index)
            r.adjust(self.padding/2,self.padding/2,-self.padding/2,-self.padding/2)
            painter.drawRoundRect(r, self.padding, self.padding)
            painter.restore()
            
            
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
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
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
        self.connect(self.horizontalHeader(),
                     QtCore.SIGNAL('sectionPressed(int)'),
                     self.forceColumnMutliSelect) 
        self.setVerticalHeader(StandardWidgetHeaderView(QtCore.Qt.Vertical,
                                                        self))
        self.verticalHeader().setSelectionModel(self.selectionModel())
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionCountChanged(int, int)'),
                     self.updateRowLabels)
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionMoved(int,int,int)'),
                     self.rowMoved)
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionPressed(int)'),
                     self.forceRowMutliSelect) 
        self.delegate = StandardWidgetItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.helpers = CellHelpers(parent, CellResizer(self))
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setFitToWindow(True)
        self.connect(self,
                     QtCore.SIGNAL('cellActivated(int, int, bool)'),
                     self.selectCell)
        self.activeCell = (-1,-1)

    def forceColumnMutliSelect(self, logicalIndex):
        """ forceColumnMutliSelect(logicalIndex: int) -> None        
        Make sure we always toggle the headerview in the right way        
        NOTE: the MultiSelection type of SelectionMode does not work
        correctly for overlapping columns and rows selection
        
        """
        if (self.selectionModel().isColumnSelected(logicalIndex, QtCore.QModelIndex())):
            self.selectionModel().select(self.model().index(0, logicalIndex),
                                         QtGui.QItemSelectionModel.Deselect |
                                         QtGui.QItemSelectionModel.Columns)
        else:
            self.selectionModel().select(self.model().index(0, logicalIndex),
                                         QtGui.QItemSelectionModel.Select |
                                         QtGui.QItemSelectionModel.Columns)

    def forceRowMutliSelect(self, logicalIndex):
        """ forceRowMutliSelect(logicalIndex: int) -> None        
        Make sure we always toggle the headerview in the right way        
        NOTE: the MultiSelection type of SelectionMode does not work
        correctly for overlapping columns and rows selection
        
        """
        if (self.selectionModel().isRowSelected(logicalIndex, QtCore.QModelIndex())):
            self.selectionModel().select(self.model().index(logicalIndex, 0),
                                         QtGui.QItemSelectionModel.Deselect |
                                         QtGui.QItemSelectionModel.Rows)
        else:
            self.selectionModel().select(self.model().index(logicalIndex, 0),
                                         QtGui.QItemSelectionModel.Select |
                                         QtGui.QItemSelectionModel.Rows)

    def updateHeaderStatus(self):
        """ updateHeaderStatus() -> None
        Update the visibility of the row and column header
        
        """
        return
        self.horizontalHeader().setVisible(self.columnCount() > 1 or
                                           self.rowCount() > 1)
        self.verticalHeader().setVisible(self.columnCount() > 1 or
                                         self.rowCount() > 1)

    def updateRowLabels(self, oldCount, newCount):
        """ updateRowLabels(oldCount: int, newCount: int) -> None
        Update vertical labels when the number of row changed
        
        """
        vLabels = QtCore.QStringList()
        vIdx = self.verticalHeader().visualIndex
        for i in xrange(newCount):
            vLabels << str(vIdx(i)+1)
        self.setVerticalHeaderLabels(vLabels)
        self.updateHeaderStatus()

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
        for i in xrange(newCount):
            hLabels << chr(vIdx(i)+ord('A'))
        self.setHorizontalHeaderLabels(hLabels)
        self.updateHeaderStatus()
        
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

    def showHelpers(self, show, row, col):
        """ showHelpers(show: boolean, row: int, col: int) -> None        
        Show/hide the helpers (resizer, toolbar) on the current cell
        depending on the value of show
        
        """
        if self.helpers.isInteracting():
            return
        if show:
            if row>=0 and col>=0:
                self.helpers.snapTo(row, col)
                self.helpers.adjustPosition()
                self.helpers.show()
            else:
                self.helpers.hide()
        else:
            self.helpers.hide()

    def getCell(self, row, col):
        """ getCell(row: int, col: int) -> QWidget
        Get cell at a specific row and column
        
        """
        row = self.verticalHeader().logicalIndex(row)
        col = self.horizontalHeader().logicalIndex(col)
        return self.cellWidget(row, col)

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates
        
        """
        row = self.verticalHeader().logicalIndex(row)
        col = self.horizontalHeader().logicalIndex(col)
        idx = self.model().index(row, col)
        return self.visualRect(idx)

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates
        
        """
        row = self.verticalHeader().logicalIndex(row)
        col = self.horizontalHeader().logicalIndex(col)
        rect = self.getCellRect(row, col)
        rect.moveTo(self.viewport().mapToGlobal(rect.topLeft()))
        return rect

    def setCellByWidget(self, row, col, cellWidget):
        """ setCellByWidget(row: int,
                            col: int,                            
                            cellWidget: QWidget) -> None
        Replace the current location (row, col) with a cell widget
        
        """
        if cellWidget:
            # Relax the size constraint of the widget
            cellWidget.setMinimumSize(QtCore.QSize(0, 0))
            cellWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
            cellWidget.setParent(self)
        row = self.verticalHeader().logicalIndex(row)
        col = self.horizontalHeader().logicalIndex(col)
        index = self.model().index(row, col)
        self.setCellWidget(row, col, cellWidget)
        if cellWidget:
            self.delegate.updateEditorGeometry(cellWidget, None, index)

    def selectCell(self, row, col, toggling):
        """ selectCell(row: int, col: int, toggling: bool) -> None
        Select a cell based on its current selection
        
        """
        if toggling:
            self.selectionModel().setCurrentIndex(self.model().index(row, col),
                                                  QtGui.QItemSelectionModel.Toggle)
            if (self.selectionModel().isSelected(self.model().index(row, col))):
                self.setActiveCell(row, col)
            else:
                self.setActiveCell(-1, -1)
        else:
            if len(self.selectionModel().selectedIndexes())<=1:
                self.selectionModel().setCurrentIndex(
                    self.model().index(row, col),
                    QtGui.QItemSelectionModel.ClearAndSelect)
            self.setActiveCell(row, col)
        self.viewport().repaint()

    def setActiveCell(self, row, col):
        """ setActiveCell(row: int, col: int) -> None
        Set the location of an active cell also bring up the
        corresponding toolbar

        """
        self.activeCell = (row, col)
        toolBar = self.parent().getCellToolBar(row, col)
        if (toolBar):
            toolBar.snapTo(row, col)
        self.parent().toolBar.setCellToolBar(toolBar)
