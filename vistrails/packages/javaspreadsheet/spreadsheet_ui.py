from java.lang import Object as JavaObject
from java.awt import AlphaComposite, BorderLayout, Color, Dimension, Point
from java.awt.datatransfer import (DataFlavor, Transferable,
                                   UnsupportedFlavorException)
from java.awt.event import MouseListener
from java.io import IOException
from javax.swing import (AbstractCellEditor, ButtonGroup, DropMode, ImageIcon,
                         JButton, JFrame, JLabel, JMenu, JMenuBar, JPanel,
                         JRadioButtonMenuItem, JScrollPane, JTabbedPane,
                         JTable, JToolBar, TransferHandler)
from javax.swing.table import (DefaultTableCellRenderer, DefaultTableModel,
                               TableCellEditor)

from core.utils import product

from jtablerowheader import JTableRowHeader


# JAVAPORT : Will be a Java interface
class SpreadsheetInterface(object):
    def executePipelineToCell(self, infos, dst_sheet, dst_loc):
        pass

    def select_version(self, infos):
        pass


ICON_SIZE = Dimension(64, 64)


COPY = ImageIcon('packages/javaspreadsheet/images/copy.png')
MOVE = ImageIcon('packages/javaspreadsheet/images/move.png')
LOCATE_VERSION = ImageIcon('packages/javaspreadsheet/images/locate.png')


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
            if not self.canImport(support):
                return False

            try:
                command, source = support.getTransferable().getTransferData(
                        manipulatorData)
            except UnsupportedFlavorException:
                return False
            except IOException:
                return False

            target_loc = support.getDropLocation()
            target_loc = Point(target_loc.getColumn(), target_loc.getRow())
            self.table.manipulator_action(command, source, target_loc)

            return True
        else:
            # importData(JComponent comp, Transferable t)
            return TransferHandler.importData(self, *args)


class CellManipulator(JLabel, MouseListener):
    def __init__(self, icon, cell, command):
        JLabel.__init__(self, icon)
        self.cell = cell
        self.command = command

        self.setTransferHandler(CellManipulatorTransferHandler(self))
        self.addMouseListener(self)

    # @Override
    def mousePressed(self, event):
        self.getTransferHandler().exportAsDrag(
                self, event, TransferHandler.COPY)


class TranslucentCellOverlay(JPanel):
    OVERLAY_COLOR = Color(113, 159, 203)

    def __init__(self, component, size):
        JPanel.__init__(self, BorderLayout())
        if component is not None:
            self.add(component)
        self.setSize(size)

    # @Override
    def paint(self, g):
        JPanel.paint(self, g)
        g = g.create()
        g.setComposite(
                AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.5))
        g.setColor(self.OVERLAY_COLOR)
        g.fillRect(0, 0, self.getWidth(), self.getHeight())
        g.dispose()


INTERACTIVE = 1
EDITING = 2


class Cell(JPanel):
    SELECTION_COLOR = Color(51, 153, 255)

    def __init__(self, observer, interface, mode=INTERACTIVE):
        self._observer = observer
        self._interface = interface
        self.setLayout(None)
        self.infos = None
        self._widget = None
        self.selected = False
        self._mode = mode
        self._setup()

    def _set_selected(self, selected):
        self.setBackground(selected and self.SELECTION_COLOR or None)
    selected = property(fset=_set_selected)

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
            self._label_height = 0

            def add(title, text):
                label = JLabel('%s: %s' % (
                        title, text))
                label.setOpaque(True)
                label.setBackground(Color(230, 240, 230))
                self.add(label)
                h = int(label.getPreferredSize().getHeight())
                label.setBounds(0, self._label_height, 999999, h)
                self._label_height += h

            if self.infos is not None:
                add("Vistrail", self.infos['vistrail'])
                add("Index", "Pipeline: %d, Module: %d" % (
                        self.infos['version'], self.infos['module_id']))
                add("Created by", self.infos['reason'])

            self.add(CellManipulator(COPY, self, 'copy'))
            self.add(CellManipulator(MOVE, self, 'move'))

            locate_version = JButton(LOCATE_VERSION)
            locate_version.actionPerformed = self._select_version
            self.add(locate_version)

        if self._widget is not None:
            self.add(self._widget)

        self._layout()

    def _layout(self):
        nb_manips = 0
        for i in xrange(self.getComponentCount()):
            component = self.getComponent(i)
            if component is self._widget:
                component.setBounds(2, 2,
                                    self.getWidth() - 4, self.getHeight() - 4)
            elif isinstance(component, (CellManipulator, JButton)):
                component.setBounds(
                        nb_manips * ICON_SIZE.width + 20,
                        self._label_height + 20,
                        ICON_SIZE.width,
                        ICON_SIZE.height)
                nb_manips += 1

    def setWidget(self, widget):
        if self._widget is not None:
            self.remove(self._widget)
        self._widget = widget
        self.add(widget)
        self._layout()

    def _select_version(self, event=None):
        self._interface.select_version(self.infos)

    def assign(self, infos):
        # JAVAPORT : 'infos' dictionary could be replaced by a class
        self._widget = None
        self.infos = infos
        self._setup()

    # @Override
    def paint(self, g):
        JPanel.paint(self, g)
        self._observer.repainted(self)

    # @Override
    def setSize(self, *args):
        JPanel.setSize(self, *args)
        self._layout()


class SpreadsheetModel(DefaultTableModel):
    """The model for the _table, holding all the cells.
    """
    def __init__(self, name, rows, columns, interface):
        self.name = name
        self.nbRows = rows
        self.nbColumns = columns
        self._interface = interface
        self.cells = dict() # Point -> Cell
        self.cellpositions = dict() # Cell -> Point
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
            return self.cells[Point(column, row)]
        except KeyError:
            if create:
                c = Cell(self, self._interface, self._mode)
                self.cells[Point(column, row)] = c
                self.cellpositions[c] = Point(column, row)
                self.fireTableCellUpdated(row, column)
                return c
            else:
                return None

    # @Override
    def setValueAt(self, value, row, column):
        try:
            old_cell = self.cells[Point(column, row)]
            del self.cellpositions[old_cell]
        except KeyError:
            pass

        if value is not None:
            try:
                old_point = self.cellpositions[value] # might raise
                old_column = old_point.x
                old_row = old_point.y
                del self.cellpositions[value]
                del self.cells[old_point] # might raise
                self.fireTableCellUpdated(old_row, old_column)
            except KeyError:
                pass

            self.cells[Point(column, row)] = value
            self.cellpositions[value] = Point(column, row)
        else:
            try:
                del self.cells[Point(column, row)]
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
        self.fireTableCellUpdated(pos.y, pos.x)

    def swap_cells(self, loc1, loc2):
        prev1 = self.cells.get(loc1, None)
        prev2 = self.cells.get(loc2, None)
        self.setValueAt(prev2, loc1.y, loc1.x)
        self.setValueAt(prev1, loc2.y, loc2.x)

    def copy_cell(self, src_loc, dst_loc):
        try:
            cell = self.cells[src_loc]
        except KeyError:
            return False
        return self._interface.executePipelineToCell(
                cell.infos, self.name, dst_loc)


class SpreadsheetRenderer(DefaultTableCellRenderer):
    def __init__(self, table):
        super(SpreadsheetRenderer, self).__init__()
        self.table = table

    # @Override
    def getTableCellRendererComponent(self, table, cell, isSelected, hasFocus,
                                      row, column):
        new_size = self.table.getCellSize(row, column)
        if isinstance(cell, Cell):
            if ((cell.getSize()) != new_size):
                cell.setSize(new_size)
            cell.selected = False

        drop_location = table.getDropLocation()
        if (drop_location is not None and
                not drop_location.isInsertRow() and
                not drop_location.isInsertColumn() and
                drop_location.getRow() == row and
                drop_location.getColumn() == column):
            # We use a wrapper component instead of a simple property inside
            # class Cell because 'cell' might be None here
            return TranslucentCellOverlay(cell, new_size)
        return cell


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
            new_size = self.table.getCellSize(row, column)
            if ((value.getSize()) != new_size):
                value.setSize(new_size)
            value.selected = True
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

    def getCellSize(self, row, column):
        return Dimension(
                self.getColumnModel().getColumn(column).getWidth(),
                self.getRowHeight(row))

    def manipulator_action(self, command, source, target_loc):
        if command == 'copy':
            self.editor.cancelCellEditing()
            self.getModel().copy_cell(
                    self.getModel().cellpositions[source],
                    target_loc)
        elif command == 'move':
            self.editor.cancelCellEditing()
            self.getModel().swap_cells(
                    self.getModel().cellpositions[source],
                    target_loc)


class Sheet(JScrollPane):
    """A sheet containing a _table.
    """
    def __init__(self, name, interface):
        self.model = SpreadsheetModel(name, 2, 3, interface)
        self._table = SpreadsheetTable(self.model)
        self.setViewportView(self._table)
        self.setColumnHeaderView(self._table.getTableHeader())
        self.setRowHeaderView(JTableRowHeader(self._table))

    def _get_mode(self):
        return self.model.mode
    def _set_mode(self, mode):
        self.model.mode = mode
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

    def clearSelectedCell(self):
        self._table.editor.cancelCellEditing()
        self.model.setValueAt(
                None,
                self._table.getSelectedRow(), self._table.getSelectedColumn())

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
    def __init__(self, interface):
        self._interface = interface

        self.title = "Java Spreadsheet Window"

        self.tabbedPane = JTabbedPane(JTabbedPane.BOTTOM)
        panel = JPanel()
        panel.setLayout(BorderLayout())
        self.setContentPane(panel)
        panel.add(self.tabbedPane, BorderLayout.CENTER)
        self.sheets = dict()
        self.addTab("sheet1", Sheet("sheet1", self._interface))

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

        toolBar = JToolBar()
        clearButton = JButton("Clear cell")
        def clear(event=None):
            self.tabbedPane.getSelectedComponent().clearSelectedCell()
        clearButton.actionPerformed = clear
        toolBar.add(clearButton)
        panel.add(toolBar, BorderLayout.NORTH)

        self.pack()

    def addTab(self, name, tab):
        self.sheets[name] = tab
        self.tabbedPane.addTab(name, tab)

    def getSheet(self, sheetref=None):
        if sheetref and sheetref.name:
            try:
                return self.sheets[sheetref.name]
            except KeyError:
                sheet = Sheet(sheetref.name, self._interface)
                self.addTab(sheetref.name, sheet)
                return sheet
        else:
            # No specific sheet was requested, we'll use the current one
            sheet = self.tabbedPane.getSelectedComponent()
            if not sheet:
                sheet = Sheet("sheet1", self._interface)
                self.addTab("sheet1", sheet)
            return sheet
