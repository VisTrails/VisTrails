from PyQt4 import QtCore, QtGui
from spreadsheet_tab import StandardWidgetSheetTab
from spreadsheet_helpers import *
from spreadsheet_registry import spreadsheetRegistry

################################################################################
################################################################################
### StandardSheetReference: Specify which sheet a cell want to be on
class StandardSheetReference(object):

    ### Initial to a current sheet with no minimum size
    def __init__(self):
        self.sheetName = None
        self.minimumRowCount = 1
        self.minimumColumnCount = 1
        self.candidate = None

    ### Check to see if the tab is an acceptable type
    def isTabValid(self, tabWidget):
        return issubclass(StandardWidgetSheetTab, tabWidget.__class__)

    ### Set no candidate for reference:
    def clearCandidate(self):
        self.candidate = None

    ### Check to see if a widget is better than the candidate we have?
    def checkCandidate(self, tabWidget, tabLabel, tabIndex, curIndex):
        if self.isTabValid(tabWidget):
            if (self.sheetName!=None and
                str(tabLabel)!=str(self.sheetName)):
                return
            if self.candidate!=None:
                if (self.sheetName==None or
                    (str(tabLabel)==str(self.sheetName))==
                    (str(self.candidate[1])==str(self.sheetName))):
                    if (tabWidget.sheet.rowCount()<self.minimumRowCount and
                        self.candidate[0].sheet.rowCount()>=self.minimumRowCount):
                        return
                    if (tabWidget.sheet.columnCount()<self.minimumColumnCount and
                        self.candidate[0].sheet.columnCount()>=self.minimumColumnCount):
                        return
                    if (((tabWidget.sheet.rowCount()<self.minimumRowCount)==
                         (self.candidate[0].sheet.rowCount()<self.minimumRowCount)) and
                        ((tabWidget.sheet.columnCount()<self.minimumColumnCount)==
                         (self.candidate[0].sheet.columnCount()<self.minimumColumnCount))):
                        if tabIndex!=curIndex:
                            return
            self.candidate = (tabWidget, tabLabel, tabIndex, curIndex)
                
    ### Setup the candidate on the tab controller
    def setupCandidate(self, tabController):
        if self.candidate==None:
            candidate = StandardWidgetSheetTab(tabController,
                                               self.minimumRowCount,
                                               self.minimumColumnCount)
            tabController.setCurrentIndex(tabController.addTabWidget(candidate, self.sheetName))
            candidate.sheet.stretchCells()
            return candidate
        else:
            if self.candidate[0].sheet.rowCount()<self.minimumRowCount:
                self.candidate[0].sheet.setRowCount(self.minimumRowCount)
            if self.candidate[0].sheet.columnCount()<self.minimumColumnCount:
                self.candidate[0].sheet.setColumnCount(self.minimumColumnCount)
            tabController.setCurrentWidget(self.candidate[0])
            return self.candidate[0]

################################################################################
################################################################################
### StandardSingleCellSheetTab: a container of StandardWidgetSheet
### with only a single cell. This will be added directly to a
### QTabWidget for displaying the spreadsheet.
class StandardSingleCellSheetTab(QtGui.QWidget):

    ### Init with the initial vertical layout
    def __init__(self, tabWidget, row=1, col=1):
        QtGui.QWidget.__init__(self, None)
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
            
    ### Return True if this is a sheet tab widget
    def isSheetTabWidget(self):
        return True

    ### Get the sheet dimensions
    def getDimension(self):
        return (1,1)
            
    ### Set the sheet dimensions
    def setDimension(self, rc, cc):
        pass
            
    ### Get cell at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCell(self, row, col):
        return self.cell

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
        return self.sheet.getCellToolBar(row, col)

    ### Get the cell rectangle at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellRect(self, row, col):
        return self.contentsRect()

    ### Get the global cell rectangle at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellGlobalRect(self, row, col):
        rect = self.getCellRect(row, col)
        rect.moveTo(self.mapToGlobal(rect.topLeft()))
        return rect

    ### Get a free cell on the spreadsheet
    def getFreeCell(self):
        return (0,0)

    ### Create a cell based on celltype, location and input ports
    def setCellByType(self, row, col, cellType, inputPorts):
        oldCell = self.getCell(row, col)
        if type(oldCell)!=cellType:
            oldCell.hide()
            self.layout().removeWidget(oldCell)
            if cellType:
                self.cell = cellType(self)
                self.cell.setGeometry(self.getCellRect(row, col))
                self.layout().addWidget(self.cell)
                self.cell.show()
                self.cell.updateContents(inputPorts)
            del oldCell
        else:
            oldCell.updateContents(inputPorts)

    ### Show the helpers at a location p
    def showHelpers(self, ctrl, globalPos):
        if ctrl:
            self.helpers.snapTo(0,0)
            self.helpers.adjustPosition()
            self.helpers.show()
        else:
            self.helpers.hide()
            
    ### Set information about a vistrail cell
    def setCellPipelineInfo(self, row, col, info):
        if not (row,col) in self.pipelineInfo:
            self.pipelineInfo[(row,col)] = {}
        self.pipelineInfo[(row,col)] = info

    ### Get information about a vistrail cell
    def getCellPipelineInfo(self, row, col):
        if not (row,col) in self.pipelineInfo:
            return None
        return self.pipelineInfo[(row,col)]

    ### Return the selected locations (row, col) of the current sheet
    def getSelectedLocations(self):
        return [(0,0)]

################################################################################
################################################################################
### StandardSingleCellSheetReference: A sheet reference that only accepts 1 cell
class StandardSingleCellSheetReference(StandardSheetReference):

    ### Check to see if the tab is an acceptable type
    def isTabValid(self, tabWidget):
        return issubclass(StandardSingleCellSheetTab, tabWidget.__class__)

    ### Check to see if a widget is better than the candidate we have?
    def checkCandidate(self, tabWidget, tabLabel, tabIndex, curIndex):
        if self.isTabValid(tabWidget):
            better = False
            if (self.sheetName!=None and
                str(tabLabel)!=str(self.sheetName)):
                return
            if self.candidate!=None:
                if self.candidate[2]==curIndex or tabIndex!=curIndex:
                    return
            self.candidate = (tabWidget, tabLabel, tabIndex, curIndex)
                
    ### Setup the candidate on the tab controller
    def setupCandidate(self, tabController):
        if self.candidate==None:
            candidate = StandardSingleCellSheetTab(tabController)
            tabController.setCurrentIndex(tabController.addTabWidget(candidate, self.sheetName))
            return candidate
        else:
            return self.candidate[0]

spreadsheetRegistry.registerSheet('StandardSingleCellSheetTab', StandardSingleCellSheetTab)

