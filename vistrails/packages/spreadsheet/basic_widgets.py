from core import modules
from core.modules.vistrails_module import Module
from spreadsheet_base import *
from spreadsheet_controller import *
from spreadsheet_event import *

def widgetName():
    return 'Basic Widgets'

def registerWidget(reg, basicModules, basicWidgets):
    reg.addModule(SheetReference)
    reg.addInputPort(SheetReference, "MinRowCount", basicModules.Integer, True)
    reg.addInputPort(SheetReference, "MinColumnCount", basicModules.Integer, True)
    reg.addInputPort(SheetReference, "SheetName", basicModules.String, True)
    reg.addOutputPort(SheetReference, "self", SheetReference)
     
    reg.addModule(CellLocation)
    reg.addInputPort(CellLocation, "ColumnRowAddress", basicModules.String, True)
    reg.addInputPort(CellLocation, "Row", basicModules.Integer, True)
    reg.addInputPort(CellLocation, "Column", basicModules.Integer, True)
    reg.addInputPort(CellLocation, "SheetReference", SheetReference)
    reg.addOutputPort(CellLocation, "self", CellLocation)

    reg.addModule(SpreadsheetCell)
    reg.addInputPort(SpreadsheetCell, "Location", CellLocation)

    reg.addModule(SingleCellSheetReference)
    reg.addInputPort(SingleCellSheetReference, "SheetName", basicModules.String, True)
    reg.addOutputPort(SingleCellSheetReference, "self", SingleCellSheetReference)
     
class SheetReference(Module):
    
    def __init__(self):
        modules.vistrails_module.Module.__init__(self)
        self.sheetReference = None

    def compute(self):
        if self.sheetReference==None:
            self.sheetReference = StandardSheetReference()
        self.sheetReference.minimumRowCount = self.forceGetInputFromPort("MinRowCount", 1)
        self.sheetReference.minimumColumnCount = self.forceGetInputFromPort("MinColumnCount", 1)
        self.sheetReference.sheetName = self.forceGetInputFromPort("SheetName")

    def getSheetReference(self):
        return self.sheetReference

class CellLocation(Module):
    
    def __init__(self):
        modules.vistrails_module.Module.__init__(self)
        self.row = -1
        self.col = -1
        self.sheetReference = None

    def compute(self):
        ref = self.forceGetInputFromPort("SheetReference")
        if ref:
            self.sheetReference = ref.getSheetReference()
            
        if self.hasInputFromPort("Row") and self.hasInputFromPort("Column"):
            self.row = self.getInputFromPort("Row")-1
            self.col = self.getInputFromPort("Column")-1
        elif self.hasInputFromPort("ColumnRowAddress"):
            address = self.getInputFromPort("ColumnRowAddress")
            address = address.replace(' ', '').upper()
            if len(address)>1:
                self.col = ord(address[0])-ord('A')
                try:
                    self.row = int(address[1:])-1
                except:
                    self.row = -1

class SpreadsheetCell(Module):
    
    def display(self, cellType, inputPorts):
        e = DisplayCellEvent()        
        e.vistrail = (self.vistrailName, self.currentVersion)
        location = self.forceGetInputFromPort("Location")
        if location:
            e.row = location.row
            e.col = location.col
            e.sheetReference = location.sheetReference
        e.cellType = cellType
        e.inputPorts = inputPorts
        spreadsheetController.postEventToSpreadsheet(e)

class SingleCellSheetReference(SheetReference):
    
    def compute(self):
        if self.sheetReference==None:
            self.sheetReference = StandardSingleCellSheetReference()
        self.sheetReference.sheetName = self.forceGetInputFromPort("SheetName")

