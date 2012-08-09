import copy

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

from core.application import get_vistrails_application
from core.inspector import PipelineInspector
from core.interpreter.default import get_default_interpreter
from core.modules.module_registry import get_module_registry
from core.utils import DummyView, product
from core.vistrail.controller import VistrailController

from jtablerowheader import JTableRowHeader


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
            target_loc = Point(target_loc.getColumn(), target_loc.getRow())
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

    def __init__(self, observer, mode=INTERACTIVE):
        self.observer = observer
        self.setBackground(Color.white)
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

            self.add(CellManipulator(COPY, self, 'copy', self.observer))
            self.add(CellManipulator(MOVE, self, 'move', self.observer))

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

    def _get_widget(self):
        return self._widget
    def _set_widget(self, widget):
        if self._widget is not None:
            self.remove(self._widget)
        self._widget = widget
        self.add(widget)
        self._layout()
    widget = property(_get_widget, _set_widget)

    def _select_version(self, event=None):
        app = get_vistrails_application()
        try:
            window = app.builderWindow
        except AttributeError:
            pass
        else:
            window.select_vistrail(self.infos['locator'],
                                   self.infos['version'])

    def assign(self, infos):
        # JAVAPORT : 'infos' dictionary could be replaced by a class
        self._widget = None
        self.infos = infos
        self._setup()

    # @Override
    def paint(self, g):
        JPanel.paint(self, g)
        self.observer.repainted(self)

    # @Override
    def setSize(self, *args):
        JPanel.setSize(self, *args)
        self._layout()


class SpreadsheetModel(DefaultTableModel):
    """The model for the _table, holding all the cells.
    """
    def __init__(self, name, rows, columns):
        self.name = name
        self.nbRows = rows
        self.nbColumns = columns
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
                c = Cell(self, self._mode)
                self.cells[Point(column, row)] = c
                self.cellpositions[c] = Point(column, row)
                self.fireTableCellUpdated(column, row)
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
                del self.cells[Point(old_column, old_row)] # might raise
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
        self.fireTableCellUpdated(column, row)

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
        infos = cell.infos
        pipeline = infos['pipeline']
        if pipeline is None:
            return False
        mod_id = infos['module_id']
        # JAVAPORT : This has to be implemented in Python
        pipeline = assignPipelineCellLocations(
                pipeline,
                self.name,
                dst_loc,
                [mod_id])
        interpreter = get_default_interpreter()
        interpreter.execute(
                pipeline,
                locator=infos['locator'],
                current_version=infos['version'],
                view=DummyView(),
                actions=infos['actions'],
                reason=infos['reason'],
                sinks=[mod_id])
        return True


# This is an adaptation of packages.spreadsheet.spreadsheet_execute
# FIXME : there must be a better way to do this
def assignPipelineCellLocations(pipeline, sheetName, 
                                dst_loc, modules=[]):
    """ assignPipelineCellLocations(pipeline: Pipeline, sheetName: str,
                                    dst_loc: (int, int),
                                    modules: [ids]) -> Pipeline                                  
    Modify the pipeline to have its cells (provided by modules) to
    be located at the specified location on this sheet.
    """
    col, row = dst_loc.x, dst_loc.y

    reg = get_module_registry()
    # These are the modules we need to edit
    spreadsheet_cell_desc = \
        reg.get_descriptor_by_name('edu.utah.sci.vistrails.javaspreadsheet',
                                   'AssignCell')

    create_module = VistrailController.create_module_static
    create_function = VistrailController.create_function_static
    create_connection = VistrailController.create_connection_static

    pipeline = copy.copy(pipeline)
    root_pipeline = pipeline
    if modules is None:
        inspector = PipelineInspector()
        inspector.inspect_spreadsheet_cells(pipeline)
        inspector.inspect_ambiguous_modules(pipeline)
        modules = inspector.spreadsheet_cells

    for id_list in modules:
        # find at which depth we need to be working
        try:                
            id_iter = iter(id_list)
            m = pipeline.modules[id_iter.next()]
            for mId in id_iter:
                pipeline = m.pipeline
                m = pipeline.modules[mId]
        except TypeError:
            mId = id_list

        m = pipeline.modules[mId]
        if not reg.is_descriptor_subclass(m.module_descriptor, 
                                          spreadsheet_cell_desc):
            continue

        # Walk through all connections and remove all CellLocation
        # modules connected to this spreadsheet cell
        conns_to_delete = []
        for conn_id, c in pipeline.connections.iteritems():
            if (c.destinationId==mId and pipeline.modules[c.sourceId].name in
                    ('CellLocation', 'SheetReference')):
                conns_to_delete.append(c.id)
        for c_id in conns_to_delete:
            pipeline.delete_connection(c_id)

        # a hack to first get the id_scope to the local pipeline scope
        # then make them negative by hacking the getNewId method
        # all of this is reset at the end of this block
        id_scope = pipeline.tmp_id
        orig_getNewId = pipeline.tmp_id.__class__.getNewId
        def getNewId(self, objType):
            return -orig_getNewId(self, objType)
        pipeline.tmp_id.__class__.getNewId = getNewId

        # Add a sheet reference with a specific name
        sheetReference = create_module(
                id_scope,
                'edu.utah.sci.vistrails.javaspreadsheet', 'SheetReference')
        sheetNameFunction = create_function(id_scope, sheetReference, 
                                            'sheet', [str(sheetName)])
        sheetReference.add_function(sheetNameFunction)

        # Add a cell location module with a specific row and column
        cellLocation = create_module(id_scope, 
                                     "edu.utah.sci.vistrails.javaspreadsheet",
                                     "CellLocation")
        rowFunction = create_function(id_scope, cellLocation, "row", [str(row)])
        colFunction = create_function(id_scope, cellLocation, "column", 
                                      [str(col)])

        cellLocation.add_function(rowFunction)
        cellLocation.add_function(colFunction)

        cell_module = pipeline.get_module_by_id(mId)
        # Then connect the SheetReference to the AssignCell
        sheet_conn = create_connection(id_scope, sheetReference, 'reference',
                                       cell_module, 'sheet')
        # Then connect the CellLocation to the spreadsheet cell
        cell_conn = create_connection(id_scope, cellLocation, 'location',
                                      cell_module, 'location')

        pipeline.add_module(sheetReference)
        pipeline.add_module(cellLocation)
        pipeline.add_connection(sheet_conn)
        pipeline.add_connection(cell_conn)
        # replace the getNewId method
        pipeline.tmp_id.__class__.getNewId = orig_getNewId

    return root_pipeline


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
    def __init__(self, name):
        self.model = SpreadsheetModel(name, 2, 3)
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
    def __init__(self):
        self.title = "Java Spreadsheet Window"

        self.tabbedPane = JTabbedPane(JTabbedPane.BOTTOM)
        panel = JPanel()
        panel.setLayout(BorderLayout())
        self.setContentPane(panel)
        panel.add(self.tabbedPane, BorderLayout.CENTER)
        self.sheets = dict()
        self.addTab("sheet1", Sheet("sheet1"))

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
                sheet = Sheet(sheetref.name)
                self.addTab(sheetref.name, sheet)
                return sheet
        else:
            # No specific sheet was requested, we'll use the current one
            sheet = self.tabbedPane.getSelectedComponent()
            if not sheet:
                sheet = Sheet("sheet1")
                self.addTab("sheet1", sheet)
                return sheet
            else:
                return sheet
