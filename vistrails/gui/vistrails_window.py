############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

from gui.pipeline_view import QPipelineView
from gui.version_view import QVersionTreeView
from gui.query_view import QQueryView
from gui.vis_diff import QDiffView
from gui.paramexplore.param_view import QParameterView
from gui.vistrail_controller import VistrailController

class QVistrailsWindow(QtGui.QMainWindow):
    def __init__(self, vistrail, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)

        self.controller = None
        # have a toolbar
        self.toolbar = QtGui.QToolBar(self)
        history_action = QtGui.QAction("History", self)
        history_action.method = self.history_selected
        history_action.un_method = self.history_unselected
        query_action = QtGui.QAction("Search", self)
        query_action.method = self.query_selected
        query_action.un_method = self.query_unselected
        explore_action = QtGui.QAction("Explore", self)
        explore_action.method = self.explore_selected
        explore_action.un_method = self.explore_unselected
        toolbar_actions = [history_action, query_action, explore_action]
        self.action_group = QtGui.QActionGroup(self)
        for action in toolbar_actions:
            action.setCheckable(True)
            self.action_group.addAction(action)
        self.connect(self.action_group, QtCore.SIGNAL("triggered(QAction *)"), 
                     self.action_triggered)
        self.toolbar.addAction(history_action)
        self.toolbar.addAction(query_action)
        self.toolbar.addAction(explore_action)
        self.addToolBar(self.toolbar)
        self.selected_mode = None

    
        # default view is pipeline, but can have history, query, and 
        # param_exp views
        # self.version_view = QVersionTreeView(self)
        # self.query_view = QQueryView(self)
        # self.param_view = QParameterView(self)
        widget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.tabs = QtGui.QTabBar(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        layout.addWidget(self.tabs)
        self.stack = QtGui.QStackedWidget(self)
        layout.addWidget(self.stack)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.tab_to_stack_idx = {}
        self.tab_state = {}

        self.version_view = self.create_version_view()
        self.query_view = self.create_query_view()
        pipeline_view = self.create_pipeline_view()
        pipeline_view_2 = self.create_pipeline_view()
        pipeline_view_3 = self.create_pipeline_view()
        # version_view.current_pipeline_view = pipeline_view.scene()

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus(QtCore.Qt.OtherFocusReason)

        print "setting controller to:", id(pipeline_view.scene())
        self.controller = VistrailController(vistrail)
        pipeline_view.set_controller(self.controller)
        pipeline_view.set_to_current()
        self.set_controller(self.controller)

        # self.controller.current_pipeline_view = pipeline_view.scene()
        # self.tabs.setCurrentIndex(0)
        self.connect(self.tabs, QtCore.SIGNAL("currentChanged(int)"),
                     self.view_changed)
        self.connect(self.tabs, QtCore.SIGNAL("tabCloseRequested(int)"),
                     self.remove_view_by_index)
        self.tabs.setCurrentIndex(0)
        self.view_changed(0)

    def action_triggered(self, action):
        if self.selected_mode is not None:
            self.selected_mode.un_method()
        if self.selected_mode != action:
            self.selected_mode = action
            action.method()
        elif self.selected_mode is not None:
            self.selected_mode = None
            action.setChecked(False)
        self.tab_state[self.tabs.currentIndex()] = self.selected_mode

    def history_selected(self):
        print "VERSION"
        # idx = self.stack.addWidget(self.version_view)
        self.stack.setCurrentIndex(self.stack.indexOf(self.version_view))
        self.tabs.setTabText(self.tabs.currentIndex(), "History")

    def history_unselected(self):
        print "VERSION UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(), 
                             self.stack.currentWidget().get_title())

    def query_selected(self):
        print "QUERY"
        self.stack.setCurrentIndex(self.stack.indexOf(self.query_view))
        self.tabs.setTabText(self.tabs.currentIndex(), "Search")
        pass

    def explore_selected(self):
        print "EXPLORE"
        pass

    def query_unselected(self):
        print "QUERY UN"
        self.stack.setCurrentIndex(
            self.tab_to_stack_idx[self.tabs.currentIndex()])
        self.tabs.setTabText(self.tabs.currentIndex(), 
                             self.stack.currentWidget().get_title())

    def explore_unselected(self):
        print "EXPLORE UN"
        pass
    
    def sizeHint(self):
        return QtCore.QSize(1024, 768)

    def set_controller(self, controller):
        self.controller = controller
        self.controller.vistrail_view = self
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            if hasattr(view, 'set_controller'):
                view.set_controller(controller)

    def get_controller(self):
        return self.controller

    def set_title(self, title):
        self.setWindowTitle(title)
        
    def create_pipeline_view(self):
        view = self.create_view(QPipelineView)
        self.connect(view.scene(), QtCore.SIGNAL('moduleSelected'), 
                     self.gen_module_selected(view))
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
        return view

    def gen_module_selected(self, view):
        def module_selected(module_id, selection = []):
            from gui.vistrails_app import _app
            pipeline = view.scene().current_pipeline
            if module_id in pipeline.modules:
                module = pipeline.modules[module_id]
                _app.notify('module_changed', module)
        return module_selected
                 
    def version_selected(self, version_id, by_click, do_validate=True,
                         from_root=False, double_click=False):
        from gui.vistrails_app import _app
        print 'got version selected:', version_id
        self.controller.change_selected_version(version_id, by_click, 
                                                do_validate, from_root)
        _app.notify("version_changed", version_id)
        if by_click:
            view = self.stack.widget(
                self.tab_to_stack_idx[self.tabs.currentIndex()])
            view.scene().fitToView(view, True)
        if double_click:
            # view = self.create_pipeline_view()
            # view.set_controller(self.controller)
            # view.set_to_current()
            # self.tabs.setCurrentWidget(view.parent())
            self.action_triggered(self.selected_mode)

    def diff_requested(self, version_a, version_b):
        view = self.create_diff_view()
        self.switch_to_tab(-1)
        view.set_diff(self.controller.vistrail.get_pipeline_diff(version_a,
                                                                 version_b))
        
    def reset_version_view(self):
        self.version_view.scene().setupScene(self.controller)

    def create_view(self, klass, add_tab=True):
        view = klass(self)
        idx = self.stack.addWidget(view)
        view.set_index(idx)
        if add_tab:
            tab_idx = self.tabs.addTab(view.get_title())
            view.set_tab_idx(tab_idx)
            self.tab_to_stack_idx[tab_idx] = idx
        return view

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
        self.view_changed(index)

    def view_changed(self, index):
        print 'raw view_changed', index
        if index < 0 or self.controller is None:
            return
    
        self.stack.setCurrentIndex(self.tab_to_stack_idx[index])
        view = self.stack.currentWidget()

        print "PIPELINE_VIEW NEW SCENE:", id(view.scene())
        if isinstance(view, QPipelineView):
            from gui.vistrails_app import _app

            # need to set the controller's version, pipeline, view
            # to this view...
            # self.controller.current_version = view.current_version
            # self.controller.current_pipeline = view.current_pipeline
            view.set_to_current()
            print "view changed!", self.controller, \
                self.controller.current_version
            _app.notify("controller_changed", self.controller)
            self.reset_version_view()

        for action in self.action_group.actions():
            action.setChecked(False)
        self.selected_mode = None
        if index in self.tab_state:
            action = self.tab_state[index]
            if action is not None:
                action.setChecked(True)
            self.action_triggered(action)


    # def focusInEvent(self, event):
    #     print 'got focusInEvent', event, event.reason()
    #     self.emit(QtCore.SIGNAL("focus(QWidget*)"), self)
