###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
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

from __future__ import division

import os
from PyQt4 import QtCore, QtGui

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell, \
    SpreadsheetMode
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget

class TableToSpreadsheetMode(SpreadsheetMode):
    def compute_output(self, output_module, configuration):
        table = output_module.get_input('value')
        self.display_and_wait(output_module, configuration,
                              TableCellWidget, (table,))

class TableCell(SpreadsheetCell):
    """Shows a table in a spreadsheet cell.
    """
    _input_ports = [('table', '(org.vistrails.vistrails.tabledata:Table)')]

    def compute(self):
        table = self.get_input('table')
        self.displayAndWait(TableCellWidget, (table,))


class TableCellWidget(QCellWidget):
    save_formats = QCellWidget.save_formats + ["HTML files (*.html)"]

    def __init__(self, parent=None):
        QCellWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.table = QtGui.QTableWidget()

        scrollarea = QtGui.QScrollArea(self)
        scrollarea.setWidgetResizable(True)
        scrollarea.setWidget(self.table)
        layout.addWidget(scrollarea)

        self.setLayout(layout)

    def updateContents(self, inputPorts):
        table, = inputPorts
        self.orig_table = table

        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setColumnCount(table.columns + 1)
        self.table.setRowCount(table.rows)

        for row in xrange(table.rows):
            item = QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.EditRole, row)
            item.setFlags(QtCore.Qt.NoItemFlags)
            self.table.setItem(row, 0, item)

        try:
            for col in xrange(table.columns):
                column = table.get_column(col)
                for row in xrange(table.rows):
                    elem = column[row]
                    if isinstance(elem, bytes):
                        elem = elem.decode('utf-8', 'replace')
                    elif not isinstance(elem, unicode):
                        elem = unicode(elem)
                    item = QtGui.QTableWidgetItem(elem)
                    item.setFlags(QtCore.Qt.ItemIsEnabled |
                                  QtCore.Qt.ItemIsSelectable)
                    self.table.setItem(row, col + 1, item)
        except:
            self.table.setColumnCount(1)
            raise

        if table.names is not None:
            names = table.names
        else:
            names = ['col %d' % n for n in xrange(table.columns)]
        self.table.setHorizontalHeaderLabels(['row' ] + names)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.table.resizeColumnsToContents()

    def write_html(self):
        document = ['<!DOCTYPE html>\n'
                    '<html>\n  <head>\n'
                    '    <meta http-equiv="Content-type" content="text/html; '
                            'charset=utf-8" />\n'
                    '    <title>Exported table</title>\n'
                    '    <style type="text/css">\n'
                    'table { border-collapse: collapse; }\n'
                    'td, th { border: 1px solid black; }\n'
                    '    </style>\n'
                    '  </head>\n  <body>\n    <table>\n']
        table = self.orig_table
        if table.names is not None:
            names = table.names
        else:
            names = ['col %d' % n for n in xrange(table.columns)]
        document.append('<tr>\n')
        document.extend('  <th>%s</th>\n' % name for name in names)
        document.append('</tr>\n')
        columns = [table.get_column(col) for col in xrange(table.columns)]
        for row in xrange(table.rows):
            document.append('<tr>\n')
            for col in xrange(table.columns):
                elem = columns[col][row]
                if isinstance(elem, bytes):
                    elem = elem.decode('utf-8', 'replace')
                elif not isinstance(elem, unicode):
                    elem = unicode(elem)
                document.append('  <td>%s</td>\n' % elem)
            document.append('</tr>\n')
        document.append('    </table>\n  </body>\n</html>\n')

        return ''.join(document)

    def dumpToFile(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.html', '.htm'):
            with open(filename, 'wb') as fp:
                fp.write(self.write_html())
        else:
            super(TableCellWidget, self).dumpToFile(filename)

    def saveToPDF(self, filename):
        document = QtGui.QTextDocument()
        document.setHtml(self.write_html())
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        document.print_(printer)


_modules = [TableCell]
