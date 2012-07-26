from java.awt import Color, Dimension
from java.awt.event import ComponentListener
from javax.swing import (AbstractCellEditor, JFrame, JLabel, JPanel,
                         JScrollPane, JTabbedPane, JTable, JMenuBar, JMenu,
                         JRadioButtonMenuItem, ButtonGroup)
from javax.swing.table import (DefaultTableModel, DefaultTableCellRenderer,
                               TableCellEditor)

from core.utils import product
from javagui.utils import resized_icon

from jtablerowheader import JTableRowHeader


ICON_SIZE = Dimension(64, 64)


COPY = resized_icon(
        'packages/javaspreadsheet/images/copy.png', ICON_SIZE)
MOVE = resized_icon(
        'packages/javaspreadsheet/images/move.png', ICON_SIZE)
CREATE_ANALOGY = resized_icon(
        'packages/javaspreadsheet/images/create_analogy.png', ICON_SIZE)
APPLY_ANALOGY = resized_icon(
        'packages/javaspreadsheet/images/apply_analogy.png', ICON_SIZE)


class CellManipulator(JLabel):
    def __init__(self, icon, command, observer):
        JLabel.__init__(self, icon)
        self.command = command
        self.observer = observer

    # TODO : drag and drop


INTERACTIVE = 1
EDITING = 2


class Cell(JPanel):
    def __init__(self, observer, mode=INTERACTIVE):
        self.observer = observer
        self.setBackground(Color.white)
        self._widget = None
        self._mode = mode
        self._setup()

    def _get_mode(self):
        return self._mode
    def _set_mode(self, mode):
        if mode == self._mode:
            return
        self._mode = mode
        self._setup()
    mode = property(_get_mode, _set_mode)

    def _setup(self):
        self.removeAll()
        if self._widget is not None:
            self.add(self._widget)

        if self._mode == EDITING:
            self.add(CellManipulator(COPY, 'copy', self.observer))
            self.add(CellManipulator(MOVE, 'move', self.observer))
            self.add(CellManipulator(CREATE_ANALOGY, 'create_analogy',
                                     self.observer))
            self.add(CellManipulator(APPLY_ANALOGY, 'apply_analogy',
                                     self.observer))

    def _get_widget(self):
        return self._widget
    def _set_widget(self, widget):
        if self._widget is not None:
            self.remove(self._widget)
        self._widget = widget
        self._setup()
    widget = property(_get_widget, _set_widget)

    # @Override
    def paint(self, g):
        JPanel.paint(self, g)
        self.observer.repainted(self)

    # TODO : Correctly react to resize events (resize the widget)


class SpreadsheetModel(DefaultTableModel):
    """The model for the _table, holding all the cells.
    """
    def __init__(self, rows, columns):
        self.nbRows = rows
        self.nbColumns = columns
        self.cells = {}
        self.cellpositions = {}
        self._mode = INTERACTIVE

    def _get_mode(self):
        return self._mode
    def _set_mode(self, mode):
        if mode != self._mode:
            self._mode = mode
            for cell in self.cells.itervalues():
                cell.mode = mode
    mode = property(_get_mode, _set_mode)

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
                c = Cell(self, self._mode)
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

    def _get_mode(self):
        return self._table.getModel().mode
    def _set_mode(self, mode):
        self._table.getModel().mode = mode
    mode = property(_get_mode, _set_mode)

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

        def ch_mode(mode):
            def action(event=None):
                for sheet in self.sheets.itervalues():
                    sheet.mode = mode
            return action
        menuBar = JMenuBar()
        viewMenu = JMenu("View")
        interactiveMode = JRadioButtonMenuItem("Interactive Mode", True)
        interactiveMode.actionPerformed = ch_mode(INTERACTIVE)
        viewMenu.add(interactiveMode)
        editingMode = JRadioButtonMenuItem("Editing Mode")
        editingMode.actionPerformed = ch_mode(EDITING)
        viewMenu.add(editingMode)
        group = ButtonGroup()
        group.add(interactiveMode)
        group.add(editingMode)
        menuBar.add(viewMenu)
        self.setJMenuBar(menuBar)

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
