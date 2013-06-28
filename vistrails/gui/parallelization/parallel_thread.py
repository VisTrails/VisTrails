import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.parallelization.parallel_thread import ThreadScheme


class QParallelThreadSettings(QtGui.QWidget):
    TAB_NAME = 'threading'

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self._default_threads = multiprocessing.cpu_count()

        layout = QtGui.QFormLayout()

        checkbox = QtGui.QCheckBox()
        checkbox.setChecked(True)
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        label = QtGui.QLabel("Use threads:")
        label.setBuddy(checkbox)
        layout.addRow(label, checkbox)

        processes = QtGui.QSpinBox()
        processes.setRange(0, 32)
        processes.setSpecialValueText("autodetect (%d)" %
                                      self._default_threads)
        self.connect(processes, QtCore.SIGNAL('valueChanged(int)'),
                     self.processes_changed)
        layout.addRow("Number of processes:", processes)

        self.setLayout(layout)

    def enable_clicked(self, state):
        ThreadScheme.set_enabled(state == QtCore.Qt.Checked)

    def processes_changed(self, nb):
        if nb == 0:
            nb = self._default_threads
        ThreadScheme.set_pool_size(nb)
