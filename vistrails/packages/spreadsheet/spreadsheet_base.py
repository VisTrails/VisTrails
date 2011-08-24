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
# This file contains a set of internal Spreadsheet basic classes used
# by others:
#   StandardSheetReference
#   StandardSingleCellSheetReference
#   StandardSingleCellSheetTab
################################################################################
from PyQt4 import QtCore, QtGui
from spreadsheet_helpers import CellHelpers
from spreadsheet_registry import spreadsheetRegistry
from spreadsheet_tab import (StandardWidgetSheetTab,
                             StandardWidgetSheetTabInterface)

################################################################################

class StandardSheetReference(object):
    """
    StandardSheetReference is used to specify which sheet a cell want
    to be on. It also knows how to decide if a sheet on the
    spreadsheet is appropriate for itself.
    """

    def __init__(self):
        """ StandardSheetReference() -> StandardSheetReference
        Initialize to the current sheet with no minimum size
        
        """
        self.sheetName = None
        self.minimumRowCount = 1
        self.minimumColumnCount = 1
        self.candidate = None

    def isTabValid(self, tabWidget):
        """ isTabValid(tabWidget: QWidget) -> boolean
        Check to see if the tab is an acceptable type
        
        """
        return issubclass(tabWidget.__class__, StandardWidgetSheetTab)

    def clearCandidate(self):
        """ clearCandidate() -> None        
        Begin the candidate searching process by clearing the previous        
        candidate sheet. The searching process is done by looping
        through all available sheets and let the SheetReference decides
        and keep track of which one is the best appropriate
        
        """
        self.candidate = None

    def checkCandidate(self, tabWidget, tabLabel, tabIndex, curIndex):
        """ checkCandidate(tabWidget: QWidget,
                           tabLabel: str,
                           tabIndex: int,
                           curIndex: int) -> None                           
        Check to see if this new candidate is better than the one we
        have right now. If it is then use this one instead. The
        condition is very simple, sheet type comes first, then name
        and dimensions.

        Keyword arguments:
        tabWidget --- QWidget controlling actual sheet widget
        tabLabel  --- the display label of the sheet
        tabIndex  --- its index inside the tab controller
        curIndex  --- the current active index of the tab controller
        
        """
        if self.isTabValid(tabWidget):
            if (self.sheetName!=None and
                str(tabLabel)!=str(self.sheetName)):
                return
            if self.candidate!=None:
                if (self.sheetName==None or
                    (str(tabLabel)==str(self.sheetName))==
                    (str(self.candidate[1])==str(self.sheetName))):
                    storedSheet = self.candidate[0].sheet
                    newSheet = tabWidget.sheet
                    if (newSheet.rowCount()<self.minimumRowCount and
                        storedSheet.rowCount()>=self.minimumRowCount):
                        return
                    if (newSheet.columnCount()<self.minimumColumnCount and
                        storedSheet.columnCount()>=self.minimumColumnCount):
                        return
                    if (((newSheet.rowCount()<self.minimumRowCount)==
                         (storedSheet.rowCount()<self.minimumRowCount)) and
                        ((newSheet.columnCount()<self.minimumColumnCount)==
                         (storedSheet.columnCount()<self.minimumColumnCount))):
                        if tabIndex!=curIndex:
                            return
            self.candidate = (tabWidget, tabLabel, tabIndex, curIndex)
                
    def setupCandidate(self, tabController):
        """ setupCandidate(tabController: SpreadsheetTabController) -> None
        Setup the candidate we have to completely satisfy the reference,
        making ready to be displayed on, e.g. extend the number of row and
        column
        
        """
        if self.candidate==None:
            candidate = StandardWidgetSheetTab(tabController,
                                               self.minimumRowCount,
                                               self.minimumColumnCount)
            idx = tabController.addTabWidget(candidate, self.sheetName)
            tabController.setCurrentIndex(idx)
            candidate.sheet.stretchCells()
            return candidate
        else:
            if self.candidate[0].sheet.rowCount()<self.minimumRowCount:
                self.candidate[0].sheet.setRowCount(self.minimumRowCount)
            if self.candidate[0].sheet.columnCount()<self.minimumColumnCount:
                self.candidate[0].sheet.setColumnCount(self.minimumColumnCount)
            tabController.setCurrentWidget(self.candidate[0])
            return self.candidate[0]

class StandardSingleCellSheetTab(QtGui.QWidget,
                                 StandardWidgetSheetTabInterface):
    """
    StandardSingleCellSheetTab is a container of StandardWidgetSheet
    with only a single cell. This will be added directly to a
    QTabWidget on the spreadsheet as a sheet for displaying
    
    """
    def __init__(self, tabWidget, row=1, col=1):
        """ StandardSingleCellSheetTab(row: int,
                                       col: int) -> StandardSingleCellSheetTab
        Initialize with the vertical layout containing only a single widget
        
        """
        QtGui.QWidget.__init__(self, None)
        StandardWidgetSheetTabInterface.__init__(self)
        self.type = 'StandardSingleCellSheetTab'
        self.tabWidget = tabWidget
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setSpacing(0)
        self.vLayout.setMargin(0)
        self.setLayout(self.vLayout)
        self.cell = QtGui.QWidget()
        self.layout().addWidget(self.cell)
        self.helpers = CellHelpers(self)
        self.toolBars = {}
        self.blankCellToolBar = None
        self.pipelineInfo = {}

    ### Belows are API Wrappers to connect to self.sheet
            
    def getDimension(self):
        """ getDimension() -> tuple
        Get the sheet dimensions
        
        """
        return (1,1)
            
    def getCell(self, row, col):
        """ getCell(row: int, col: int) -> QWidget
        Get cell at a specific row and column.
        
        """
        return self.cell

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
        return self.sheet.getCellToolBar(row, col)

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates
        
        """
        return self.contentsRect()

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates
        
        """
        rect = self.getCellRect(row, col)
        rect.moveTo(self.mapToGlobal(rect.topLeft()))
        return rect

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
            oldCell.hide()
            self.layout().removeWidget(oldCell)
            if cellType:
                self.cell = cellType(self)
#                self.cell.setGeometry(self.getCellRect(row, col))
                self.layout().addWidget(self.cell)
                self.cell.show()
                self.cell.updateContents(inputPorts)
            if hasattr(oldCell, 'deleteLater'):
                oldCell.deleteLater()
            del oldCell
        else:
            oldCell.updateContents(inputPorts)

    def showHelpers(self, show, globalPos):
        """ showHelpers(show: boolean, globalPos: QPoint) -> None
        Show the helpers (toolbar, resizer) when show==True
        
        """
        if show:
            self.helpers.snapTo(0,0)
            self.helpers.adjustPosition()
            self.helpers.show()
        else:
            self.helpers.hide()

    def getSelectedLocations(self):
        """ getSelectedLocations() -> tuple
        Return the selected locations (row, col) of the current sheet
        
        """
        return [(0,0)]

class StandardSingleCellSheetReference(StandardSheetReference):
    """
    StandardSingleCellSheetReference is a sheet reference that only
    accepts a single cell. This overrides the StandardSheetReference
    
    """
    def isTabValid(self, tabWidget):
        """ isTabValid(tabWidget: QWidget) -> boolean
        Only accepts StandardSingleCellSheetTab
        
        """
        return issubclass(tabWidget.__class__, StandardSingleCellSheetTab)

    def checkCandidate(self, tabWidget, tabLabel, tabIndex, curIndex):
        """ checkCandidate(tabWidget: QWidget,
                           tabLabel: str,
                           tabIndex: int,
                           curIndex: int) -> None
        Better candidate is decided merely if it is the current index
        
        """
        if self.isTabValid(tabWidget):
            better = False
            if (self.sheetName!=None and
                str(tabLabel)!=str(self.sheetName)):
                return
            if self.candidate!=None:
                if self.candidate[2]==curIndex or tabIndex!=curIndex:
                    return
            self.candidate = (tabWidget, tabLabel, tabIndex, curIndex)
                
    def setupCandidate(self, tabController):
        """ setupCandidate(tabController: SpreadsheetTabController) -> None
        Set up the sheet to be single-cell sheet
        
        """
        if self.candidate==None:
            candidate = StandardSingleCellSheetTab(tabController)
            index = tabController.addTabWidget(candidate, self.sheetName)
            tabController.setCurrentIndex(index)
            return candidate
        else:
            return self.candidate[0]

spreadsheetRegistry.registerSheet('StandardSingleCellSheetTab',
                                  StandardSingleCellSheetTab)

