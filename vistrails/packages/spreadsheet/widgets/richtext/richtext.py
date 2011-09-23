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
# Richtext widgets implementation
################################################################################
from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
import shutil
import os.path
################################################################################

class RichTextCell(SpreadsheetCell):
    """
    RichTextCell is a custom Module to view HTML files
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the HTML contents to the spreadsheet
        """
        if self.hasInputFromPort("File"):
            fileValue = self.getInputFromPort("File")
        else:
            fileValue = None
        self.cellWidget = self.displayAndWait(RichTextCellWidget, (fileValue,))

class RichTextCellWidget(QCellWidget):
    """
    RichTextCellWidget has a QTextBrowser to display HTML files
    
    """
    def __init__(self, parent=None):
        """ RichTextCellWidget(parent: QWidget) -> RichTextCellWidget
        Create a rich text cell without a toolbar
        
        """
        QCellWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.browser = QtGui.QTextBrowser()
        self.layout().addWidget(self.browser)
        self.browser.setMouseTracking(True)
        self.browser.controlBarType = None
        self.fileSrc = None
        
    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        self.fileSrc = None
        (fileValue,) = inputPorts
        if fileValue:
            try:
                fi = open(fileValue.name, "r")
            except IOError:
                self.browser.setText("Cannot load the HTML file!")
                return            
            self.browser.setHtml(fi.read())
            fi.close()
            self.fileSrc = fileValue.name
        else:
            self.browser.setText("No HTML file is specified!")
            
    def dumpToFile(self, filename):
        """ dumpToFile(filename) -> None 
        It will generate a screenshot of the cell contents and dump to filename.
        It will also create a copy of the original text file used with 
        filename's basename and the original extension.
        """
        if self.fileSrc is not None:
            (_, s_ext) = os.path.splitext(self.fileSrc)
            (f_root, f_ext) = os.path.splitext(filename)
            ori_filename = f_root + s_ext
            shutil.copyfile(self.fileSrc, ori_filename)
        QCellWidget.dumpToFile(self,filename)
            
    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)
        