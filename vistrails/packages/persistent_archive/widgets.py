from PyQt4 import QtCore, QtGui

from vistrails.core.db.action import create_action
from vistrails.gui.modules.module_configure import \
    StandardModuleConfigurationWidget

from .queries import QueryCondition, EqualString, EqualInt


def str_repr(s):
    if isinstance(s, unicode):
        s = (s.replace('\\', '\\\\')
              .replace("'", "\\'")
              .encode('ascii', 'backslashreplace'))
    else:
        s = (s.replace('\\', '\\\\')
              .replace("'", "\\'"))
    return "'%s'" % s


class Metadata(QtGui.QWidget):
    remove = QtCore.pyqtSignal()
    changed = QtCore.pyqtSignal()

    def __init__(self, name, value=None):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        self.key = QtGui.QLineEdit()
        self.key.setText(name)
        layout.addWidget(self.key, 1)
        self.value = self.value_widget(value)
        layout.addWidget(self.value, 2)

        remove_button = QtGui.QPushButton("Remove port")
        remove_button.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                    QtGui.QSizePolicy.Fixed)
        layout.addWidget(remove_button)

        self.connect(remove_button, QtCore.SIGNAL('clicked()'),
                     self.remove)
        self.connect(self.key, QtCore.SIGNAL('textEdited(const QString &)'),
                     self.changed)
        self.connect(self.value, QtCore.SIGNAL('textEdited(const QString &)'),
                     self.changed)


class StringMetadata(Metadata):
    @staticmethod
    def value_widget(value=None):
        return QtGui.QLineEdit(value)

    def to_string(self):
        return 'EqualString(%s, %s)' % (str_repr(self.key.text()),
                                        str_repr(self.value.text()))


class IntMetadata(Metadata):
    def value_widget(self, value=None):
        w = QtGui.QLineEdit()
        if value is not None:
            w.setText('%d' % value)
        w.setValidator(QtGui.QIntValidator(self))
        return w

    def to_string(self):
        try:
            i = int(self.value.text())
        except ValueError:
            i = 0
        return 'EqualInt(%s, %d)' % (str_repr(self.key.text()), i)


class SetMetadataWidget(StandardModuleConfigurationWidget):
    """
    Configuration widget allowing to set metadata on persisted modules.

    It is a visual editor for the strings functions set on the 'metadata' port,
    which have the form EqualString('mkey', 'mvalue') or EqualInt('mkey', 2).
    """
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

        # Window title
        self.setWindowTitle("Metadata editor")

        central_layout = QtGui.QVBoxLayout()
        central_layout.setMargin(0)
        central_layout.setSpacing(0)
        self.setLayout(central_layout)

        self._scroll_area = QtGui.QScrollArea()
        inner_widget = QtGui.QWidget()
        self._list_layout = QtGui.QVBoxLayout()
        scroll_layout = QtGui.QVBoxLayout()
        scroll_layout.addLayout(self._list_layout)
        scroll_layout.addStretch()
        inner_widget.setLayout(scroll_layout)
        self._scroll_area.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOn)
        self._scroll_area.setWidget(inner_widget)
        self._scroll_area.setWidgetResizable(True)
        central_layout.addWidget(self._scroll_area)

        add_buttons = QtGui.QHBoxLayout()
        central_layout.addLayout(add_buttons)
        add_string = QtGui.QPushButton("Add a string")
        self.connect(add_string, QtCore.SIGNAL('clicked()'),
                     self.add_string)
        add_buttons.addWidget(add_string, 2)
        add_int = QtGui.QPushButton("Add an integer")
        self.connect(add_int, QtCore.SIGNAL('clicked()'),
                     self.add_int)
        add_buttons.addWidget(add_int, 1)

        self.createButtons()

        self.createEntries()

    def add_item(self, item):
        self._list_layout.addWidget(item)
        self.connect(item, QtCore.SIGNAL('remove()'),
                     lambda: item.deleteLater())
        self.connect(item, QtCore.SIGNAL('changed()'),
                     self.updateState)

    def add_string(self):
        self.add_item(StringMetadata(
                "string%d" % (self._list_layout.count() + 1)))
        self.updateState()

    def add_int(self):
        self.add_item(IntMetadata(
                "int%d" % (self._list_layout.count() + 1)))
        self.updateState()

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

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update functions on the metadata port of the module
        """
        # Remove the keys that we loaded
        ops = [('delete', func) for func in self._loaded_keys]

        # Add the metadata in the list
        for i in xrange(self._list_layout.count()):
            widget = self._list_layout.itemAt(i).widget()
            ops.extend(self.controller.update_function_ops(
                    self.module, 'metadata',
                    [widget.to_string()]))

        # This code should really be in VistrailController
        self.controller.flush_delayed_actions()
        action = create_action(ops)
        self.controller.add_new_action(action,
                                       "Updated PersistedPath metadata")
        self.controller.perform_action(action)

        return True

    def getCurrentFunctions(self):
        for i in xrange(self.module.getNumFunctions()):
            func = self.module.functions[i]
            if func.name == 'metadata':
                yield func, func.params[0].strValue

    def createEntries(self):
        self._loaded_keys = set()
        for func, metadata in self.getCurrentFunctions():
            metadata = QueryCondition.translate_to_python(metadata)
            save = True
            if metadata is None:
                save = False
            elif isinstance(metadata, EqualString):
                self.add_item(StringMetadata(metadata.key, metadata.value))
            elif isinstance(metadata, EqualInt):
                self.add_item(IntMetadata(metadata.key, metadata.value))
            else:
                save = False

            if save:
                self._loaded_keys.add(func)

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
