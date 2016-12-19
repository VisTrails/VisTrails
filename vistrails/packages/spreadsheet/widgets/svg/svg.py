###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from vistrails.core.modules.basic_modules import PathObject
from vistrails.core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui, QtSvg
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_base import StandardSingleCellSheetReference
from vistrails.packages.spreadsheet.spreadsheet_controller import spreadsheetController
from vistrails.packages.spreadsheet.spreadsheet_event import (DisplayCellEvent,
                                                    BatchDisplayCellEvent)
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
import os
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
        if self.has_input("File"):
            window = spreadsheetController.findSpreadsheetWindow()
            file_to_display = self.get_input("File")
            fileValue = window.file_pool.make_local_copy(file_to_display.name)
        else:
            fileValue = None
        self.displayAndWait(SVGCellWidget, (fileValue,))

### SVG Cell  widget type
class SVGCellWidget(QCellWidget):
    """
    SVGCellWidget derives from QSvgWidget to dispay SVG contents and
    received SVG file from the SVGCell
    
    """
    save_formats = (QCellWidget.save_formats +
                    ["Scalable Vector Graphics (*.svg)"])

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
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.svg':
            if self.fileSrc is not None:
                shutil.copyfile(self.fileSrc, filename)
        else:
            super(SVGCellWidget, self).dumpToFile(filename)

    def saveToPDF(self, filename):
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
        if self.has_input("File"):
            fileValue = self.get_input("File")
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
                    from os.path import abspath, basename, dirname, join
                    F = PathObject(join(dirname(abspath(fileValue.name)),
                                        basename(comps[0])))
                    e.inputPorts = (F,)
                    batchDisplayEvent.displayEvents.append(e)
            f.close()
            spreadsheetController.postEventToSpreadsheet(batchDisplayEvent)
