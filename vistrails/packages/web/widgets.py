from PyQt4 import QtCore, QtGui
import urllib

from vistrails.core.modules.basic_modules import File
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.gui.modules.module_configure import \
    StandardModuleConfigurationWidget


class PortFile(QtGui.QWidget):
    remove = QtCore.pyqtSignal()
    changed = QtCore.pyqtSignal()
    file_port_selected = QtCore.pyqtSignal(object)

    radio_button = False

    def __init__(self, buttongroup, uri):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtGui.QLabel("URI:"))
        self.uri_widget = QtGui.QLineEdit(uri)
        layout.addWidget(self.uri_widget)
        layout.addStretch()
        if self.radio_button:
            change = QtGui.QRadioButton()
            buttongroup.addButton(change)
            layout.addWidget(change)
            self.connect(change, QtCore.SIGNAL('clicked()'),
                         lambda: self.file_port_selected.emit(self))
        remove_button = QtGui.QPushButton("Remove port")
        remove_button.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                    QtGui.QSizePolicy.Fixed)
        layout.addWidget(remove_button)

        self.connect(remove_button, QtCore.SIGNAL('clicked()'),
                     self.remove)
        self.connect(self.uri_widget, QtCore.SIGNAL('textEdited(const QString &)'),
                     self.uri_changed)

    def uri_changed(self, new_value):
        if not new_value.startswith('/'):
            new_value = '/' + new_value
            self.uri_widget.setText(new_value)
        self.changed.emit()

    @property
    def uri(self):
        return str(self.uri_widget.text())


class DirectFile(PortFile):
    radio_button = True


class Editor(QtGui.QTextEdit):
    textEdited = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QTextEdit.__init__(self)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.setCursorWidth(8)
        self.setContent(None)
        self._changing = False
        self.connect(self, QtCore.SIGNAL('textChanged()'),
                     self.editedCheck)

    def editedCheck(self):
        if not self._changing:
            self.textEdited.emit()

    def setContent(self, content):
        self._changing = True
        try:
            if content is None:
                self.setHtml("<p></p>"
                             "<p><center>No inline file selected</center></p>")
                self.setEnabled(False)
            else:
                self.setEnabled(True)
                self.setPlainText(content)
        finally:
            self._changing = False

    def content(self):
        return self.toPlainText()


class WebSiteWidget(StandardModuleConfigurationWidget):
    """Configuration widget allowing to setup files for the WebSite module.
    """
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

        # Window title
        self.setWindowTitle("Web site configuration")

        central_layout = QtGui.QVBoxLayout()
        central_layout.setMargin(0)
        central_layout.setSpacing(0)
        self.setLayout(central_layout)

        self._direct_files_group = QtGui.QButtonGroup(self)
        self._file_contents = {}

        default_uri_layout = QtGui.QHBoxLayout()
        default_uri_layout.addWidget(QtGui.QLabel("Display URI:"))
        self._default_uri = QtGui.QLineEdit(
                self.getPortValue('spreadsheet_page', '/index.html'))
        default_uri_layout.addWidget(self._default_uri)
        central_layout.addLayout(default_uri_layout)

        scroll_area = QtGui.QScrollArea()
        inner_widget = QtGui.QWidget()
        self._list_layout = QtGui.QVBoxLayout()
        scroll_layout = QtGui.QVBoxLayout()
        scroll_layout.addLayout(self._list_layout)
        scroll_layout.addStretch()
        inner_widget.setLayout(scroll_layout)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setWidget(inner_widget)
        scroll_area.setWidgetResizable(True)
        central_layout.addWidget(scroll_area)

        self._editing_item = None
        self._editor = Editor()
        def print_and_update():
            print("Editor changed")
            self.updateState()
        self.connect(self._editor, QtCore.SIGNAL('textEdited()'),
                     print_and_update)
        central_layout.addWidget(self._editor)

        add_buttons = QtGui.QHBoxLayout()
        central_layout.addLayout(add_buttons)
        add_direct = QtGui.QPushButton("Add an inline file")
        self.connect(add_direct, QtCore.SIGNAL('clicked()'),
                     self.add_direct)
        add_buttons.addWidget(add_direct)
        add_port = QtGui.QPushButton("Add a File port")
        self.connect(add_port, QtCore.SIGNAL('clicked()'),
                     self.add_port)
        add_buttons.addWidget(add_port)

        self.createButtons()

        self.createEntries()

    def add_item(self, item):
        self._list_layout.addWidget(item)
        self.connect(item, QtCore.SIGNAL('remove()'),
                     lambda: item.deleteLater())
        self.connect(item, QtCore.SIGNAL('changed()'),
                     self.updateState)
        self.connect(item, QtCore.SIGNAL('file_port_selected(PyQt_PyObject)'),
                     self.edit_file)

    def add_direct(self):
        widget = DirectFile(self._direct_files_group, "/index.html")
        self.add_item(widget)
        self._file_contents[widget] = ""
        self.updateState()

    def add_port(self):
        self.add_item(PortFile(self._direct_files_group, "/file"))
        self.updateState()

    def edit_file(self, item):
        print("Changing file to edit")
        if self._editing_item is not None:
            contents = self._editor.content()
            if self._file_contents[self._editing_item] != contents:
                print("Old file modified; pulling")
                self._file_contents[self._editing_item] = contents
                self.updateState()
        if item is not None:
            self._editing_item = item
            self._editor.setContent(self._file_contents[item])
        else:
            self._editing_item = None
            self._editor.setContent(None)

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button

        """
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.setMargin(5)
        self.saveButton = QtGui.QPushButton("&Save", self)
        self.saveButton.setFixedWidth(100)
        self.saveButton.setEnabled(False)
        buttonLayout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton("&Reset", self)
        self.resetButton.setFixedWidth(100)
        self.resetButton.setEnabled(False)
        buttonLayout.addWidget(self.resetButton)
        self.layout().addLayout(buttonLayout)
        self.connect(self.saveButton, QtCore.SIGNAL('clicked(bool)'),
                     self.saveTriggered)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked(bool)'),
                     self.resetTriggered)

    def saveTriggered(self, checked = False):
        """ saveTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok

        """
        if self.updateVistrail():
            self.saveButton.setEnabled(False)
            self.resetButton.setEnabled(False)
            self.state_changed = False
            self.emit(QtCore.SIGNAL('stateChanged'))
            self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)

    def closeEvent(self, event):
        self.askToSaveChanges()
        event.accept()

    def getPortValue(self, portname, default):
        for i in xrange(self.module.getNumFunctions()):
            fun = self.module.functions[i]
            if fun.name == portname:
                return fun.params[0].strValue
        return default

    def getCurrentPorts(self):
        current_ports = []
        for port_spec in self.module.input_port_specs:
            is_direct = port_spec.signature[0][0] is not File
            if is_direct:
                code = self.getPortValue(port_spec.name, "")
                code = urllib.unquote(code)
                current_ports.append((port_spec.name, is_direct, code))
            else:
                current_ports.append((port_spec.name, is_direct, None))
        return current_ports

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table

        """
        self.edit_file(self._editing_item)
        file_sig = '(%s:File)' % get_vistrails_basic_pkg_id()
        string_sig = '(%s:String)' % get_vistrails_basic_pkg_id()
        seen_new_ports = set()
        current_ports = dict(
                (uri, (is_direct, data))
                for uri, is_direct, data in self.getCurrentPorts())
        add_ports = []
        functions = []
        delete_ports = []
        for i in xrange(self._list_layout.count()):
            widget = self._list_layout.itemAt(i).widget()
            is_direct = isinstance(widget, DirectFile)
            uri = widget.uri

            if uri in seen_new_ports:
                QtGui.QMessageBox.critical(
                        self,
                        "Duplicated port name",
                        "There is several input ports with uri %r" % uri)
                return
            seen_new_ports.add(uri)

            if uri in current_ports:
                old_is_direct, _ = current_ports.pop(uri)
                if is_direct and old_is_direct:
                    # Update value?
                    current = self.getPortValue(uri, None)
                    new = self._file_contents[widget]
                    new = urllib.quote(new.encode('utf-8'))
                    print("current=%r, new=%r" % (current, new))
                    if current != new:
                        print("Updating value on port %s" % uri)
                        functions.append((uri, [new]))
                    continue
                if is_direct == old_is_direct:
                    continue
                delete_ports.append(('input', uri))
            elif is_direct:
                new = self._file_contents[widget]
                new = urllib.quote(new.encode('utf-8'))
                print("creating, new=%r" % new)
                functions.append((uri, [new]))

            sigstring = string_sig if is_direct else file_sig
            add_ports.append(('input', uri,
                              sigstring, -1))

        delete_ports.extend(('input', unseen_port)
                            for unseen_port in current_ports.iterkeys())

        print("update_ports_and_functions(\n"
              "    delete: %r\n"
              "    add: %r\n"
              "    functions: %r" % (delete_ports, add_ports, functions))
        self.controller.update_ports(self.module.id, delete_ports, add_ports)
        self.controller.update_functions(self.module, functions)

        return True

    def createEntries(self):
        self._editing_item = None
        self._editor.setContent(None)

        # If there are no ports, create a default for index.html
        current_ports = self.getCurrentPorts()
        if not current_ports:
            widget = DirectFile(self._direct_files_group, "/index.html")
            self.add_item(widget)
            self._file_contents[widget] = """\
<!DOCTYPE html>
<html>
  <head></head>
  <body>
    <p>VisTrails web cell</p>
  </body>
</html>
"""
            self.saveButton.setEnabled(True)
            self.resetButton.setEnabled(True)
        else:
            for uri, is_direct, data in current_ports:
                if is_direct:
                    widget = DirectFile(self._direct_files_group, uri)
                    self._file_contents[widget] = data
                    self.add_item(widget)
                else:
                    self.add_item(PortFile(self._direct_files_group, uri))

    def resetTriggered(self, checked = False):
        for i in xrange(self._list_layout.count()):
            self._list_layout.itemAt(i).widget().deleteLater()

        self.createEntries()

        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL('stateChanged'))

    def updateState(self):
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        if not self.state_changed:
            self.state_changed = True
            self.emit(QtCore.SIGNAL('stateChanged'))
