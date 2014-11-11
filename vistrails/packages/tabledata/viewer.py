import os
from PyQt4 import QtCore, QtGui

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell, \
    SpreadsheetMode
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget

class TableToSpreadsheetMode(SpreadsheetMode):
    @classmethod
    def can_compute(cls):
        return SpreadsheetMode.can_compute()

    def compute_output(self, output_module, configuration=None):
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
        for row in xrange(table.rows):
            item = QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.EditRole, row)
            item.setFlags(QtCore.Qt.NoItemFlags)
            self.table.setItem(row, 0, item)

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
