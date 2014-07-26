###############################################################################
##
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
from vistrails.core.configuration import ConfigField, \
    get_vistrails_configuration
from vistrails.core.modules.output_modules import OutputMode, OutputModeConfig
from vistrails.core.modules.vistrails_module import Module, NotCacheable, ModuleError
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
    reg.add_output_port(SheetReference, "value", SheetReference)

    reg.add_module(CellLocation)
    reg.add_input_port(CellLocation, "ColumnRowAddress",
                       basicModules.String, True)
    reg.add_input_port(CellLocation, "Row", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "Column", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "RowSpan", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "ColumnSpan", basicModules.Integer, True)
    reg.add_input_port(CellLocation, "SheetReference", SheetReference)
    reg.add_output_port(CellLocation, "value", CellLocation)

    reg.add_module(SpreadsheetCell)
    reg.add_input_port(SpreadsheetCell, "Location", CellLocation)
    reg.add_output_port(SpreadsheetCell, "Widget", SpreadsheetCell)

    reg.add_module(SingleCellSheetReference)
    reg.add_input_port(SingleCellSheetReference, "SheetName",
                       basicModules.String, True)
    reg.add_output_port(SingleCellSheetReference, "value",
                        SingleCellSheetReference)
     
class SheetReference(Module):
    """
    SheetReference is a VisTrail Module that allows users to specify
    which sheet (page) to put the visualiation on. This is as
    well a wrapper to simply contain real sheet reference classes
    
    """
    def compute(self):
        """ compute() -> None
        Store information on input ports and ready to be passed on to whoever
        needs it
        
        """
        ref = StandardSheetReference()
        ref.minimumRowCount = self.force_get_input("MinRowCount", 1)
        ref.minimumColumnCount = self.force_get_input("MinColumnCount", 1)
        ref.sheetName = self.force_get_input("SheetName")

        self.set_output('value', ref)

class CellLocation(Module):
    """
    CellLocation is a Vistrail Module that allow users to specify
    where to put a visualization on a sheet, i.e. row, column
    location
    
    """
    class Location(object):
        def __init__(self):
            self.row = -1
            self.col = -1
            self.rowSpan = -1
            self.colSpan = -1
            self.sheetReference = None

    def compute(self):
        """ compute() -> None
        Translate input ports into (row, column) location
        
        """
        loc = CellLocation.Location()

        def set_row_col(row, col):
            try:
                loc.col = ord(col) - ord('A')
                loc.row = int(row) - 1
            except (TypeError, ValueError):
                raise ModuleError(self, 'ColumnRowAddress format error')

        ref = self.force_get_input("SheetReference")
        if ref:
            loc.sheetReference = ref

        loc.rowSpan = self.force_get_input("RowSpan", -1)
        loc.colSpan = self.force_get_input("ColumnSpan", -1)
        if self.has_input("Row") and self.has_input("Column"):
            loc.row = self.get_input("Row")-1
            loc.col = self.get_input("Column")-1
        elif self.has_input("ColumnRowAddress"):
            address = self.get_input("ColumnRowAddress")
            address = address.replace(' ', '').upper()
            if len(address) > 1:
                if address[0] >= 'A' and address[0] <= 'Z':
                    set_row_col(address[1:], address[0])
                else:
                    set_row_col(address[:-1], address[-1])

        self.set_output('value', loc)

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
            location = self.force_get_input("Location")
        if location:
            e.row = location.row
            e.col = location.col
            e.rowSpan = location.rowSpan
            e.colSpan = location.colSpan
            e.sheetReference = location.sheetReference
        e.cellType = cellType
        e.inputPorts = inputPorts
        return e

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
        self.cellWidget = spreadsheetWindow.displayCellEvent(e)
        self.set_output('Widget', self.cellWidget)
        return self.cellWidget

    display = displayAndWait

class SpreadsheetModeConfig(OutputModeConfig):
    mode_type = "spreadsheet"
    _fields = [ConfigField('row', None, int),
               ConfigField('col', None, int),
               ConfigField('sheetName', None, str),
               ConfigField('sheetRowCount', None, int),
               ConfigField('sheetColCount', None, int),
               ConfigField('rowSpan', None, int),
               ConfigField('colSpan', None, int)]

class SpreadsheetMode(OutputMode):
    mode_type = "spreadsheet"
    priority = 3
    config_cls = SpreadsheetModeConfig

    @classmethod
    def can_compute(cls):
        if get_vistrails_configuration().batch:
            return False
        return True

    def create_display_event(self, output_module, configuration,
                             cell_cls, input_ports):
        """create_display_event(output_module: Module,
                                configuration: OutputModeConfig,
                                cell_cls: class,
                                input_ports: tuple) -> None
        Create a DisplayEvent with all the parameters from the cell
        locations and inputs

        """
        e = DisplayCellEvent()
        if configuration is not None:
            e.row = configuration['row']
            e.col = configuration['col']
            if (configuration['sheetName'] or configuration['sheetRowCount'] or
                configuration['sheetColCount']):
                ref = StandardSheetReference()
                if configuration['sheetName']:
                    ref.sheetName = configuration['sheetName']
                if configuration['sheetRowCount']:
                    ref.minimumRowCount = configuration['sheetRowCount']
                if configuration['sheetColCount']:
                    ref.minimumColumnCount = configuration['sheetColCount']
                e.sheetReference = ref
            e.rowSpan = configuration['rowSpan']
            e.colSpan = configuration['colSpan']
        e.vistrail = output_module.moduleInfo
        e.cellType = cell_cls
        e.inputPorts = input_ports
        return e

    def display(self, output_module, configuration, cell_type, input_ports):
        """display(output_module: Module,
                   configuration: OutputModeConfig,
                   cell_cls: class,
                   input_ports: tuple) -> None
        Dispatch the cellType to the spreadsheet with appropriate input data
        to display it

        """
        if spreadsheetController.echoMode():
            return self.display_and_wait(output_module, configuration,
                                         cell_type, input_ports)
        e = self.create_display_event(cell_type, input_ports)
        spreadsheetController.postEventToSpreadsheet(e)

    def display_and_wait(self, output_module, configuration, cell_type,
                         input_ports):
        """display_and_wait(output_module: Module,
                            configuration: OutputModeConfig,
                            cell_cls: class,
                            input_ports: tuple) -> None
        Send the message and wait for the cell to complete its movement
        constructed to return it

        """
        e = self.create_display_event(output_module, configuration,
                                      cell_type, input_ports)
        QtCore.QCoreApplication.processEvents()
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
        if spreadsheetWindow.echoMode == False:
            spreadsheetWindow.configShow(show=True)
        cell = spreadsheetWindow.displayCellEvent(e)
        if cell is not None:
            cell.set_output_module(output_module, configuration)
        return cell


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
        ref = StandardSingleCellSheetReference()
        ref.sheetName = self.force_get_input("SheetName")

        self.set_output('value', ref)
