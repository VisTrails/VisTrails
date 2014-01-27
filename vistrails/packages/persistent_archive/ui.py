from PyQt4 import QtCore, QtGui

import file_archive.viewer
from file_archive.viewer import StoreViewerWindow

from vistrails.core.application import get_vistrails_application
from vistrails.core.db.locator import FileLocator

from .common import get_default_store


class VistrailsViewerWindow(StoreViewerWindow):
    WINDOW_TITLE = "Persistent archive viewer"

    _vt_only = True

    def __init__(self, store):
        StoreViewerWindow.__init__(self, store)

        # Search with no condition: list all entries (there is a limit)
        self._search()

    def _create_buttons(self):
        buttons = super(VistrailsViewerWindow, self)._create_buttons()

        open_vt_button = QtGui.QPushButton("Go to Vistrail")
        self.connect(open_vt_button, QtCore.SIGNAL('clicked()'),
                     self._open_vt)
        buttons.append(('vt', open_vt_button))

        only_vt_checkbox = QtGui.QCheckBox("Only VisTrails Persisted files")
        only_vt_checkbox.setChecked(self._vt_only)
        self.connect(only_vt_checkbox, QtCore.SIGNAL('stateChanged(int)'),
                     self._set_vt_only)
        buttons.append(('alwayson', only_vt_checkbox))

        return buttons

    def _set_vt_only(self, state):
        state = state == QtCore.Qt.Checked
        if state == self._vt_only:
            return
        self._vt_only = state
        self._search()

    def _alter_search_conditions(self, conditions):
        if self._vt_only and not 'vistrails_workflow' in conditions:
            conditions['vistrails_workflow'] = {'type': 'str'}
        return conditions

    def _selection_changed(self):
        super(VistrailsViewerWindow, self)._selection_changed()
        items = self._result_tree.selectedItems()
        for t, button in self._buttons:
            if t == 'vt':
                button.setEnabled(
                        len(items) == 1 and
                        self._find_vt(items[0]) is not None)

    @staticmethod
    def _find_vt(item):
        if isinstance(item, file_archive.viewer.MetadataItem):
            item = item.parent()
        metadata = item.entry.metadata
        try:
            workflow = metadata['vistrails_workflow']
            module_id = metadata['vistrails_module_id']
        except KeyError:
            return None
        return (workflow, module_id)

    def _open_vt(self):
        items = self._result_tree.selectedItems()
        item = items[0]
        vt = self._find_vt(item)
        if vt is None:
            return
        workflow, module_id = vt

        if ':' in workflow:
            filename, version = workflow.rsplit(':', 1)
            try:
                version = int(version)
            except ValueError:
                filename, version = workflow, None
        else:
            filename, version = workflow, None

        app = get_vistrails_application()
        if (not app.is_running_gui() or not hasattr(app, 'builderWindow') or
                app.builderWindow is None):
            return

        view = app.builderWindow.open_vistrail(FileLocator(filename),
                                               version=version)
        if module_id is not None:
            from vistrails.gui.pipeline_view import QGraphicsModuleItem

            scene = view.controller.current_pipeline_view.scene()
            for module_item in (i for i in scene.items()
                                  if isinstance(i, QGraphicsModuleItem)):
                if module_item.module.id == module_id:
                    module_item.setSelected(True)
                    break


store = get_default_store()
viewer = VistrailsViewerWindow(store)


def show_viewer():
    viewer.show()
