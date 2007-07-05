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
    reg.addModule(SheetReference)
    reg.addInputPort(SheetReference, "MinRowCount", basicModules.Integer, True)
    reg.addInputPort(SheetReference, "MinColumnCount",
                     basicModules.Integer, True)
    reg.addInputPort(SheetReference, "SheetName", basicModules.String, True)
    reg.addOutputPort(SheetReference, "self", SheetReference)
     
    reg.addModule(CellLocation)
    reg.addInputPort(CellLocation, "ColumnRowAddress",
                     basicModules.String, True)
    reg.addInputPort(CellLocation, "Row", basicModules.Integer, True)
    reg.addInputPort(CellLocation, "Column", basicModules.Integer, True)
    reg.addInputPort(CellLocation, "SheetReference", SheetReference)
    reg.addOutputPort(CellLocation, "self", CellLocation)

    reg.addModule(SpreadsheetCell)
    reg.addInputPort(SpreadsheetCell, "Location", CellLocation)

    reg.addModule(SingleCellSheetReference)
    reg.addInputPort(SingleCellSheetReference, "SheetName",
                     basicModules.String, True)
    reg.addOutputPort(SingleCellSheetReference, "self",
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
    
    def display(self, cellType, inputPorts):
        """ display(cellType: python type, iputPorts: tuple) -> None
        Dispatch the cellType to the spreadsheet with appropriate input data
        to display it

        Keyword arguments:
        cellType   --- widget type, this is truely a python type
        inputPorts --- a tuple of input data that cellType() will understand
        
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
            e.sheetReference = location.sheetReference
        e.cellType = cellType
        e.inputPorts = inputPorts
        spreadsheetController.postEventToSpreadsheet(e)

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

