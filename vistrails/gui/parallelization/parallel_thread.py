import multiprocessing

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.parallelization.preferences import ExecutionPreference


class QParallelThreadSettings(QtGui.QWidget):
    description = 'Python threads'

    def __init__(self, parent, preference):
        QtGui.QWidget.__init__(self)

        self._parent = parent
        self._preference = preference

        self._default_threads = max(multiprocessing.cpu_count(), 2)

        layout = QtGui.QHBoxLayout()

        checkbox = QtGui.QCheckBox("Enabled")
        checkbox.setChecked(preference is not None)
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
        if preference is not None:
            annotation = preference.get_annotation('pool_size')
            if annotation is not None:
                self._threads.setValue(int(annotation.value))

        self.connect(self._threads, QtCore.SIGNAL('valueChanged(int)'),
                     self.threads_changed)
        layout.addWidget(QtGui.QLabel("number:"))
        layout.addWidget(self._threads)
        layout.addStretch()

        self.setLayout(layout)

        self._threads.setEnabled(preference is not None)

    def enable_clicked(self, state):
        if state == QtCore.Qt.Checked:
            if self._preference is None:
                pref_id = self._parent._vistrail.idScope.getNewId(
                        ExecutionPreference.vtType)
                self._preference = ExecutionPreference(
                        id=pref_id,
                        system='threading')
                self._parent.config.add_execution_preference(self._preference)
            self._preference.set_annotation(
                    self._parent._vistrail.idScope,
                    'pool_size',
                    self._threads.value())
            self._parent.set_changed()
        else:
            if self._preference is not None:
                self._parent.config.delete_execution_preference(
                        self._preference)
                self._preference = None
                self._parent.set_changed()

        self._threads.setEnabled(state == QtCore.Qt.Checked)

    def threads_changed(self, nb):
        setattr(get_vistrails_persistent_configuration(),
                'parallelThread_number',
                nb)
        if self._preference:
            if nb == 0:
                nb = self._default_threads
            self._preference.set_annotation(
                    self._parent._vistrail.idScope,
                    'pool_size', nb)
            self._parent.set_changed()
