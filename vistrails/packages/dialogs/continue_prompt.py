from PyQt4 import QtCore, QtGui

from vistrails.core.modules import basic_modules
from vistrails.core.modules.vistrails_module import Module, ModuleError


class PromptWindow(QtGui.QDialog):
    def __init__(self, widget, label=None):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle("Check intermediate results")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(widget)
        if label is not None:
            self.layout().addWidget(QtGui.QLabel(label))
        buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Yes | QtGui.QDialogButtonBox.No)
        self.connect(buttons, QtCore.SIGNAL('accepted()'),
                     self, QtCore.SLOT('accept()'))
        self.connect(buttons, QtCore.SIGNAL('rejected()'),
                     self, QtCore.SLOT('reject()'))
        self.layout().addWidget(buttons)


class PromptIsOkay(Module):
    _input_ports = [('label', basic_modules.String,
                     {'optional': True}),
                    ('carry_on', basic_modules.Boolean,
                     {'optional': True, 'defaults': "['False']"}),
                    ('cell', Module)]
    _output_ports = [('result', basic_modules.Boolean)]

    def compute(self):
        cell = self.getInputFromPort('cell').cellWidget
        label = self.forceGetInputFromPort('label', None)

        result = PromptWindow(cell, label).exec_() == QtGui.QDialog.Accepted

        self.setResult('result', result)

        if not result and not self.getInputFromPort('carry_on'):
            raise ModuleError(self, "Execution aborted")

        # TODO : put widget back in the spreadsheet


_modules = [PromptIsOkay]
