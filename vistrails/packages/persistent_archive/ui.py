###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from __future__ import division

from PyQt4 import QtCore, QtGui

import file_archive.viewer
from file_archive.viewer import StoreViewerWindow

from vistrails.core.application import get_vistrails_application
from vistrails.core.db.locator import FileLocator

from .common import get_default_store, KEY_WORKFLOW, KEY_MODULE_ID


class VistrailsViewerWindow(StoreViewerWindow):
    WINDOW_TITLE = "Persistent archive viewer"

    _vt_only = True

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
        if self._vt_only and not KEY_WORKFLOW in conditions:
            conditions[KEY_WORKFLOW] = {'type': 'str'}
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
            workflow = metadata[KEY_WORKFLOW]
            module_id = metadata[KEY_MODULE_ID]
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


_viewer = None


def show_viewer():
    global _viewer
    if _viewer is None:
        store = get_default_store()
        _viewer = VistrailsViewerWindow(store)
    _viewer.show()
