from PyQt4 import QtCore, QtGui
from spreadsheet_helpers import *

################################################################################
################################################################################
### StandardWidgetHeaderView: the standard header view (containing
### column/row labels). The main difference between this class and the
### original one is that it allows resizing and stretching at the same
### time.
class StandardWidgetHeaderView(QtGui.QHeaderView):

    ### Initialize the header view to be like the one in the table
    def __init__(self, orientation, parent=None):
        QtGui.QHeaderView.__init__(self, orientation, parent)
        self.setFont(QtGui.QFont("Helvetica",12,QtGui.QFont.Bold))
        self.resizeSections(QtGui.QHeaderView.Stretch)
        self.setClickable(True)
        self.setHighlightSections(True)
        self.fitToViewport = False
        if orientation==QtCore.Qt.Vertical:
            self.setDefaultAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.minimumSize = 50

    ### Set fit to viewport for have all the sections always stretch
    ### to the whole viewport
    def setFitToViewport(self, fit=True):
        if self.fitToViewport!=fit:
            self.fitToViewport = fit
            if fit:
                self.connect(self, QtCore.SIGNAL("sectionResized(int,int,int)"), self.fixSize)
            else:
                self.disconnect(self, QtCore.SIGNAL("sectionResized(int,int,int)"), self.fixSize)

    ### This slot capture sectionResized signal and makes sure all the
    ### sections are stretched right. Then it will emit
    ### 'lastSectionResized' with the list of all sections that have
    ### been updated. QTableView should capture this signal instead if
    ### it uses StandardWidgetHeaderView.
    def fixSize(self, logicalIndex, oldSize, newSize):
        if newSize<self.minimumSize:
            self.resizeSection(logicalIndex, self.minimumSize)
            return

        updatedSections = []
    
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
                    updatedSections.append((realIndex, newS))
                diff = diff - (oldS-newS)
                if diff==0: break
            newSize = max(newSize-diff, oldSize)
            self.resizeSection(logicalIndex, newSize)
            self.setFitToViewport(True)
        updatedSections.append((logicalIndex, newSize))
        self.emit(QtCore.SIGNAL('lastSectionResized'), updatedSections)

    ### Set a default thickness of the bar to 30
    def sizeHint(self):
        size = QtGui.QHeaderView.sizeHint(self)
        if self.orientation()==QtCore.Qt.Vertical:
            size.setWidth(30)
        else:
            size.setHeight(30)
        return size

################################################################################
################################################################################
### StandardWidgetItemDelegate: this will replace the QTableWidget to
### have a padding around any cell widget.
class StandardWidgetItemDelegate(QtGui.QItemDelegate):

    ### Initialize with table and padding
    def __init__(self, table):
        self.table = table
        self.padding = 2
        QtGui.QItemDelegate.__init__(self, None)

    ### Re-set padding to a different value
    def setPadding(self, padding):
        if self.padding!=padding:
            self.padding = padding

    ### Make sure the widget only occupied inside the padded area
    def updateEditorGeometry(self, editor, option, index):
        rect = self.table.visualRect(index)
        rect.adjust(self.padding,self.padding,-self.padding,-self.padding)
        editor.setGeometry(rect)
        editor.setFixedSize(rect.width(), rect.height())
            
################################################################################
################################################################################
### StandardWidgetSheet: the standard sheet that can contains any type
### of cell widget.  Each of them will be put into a separate cell. In
### the case of vtkRenderWindow, where creating each sheet separately
### can end up with a large number of GL contexts, a new VTK sheet
### need to be created inherited from this one.
class StandardWidgetSheet(QtGui.QTableWidget):

    ### Construct a sheet with rows x cols cells
    def __init__(self, rows=0, cols=0, parent=None):
        QtGui.QTableWidget.__init__(self, 0, 0, parent)
        self.fitToWindow = False
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setHorizontalHeader(StandardWidgetHeaderView(QtCore.Qt.Horizontal, self))
        self.horizontalHeader().setSelectionModel(self.selectionModel())
        self.connect(self.horizontalHeader(),
                     QtCore.SIGNAL('sectionCountChanged(int, int)'),
                     self.updateColumnLabels)
        self.setVerticalHeader(StandardWidgetHeaderView(QtCore.Qt.Vertical, self))
        self.verticalHeader().setSelectionModel(self.selectionModel())
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL('sectionCountChanged(int, int)'),
                     self.updateRowLabels)
        self.delegate = StandardWidgetItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.helpers = CellHelpers(self, CellResizer(self))
        self.toolBars = {}
        self.blankCellToolBar = None
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setFitToWindow(True)

    ### Update vertical labels when the number of row changed
    def updateRowLabels(self, oldCount, newCount):
        vLabels = QtCore.QStringList()
        for i in range(newCount):
            vLabels << str(i+1)
        self.setVerticalHeaderLabels(vLabels)


    ### Update horizontal labels when the number of column changed
    def updateColumnLabels(self, oldCount, newCount):
        hLabels = QtCore.QStringList()
        for i in range(newCount):
            hLabels << chr(i+ord('A'))
        self.setHorizontalHeaderLabels(hLabels)

    ### Force to fit all cells into the visible area. Set fit=False
    ### for the scroll mode where hidden cell can be view by scrolling
    ### the scrollbars.
    def setFitToWindow(self, fit=True):
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

    ### A helper function to set the resizing mode of the table to Stretch
    def stretchCells(self):
        if self.fitToWindow:
            self.horizontalHeader().resizeSections(QtGui.QHeaderView.Stretch)
            self.verticalHeader().resizeSections(QtGui.QHeaderView.Stretch)
            
    ### resizeEvent will make sure all columns/rows stretched right
    ### when the table get resized
    def resizeEvent(self, e):
        QtGui.QTableWidget.resizeEvent(self, e)
        self.stretchCells()

    ### Show the helpers (resizer, toolbar) on the current cell
    def showHelpers(self, ctrl, row, col):
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

    ### Hide the helpers when mouse leave the widget
    def leaveEvent(self, e):
        self.showHelpers(False, -1, -1)

    ### Get cell at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCell(self, row, col):
        return self.cellWidget(row, col)

    ### Get cell toolbar at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellToolBar(self, row, col):
        cell = self.getCell(row, col)
        if cell and hasattr(cell, 'toolBarType'):
            if not self.toolBars.has_key(cell.toolBarType):
                self.toolBars[cell.toolBarType] = cell.toolBarType(self)
            return self.toolBars[cell.toolBarType]
        else:
            return self.blankCellToolBar

    ### Get the cell rectangle at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellRect(self, row, col):
        idx = self.model().index(row, col)
        return self.visualRect(idx)

    ### Get the global cell rectangle at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellGlobalRect(self, row, col):
        rect = self.getCellRect(row, col)
        rect.moveTo(self.viewport().mapToGlobal(rect.topLeft()))
        return rect

    ### Get a free cell on the spreadsheet
    def getFreeCell(self):
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                if self.getCell(r, c)==None:
                    return (r,c)
        return (0,0)

    ### Create a cell based on celltype, location and input ports
    def setCellByType(self, row, col, cellType, inputPorts):
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
            del oldCell
        else:
            oldCell.updateContents(inputPorts)
