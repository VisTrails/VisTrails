############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
# SVG widgets implementation
################################################################################
from core.modules.basic_modules import File
from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui, QtSvg
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_base import StandardSingleCellSheetReference
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from packages.spreadsheet.spreadsheet_event import (DisplayCellEvent,
                                                    BatchDisplayCellEvent)
from packages.spreadsheet.spreadsheet_cell import QCellWidget

################################################################################

class SVGCell(SpreadsheetCell):
    """
    SVGCell is a VisTrails Module that can display SVG files

    """
    def compute(self):
        """ compute() -> None
        Dispatch SVG file into the spreadshet for display
        """
        if self.hasInputFromPort("File"):
            window = spreadsheetController.findSpreadsheetWindow()
            file_to_display = self.getInputFromPort("File")
            fileValue = window.file_pool.make_local_copy(file_to_display.name)
        else:
            fileValue = None
        self.display(SVGCellWidget, (fileValue,))

### SVG Cell  widget type
class SVGCellWidget(QCellWidget):
    """
    SVGCellWidget derives from QSvgWidget to dispay SVG contents and
    received SVG file from the SVGCell
    
    """
    def __init__(self, parent=None):
        """ SVGCellWidget(parent: QWidget) -> SVGCellWidget
        Create a SVGCellWidget without any toolbar
        """
        QCellWidget.__init__(self, parent)        
        self.setLayout(QtGui.QVBoxLayout(self))

        self.svgWidget = QtSvg.QSvgWidget()
        self.layout().addWidget(self.svgWidget)
        
        self.controlBarType = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents of the SVG widget with a new file name
        
        """
        (fileValue,) = inputPorts
        self.svgWidget.load(fileValue.name)


# A custom widget to displays SVG slide show
class SVGSplitter(Module):
    """
    SVGSplitter is a special Module that can dispatch multiple SVG
    files to the spreadsheet for displaying a slideshow
    
    """
    def compute(self):
        """ compute() -> None
        Use BatchDisplayCellEvent to display a serie of SVG files
        
        """
        if self.hasInputFromPort("File"):
            fileValue = self.getInputFromPort("File")
        else:
            fileValue = None
        if fileValue:
            batchDisplayEvent = BatchDisplayCellEvent()
            # FIXME: Will this work? there should be no
            # self.currentVersion in the module (there is a
            # self.version)
            batchDisplayEvent.vistrail = (self.vistrailName,
                                          self.currentVersion)
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
                    F.name = (dirname(abspath(fileValue.name))+
                              '/'+basename(comps[0]))
                    e.inputPorts = (F,)
                    batchDisplayEvent.displayEvents.append(e)
            f.close()
            spreadsheetController.postEventToSpreadsheet(batchDisplayEvent)
                    
