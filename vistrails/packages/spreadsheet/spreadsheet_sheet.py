###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

"""This file contains a set of internal Spreadsheet basic classes used by
others:
  StandardWidgetHeaderView
  StandardWidgetItemDelegate
  StandardWidgetSheet
"""

from __future__ import division

from PyQt4 import QtCore, QtGui

from .spreadsheet_helpers import CellHelpers, CellResizer


class StandardWidgetHeaderView(QtGui.QHeaderView):
    """
    StandardWidgetHeaderView is the standard header view (containing
    column/row labels) inheriting from QHeaderView. The main
    difference between this class and the original one is that it
    allows resizing and stretching at the same time

    """
    THICKNESS = 30
    MINIMUM_SIZE = 50

    fitToWindow = True

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
        if orientation==QtCore.Qt.Vertical:
            self.setDefaultAlignment(QtCore.Qt.AlignHCenter |
                                     QtCore.Qt.AlignVCenter)

        self.connect(self, QtCore.SIGNAL('sectionResized(int, int, int)'),
                     self.section_resized)
        self._target_size = None

    section_sizes = None
    def read_section_sizes(self):
        if (self.section_sizes is None or
                len(self.section_sizes) != self.count()):
            self.section_sizes = [float(self.sectionSize(self.logicalIndex(i)))
                                  for i in xrange(self.count())]

    _resizing = False

    def section_resized(self, log_index, old_size, new_size):
        if self._resizing:
            return
        else:
            self._resizing = True
            try:
                self._section_resized(log_index, old_size, new_size)
            finally:
                self._resizing = False

    def resize_right_rows(self, vis_index):
        if self._resizing:
            return
        else:
            self._resizing = True
            try:
                self._resize_right_rows(vis_index)
            finally:
                self._resizing = False

    def _section_resized(self, log_index, old_size, new_size):
        """ section_resized(horizontal: bool, log_index: int,
                old_size: int, new_size: int) -> None
        Called when a section of of the header is resized
        """
        if not self.fitToWindow or self._target_size is None:
            return

        vis_index = self.visualIndex(log_index)
        if vis_index == self.count() - 1:
            self.resizeSection(log_index, old_size)
            return

        orig_new_size = new_size

        # Can't shrink below minimum size
        if new_size < old_size and new_size < self.MINIMUM_SIZE:
            new_size = self.MINIMUM_SIZE

        if self._target_size is None:
            return

        # Can't take other cells below minimum size
        if new_size > old_size:
            min_right = 0
            for i in xrange(vis_index + 1, self.count()):
                if not self.isSectionHidden(self.logicalIndex(i)):
                    min_right += self.MINIMUM_SIZE
            pos = self.sectionPosition(log_index)
            total_right = self._target_size - pos - new_size
            if total_right < min_right:
                new_size = self._target_size - pos - min_right

        if new_size != orig_new_size:
            self.resizeSection(log_index, new_size)

        # Resize the rows to the right
        self.read_section_sizes()
        self.section_sizes[vis_index] = float(new_size)
        self._resize_right_rows(vis_index + 1)

    def _resize_right_rows(self, vis_index):
        self.read_section_sizes()

        previous_space = sum(self.section_sizes[vis_index:])
        new_space = self._target_size - sum(self.section_sizes[:vis_index])

        # If we are growing the sections
        if new_space > previous_space:
            allocated_space = new_space - previous_space
            for i, size in enumerate(self.section_sizes[vis_index:], vis_index):
                size += allocated_space * (size / previous_space)
                self.section_sizes[i] = size
                self.resizeSection(self.logicalIndex(i), size)
        # If we are shrinking the sections
        else:
            reclaimed_space = previous_space - new_space
            for i, size in enumerate(self.section_sizes[vis_index:], vis_index):
                size -= reclaimed_space * (
                        (size - self.MINIMUM_SIZE)/previous_space)
                self.section_sizes[i] = size
                self.resizeSection(self.logicalIndex(i), size)

    def sizeHint(self):
        """ sizeHint() -> QSize
        Set a default thickness of the bar to 30

        """
        size = QtGui.QHeaderView.sizeHint(self)
        if self.orientation()==QtCore.Qt.Vertical:
            size.setWidth(self.THICKNESS)
        else:
            size.setHeight(self.THICKNESS)
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
            painter.setClipRegion(QtGui.QRegion(r))
            r.adjust(self.padding//2, self.padding//2,
                     -self.padding//2, -self.padding//2)
            painter.drawRoundedRect(r, self.padding, self.padding)
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
                     self.forceColumnMultiSelect)
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
                     self.forceRowMultiSelect)

        # A hack to force the select all button in single click mode
        cornerButton = self.findChild(QtGui.QAbstractButton)
        if cornerButton:
            self.connect(cornerButton,
                         QtCore.SIGNAL('clicked()'),
                         self.forceSheetSelect)

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

    def forceColumnMultiSelect(self, logicalIndex):
        """ forceColumnMultiSelect(logicalIndex: int) -> None
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

    def forceRowMultiSelect(self, logicalIndex):
        """ forceRowMultiSelect(logicalIndex: int) -> None
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

    def forceSheetSelect(self):
        """ forceSheetSelect() -> None
        Make sure we can toggle the whole sheet selection

        """
        totalCells = self.rowCount()*self.columnCount()
        if (len(self.selectionModel().selectedIndexes())<totalCells):
            self.selectionModel().select(
                QtGui.QItemSelection(self.model().index(0,0),
                                     self.model().index(self.rowCount()-1,
                                                        self.columnCount()-1)),
                QtGui.QItemSelectionModel.Select)
        else:
            self.selectionModel().clearSelection()

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
        vLabels = []
        vIdx = self.verticalHeader().visualIndex
        for i in xrange(newCount):
            vLabels.append(str(vIdx(i)+1))
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
        hLabels = []
        vIdx = self.horizontalHeader().visualIndex
        for i in xrange(newCount):
            hLabels.append(chr(vIdx(i)+ord('A')))
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
        for the scroll mode where hidden cell can be viewed by scrolling
        the scrollbars.

        """
        if fit!=self.fitToWindow:
            self.fitToWindow = fit
            self.horizontalHeader().fitToWindow = fit
            self.horizontalHeader()._target_size = None
            self.verticalHeader().fitToWindow = fit
            self.verticalHeader()._target_size = None
            if not fit:
                width = self.columnWidth(self.columnCount()-1)
                height = self.rowHeight(self.rowCount()-1)

                self.setColumnWidth(self.columnCount()-1, width)
                self.setRowHeight(self.rowCount()-1, height)
            self.stretchCells()
            policy = (QtCore.Qt.ScrollBarAlwaysOff if fit
                      else QtCore.Qt.ScrollBarAlwaysOn)
            self.setHorizontalScrollBarPolicy(policy)
            self.setVerticalScrollBarPolicy(policy)

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
            self.horizontalHeader().resizeSections(QtGui.QHeaderView.Stretch)
            self.verticalHeader().resizeSections(QtGui.QHeaderView.Stretch)

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

    def resizeEvent(self, e):
        if not self.fitToWindow:
            return

        thickness = StandardWidgetHeaderView.THICKNESS
        self.horizontalHeader()._target_size = self.size().width() - thickness
        self.horizontalHeader().resize_right_rows(0)
        self.verticalHeader()._target_size = self.size().height() - thickness
        self.verticalHeader().resize_right_rows(0)

    def getRealLocation(self, vRow, vCol, visual=False):
        """ getRealLocation(vRow: int, vCol: int, visual: bool) -> (int, int)
        Return the actual location even if there is spanning at (vRow, vCol)

        """
        # Qt doesn't provide a mechanism to map from a cell to its
        # span region, so we have to scan the whole spreadsheet N^2
        # for now, but our spreadsheet is usuallly small enough.
        if visual:
            (row, col) = (vRow, vCol)
        else:
            row = self.verticalHeader().logicalIndex(vRow)
            col = self.horizontalHeader().logicalIndex(vCol)
        cellSet = set()
        for r in xrange(self.rowCount()):
            for c in xrange(self.columnCount()):
                cellSet.add((r, c))
        for r in xrange(self.rowCount()):
            for c in xrange(self.columnCount()):
                if (r, c) not in cellSet:
                    continue
                rect = self.visualRect(self.model().index(r, c))
                rSpan = self.rowSpan(r, c)
                cSpan = self.columnSpan(r, c)
                for rs in xrange(rSpan):
                    for cs in xrange(cSpan):
                        if (row==r+rs) and (col==c+cs):
                            return (r, c)
                        if (r+rs, c+cs) in cellSet:
                            cellSet.remove((r+rs, c+cs))
        return (-1, -1)

    def getCell(self, row, col):
        """ getCell(row: int, col: int) -> QWidget
        Get cell at a specific row and column

        """
        return self.cellWidget(*self.getRealLocation(row, col))

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates

        """
        idx = self.model().index(*self.getRealLocation(row, col))
        return self.visualRect(idx)

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates

        """
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
        (row, col) = self.getRealLocation(row, col)
        index = self.model().index(row, col)
        self.setCellWidget(row, col, cellWidget)
        if cellWidget:
            self.delegate.updateEditorGeometry(cellWidget, None, index)
        if (row, col) == self.activeCell:
            self.setActiveCell(row, col)

    def selectCell(self, row, col, toggling):
        """ selectCell(row: int, col: int, toggling: bool) -> None
        Select a cell based on its current selection

        """
        (row, col) = self.getRealLocation(row, col, visual=True)
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
        if toolBar:
            toolBar.snapTo(row, col)
        self.parent().toolBar.setCellToolBar(toolBar)

    def adjustWidgetGeometry(self, row, col):
        """ setActiveCell(row: int, col: int) -> None
        Adjust the widget at cell (row, col) to fit inside the cell

        """
        cellWidget = self.getCell(row, col)
        if cellWidget:
            index = self.model().index(*self.getRealLocation(row, col))
            self.delegate.updateEditorGeometry(cellWidget, None, index)
