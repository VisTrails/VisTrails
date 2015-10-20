from __future__ import division

from PyQt4 import QtCore, QtGui

from vistrails.gui.modules.module_configure import \
    StandardModuleConfigurationWidget
from vistrails.gui.modules.source_configure import SourceConfigurationWidget
from vistrails.gui.modules.string_configure import TextEditor


class ShellSourceConfigurationWidget(SourceConfigurationWidget):
    """Configuration widget for SubmitShellJob.

    Allows the user to edit a shell script that will be run on the server.
    """
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller,
                                           TextEditor,
                                           has_inputs=False, has_outputs=False,
                                           parent=parent)


class DirectoryConfigurationWidget(StandardModuleConfigurationWidget):
    """Configuration widget for MakeDirectory.

    Allows to edit a list of filenames.
    """
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

        # Window title
        self.setWindowTitle("Directory configuration")

        central_layout = QtGui.QVBoxLayout()
        central_layout.setMargin(0)
        central_layout.setSpacing(0)
        self.setLayout(central_layout)

        self._list = QtGui.QListWidget()
        self._list.setSortingEnabled(True)
        self.connect(self._list,
                     QtCore.SIGNAL('itemChanged(QListWidgetItem*)'),
                     lambda i: self.updateState())
        central_layout.addWidget(self._list)

        add_button = QtGui.QPushButton("Add a file")
        self.connect(add_button, QtCore.SIGNAL('clicked()'),
                     self.add_file)
        central_layout.addWidget(add_button)

        self.createButtons()

        self.createEntries()

    def add_file(self):
        item = QtGui.QListWidgetItem("file")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsEnabled)
        self._list.addItem(item)

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

    def getCurrentPorts(self):
        return (port_spec.name for port_spec in self.module.input_port_specs)

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table

        """
        file_sig = '(org.vistrails.vistrails.basic:File)'
        seen_new_ports = set()
        current_ports = set(self.getCurrentPorts())
        add_ports = []
        delete_ports = []
        for i in xrange(self._list.count()):
            name = str(self._list.item(i).text())

            if name in seen_new_ports:
                QtGui.QMessageBox.critical(
                        self,
                        "Duplicated port name",
                        "There are several input ports with name %r" % name)
                return
            seen_new_ports.add(name)

            if name in current_ports:
                current_ports.discard(name)
                continue

            add_ports.append(('input', name,
                              file_sig, -1))

        delete_ports.extend(('input', unseen_port)
                            for unseen_port in current_ports)

        self.controller.update_ports(self.module.id, delete_ports, add_ports)

        return True

    def createEntries(self):
        for name in self.getCurrentPorts():
            item = QtGui.QListWidgetItem(name)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                          QtCore.Qt.ItemIsEnabled)
            self._list.addItem(item)

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
