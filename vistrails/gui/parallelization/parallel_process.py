import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.parallelization.parallel_process import ProcessScheme


class QParallelProcessSettings(QtGui.QWidget):
    TAB_NAME = 'multiprocessing'

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self._default_processes = multiprocessing.cpu_count()

        layout = QtGui.QVBoxLayout()

        checkbox = QtGui.QCheckBox("Use multiprocessing:")
        checkbox.setChecked(True)
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        layout.addWidget(checkbox)

        form = QtGui.QFormLayout()
        processes = QtGui.QSpinBox()
        processes.setRange(0, 16)
        processes.setSpecialValueText("autodetect (%d)" %
                                      self._default_processes)
        processes.setValue(getattr(get_vistrails_configuration(),
                                   'parallelProcess_number'))
        self.processes_changed(processes.value())
        self.connect(processes, QtCore.SIGNAL('valueChanged(int)'),
                     self.processes_changed)
        form.addRow("Number of processes:", processes)
        layout.addLayout(form)

        layout.addStretch()

        self.setLayout(layout)

    def enable_clicked(self, state):
        ProcessScheme.set_enabled(state == QtCore.Qt.Checked)

    def processes_changed(self, nb):
        setattr(get_vistrails_persistent_configuration(),
                'parallelProcess_number',
                nb)
        if nb == 0:
            nb = self._default_processes
        ProcessScheme.set_pool_size(nb)
