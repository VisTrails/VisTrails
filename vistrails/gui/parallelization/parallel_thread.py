import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.parallelization.preferences import ExecutionTarget


class QParallelThreadSettings(QtGui.QWidget):
    description = 'Python threads'

    def __init__(self, parent, target):
        QtGui.QWidget.__init__(self)

        self._parent = parent
        self._target = target

        self._default_threads = max(multiprocessing.cpu_count(), 2)

        layout = QtGui.QHBoxLayout()

        checkbox = QtGui.QCheckBox("Enabled")
        checkbox.setChecked(target is not None)
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        layout.addWidget(checkbox)

        layout.addStretch()

        self._threads = QtGui.QSpinBox()
        self._threads.setRange(0, 32)
        self._threads.setSpecialValueText("autodetect (%d)" %
                                    self._default_threads)
        self._threads.setValue(getattr(get_vistrails_configuration(),
                                 'parallelThread_number'))
        if target is not None:
            annotation = target.get_annotation('pool_size')
            if annotation is not None:
                self._threads.setValue(int(annotation.value))

        self.connect(self._threads, QtCore.SIGNAL('valueChanged(int)'),
                     self.threads_changed)
        layout.addWidget(QtGui.QLabel("number:"))
        layout.addWidget(self._threads)
        layout.addStretch()

        self.setLayout(layout)

        self._threads.setEnabled(target is not None)

    def enable_clicked(self, state):
        if state == QtCore.Qt.Checked:
            if self._target is None:
                target_id = self._parent.vistrail.idScope.getNewId(
                        ExecutionTarget.vtType)
                self._target = ExecutionTarget(
                        id=target_id,
                        scheme='threading')
                self._parent.config.add_execution_target(self._target)
            self._target.set_annotation(
                    self._parent.vistrail.idScope,
                    'pool_size',
                    self._threads.value())
            self._parent.set_changed()
        else:
            if self._target is not None:
                self._parent.delete_execution_target(
                        self._target)
                self._target = None
                self._parent.set_changed()

        self._threads.setEnabled(state == QtCore.Qt.Checked)

    def threads_changed(self, nb):
        setattr(get_vistrails_persistent_configuration(),
                'parallelThread_number',
                nb)
        if self._target:
            if nb == 0:
                nb = self._default_threads
            self._target.set_annotation(
                    self._parent.vistrail.idScope,
                    'pool_size', nb)
            self._parent.set_changed()

    @staticmethod
    def describe(target):
        if target.scheme != 'threading':
            raise ValueError

        # There can be only one instance of the threading scheme so there is no
        # need to display any kind of parameter in the description
        return QParallelThreadSettings.description
