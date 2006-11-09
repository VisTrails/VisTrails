from core.modules.basic_modules import File
from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui, QtSvg
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_controller import *
from packages.spreadsheet.spreadsheet_event import *
from packages.spreadsheet.spreadsheet_base import *

# A custom widget to show SVG files
class SVGCell(SpreadsheetCell):
    
    def compute(self):
        if self.hasInputFromPort("File"): fileValue = self.getInputFromPort("File")
        else: fileValue = None
        self.display(SVGCellWidget, (fileValue,))

### SVG Cell  widget type
class SVGCellWidget(QtSvg.QSvgWidget):
    def __init__(self, parent=None):
        QtSvg.QSvgWidget.__init__(self, parent)
        self.controlBarType = None

    def updateContents(self, inputPorts):
        (fileValue,) = inputPorts
        self.load(fileValue.name)


# A custom widget to displays SVG slide show
class SVGSplitter(Module):

    def compute(self):
        if self.hasInputFromPort("File"): fileValue = self.getInputFromPort("File")
        else: fileValue = None
        if fileValue:
            batchDisplayEvent = BatchDisplayCellEvent()
            batchDisplayEvent.vistrail = (self.vistrailName, self.currentVersion)
            f = open(fileValue.name, 'r')            
            for line in f.read().split('\n'):
                comps = line.split('|')
                if len(comps)==2:
                    e = DisplayCellEvent()        
                    e.sheetReference = StandardSingleCellSheetReference()
                    e.sheetReference.sheetName = comps[1]                    
                    e.cellType = SVGCellWidget
                    F = File()
                    from os.path import abspath, basename, dirname
                    F.name = dirname(abspath(fileValue.name))+'/'+basename(comps[0])
                    e.inputPorts = (F,)
                    batchDisplayEvent.displayEvents.append(e)
            f.close()
            spreadsheetController.postEventToSpreadsheet(batchDisplayEvent)
                    
