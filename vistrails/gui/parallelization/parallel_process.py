from PyQt4 import QtCore, QtGui

from vistrails.core.parallelization.parallel_process import ProcessScheme


class QParallelProcessSettings(QtGui.QWidget):
    TAB_NAME = 'multiprocessing'

    def __init__(self):
        QtGui.QWidget.__init__(self)

        layout = QtGui.QFormLayout()

        checkbox = QtGui.QCheckBox()
        checkbox.setChecked(True)
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        layout.addRow("Use multiprocessing:", checkbox)

        self.setLayout(layout)

    def enable_clicked(self, state):
        ProcessScheme.set_enabled(state == QtCore.Qt.Checked)
