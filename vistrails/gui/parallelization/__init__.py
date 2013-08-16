from PyQt4 import QtCore, QtGui

from vistrails.core import get_vistrails_application
from vistrails.core.parallelization.preferences import ExecutionPreference
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

from .parallel_thread import QParallelThreadSettings
from .parallel_process import QParallelProcessSettings
#from .parallel_ipython import QParallelIPythonSettings#, \
    #QParallelIPythonStandaloneSettings


class SchemeWidgetWrapper(QtGui.QGroupBox):
    def __init__(self, parent, widget, removable=True):
        QtGui.QWidget.__init__(self, widget.description)

        self.widget = widget

        if removable:
            remove_button = QtGui.QPushButton("X")
            self.connect(remove_button, QtCore.SIGNAL('clicked'),
                         lambda: parent.remove_widget(self))

        layout = QtGui.QHBoxLayout()
        layout.addWidget(widget)
        if removable:
            layout.addStretch()
            layout.addWidget(remove_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class UnknownSystem(QtGui.QWidget):
    """Configuration widget displayed for unknown schemes.

    The execution configuration file can contain unknown parallelization
    schemes that are here because the configuration was generated on a
    different version of VisTrails. In this case, the scheme won't be usable
    (no module will use it when executing) but we still display it and keep the
    info (unless the user removes it from this UI).
    """
    def __init__(self, preference):
        QtGui.QWidget.__init__(self)
        self.setEnabled(False)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(
                QtGui.QLabel("Unknown scheme: %s" % preference.system))
        self.setLayout(layout)


class QParallelizationSettings(QtGui.QWidget, QVistrailsPaletteInterface):
    WIDGETS = {
            # These two are handled separately, because they are always in the
            # list but can be enabled/disabled
            # 'threading': QParallelThreadSettings,
            # 'multiprocessing': QParallelProcessSettings,
            #'ipython': QParallelIPythonSettings,
            #'ipython-standalone': QParallelIPythonStandaloneSettings,
        }

    ALL_WIDGETS = {
            'threading': QParallelThreadSettings,
            'multiprocessing': QParallelProcessSettings,
        }
    ALL_WIDGETS.update(WIDGETS)

    def __init__(self, parent=None):
        super(QParallelizationSettings, self).__init__(parent)

        self.setWindowTitle("Parallelization")

        self._add_menu = QtGui.QMenu()
        for scheme, widget_klass in self.WIDGETS.iteritems():
            action = QtGui.QAction(widget_klass.description, self)
            self._add_menu.addAction(action)
            self.connect(action, QtCore.SIGNAL('triggered()'),
                         lambda: self.add_scheme(scheme))

        layout = QtGui.QVBoxLayout()
        add_button = QtGui.QPushButton("Add scheme...")
        add_button.setMenu(self._add_menu)
        layout.addWidget(add_button)
        self._list = QtGui.QListWidget()
        layout.addWidget(self._list)
        self.setLayout(layout)

        self._schemes = {} # wrapper -> (listitem, preference)

        app = get_vistrails_application()
        app.register_notification(
                'controller_changed', self._check_vistrail)
        app.register_notification(
                'vistrail_saved', self._check_vistrail)
        self.vistrail = False
        self.config = False
        self._set_vistrail(None)

    def _check_vistrail(self, *args):
        controller = get_vistrails_application().get_current_controller()
        if controller is not None:
            self._set_vistrail(controller.vistrail)
        else:
            self._set_vistrail(None)

    def _set_vistrail(self, vistrail):
        if vistrail is not None:
            config = vistrail.get_persisted_execution_preferences()
        else:
            config = None

        if config is self.config:
            return

        self._schemes = {}
        self._list.clear()

        self.vistrail = vistrail
        self.config = config

        self.threading = None
        self.multiprocessing = None

        if vistrail is None:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

            # Build widget from configuration
            for preference in self.config.execution_preferences:
                if preference.system == 'threading':
                    self.threading = QParallelThreadSettings(self,
                                                             preference)
                elif preference.system == 'multiprocessing':
                    self.multiprocessing = QParallelProcessSettings(self,
                                                                    preference)
                else:
                    widget_klass = self.WIDGETS.get(
                            preference.system,
                            UnknownSystem)
                    widget = widget_klass(preference)
                    item = self._add_widget(widget)
                    wrapper = SchemeWidgetWrapper(self, widget)
                    self._schemes[wrapper] = item, preference

        if self.threading is None:
            self.threading = QParallelThreadSettings(self, None)
        self._add_widget(SchemeWidgetWrapper(self,
                                             self.threading,
                                             removable=False))
        if self.multiprocessing is None:
            self.multiprocessing = QParallelProcessSettings(self, None)
        self._add_widget(SchemeWidgetWrapper(self,
                                             self.multiprocessing,
                                             removable=False))

    def _add_widget(self, widget):
        item = QtGui.QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self._list.addItem(item)
        self._list.setItemWidget(item, widget)
        return item

    def add_scheme(self, scheme):
        pref_id = self.vistrail.idScope.getNewId(ExecutionPreference.vtType)
        preference = ExecutionPreference(id=pref_id,
                                         system=scheme)

        widget_klass = self.WIDGETS.get(scheme, UnknownSystem)
        widget = widget_klass()
        item = self._add_widget(widget)
        wrapper = SchemeWidgetWrapper(self, widget)
        self._schemes[wrapper] = item, preference

    def remove_widget(self, wrapper):
        item, preference = self._schemes[wrapper]
        self._list.removeItemWidget(item)
        self.widget.remove()
        self.config.delete_execution_preference(preference)

    def set_changed(self):
        get_vistrails_application().get_current_controller().set_changed(True)

    @staticmethod
    def describe_scheme(scheme):
        try:
            return QParallelizationSettings.ALL_WIDGETS[scheme].description
        except KeyError:
            return "Unknown scheme: %s" % scheme
