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
# This file describes basic VisTrails Modules of the Spreadsheet package:
#   CellLocation
#   SheetReference
#   SingleCellSheetReference
#   SpreadsheetCell
################################################################################
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
from spreadsheet_base import (StandardSheetReference,
                              StandardSingleCellSheetReference)
from spreadsheet_controller import spreadsheetController
from spreadsheet_event import DisplayCellEvent
from PyQt4 import QtCore

################################################################################

def widgetName():
    """ widgetName() -> str
    Identify the name of the package
    
    """
    return 'Basic Widgets'

def registerWidget(reg, basicModules, basicWidgets):
    """ registerWidget(reg: module_registry, basicModules: package,
                       basicWidgets:package) -> None
    Register widgets with VisTrails registry
    
    """
    reg.add_module(SheetReference)
    reg.add_input_port(SheetReference, "MinRowCount", basicModules.Integer, True)
    reg.add_input_port(SheetReference, "MinColumnCount",
                       basicModules.Integer, True)
    reg.add_input_port(SheetReference, "SheetName", basicModules.String, True)
    reg.add_output_port(SheetReference, "self", SheetReference)
     
    reg.add_module(CellLocation)
    reg.add_input_port(CellLocation, "ColumnRowAddress",
                       basicModules.String, True)
    reg.add_input_port(CellLocation, "Row", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "Column", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "RowSpan", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "ColumnSpan", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "SheetReference", SheetReference)
    reg.add_output_port(CellLocation, "self", CellLocation)

    reg.add_module(SpreadsheetCell)
    reg.add_input_port(SpreadsheetCell, "Location", CellLocation)

    reg.add_module(SingleCellSheetReference)
    reg.add_input_port(SingleCellSheetReference, "SheetName",
                       basicModules.String, True)
    reg.add_output_port(SingleCellSheetReference, "self",
                        SingleCellSheetReference)
     
class SheetReference(Module):
    """
    SheetReference is a VisTrail Module that allows users to specify
    which sheet (page) to put the visualiation on. This is as
    well a wrapper to simply contain real sheet reference classes
    
    """
    def __init__(self):
        """ SheetReference() -> SheetReference
        Instantiate an empty SheetReference
        
        """
        Module.__init__(self)
        self.sheetReference = None

    def compute(self):
        """ compute() -> None
        Store information on input ports and ready to be passed on to whoever
        needs it
        
        """
        if self.sheetReference==None:
            self.sheetReference = StandardSheetReference()
        ref = self.sheetReference
        ref.minimumRowCount = self.forceGetInputFromPort("MinRowCount", 1)
        ref.minimumColumnCount = self.forceGetInputFromPort("MinColumnCount", 1)
        ref.sheetName = self.forceGetInputFromPort("SheetName")

    def getSheetReference(self):
        """ getSheetReference() -> subclass of StandardSheetReference
        Return the actual information stored in the SheetReference
        
        """
        return self.sheetReference

class CellLocation(Module):
    """
    CellLocation is a Vistrail Module that allow users to specify
    where to put a visualization on a sheet, i.e. row, column
    location
    
    """
    def __init__(self):
        """ CellLocation() -> CellLocation
        Instantiate an empty cell location, i.e. any available cell
        
        """
        Module.__init__(self)
        self.row = -1
        self.col = -1
        self.rowSpan = -1
        self.colSpan = -1
        self.sheetReference = None

    def compute(self):
        """ compute() -> None
        Translate input ports into (row, column) location
        
        """
        def set_row_col(row, col):
            try:
                self.col = ord(col)-ord('A')
                self.row = int(row)-1
            except:
                raise ModuleError(self, 'ColumnRowAddress format error')
            
        ref = self.forceGetInputFromPort("SheetReference")
        if ref:
            self.sheetReference = ref.getSheetReference()

        self.rowSpan = self.forceGetInputFromPort("RowSpan", -1)
        self.colSpan = self.forceGetInputFromPort("ColumnSpan", -1)
        if self.hasInputFromPort("Row") and self.hasInputFromPort("Column"):
            self.row = self.getInputFromPort("Row")-1
            self.col = self.getInputFromPort("Column")-1
        elif self.hasInputFromPort("ColumnRowAddress"):
            address = self.getInputFromPort("ColumnRowAddress")
            address = address.replace(' ', '').upper()
            if len(address)>1:
                if address[0] >= 'A' and address[0] <= 'Z':
                    set_row_col(address[1:], address[0])
                else:
                    set_row_col(address[:-1], address[-1])

class SpreadsheetCell(NotCacheable, Module):
    """
    SpreadsheetCell is a base class to other widget types. It provides
    a simple protocol to dispatch information to the spreadsheet
    cells. But it doesn't know how to display the information
    itself. That should be done by the specific widget type.
    
    """
    def __init__(self):
        """ SpreadsheetCell() -> SpreadsheetCell
        Initialize attributes
        
        """
        Module.__init__(self)
        self.location = None
    
    def overrideLocation(self, location):
        """ overrideLocation(location: CellLocation) -> None        
        Make the cell always use this location instead of reading from
        the port
        
        """
        self.location = location

    def createDisplayEvent(self, cellType, inputPorts):
        """ display(cellType: python type, iputPorts: tuple) -> None        
        Create a DisplayEvent with all the parameters from the cell
        locations and inputs
        
        """
        e = DisplayCellEvent()
        e.vistrail = self.moduleInfo
        if self.location:
            location = self.location
        else:
            location = self.forceGetInputFromPort("Location")
        if location:
            e.row = location.row
            e.col = location.col
            e.rowSpan = location.rowSpan
            e.colSpan = location.colSpan
            e.sheetReference = location.sheetReference
        e.cellType = cellType
        e.inputPorts = inputPorts
        return e
    
    def display(self, cellType, inputPorts):
        """ display(cellType: python type, iputPorts: tuple) -> None
        Dispatch the cellType to the spreadsheet with appropriate input data
        to display it

        Keyword arguments:
        cellType   --- widget type, this is truely a python type
        inputPorts --- a tuple of input data that cellType() will understand
        
        """
        if spreadsheetController.echoMode():
            return self.displayAndWait(cellType, inputPorts)
        e = self.createDisplayEvent(cellType, inputPorts)
        spreadsheetController.postEventToSpreadsheet(e)

    def displayAndWait(self, cellType, inputPorts):
        """ displayAndWait(cellType: python type, iputPorts: tuple)
        Send the message and wait for the cell to complete its movement
        constructed to return it

        Keyword arguments:
        cellType   --- widget type, this is truely a python type
        inputPorts --- a tuple of input data that cellType() will understand
        
        """
        e = self.createDisplayEvent(cellType, inputPorts)
        QtCore.QCoreApplication.processEvents()
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
        if spreadsheetWindow.echoMode == False:
            spreadsheetWindow.configShow(show=True)
        return spreadsheetWindow.displayCellEvent(e)

class SingleCellSheetReference(SheetReference):
    """
    SingleCellSheetReference is a wrapper of StandardSingleCellSheetReference
    that will allow users to dedicate a whole sheet to view a single
    visualization by pass all other sheet control widgets.
    
    """
    def compute(self):
        """ compute() -> None
        Store information from input ports into internal structure
        
        """
        if self.sheetReference==None:
            self.sheetReference = StandardSingleCellSheetReference()
        self.sheetReference.sheetName = self.forceGetInputFromPort("SheetName")

