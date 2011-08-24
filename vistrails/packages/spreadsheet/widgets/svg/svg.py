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
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
import shutil
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
        self.fileSrc = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents of the SVG widget with a new file name
        
        """
        (fileValue,) = inputPorts
        self.svgWidget.load(fileValue.name)
        self.fileSrc = fileValue.name
        
    def dumpToFile(self, filename):
        if self.fileSrc is not None:
            shutil.copyfile(self.fileSrc, filename)

    def saveToPDF(self):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        b_rect = self.svgWidget.contentsRect()
        printer.setPaperSize(QtCore.QSizeF(b_rect.width(), b_rect.height()),
                             QtGui.QPrinter.Point)
        painter = QtGui.QPainter(printer)
        self.svgWidget.render(painter, QtCore.QRectF(), b_rect)
        painter.end()

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
                    
class SVGSaveAction(QtGui.QAction):
    """
    ImageViewerSaveAction is the action to save the image to file
    
    """
    def __init__(self, parent=None):
        """ ImageViewerSaveAction(parent: QWidget) -> ImageViewerSaveAction
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/save.png"),
                               "&Save svg as...",
                               parent)
        self.setStatusTip("Save svg to file")
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        
        fn = QtGui.QFileDialog.getSaveFileName(None, "Save svg as...",
                                               "screenshot.png",
                                               "SVG (*.svg);;PDF files (*.pdf)")
        if not fn:
            return
        if fn.endsWith(QtCore.QString("svg"), QtCore.Qt.CaseInsensitive):
            cellWidget.dumpToFile(str(fn))
        elif fn.endsWith(QtCore.QString("pdf"), QtCore.Qt.CaseInsensitive):
            cellWidget.saveToPDF(str(fn))
        
class SVGToolBar(QCellToolBar):
    """
    ImageViewerToolBar derives from CellToolBar to give the ImageViewerCellWidget
    a customizable toolbar
    
    """
    def createToolBar(self):
        """ createToolBar() -> None
        This will get call initiallly to add customizable widgets
        
        """
        self.appendAction(SVGSaveAction(self))
