import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.parallelization.preferences import ExecutionTarget


class QParallelProcessSettings(QtGui.QWidget):
    description = 'Python multiprocessing'

    def __init__(self, parent, target):
        QtGui.QWidget.__init__(self)

        self._parent = parent
        self._target = target

        self._default_processes = multiprocessing.cpu_count()

        layout = QtGui.QHBoxLayout()

        checkbox = QtGui.QCheckBox("Enabled")
        checkbox.setChecked(target is not None)
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
        if target is not None:
            annotation = target.get_annotation('pool_size')
            if annotation is not None:
                self._processes.setValue(int(annotation.value))

        self.connect(self._processes, QtCore.SIGNAL('valueChanged(int)'),
                     self.processes_changed)
        layout.addWidget(QtGui.QLabel("number:"))
        layout.addWidget(self._processes)
        layout.addStretch()

        self.setLayout(layout)

        self._processes.setEnabled(target is not None)

    def enable_clicked(self, state):
        if state == QtCore.Qt.Checked:
            if self._target is None:
                target_id = self._parent.vistrail.idScope.getNewId(
                        ExecutionTarget.vtType)
                self._target = ExecutionTarget(
                        id=target_id,
                        scheme='multiprocessing')
                self._parent.config.add_execution_target(self._target)
            self._target.set_annotation(
                    self._parent.vistrail.idScope,
                    'pool_size',
                    '%d' % self._processes.value())
            self._parent.set_changed()
        else:
            if self._target is not None:
                self._parent.config.delete_execution_target(
                        self._target)
                self._target = None
                self._parent.set_changed()

        self._processes.setEnabled(state == QtCore.Qt.Checked)

    def processes_changed(self, nb):
        setattr(get_vistrails_persistent_configuration(),
                'parallelProcess_number',
                nb)
        if self._target:
            if nb == 0:
                nb = self._default_processes
            self._target.set_annotation(
                    self._parent.vistrail.idScope,
                    'pool_size', nb)
            self._parent.set_changed()

    @staticmethod
    def describe(target):
        if target.scheme != 'multiprocessing':
            raise ValueError

        # There can be only one instance of the multiprocessing scheme so there
        # is no need to display any kind of parameter in the description
        return QParallelProcessSettings.description
