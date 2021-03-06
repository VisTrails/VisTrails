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

############################################################################
# web browser view implementation
############################################################################
from __future__ import division

from PyQt4 import QtCore, QtGui, QAxContainer
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget, \
    QCellToolBar
import os
import shutil
############################################################################

class IECell(SpreadsheetCell):
    """
    IECell is a custom Module to view URLs using the IE ActiveX Control
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the URL to the spreadsheet
        """
        if self.has_input("url"):
            urlValue = self.get_input("url")
            fileValue = None
        elif self.has_input("file"):
            fileValue = self.get_input("file")
            urlValue = None
        else:
            fileValue = None
            urlValue = None
        self.displayAndWait(IECellWidget, (urlValue, fileValue))

class IECellWidget(QCellWidget):
    """
    IECellWidget has a QAxContainer to display supported documents
    
    """
    save_formats = QCellWidget.save_formats + ["HTML files (*.html)"]

    def __init__(self, parent=None):
        """ IECellWidget(parent: QWidget) -> IECellWidget
        Create a ActiveX Container pointing to the IE Cell
        
        """
        QCellWidget.__init__(self, parent)
        vbox = QtGui.QVBoxLayout(self)
        vbox.setMargin(0)
        self.setLayout(vbox)
        self.browser = QAxContainer.QAxWidget(self)
        self.browser.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.browser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        vbox.addWidget(self.browser)
        self.urlSrc = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        self.urlSrc = None
        (urlValue, fileValue) = inputPorts
        if urlValue:
            self.urlSrc = QtCore.QUrl(urlValue)
        elif fileValue:
            self.urlSrc = QtCore.QUrl.fromLocalFile(fileValue.name)
        if self.urlSrc!=None:
            self.browser.dynamicCall('Navigate(const QString&)', self.urlSrc)
        else:
            self.browser.dynamicCall('Navigate(const QString&)', 'about:blank')

    def dumpToFile(self, filename):
        if os.path.splitext(filename)[1].lower() in ('.html', '.htm'):
            if self.urlSrc is not None:
                shutil.copyfile(str(self.urlSrc.toLocalFile()), filename)
        else:
            super(IECellWidget, self).dumpToFile(filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)
