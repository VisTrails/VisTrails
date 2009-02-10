from cdat_cell import QCDATWidget
from core.modules.vistrails_module import (Module, ModuleError)
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from packages.spreadsheet.spreadsheet_event import DisplayCellEvent
from PyQt4 import QtCore, QtGui

class quickplot(Module):
    """hackiness to push a cdat plot to our spreadsheet.
       needs: QCDATWidget ref
              cdms2.open()d dataset
              blah this is out of date variable name"""

    def compute(self):
        args = []
        if not self.hasInputFromPort('dataset'):
            raise ModuleError(self, "'dataset' is mandatory.")
        if not self.hasInputFromPort('plot'):
            raise ModuleError(self, "'plot' is mandatory.")

        dataset = self.getInputFromPort('dataset')
        plotType = self.getInputFromPort('plot')

        ev = DisplayCellEvent()
        ev.vistrail = {'locator': None, 'version': -1, 'actions': []}
        ev.cellType = QCDATWidget
        ev.inputPorts = (dataset, 'ASD', plotType)
        QtCore.QCoreApplication.processEvents()
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
        spreadsheetWindow.displayCellEvent(ev)
