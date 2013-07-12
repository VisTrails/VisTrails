from vistrails.gui.QtWrapper import QtCore, QtGui

from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget

class ListConfigurationWidget(StandardModuleConfigurationWidget):
    """
    Configuration widget allowing to choose the number of ports.

    This is used to build a List from several modules while ensuring a given
    order. If no particular ordering is needed, connecting multiple ports to
    the 'head' input ports should be sufficient.

    """
    def __init__(self, module, controller, parent=None):
        """ ListConfigurationWidget(module: Module,
                                     controller: VistrailController,
                                     parent: QWidget)
                                     -> TupleConfigurationWidget

        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.
        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        self.module : the Module object int the pipeline
        self.controller: the current vistrail controller

        """
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

        # Give it a nice window title
        self.setWindowTitle("List Configuration")

        # Add an empty vertical layout
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.setLayout(centralLayout)

        # Add the configuration widget
        config_layout = QtGui.QFormLayout()
        self.number = QtGui.QSpinBox()
        self.number.setValue(self.countAdditionalPorts())
        self.connect(self.number, QtCore.SIGNAL('valueChanged(int)'),
                     lambda r: self.updateState())
        config_layout.addRow("Number of additional connections:", self.number)
        centralLayout.addLayout(config_layout)

        self.createButtons()

    def activate(self):
        self.number.focusWidget(QtCore.Qt.ActiveWindowFocusReason)

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button

        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.saveButton = QtGui.QPushButton("&Save", self)
        self.saveButton.setFixedWidth(100)
        self.saveButton.setEnabled(False)
        self.buttonLayout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton("&Reset", self)
        self.resetButton.setFixedWidth(100)
        self.resetButton.setEnabled(False)
        self.buttonLayout.addWidget(self.resetButton)
        self.layout().addLayout(self.buttonLayout)
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

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table

        """
        requested = self.number.value()
        current = self.countAdditionalPorts()

        if requested == current:
            # Nothing changed
            return

        if requested > current:
            sigstring = '(%s:Module)' % get_vistrails_basic_pkg_id()
            add_ports = [('input', 'item%d' % i, sigstring, -1)
                           for i in xrange(current, requested)]
            self.controller.update_ports(self.module.id, [], add_ports)
        elif requested < current:
            delete_ports = [('input', p.name) for p in self.module.input_port_specs[requested-current:]]
            self.controller.update_ports(self.module.id, delete_ports, [])
        return True

    def countAdditionalPorts(self):
        return len(self.module.input_port_specs)

    def resetTriggered(self, checked = False):
        self.number.setValue(self.countAdditionalPorts())
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL('stateChanged'))

    def updateState(self):
        if not self.hasFocus():
            self.setFocus(QtCore.Qt.TabFocusReason)
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        if not self.state_changed:
            self.state_changed = True
            self.emit(QtCore.SIGNAL('stateChanged'))
