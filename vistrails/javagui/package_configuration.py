from java.awt import Dialog
from java.awt.event import KeyListener

from javax.swing import BoxLayout, JDialog, JPanel, JScrollPane
from javax.swing import JTable, JTextField
from javax.swing.table import DefaultTableModel


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
        line = self._filtered_lines[row]
        try:
            if line.type == int:
                aValue = int(aValue)
            elif line.type == str:
                aValue = str(aValue) # aValue is a Java String, it gets sent as
                        # unicode
            elif line.type == bool:
                if aValue.lower() == "true" or aValue == "1":
                    aValue = True
                elif aValue.lower() == "false" or aValue == "0":
                    aValue = False
                else:
                    raise ValueError
            elif line.type == float:
                aValue = float(aValue)
            line.value = aValue
            print "!!! setting value: %s (%s)" % (aValue, type(aValue))
            setattr(self._configuration, line.name, line.value)
            self.fireTableCellUpdated(row, column)
        except ValueError:
            # Not updating anything -- cell content will revert
            pass

    # @Override
    def isCellEditable(self, row, column):\
        return column == 1

    def filter(self, search):
        search = search.lower()
        self._filtered_lines = []
        for name in sorted(self._configuration.keys()):
            if search in name.lower():
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
        super(PackageConfigurationWindow, self).__init__(
                frame,
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
