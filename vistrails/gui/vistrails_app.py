###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
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
##  - Neither the name of the University of Utah nor the names of its 
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

from PyQt4 import QtCore, QtGui
import copy

from core.db.locator import FileLocator, XMLFileLocator, untitled_locator
from core.db.io import load_vistrail
from core.modules.module_registry import ModuleRegistryException
from core.vistrail.vistrail import Vistrail

from gui.application import get_vistrails_application
from gui.theme import initializeCurrentTheme
from gui.palette_container import PaletteContainer
from gui.vistrails_window import QVistrailsWindow

class VisTrailsApp(QtGui.QMainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        global _app
        QtGui.QMainWindow.__init__(self, parent, f)
        self.windows = []
        self.palette_containers = []
        self.current_window = None
        self.notifications = {}
        self.dbDefault = False

        # FIXME not the best way to assign the global
        _app = self

        self.init_palettes()
        self.create_menus()
        self.connect(get_vistrails_application(), 
                     QtCore.SIGNAL('focusChanged(QWidget*, QWidget*)'),
                     self.window_changed)

    def init_palettes(self):
        # palettes are global!
        from gui.module_configuration import QModuleConfiguration
        from gui.module_documentation import QModuleDocumentation
        from gui.module_palette import QModulePalette
        from gui.module_info import QModuleInfo
        from gui.version_prop import QVersionProp
        self.palettes = []
        palette_layout = [[QModulePalette], 
                          [(QModuleInfo, 
                            (('controller_changed', 'set_controller'),
                             ('module_changed', 'update_module'))),
                           (QVersionProp, 
                            (('controller_changed', 'updateController'),
                             ('version_changed', 'updateVersion')))],
                          [(QModuleConfiguration, 
                            (('controller_changed', 'set_controller'),
                             ('module_changed', 'updateModule'))),
                           (QModuleDocumentation,
                            (('controller_changed', 'set_controller'),
                             ('module_changed', 'update_module'),
                             ('descriptor_changed', 'update_descriptor')))]]
        for p_group in palette_layout:
            # first_added = None
            container = PaletteContainer()
            for p_klass in p_group:
                notifications = []
                if type(p_klass) == tuple:
                    p_klass, notifications = p_klass
                palette = p_klass(self)
                self.palettes.append(palette)
                container.add_palette(palette)
                for n_tuple in notifications:
                    if type(n_tuple) == tuple:
                        if len(n_tuple) > 1:
                            n_id, method_name = n_tuple
                        else:
                            n_id = n_tuple[0]
                            method_name = n_tuple[0]
                    else:
                        n_id = n_tuple
                        method_name = n_tuple
                    method = getattr(palette, method_name)
                    self.register_notification(n_id, method)
                # palette.toolWindow().show()
                # palette.toolWindow().setFloating(True)
                # if first_added is not None:
                #     self.tabifyDockWidget(first_added, palette.toolWindow())
                # first_added = palette.toolWindow()
            container.toolWindow().show()
            container.toolWindow().setFloating(True)
            container.toolWindow().hide()
            self.palette_containers.append(container)

    def create_notification(self, notification_id):
        if notification_id not in self.notifications:
            self.notifications[notification_id] = set()
        else:
            print "already added notification", notification_id

    def register_notification(self, notification_id, method):
        if notification_id not in self.notifications:
            self.create_notification(notification_id)
        self.notifications[notification_id].add(method)

    def unregister_notification(self, notification_id, method):
        if notification_id in self.notifications:
            self.notifications[notification_id].remove(method)

    def notify(self, notification_id, *args):
        if notification_id in self.notifications:
            for m in self.notifications[notification_id]:
                m(*args)

    def add_window(self, vistrail):
        window = QVistrailsWindow(vistrail)
        self.connect(window, QtCore.SIGNAL("focus(QWidget*)"), 
                     self.window_changed)
        self.windows.append(window)
        window.show()
        return window
    
    # def window_changed(self, new_window):
    def window_changed(self, old_window, new_window):
        # if window != self.current_window:
        #     print "NOT CURRENT WINDOW"
        #     self.current_window = window
        #     self.notify('controller_changed', window.get_controller())
        # else:
        #     print "CURRENT WINDOW"
        
        new_window = get_vistrails_application().activeWindow()
        if isinstance(new_window, QVistrailsWindow):
            if self.current_window != new_window:
                # print "CURRENT WINDOW CHANGED"
                self.current_window = new_window
                self.notify('controller_changed', new_window.get_controller())
        # else:
        #     print "NOT VISTRAILS WINDOW", type(new_window)
            
    def default_layout(self):
        geom_rect = QtGui.QApplication.desktop().availableGeometry()
        x = geom_rect.x()
        y = geom_rect.y()
        if geom_rect.width() > 1280:
            width = 1280
        else:
            width = geom_rect.width()
        if geom_rect.height() > 800:
            height = 800
        else:
            height = geom_rect.height()
        
        w = self.palette_containers[0].toolWindow()
        w.setGeometry(x, y, 256, height - 8)
        w.show()
 
        w = self.windows[0]
        w.setGeometry(x+256,y,width - 512, height - 12)
        w.show()

        w = self.palette_containers[1].toolWindow()
        w.setGeometry(x + width - 256, y, 256, height - 8)
        w.show()

    def show(self):
        # for window in self.windows:
        #     window.show()
        # for palette_container in self.palette_containers:
        #     palette_container.toolWindow().show()
        self.default_layout()

    def hide(self):
        for window in self.windows:
            window.hide()
        for palette_container in self.palette_containers:
            palette_container.toolWindow().hide()

    def create_menus(self):
        global _menu_bar 
        self.fileMenu = _menu_bar.addMenu('&File')
        self.newVistrailAction = QtGui.QAction('&New', self)
        self.newVistrailAction.setShortcut('Ctrl+N')
        self.newVistrailAction.setStatusTip('Create a new vistrail')
        self.openFileAction = QtGui.QAction('&Open', self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setStatusTip('Open an existing vistrail from '
                                         'a file')
        
        self.fileMenu.addAction(self.newVistrailAction)
        self.fileMenu.addAction(self.openFileAction)

        trigger_actions = [(self.newVistrailAction, self.new_vistrail),
                           (self.openFileAction, self.open_vistrail_default)]
        for (emitter, receiver) in trigger_actions:
            self.connect(emitter, QtCore.SIGNAL('triggered()'), receiver)

    def create_first_vistrail(self):
        self.new_vistrail()

    def new_vistrail(self, recover_files=True):
        # if self.single_document_mode and self.currentView():
        #     if not self.closeVistrail():
        #         return None
        if recover_files and untitled_locator().has_temporaries():
            locator = copy.copy(untitled_locator())
        else:
            locator = None
        # try:
        #     (vistrail, abstraction_files, thumbnail_files) = load_vistrail(locator)
        # except ModuleRegistryException, e:
        #     debug.critical("Module registry error for %s" %
        #                    str(e.__class__.__name__), str(e))
        # except Exception, e:
        #     debug.critical('An error has occurred', str(e))
        #     raise
        # return self.set_vistrail_view(vistrail, locator, abstraction_files,
        #                               thumbnail_files)
        
        self.open_vistrail(locator)

    def open_vistrail(self, locator, version=None, is_abstraction=False):
        """open_vistrail(locator: Locator, version = None: int or str,
                         is_abstraction: bool)

        opens a new vistrail from the given locator, selecting the
        given version.

        """
        # self.close_first_vistrail_if_necessary()
        # if self.single_document_mode and self.currentView():
        #     self.closeVistrail()
        # view = self.ensureVistrail(locator)
        # if view:
        #     if version is not None:
        #         if type(version) == type(""):
        #             try:
        #                 version = view.vistrail.get_version_number(version)
        #             except:
        #                 version = None
        #         if version is not None:
        #             view.setup_view(version)
        #     return view
        try:
            (vistrail, abstraction_files, thumbnail_files, _) = \
                                        load_vistrail(locator, is_abstraction)
            window = self.add_window(vistrail)
            self.window_changed(None, window)
            # self.window_changed(window)
            # result = self.set_vistrail_view(vistrail, locator, 
            #                                 abstraction_files, thumbnail_files,
            #                                 version)
            # return result
        # except ModuleRegistryException, e:
        #     debug.critical("Module registry error for %s" %
        #                    str(e.__class__.__name__), str(e))
        except Exception, e:
            # debug.critical('An error has occurred', str(e))
            print "An error has occurred", str(e)
            raise

    def open_vistrail_from_locator(self, locator_class):
        """ open_vistrail(locator_class) -> None
        Prompt user for information to get to a vistrail in different ways,
        depending on the locator class given.
        """
        locator = locator_class.load_from_gui(self, Vistrail.vtType)
        if locator:
            if locator.has_temporaries():
                if not locator_class.prompt_autosave(self):
                    locator.clean_temporaries()
            if hasattr(locator, '_vnode'):
                version = locator._vnode
                if hasattr(locator,'_vtag'):
                    # if a tag is set, it should be used instead of the
                    # version number
                    if locator._vtag != '':
                        version = locator._vtag
            self.open_vistrail_without_prompt(locator, version)
            # self.set_current_locator(locator)

    def open_vistrail_without_prompt(self, locator, version=None,
                                     execute_workflow=False, 
                                     is_abstraction=False):
        """open_vistrail_without_prompt(locator_class, version: int or str,
                                        execute_workflow: bool,
                                        is_abstraction: bool) -> None
        Open vistrail depending on the locator class given.
        If a version is given, the workflow is shown on the Pipeline View.
        If execute_workflow is True the workflow will be executed.
        If is_abstraction is True, the vistrail is flagged as abstraction
        """
        if not locator.is_valid():
            ok = locator.update_from_gui(self)
        else:
            ok = True
        if ok:
            self.open_vistrail(locator, version, is_abstraction)
            # self.closeVistrailAction.setEnabled(True)
            # self.saveFileAsAction.setEnabled(True)
            # self.exportFileAction.setEnabled(True)
            # self.vistrailMenu.menuAction().setEnabled(True)
            # self.mergeMenu.menuAction().setEnabled(True)
            # self.viewManager.changeCursor(self.interactionToolBar.cursorMode)
            # if version:
            #     self.viewModeChanged(0)
            # else:
            #     self.viewModeChanged(1)
            # if execute_workflow:
            #     self.execute_current_pipeline()
                
        
    def open_vistrail_default(self):
        """ open_vistrail_default() -> None
        Opens a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail_from_locator(DBLocator)
        else:
            self.open_vistrail_from_locator(FileLocator())

    def link_registry(self):
        for palette in self.palettes:
            if hasattr(palette, 'link_registry'):
                palette.link_registry()

_app = None
_menu_bar = QtGui.QMenuBar()
        
if __name__ == '__main__':
    import gui.requirements
    gui.requirements.check_pyqt4()

    from PyQt4 import QtGui
    import gui.application
    import sys
    import os
    try:
        v = gui.application.start_application()
        if v != 0:
            if gui.application.get_vistrails_application():
                gui.application.get_vistrails_application().finishSession()
            sys.exit(v)
        app = gui.application.get_vistrails_application()()
    except SystemExit, e:
        if gui.application.get_vistrails_application():
            gui.application.get_vistrails_application().finishSession()
        sys.exit(e)
    except Exception, e:
        if gui.application.get_vistrails_application():
            gui.application.get_vistrails_application().finishSession()
        print "Uncaught exception on initialization: %s" % e
        import traceback
        traceback.print_exc()
        sys.exit(255)
    if (app.temp_configuration.interactiveMode and
        not app.temp_configuration.check('spreadsheetDumpCells')): 
        v = app.exec_()
        
    gui.application.stop_application()
    sys.exit(v)

    # app = QtGui.QApplication([])
    # initializeCurrentTheme()
    # top_window = VisTrailsApp()
    # # top_window.show()
    # app.exec_()
