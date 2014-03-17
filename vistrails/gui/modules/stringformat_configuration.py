from PyQt4 import QtCore, QtGui

from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget


class StringFormatConfigurationWidget(StandardModuleConfigurationWidget):
    """
    Configuration widget creating the ports corresponding to the format.

    """
    def __init__(self, module, controller, parent=None):
        """ StringFormatConfigurationWidget(
                module: Module,
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
        self.setWindowTitle("StringFormat Configuration")

        # Add an empty vertical layout
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.setLayout(centralLayout)

        # Add the configuration button
        self.button = QtGui.QPushButton("Sync ports")
        self.connect(self.button, QtCore.SIGNAL('clicked()'),
                     self.saveTriggered)
        centralLayout.addWidget(self.button)

    def activate(self):
        self.button.focusWidget(QtCore.Qt.ActiveWindowFocusReason)

    def saveTriggered(self, checked = False):
        """ saveTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok

        """
        if self.updateVistrail():
            self.emit(QtCore.SIGNAL('stateChanged'))
            self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)

    def get_format(self):
        for i in xrange(self.module.getNumFunctions()):
            func = self.module.functions[i]
            if func.name == 'format':
                return func.params[0].strValue
        else:
            return ''

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table

        """
        from vistrails.core.modules.basic_modules import StringFormat
        args, kwargs = StringFormat.list_placeholders(self.get_format())
        wanted_ports = set('_%d' % n for n in xrange(args)) | kwargs

        current_ports = set(port_spec.name
                            for port_spec in self.module.input_port_specs)

        sigstring = '(org.vistrails.vistrails.basic:Variant)'
        add_ports = [('input', n, sigstring, -1)
                     for n in (wanted_ports - current_ports)]
        delete_ports = [('input', n)
                        for n in (current_ports - wanted_ports)]

        self.controller.update_ports(self.module.id, delete_ports, add_ports)

        return True
