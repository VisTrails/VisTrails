from PyQt4 import QtCore, QtGui

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget


class TableCell(SpreadsheetCell):
    """Shows a table in a spreadsheet cell.
    """
    _input_ports = [('table', '(org.vistrails.vistrails.tabledata:Table)')]

    def compute(self):
        table = self.getInputFromPort('table')
        self.cellWidget = self.displayAndWait(TableCellWidget, (table,))


class TableCellWidget(QCellWidget):
    def __init__(self, parent=None):
        QCellWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()

        self.table = QtGui.QTableWidget()

        scrollarea = QtGui.QScrollArea(self)
        scrollarea.setWidgetResizable(True)
        scrollarea.setWidget(self.table)
        layout.addWidget(scrollarea)

        self.setLayout(layout)

    def updateContents(self, inputPorts):
        table, = inputPorts

        self.table.setColumnCount(table.columns)
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
                self.table.setItem(row, col, item)

        if table.names is not None:
            self.table.setHorizontalHeaderLabels(table.names)


_modules = [TableCell]
