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

from PyQt4 import QtCore, QtGui, QtWebKit
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget, \
    QCellToolBar
import os
import webbrowser
############################################################################

class WebViewCell(SpreadsheetCell):
    """
    WebViewCell is a custom Module to view URLs using WebKit
    
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
        self.displayAndWait(WebViewCellWidget, (urlValue, fileValue))

class WebViewCellWidget(QCellWidget):
    """
    WebViewCellWidget has a QTextBrowser to display HTML files
    
    """
    save_formats = QCellWidget.save_formats + ["HTML files (*.html)"]

    def __init__(self, parent=None):
        """ WebViewCellWidget(parent: QWidget) -> WebViewCellWidget
        Create a rich text cell without a toolbar
        
        """
        QCellWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.toolBarType = WebViewCellToolBar
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.browser = QtWebKit.QWebView()
        self.layout().addWidget(self.browser)
        self.browser.setMouseTracking(True)
        self.urlSrc = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        self.urlSrc = None
        (urlValue, fileValue) = inputPorts
        if urlValue:
            url = QtCore.QUrl(urlValue)
            self.browser.load(url)
            self.urlSrc = url
        elif fileValue:
            url = QtCore.QUrl.fromLocalFile(fileValue.name)
            self.browser.load(url)
            self.urlSrc = url
        else:
            self.browser.setHtml("No HTML file is specified!")

    def dumpToFile(self, filename):
        if os.path.splitext(filename)[1].lower() in ('.html', '.htm'):
            with open(filename, 'wb') as fp:
                fp.write(self.browser.page().mainFrame().toHtml())
        else:
            super(WebViewCellWidget, self).dumpToFile(filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)


class OpenInBrowserAction(QtGui.QAction):
    def __init__(self, parent):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/new-window.png"),
                               "Open in &Browser",
                               parent)
        self._view = None
        self.setEnabled(False)
        self.setStatusTip("Open this page in the system web browser")

    def updateStatus(self, info):
        self._view = info[3]
        self.setEnabled(self._view is not None)

    def triggeredSlot(self, checked=False):
        if self._view is not None:
            webbrowser.open(self._view.browser.url().toString())


class WebViewCellToolBar(QCellToolBar):
    def createToolBar(self):
        self.appendAction(OpenInBrowserAction(self))
        self.addAnimationButtons()
