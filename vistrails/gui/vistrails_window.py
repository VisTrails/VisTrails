###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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
""" The file describes a container widget consisting of a pipeline
view and a version tree for each opened Vistrail """

from PyQt4 import QtCore, QtGui
import copy
from itertools import izip
import operator

from core.configuration import (get_vistrails_configuration,
                                get_vistrails_persistent_configuration)
from core.db.locator import FileLocator, XMLFileLocator, DBLocator, \
    untitled_locator
from core.db.io import load_vistrail
from core.interpreter.cached import CachedInterpreter
from core.modules.module_registry import ModuleRegistry, \
                                         ModuleRegistryException
from core.recent_vistrails import RecentVistrailList
import core.system
import core.db.action
from core.packagemanager import get_package_manager
from core.system import vistrails_default_file_type
from core.vistrail.vistrail import Vistrail
from core.vistrail.pipeline import Pipeline
from core.thumbnails import ThumbnailCache
from core.collection import Collection
from core import debug

from gui.application import VistrailsApplication
from gui.preferences import QPreferencesDialog
from gui.base_view import BaseView
from gui.pipeline_view import QPipelineView
from gui.repository import QRepositoryDialog
from gui.theme import initializeCurrentTheme, CurrentTheme
from gui.utils import build_custom_window
from gui.vistrail_view import QVistrailView
from gui import merge_gui
from gui.vistrail_variables import QVistrailVariables

from db.services.io import SaveBundle
import db.services.vistrail


class QVistrailsWindow(QtGui.QMainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        global _app
        QtGui.QMainWindow.__init__(self, parent, f)

        self.current_view = None
        self.windows = {}
        self.notifications = {}
        self.view_notifications = {}
        self.view_notifications[-1] = {}
        self.action_links = {}
        self.dbDefault = False

        # FIXME not the best way to assign the global
        _app = self

        self.stack = QtGui.QStackedWidget()
        self.vistrail_to_widget = {}
        self.setCentralWidget(self.stack)
        self.setDocumentMode(True)
        
        # This keeps track of the menu items for each package
        self._package_menu_items = {}
        
        self.init_palettes()
        self.create_menus()
        self.setup_recent_vistrails()
        self.init_toolbar()

        self._focus_owner = None
        self.connect(QtGui.QApplication.clipboard(),
                     QtCore.SIGNAL('dataChanged()'),
                     self.clipboard_changed)
        self.connect(QtGui.QApplication.instance(), 
                     QtCore.SIGNAL("focusChanged(QWidget*,QWidget*)"),
                     self.applicationFocusChanged)

    def create_view(self, vistrail, locator,  abstraction_files=None, 
                                    thumbnail_files=None, mashups=None):
        from gui.collection.workspace import QWorkspaceWindow
        view = QVistrailView(vistrail, locator, abstraction_files,
                             thumbnail_files, mashups)
        self.vistrail_to_widget[view.get_name()] = view
        index = self.stack.addWidget(view)
        self.stack.setCurrentIndex(index)
        self.view_notifications[view] = {}
        for notification_id, method in view.get_notifications().iteritems():
            self.register_notification(notification_id, method, True, view)

        QWorkspaceWindow.instance().add_vt_window(view)

        return view

    def remove_view(self, view):
        from gui.collection.workspace import QWorkspaceWindow
        if not self.windows.has_key(view):
            if self.view_notifications.has_key(view):
                del self.view_notifications[view]
            self.stack.removeWidget(view)
        else:
            window = self.windows[view]
            window.close()
        QWorkspaceWindow.instance().remove_vt_window(view)

    def init_toolbar(self):
        def create_spacer():
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                                  QtGui.QSizePolicy.Preferred)
            return spacer
        def create_separator():
            sep = QtGui.QWidget()
            sep.setMinimumWidth(50)
            return sep
        # have a toolbar
        # self.create_pass_actions()
        # self.toolbar = QtGui.QToolBar(self)
        # history_action = QtGui.QAction("History", self)
        # history_action.method = self.history_selected
        # history_action.un_method = self.history_unselected
        # query_action = QtGui.QAction("Search", self)
        # query_action.method = self.query_selected
        # query_action.un_method = self.query_unselected
        # explore_action = QtGui.QAction("Explore", self)
        # explore_action.method = self.explore_selected
        # explore_action.un_method = self.explore_unselected
        # toolbar_actions = [history_action, query_action, explore_action]
        # self.action_group = QtGui.QActionGroup(self)
        # for action in toolbar_actions:
        #     action.setCheckable(True)
        #     self.action_group.addAction(action)
        # self.connect(self.action_group, QtCore.SIGNAL("triggered(QAction *)"), 
        #              self.action_triggered)
        # self.toolbar.addAction(history_action)
        # self.toolbar.addAction(query_action)
        # self.toolbar.addAction(explore_action)
        # self.addToolBar(self.toolbar)
        self.selected_mode = None
        self.toolbar = QtGui.QToolBar(self)
        
        #left side
        for action in [self.qactions[n] 
                       for n in ['newVistrail', 'openFile', 'saveFile']]:
            self.toolbar.addAction(action)
        
        self.toolbar.addWidget(create_spacer())
        
        #second group
        self.view_action_group = QtGui.QActionGroup(self)
        for action in [self.qactions[n] 
                       for n in ['pipeline', 'history', 
                                 'search', 'explore', 'provenance', 'mashup']]:
            self.toolbar.addAction(action)
            self.view_action_group.addAction(action)
        self.toolbar.addWidget(create_separator())
        # self.connect(self.view_action_group, 
        #              QtCore.SIGNAL("triggered(QAction*)"),
        #              self.view_triggered)
        #third group
        for action in [self.qactions[n] 
                       for n in ['execute']]:
            self.toolbar.addAction(action)
            
        
        self.toolbar.addWidget(create_spacer())
        self.toolbar.addWidget(create_spacer())
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        self.setUnifiedTitleAndToolBarOnMac(True)

    def view_triggered(self, action):
        print "VIEW_TRIGGERED", action
        if self.selected_mode == action:
            if action is not None:
                print "SETTING CHECKED FALSE"
                action.setChecked(False)
            self.selected_mode = None
        else:
            self.selected_mode = action
        current_view = self.stack.currentWidget()
        current_view.tab_state[current_view.tabs.currentIndex()] = \
            self.selected_mode
        current_view.view_changed()

    def action_triggered(self, action):
        if self.selected_mode is not None:
            self.selected_mode.un_method()
        if self.selected_mode != action:
            self.selected_mode = action
            if action is not None:
                action.method()
        elif self.selected_mode is not None:
            self.selected_mode = None
            action.setChecked(False)
        current_view = self.stack.currentWidget()
        current_view.tab_state[current_view.tabs.currentIndex()] = \
            self.selected_mode
        current_view.view_changed()

    def init_palettes(self):
        # palettes are global!
        from gui.debug import DebugView
        from gui.debugger import QDebugger
        from gui.module_configuration import QModuleConfiguration
        from gui.module_documentation import QModuleDocumentation
        from gui.module_palette import QModulePalette
        from gui.module_info import QModuleInfo
        from gui.paramexplore.param_view import QParameterView
        from gui.paramexplore.pe_palette import QParamExplorePalette
        from gui.shell import QShellDialog
        from gui.version_prop import QVersionProp
        from gui.vis_diff import QDiffProperties
        from gui.collection.explorer import QExplorerWindow
        from gui.collection.workspace import QWorkspaceWindow
        from gui.collection.vis_log import QLogDetails
        from gui.mashups.mashups_inspector import QMashupsInspector
        from gui.mashups.alias_parameter_view import QAliasParameterView
        from gui.publishing import QLatexAssistant as QVersionEmbed
        self.palettes = []
        self.palette_window = None
        
        self.palette_layout = [(QtCore.Qt.LeftDockWidgetArea, 
                           [(QModulePalette, True), (QWorkspaceWindow,True),
                            ((QParamExplorePalette, False),
                             (('pipeline_changed', 'set_pipeline'),
                              ('controller_changed', 'set_controller'))),
                             ((QMashupsInspector, False),
                              (('controller_changed', 'updateVistrailController'),
                               ('mshpcontroller_changed', 'updateMshpController'),
                               ('mshpversion_changed', 'updateMshpVersion'),
                               ('version_changed', 'updateVistrailVersion')))]),
                          (QtCore.Qt.RightDockWidgetArea,
                           [((QModuleInfo, True), 
                             (('controller_changed', 'set_controller'),
                              ('module_changed', 'update_module'))),
                            ((QVersionProp, True), 
                             (('controller_changed', 'updateController'),
                              ('version_changed', 'updateVersion'))),
                            ((QDiffProperties, False),
                             (('controller_changed', 'set_controller'),
                              ('module_changed', 'update_module'))),
                            ((QParameterView, False),
                             (('pipeline_changed', 'set_pipeline'),)),
                            ((QLogDetails, False),
                             (('controller_changed', 'set_controller'),
                              ('execution_updated', 'execution_updated'),
                              ('execution_changed', 'execution_changed'))),
                            ((QAliasParameterView, False),
                             (('mshpcontroller_changed', 'updateMshpController'),
                              ('mshpversion_changed', 'updateMshpVersion'))),
                            ((QVistrailVariables, False),
                             (('controller_changed', 'updateController'),))]),
                          (QtCore.Qt.NoDockWidgetArea,
                           [((QModuleConfiguration, True), 
                             (('controller_changed', 'set_controller'),
                              ('module_changed', 'updateModule'))),
                            ((QModuleDocumentation, True),
                             (('controller_changed', 'set_controller'),
                              ('module_changed', 'update_module'),
                              ('descriptor_changed', 'update_descriptor'))),
                            ((QShellDialog, True),
                             (('controller_changed', 'set_controller'),)),
                            ((QDebugger, True),
                             (('controller_changed', 'set_controller'),)),
                            (DebugView, True),
                            (QExplorerWindow, True),
                            ((QVersionEmbed, True),
                             (('controller_changed', 'set_controller'),))])]
        
        for dock_area, p_group in self.palette_layout:
            first_added = None
            for p_klass in p_group:
                notifications = []
                if type(p_klass) == tuple:
                    p_klass, visible = p_klass
                    if type(p_klass) == tuple:
                        notifications = visible
                        p_klass, visible = p_klass      
                print "generating instance", p_klass
                palette = p_klass.instance()
                print 'palette:', palette
                self.palettes.append(palette)
                for n_tuple in notifications:
                    print "n_tuple:", n_tuple
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
                if dock_area != QtCore.Qt.NoDockWidgetArea:
                    palette.set_pin_status(visible)
                    if first_added is None:
                        self.addDockWidget(dock_area, palette.toolWindow())
                        first_added = palette.toolWindow()
                    else:
                        self.tabifyDockWidget(first_added, palette.toolWindow())
                    if not visible:
                        palette.toolWindow().close()
                    
                else:
                    if first_added is None:
                        self.palette_window = QtGui.QMainWindow()
                        self.palette_window.setWindowTitle('VisTrails - Tools')
                        self.palette_window.setGeometry(200, 200, 768, 512)
                        self.palette_window.setDocumentMode(True)
                        self.palette_window.addDockWidget(
                            QtCore.Qt.TopDockWidgetArea, palette.toolWindow())
                        #self.palette_window.show()
                        first_added = palette.toolWindow()
                        palette.set_main_window(self.palette_window)
                    else:
                        self.palette_window.tabifyDockWidget(
                            first_added, palette.toolWindow())
                        palette.set_main_window(self.palette_window)
        if self.palette_window:
            self.palette_window.hide()
                        
        self.connect(QWorkspaceWindow.instance(), 
                     QtCore.SIGNAL("vistrailChanged(PyQt_PyObject)"),
                     self.change_view)
        self.connect(QWorkspaceWindow.instance(), 
                     QtCore.SIGNAL("detachVistrail"),
                     self.detach_view)

    def dock_palettes(self):
        window = QtGui.QApplication.activeWindow()
        if window == self or window in self.windows.values():
            left_first_added = None
            right_first_added = None
            for dock_area, p_group in self.palette_layout:
                for p_klass in p_group:
                
                    if type(p_klass) == tuple:
                        p_klass, visible = p_klass
                        if type(p_klass) == tuple:
                            notifications = visible
                            p_klass, visible = p_klass      
                    palette = p_klass.instance()
                    if dock_area == QtCore.Qt.RightDockWidgetArea:
                        pin_status = palette.get_pin_status()
                        palette.toolWindow().setParent(window)
                        if right_first_added is None:
                            window.addDockWidget(dock_area, palette.toolWindow())
                            right_first_added = palette.toolWindow()
                        else:
                            window.tabifyDockWidget(right_first_added, palette.toolWindow())
                    elif dock_area == QtCore.Qt.LeftDockWidgetArea:
                        pin_status = palette.get_pin_status()
                        palette.toolWindow().setParent(window)
                        if left_first_added is None:
                            window.addDockWidget(dock_area, palette.toolWindow())
                            left_first_added = palette.toolWindow()
                        else:
                            window.tabifyDockWidget(left_first_added, palette.toolWindow())
                    if not visible:
                        palette.toolWindow().close()
                    else:
                        palette.toolWindow().show()
                        
    def create_notification(self, notification_id, link_view=False, view=None):
        if link_view:
            if view is not None:
                notifications = self.view_notifications[view]
        else:
            notifications = self.notifications
        if notification_id not in notifications:
            notifications[notification_id] = set()
        else:
            print "already added notification", notification_id

    def register_notification(self, notification_id, method, link_view=False,
                              view=None):
        if link_view:
            if view is not None:
                notifications = self.view_notifications[view]
                #print '>>> LOCAL adding notification', notification_id, view, method
            #print id(notifications), notifications
            #for n, o in notifications.iteritems():
            #    print "    ", n , "(%s)"%len(o)
            #    for m in o:
            #        print "        ", m
        else:
            notifications = self.notifications     
            #print '>>> GLOBAL adding notification', notification_id, method  
            #print id(notifications), notifications
        if notification_id not in notifications:
            self.create_notification(notification_id, link_view, view)
        notifications[notification_id].add(method)

    def unregister_notification(self, notification_id, method, link_view=False,
                                view=None):
        if link_view:
            notifications = {}
            if self.view_notifications.has_key(view):
                notifications = self.view_notifications[view]
                #print '>>> LOCAL remove notification', notification_id, view
            
            #print id(notifications), notifications
#            for n, o in notifications.iteritems():
#                print "    ", n , "(%s)"%len(o)
#                for m in o:
#                    print "        ", m
        else:
            notifications = self.notifications    
            #print '>>> GLOBAL remove notification', notification_id, method   
            #print id(notifications), notifications           
        if notification_id in notifications:
            notifications[notification_id].remove(method)

    def notify(self, notification_id, *args):
        # do global notifications
        if notification_id in self.notifications:
            print 'global notification ', notification_id
            for m in self.notifications[notification_id]:
                try:
                    #print "  m: ", m
                    m(*args)
                except Exception, e:
                    import traceback
                    traceback.print_exc()
        notifications = {}
        # do local notifications
        if self.view_notifications.has_key(self.current_view):
            notifications = self.view_notifications[self.current_view]
            print 'local notification ', notification_id, self.current_view
                
        if notification_id in notifications:
            for m in notifications[notification_id]:
                try:
                    #print "  m: ", m
                    m(*args)
                except Exception, e:
                    import traceback
                    traceback.print_exc()

    def clipboard_changed(self):
        self.notify("clipboard_changed")

    def set_action_links(self, action_links, obj, view):
        link_list = []
        def get_method(_qaction, _check):
            def do_check_and_set(*args, **kwargs):
                _qaction.setEnabled(_check(*args, **kwargs))
            return do_check_and_set
        for action, (notification_id, check) in action_links.iteritems():
            window = obj.window()
            qaction = window.qactions[action]
            method = get_method(qaction, check)
            notification = (notification_id, method, True, view)
            self.register_notification(*notification)
            link_list.append(notification)
        self.action_links[id(obj)] = link_list
    
    def unset_action_links(self, obj):
        if id(obj) in self.action_links:
            for notification in self.action_links[id(obj)]:
                self.unregister_notification(*notification)
        
    def set_action_defaults(self, obj):
        window = obj.window()
        qactions = window.qactions
        for action, mlist in obj.action_defaults.iteritems():
            qaction = qactions[action]
            for (method, is_callback, value) in mlist:
                if is_callback:
                    getattr(qaction, method)(value())
                else:
                    getattr(qaction, method)(value)
            
    def get_name(self):
        return self.windowTitle()

    def set_name(self):
        widget = self.stack.currentWidget()
        if widget:
            self.set_title(widget.get_name())
        else:
            self.set_title('(empty)')

    # def action_triggered(self, action):
    #     if self.selected_mode is not None:
    #         self.selected_mode.un_method()
    #     if self.selected_mode != action:
    #         self.selected_mode = action
    #         if action is not None:
    #             action.method()
    #     elif self.selected_mode is not None:
    #         self.selected_mode = None
    #         action.setChecked(False)
    #     current_view = self.stack.currentWidget()
    #     current_view.tab_state[current_view.tabs.currentIndex()] = \
    #         self.selected_mode
    #     current_view.view_changed()

    # def create_pass_actions(self):
    #     actions = ['history_selected', 'history_unselected',
    #                'query_selected', 'query_unselected',
    #                'explore_selected', 'explore_unselected']
    #     def create_action(action_str):
    #         def new_action():
    #             getattr(self.stack.currentWidget(), action_str)()
    #         return new_action
    #     for action_str in actions:
    #         method = create_action(action_str)
    #         setattr(self, action_str, method)

    def sizeHint(self):
        return QtCore.QSize(1280, 768)

    def set_title(self, title):
        self.setWindowTitle(title)
                         
    def create_first_vistrail(self):
        print 'calling create_first_vistrail'
        if not self.dbDefault and untitled_locator().has_temporaries():
            if not FileLocator().prompt_autosave(self):
                untitled_locator().clean_temporaries()
        self._first_view = None
        self.new_vistrail(True)
        self._first_view = self.get_current_view()

    def change_view(self, view):
        print 'changing view', id(view), view
        if not self.windows.has_key(view):
            if self.stack.currentWidget() != view:
                self.stack.setCurrentWidget(view)
                view.reset_tab_state()
        self.view_changed(view)
            

    def detach_view(self, view):
        if not self.windows.has_key(view):
            index = self.stack.indexOf(view)
            self.stack.removeWidget(view)
            window = QVistrailViewWindow(view, parent=None)
            self.windows[view] = window
            self.connect(window, QtCore.SIGNAL("window_closed"),
                         self.window_closed)
            window.qactions['history'].setChecked(True)
            window.show()
            self.view_changed(view)
        else:
            self.view_changed(view)
            
    def window_closed(self, view):
        if self.windows.has_key(view):
            del self.windows[view]
            
    def view_changed(self, new_view):
        """ Updates the controller when the view changes and 
            updates buttons when """
        if self.current_view != new_view:
            self.current_view = new_view
            if new_view is not None:
                self.notify('controller_changed', new_view.get_controller())
        
        if new_view is not None:
            window = None
            if self.windows.has_key(new_view):
                window = self.windows[new_view]
            if window is None:
                if self.current_view.has_changes():
                    print "current view has changes"
                    self.qactions['saveFile'].setEnabled(True)
                    # un-remember first view when it is changed
                    if self._first_view:
                        self._first_view = None
                self.qactions['saveFileAs'].setEnabled(True)
                self.qactions['closeVistrail'].setEnabled(True)
            else:
                window.set_name()
                window.activateWindow()
                window.raise_()
                if self.current_view.has_changes():
                    window.qactions['saveFile'].setEnabled(True)
                window.qactions['saveFileAs'].setEnabled(True)
                window.qactions['closeVistrail'].setEnabled(True)
        else:
            self.qactions['saveFile'].setEnabled(False)
            self.qactions['saveFileAs'].setEnabled(False)
            self.qactions['closeVistrail'].setEnabled(False)

        from gui.collection.workspace import QWorkspaceWindow
        QWorkspaceWindow.instance().change_vt_window(new_view)
        self.update_merge_menu()
        self.update_window_menu()
        self.update_recent_vistrail_menu()
        self.set_name()

    def reset_toolbar_for_view(self, view):
        if view:
            window = view.window()
        else:
            window = self
        for action in window.view_action_group.actions():
            action.setChecked(False)
            
    def state_changed(self, view):
        """ state for the view changed so we need to update buttons"""
        self.view_changed(view)

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
        self.qactions['pipeline'].trigger()

    def close_first_vistrail_if_necessary(self):
        # Close first vistrail of no change was made
        if not self._first_view:
            return
        vt = self._first_view.controller.vistrail
        if vt.get_version_count() == 0:
            print "closing first vistrail"
            self.close_vistrail(self._first_view)
            self._first_view = None
        else:
            # We set it to none, since it's been changed, so
            # we don't want to ever close it again.
            self._first_view = None

    def ensureVistrail(self, locator):
        """ ensureVistrail(locator: VistrailLocator) -> QVistrailView        
        This will first find among the opened vistrails to see if
        vistrails from locator has been opened. If not, it will return None.
        
        """
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            if view.controller.vistrail.locator == locator:
                self.stack.setCurrentWidget(view)
                return view
        for (view, window) in self.windows.iteritems():
            if view.controller.vistrail.locator == locator:
                window.activateWindow()
                window.raise_()
                return view
        return None

    def open_vistrail(self, locator, version=None, is_abstraction=False):
        """open_vistrail(locator: Locator, version = None: int or str,
                         is_abstraction: bool)

        opens a new vistrail from the given locator, selecting the
        given version.

        """
        self.close_first_vistrail_if_necessary()

        view = self.ensureVistrail(locator)
        if view:
            if version is not None:
                if type(version) == type(""):
                    try:
                        version = view.vistrail.get_version_number(version)
                    except:
                        version = None
                if version is not None:
                    view.version_selected(version, True, double_click=True)
            self.view_changed(view)
            return view
        try:
            (vistrail, abstraction_files, thumbnail_files, mashups) = \
                                        load_vistrail(locator, is_abstraction)
            # we need to send all the elements above to create_view so they are 
            # sent to the controller.
            view = self.create_view(vistrail, locator, abstraction_files, 
                                    thumbnail_files, mashups)
            self.view_changed(view)
            self.reset_toolbar_for_view(view)
            self.qactions['history'].trigger()
            view.version_view.zoomToFit()
            if version:
                view.version_selected(version, True, double_click=True)
            view.controller.set_changed(False)
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
        # update collection
        try:
            if not locator:
                return
            thumb_cache = ThumbnailCache.getInstance()
            view.controller.vistrail.thumbnails = \
                view.controller.find_thumbnails(
                    tags_only=thumb_cache.conf.tagsOnly)
            view.controller.vistrail.abstractions = \
                view.controller.find_abstractions(view.controller.vistrail, 
                                                  True)

            collection = Collection.getInstance()
            url = locator.to_url()
            # create index if not exist
#            entity = collection.fromUrl(url)
#            if entity:
                # find parent vistrail
#                while entity.parent:
#                    entity = entity.parent
#            else:
            entity = collection.updateVistrail(url, view.controller.vistrail)
            # add to relevant workspace categories
            collection.add_to_workspace(entity)
            collection.commit()
        except Exception, e:
            import traceback
            debug.critical('Failed to index vistrail', traceback.print_exc())


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
            self.set_current_locator(locator)

    def open_vistrail_without_prompt(self, locator, version=None,
                                     execute_workflow=False, 
                                     is_abstraction=False, workflow_exec=None):
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
            if workflow_exec:
                self.qactions['provenance'].trigger()
                self.current_view.log_view.set_exec_by_id(workflow_exec) or \
                 self.current_view.log_view.set_exec_by_date(workflow_exec)

    def open_vistrail_default(self):
        """ open_vistrail_default() -> None
        Opens a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail_from_locator(DBLocator)
        else:
            self.open_vistrail_from_locator(FileLocator())

    def import_vistrail_default(self):
        """ import_vistrail_default() -> None
        Imports a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail_from_locator(FileLocator())
        else:
            self.open_vistrail_from_locator(DBLocator)

    def import_workflow(self, locator_class):
        locator = locator_class.load_from_gui(self, Pipeline.vtType)
        if locator:
            if not locator.is_valid():
                ok = locator.update_from_gui(self, Pipeline.vtType)
            else:
                ok = True
            if ok:
                self.open_workflow(locator)

    def import_workflow_default(self):
        self.import_workflow(XMLFileLocator)

    def open_workflow(self, locator, version=None):
        self.close_first_vistrail_if_necessary()

        vistrail = Vistrail()
        try:
            if locator is not None:
                workflow = locator.load(Pipeline)
                action_list = []
                for module in workflow.module_list:
                    action_list.append(('add', module))
                for connection in workflow.connection_list:
                    action_list.append(('add', connection))
                action = core.db.action.create_action(action_list)
                vistrail.add_action(action, 0L)
                vistrail.update_id_scope()
                vistrail.addTag("Imported workflow", action.id)
                # FIXME might need different locator?
        except ModuleRegistryException, e:
            msg = ('Cannot find module "%s" in package "%s". '
                    'Make sure package is ' 
                   'enabled in the Preferences dialog.' % \
                       (e._name, e._identifier))
            debug.critical(msg)
        except Exception, e:
            debug.critical('An error has occurred', str(e))
            raise

        view = self.create_view(vistrail, None)
        self.view_changed(view)
        view.controller.set_changed(True)
        view.version_selected(vistrail.get_latest_version(), \
                              True)
        self.qactions['pipeline'].trigger()
    
    def close_vistrail(self, current_view = None):
        if not current_view:
            current_view = self.get_current_view()
        if current_view.has_changes():
            window = current_view.window()
            text = current_view.controller.name
            if text=='':
                text = 'Untitled%s'%core.system.vistrails_default_file_type()
            text = ('Vistrail ' +
                    QtCore.Qt.escape(text) +
                    ' contains unsaved changes.\n Do you want to '
                    'save changes before closing it?')
            res = QtGui.QMessageBox.information(window,
                                                'Vistrails',
                                                text, 
                                                '&Save', 
                                                '&Discard',
                                                'Cancel',
                                                0,
                                                2)
        else:
            res = 1
        locator = current_view.controller.locator
        if res == 0:
            if locator is None:
                class_ = FileLocator()
            else:
                class_ = type(locator)
            locator = current_view.save_vistrail(class_)
            if not locator:
                return False
        elif res == 2:
            return False
        current_view.controller.close_vistrail(locator)
        current_view.controller.cleanup()
        self.remove_view(current_view)
        if current_view == self._first_view:
            self._first_view = None
        elif not self.stack.count():
            self.create_first_vistrail()
        return True

    def close_all_vistrails(self):
        while self.stack.count() > 0 and not \
              (self.stack.count() == 1 and self._first_view):
            if not self.close_vistrail():
                return False
        while len(self.windows) > 0:
            window = self.windows.values()[0]
            window.activateWindow()
            window.raise_()
            if not window.close():
                return False
        return True

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None
        Close the whole application when the builder is closed

        """
        if not self.quit():
            e.ignore()

    def quit(self):
        if self.close_all_vistrails():
            QtCore.QCoreApplication.quit()
            # In case the quit() failed (when Qt doesn't have the main
            # event loop), we have to return True still
            return True
        return False

    def link_registry(self):
        from gui.module_palette import QModulePalette
        QModulePalette.instance().link_registry()
       
    def get_current_view(self):
        if self.isActiveWindow():
            return self.stack.currentWidget()
        else:
            window = QtGui.QApplication.activeWindow()
            for view, w in self.windows.iteritems():
                if w == window:
                    return view
            else:
                return self.stack.currentWidget()
        
    def get_current_controller(self):
        return self.get_current_view().get_controller()

    def get_current_tab(self):
        return self.get_current_view().get_current_tab()

    def get_current_scene(self):
        return self.get_current_tab().scene()

    def pass_through(self, accessor, method_name):
        def method():
            obj = accessor()
            if obj is not None:
                if hasattr(obj, method_name):
                    getattr(obj, method_name)()
        return method

    def pass_through_bool(self, accessor, method_name):
        def method(checked):
            obj = accessor()
            if obj is not None:
                getattr(obj, method_name)(checked)
        return method

    def pass_through_locator(self, accessor, method_name, locator_klass=None,
                             reverse=False):
        def method():
            obj = accessor()
            obj_method = getattr(obj, method_name)
            if locator_klass is not None:
                obj_method(locator_klass)
            elif self.dbDefault ^ reverse:
                obj_method(DBLocator())
            else:
                obj_method(FileLocator())
        return method

    def create_menus(self):
        self.createActions()
        # self.fileMenu = _menu_bar.addMenu('&File')
        # self.newVistrailAction = QtGui.QAction('&New', self)
        # self.newVistrailAction.setShortcut('Ctrl+N')
        # self.newVistrailAction.setStatusTip('Create a new vistrail')
        # self.openFileAction = QtGui.QAction('&Open', self)
        # self.openFileAction.setShortcut('Ctrl+O')
        # self.openFileAction.setStatusTip('Open an existing vistrail from '
        #                                  'a file')
        
        # self.fileMenu.addAction(self.newVistrailAction)
        # self.fileMenu.addAction(self.openFileAction)

        # trigger_actions = [(self.newVistrailAction, self.new_vistrail),
        #                    (self.openFileAction, self.open_vistrail_default)]
        # for (emitter, receiver) in trigger_actions:
        #     self.connect(emitter, QtCore.SIGNAL('triggered()'), receiver)


    def create_palette_actions(self):
        palette_actions = []
        for palette in self.palettes:
            # palette_actions.append((palette.get_title(), palette.get_action()))
            palette_actions.append((palette.get_action_tuple(), palette))
        palette_actions.sort()
        return zip(*palette_actions)

    def createActions(self):
        """ createActions() -> None
        Construct all menu/toolbar actions for builder window

        """
        # self.newVistrailAction = QtGui.QAction(CurrentTheme.NEW_VISTRAIL_ICON,
        #                                        '&New', self)
        # self.newVistrailAction.setShortcut('Ctrl+N')
        # self.newVistrailAction.setStatusTip('Create a new vistrail')

        # self.openFileAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_ICON,
        #                                     '&Open', self)
        # self.openFileAction.setShortcut('Ctrl+O')
        # self.openFileAction.setStatusTip('Open an existing vistrail from '
        #                                  'a file')
        
        # self.create_recent_vistrail_actions()
            
        # self.importFileAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_DB_ICON,
        #                                       'From DB...', self)
        # self.importFileAction.setStatusTip('Import an existing vistrail from '
        #                                    'a database')

        # self.saveFileAction = QtGui.QAction(CurrentTheme.SAVE_VISTRAIL_ICON,
        #                                         '&Save', self)
        # self.saveFileAction.setShortcut('Ctrl+S')
        # self.saveFileAction.setStatusTip('Save the current vistrail '
        #                                  'to a file')
        # self.saveFileAction.setEnabled(False)

        # self.saveFileAsAction = QtGui.QAction('Save as...', self)
        # self.saveFileAsAction.setShortcut('Ctrl+Shift+S')
        # self.saveFileAsAction.setStatusTip('Save the current vistrail '
        #                                    'to a different file location')
        # self.saveFileAsAction.setEnabled(False)

        # self.exportFileAction = QtGui.QAction('To DB...', self)
        # self.exportFileAction.setStatusTip('Export the current vistrail to '
        #                                    'a database')
        # self.exportFileAction.setEnabled(False)

        # self.closeVistrailAction = QtGui.QAction('Close', self)
        # self.closeVistrailAction.setShortcut('Ctrl+W')
        # self.closeVistrailAction.setStatusTip('Close the current vistrail')
        # self.closeVistrailAction.setEnabled(False)

        # self.exportStableAction = QtGui.QAction('To Stable Version...', 
        #                                         self)
        # self.exportStableAction.setStatusTip('Save vistrail as XML according '
        #                                      'to the older (stable) schema')
        # self.exportStableAction.setEnabled(True)

        # self.saveOpmAction = QtGui.QAction('OPM XML...', self)
        # self.saveOpmAction.setStatusTip('Saves provenance according to the'
        #                                 'Open Provenance Model in XML')
        # self.saveOpmAction.setEnabled(True)

        # self.saveLogAction = QtGui.QAction('Log To XML...', self)
        # self.saveLogAction.setStatusTip('Save the execution log to '
        #                                 'a file')
        # self.saveLogAction.setEnabled(True)

        # self.exportLogAction = QtGui.QAction('Log To DB...', self)
        # self.exportLogAction.setStatusTip('Save the execution log to '
        #                                   'a database')
        # self.exportLogAction.setEnabled(True)

        # self.importWorkflowAction = QtGui.QAction('Workflow...', self)
        # self.importWorkflowAction.setStatusTip('Import a workflow from an '
        #                                        'xml file')
        # self.importWorkflowAction.setEnabled(True)

        # self.saveWorkflowAction = QtGui.QAction('Workflow To XML...', self)
        # self.saveWorkflowAction.setStatusTip('Save the current workflow to '
        #                                      'a file')
        # self.saveWorkflowAction.setEnabled(True)

        # self.exportWorkflowAction = QtGui.QAction('Workflow To DB...', self)
        # self.exportWorkflowAction.setStatusTip('Save the current workflow to '
        #                                        'a database')
        # self.exportWorkflowAction.setEnabled(True)

        # self.saveRegistryAction = QtGui.QAction('Registry To XML...', self)
        # self.saveRegistryAction.setStatusTip('Save the current registry to '
        #                                      'a file')
        # self.saveRegistryAction.setEnabled(True)

        # self.exportRegistryAction = QtGui.QAction('Registry To DB...', self)
        # self.exportRegistryAction.setStatusTip('Save the current registry to '
        #                                        'a database')
        # self.exportRegistryAction.setEnabled(True)

        # self.savePDFAction = QtGui.QAction('PDF...', self)
        # self.savePDFAction.setStatusTip('Save the current view'
        #                                              'to a PDF file')
        # self.savePDFAction.setEnabled(True)

        # self.quitVistrailsAction = QtGui.QAction('Quit', self)
        # self.quitVistrailsAction.setShortcut('Ctrl+Q')
        # self.quitVistrailsAction.setStatusTip('Exit Vistrails')

        # self.undoAction = QtGui.QAction(CurrentTheme.UNDO_ICON,
        #                                 'Undo', self)
        # self.undoAction.setEnabled(False)
        # self.undoAction.setStatusTip('Undo the previous action')
        # self.undoAction.setShortcut('Ctrl+Z')

        # self.redoAction = QtGui.QAction(CurrentTheme.REDO_ICON,
        #                                 'Redo', self)
        # self.redoAction.setEnabled(False)
        # self.redoAction.setStatusTip('Redo an undone action')
        # self.redoAction.setShortcut('Ctrl+Y')

        # self.copyAction = QtGui.QAction('Copy\tCtrl+C', self)
        # self.copyAction.setEnabled(False)
        # self.copyAction.setStatusTip('Copy selected modules in '
        #                              'the current pipeline view')

        # self.pasteAction = QtGui.QAction('Paste\tCtrl+V', self)
        # self.pasteAction.setEnabled(False)
        # self.pasteAction.setStatusTip('Paste copied modules in the clipboard '
        #                               'into the current pipeline view')

                   
                     
                    
                    
        # self.groupAction = QtGui.QAction('Group', self)
        # self.groupAction.setShortcut('Ctrl+G')
        # self.groupAction.setEnabled(False)
        # self.groupAction.setStatusTip('Group the '
        #                               'selected modules in '
        #                               'the current pipeline view')
        # self.ungroupAction = QtGui.QAction('Ungroup', self)
        # self.ungroupAction.setShortcut('Ctrl+Shift+G')
        # self.ungroupAction.setEnabled(False)
        # self.ungroupAction.setStatusTip('Ungroup the '
        #                               'selected groups in '
        #                               'the current pipeline view')
        # self.showGroupAction = QtGui.QAction('Show Group Pipeline', self)
        # self.showGroupAction.setEnabled(True)
        # self.showGroupAction.setStatusTip('Show the underlying pipelines '
        #                                   'for the selected groups in '
        #                                   'the current pipeline view')

        # self.makeAbstractionAction = QtGui.QAction('Make SubWorkflow', self)
        # self.makeAbstractionAction.setStatusTip('Create a subworkflow '
        #                                         'from the selected modules')
        # self.convertToAbstractionAction = \
        #     QtGui.QAction('Convert to SubWorkflow', self)
        # self.convertToAbstractionAction.setStatusTip('Convert selected group '
        #                                              'to a subworkflow')
        # self.editAbstractionAction = QtGui.QAction("Edit SubWorkflow", self)
        # self.editAbstractionAction.setStatusTip("Edit a subworkflow")
        # self.importAbstractionAction = QtGui.QAction('Import SubWorkflow', self)
        # self.importAbstractionAction.setStatusTip('Import subworkflow from '
        #                                           'a vistrail to local '
        #                                           'subworkflows')
        # self.exportAbstractionAction = QtGui.QAction('Export SubWorkflows', self)
        # self.exportAbstractionAction.setStatusTip('Export subworkflows from '
        #                                           'local subworkflows for '
        #                                           'use in a package')
        # self.controlFlowAssistAction = QtGui.QAction('Control Flow Assistant', self)
        # self.controlFlowAssistAction.setStatusTip('Launch the Control Flow '
        #                                           'Assistant with the selected modules')
        # self.selectAllAction = QtGui.QAction('Select All\tCtrl+A', self)
        # self.selectAllAction.setEnabled(False)
        # self.selectAllAction.setStatusTip('Select all modules in '
        #                                   'the current pipeline view')

        # self.repositoryOptions = QtGui.QAction('Web Repository Options', self)
        # self.repositoryOptions.setEnabled(True)
        # self.repositoryOptions.setStatusTip('Add this VisTrail to VisTrails Repository')

        # self.editPreferencesAction = QtGui.QAction('Preferences...', self)
        # self.editPreferencesAction.setEnabled(True)
        # self.editPreferencesAction.setStatusTip('Edit system preferences')

        # self.workspaceAction = QtGui.QAction('Workspaces', self)
        # self.workspaceAction.setCheckable(True)
        # self.workspaceAction.setChecked(False)

        # self.provenanceBrowserAction = QtGui.QAction('Provenance Browser', self)
        # self.provenanceBrowserAction.setCheckable(True)
        # self.provenanceBrowserAction.setChecked(False)

        # self.shellAction = QtGui.QAction(CurrentTheme.CONSOLE_MODE_ICON,
        #                                  'VisTrails Console', self)
        # self.shellAction.setCheckable(True)
        # self.shellAction.setShortcut('Ctrl+H')

        # self.debugAction = QtGui.QAction('VisTrails Debugger', self)
        # self.debugAction.setCheckable(True)
        # self.debugAction.setChecked(False)

        # self.messagesAction = QtGui.QAction('VisTrails Messages', self)
        # self.messagesAction.setCheckable(True)
        # self.messagesAction.setChecked(False)

        # self.pipViewAction = QtGui.QAction('Picture-in-Picture', self)
        # self.pipViewAction.setCheckable(True)
        # self.pipViewAction.setChecked(True)

        # self.methodsViewAction = QtGui.QAction('Methods Panel', self)
        # self.methodsViewAction.setCheckable(True)
        # self.methodsViewAction.setChecked(True)

        # self.setMethodsViewAction = QtGui.QAction('Set Methods Panel', self)
        # self.setMethodsViewAction.setCheckable(True)
        # self.setMethodsViewAction.setChecked(True)

        # self.propertiesViewAction = QtGui.QAction('Properties Panel', self)
        # self.propertiesViewAction.setCheckable(True)
        # self.propertiesViewAction.setChecked(True)

        # self.propertiesOverlayAction = QtGui.QAction('Properties Overlay', self)
        # self.propertiesOverlayAction.setCheckable(True)
        # self.propertiesOverlayAction.setChecked(False)

        # self.expandBranchAction = QtGui.QAction('Expand Branch', self)
        # self.expandBranchAction.setEnabled(True)
        # self.expandBranchAction.setStatusTip('Expand all versions in the tree below the current version')

        # self.collapseBranchAction = QtGui.QAction('Collapse Branch', self)
        # self.collapseBranchAction.setEnabled(True)
        # self.collapseBranchAction.setStatusTip('Collapse all expanded versions in the tree below the current version')

        # self.collapseAllAction = QtGui.QAction('Collapse All', self)
        # self.collapseAllAction.setEnabled(True)
        # self.collapseAllAction.setStatusTip('Collapse all expanded branches of the tree')

        # self.hideBranchAction = QtGui.QAction('Hide Branch', self)
        # self.hideBranchAction.setEnabled(True)
        # self.hideBranchAction.setStatusTip('Hide all versions in the tree including and below the current version')

        # self.showAllAction = QtGui.QAction('Show All', self)
        # self.showAllAction.setEnabled(True)
        # self.showAllAction.setStatusTip('Show all hidden versions')
            
        # self.moduleConfigViewAction = QtGui.QAction('Module Configuration Panel', self)
        # self.moduleConfigViewAction.setCheckable(True)
        # self.moduleConfigViewAction.setChecked(True)
        
        # self.helpAction = QtGui.QAction(self.tr('About VisTrails...'), self)

        # self.checkUpdateAction = QtGui.QAction(self.tr('Check for Updates'), self)

        # a = QtGui.QAction(self.tr('Execute Current Workflow\tCtrl+Enter'),
        #                   self)
        # self.executeCurrentWorkflowAction = a
        # self.executeCurrentWorkflowAction.setEnabled(False)

        # self.executeDiffAction = QtGui.QAction('Execute Version Difference', self)
        # self.executeDiffAction.setEnabled(False)
        # self.flushCacheAction = QtGui.QAction(self.tr('Erase Cache Contents'),
        #                                       self)

        # self.executeQueryAction = QtGui.QAction('Execute Visual Query', self)
        # self.executeQueryAction.setEnabled(False)

        # self.executeExplorationAction = QtGui.QAction(
        #     'Execute Parameter Exploration', self)
        # self.executeExplorationAction.setEnabled(False)

        # self.executeShortcuts = [
        #     QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.ControlModifier +
        #                                        QtCore.Qt.Key_Return), self),
        #     QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.ControlModifier +
        #                                        QtCore.Qt.Key_Enter), self)
        #     ]
        
        # self.vistrailActionGroup = QtGui.QActionGroup(self)
        # self.mergeActionGroup = QtGui.QActionGroup(self)

        # format of each item in the list is:
        # item: reference, title, options
        # where options is either a list of subitems or
        # a dictionary of options to be set for an action
        # Also, "---" denotes a separator

        global _global_menubar

        palette_actions, palettes = self.create_palette_actions()
        palette_actions = list(palette_actions)
        # palettes = []
        # palette_actions = []

        actions = [("file", "&File",
                    [('newVistrail', "&New",
                      {'icon': CurrentTheme.NEW_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.New,
                       'statusTip': 'Create a new vistrail',
                       'callback': self.new_vistrail}),
                     ('openFile', "&Open",
                      {'icon': CurrentTheme.OPEN_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.Open,
                       'statusTip': 'Open an existing vistrail from a file',
                       'callback': self.open_vistrail_default}),
                     ("openRecent", "Open Recent", 
                      []),
                     ('saveFile', "&Save",
                      {'icon': CurrentTheme.SAVE_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.Save,
                       'statusTip': "Save the current vistrail to a file",
                       'enabled': False,
                       'callback': \
                           self.pass_through_locator(self.get_current_view,
                                                     'save_vistrail')}),
                     ('saveFileAs', "Save as...",
                      {'shortcut': QtGui.QKeySequence.SaveAs,
                       'statusTip': "Save the current vistrail to a " \
                           "different file location",
                       'enabled': False,
                       'callback': \
                           self.pass_through_locator(self.get_current_view,
                                                     'save_vistrail_as')}),
                     ('closeVistrail', "Close",
                      {'shortcut': QtGui.QKeySequence.Close,
                       'statusTip': "Close the current vistrail",
                       'enabled': True,
                       'callback': self.close_vistrail}),
                     "---",
                     ("import", "Import",
                      [('importFile', "From DB...",
                        {'icon': CurrentTheme.OPEN_VISTRAIL_DB_ICON,
                         'statusTip': "Import an existing vistrail " \
                             "from a database",
                         'callback': \
                             self.import_vistrail_default}),
                       "---",
                       ('importWorkflow', "Workflow...",
                        {'statusTip': "Import a workflow from an XML file",
                         'enabled': True,
                         'callback': self.import_workflow_default})]),
                     ("export", "Export",
                      [('exportFile', "To DB...",
                        {'statusTip': "Export the current vistrail to a " \
                             "database",
                         'enabled': False,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'export_vistrail', 
                                                       reverse=True)}),
                       ('exportStable', "To Stable Version...",
                        {'statusTip': "Save vistrail as XML according to " \
                             "the older (stable) schema",
                         'enabled': True,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'export_stable')}),
                       "---",
                       ('savePDF', "PDF...",
                        {'statusTip': "Save the current view to a PDF file",
                         'enabled': True,
                         'callback': self.pass_through(self.get_current_tab,
                                                       'save_pdf')}),
                       "---",
                       ('saveWorkflow', "Workflow To XML...",
                        {'statusTip': "Save the current workflow to a file",
                         'enabled': True,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       FileLocator())}),
                       ('exportWorkflow', "Workflow to DB...",
                        {'statusTip': "Save the current workflow to a database",
                         'enabled': True,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       DBLocator)}),
                       "---",
                       ('saveOpm', "OPM XML...",
                        {'statusTip': "Save proveannce according to the " \
                             "Open Provenance Model in XML",
                         'enabled': True,
                         'callback': self.pass_through(self.get_current_view,
                                                       'save_opm')}),
                       ('saveLog', "Log to XML...",
                        {'statusTip': "Save the execution log to a file",
                         'enabled': False,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'save_log',
                                                       FileLocator())}),
                       ('exportLog', "Log to DB...",
                        {'statusTip': "Save the execution log to a database",
                         'enabled': True,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'save_log',
                                                       DBLocator)}),
                       "---",
                       ('saveRegistry', "Registry to XML...",
                        {'statusTip': "Save the current registry to a file",
                         'enabled': True,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'save_registry',
                                                       FileLocator())}),
                       ('exportRegistry', "Registry to DB...",
                        {'statusTip': "Save the current registry to a database",
                         'enabled': True,
                         'callback': \
                             self.pass_through_locator(self.get_current_view,
                                                       'save_registry',
                                                       DBLocator)})]),
                     "---",
                     ('quitVistrails', "Quit",
                      {'shortcut': QtGui.QKeySequence.Quit,
                       'statusTip': "Exit VisTrails",
                       'callback': self.quit})]),
                   ("edit", "&Edit",
                    [("undo", "Undo",
                      {'statusTip': "Undo the previous action",
                       'shortcut': QtGui.QKeySequence.Undo,
                       'enabled': False}),
                     ("redo", "Redo",
                      {'statusTip': "Redo an undone action",
                       'shortcut': QtGui.QKeySequence.Redo,
                       'enabled': False}),
                     "---",
                     ("copy", "Copy",
                      {'statusTip': "Copy the selected modules in the " \
                           "current pipeline view",
                       'shortcut': QtGui.QKeySequence.Copy,
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'copySelection')}),
                     ("paste", "Paste",
                      {'statusTip': "Paste modules from the clipboard into " \
                           "the current pipeline view",
                       'shortcut': QtGui.QKeySequence.Paste,
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_tab,
                                                     'pasteFromClipboard')}),
                     ("selectAll", "Select All",
                      {'statusTip': "Select all modules in the current " \
                           "pipeline view",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.SelectAll,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'selectAll')}),
                     "---",
                     ("controlFlowAssist", "Control Flow Assistant",
                      {'statusTip': "Create a loop over the selected modules"}),
                     ("merge", "Merge with...", 
                      []),
                     "---",
                     ("editPreferences", "Preferences...",
                      {'statusTip': "Edit system preferences",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.Preferences,
                       'callback': self.showPreferences}),
                     ]),
                   ("run", "&Workflow",
                    [("execute", "Execute",
                      {'icon': CurrentTheme.EXECUTE_PIPELINE_ICON,
                       'shortcut': 'Ctrl+Return',
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_view,
                                                     'execute')}),
                     ("flushCache", "Erase Cache Contents", 
                      {'enabled': True,
                       'callback': self.flush_cache}),
                     "---",
                     ("group", "Group",
                      {'statusTip': "Group the selected modules in the " \
                           "current pipeline view",
                       'shortcut': 'Ctrl+G',
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'group')}),
                     ("ungroup", "Ungroup",
                      {'statusTip': "Ungroup the selected groups in the " \
                           "current pipeline view",
                       'shortcut': 'Ctrl+Shift+G',
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'ungroup')}),
                     ("showGroup", "Show Pipeline",
                      {'statusTip': "Show the underlying pipeline for the " \
                           "selected group in the current pipeline view",
                       'enabled': False,
                       'callback': self.show_group}),
                     "---",
                     ("makeAbstraction", "Create Subworkflow",
                      {'statusTip': "Create a subworkflow from the selected " \
                           "modules",
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'makeAbstraction')}),
                     ("convertToAbstraction", "Convert to Subworkflow",
                      {'statusTip': "Convert selected group to a subworkflow",
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'convertToAbstraction')}),
                     ("editAbstraction", "Edit Subworkflow",
                      {'statusTip': "Edit a subworkflow",
                       'enabled': False,
                       'callback': self.edit_abstraction}),
                     ("importAbstraction", "Import Subworkflow",
                      {'statusTip': "Import subworkflow from a vistrail to " \
                           "local subworkflows",
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'importAbstraction')}),
                     ("exportAbstraction", "Export Subworkflow",
                      {'statusTip': "Export subworkflow from local " \
                           "subworkflows for use in a package",
                       'enabled': False,
                       'callback': self.pass_through(self.get_current_scene,
                                                     'exportAbstraction')}),
                     "---",
                     ("configureModule", "Configure Module...",
                      {'shortcut': "Ctrl+E",
                       'enabled': False,
                       'callback': self.configure_module}),
                     ("documentModule", "Module Documentation...",
                      {'enabled': False,
                       'callback': self.show_documentation})]),
                     # ("executeDiff", "Show Version Difference",
                     #  {'enabled': False}),
                     # ("executeQuery", "Perform Query",
                     #  {'enabled': False}),
                     # ("executeExploration", "Perform Parameter Exploration",
                     #  {'enabled': False})]),
                   ("vistrail", "Vis&trail",
                    [("tag", "Tag...",
                      {'statusTip': "Tag the current pipeline",
                       'shortcut': "Ctrl+Shift+T",
                       'enabled': True,
                       'callback': self.add_tag}),
                     "---",
                     ("expandBranch", "Expand Branch",
                      {'statusTip': "Expand all versions in the tree below " \
                           "the current version",
                       'enabled': True,
                       'callback': \
                           self.pass_through(self.get_current_controller,
                                             'expand_all_versions_below')}),
                     ("collapseBranch", "Collapse Branch",
                      {'statusTip': "Collapse all expanded versions of the " \
                           "tree",
                       'enabled': True,
                       'callback': \
                           self.pass_through(self.get_current_controller,
                                             'collapse_all_versions_below')}),
                     ("collapseAll", "Collapse All",
                      {'statusTip': "Collapse all expanded branches of the " \
                           "tree",
                       'enabled': True,
                       'callback': \
                           self.pass_through(self.get_current_controller,
                                             'collapse_all_versions')}),
                     ("hideBranch", "Hide Branch",
                      {'statusTip': "Hide all versions in the tre including " \
                           "and below the current version",
                       'enabled': True,
                       'callback': \
                           self.pass_through(self.get_current_controller,
                                             'hide_versions_below')}),
                     ("showAll", "Show All",
                      {'enabled': True,
                       'statusTip': "Show all hidden versions",
                       'callback': \
                           self.pass_through(self.get_current_controller,
                                             'show_all_versions')})]),
                   ("view", "&Views",
                    [("newView", "New Pipeline View",
                      {'shortcut': QtGui.QKeySequence.AddTab,
                       'enabled': True,
                       'statusTip': "Create a new pipeline view",
                       'callback': self.pass_through(self.get_current_view,
                                                     'add_pipeline_view')}),
                     ("newDiff", "New Visual Difference",
                      {'enabled': True,
                       'statusTip': "Create a new visual difference for two" \
                           "pipelines",
                       'callback': self.new_diff}),
                     "---",
                     ("zoomToFit", "Zoom To Fit",
                      {'enabled': True,
                       'shortcut': "Ctrl+R",
                       'statusTip': "Fit current view to window",
                       'callback': self.pass_through(self.get_current_tab,
                                                     'zoomToFit')}),
                     ("zoomIn", "Zoom In",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomIn,
                       'callback': self.pass_through(self.get_current_tab,
                                                     'zoomIn')}),
                     ("zoomOut", "Zoom Out",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomOut,
                       'callback': self.pass_through(self.get_current_tab,
                                                     'zoomOut')}),
                     "---",
                     ("pipeline", "Pipeline",
                      {'icon': CurrentTheme.PIPELINE_ICON,
                       'checkable': True,
                       'checked': True,
                       'callback': \
                           self.pass_through_bool(self.get_current_view,
                                                  'pipeline_change')}),
                     ("history", "History",
                      {'icon': CurrentTheme.HISTORY_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           self.pass_through_bool(self.get_current_view,
                                                  'history_change')}),
                     ("search", "Search",
                      {'icon': CurrentTheme.QUERY_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           self.pass_through_bool(self.get_current_view,
                                                  'search_change')}),
                     ("explore", "Explore",
                      {'icon': CurrentTheme.EXPLORE_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           self.pass_through_bool(self.get_current_view,
                                                  'explore_change')}),
                     ("provenance", "Provenance",
                      {'icon': CurrentTheme.PROVENANCE_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           self.pass_through_bool(self.get_current_view,
                                                  'provenance_change')}),
                    ("mashup", "Mashup",
                      {'icon': CurrentTheme.MASHUP_ICON,
                       'checkable': True,
                       'checked': False,
                       'enabled': False,
                       'callback': \
                           self.pass_through_bool(self.get_current_view,
                                                  'mashup_change')}),
                     "---"] + palette_actions + ["---", 
                       ("dockPalettes", "Dock Palettes", 
                        {'enabled': True,
                         'statusTip': "Dock palettes on active window",
                         'callback': self.dock_palettes})]),
                    # [("workspace", "Workspaces",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("provenanceBrowser", "Provenance Browser",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("shell", "Console",
                    #   {'icon': CurrentTheme.CONSOLE_MODE_ICON,
                    #    'checkable': True,
                    #    'checked': False}),
                    #  ("debug", "Debugger",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("messages", "Messages",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("pipView", "Picture-in-Picture",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("properties", "Properties",
                    #   {'checkable': True,
                    #    'checked': True}),
                    #  ("propertiesOverlay", "Properties Overlay",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("moduleConfigView", "Module Configuration",
                    #   {'checkable': True,
                    #    'checked': False}),
                    #  ("moduleDocumentation", "Module Documentation",
                    #   {'checkable': True,
                    #    'checked': False})]),
                   ("publish", "Publish",
                    [("publishPaper", "To Paper...", 
                      {'enabled': True,
                       'statusTip': \
                           "Embed workflow and results into a paper",
                        'callback': self.pass_through(self.get_current_view,
                                                      'publish_to_paper')}),
                     ("publishWeb", "To Wiki...",
                      {'enabled': True,
                       'statusTip': "Embed workflow in wiki",
                       'callback' : self.pass_through(self.get_current_view,
                                                      'publish_to_web')}),
                     ("publishCrowdLabs", "To crowdLabs...",
                      {'enabled': True,
                       'statusTip': "Publish workflows on crowdlabs.org",
                       'callback': self.publish_to_crowdlabs})]),
                    ("packages", "Packages", 
                      []),
                    ("window", "Window", 
                      []),
                   ("help", "Help",
                    [("help", "About VisTrails...", 
                      {'callback': self.showAboutMessage}),
                     ("checkUpdate", "Check for Updates", 
                      {'callback': self.showUpdatesMessage})])]


        qactions = {}
        qmenus = {}
        def process_list(action_list, parent):
            for data in action_list:
                if data == "---":
                    if parent is not None:
                        parent.addSeparator()
                    continue
                name, title, options = data
                if type(options) == list:
                    # menu
                    if parent is not None:
                        qmenu = parent.addMenu(title)
                    qmenus[name] = qmenu
                    process_list(options, qmenu)
                else:
                    qaction = QtGui.QAction(title, self)
                    callback = None
                    if 'callback' in options:
                        callback = options['callback']
                        del options['callback']
                    for option, value in options.iteritems():
                        method = getattr(qaction, 'set%s' % \
                                             option[0].capitalize() + \
                                             option[1:])
                        method(value)
                    qactions[name] = qaction
                    if parent is not None:
                        parent.addAction(qaction)
                    if callback is not None:
                        if 'checkable' in options and \
                                options['checkable'] is True:
                            self.connect(qaction, 
                                         QtCore.SIGNAL("toggled(bool)"),
                                         callback)
                        else:
                            self.connect(qaction, QtCore.SIGNAL("triggered()"),
                                         callback)
                        

            self.qactions = qactions
            self.qmenus = qmenus

        if core.system.systemType in ['Darwin']:
            menu_bar = QtGui.QMenuBar()
            _global_menubar = menu_bar
        else:
            menu_bar = self.menuBar()
        print 'menu_bar:', menu_bar
        process_list(actions, menu_bar)
        print 'done processing list'

        for action_tuple, palette in izip(palette_actions, palettes):
            palette.set_action(self.qactions[action_tuple[0]])

        self.connect_package_manager_signals()
        # view_menu = self.qmenus["view"]
        # for action_name, action in self.create_palette_actions():
        #     self.qactions[action_name] = action
        #     view_menu.addAction(action)

    def connect_package_manager_signals(self):
        """ connect_package_manager_signals()->None
        Connect specific signals related to the package manager """
        pm = get_package_manager()
        self.connect(pm,
                     pm.add_package_menu_signal,
                     self.add_package_menu_items)
        self.connect(pm,
                     pm.remove_package_menu_signal,
                     self.remove_package_menu_items)
        self.connect(pm,
                     pm.package_error_message_signal,
                     self.show_package_error_message)

    def add_package_menu_items(self, pkg_id, pkg_name, items):
        """add_package_menu_items(pkg_id: str,pkg_name: str,items: list)->None
        Add a pacckage menu entry with submenus defined by 'items' to
        Packages menu.

        """
        if len(self._package_menu_items) == 0:
            self.qmenus['packages'].menuAction().setEnabled(True)

        # we don't support a menu hierarchy yet, only a flat list
        # this can be added later
        def update_menu(d, packagesMenu):
            if not d.has_key(pkg_id):
                pkg_menu = packagesMenu.addMenu(str(pkg_name))
                d[pkg_id] = {}
                d[pkg_id]['menu'] = pkg_menu
                d[pkg_id]['items'] = []
            else:
                pkg_menu = d[pkg_id]['menu']
                pkg_menu.clear()
            d[pkg_id]['items'] = [(pkg_name,items)]
            
            for item in items:
                (name, callback) = item
                action = QtGui.QAction(name,self,
                                       triggered=callback)
                pkg_menu.addAction(action)
                
        update_menu(self._package_menu_items,self.qmenus['packages'])    
        
        for w in self.windows.values():
            update_menu(w._package_menu_items, w.qmenus['packages'])

    def remove_package_menu_items(self, pkg_id):
        """remove_package_menu_items(pkg_id: str)-> None
        removes all menu entries from the Packages Menu created by pkg_id """
        def update_menu(items, menu):
            if items.has_key(pkg_id):
                pkg_menu = items[pkg_id]['menu']
                del items[pkg_id]
                pkg_menu.clear()
                pkg_menu.deleteLater()
            if len(items) == 0:
                menu.menuAction().setEnabled(False)
            
        update_menu(self._package_menu_items, self.qmenus['packages'])
        for w in self.windows.values():
            update_menu(w._package_menu_items, w.qmenus['packages'])
            
    def show_package_error_message(self, pkg_id, pkg_name, msg):
        """show_package_error_message(pkg_id: str, pkg_name: str, msg:str)->None
        shows a message box with the message msg.
        Because the way initialization is being set up, the messages will be
        shown after the builder window is shown.

        """
        msgbox = build_custom_window("Package %s (%s) says:"%(pkg_name,pkg_id),
                                    msg,
                                    modal=True,
                                    parent=self)
        #we cannot call self.msgbox.exec_() or the initialization will hang
        # creating a modal window and calling show() does not cause it to hang
        # and forces the messages to be shown on top of the builder window after
        # initialization
        msgbox.show()

    def showAboutMessage(self):
        """showAboutMessage() -> None
        Displays Application about message

        """
        class About(QtGui.QLabel):
            def mousePressEvent(self, e):
                self.emit(QtCore.SIGNAL("clicked()"))

        dlg = QtGui.QDialog(self, QtCore.Qt.FramelessWindowHint)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        bgimage = About(dlg)
        bgimage.setPixmap(CurrentTheme.DISCLAIMER_IMAGE)
        layout.addWidget(bgimage)
        dlg.setLayout(layout)
        text = "<font color=\"white\"><b>%s</b></font>" % \
            core.system.short_about_string()
        version = About(text, dlg)
        version.setGeometry(11,20,450,30)
        self.connect(bgimage,
                     QtCore.SIGNAL('clicked()'),
                     dlg,
                     QtCore.SLOT('accept()'))
        self.connect(version,
                     QtCore.SIGNAL('clicked()'),
                     dlg,
                     QtCore.SLOT('accept()'))
        dlg.setSizeGripEnabled(False)
        dlg.exec_()

    def showUpdatesMessage(self):
        """ showUpdatesMessage() -> None
        Displays Check for Updates message.
        This queries vistrails.org for new VisTrails Versions

        """

        new_version_exists, version = core.system.new_vistrails_release_exists()
        if new_version_exists:
            msg = 'Version %s of VisTrails is available at ' \
                '<a href="%s">%s</a>' % \
                (version, "http://www.vistrails.org/index.php/Downloads", \
                     "http://www.vistrails.org/index.php/Downloads")
        else:
            msg = "Your VisTrails installation is up-to-date."
        QtGui.QMessageBox.information(self, "Check for VisTrails Updates",
                                      msg)
                                      
    def showRepositoryOptions(self):
        """ Displays Repository Options for authentication and pushing VisTrail to Repository """
        dialog = QRepositoryDialog(self)
        dialog.exec_()

    def setDBDefault(self, dbState):
        """ setDBDefault(on: bool) -> None
        The preferences are set to turn on/off read/write from db instead of
        file. Update the state accordingly.

        """
        self.dbDefault = dbState
        if self.dbDefault:
            openFileAction = self.qactions['openFile']
            openFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_DB_ICON)
            openFileAction.setStatusTip('Open an existing vistrail from '
                                        'a database')
            importFileAction = self.qactions['importFile']
            importFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_ICON)
            importFileAction.setText('From XML File...')
            importFileAction.setStatusTip('Import an existing vistrail '
                                          'from a file')
            saveFileAction = self.qactions['saveFile']
            saveFileAction.setStatusTip('Save the current vistrail '
                                        'to a database')
            saveFileAsAction = self.qactions['saveFileAs']
            saveFileAsAction.setStatusTip('Save the current vistrail to a '
                                          'different database location')
            exportFileAction = self.qactions['exportFile']
            exportFileAction.setText('To XML File...')
            exportFileAction.setStatusTip('Save the current vistrail to '
                                          'a file')
        else:
            openFileAction = self.qactions['openFile']
            openFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_ICON)
            openFileAction.setStatusTip('Open an existing vistrail from '
                                             'a file')
            importFileAction = self.qactions['importFile']
            importFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_DB_ICON)
            importFileAction.setText('From DB...')
            importFileAction.setStatusTip('Import an existing vistrail '
                                          'from a database')
            saveFileAction = self.qactions['saveFile']
            saveFileAction.setStatusTip('Save the current vistrail '
                                             'to a file')
            saveFileAsAction = self.qactions['saveFileAs']
            saveFileAsAction.setStatusTip('Save the current vistrail to a '
                                          'different file location')
            exportFileAction = self.qactions['exportFile']
            exportFileAction.setText('To DB...')
            exportFileAction.setStatusTip('Save the current vistrail to '
                                          'a database')

    def flush_cache(self):
        CachedInterpreter.flush()
            
    def showPreferences(self):
        """showPreferences() -> None
        Display Preferences dialog

        """
        dialog = QPreferencesDialog(self)
        retval = dialog.exec_()
        if retval != 0:
            self.flush_cache()
            currentView = self.get_current_view()
            if currentView:
                current_pipeline = currentView.controller.current_pipeline
                if current_pipeline:
                    current_pipeline.validate()
            
        # Update the state of the icons if changing between db and file
        # support
        dbState = getattr(get_vistrails_configuration(), 'dbDefault')
        if self.dbDefault != dbState:
            self.setDBDefault(dbState)

    def new_diff(self):
        selected_items = \
            self.get_current_view().version_view.scene().selectedItems()
        if len(selected_items) == 2:
            selected_ids = [item.id for item in selected_items]
            self.get_current_view().diff_requested(*selected_ids)

    def setup_recent_vistrails(self):
        conf = get_vistrails_configuration()
        if conf.check('recentVistrailList'):
            self.recentVistrailLocators = \
                RecentVistrailList.unserialize(conf.recentVistrailList)
        else:
            self.recentVistrailLocators = RecentVistrailList()
        conf.subscribe('maxRecentVistrails', self.max_recent_vistrails_changed)
        self.update_recent_vistrail_actions()

    def open_recent_vistrail(self):
        """ open_recent_vistrail() -> None
        Opens a vistrail from Open Recent menu list
        
        """
        action = self.sender()
        if action:
            self.open_vistrail_without_prompt(action.locator)
            self.set_current_locator(action.locator)
            
    def update_recent_vistrail_menu(self):
        #check if we have enough actions
        def update_menu(openRecentMenu):
            openRecentMenu.clear()
            for i, locator in enumerate(self.recentVistrailLocators.locators):
                action = QtGui.QAction(self)
                self.connect(action, QtCore.SIGNAL("triggered()"),
                             self.open_recent_vistrail)
                action.locator = locator
                action.setText("&%d %s" % (i+1, locator.name))
                openRecentMenu.addAction(action)
        update_menu(self.qmenus['openRecent'])
        for w in self.windows.values():
            update_menu(w.qmenus['openRecent'])
            
    def update_window_menu(self):
        def update_menu(windowMenu):
            windowMenu.clear()
            action = QtGui.QAction("Main Window", self, 
                                   triggered=self.activateWindow)
            action.setCheckable(True)
            if self.current_view.window() == self:
                action.setChecked(True)
            windowMenu.addAction(action)
            for view, w in self.windows.iteritems():
                action = QtGui.QAction(view.get_name(),
                                       self,
                                       triggered=w.activateWindow)
                action.setCheckable(True)
                if view == self.current_view:
                    action.setChecked(True)
                windowMenu.addAction(action)

        update_menu(self.qmenus['window'])
        for w in self.windows.values():
            update_menu(w.qmenus['window'])
            
    def update_merge_menu(self):
        #check if we have enough actions
        def update_menu(mergeMenu):
            mergeMenu.clear()
            for i in xrange(self.stack.count()):
                view = self.stack.widget(i)
                # skip merge with self and not saved views
                if view == self.current_view or not view.controller.vistrail.locator:
                    continue
                action = QtGui.QAction(self)
                self.connect(action, QtCore.SIGNAL("triggered()"),
                             self.merge_vistrail)
                action.controller = view.controller
                action.setText("%s" % view.controller.vistrail.locator.name)
                mergeMenu.addAction(action)
            for view, w in self.windows.iteritems():
                # skip merge with self and not saved views
                if view == self.current_view or not view.controller.vistrail.locator:
                    continue
                action = QtGui.QAction(self)
                self.connect(action, QtCore.SIGNAL("triggered()"),
                             self.merge_vistrail)
                action.controller = view.controller
                action.setText("%s" % view.controller.vistrail.locator.name)
                mergeMenu.addAction(action)
                
        update_menu(self.qmenus['merge'])
        for w in self.windows.values():
            update_menu(w.qmenus['merge'])

    def update_recent_vistrail_actions(self):
        maxRecentVistrails = \
            int(get_vistrails_configuration().maxRecentVistrails)
        self.recentVistrailLocators.ensure_no_more_than_max(maxRecentVistrails)
        self.update_recent_vistrail_menu()
        
        conf = get_vistrails_persistent_configuration()
        tconf = get_vistrails_configuration()
        conf.recentVistrailList = self.recentVistrailLocators.serialize()
        tconf.recentVistrailList = conf.recentVistrailList
        VistrailsApplication.save_configuration()
        
    def set_current_locator(self, locator):
        """ set_current_locator(locator: CoreLocator)
        Updates the list of recent files in the gui and in the configuration
        
        """
        if locator:
            self.recentVistrailLocators.add_locator(locator)
            self.update_recent_vistrail_actions()
    
    def max_recent_vistrails_changed(self, field, value):
        """max_recent_vistrails_changed()-> obj
        callback to create an object to be used as a subscriber when the 
        configuration changed.
        
        """
        self.update_recent_vistrail_actions()
                
    def configure_module(self):
        from gui.module_configuration import QModuleConfiguration
        action_name = QModuleConfiguration.instance().get_title()
        # easy way to make sure that configuration window is raised
        self.qactions[action_name].setChecked(False)
        self.qactions[action_name].setChecked(True)

    def show_documentation(self):
        from gui.module_documentation import QModuleDocumentation
        action_name = QModuleDocumentation.instance().get_title()
        # easy way to make sure that documentation window is raised
        self.qactions[action_name].setChecked(False)
        self.qactions[action_name].setChecked(True)

    def show_group(self):
        class DummyController(object):
            def __init__(self, pip):
                self.current_pipeline = pip
                self.search = None
        active_window = VistrailsApplication.activeWindow()
        central_widget = active_window.centralWidget()
        if central_widget.metaObject().className() == "QPipelineView":
            current_scene = central_widget.scene()
        else:
            current_scene = self.get_current_tab().scene()
        selected_module_ids = current_scene.get_selected_module_ids()
        if len(selected_module_ids) > 0:
            for m_id in selected_module_ids:
                module = current_scene.current_pipeline.modules[m_id]
                if module.is_group() or module.is_abstraction():
                    pipelineMainWindow = QtGui.QMainWindow(self)
                    pipelineView = QPipelineView()
                    controller = DummyController(module.pipeline)
                    pipelineView.controller = controller
                    pipelineMainWindow.setCentralWidget(pipelineView)
                    pipelineView.scene().controller = \
                        controller
                    controller.current_pipeline_view = \
                        pipelineView.scene()
                    module.pipeline.ensure_connection_specs()
                    pipelineView.scene().setupScene(module.pipeline)
                    pipelineView.scene().current_pipeline = module.pipeline
                    pipelineView.scene().fitToView(pipelineView, True)
                    pipelineView.show()
                    pipelineMainWindow.show()

    def openAbstraction(self, filename):
        locator = XMLFileLocator(filename)
        self.open_vistrail_without_prompt(locator, None, False, True)

    def edit_abstraction(self):
        current_scene = self.get_current_tab().scene()
        selected_module_ids = current_scene.get_selected_module_ids()
        if len(selected_module_ids) > 0:
            for m_id in selected_module_ids:
                module = current_scene.current_pipeline.modules[m_id]
                if module.is_abstraction():
                    from core.modules.abstraction import identifier as \
                        abstraction_pkg                    
                    ann_get = module.vistrail.get_annotation
                    if module.package == abstraction_pkg and \
                            ann_get('__abstraction_descriptor_info__') is None:
                        desc = module.module_descriptor
                        filename = desc.module.vt_fname
                        self.openAbstraction(filename)
                    else:
                        show_info('Package SubWorkflow is Read-Only',
                                  "This SubWorkflow is from a package and "
                                  "cannot be modified.  You can create an "
                                  "editable copy in 'My SubWorkflows' using "
                                  "'Edit->Import SubWorkflow'")
    def merge_vistrail(self):
        action = self.sender()
        if action:
            self.merge_vistrails(self.current_view.controller, action.controller)

    def merge_vistrails(self, c1, c2):
        """ merge_vistrails(c1: VistrailController, c2: VistrailController) -> None
            hamdle merge vistrail from 2 controller into new vistrail

        """
        thumb_cache = ThumbnailCache.getInstance()
        
        l1 = c1.locator._name if c1.locator is not None else ''
        t1 = c1.find_thumbnails(tags_only=thumb_cache.conf.tagsOnly) \
            if thumb_cache.conf.autoSave else []
        s1 = SaveBundle(c1.vistrail.vtType, c1.vistrail.do_copy(), c1.log, thumbnails=t1)

        l2 = c2.locator._name if c2.locator is not None else ''
        t2 = c2.find_thumbnails(tags_only=thumb_cache.conf.tagsOnly) \
            if thumb_cache.conf.autoSave else []
        s2 = SaveBundle(c2.vistrail.vtType, c2.vistrail, c2.log, thumbnails=t2)

        db.services.vistrail.merge(s1, s2, "", merge_gui, l1, l2)
        vistrail = s1.vistrail
        vistrail.locator = None
        vistrail.set_defaults()
        view = self.create_view(vistrail, None)
        view.controller.set_vistrail(vistrail, None, thumbnails=s1.thumbnails)
        view.controller.set_changed(True)
        self.view_changed(view)
        self.qactions['history'].trigger()
        view.version_view.scene().fitToView(view.version_view, True)


        
    def do_tag_prompt(self, name="", exists=False):
        if exists:
            prompt = "'%s' already exists.  Enter a new tag" % name
        else:
            prompt = "Enter a tag"
            
        (text, ok) = QtGui.QInputDialog.getText(None, 
                                                'Tag Version',
                                                prompt,
                                                QtGui.QLineEdit.Normal,
                                                name)
        if ok and not text.isEmpty():
            return str(text).strip().rstrip()
        if not ok:
            return None
        return ""

    def add_tag(self, check_exists=True):
        controller = self.get_current_controller()
        vistrail = controller.vistrail
        name = self.do_tag_prompt()
        if name is None:
            return None
        while name == "" or (check_exists and vistrail.has_tag_str(name)):
            name = self.do_tag_prompt(name, name != "")
            if name is None:
                return None
        controller.update_current_tag(name)
        
    def publish_to_crowdlabs(self):
        dialog = QRepositoryDialog(self)
        dialog.exec_()
        
    def closeNotPinPalettes(self):
        if (QtGui.QApplication.activeWindow() == self or 
            QtGui.QApplication.activeWindow() in self.windows.values()):
            for p in self.palettes:
                if p.toolWindow().window() == QtGui.QApplication.activeWindow():
                    if (p.toolWindow().isVisible() and 
                        not p.toolWindow().isFloating() and not p.get_pin_status()):
                        p.toolWindow().close()
                      
    def createMenu(self):
        """ createMenu() -> None
        Initialize menu bar of builder window

        """
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.newVistrailAction)
        self.fileMenu.addAction(self.openFileAction)
        self.openRecentMenu = self.fileMenu.addMenu('Open Recent')
        
        self.update_recent_vistrail_menu()
            
        self.fileMenu.addAction(self.saveFileAction)
        self.fileMenu.addAction(self.saveFileAsAction)
        self.fileMenu.addAction(self.closeVistrailAction)
        self.fileMenu.addSeparator()
        self.importMenu = self.fileMenu.addMenu('Import')
        self.importMenu.addAction(self.importFileAction)
        self.importMenu.addSeparator()
        self.importMenu.addAction(self.importWorkflowAction)
        self.exportMenu = self.fileMenu.addMenu('Export')
        self.exportMenu.addAction(self.exportFileAction)
        self.exportMenu.addAction(self.exportStableAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.savePDFAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.saveWorkflowAction)
        self.exportMenu.addAction(self.exportWorkflowAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.saveOpmAction)
        self.exportMenu.addAction(self.saveLogAction)
        self.exportMenu.addAction(self.exportLogAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.saveRegistryAction)
        self.exportMenu.addAction(self.exportRegistryAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitVistrailsAction)

        self.editMenu = self.menuBar().addMenu('&Edit')
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.pasteAction)
        self.editMenu.addAction(self.selectAllAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.groupAction)
        self.editMenu.addAction(self.ungroupAction)
        self.editMenu.addAction(self.showGroupAction)
        self.editMenu.addAction(self.makeAbstractionAction)
        self.editMenu.addAction(self.convertToAbstractionAction)
        self.editMenu.addAction(self.editAbstractionAction)
        self.editMenu.addAction(self.importAbstractionAction)
        self.editMenu.addAction(self.exportAbstractionAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.controlFlowAssistAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.repositoryOptions)
        self.mergeMenu = self.editMenu.addMenu('Merge with')
        self.mergeMenu.menuAction().setEnabled(False)
        self.mergeMenu.menuAction().setStatusTip('Merge another VisTrail into the current VisTrail')
        self.editMenu.addAction(self.repositoryOptions)
        self.editMenu.addSeparator()        
        self.editMenu.addAction(self.editPreferencesAction)

        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(self.workspaceAction)
        self.viewMenu.addAction(self.shellAction)
        self.viewMenu.addAction(self.debugAction)
        self.viewMenu.addAction(self.provenanceBrowserAction)
        self.viewMenu.addAction(self.messagesAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.expandBranchAction)
        self.viewMenu.addAction(self.collapseBranchAction)
        self.viewMenu.addAction(self.collapseAllAction)
        #self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.hideBranchAction)
        self.viewMenu.addAction(self.showAllAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.pipViewAction)
        self.viewMenu.addAction(
            self.modulePalette.toolWindow().toggleViewAction())
        self.viewMenu.addAction(self.methodsViewAction)
        self.viewMenu.addAction(self.setMethodsViewAction)
        self.viewMenu.addAction(self.moduleConfigViewAction)
        self.viewMenu.addAction(self.propertiesViewAction)
        self.viewMenu.addAction(self.propertiesOverlayAction)

        self.runMenu = self.menuBar().addMenu('&Run')
        self.runMenu.addAction(self.executeCurrentWorkflowAction)
        self.runMenu.addAction(self.executeDiffAction)
        self.runMenu.addAction(self.executeQueryAction)
        self.runMenu.addAction(self.executeExplorationAction)
        self.runMenu.addSeparator()
        self.runMenu.addAction(self.flushCacheAction)

        self.vistrailMenu = self.menuBar().addMenu('Vis&trail')
        self.vistrailMenu.menuAction().setEnabled(False)

        self.packagesMenu = self.menuBar().addMenu('Packages')
        self.packagesMenu.menuAction().setEnabled(False)

        self.helpMenu = self.menuBar().addMenu('Help')
        self.helpMenu.addAction(self.helpAction)
        self.helpMenu.addAction(self.checkUpdateAction)
        
    def applicationFocusChanged(self, old, current):
        if current is not None:
            owner = current.window()
            if owner != self._focus_owner:
                self._focus_owner = owner
                if (self.isAncestorOf(current) or 
                    current.window() in self.windows.values()):
                    view = self.get_current_view()
                    if view:
                        self.change_view(view)
                        view.reset_tab_view_to_current()
                        self.update_window_menu()
                elif isinstance(current, BaseView):
                    view = current.get_vistrail_view()
                    if view:
                        self.change_view(view)
                        view.set_to_current(current)
                        self.update_window_menu()
     
_app = None
_global_menubar = None
    
class QVistrailViewWindow(QtGui.QMainWindow):
    def __init__(self, view, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
        self.view = view
        self.setDocumentMode(True)
        self.setCentralWidget(view)
        
        # This keeps track of the menu items for each package
        self._package_menu_items = {}
        
        self.create_actions()
        self.init_toolbar()
        self.view.setVisible(True)
        self.setWindowTitle(self.view.get_name())
        
    def close_vistrail(self):
        return _app.close_vistrail(self.view)
        
    def closeEvent(self, event):
        if not self.close_vistrail():
            event.ignore()
        else:
            self.emit(QtCore.SIGNAL("window_closed"), self.view)
            event.accept()
        
    def create_actions(self):

        palette_actions, palettes = _app.create_palette_actions()
        palette_actions = list(palette_actions)
        
        actions = [("file", "&File",
                    [('newVistrail', "&New",
                      {'icon': CurrentTheme.NEW_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.New,
                       'statusTip': 'Create a new vistrail',
                       'callback': _app.new_vistrail}),
                     ('openFile', "&Open",
                      {'icon': CurrentTheme.OPEN_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.Open,
                       'statusTip': 'Open an existing vistrail from a file',
                       'callback': _app.open_vistrail_default}),
                     ("openRecent", "Open Recent", 
                      []),
                     ('saveFile', "&Save",
                      {'icon': CurrentTheme.SAVE_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.Save,
                       'statusTip': "Save the current vistrail to a file",
                       'enabled': False,
                       'callback': \
                           _app.pass_through_locator(self.get_current_view,
                                                     'save_vistrail')}),
                     ('saveFileAs', "Save as...",
                      {'shortcut': QtGui.QKeySequence.SaveAs,
                       'statusTip': "Save the current vistrail to a " \
                           "different file location",
                       'enabled': False,
                       'callback': \
                           _app.pass_through_locator(self.get_current_view,
                                                     'save_vistrail_as')}),
                     ('closeVistrail', "Close",
                      {'shortcut': QtGui.QKeySequence.Close,
                       'statusTip': "Close the current vistrail",
                       'enabled': True,
                       'callback': _app.close_vistrail}),
                     "---",
                     ("import", "Import",
                      [('importFile', "From DB...",
                        {'icon': CurrentTheme.OPEN_VISTRAIL_DB_ICON,
                         'statusTip': "Import an existing vistrail " \
                             "from a database",
                         'callback': \
                             _app.import_vistrail_default}),
                       "---",
                       ('importWorkflow', "Workflow...",
                        {'statusTip': "Import a workflow from an XML file",
                         'enabled': True,
                         'callback': _app.import_workflow_default})]),
                     ("export", "Export",
                      [('exportFile', "To DB...",
                        {'statusTip': "Export the current vistrail to a " \
                             "database",
                         'enabled': False,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'export_vistrail', 
                                                       reverse=True)}),
                       ('exportStable', "To Stable Version...",
                        {'statusTip': "Save vistrail as XML according to " \
                             "the older (stable) schema",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'export_stable')}),
                       "---",
                       ('savePDF', "PDF...",
                        {'statusTip': "Save the current view to a PDF file",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_tab,
                                                       'save_pdf')}),
                       "---",
                       ('saveWorkflow', "Workflow To XML...",
                        {'statusTip': "Save the current workflow to a file",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       FileLocator())}),
                       ('exportWorkflow', "Workflow to DB...",
                        {'statusTip': "Save the current workflow to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       DBLocator)}),
                       "---",
                       ('saveOpm', "OPM XML...",
                        {'statusTip': "Save proveannce according to the " \
                             "Open Provenance Model in XML",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_view,
                                                       'save_opm')}),
                       ('saveLog', "Log to XML...",
                        {'statusTip': "Save the execution log to a file",
                         'enabled': False,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_log',
                                                       FileLocator())}),
                       ('exportLog', "Log to DB...",
                        {'statusTip': "Save the execution log to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_log',
                                                       DBLocator)}),
                       "---",
                       ('saveRegistry', "Registry to XML...",
                        {'statusTip': "Save the current registry to a file",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_registry',
                                                       FileLocator())}),
                       ('exportRegistry', "Registry to DB...",
                        {'statusTip': "Save the current registry to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_registry',
                                                       DBLocator)})]),
                     "---",
                     ('quitVistrails', "Quit",
                      {'shortcut': QtGui.QKeySequence.Quit,
                       'statusTip': "Exit VisTrails",
                       'callback': _app.quit})]),
                   ("edit", "&Edit",
                    [("undo", "Undo",
                      {'statusTip': "Undo the previous action",
                       'shortcut': QtGui.QKeySequence.Undo,
                       'enabled': False}),
                     ("redo", "Redo",
                      {'statusTip': "Redo an undone action",
                       'shortcut': QtGui.QKeySequence.Redo,
                       'enabled': False}),
                     "---",
                     ("copy", "Copy",
                      {'statusTip': "Copy the selected modules in the " \
                           "current pipeline view",
                       'shortcut': QtGui.QKeySequence.Copy,
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'copySelection')}),
                     ("paste", "Paste",
                      {'statusTip': "Paste modules from the clipboard into " \
                           "the current pipeline view",
                       'shortcut': QtGui.QKeySequence.Paste,
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'pasteFromClipboard')}),
                     ("selectAll", "Select All",
                      {'statusTip': "Select all modules in the current " \
                           "pipeline view",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.SelectAll,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'selectAll')}),
                     "---",
                     ("controlFlowAssist", "Control Flow Assistant",
                      {'statusTip': "Create a loop over the selected modules"}),
                     ("merge", "Merge with...", 
                      []),
                     "---",
                     ("editPreferences", "Preferences...",
                      {'statusTip': "Edit system preferences",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.Preferences,
                       'callback': _app.showPreferences}),
                     ]),
                   ("run", "&Workflow",
                    [("execute", "Execute",
                      {'icon': CurrentTheme.EXECUTE_PIPELINE_ICON,
                       'shortcut': 'Ctrl+Return',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_view,
                                                     'execute')}),
                     ("flushCache", "Erase Cache Contents", 
                      {'enabled': True,
                       'callback': _app.flush_cache}),
                     "---",
                     ("group", "Group",
                      {'statusTip': "Group the selected modules in the " \
                           "current pipeline view",
                       'shortcut': 'Ctrl+G',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'group')}),
                     ("ungroup", "Ungroup",
                      {'statusTip': "Ungroup the selected groups in the " \
                           "current pipeline view",
                       'shortcut': 'Ctrl+Shift+G',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'ungroup')}),
                     ("showGroup", "Show Pipeline",
                      {'statusTip': "Show the underlying pipeline for the " \
                           "selected group in the current pipeline view",
                       'enabled': False,
                       'callback': _app.show_group}),
                     "---",
                     ("makeAbstraction", "Create Subworkflow",
                      {'statusTip': "Create a subworkflow from the selected " \
                           "modules",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'makeAbstraction')}),
                     ("convertToAbstraction", "Convert to Subworkflow",
                      {'statusTip': "Convert selected group to a subworkflow",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'convertToAbstraction')}),
                     ("editAbstraction", "Edit Subworkflow",
                      {'statusTip': "Edit a subworkflow",
                       'enabled': False,
                       'callback': _app.edit_abstraction}),
                     ("importAbstraction", "Import Subworkflow",
                      {'statusTip': "Import subworkflow from a vistrail to " \
                           "local subworkflows",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'importAbstraction')}),
                     ("exportAbstraction", "Export Subworkflow",
                      {'statusTip': "Export subworkflow from local " \
                           "subworkflows for use in a package",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'exportAbstraction')}),
                     "---",
                     ("configureModule", "Configure Module...",
                      {'shortcut': "Ctrl+E",
                       'enabled': False,
                       'callback': _app.configure_module}),
                     ("documentModule", "Module Documentation...",
                      {'enabled': False,
                       'callback': _app.show_documentation})]),
                   ("vistrail", "Vis&trail",
                    [("tag", "Tag...",
                      {'statusTip': "Tag the current pipeline",
                       'shortcut': "Ctrl+Shift+T",
                       'enabled': True,
                       'callback': _app.add_tag}),
                     "---",
                     ("expandBranch", "Expand Branch",
                      {'statusTip': "Expand all versions in the tree below " \
                           "the current version",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'expand_all_versions_below')}),
                     ("collapseBranch", "Collapse Branch",
                      {'statusTip': "Collapse all expanded versions of the " \
                           "tree",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'collapse_all_versions_below')}),
                     ("collapseAll", "Collapse All",
                      {'statusTip': "Collapse all expanded branches of the " \
                           "tree",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'collapse_all_versions')}),
                     ("hideBranch", "Hide Branch",
                      {'statusTip': "Hide all versions in the tre including " \
                           "and below the current version",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'hide_versions_below')}),
                     ("showAll", "Show All",
                      {'enabled': True,
                       'statusTip': "Show all hidden versions",
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'show_all_versions')})]),
                   ("view", "&Views",
                    [("newView", "New Pipeline View",
                      {'shortcut': QtGui.QKeySequence.AddTab,
                       'enabled': True,
                       'statusTip': "Create a new pipeline view",
                       'callback': _app.pass_through(self.get_current_view,
                                                     'add_pipeline_view')}),
                     ("newDiff", "New Visual Difference",
                      {'enabled': True,
                       'statusTip': "Create a new visual difference for two" \
                           "pipelines",
                       'callback': _app.new_diff}),
                     "---",
                     ("zoomToFit", "Zoom To Fit",
                      {'enabled': True,
                       'shortcut': "Ctrl+R",
                       'statusTip': "Fit current view to window",
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomToFit')}),
                     ("zoomIn", "Zoom In",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomIn,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomIn')}),
                     ("zoomOut", "Zoom Out",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomOut,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomOut')}),
                     "---",
                     ("pipeline", "Pipeline",
                      {'icon': CurrentTheme.PIPELINE_ICON,
                       'checkable': True,
                       'checked': True,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'pipeline_change')}),
                     ("history", "History",
                      {'icon': CurrentTheme.HISTORY_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'history_change')}),
                     ("search", "Search",
                      {'icon': CurrentTheme.QUERY_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'search_change')}),
                     ("explore", "Explore",
                      {'icon': CurrentTheme.EXPLORE_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'explore_change')}),
                     ("provenance", "Provenance",
                      {'icon': CurrentTheme.PROVENANCE_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'provenance_change')}),
                    ("mashup", "Mashup",
                      {'icon': CurrentTheme.MASHUP_ICON,
                       'checkable': True,
                       'checked': False,
                       'enabled': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'mashup_change')}),
                     "---"] + palette_actions + ["---", 
                       ("dockPalettes", "Dock Palettes", 
                        {'enabled': True,
                         'statusTip': "Dock palettes on active window",
                         'callback': _app.dock_palettes})]),
                   ("publish", "Publish",
                    [("publishPaper", "To Paper...", 
                      {'enabled': True,
                       'statusTip': \
                           "Embed workflow and results into a paper",
                        'callback': _app.pass_through(self.get_current_view,
                                                      'publish_to_paper')}),
                     ("publishWeb", "To Wiki...",
                      {'enabled': True,
                       'statusTip': "Embed workflow in wiki",
                       'callback' : _app.pass_through(self.get_current_view,
                                                      'publish_to_web')}),
                     ("publishCrowdLabs", "To crowdLabs...",
                      {'enabled': True,
                       'statusTip': "Publish workflows on crowdlabs.org",
                       'callback': _app.publish_to_crowdlabs})]),
                   ("packages", "Packages", 
                      []),
                   ("window", "Window", 
                      []),
                   ("help", "Help",
                    [("help", "About VisTrails...", 
                      {'callback': _app.showAboutMessage}),
                     ("checkUpdate", "Check for Updates", 
                      {'callback': _app.showUpdatesMessage})])]


        qactions = {}
        qmenus = {}
        def process_list(action_list, parent):
            for data in action_list:
                if data == "---":
                    if parent is not None:
                        parent.addSeparator()
                    continue
                name, title, options = data
                if type(options) == list:
                    # menu
                    if parent is not None:
                        qmenu = parent.addMenu(title)
                    qmenus[name] = qmenu
                    process_list(options, qmenu)
                else:
                    qaction = QtGui.QAction(title, self)
                    callback = None
                    if 'callback' in options:
                        callback = options['callback']
                        del options['callback']
                    for option, value in options.iteritems():
                        method = getattr(qaction, 'set%s' % \
                                             option[0].capitalize() + \
                                             option[1:])
                        method(value)
                    qactions[name] = qaction
                    if parent is not None:
                        parent.addAction(qaction)
                    if callback is not None:
                        if 'checkable' in options and \
                                options['checkable'] is True:
                            self.connect(qaction, 
                                         QtCore.SIGNAL("toggled(bool)"),
                                         callback)
                        else:
                            self.connect(qaction, QtCore.SIGNAL("triggered()"),
                                         callback)
                        

            self.qactions = qactions
            self.qmenus = qmenus

        menu_bar = self.menuBar()
        print 'menu_bar:', menu_bar
        process_list(actions, menu_bar)
        print 'done processing list'
            
        self.build_packages_menu_from_main_app()
        
    def get_current_controller(self):
        return self.view.get_controller()

    def get_current_view(self):
        return self.view
    
    def get_current_tab(self):
        return self.view.get_current_tab()

    def get_current_scene(self):
        return self.get_current_tab().scene()

    def init_toolbar(self):
        def create_spacer():
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                                  QtGui.QSizePolicy.Preferred)
            return spacer
        def create_separator():
            sep = QtGui.QWidget()
            sep.setMinimumWidth(50)
            return sep
        
        self.selected_mode = None
        self.toolbar = QtGui.QToolBar(self)
        
        #left side
        for action in [self.qactions[n] 
                       for n in ['newVistrail', 'openFile', 'saveFile']]:
            self.toolbar.addAction(action)
        
        self.toolbar.addWidget(create_spacer())
        self.view_action_group = QtGui.QActionGroup(self)
        for action in [self.qactions[n] 
                       for n in ['pipeline', 'history', 
                                 'search', 'explore', 'provenance', 'mashup']]:
            self.toolbar.addAction(action)
            self.view_action_group.addAction(action)
            
        self.toolbar.addWidget(create_separator())
        for action in [self.qactions[n] 
                       for n in ['execute']]:
            self.toolbar.addAction(action)
            
        
        self.toolbar.addWidget(create_spacer())
        self.toolbar.addWidget(create_spacer())
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        self.setUnifiedTitleAndToolBarOnMac(True)
        
    def build_packages_menu_from_main_app(self):
        if len(self._package_menu_items) == 0:
            self.qmenus['packages'].menuAction().setEnabled(True)
            
        for (pkg_id, d) in _app._package_menu_items.iteritems():
            self._package_menu_items[pkg_id] = {}
            for pkg_name,items in d['items']:
                pkg_menu = self.qmenus['packages'].addMenu(str(pkg_name))
                self._package_menu_items[pkg_id]['menu'] = pkg_menu
                self._package_menu_items[pkg_id]['items'] = (pkg_name, items)
                for item in items:
                    (name, callback) = item
                    action = QtGui.QAction(name,self,
                                           triggered=callback)
                    pkg_menu.addAction(action)
        
    def set_title(self, title):
        self.setWindowTitle(title)
        
    def get_name(self):
        return self.windowTitle()

    def set_name(self):
        if self.view:
            self.set_title(self.view.get_name())
        else:
            self.set_title('(empty)')
        