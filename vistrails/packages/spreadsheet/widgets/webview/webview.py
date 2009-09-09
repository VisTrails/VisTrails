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

############################################################################
# web browser view implementation
############################################################################

from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui, QtWebKit
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget

############################################################################

class WebViewCell(SpreadsheetCell):
    """
    WebViewCell is a custom Module to view URLs using WebKit
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the URL to the spreadsheet
        """
        if self.hasInputFromPort("url"):
            urlValue = self.getInputFromPort("url")
            fileValue = None
        elif self.hasInputFromPort("file"):
            fileValue = self.getInputFromPort("file")
            urlValue = None
        else:
            fileValue = None
            urlValue = None
        self.display(WebViewCellWidget, (urlValue, fileValue))

class WebViewCellWidget(QCellWidget):
    """
    WebViewCellWidget has a QTextBrowser to display HTML files
    
    """
    def __init__(self, parent=None):
        """ WebViewCellWidget(parent: QWidget) -> WebViewCellWidget
        Create a rich text cell without a toolbar
        
        """
        QCellWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.browser = QtWebKit.QWebView()
        self.layout().addWidget(self.browser)
        self.browser.setMouseTracking(True)
        # self.browser.controlBarType = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        (urlValue, fileValue) = inputPorts
        if urlValue:
            url = QtCore.QUrl(urlValue)
            self.browser.load(url)
        elif fileValue:
            url = QtCore.QUrl.fromLocalFile(fileValue.name)
            self.browser.load(url)
        else:
            self.browser.setHtml("No HTML file is specified!")
