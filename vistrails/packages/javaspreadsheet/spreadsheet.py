from itertools import izip, repeat

from java.awt import Color

from javax.swing import (JPanel, JFrame, JScrollPane, JTable, JTabbedPane,
                         AbstractCellEditor)
from javax.swing.table import (DefaultTableModel, DefaultTableCellRenderer,
                               TableCellEditor)

from jtablerowheader import JTableRowHeader


class Cell(JPanel):
    def __init__(self, observer):
        self.observer = observer
        self.setBackground(Color.white)

    # @Override
    def paint(self, g):
        JPanel.paint(self, g)
        if self.observer is not None:
            self.observer.repainted(self)


class SpreadsheetModel(DefaultTableModel):
    """The model for the table, holding all the cells.
    """
    def __init__(self, rows, columns):
        self.nbRows = rows
        self.nbColumns = columns
        self.cells = {}
        self.cellpositions = {}

    # @Override
    def getRowCount(self):
        return self.nbRows

    # @Override
    def getColumnCount(self):
        return self.nbColumns

    # @Override
    def getValueAt(self, row, column):
        try:
            return self.cells[(row, column)]
        except KeyError:
            c = Cell(self)
            self.cells[(row, column)] = c
            self.cellpositions[c] = (row, column)
            return c

    def cellExists(self, row, column):
        try:
            return self.cells[(row, column)] and True
        except KeyError:
            return False

    # @Override
    def setValueAt(self, value, row, column):
        self.cells[(row, column)] = value

    # @Override
    def getColumnName(self, column):
        name = ""
        column += 1
        while column > 0:
            column -= 1
            name = chr((column % 26) + ord('A')) + name
            column /= 26
        return name

    def repainted(self, cell):
        pos = self.cellpositions[cell]
        self.fireTableCellUpdated(pos[1], pos[0])


class SpreadsheetRenderer(DefaultTableCellRenderer):
    # @Override
    def getTableCellRendererComponent(self, table, value, isSelected, hasFocus,
                                      row, column):
        return value


class SpreadsheetEditor(AbstractCellEditor, TableCellEditor):
    def __init__(self):
        super(SpreadsheetEditor, self).__init__()
        self.cell = None

    # @Override
    def getCellEditorValue(self):
        return self.cell

    # @Override
    def getTableCellEditorComponent(self, table, value, isSelected,
                                    row, column):
        self.cell = value
        return self.cell


class CustomTable(JTable):
    def __init__(self, model):
        super(CustomTable, self).__init__(model)
        self.renderer = SpreadsheetRenderer()
        self.editor = SpreadsheetEditor()
        self.setRowHeight(100)

    # @Override
    def getDefaultRenderer(self, c):
        return self.renderer

    # @Override
    def getDefaultEditor(self, columnClass):
        return self.editor


class Sheet(JScrollPane):
    """A sheet containing a table.
    """
    def __init__(self):
        self.model = SpreadsheetModel(2, 3)
        self.table = CustomTable(self.model)
        self.setViewportView(self.table)
        self.setColumnHeaderView(self.table.getTableHeader())
        self.setRowHeaderView(JTableRowHeader(self.table))

    def getCell(self, location=None):
        # Locate the requested cell
        row, column = None, None
        if location:
            row = location.row
            column = location.column

        # Should we grow the table?
        newrowcount, newcolumncount = None, None
        if row and row >= self.model.getRowCount():
            newrowcount = row+1
        if column and column >= self.model.getColumnCount():
            newcolumncount = column+1
        if newrowcount or newcolumncount:
            self.model.changeSize(
                    newrowcount or self.model.getRowCount(),
                    newcolumncount or self.model.getColumnCount())

        row, column = Sheet.findCell(self.model, row, column)

        return self.model.getValueAt(row, column)

    @staticmethod
    def findCell(model, row, column):
        if row and column:
            return row, column
        rows = xrange(0, model.getRowCount())
        columns = xrange(0, model.getColumnCount())
        if row and not column:
            cells = izip(repeat(row), columns)
            first = row, 0
        elif column and not row:
            cells = izip(rows, repeat(column))
            first = 0, column
        else:
            cells = izip(rows, columns)
            first = 0, 0
        for row, column in cells:
            if not model.cellExists(row, column):
                return row, column
        return first


class Spreadsheet(JFrame):
    """The spreadsheet window, that contains several sheets.
    """
    def __init__(self):
        self.tabbedPane = JTabbedPane(JTabbedPane.BOTTOM)
        self.setContentPane(self.tabbedPane)
        self.sheets = {}
        self.addTab("sheet1", Sheet())
        self.pack()

    def addTab(self, name, tab):
        self.sheets[name] = tab
        self.tabbedPane.addTab(name, tab)

    def getSheet(self, sheetref=None):
        if sheetref and sheetref.name:
            try:
                return self.sheets[sheetref.name]
            except KeyError:
                sheet = Sheet()
                self.addTab(sheetref.name, sheet)
                return sheet
        else:
            # No specific sheet was requested, we'll use the current one
            sheet = self.tabbedPane.getSelectedComponent()
            if not sheet:
                sheet = Sheet()
                self.addTab("sheet1", sheet)
                return sheet
            else:
                return sheet
