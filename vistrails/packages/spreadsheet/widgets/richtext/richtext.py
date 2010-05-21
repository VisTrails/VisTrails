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
################################################################################
# Richtext widgets implementation
################################################################################
from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
import shutil
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
        self.display(RichTextCellWidget, (fileValue,))

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
        if self.fileSrc is not None:
            shutil.copyfile(self.fileSrc, filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)
        