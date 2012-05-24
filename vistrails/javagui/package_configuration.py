from java.awt import Dialog
from java.awt.event import KeyEvent
from java.awt.event import KeyListener
from java.util import Vector

from javax.swing import BoxLayout
from javax.swing import JDialog
from javax.swing import JFrame
from javax.swing import JPanel
from javax.swing import JScrollPane
from javax.swing import JTable
from javax.swing import JTextField
from javax.swing.table import DefaultTableModel

from java.lang import System


class Line(object):
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type


class ConfigurationModel(DefaultTableModel):
    COLUMNS = ["Name", "Value", "Type"]

    def __init__(self, lines):
        self._configuration = lines
        self.filter('')

    # @Override
    def getRowCount(self):
        return len(self._filtered_lines)

    # @Override
    def getColumnCount(self):
        return 3

    # @Override
    def getColumnName(self, column):
        return ConfigurationModel.COLUMNS[column]

    # @Override
    def getValueAt(self, row, column):
        line = self._filtered_lines[row]
        if column == 0:
            return line.name
        elif column == 1:
            return line.value
        elif column == 2:
            return line.type.__name__

    # @Override
    def setValueAt(self, aValue, row, column):
        # TODO : validate type and change value IN BOTH LISTS
        pass

    # @Override
    def isCellEditable(self, row, column):\
        return column == 1

    def filter(self, search):
        self._filtered_lines = []
        for name in sorted(self._configuration.keys()):
            if search in name:
                value = getattr(self._configuration, name)
                if isinstance(value, tuple):
                    t = value[1]
                    value = value[0]
                else:
                    t = type(value)
                self._filtered_lines.append(Line(name, value, t))
        self.fireTableDataChanged()


class PackageConfigurationWindow(JDialog, KeyListener):
    def __init__(self, frame, package):
        JDialog.__init__(
                self, frame,
                "Package configuration", Dialog.ModalityType.DOCUMENT_MODAL)

        self._package = package

        top = JPanel()
        top.setLayout(BoxLayout(top, BoxLayout.PAGE_AXIS))
        self.setContentPane(top)

        searchLine = JPanel()
        searchLine.setLayout(BoxLayout(searchLine, BoxLayout.LINE_AXIS))
        # TODO : add the search icon here
        self._search_field = JTextField()
        self._search_field.addKeyListener(self)
        searchLine.add(self._search_field)
        top.add(searchLine)

        self._table_model = ConfigurationModel(self._package.configuration)
        table = JTable(self._table_model)
        pane = JScrollPane(table)
        pane.setColumnHeaderView(table.getTableHeader())
        top.add(pane)

        self.pack()

    # @Override
    def keyTyped(self, e):
        self._table_model.filter(self._search_field.getText())

    # @Override
    def keyPressed(self, e):
        pass

    # @Override
    def keyReleased(self, e):
        pass
