import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.parallelization.preferences import ExecutionPreference


class QParallelProcessSettings(QtGui.QWidget):
    description = 'Python multiprocessing'

    def __init__(self, parent, preference):
        QtGui.QWidget.__init__(self)

        self._parent = parent
        self._preference = preference

        self._default_processes = multiprocessing.cpu_count()

        layout = QtGui.QHBoxLayout()

        checkbox = QtGui.QCheckBox("Enabled")
        checkbox.setChecked(preference is not None)
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        layout.addWidget(checkbox)

        layout.addStretch()

        self._processes = QtGui.QSpinBox()
        self._processes.setRange(0, 16)
        self._processes.setSpecialValueText("autodetect (%d)" %
                                      self._default_processes)
        self._processes.setValue(getattr(get_vistrails_configuration(),
                                   'parallelProcess_number'))
        if preference is not None:
            annotation = preference.get_annotation('pool_size')
            if annotation is not None:
                self._processes.setValue(int(annotation.value))

        self.connect(self._processes, QtCore.SIGNAL('valueChanged(int)'),
                     self.processes_changed)
        layout.addWidget(QtGui.QLabel("number:"))
        layout.addWidget(self._processes)
        layout.addStretch()

        self.setLayout(layout)

        self._processes.setEnabled(preference is not None)

    def enable_clicked(self, state):
        if state == QtCore.Qt.Checked:
            if self._preference is None:
                pref_id = self._parent.vistrail.idScope.getNewId(
                        ExecutionPreference.vtType)
                self._preference = ExecutionPreference(
                        id=pref_id,
                        system='multiprocessing')
                self._parent.config.add_execution_preference(self._preference)
            self._preference.set_annotation(
                    self._parent.vistrail.idScope,
                    'pool_size',
                    '%d' % self._processes.value())
            self._parent.set_changed()
        else:
            if self._preference is not None:
                self._parent.config.delete_execution_preference(
                        self._preference)
                self._preference = None
                self._parent.set_changed()

        self._processes.setEnabled(state == QtCore.Qt.Checked)

    def processes_changed(self, nb):
        setattr(get_vistrails_persistent_configuration(),
                'parallelProcess_number',
                nb)
        if self._preference:
            if nb == 0:
                nb = self._default_processes
            self._preference.set_annotation(
                    self._parent.vistrail.idScope,
                    'pool_size', nb)
            self._parent.set_changed()
