############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
from PyQt4 import QtCore, QtGui, QAxContainer
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
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
        if self.hasInputFromPort("url"):
            urlValue = self.getInputFromPort("url")
            fileValue = None
        elif self.hasInputFromPort("file"):
            fileValue = self.getInputFromPort("file")
            urlValue = None
        else:
            fileValue = None
            urlValue = None
        self.display(IECellWidget, (urlValue, fileValue))

class IECellWidget(QCellWidget):
    """
    IECellWidget has a QAxContainer to display supported documents
    
    """
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
            self.browser.dynamicCall('Navigate(const QString&)', self.urlSrc.toString())
        else:
            self.browser.dynamicCall('Navigate(const QString&)', QtCore.QString('about:blank'))

    def dumpToFile(self, filename):
        if self.urlSrc is not None:
            shutil.copyfile(str(self.urlSrc.toLocalFile()), filename)
            
    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)
