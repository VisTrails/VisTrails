from PyQt4 import QtCore, QtGui

from vistrails.core import get_vistrails_application
from vistrails.core.parallelization.preferences import ExecutionTarget
from vistrails.core.utils.color import ColorGenerator
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

from .parallel_thread import QParallelThreadSettings
from .parallel_process import QParallelProcessSettings
from .parallel_ipython import QParallelIPythonSettings, \
    QParallelIPythonStandaloneSettings


class SchemeWidgetWrapper(QtGui.QGroupBox):
    def __init__(self, parent, widget, color, removable=True):
        QtGui.QWidget.__init__(self, widget.description)

        self.widget = widget

        layout = QtGui.QVBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        if removable:
            self._remove_button = QtGui.QToolButton(self)
            self._remove_button.setText("X")
            self._remove_button.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                        QtGui.QSizePolicy.Fixed)
            self.connect(self._remove_button, QtCore.SIGNAL('clicked()'),
                         lambda: parent.remove_widget(self))
        else:
            self._remove_button = None

        self.color = color
        color = tuple(i*255 for i in color)
        self.setStyleSheet(
                '''
                SchemeWidgetWrapper {
                    border-style: inset;
                    border-width: 2px;
                    border-radius: 3px;
                    border-color: rgb(%d, %d, %d);
                    margin-top: 4px;
                }
                ''' % color)

        self.do_layout()

    def resizeEvent(self, event):
        super(SchemeWidgetWrapper, self).resizeEvent(event)
        self.do_layout()

    def do_layout(self):
        if self._remove_button:
            self._remove_button.setGeometry(
                    self.width() - self._remove_button.width() - 3,
                    2,
                    self._remove_button.minimumSizeHint().width(),
                    self._remove_button.minimumSizeHint().height())


class UnknownSystem(QtGui.QWidget):
    """Configuration widget displayed for unknown schemes.

    The execution configuration file can contain unknown parallelization
    schemes that are here because the configuration was generated on a
    different version of VisTrails. In this case, the scheme won't be usable
    (no module will use it when executing) but we still display it and keep the
    info (unless the user removes it from this UI).
    """
    def __init__(self, target):
        QtGui.QWidget.__init__(self)
        self.setEnabled(False)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(
                QtGui.QLabel("Unknown scheme: %s" % target.scheme))
        self.setLayout(layout)


class QParallelizationSettings(QtGui.QWidget, QVistrailsPaletteInterface):
    WIDGETS = {
            # These two are handled separately, because they are always in the
            # list but can be enabled/disabled
            # 'threading': QParallelThreadSettings,
            # 'multiprocessing': QParallelProcessSettings,
            'ipython': QParallelIPythonSettings,
            'ipython-standalone': QParallelIPythonStandaloneSettings,
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
                         lambda s=scheme: self.new_target(s))

        layout = QtGui.QVBoxLayout()
        add_button = QtGui.QPushButton("Add scheme...")
        add_button.setMenu(self._add_menu)
        layout.addWidget(add_button)
        self._list = QtGui.QListWidget()
        layout.addWidget(self._list)
        self.setLayout(layout)

        self._widgets = {}          # wrapper -> (listitem, target)
        self._target2widget = {}    # target_id: int -> wrapper

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
            config = vistrail.get_persisted_execution_configuration()
        else:
            config = None

        if config is self.config:
            return

        self._widgets = {}
        self._target2widget = {}
        self._list.clear()

        self.vistrail = vistrail
        self.config = config

        self.colors = iter(ColorGenerator())

        self.threading = None
        self.multiprocessing = None

        if vistrail is None:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

            # Build widget from configuration
            for target in self.config.execution_targets:
                if target.scheme == 'threading':
                    self.threading = QParallelThreadSettings(self,
                                                             target)
                elif target.scheme == 'multiprocessing':
                    self.multiprocessing = QParallelProcessSettings(self,
                                                                    target)
                else:
                    self.add_target(target)

        if self.threading is None:
            self.threading = QParallelThreadSettings(self, None)
        self.threading_color = self.colors.next()
        self._add_widget(SchemeWidgetWrapper(self,
                                             self.threading,
                                             self.threading_color,
                                             removable=False))

        if self.multiprocessing is None:
            self.multiprocessing = QParallelProcessSettings(self, None)
        self.multiprocessing_color = self.colors.next()
        self._add_widget(SchemeWidgetWrapper(self,
                                             self.multiprocessing,
                                             self.multiprocessing_color,
                                             removable=False))

    def _add_widget(self, widget):
        item = QtGui.QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self._list.addItem(item)
        self._list.setItemWidget(item, widget)
        return item

    def new_target(self, scheme):
        target_id = self.vistrail.idScope.getNewId(ExecutionTarget.vtType)
        target = ExecutionTarget(id=target_id,
                                 scheme=scheme)
        self.config.add_execution_target(target)
        self.add_target(target)

    def add_target(self, target):
        widget_klass = self.WIDGETS.get(target.scheme, UnknownSystem)
        widget = widget_klass(self, target)
        wrapper = SchemeWidgetWrapper(self, widget, self.colors.next())
        item = self._add_widget(wrapper)
        self._widgets[wrapper] = item, target
        self._target2widget[target.id] = wrapper

    def remove_widget(self, wrapper):
        item, target = self._widgets[wrapper]
        wrapper.widget.remove()
        self._list.model().removeRow(self._list.indexFromItem(item).row())
        self.delete_execution_target(target)
        del self._widgets[wrapper]
        del self._target2widget[target.id]

    def delete_execution_target(self, target):
        # This removes the association with modules in cascade
        self.config.delete_execution_target(target)

        app = get_vistrails_application()
        controller = app.get_current_controller()

        # Update the pipeline
        controller.vistrail.set_execution_preferences(
                controller.current_pipeline)

        # Now we need to update the pipeline view
        # Refresh everything
        scene = controller.current_pipeline_scene
        scene.update_parallel_markers()
        # It's hard to use recreate_module() here with specific ids because we
        # don't even know what (sub)pipeline is displayed...

        self.set_changed()

    def set_changed(self):
        get_vistrails_application().get_current_controller().set_changed(True)

    @staticmethod
    def describe_target(target):
        """Makes a readable string describing an execution target.
        """
        if not target.scheme:
            return "Local execution"
        try:
            widget_klass = QParallelizationSettings.ALL_WIDGETS[target.scheme]
        except KeyError:
            return "Unknown scheme: %s" % target.scheme
        else:
            return widget_klass.describe(target)

    @classmethod
    def get_target_color(klass, target):
        self = klass.instance()
        if not target.scheme:
            return None
        elif target.scheme == 'threading':
            return self.threading_color
        elif target.scheme == 'multiprocessing':
            return self.multiprocessing_color
        else:
            return self._target2widget[target.id].color
