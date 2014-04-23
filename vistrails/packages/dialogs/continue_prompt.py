from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.modules import basic_modules
from vistrails.core.modules.vistrails_module import Module, ModuleError

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellContainer


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
                    ('cell', SpreadsheetCell)]
    _output_ports = [('result', basic_modules.Boolean)]

    def compute(self):
        vt_configuration = get_vistrails_configuration()
        if not getattr(vt_configuration, 'interactiveMode', False):
            self.setResult('result', True)
            return

        cell = self.getInputFromPort('cell')
        label = self.forceGetInputFromPort('label', None)

        # FIXME : This should be done via the spreadsheet, removing it properly
        # and then sending a new DisplayCellEvent
        # However, there is currently no facility to remove the widget from
        # wherever it is
        oldparent = cell.parent()
        assert isinstance(oldparent, QCellContainer)
        ncell = oldparent.takeWidget()
        assert ncell == cell
        dialog = PromptWindow(cell, label)
        result = dialog.exec_() == QtGui.QDialog.Accepted
        oldparent.setWidget(cell)

        self.setResult('result', result)

        if not result and not self.getInputFromPort('carry_on'):
            raise ModuleError(self, "Execution aborted")


_modules = [PromptIsOkay]
