import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.parallelization.parallel_thread import ThreadScheme


class QParallelThreadSettings(QtGui.QWidget):
    TAB_NAME = 'threading'

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self._default_threads = max(multiprocessing.cpu_count(), 2)

        layout = QtGui.QVBoxLayout()

        checkbox = QtGui.QCheckBox("Use threads")
        checkbox.setChecked(True)
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        layout.addWidget(checkbox)

        form = QtGui.QFormLayout()
        threads = QtGui.QSpinBox()
        threads.setRange(0, 32)
        threads.setSpecialValueText("autodetect (%d)" %
                                    self._default_threads)
        threads.setValue(getattr(get_vistrails_configuration(),
                                 'parallelThread_number'))
        self.threads_changed(threads.value())
        self.connect(threads, QtCore.SIGNAL('valueChanged(int)'),
                     self.threads_changed)
        form.addRow("Number of threads:", threads)
        layout.addLayout(form)

        layout.addStretch()

        self.setLayout(layout)

    def enable_clicked(self, state):
        ThreadScheme.set_enabled(state == QtCore.Qt.Checked)

    def threads_changed(self, nb):
        setattr(get_vistrails_persistent_configuration(),
                'parallelThread_number',
                nb)
        if nb == 0:
            nb = self._default_threads
        ThreadScheme.set_pool_size(nb)
