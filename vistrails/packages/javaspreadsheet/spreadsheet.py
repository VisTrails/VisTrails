from java.lang import Object as JavaObject
from java.awt import Color, Dimension
from java.awt.datatransfer import (DataFlavor, Transferable,
                                   UnsupportedFlavorException)
from java.awt.event import MouseListener
from java.io import IOException

from javax.swing import (AbstractCellEditor, ButtonGroup, DropMode, JFrame,
                         JLabel, JMenu, JMenuBar, JPanel, JRadioButtonMenuItem,
                         JScrollPane, JTabbedPane, JTable, TransferHandler)
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


manipulatorData = DataFlavor(
        JavaObject,
        'X-Vistrails-Spreadsheet-Manipulator; class=<java.lang.Object>')


class CellManipulatorTransferable(Transferable):
    def __init__(self, command, source):
        self.command = command
        self.source = source

    # @Override
    def getTransferData(self, flavor):
        if flavor == manipulatorData:
            return (self.command, self.source)
        else:
            return None

    # @Override
    def getTransferDataFlavors(self):
        return [manipulatorData]

    # @Override
    def isDataFlavorSupported(self, flavor):
        return flavor == manipulatorData


class CellManipulatorTransferHandler(TransferHandler):
    def __init__(self, manipulator):
        TransferHandler.__init__(self)
        self.manipulator = manipulator

    # @Override
    def getSourceActions(self, c):
        return TransferHandler.COPY

    # @Override
    def createTransferable(self, tree):
        return CellManipulatorTransferable(self.manipulator.command,
                                           self.manipulator.cell)

class TableTransferHandler(TransferHandler):
    def __init__(self, table):
        TransferHandler.__init__(self)
        self.table = table

    # @Override
    def canImport(self, *args):
        if len(args) == 1:
            # canImport(TransferSupport support)
            support = args[0]
            if not support.isDrop():
                return False
            elif not support.isDataFlavorSupported(manipulatorData):
                return False
            return True
        else:
            # canImport(JComponent comp, DataFlavor[] transferFlavors)
            return TransferHandler.canImport(self, *args)

    # @Override
    def importData(self, *args):
        if len(args) == 1:
            # importData(TransferSupport support)
            support = args[0]
            if not support.isDrop():
                return False
            elif not self.canImport(support):
                return False

            try:
                command, source = support.getTransferable().getTransferData(
                        manipulatorData)
            except UnsupportedFlavorException:
                return False
            except IOException:
                return False

            target_loc = support.getDropLocation()
            target_loc = (target_loc.getRow(), target_loc.getColumn())
            self.table.manipulator_action(command, source, target_loc)

            return True
        else:
            # importData(JComponent comp, Transferable t)
            return TransferHandler.importData(self, *args)


class CellManipulator(JLabel, MouseListener):
    def __init__(self, icon, cell, command, observer):
        JLabel.__init__(self, icon)
        self.cell = cell
        self.command = command
        self.observer = observer

        self.setTransferHandler(CellManipulatorTransferHandler(self))
        self.addMouseListener(self)

    # @Override
    def mousePressed(self, event):
        self.getTransferHandler().exportAsDrag(
                self, event, TransferHandler.COPY)


INTERACTIVE = 1
EDITING = 2


class Cell(JPanel):
    def __init__(self, observer, mode=INTERACTIVE):
        self.observer = observer
        self.setBackground(Color.white)
        self.setLayout(None)
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

        if self._mode == EDITING:
            def add(manipulator):
                self.add(manipulator)
                manipulator.setBounds(add.nb * ICON_SIZE.width + 20, 20,
                                      ICON_SIZE.width, ICON_SIZE.height)
                add.nb += 1
            add.nb = 0

            add(CellManipulator(COPY, self, 'copy', self.observer))
            add(CellManipulator(MOVE, self, 'move', self.observer))
            add(CellManipulator(CREATE_ANALOGY, self, 'create_analogy',
                                self.observer))
            add(CellManipulator(APPLY_ANALOGY, self, 'apply_analogy',
                                self.observer))

        if self._widget is not None:
            self.add(self._widget)
            self._widget.setBounds(0, 0, self.getWidth(), self.getHeight())

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

    # @Override
    def setSize(self, *args):
        JPanel.setSize(self, *args)
        if self._widget is not None:
            self._widget.setBounds(0, 0, self.getWidth(), self.getHeight())


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
        try:
            old_row, old_column = self.cellpositions[value] # might raise
            del self.cellpositions[value]
            del self.cells[(old_row, old_column)] # might raise
            self.fireTableCellUpdated(old_row, old_column)
        except KeyError:
            pass

        if value is not None:
            try:
                old_cell = self.cells[(row, column)]
                del self.cellpositions[old_cell]
            except KeyError:
                pass
            self.cells[(row, column)] = value
            self.cellpositions[value] = (row, column)
        else:
            try:
                del self.cells[(row, column)]
            except KeyError:
                pass
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

    def swap_cells(self, loc1, loc2):
        prev1 = self.cells.get(loc1, None)
        prev2 = self.cells.get(loc2, None)
        self.setValueAt(prev2, loc1[0], loc1[1])
        self.setValueAt(prev1, loc2[0], loc2[1])


class SpreadsheetRenderer(DefaultTableCellRenderer):
    def __init__(self, table):
        super(SpreadsheetRenderer, self).__init__()
        self.table = table

    # @Override
    def getTableCellRendererComponent(self, table, value, isSelected, hasFocus,
                                      row, column):
        if isinstance(value, Cell):
            new_size = self.table.getCellSize(value)
            if ((value.getSize()) != new_size):
                value.setSize(new_size)
        return value


class SpreadsheetEditor(AbstractCellEditor, TableCellEditor):
    def __init__(self, table):
        super(SpreadsheetEditor, self).__init__()
        self.cell = None
        self.table = table

    # @Override
    def getCellEditorValue(self):
        return self.cell

    # @Override
    def getTableCellEditorComponent(self, table, value, isSelected,
                                    row, column):
        if isinstance(value, Cell):
            new_size = self.table.getCellSize(value)
            if ((value.getSize()) != new_size):
                value.setSize(new_size)
        self.cell = value
        return self.cell


class SpreadsheetTable(JTable):
    def __init__(self, model):
        super(SpreadsheetTable, self).__init__(model)
        self.renderer = SpreadsheetRenderer(self)
        self.editor = SpreadsheetEditor(self)
        self.setRowHeight(100)
        self.getTableHeader().setReorderingAllowed(False)
        self.setDropMode(DropMode.USE_SELECTION)
        self.setTransferHandler(TableTransferHandler(self))

    # @Override
    def getDefaultRenderer(self, c):
        return self.renderer

    # @Override
    def getDefaultEditor(self, columnClass):
        return self.editor

    def getCellSize(self, cell):
        row, column = self.getModel().cellpositions[cell]
        return Dimension(
                self.getColumnModel().getColumn(column).getWidth(),
                self.getRowHeight(row))

    def manipulator_action(self, command, source, target_loc):
        if command == 'copy':
            # TODO : I don't know how to do that
            pass
        elif command == 'move':
            self.editor.cancelCellEditing()
            self.getModel().swap_cells(
                    self.getModel().cellpositions[source],
                    target_loc)
        elif command == 'create_analogy':
            # TODO : create an analogy
            pass
        elif command == 'apply_analogy':
            # TODO : apply an analogy
            pass


class Sheet(JScrollPane):
    """A sheet containing a _table.
    """
    def __init__(self):
        self.model = SpreadsheetModel(2, 3)
        self._table = SpreadsheetTable(self.model)
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
