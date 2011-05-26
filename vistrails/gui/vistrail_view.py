############################################################################
##
## Copyright (C) 2006-2011 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
""" The file describes a container widget consisting of a pipeline
view and a version tree for each opened Vistrail """

from PyQt4 import QtCore, QtGui

from core.collection import Collection
from core.db.locator import untitled_locator
from core.debug import critical
from core.system import vistrails_default_file_type
from core.thumbnails import ThumbnailCache
from core.vistrail.vistrail import Vistrail

from gui.collection.vis_log import QLogView
from gui.pipeline_view import QPipelineView
from gui.version_view import QVersionTreeView
from gui.query_view import QQueryView
from gui.paramexplore.pe_view import QParamExploreView
from gui.vis_diff import QDiffView
from gui.paramexplore.param_view import QParameterView
from gui.vistrail_controller import VistrailController

################################################################################

class QVistrailView(QtGui.QWidget):
    """
    QVistrailView is a widget containing four stacked widgets: Pipeline View,
    Version Tree View, Query View and Parameter Exploration view
    for manipulating vistrails.
    """
    def __init__(self, vistrail, locator=None, parent=None):
        """ QVistrailView(parent: QWidget) -> QVistrailView
        
        """
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.notifications = {}
        self.tabs = QtGui.QTabBar(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.hide()
        layout.addWidget(self.tabs)
        self.stack = QtGui.QStackedWidget(self)
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.tab_to_stack_idx = {}
        self.tab_state = {}

        # Initialize the vistrail controller
        self.controller = VistrailController(vistrail)

        # Create the initial views
        self.version_view = None
        pipeline_view = self.create_pipeline_view()
        self.version_view = self.create_version_view()
        self.query_view = self.create_query_view()
        self.pe_view = self.create_pe_view()
        self.log_view = self.create_log_view()
        
        self.set_controller(self.controller)
        self.locator = locator
        self.controller.set_vistrail(vistrail, self.locator)

        self.connect(self.tabs, QtCore.SIGNAL("currentChanged(int)"),
                     self.tab_changed)
        self.connect(self.tabs, QtCore.SIGNAL("tabCloseRequested(int)"),
                     self.remove_view_by_index)
        self.tabs.setCurrentIndex(0)
        self.current_tab = self.stack.currentWidget()
        self.view_changed()
        self.tab_changed(0)

        self.connect(self.controller,
                     QtCore.SIGNAL('stateChanged'),
                     self.stateChanged)

        # self.controller = VistrailController()
        # self.controller.vistrail_view = self
        # self.connect(self.controller,
        #              QtCore.SIGNAL('stateChanged'),
        #              self.stateChanged)
        # self.connect(self.controller,
        #              QtCore.SIGNAL('new_action'),
        #              self.new_action)

        # # self.versionTab.versionView.scene()._vistrail_view = self
        # self.connect(self.versionTab.versionView.scene(),
        #              QtCore.SIGNAL('versionSelected(int,bool,bool,bool)'),
        #              self.versionSelected,
        #              QtCore.Qt.QueuedConnection)

        # self.connect(self.versionTab,
        #              QtCore.SIGNAL('twoVersionsSelected(int,int)'),
        #              self.twoVersionsSelected)
        # self.connect(self.queryTab,
        #              QtCore.SIGNAL('queryPipelineChange'),
        #              self.queryPipelineChange)
        # self.connect(self.peTab,
        #              QtCore.SIGNAL('exploreChange(bool)'),
        #              self.exploreChange)

        # # We also keep track where this vistrail comes from
        # # So we can save in the right place
        # self.locator = None
        
        # self.closeEventHandler = None

        # # the redo stack stores the undone action ids 
        # # (undo is automatic with us, through the version tree)
        # self.redo_stack = []

        # # Keep the state of the execution button and menu items for the view
        # self.execQueryEnabled = False
        # self.execDiffEnabled = False
        # self.execExploreEnabled = False
        # self.execPipelineEnabled = False
        # self.execDiffId1 = -1
        # self.execDiffId2 = -1

    def get_notifications(self):
        return self.notifications

    def set_controller(self, controller):
        self.controller = controller
        self.controller.vistrail_view = self
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            if hasattr(view, 'set_controller'):
                view.set_controller(controller)

    def get_controller(self):
        return self.controller

    def get_name(self):
        title = self.controller.name
        if title=='':
            title = 'Untitled%s'%vistrails_default_file_type()
        if self.controller.changed:
            title += '*'
        # self.setWindowTitle(title)
        return title

    def set_name(self):
        title = self.get_name()
        self.setWindowTitle(title)

    def reset_version_view(self):
        if self.version_view is not None:
            self.version_view.scene().setupScene(self.controller)

    def pipeline_selected(self):
        from gui.vistrails_window import _app
        print "PIPELINE"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(),
                             self.stack.currentWidget().get_title())
        self.tab_state[self.tabs.currentIndex()] = _app.qactions['pipeline']

    def pipeline_unselected(self):
        print "PIPELINE UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(),
                             self.stack.currentWidget().get_title())

    def history_selected(self):
        from gui.vistrails_window import _app
        print "VERSION"
        self.stack.setCurrentIndex(self.stack.indexOf(self.version_view))
        self.tabs.setTabText(self.tabs.currentIndex(), "History")
        self.tab_state[self.tabs.currentIndex()] = _app.qactions['history']

    def history_unselected(self):
        print "VERSION UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(), 
                             self.stack.currentWidget().get_title())

    def query_selected(self):
        from gui.vistrails_window import _app
        print "QUERY"
        self.stack.setCurrentIndex(self.stack.indexOf(self.query_view))
        self.tabs.setTabText(self.tabs.currentIndex(), "Search")
        self.tab_state[self.tabs.currentIndex()] = _app.qactions['search']

    def query_unselected(self):
        print "QUERY UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(), 
                             self.stack.currentWidget().get_title())

    def explore_selected(self):
        from gui.vistrails_window import _app
        print "EXPLORE"
        self.stack.setCurrentIndex(self.stack.indexOf(self.pe_view))
        self.tabs.setTabText(self.tabs.currentIndex(), "Explore")
        self.tab_state[self.tabs.currentIndex()] = _app.qactions['explore']

    def explore_unselected(self):
        print "EXPLORE UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(), 
                             self.stack.currentWidget().get_title())

    def provenance_selected(self):
        from gui.vistrails_window import _app
        print "PROVENANCE"
        self.stack.setCurrentIndex(self.stack.indexOf(self.log_view))
        self.tabs.setTabText(self.tabs.currentIndex(), "Provenance")
        self.tab_state[self.tabs.currentIndex()] = _app.qactions['provenance']

    def provenance_unselected(self):
        print "PROVENANCE UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(), 
                             self.stack.currentWidget().get_title())

    def pipeline_change(self, checked):
        if checked:
            print "PIPELINE SELECTED"
            self.pipeline_selected()
        else:
            print "PIPELINE UNSELECTED"
            self.pipeline_unselected()
        self.view_changed()

    def history_change(self, checked):
        from vistrails_window import _app
        if checked:
            print "HISTORY SELECTED"
            self.history_selected()
        else:
            print "HISTORY UNSELECTED"
            self.history_unselected()
        self.view_changed()

    def search_change(self, checked):
        if checked:
            self.query_selected()
        else:
            self.query_unselected()
        self.view_changed()

    def explore_change(self, checked):
        if checked:
            self.explore_selected()
        else:
            self.explore_unselected()
        self.view_changed()

    def provenance_change(self, checked):
        if checked:
            self.provenance_selected()
        else:
            self.provenance_unselected()
        self.view_changed()

    def create_view(self, klass, add_tab=True):
        view = klass(self)
        idx = self.stack.addWidget(view)
        view.set_index(idx)
        if add_tab:
            tab_idx = self.tabs.addTab(view.get_title())
            view.set_tab_idx(tab_idx)
            self.tab_to_stack_idx[tab_idx] = idx
        self.connect(view, QtCore.SIGNAL("windowTitleChanged"),
                     self.view_title_changed)
        if self.tabs.count() == 1:
            self.tabs.hide()
        else:
            self.tabs.show()
        return view

    def view_title_changed(self, view):
        if self.stack.currentWidget() == view:
            self.tabs.setTabText(self.tabs.currentIndex(), view.windowTitle())

    def remove_view_by_index(self, index):
        self.tabs.removeTab(index)
        stack_idx = self.tab_to_stack_idx[index]
        if stack_idx >= 0:
            self.stack.removeWidget(self.stack.widget(stack_idx))
        if self.tabs.count() == 1:
            self.tabs.hide()

    def switch_to_tab(self, index):
        if index < 0:
            index = self.tabs.count() + index
        self.tabs.setCurrentIndex(index)
        self.tab_changed(index)

    def get_current_tab(self):
        widget = self.stack.currentWidget()
        if type(widget) == QQueryView:
            widget = widget.get_current_view()
        return widget

    def view_changed(self):
        from gui.vistrails_window import _app

        view = self.stack.currentWidget()
        _app.unset_action_links(self.current_tab)
        self.current_tab = view
        _app.set_action_links(self.current_tab.action_links, self.current_tab)

        for dock_loc, palette_klass in self.current_tab.layout.iteritems():
            palette_instance = palette_klass.instance()
            current_loc = _app.dockWidgetArea(palette_instance.toolWindow())
            print ">> P:", palette_instance.__class__.__name__, current_loc, \
                dock_loc
            
            if current_loc == dock_loc:
                # palette_instance.get_action().trigger()
                palette_instance.toolWindow().raise_()
                # print ">> doing show", palette_instance.toolWindow().isVisible()        

    def tab_changed(self, index):
        print 'raw tab_changed', index
        if index < 0 or self.controller is None:
            return

        from gui.vistrails_window import _app

        self.stack.setCurrentIndex(self.tab_to_stack_idx[index])
        for action in _app.view_action_group.actions():
            action.setChecked(False)
        self.selected_mode = None
        action = None
        if index in self.tab_state:
            action = self.tab_state[index]
            # if action is not None:
                # print 'running toggle'
                # action.toggle()
                # action.setChecked(True)
        else:
            self.tab_state[index] = _app.qactions['pipeline']
        if action is not None:
            action.setChecked(True)
            # _app.view_triggered(action)

        view = self.stack.widget(self.tab_to_stack_idx[index])
        if isinstance(view, QDiffView):
            view.set_to_current()
            print "view changed!", self.controller, \
                self.controller.current_version
            _app.notify("controller_changed", self.controller)
            self.reset_version_view()
        elif isinstance(view, QLogView):
            view.set_to_current()
            print "view changed!", self.controller, \
                self.controller.current_version
            _app.notify("controller_changed", self.controller)
            self.reset_version_view()
        elif isinstance(view, QPipelineView):
            print "PIPELINE_VIEW NEW SCENE:", id(view.scene())

            # need to set the controller's version, pipeline, view
            # to this view...
            # self.controller.current_version = view.current_version
            # self.controller.current_pipeline = view.current_pipeline
            view.set_to_current()
            print "view changed!", self.controller, \
                self.controller.current_version
            _app.notify("controller_changed", self.controller)
            self.reset_version_view()


    def create_pipeline_view(self):
        view = self.create_view(QPipelineView)
        self.connect(view.scene(), QtCore.SIGNAL('moduleSelected'), 
                     self.gen_module_selected(view))
        view.set_controller(self.controller)
        view.set_to_current()
        self.switch_to_tab(-1)
        return view

    def create_version_view(self):
        view = self.create_view(QVersionTreeView, False)
        self.connect(view.scene(), 
                     QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
                     self.version_selected)
        self.connect(view.scene(),
                     QtCore.SIGNAL('diffRequested(int,int)'),
                     self.diff_requested)
        return view

    def create_query_view(self):
        view = self.create_view(QQueryView, False)
        return view

    def create_diff_view(self):
        view = self.create_view(QDiffView)
        self.connect(view.scene(), QtCore.SIGNAL('moduleSelected'),
                     self.gen_module_selected(view))
        return view

    def create_pe_view(self):
        view = self.create_view(QParamExploreView, False)
        return view

    def create_log_view(self):
        from gui.vistrails_window import _app
        view = self.create_view(QLogView, False)
        self.notifications['execution_changed'] = view.set_execution
        return view

    def gen_module_selected(self, view):
        def module_selected(module_id, selection = []):
            from gui.vistrails_window import _app
            pipeline = view.scene().current_pipeline
            if module_id in pipeline.modules:
                module = pipeline.modules[module_id]
                _app.notify('module_changed', module)
            else:
                _app.notify('module_changed', None)
        return module_selected

    def version_selected(self, version_id, by_click, do_validate=True,
                         from_root=False, double_click=False):
        from gui.vistrails_window import _app
        print 'got version selected:', version_id
        view = self.stack.widget(
            self.tab_to_stack_idx[self.tabs.currentIndex()])

        if by_click:
            self.controller.change_selected_version(version_id, by_click, 
                                                    do_validate, from_root)

            view.scene().fitToView(view, True)
            if double_click:
                # view = self.create_pipeline_view()
                # view.set_controller(self.controller)
                # view.set_to_current()
                # self.tabs.setCurrentWidget(view.parent())
                _app.qactions['pipeline'].trigger()
        view.set_title(self.controller.get_pipeline_name())
        _app.notify("version_changed", version_id)
        _app.notify("pipeline_changed", self.controller.current_pipeline)

    def diff_requested(self, version_a, version_b):
        view = self.create_diff_view()
        view.set_controller(self.controller)
        view.set_diff(version_a,version_b)
        self.switch_to_tab(-1)

    def save_vistrail(self, locator_class, force_choose_locator=False):
        """
        force_choose_locator=True triggers 'save as' behavior

        """
        locator = self.controller.locator
        if locator is not None:
            locator_class = type(locator)

        print "CALLED SAVE VISTRAIL", locator_class

        self.flush_changes()
        gui_get = locator_class.save_from_gui
        # get a locator to write to
        if force_choose_locator:
            locator = gui_get(self, Vistrail.vtType,
                              self.controller.locator)
        else:
            locator = (self.controller.locator or
                       gui_get(self, Vistrail.vtType,
                               self.controller.locator))
        if locator == untitled_locator():
            locator = gui_get(self, Vistrail.vtType,
                              self.controller.locator)
        # if couldn't get one, ignore the request
        if not locator:
            return False
        # update collection
        try:
            self.controller.write_vistrail(locator)
        except Exception, e:
            debug.critical('An error has occurred', str(e))
            raise
            return False
        try:
            thumb_cache = ThumbnailCache.getInstance()
            self.controller.vistrail.thumbnails = \
                self.controller.find_thumbnails(
                    tags_only=thumb_cache.conf.tagsOnly)
            self.controller.vistrail.abstractions = \
                self.controller.find_abstractions(self.controller.vistrail, 
                                                  True)

            collection = Collection.getInstance()
            url = locator.to_url()
            # create index if not exist
            entity = collection.fromUrl(url)
            if entity:
                # find parent vistrail
                while entity.parent:
                    entity = entity.parent 
            else:
                entity = collection.updateVistrail(url, 
                                                   self.controller.vistrail)
            # add to relevant workspace categories
            collection.add_to_workspace(entity)
            collection.commit()
        except Exception, e:
            debug.critical('Failed to index vistrail', str(e))

        # update name
        self.set_name()
        from gui.vistrails_window import _app
        _app.view_changed(self)
        return locator

    def save_vistrail_as(self, locator_class):
        print "CALLED SAVE AS VISTRAIL", locator_class
        self.save_vistrail(locator_class, force_choose_locator=True)

    def has_changes(self):
        return self.controller.changed

    def flush_changes(self):
        """Flush changes in the vistrail before closing or saving.
        """
        # Quick workaround for notes focus out bug (ticket #182)
        # There's probably a much better way to fix this.
        from gui.version_prop import QVersionProp
        prop = QVersionProp.instance()
        prop.versionNotes.commit_changes()

    def execute(self):
        view = self.get_current_tab()
        if isinstance(view, QPipelineView):
            view.setFocus(QtCore.Qt.MouseFocusReason)
            # view.checkModuleConfigPanel()
            self.controller.execute_current_workflow()

    # def updateCursorState(self, mode):
    #     """ updateCursorState(mode: Int) -> None 
    #     Change cursor state in all different modes.

    #     """
    #     self.pipelineTab.pipelineView.setDefaultCursorState(mode)
    #     self.versionTab.versionView.setDefaultCursorState(mode)
    #     self.queryTab.pipelineView.setDefaultCursorState(mode)
    #     if self.parent().parent().parent().pipViewAction.isChecked():
    #         self.pipelineTab.pipelineView.pipFrame.graphicsView.setDefaultCursorState(mode)
    #         self.versionTab.versionView.pipFrame.graphicsView.setDefaultCursorState(mode)


    # def flush_changes(self):
    #     """Flush changes in the vistrail before closing or saving.
    #     """
    #     # Quick workaround for notes focus out bug (ticket #182)
    #     # There's probably a much better way to fix this.
    #     prop = self.versionTab.versionProp
    #     prop.versionNotes.commit_changes()

    # def setup_view(self, version=None):
    #     """setup_view(version = None:int) -> None

    #     Sets up the correct view for a fresh vistrail.

    #     Previously, there was a method setInitialView and another
    #     setOpenView.

    #     They were supposed to do different things but the code was
    #     essentially identical.

    #     FIXME: this means that the different calls are being handled
    #     somewhere else in the code. Figure this out."""

    #     if version is None:
    #         self.controller.select_latest_version()
    #         version = self.controller.current_version
    #     else:
    #         self.versionSelected(version, True, True, False)
    #     self.controller.recompute_terse_graph()
    #     self.controller.invalidate_version_tree(True)
    #     self.setPIPMode(True)
    #     self.setQueryMode(False)
       
    # def setPIPMode(self, on):
    #     """ setPIPMode(on: bool) -> None
    #     Set the PIP state for the view

    #     """
    #     self.pipelineTab.pipelineView.setPIPEnabled(on)
    #     self.versionTab.versionView.setPIPEnabled(on)

    # def setQueryMode(self, on):
    #     """ setQueryMode(on: bool) -> None
    #     Set the Reset Query button mode for the view
        
    #     """
    #     self.pipelineTab.pipelineView.setQueryEnabled(on)
    #     self.versionTab.versionView.setQueryEnabled(on)
    #     self.queryTab.pipelineView.setQueryEnabled(on)

    # def setMethodsMode(self, on):
    #     """ setMethodsMode(on: bool) -> None
    #     Set the methods panel state for the view

    #     """
    #     if on:
    #         self.pipelineTab.methodPalette.toolWindow().show()
    #     else:
    #         self.pipelineTab.methodPalette.toolWindow().hide()

    # def setSetMethodsMode(self, on):
    #     """ setSetMethodsMode(on: bool) -> None
    #     Set the set methods panel state for the view

    #     """
    #     if on:
    #         self.pipelineTab.moduleMethods.toolWindow().show()
    #     else:
    #         self.pipelineTab.moduleMethods.toolWindow().hide()

    # def setPropertiesMode(self, on):
    #     """ setPropertiesMode(on: bool) -> None
    #     Set the properties panel state for the view

    #     """
    #     if on:
    #         self.versionTab.versionProp.toolWindow().show()
    #     else:
    #         self.versionTab.versionProp.toolWindow().hide()

    # def setPropertiesOverlayMode(self, on):
    #     """ setPropertiesMode(on: bool) -> None
    #     Set the properties overlay state for the view

    #     """
    #     if on:
    #         self.versionTab.versionView.versionProp.show()
    #     else:
    #         self.versionTab.versionView.versionProp.hide()
            
    # def setModuleConfigMode(self, on):
    #     """ setModuleConfigMode(on: bool) -> None
    #     Set the Module configuration panel state for the view

    #     """
    #     if on:
    #         self.pipelineTab.moduleConfig.toolWindow().show()
    #     else:
    #         self.pipelineTab.moduleConfig.toolWindow().hide()

    # def viewModeChanged(self, index):
    #     """ viewModeChanged(index: int) -> None        
    #     Slot for switching different views when the tab's current
    #     widget is changed
        
    #     """
    #     if self.stackedWidget.count()>index:
    #         self.stackedWidget.setCurrentIndex(index)

    # def pasteToCurrentTab(self):
    #     index = self.stackedWidget.currentIndex()
    #     if index == 0:
    #         self.pipelineTab.pipelineView.pasteFromClipboard()
    #     elif index == 2:
    #         self.queryTab.pipelineView.pasteFromClipboard()
            
    # def selectAll(self):
    #     index = self.stackedWidget.currentIndex()
    #     if index == 0:
    #         self.pipelineTab.pipelineView.scene().selectAll()    
    #     elif index == 2:
    #         self.queryTab.pipelineView.scene().selectAll()
            
    # def sizeHint(self):
    #     """ sizeHint(self) -> QSize
    #     Return recommended size of the widget
        
    #     """
    #     return QtCore.QSize(1024, 768)

    # def set_vistrail(self, vistrail, locator=None, abstractions=None, 
    #                  thumbnails=None):
    #     """ set_vistrail(vistrail: Vistrail, locator: BaseLocator) -> None
    #     Assign a vistrail to this view, and start interacting with it
        
    #     """
    #     self.vistrail = vistrail
    #     self.locator = locator
    #     self.controller.set_vistrail(vistrail, locator, abstractions, thumbnails)
    #     self.versionTab.setController(self.controller)
    #     self.pipelineTab.setController(self.controller)
    #     self.peTab.setController(self.controller)

    def stateChanged(self):
        """ stateChanged() -> None
        Handles 'stateChanged' signal from VistrailController """
        from gui.vistrails_window import _app
        _app.state_changed(self)
        

    # def stateChanged(self):
    #     """ stateChanged() -> None

    #     Handles 'stateChanged' signal from VistrailController
        
    #     Update the window and tab title
        
    #     """
    #     title = self.controller.name
    #     if title=='':
    #         title = 'untitled%s'%vistrails_default_file_type()
    #     if self.controller.changed:
    #         title += '*'
    #     self.setWindowTitle(title)
    #     # propagate the state change to the version prop
    #     # maybe in the future we should propagate as a signal
    #     versionId = self.controller.current_version
    #     self.versionTab.versionProp.updateVersion(versionId)

    # def emitDockBackSignal(self):
    #     """ emitDockBackSignal() -> None
    #     Emit a signal for the View Manager to take this widget back
        
    #     """
    #     self.emit(QtCore.SIGNAL('dockBack'), self)

    # def closeEvent(self, event):
    #     """ closeEvent(event: QCloseEvent) -> None
    #     Only close if we save information
        
    #     """
    #     if self.closeEventHandler:
    #         if self.closeEventHandler(self):
    #             event.accept()
    #         else:
    #             event.ignore()
    #     else:
    #         #I think there's a problem with two pipeline views and the same
    #         #scene on Macs. After assigning a new scene just before deleting
    #         #seems to solve the problem
    #         self.peTab.annotatedPipelineView.setScene(QtGui.QGraphicsScene())
    #         return QDockContainer.closeEvent(self, event)
    #         # super(QVistrailView, self).closeEvent(event)

    # def queryVistrail(self, on=True):
    #     """ queryVistrail(on: bool) -> None
    #     Inspecting the query tab to get a pipeline for querying
        
    #     """
    #     if on:
    #         queryPipeline = self.queryTab.controller.current_pipeline
    #         if queryPipeline:
    #             self.controller.query_by_example(queryPipeline)
    #             self.setQueryMode(True)
    #     else:
    #         self.controller.set_search(None)
    #         self.setQueryMode(False)

    # def createPopupMenu(self):
    #     """ createPopupMenu() -> QMenu
    #     Create a pop up menu that has a list of all tool windows of
    #     the current tab of the view. Tool windows can be toggled using
    #     this menu
        
    #     """
    #     return self.stackedWidget.currentWidget().createPopupMenu()

    # def executeParameterExploration(self):
    #     """ executeParameterExploration() -> None
    #     Execute the current parameter exploration in the exploration tab
        
    #     """
    #     self.peTab.performParameterExploration()

    # def versionSelected(self, versionId, byClick, doValidate=True, 
    #                     fromRoot=False):
    #     """ versionSelected(versionId: int, byClick: bool) -> None
    #     A version has been selected/unselected, update the controller
    #     and the pipeline view
        
    #     """
    #     if self.controller:
    #         if byClick:
    #             if self.controller.current_version > 0:
    #                 if self.controller.has_move_actions():
    #                     self.controller.flush_delayed_actions()
    #                     self.controller.invalidate_version_tree(False)
    #             self.controller.reset_pipeline_view = byClick
    #             self.controller.change_selected_version(versionId, True,
    #                                                     doValidate, fromRoot)
    #             versionId = self.controller.current_version
    #             self.controller.current_pipeline_view.fitToAllViews(True)
    #             self.redo_stack = []
    #         self.versionTab.versionProp.updateVersion(versionId)
    #         self.versionTab.versionView.versionProp.updateVersion(versionId)
    #         self.emit(QtCore.SIGNAL('versionSelectionChange'),versionId)
    #         self.execPipelineEnabled = versionId>-1
    #         self.execExploreEnabled = \
    #                     self.controller.vistrail.get_paramexp(versionId) != None
    #         self.execDiffEnabled = False
    #         self.execExploreChange = False
    #         self.emit(QtCore.SIGNAL('execStateChange()'))

    #         return versionId

    # def twoVersionsSelected(self, id1, id2):
    #     """ twoVersionsSelected(id1: Int, id2: Int) -> None
    #     Just echo the signal from the view
        
    #     """
    #     self.execDiffEnabled = True
    #     self.execDiffId1 = id1
    #     self.execDiffId2 = id2
    #     self.emit(QtCore.SIGNAL('execStateChange()'))

    # def queryPipelineChange(self, notEmpty):
    #     """ queryPipelineChange(notEmpty: bool) -> None
    #     Update the status of tool bar buttons if there are
    #     modules on the query canvas
        
    #     """
    #     self.execQueryEnabled = notEmpty
    #     self.emit(QtCore.SIGNAL('execStateChange()'))
                  
    # def exploreChange(self, notEmpty):
    #     """ exploreChange(notEmpty: bool) -> None
    #     Update the status of tool bar buttons if there are
    #     parameters in the exploration canvas
        
    #     """
    #     self.execExploreEnabled = notEmpty
    #     self.emit(QtCore.SIGNAL('execStateChange()'))
        
    # def checkModuleConfigPanel(self):
    #     """ checkModuleConfigPanel(self) -> None 
    #     This will ask if user wants to save changes """
    #     self.pipelineTab.checkModuleConfigPanel()
         
    # ##########################################################################
    # # Undo/redo
        
    # def set_pipeline_selection(self, old_action, new_action, optype):
    #     # need to check if anything on module changed or
    #     # any connections changed
    #     module_types = set(['module', 'group', 'abstraction'])
    #     module_child_types = set(['function', 'parameter', 'location', 
    #                               'portSpec', 'annotation'])
    #     conn_types = set(['connection'])
    #     conn_child_types = set(['port'])

    #     pipeline_scene = self.pipelineTab.pipelineView.scene()

    #     if old_action is None:
    #         old_action_id = 0
    #     else:
    #         old_action_id = old_action.id
    #     if new_action is None:
    #         new_action_id = 0
    #     else:
    #         new_action_id = new_action.id
    #     action = self.controller.vistrail.general_action_chain(old_action_id,
    #                                                            new_action_id)

    #     def module_change():
    #         module_ids = set()
    #         function_ids = set()
    #         for op in action.operations:
    #             if op.what in module_types and \
    #                     (op.vtType == 'change' or op.vtType == 'add'):
    #                 module_ids.add(op.objectId)
    #             elif op.what in module_child_types and \
    #                     (op.vtType == 'change' or op.vtType == 'add' or
    #                      op.vtType == 'delete'):
    #                 if op.what == 'parameter':
    #                     function_ids.add(op.parentObjId)
    #                 else:
    #                     module_ids.add(op.parentObjId)
    #         if len(function_ids) > 0:
    #             for m_id, module in \
    #                     self.controller.current_pipeline.modules.iteritems():
    #                 to_discard = set()
    #                 for f_id in function_ids:
    #                     if module.has_function_with_real_id(f_id):
    #                         module_ids.add(m_id)
    #                         to_discard.add(f_id)
    #                 function_ids -= to_discard

    #         for id in module_ids:
    #             if id in pipeline_scene.modules:
    #                 pipeline_scene.modules[id].setSelected(True)

    #     def connection_change():
    #         conn_ids = set()
    #         for op in action.operations:
    #             if op.what in conn_types and \
    #                     (op.vtType == 'change' or op.vtType == 'add'):
    #                 conn_ids.add(op.objectId)
    #             elif op.what in conn_child_types and \
    #                     (op.vtType == 'change' or op.vtType == 'add' or 
    #                      op.vtType == 'delete'):
    #                 conn_ids.add(op.parentObjId)
    #         for id in conn_ids:
    #             if id in pipeline_scene.connections:
    #                 pipeline_scene.connections[id].setSelected(True)
                    
    #     module_change()
    #     connection_change()
        
    # def undo(self):
    #     """Performs one undo step, moving up the version tree."""
    #     action_map = self.controller.vistrail.actionMap
    #     old_action = action_map.get(self.controller.current_version, None)
    #     self.redo_stack.append(self.controller.current_version)
    #     self.controller.show_parent_version()
    #     new_action = action_map.get(self.controller.current_version, None)
    #     self.set_pipeline_selection(old_action, new_action, 'undo')
    #     return self.controller.current_version
        
    # def redo(self):
    #     """Performs one redo step if possible, moving down the version tree."""
    #     action_map = self.controller.vistrail.actionMap
    #     old_action = action_map.get(self.controller.current_version, None)
    #     if not self.can_redo():
    #         critical("Redo on an empty redo stack. Ignoring.")
    #         return
    #     next_version = self.redo_stack[-1]
    #     self.redo_stack = self.redo_stack[:-1]
    #     self.controller.show_child_version(next_version)
    #     new_action = action_map[self.controller.current_version]
    #     self.set_pipeline_selection(old_action, new_action, 'redo')
    #     return next_version

    # def can_redo(self):
    #     return len(self.redo_stack) <> 0

    # def new_action(self, action):
    #     """new_action

    #     Handler for VistrailController.new_action

    #     """
    #     self.redo_stack = []

################################################################################

# FIXME: There is a bug on VisTrails that shows up if you load terminator.vt,
# open the image slices HW, undo about 300 times and then try to redo.
# This should be a test here, as soon as we have an api for that.

if __name__=="__main__":
    # Initialize the Vistrails Application and Theme
    import sys
    from gui import qt, theme
    app = qt.createBogusQtGuiApp(sys.argv)
    theme.initializeCurrentTheme()

    # Now visually test QPipelineView
    vv = QVistrailView(None)
    vv.show()    
    sys.exit(app.exec_())
