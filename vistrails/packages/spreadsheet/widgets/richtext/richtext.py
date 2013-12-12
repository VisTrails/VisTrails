###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
import os
from PyQt4 import QtGui
from PyQt4.QtCore import QUrl
from PyQt4.QtXmlPatterns import QXmlQuery

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.modules.vistrails_module import ModuleError
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget
################################################################################

class RichTextCell(SpreadsheetCell):
    """
    RichTextCell is a custom Module to view HTML files

    """
    def compute(self):
        """ compute() -> None
        Dispatch the HTML contents to the spreadsheet
        """
        filename = self.getInputFromPort("File").name

        text_format = self.getInputFromPort("Format")
        with open(filename, 'rb') as fp:
            if text_format == 'html':
                html = fp.read()
            elif text_format == 'rtf':
                try:
                    py_import('pyth', {'pip': 'pyth'})
                except ImportError:
                    raise ModuleError(self, "'rtf' format requires the pyth "
                                      "Python library")
                else:
                    from pyth.plugins.rtf15.reader import Rtf15Reader
                    from pyth.plugins.xhtml.writer import XHTMLWriter
                    doc = Rtf15Reader.read(fp)
                    html = XHTMLWriter.write(doc).read().decode('utf-8')
            else:
                raise ModuleError(self, "'%s' format is unknown" % text_format)

        self.cellWidget = self.displayAndWait(RichTextCellWidget, (html,))


class XSLCell(SpreadsheetCell):
    """
    XSLCell is a custom Module to render an XML file via an XSL stylesheet

    """
    def compute(self):
        """ compute() -> None
        Render the XML tree and display it on the spreadsheet
        """
        xml = self.getInputFromPort('XML').name
        xsl = self.getInputFromPort('XSL').name

        query = QXmlQuery(QXmlQuery.XSLT20)
        query.setFocus(QUrl.fromLocalFile(os.path.join(os.getcwd(), xml)))
        query.setQuery(QUrl.fromLocalFile(os.path.join(os.getcwd(), xsl)))
        html = query.evaluateToString()

        self.cellWidget = self.displayAndWait(RichTextCellWidget, (html,))


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
        self.html = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new HTML document

        """
        (self.html,) = inputPorts
        self.browser.setHtml(self.html)

    def dumpToFile(self, filename):
        """ dumpToFile(filename) -> None
        It will generate a screenshot of the cell contents and dump to filename.
        It will also create a copy of the original text file used with
        filename's basename and the original extension.
        """
        if self.html is not None:
            basename, ext = os.path.splitext(filename)
            with open(basename + '.html', 'wb') as fp:
                fp.write(self.html.encode('utf-8'))
        QCellWidget.dumpToFile(self,filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)
