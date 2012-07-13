from core.utils import product

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
    """The model for the _table, holding all the cells.
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
    def getValueAt(self, row, column, create=False):
        try:
            return self.cells[(row, column)]
        except KeyError:
            if create:
                c = Cell(self)
                self.cells[(row, column)] = c
                self.cellpositions[c] = (row, column)
                self.fireTableCellUpdated(row, column)
                return c
            else:
                return None

    # @Override
    def setValueAt(self, value, row, column):
        self.cells[(row, column)] = value
        self.cellpositions[value] = (row, column)
        self.fireTableCellUpdated(row, column)

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
        self.fireTableCellUpdated(pos[0], pos[1])


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
        self.getTableHeader().setReorderingAllowed(False)

    # @Override
    def getDefaultRenderer(self, c):
        return self.renderer

    # @Override
    def getDefaultEditor(self, columnClass):
        return self.editor


class Sheet(JScrollPane):
    """A sheet containing a _table.
    """
    def __init__(self):
        self.model = SpreadsheetModel(2, 3)
        self._table = CustomTable(self.model)
        self.setViewportView(self._table)
        self.setColumnHeaderView(self._table.getTableHeader())
        self.setRowHeaderView(JTableRowHeader(self._table))

    def getCell(self, location=None):
        # Locate the requested cell
        row, column = None, None
        if location:
            row = location.row
            column = location.column

        # Should we grow the _table?
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

        return self.model.getValueAt(row, column, create=True)

    @staticmethod
    def findCell(model, row, column):
        if row and column:
            return row, column
        rows = xrange(0, model.getRowCount())
        columns = xrange(0, model.getColumnCount())
        if row and not column:
            cells = product([row], columns)
            first = row, 0
        elif column and not row:
            cells = product(rows, [column])
            first = 0, column
        else:
            cells = product(rows, columns)
            first = 0, 0
        for row, column in cells:
            if not model.getValueAt(row, column, create=False):
                return row, column
        return first


class Spreadsheet(JFrame):
    """The spreadsheet window, that contains several sheets.
    """
    def __init__(self):
        self.title = "Java Spreadsheet Window"
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
