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
################################################################################
# This file contains classes controlling tabs in the spreadsheets. A tab is
# a container of a sheet:
#   SizeSpinBox
#   StandardTabDockWidget
#   StandardWidgetSheetTab
#   StandardWidgetTabBar
#   StandardWidgetTabBarEditor
#   StandardWidgetToolBar
################################################################################
from PyQt4 import QtCore, QtGui
import os.path
from spreadsheet_registry import spreadsheetRegistry
from spreadsheet_sheet import StandardWidgetSheet
from spreadsheet_cell import QCellPresenter, QCellContainer, QCellToolBar
from spreadsheet_execute import assignPipelineCellLocations, \
     executePipelineWithProgress
from spreadsheet_config import configuration
from core.inspector import PipelineInspector
import spreadsheet_rc

################################################################################

class SizeSpinBox(QtGui.QSpinBox):
    """
    SizeSpinBox is just an overrided spin box that will also emit
    'editingFinished()' signal when the user interact with mouse
    
    """    
    def __init__(self, initValue=0, parent=None):
        """ SizeSpinBox(initValue: int, parent: QWidget) -> SizeSpinBox
        Initialize with a default width of 50 and a value of 0
        
        """
        QtGui.QSpinBox.__init__(self, parent)
        self.setMinimum(1)
        self.setMinimumWidth(50)
        self.setMaximumWidth(50)
        self.setValue(initValue)

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Emit 'editingFinished()' signal when the user release a mouse button
        
        """
        QtGui.QSpinBox.mouseReleaseEvent(self, event)
        self.emit(QtCore.SIGNAL("editingFinished()"))        

class StandardWidgetToolBar(QtGui.QToolBar):
    """
    StandardWidgetToolBar: The default toolbar for each sheet
    container. By default, only FitToWindow and Table resizing are
    included
    
    """
    def __init__(self, parent=None):
        """ StandardWidgetToolBar(parent: QWidget) -> StandardWidgetToolBar
        Init the toolbar with default actions
        
        """
        QtGui.QToolBar.__init__(self, parent)
        self.sheetTab = parent
        self.addAction(self.sheetTab.tabWidget.newSheetAction())
        self.addAction(self.sheetTab.tabWidget.openAction())
        self.addAction(self.sheetTab.tabWidget.saveAction())
        self.addWidget(self.rowCountSpinBox())
        self.addWidget(self.colCountSpinBox())
        self.addAction(self.sheetTab.tabWidget.exportSheetToImageAction())
        self.addSeparator()
        self.layout().setSpacing(2)
        self.currentToolBarAction = None
    
    def rowCountSpinBox(self):
        """ rowCountSpinBox() -> SizeSpinBox
        Return the row spin box widget:
        
        """
        if not hasattr(self, 'rowSpinBox'):
            self.rowSpinBox = SizeSpinBox(self.sheetTab.sheet.rowCount())
            self.rowSpinBox.setToolTip('The number of rows')
            self.rowSpinBox.setStatusTip('Change the number of rows '
                                         'of the current sheet')
            self.connect(self.rowSpinBox,
                         QtCore.SIGNAL('editingFinished()'),
                         self.sheetTab.rowSpinBoxChanged)
        return self.rowSpinBox

    def colCountSpinBox(self):
        """ colCountSpinBox() -> SizeSpinBox
        Return the column spin box widget:
        
        """
        if not hasattr(self, 'colSpinBox'):
            self.colSpinBox = SizeSpinBox(self.sheetTab.sheet.columnCount())
            self.colSpinBox.setToolTip('The number of columns')
            self.colSpinBox.setStatusTip('Change the number of columns '
                                         'of the current sheet')
            self.connect(self.colSpinBox,
                         QtCore.SIGNAL('editingFinished()'),
                         self.sheetTab.colSpinBoxChanged)
        return self.colSpinBox

    def setCellToolBar(self, cellToolBar):
        """ setCellToolBar(cellToolBar: QToolBar) -> None
        Set the current cell toolbar on this toolbar. Use None to
        remove the cell toolbar
        
        """
        if (not self.currentToolBarAction or
            self.widgetForAction(self.currentToolBarAction)!=cellToolBar):
            if self.currentToolBarAction:
                self.removeAction(self.currentToolBarAction)
            if cellToolBar:
                self.currentToolBarAction = self.addWidget(cellToolBar)
                self.currentToolBarAction.setVisible(True)
                self.currentToolBarAction.setEnabled(True)
            else:
                self.currentToolBarAction = None

class StandardWidgetSheetTabInterface(object):
    """
    StandardWidgetSheetTabInterface is the interface for tab
    controller to call for manipulating a tab
    
    """
    ### Belows are API Wrappers to connect to self.sheet

    def __init__(self):
        self.lastCellLocation = (0, 0)
        self.emptyCellToolBar = None

    def isSheetTabWidget(self):
        """ isSheetTabWidget() -> boolean
        Return True if this is a sheet tab widget
        
        """
        return True

    def getDimension(self):
        """ getDimension() -> tuple
        Get the sheet dimensions
        
        """
        return (0,0)
            
    def setDimension(self, rc, cc):
        """ setDimension(rc: int, cc: int) -> None
        Set the sheet dimensions
        
        """
        pass
            
    def getCell(self, row, col):
        """ getCell(row: int, col: int) -> QWidget        
        Get cell at a specific row and column. In reality, this cell
        widget is inside a QCellContainer and the cell container is
        the actual widget under the cell
        
        """
        cellWidget = self.getCellWidget(row, col)
        if type(cellWidget)==QCellContainer:
            return cellWidget.widget()
        return cellWidget

    def getCellWidget(self, row, col):
        """ getCellWidget(row: int, col: int) -> QWidget        
        Get actual cell at a specific row and column. This will in
        fact return the container widget of a cell
        
        """
        return None

    def setCellWidget(self, row, col, cellWidget):
        """ setCellWidget(row: int,
                          col: int,                            
                          cellWidget: QWidget) -> None                            
        Replace the current location (row, col) with a 
        widget. The widget will be put into a container to be
        protected from being destroyed when taken out.
        
        """
        pass

    def setCellByWidget(self, row, col, cellWidget):
        """ setCellByWidget(row: int,
                            col: int,                            
                            cellWidget: QWidget) -> None
        Put the cellWidget inside a container and place it on the sheet

        """
        if type(cellWidget)!=QCellContainer:
            container = QCellContainer(cellWidget)
        else:
            container = cellWidget
        self.setCellWidget(row, col, container)
        self.lastCellLocation = (row, col)

    def getCellToolBar(self, row, col):
        """ getCellToolBar(row: int, col: int) -> QWidget
        Return the toolbar widget at cell location (row, col)
        
        """
        cell = self.getCell(row, col)
        if cell:
            if hasattr(cell, 'toolBarType'):
                toolBarType = cell.toolBarType
            else:
                toolBarType = QCellToolBar
            container = self.getCellWidget(row, col)
            if type(container)==QCellContainer:
                if container.toolBar==None:
                    container.toolBar = toolBarType(self)
                return container.toolBar
        else:
            if self.emptyCellToolBar==None:
                self.emptyCellToolBar = QCellToolBar(self)
            return self.emptyCellToolBar

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates
        
        """
        return QtCore.QRect()

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates
        
        """
        return QtCore.QRect()

    def getFreeCell(self):
        """ getFreeCell() -> tuple        
        Get a free cell location (row, col) on the spreadsheet

        """
        (rowCount, colCount) = self.getDimension()
        for r in xrange(rowCount):
            for c in xrange(colCount):
                w = self.getCell(r, c)
                if w==None or (type(w)==QCellPresenter and w.cellWidget==None):
                    return (r,c)
        (r, c) = self.lastCellLocation
        (rs, cs) = self.getSpan(r, c)
        index = (colCount * r + c + cs) % (rowCount*colCount)
        return (index/colCount, index%colCount)

    def setCellByType(self, row, col, cellType, inputPorts):
        """ setCellByType(row: int,
                          col: int,
                          cellType: a type inherits from QWidget,
                          inpurPorts: tuple) -> None                          
        Replace the current location (row, col) with a cell of
        cellType. If the current type of that cell is the same as
        cellType, only the contents is updated with inputPorts.
        
        """
        oldCell = self.getCell(row, col)
        if type(oldCell)!=cellType:
            if cellType:
                newCell = cellType(self)
                self.setCellByWidget(row, col, newCell)
                newCell.show()
                newCell.updateContents(inputPorts)
            else:
                self.setCellByWidget(row, col, None)
            if hasattr(oldCell, 'deleteLater'):
                oldCell.deleteLater()
        else:
            oldCell.updateContents(inputPorts)
        self.lastCellLocation = (row, col)

    def showHelpers(self, show, globalPos):
        """ showHelpers(show: boolean, globalPos: QPoint) -> None    
        Show/hide the helpers (toolbar, resizer when the mouse is at
        globalPos
        
        """
        pass

    def setCellPipelineInfo(self, row, col, info):
        """ setCellPipelineInfo(row: int, col: int, info: any type) -> None        
        Provide a way for the spreadsheet to store vistrail
        information, info, for the cell (row, col)
        
        """
        if not (row,col) in self.pipelineInfo:
            self.pipelineInfo[(row,col)] = {}
        self.pipelineInfo[(row,col)] = info

    def getCellPipelineInfo(self, row, col):
        """ getCellPipelineInfo(row: int, col: int) -> any type        
        Provide a way for the spreadsheet to extract vistrail
        information, info, for the cell (row, col)
        
        """        
        if not (row,col) in self.pipelineInfo:
            return None
        return self.pipelineInfo[(row,col)]

    def getSelectedLocations(self):
        """ getSelectedLocations() -> list
        Return the selected locations (row, col) of the current sheet
        
        """
        return []

    def clearSelection(self):
        """ clearSelection() -> None
        Clear all the selection in the current sheet
        
        """
        pass
    
    def deleteCell(self, row, col):
        """ deleteCell(row, col: int) -> None
        Delete a cell in the sheet
        
        """
        self.setCellByType(row, col, None, None)
        self.setCellPipelineInfo(row, col, None)
        
    def deleteAllCells(self):
        """ deleteAllCells() -> None
        Delete all cells in the sheet
        
        """
        (rowCount, columnCount) = self.getDimension()
        for r in xrange(rowCount):
            for c in xrange(columnCount):
                self.deleteCell(r, c)

    def takeCell(self, row, col):
        """ takeCell(row, col) -> QWidget        
        Free the cell widget at (row, col) from the tab and return as
        the result of the function. If there is no widget at (row,
        col). This returns None. The ownership of the widget is passed
        to the caller.
        
        """
        cell = self.getCellWidget(row, col)
        if type(cell)==QCellContainer:
            widget = cell.takeWidget()
            self.setCellWidget(row, col, None)
            return widget
        else:
            return cell

    def setCellEditingMode(self, r, c, editing=True):
        """ setCellEditingMode(r: int, c: int, editing: bool) -> None
        Turn on/off the editing mode of a single cell
        
        """
        if editing:
            cellWidget = self.getCell(r, c)
            if type(cellWidget)==QCellPresenter:
                return
            presenter = QCellPresenter()
            presenter.assignCell(self, r, c)
            cellWidget = self.takeCell(r, c)
            self.setCellByWidget(r, c, presenter)
            if cellWidget:
                cellWidget.hide()
        else:
            presenter = self.getCell(r, c)
            if type(presenter)!=QCellPresenter:
                return
            presenter = self.takeCell(r, c)
            if presenter:
                cellWidget = presenter.releaseCellWidget()
                self.setCellByWidget(r, c, cellWidget)
                presenter.hide()
    
    def setEditingMode(self, editing=True):
        """ setEditingMode(editing: bool) -> None
        Turn on/off the editing mode of the tab
        
        """
        # Turn off active cell selection
        self.sheet.clearSelection()
        self.sheet.setActiveCell(-1, -1)
        # Go over all the cells and set the editing widget up
        (rowCount, colCount) = self.getDimension()
        for r in xrange(rowCount):
            for c in xrange(colCount):
                self.setCellEditingMode(r, c, editing)
        QtCore.QCoreApplication.processEvents()

    def swapCell(self, row, col, newSheet, newRow, newCol):
        """ swapCell(row, col: int, newSheet: Sheet,
                     newRow, newCol: int) -> None
        Swap the (row, col) of this sheet to (newRow, newCol) of newSheet
        
        """
        myWidget = self.takeCell(row, col)
        theirWidget = newSheet.takeCell(newRow, newCol)
        self.setCellByWidget(row, col, theirWidget)
        newSheet.setCellByWidget(newRow, newCol, myWidget)
        info = self.getCellPipelineInfo(row, col)
        self.setCellPipelineInfo(row, col,
                                 newSheet.getCellPipelineInfo(newRow, newCol))
        newSheet.setCellPipelineInfo(newRow, newCol, info)

    def copyCell(self, row, col, newSheet, newRow, newCol):
        """ copyCell(row, col: int, newSheet: Sheet,
                     newRow, newCol: int) -> None
        Copy the (row, col) of this sheet to (newRow, newCol) of newSheet
        
        """
        info = self.getCellPipelineInfo(row, col)
        if info:
            info = info[0]
            mId = info['moduleId']
            pipeline = newSheet.setPipelineToLocateAt(newRow, newCol,
                                                      info['pipeline'], [mId])
            executePipelineWithProgress(pipeline, 'Copy Cell',
                                        current_version=info['version'],
                                        actions=info['actions'],
                                        reason=info['reason'],
                                        locator=info['locator'],
                                        sinks=[mId])

    def executePipelineToCell(self, pInfo, row, col, reason=''):
        """ executePipelineToCell(p: tuple, row: int, col: int) -> None
        p: (locator, version, actions, pipeline)
        
        Execute a pipeline and put all of its cell to (row, col). This
        need to be fixed to layout all cells inside the pipeline
        
        """
        pipeline = self.setPipelineToLocateAt(row, col, pInfo[3])
        executePipelineWithProgress(pipeline, 'Execute Cell',
                                    locator=pInfo[0],
                                    current_version=pInfo[1],
                                    actions=pInfo[2],
                                    reason=reason)

    def setPipelineToLocateAt(self, row, col, inPipeline, cellIds=[]):
        """ setPipelineToLocateAt(row: int, col: int, inPipeline: Pipeline,
                                  cellIds: [ids]) -> Pipeline                                  
        Modify the pipeline to have its cells (provided by cellIds) to
        be located at (row, col) of this sheet
        
        """
        sheetName = str(self.tabWidget.tabText(self.tabWidget.indexOf(self)))
        # Note that we must increment row/col by 1 to match how the
        # CellReference module expects them
        return assignPipelineCellLocations(inPipeline, sheetName,
                                           row + 1, col + 1, cellIds)

    def getPipelineInfo(self, row, col):
        """ getPipelineInfo(row: int, col: int) -> tuple
        Return (locator, versionNumber, actions, pipeline) for a cell
        
        """
        info = self.getCellPipelineInfo(row, col)
        if info:
            return (info[0]['locator'],
                    info[0]['version'],
                    info[0]['actions'],
                    info[0]['pipeline'])
        return None

    def exportSheetToImage(self, fileName):
        """ exportSheetToImage() -> None
        Montage all the cell images and export to a file
        
        """
        (rCount, cCount) = self.getDimension()
        if rCount<1 or cCount<1: return
        cellHeights = [self.getCellRect(r, 0).height()
                       for r in xrange(rCount)]
        cellWidths = [self.getCellRect(0, c).width()
                      for c in xrange(cCount)] 
        finalImage = QtGui.QImage(sum(cellWidths), sum(cellHeights), QtGui.QImage.Format_ARGB32)
        finalImage.fill(0xFFFFFFFF)
        painter = QtGui.QPainter(finalImage)
        y = 0
        for r in xrange(rCount):
            x = 0
            for c in xrange(cCount):
                widget = self.getCell(r, c)
                if widget:
                    pix = widget.grabWindowPixmap()
                    cx = (cellWidths[c]-pix.width())/2
                    cy = (cellHeights[r]-pix.height())/2
                    painter.drawPixmap(x+cx, y+cy, widget.grabWindowPixmap())
                x += cellWidths[c]
            y += cellHeights[r]
        painter.end()
         
        #forcing png format if no extension was provided 
        (_,ext) = os.path.splitext(fileName)
        if ext == '':
            finalImage.save(fileName, 'png')
        else:
            #try to guess based on the extension
            finalImage.save(fileName)

    def exportSheetToImages(self, dirPath, format='png'):
        """ exportSheetToImage() -> None
        Montage all the cell images and export to a file
        
        """
        (rCount, cCount) = self.getDimension()
        for r in xrange(rCount):
            for c in xrange(cCount):
                widget = self.getCell(r, c)
                if widget:
                    widget.grabWindowPixmap().save(dirPath+'/'+
                                                   chr(c+ord('a'))+
                                                   str(r+1)+
                                                   '.'+format)

    def setSpan(self, row, col, rowSpan, colSpan):
        """ setSpan(row, col, rowSpan, colSpan: int) -> None
        Set the spanning at location (row, col). This is only a place
        holder. Subclasses should implement this and getSpan for a
        fully functioning spanning feature.
        
        """
        pass

    def getSpan(self, row, col):
        """ setSpan(row, col: int) -> (rowSpan, colSpan: int)
        Return the spanning at location (row, col). This is only a
        place holder. Subclasses should implement this and setSpan for
        a fully functioning spanning feature.
        
        """
        return (1, 1)

class StandardWidgetSheetTab(QtGui.QWidget, StandardWidgetSheetTabInterface):
    """
    StandardWidgetSheetTab is a container of StandardWidgetSheet with
    a toolbar on top. This will be added directly to a QTabWidget for
    displaying the spreadsheet.
    
    """
    def __init__(self, tabWidget,row=None , col=None):
        """ StandardWidgetSheet(tabWidget: QTabWidget,
                                row: int,
                                col: int) -> StandardWidgetSheet
        Initialize with a toolbar and a sheet widget
                                
        """
        QtGui.QWidget.__init__(self, None)
        StandardWidgetSheetTabInterface.__init__(self)
        if not row:
            row = configuration.rowCount
        if not col:
            col = configuration.columnCount
        self.type = 'StandardWidgetSheetTab'
        self.tabWidget = tabWidget
        self.sheet = StandardWidgetSheet(row, col, self)
        self.sheet.setFitToWindow(True)
        self.toolBar = StandardWidgetToolBar(self)
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setSpacing(0)
        self.vLayout.setMargin(0)
        self.vLayout.addWidget(self.toolBar, 0)
        self.vLayout.addWidget(self.sheet, 1)
        self.setLayout(self.vLayout)
        self.pipelineInfo = {}
        self.setAcceptDrops(True)

    def rowSpinBoxChanged(self):
        """ rowSpinBoxChanged() -> None
        Handle the number of row changed
        
        """
        if self.toolBar.rowSpinBox.value()!=self.sheet.rowCount():
            self.sheet.setRowCount(self.toolBar.rowSpinBox.value())
            self.sheet.stretchCells()
            self.setEditingMode(self.tabWidget.editingMode)
        
    def colSpinBoxChanged(self):
        """ colSpinBoxChanged() -> None
        Handle the number of row changed
        
        """
        if self.toolBar.colSpinBox.value()!=self.sheet.columnCount():
            self.sheet.setColumnCount(self.toolBar.colSpinBox.value())
            self.sheet.stretchCells()
            self.setEditingMode(self.tabWidget.editingMode)

    ### Belows are API Wrappers to connect to self.sheet

    def getDimension(self):
        """ getDimension() -> tuple
        Get the sheet dimensions
        
        """
        return (self.sheet.rowCount(), self.sheet.columnCount())
            
    def setDimension(self, rc, cc):
        """ setDimension(rc: int, cc: int) -> None
        Set the sheet dimensions
        
        """
        self.toolBar.rowCountSpinBox().setValue(rc)
        self.toolBar.colCountSpinBox().setValue(cc)
            
    def getCellWidget(self, row, col):
        """ getCellWidget(row: int, col: int) -> QWidget
        Get cell at a specific row and column.
        
        """
        return self.sheet.getCell(row, col)

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates
        
        """
        return self.sheet.getCellRect(row, col)

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates
        
        """
        return self.sheet.getCellGlobalRect(row, col)

    def showHelpers(self, show, globalPos):
        """ showHelpers(show: boolean, globalPos: QPoint) -> None        
        Show/hide the helpers (toolbar, resizer) depending on the
        status of show and the global position of the cursor
        
        """
        localPos = self.sheet.viewport().mapFromGlobal(QtGui.QCursor.pos())
        row = self.sheet.rowAt(localPos.y())
        col = self.sheet.columnAt(localPos.x())
        rect = self.sheet.getCellRect(row, col)
        show =  show and (rect.x()+rect.width()-localPos.x()<100 and
                          rect.y()+rect.height()-localPos.y()<100)
        self.sheet.showHelpers(show, row, col)
        
    def getSelectedLocations(self):
        """ getSelectedLocations() -> list
        Return the selected locations (row, col) of the current sheet
        
        """
        indexes = self.sheet.selectedIndexes()
        return [(idx.row(), idx.column()) for idx in indexes]

    def clearSelection(self):
        """ clearSelection() -> None
        Clear all the selection in the current sheet
        
        """
        self.sheet.clearSelection()
    
    def setCellWidget(self, row, col, cellWidget):
        """ setCellWidget(row: int,
                            col: int,                            
                            cellWidget: QWidget) -> None                            
        Replace the current location (row, col) with a cell widget
        
        """
        self.sheet.setCellByWidget(row, col, cellWidget)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the version tree
        
        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'versionId'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops while moving from the version tree
        
        """
        mimeData = event.mimeData()
        if (hasattr(mimeData, 'versionId') and
            hasattr(mimeData, 'controller')):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """ Execute the pipeline at the particular location """
        mimeData = event.mimeData()        
        if (hasattr(mimeData, 'versionId') and
            hasattr(mimeData, 'controller')):
            event.accept()
            versionId = mimeData.versionId
            controller = mimeData.controller
            pipeline = controller.vistrail.getPipeline(versionId)

            inspector = PipelineInspector()
            inspector.inspect_spreadsheet_cells(pipeline)
            inspector.inspect_ambiguous_modules(pipeline)
            if len(inspector.spreadsheet_cells)==1:
                localPos = self.sheet.viewport().mapFromGlobal(QtGui.QCursor.pos())
                row = self.sheet.rowAt(localPos.y())
                col = self.sheet.columnAt(localPos.x())
                if (row!=-1 and col!=-1):
                    pipeline = self.setPipelineToLocateAt(row, col, pipeline)
            executePipelineWithProgress(pipeline, 'Execute Cell',
                                        locator=controller.locator,
                                        current_version=versionId,
                                        reason='Drop Version')
        else:
            event.ignore()

    def setSpan(self, row, col, rowSpan, colSpan):
        """ setSpan(row, col, rowSpan, colSpan: int) -> None
        Set the spanning at location (row, col).
        
        """
        colSpan = max(colSpan, 1)
        rowSpan = max(rowSpan, 1)
        (curRowSpan, curColSpan) = self.getSpan(row, col)
        if rowSpan!=curRowSpan or colSpan!=curColSpan:
            # Need to remove all cell except the top-left
            for r in xrange(rowSpan):
                for c in xrange(colSpan):
                    if r!=0 or c!=0:
                        self.deleteCell(row+r, col+c)
                        
            # Take the current widget out
            curWidget = self.takeCell(row, col)

            #  ... before setting the span
            self.sheet.setSpan(row, col, rowSpan, colSpan)

            # Then put it back in
            if curWidget:
                self.setCellByWidget(row, col, curWidget)

    def getSpan(self, row, col):
        """ setSpan(row, col: int) -> (rowSpan, colSpan: int)
        Return the spanning at location (row, col). This is only a
        place holder. Subclasses should implement this and setSpan for
        a fully functioning spanning feature.
        
        """
        return (self.sheet.rowSpan(row, col), self.sheet.columnSpan(row, col))

    
class StandardWidgetTabBarEditor(QtGui.QLineEdit):    
    """
    StandardWidgetTabBarEditor overrides QLineEdit to enable canceling
    edit when Esc is pressed
    
    """
    def __init__(self, text='', parent=None):
        """ StandardWidgetTabBarEditor(text: str, parent: QWidget)
                                       -> StandardWidgetTabBarEditor
        Store the original text at during initialization
        
        """
        QtGui.QLineEdit.__init__(self, text, parent)
        self.originalText = text

    def keyPressEvent(self, e):
        """ keyPressEvent(e: QKeyEvent) -> None
        Override keyPressEvent to handle Esc key
        
        """
        if e.key()==QtCore.Qt.Key_Escape:
            e.ignore()
            self.setText(self.originalText)
            self.clearFocus()
        else:
            QtGui.QLineEdit.keyPressEvent(self, e)

class StandardWidgetTabBar(QtGui.QTabBar):
    """
    StandardWidgetTabBar: a customized QTabBar to allow double-click
    to change tab name
    
    """
    def __init__(self, parent=None):
        """ StandardWidgetTabBar(parent: QWidget) -> StandardWidgetTabBar
        Initialize like the original QTabWidget TabBar
        
        """
        QtGui.QTabBar.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setStatusTip('Move the sheet in, out and around'
                          'by dragging the tabs')
        self.setDrawBase(False)
        self.editingIndex = -1
        self.editor = None        
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self, QtCore.SIGNAL('currentChanged(int)'),
                     self.updateTabText)
        self.startDragPos = None
        self.dragging = False
        self.targetTab = -1
        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 self)
        self.outerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 None)

    def mouseDoubleClickEvent(self, e):
        """ mouseDoubleClickEvent(e: QMouseEvent) -> None
        Handle Double-Click event to start the editor
        
        """
        if e.buttons()!=QtCore.Qt.LeftButton or self.editor: return
        
        # Update the current editing tab widget
        self.editingIndex = self.currentIndex()
        
        # A hack to capture the rect of the triangular tab from commonstyle.cpp
        rect = self.tabRect(self.editingIndex)
        h = rect.height()-2
        dx = h/3 + 3
        rect.adjust(dx+1,1,-dx,-1)

        # Display the editor inplace of the tab text
        text = self.tabText(self.editingIndex)
        self.editor = StandardWidgetTabBarEditor(text, self)
        self.editor.setFont(self.font())
        self.editor.setFrame(False)
        self.editor.setGeometry(rect)
        self.editor.setAlignment(QtCore.Qt.AlignHCenter)
        self.editor.selectAll()
        self.connect(self.editor, QtCore.SIGNAL('editingFinished()'),
                     self.updateTabText)
        self.editor.show()
        self.editor.setFocus(QtCore.Qt.MouseFocusReason)

    def updateTabText(self, idx=0):
        """ updateTabText(idx: int) -> None
        Update the tab text after editing has been finished
        
        """
        if self.editingIndex>=0 and self.editor:
            self.setTabText(self.editingIndex, self.editor.text())
            self.emit(QtCore.SIGNAL('tabTextChanged(int,QString)'),
                      self.editingIndex,self.editor.text())
            self.editor.deleteLater()
            self.editingIndex = -1
            self.editor = None

    def indexAtPos(self, p):
        """ indexAtPos(p: QPoint) -> int Reimplement of the private
        indexAtPos to find the tab index under a point
        
        """
        if self.tabRect(self.currentIndex()).contains(p):
            return self.currentIndex()
        for i in xrange(self.count()):
            if self.isTabEnabled(i) and self.tabRect(i).contains(p):                
                return i
        return -1;

    def mousePressEvent(self, e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Handle mouse press event to see if we should start to drag tabs or not
        
        """
        QtGui.QTabBar.mousePressEvent(self, e)
        if e.buttons()==QtCore.Qt.LeftButton and self.editor==None:
            self.startDragPos = QtCore.QPoint(e.x(), e.y())

    def getGlobalRect(self, index):
        """ getGlobalRect(self, index: int)
        Get the rectangle of a tab in global coordinates
        
        """
        if index<0: return None
        rect = self.tabRect(index)
        rect.moveTo(self.mapToGlobal(rect.topLeft()))
        return rect

    def highlightTab(self, index):
        """ highlightTab(index: int)
        Highlight the rubber band of a tab
        
        """
        if index==-1:
            self.innerRubberBand.hide()
        else:
            self.innerRubberBand.setGeometry(self.tabRect(index))
            self.innerRubberBand.show()
            
    def mouseMoveEvent(self, e):
        """ mouseMoveEvent(e: QMouseEvent) -> None
        Handle dragging tabs in and out or around
        
        """
        QtGui.QTabBar.mouseMoveEvent(self, e)
        if self.startDragPos:
            # We already move more than 4 pixels
            if (self.startDragPos-e.pos()).manhattanLength()>=4:
                self.startDragPos = None
                self.dragging = True
        if self.dragging:
            t = self.indexAtPos(e.pos())
            if t!=-1:
                if t!=self.targetTab:                    
                    self.targetTab = t
                    self.outerRubberBand.hide()
                    self.highlightTab(t)
            else:
                self.highlightTab(-1)
                if t!=self.targetTab:
                    self.targetTab = t
                if self.count()>0:
                    if not self.outerRubberBand.isVisible():
                        index = self.getGlobalRect(self.currentIndex())
                        self.outerRubberBand.setGeometry(index)
                        self.outerRubberBand.move(e.globalPos())
                        self.outerRubberBand.show()
                    else:
                        self.outerRubberBand.move(e.globalPos())

    def mouseReleaseEvent(self, e):
        """ mouseReleaseEvent(e: QMouseEvent) -> None
        Make sure the tab moved at the end
        
        """
        QtGui.QTabBar.mouseReleaseEvent(self, e)
        if self.dragging:
            if self.targetTab!=-1 and self.targetTab!=self.currentIndex():
                self.emit(QtCore.SIGNAL('tabMoveRequest(int,int)'),
                          self.currentIndex(),
                          self.targetTab)
            elif self.targetTab==-1:
                self.emit(QtCore.SIGNAL('tabSplitRequest(int,QPoint)'),
                          self.currentIndex(),
                          e.globalPos())
            self.dragging = False
            self.targetTab = -1
            self.highlightTab(-1)
            self.outerRubberBand.hide()
            
    def slotIndex(self, pos):
        """ slotIndex(pos: QPoint) -> int
        Return the slot index between the slots at the cursor pos
        
        """
        p = self.mapFromGlobal(pos)
        for i in xrange(self.count()):
            r = self.tabRect(i)
            if self.isTabEnabled(i) and r.contains(p):
                if p.x()<(r.x()+r.width()/2):
                    return i
                else:
                    return i+1
        return -1
        
    def slotGeometry(self, idx):
        """ slotGeometry(idx: int) -> QRect
        Return the geometry between the slots at cursor pos
        
        """
        if idx<0 or self.count()==0: return None
        if idx<self.count():
            rect = self.getGlobalRect(idx)
            rect = QtCore.QRect(rect.x()-5, rect.y(), 5*2, rect.height())
            return rect
        else:
            rect = self.getGlobalRect(self.count()-1)
            rect = QtCore.QRect(rect.x()+rect.width()-5, rect.y(),
                                5*2, rect.height())
            return rect

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the other cell info
        
        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'cellInfo'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            idx = self.indexAtPos(event.pos())
            if idx>=0:
                self.setCurrentIndex(idx)
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drops from the other cell info
        
        """
        idx = self.indexAtPos(event.pos())
        if idx>=0:
            self.setCurrentIndex(idx)
            
            
class StandardTabDockWidget(QtGui.QDockWidget):
    """
    StandardTabDockWidget inherits from QDockWidget to contain a sheet
    widget floating around that can be merge back to tab controller
    
    """
    def __init__(self, title, tabWidget, tabBar, tabController):
        """ StandardTabDockWidget(title: str,
                                  tabWidget: QTabWidget,
                                  tabBar: QTabBar,
                                  tabController: StandardWidgetTabController)
                                  -> StandardTabDockWidget
        Initialize the dock widget to override the floating button
        
        """
        QtGui.QDockWidget.__init__(self, title, None,
                                   QtCore.Qt.FramelessWindowHint)
        self.tabBar = tabBar
        self.tabController = tabController
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable |
                         QtGui.QDockWidget.DockWidgetMovable |
                         QtGui.QDockWidget.DockWidgetFloatable)
        self.setFloating(True)
        self.floatingButton = self.findFloatingButton()
        if self.floatingButton:
            self.floatingButton.blockSignals(True)
            self.floatingButton.installEventFilter(self)
        self.startDragPos = None
        self.startDragging = False
        self.windowRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                  None)
        tabWidget.setParent(self)
        self.setWidget(tabWidget)
        tabWidget.show()
        self.resize(tabWidget.size())

    def findFloatingButton(self):
        """ findFloatingButton() -> QAbstractButton        
        Hack to find the private Floating Button. Since there is only
        one button exists, we just need to find QAbstractButton
        
        """
        for c in self.children():
            if type(c)==QtGui.QAbstractButton:
                return c
        return None

    def eventFilter(self, q, e):
        """ eventFilter(q: QObject, e: QEvent) -> depends on event type
        Event filter the floating button to makes it merge to the tab controller
        
        """
        if q and q==self.floatingButton:
            if (e.type()==QtCore.QEvent.MouseButtonRelease and
                e.button()&QtCore.Qt.LeftButton):
                if self.isMaximized():
                    self.showNormal()
                else:
                    self.showMaximized()
                return False
        return QtGui.QDockWidget.eventFilter(self, q, e)

    def isTabControllerUnderMouse(self, tb):        
        """ Check if any of common parent of the tab controller and tb
        is under the mouse """
        tbp = []
        while tb!=None:
            tbp.append(tb)
            tb = tb.parent()
        tc = self.tabController
        while tc!=None:
            if tc in tbp:
                return True
            tc = tc.parent()
        return False

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Handle movement of the dock widget to snap to the tab controller
        
        """
        # MOUSE PRESS (QtCore.QEvent.NonClientAreaMouseButtonPress=174)
        if e.type() in [QtCore.QEvent.MouseButtonPress,174]:
            if e.type()==174:
                gp = QtGui.QCursor.pos()
                ontitle = True
            else:
                gp = e.globalPos()
                ontitle = e.y()<self.widget().y() and e.buttons()&QtCore.Qt.LeftButton
            if ontitle:
                self.startDragPos = QtCore.QPoint(gp)
                self.grabMouse()
            return True

        elif e.type()==QtCore.QEvent.MouseMove:
            if not (e.buttons() & QtCore.Qt.LeftButton):
                self.windowRubberBand.hide()
                self.setMouseTracking(False)
                return QtGui.QDockWidget.event(self, e)
            gp = e.globalPos()
            if (not self.startDragging and
                self.startDragPos and
                (self.startDragPos-gp).manhattanLength()>=4):
                self.startDragging = True
                self.windowRubberBand.setGeometry(self.geometry())
                self.startDragPos = self.pos()-gp
                self.windowRubberBand.show()
                self.setMouseTracking(True)
            if self.startDragging:
                tb = QtGui.QApplication.widgetAt(gp)
                if tb==self.tabBar:
                    idx = tb.slotIndex(gp)
                    if idx>=0:
                        self.windowRubberBand.setGeometry(tb.slotGeometry(idx))
                elif (tb!=None and self.tabController.count()==0 and
                      self.isTabControllerUnderMouse(tb)):
                    r = self.tabController.frameGeometry()
                    r.moveTo(self.tabController.mapToGlobal(r.topLeft()))
                    self.windowRubberBand.setGeometry(r)
                else:
                    rect = QtCore.QRect(self.startDragPos+gp, self.size())
                    self.windowRubberBand.setGeometry(rect)
            return True

        # MOUSE RELEASE (QtCore.QEvent.NonClientAreaMouseRelease=175)
        elif e.type()==QtCore.QEvent.MouseButtonRelease:
            if self.startDragging:
                if e.type()==173:
                    gp = QtGui.QCursor.pos()
                else:
                    gp = e.globalPos()
                self.setMouseTracking(False)
                self.windowRubberBand.hide()
                self.startDragPos = None
                self.startDragging = False
                tb = QtGui.QApplication.widgetAt(gp)
                if tb==self.tabBar:
                    idx = tb.slotIndex(gp)
                    if idx>=0:
                        self.hide()
                        self.tabController.mergeTab(self, idx)
                elif (tb!=None and self.tabController.count()==0 and
                      self.isTabControllerUnderMouse(tb)):
                    self.hide()
                    self.tabController.mergeTab(self, 0)
                else:
                    self.move(self.windowRubberBand.pos())
            self.releaseMouse()
            self.setFocus(QtCore.Qt.MouseFocusReason)
            return True

        # MOUSE DOUBLE CLICK (QtCore.QEvent.NonClientAreaMouseButtonDblClick=176)
        elif e.type() in [QtCore.QEvent.MouseButtonDblClick, 176]:
            if (e.type()==176) or (e.buttons()&QtCore.Qt.LeftButton):
                self.hide()
                self.tabController.mergeTab(self, self.tabController.count())
                return True
            
        return QtGui.QDockWidget.event(self, e)

    def closeEvent(self, event):
        """ On close event dock the sheet back to the spreadsheet window """
        self.tabController.mergeTab(self, self.tabController.count())
        event.accept()

spreadsheetRegistry.registerSheet('StandardWidgetSheetTab',
                                  StandardWidgetSheetTab)
