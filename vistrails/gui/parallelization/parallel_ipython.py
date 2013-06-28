from PyQt4 import QtCore, QtGui

from vistrails.core.parallelization.parallel_ipython import IPythonScheme, \
    EngineManager
from .remote_buttongroup import add_to_remote_buttongroup


class QParallelIPythonSettings(QtGui.QWidget):
    TAB_NAME = 'ipython'

    def __init__(self):
        QtGui.QWidget.__init__(self)

        layout = QtGui.QVBoxLayout()

        checkbox = QtGui.QCheckBox("Use IPython for remote execution")
        checkbox.setChecked(False)
        self._global_enable = False
        self.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                    self.enable_clicked)
        add_to_remote_buttongroup(checkbox)
        layout.addWidget(checkbox)

        has_vistrails = QtGui.QCheckBox("Cluster has VisTrails")
        has_vistrails.setChecked(True)
        self._has_vistrails = True
        self.connect(has_vistrails, QtCore.SIGNAL('stateChanged(int)'),
                     self.has_vistrails_clicked)

        start_engines_button = QtGui.QPushButton("Start new engines processes")
        self.connect(start_engines_button, QtCore.SIGNAL('clicked()'),
                     lambda: EngineManager.start_engines())
        layout.addWidget(start_engines_button)

        info_button = QtGui.QPushButton("Show information on the cluster")
        self.connect(info_button, QtCore.SIGNAL('clicked()'),
                     lambda: EngineManager.info())
        layout.addWidget(info_button)

        change_profile_button = QtGui.QPushButton("Change profile")
        self.connect(change_profile_button, QtCore.SIGNAL('clicked()'),
                     lambda: EngineManager.change_profile())
        layout.addWidget(change_profile_button)

        cleanup_button = QtGui.QPushButton("Cleanup started processes")
        self.connect(cleanup_button, QtCore.SIGNAL('clicked()'),
                     lambda: EngineManager.cleanup())
        layout.addWidget(cleanup_button)

        shutdown_cluster_button = QtGui.QPushButton("Request cluster shutdown")
        self.connect(shutdown_cluster_button, QtCore.SIGNAL('clicked()'),
                     lambda: EngineManager.shutdown_cluster())
        layout.addWidget(shutdown_cluster_button)

        layout.addStretch()

        self.setLayout(layout)

    def enable_clicked(self, state):
        self._global_enable = state == QtCore.Qt.Checked
        self.enable_disable_schemes()

    def has_vistrails_clicked(self, state):
        self._has_vistrails = state == QtCore.Qt.Checked

    def enable_disable_schemes(self):
        IPythonScheme.set_enabled(self._global_enable and self._has_vistrails)
        #IPythonStandaloneScheme.set_enabled(self._global_enable)
