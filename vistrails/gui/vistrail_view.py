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
from core.debug import critical
from gui.common_widgets import QDockContainer
from gui.paramexplore.pe_tab import QParameterExplorationTab
from gui.pipeline_tab import QPipelineTab
from gui.query_tab import QQueryTab
from gui.version_tab import QVersionTab
from gui.vistrail_controller import VistrailController
from core.system import vistrails_default_file_type
################################################################################

class QVistrailView(QDockContainer):
    """
    QVistrailView is a widget containing four stacked widgets: Pipeline View,
    Version Tree View, Query View and Parameter Exploration view
    for manipulating vistrails.
    """
    def __init__(self, parent=None):
        """ QVistrailItem(parent: QWidget) -> QVistrailItem
        Make it a main window with dockable area
        
        """
        QDockContainer.__init__(self, parent)
        
        # The window title is the name of the vistrail file
        self.setWindowTitle('untitled%s'%vistrails_default_file_type())

        # Create the views
        self.pipelineTab = QPipelineTab()
        self.versionTab = QVersionTab()
        self.connect(self.versionTab.versionProp,
                     QtCore.SIGNAL('textQueryChange(bool)'),
                     self.setQueryMode)

        self.pipelineTab.pipelineView.setPIPScene(
            self.versionTab.versionView.scene())
        self.versionTab.versionView.setPIPScene(            
            self.pipelineTab.pipelineView.scene())
        self.versionTab.versionView.scene()._pipeline_scene = self.pipelineTab.pipelineView.scene()
        self.queryTab = QQueryTab()

        self.peTab = QParameterExplorationTab()
        self.peTab.annotatedPipelineView.setScene(
            self.pipelineTab.pipelineView.scene())
        
        # Setup a central stacked widget for pipeline view and version
        # tree view
        self.stackedWidget = QtGui.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.stackedWidget.addWidget(self.pipelineTab)
        self.stackedWidget.addWidget(self.versionTab)
        self.stackedWidget.addWidget(self.queryTab)
        self.stackedWidget.addWidget(self.peTab)
        self.stackedWidget.setCurrentIndex(1)

        # Initialize the vistrail controller
        self.controller = VistrailController()
        self.controller.vistrail_view = self
        self.connect(self.controller,
                     QtCore.SIGNAL('stateChanged'),
                     self.stateChanged)
        self.connect(self.controller,
                     QtCore.SIGNAL('new_action'),
                     self.new_action)

        # self.versionTab.versionView.scene()._vistrail_view = self
        self.connect(self.versionTab.versionView.scene(),
                     QtCore.SIGNAL('versionSelected(int,bool,bool,bool)'),
                     self.versionSelected,
                     QtCore.Qt.QueuedConnection)

        self.connect(self.versionTab,
                     QtCore.SIGNAL('twoVersionsSelected(int,int)'),
                     self.twoVersionsSelected)
        self.connect(self.queryTab,
                     QtCore.SIGNAL('queryPipelineChange'),
                     self.queryPipelineChange)
        self.connect(self.peTab,
                     QtCore.SIGNAL('exploreChange(bool)'),
                     self.exploreChange)

        # We also keep track where this vistrail comes from
        # So we can save in the right place
        self.locator = None
        
        self.closeEventHandler = None

        # the redo stack stores the undone action ids 
        # (undo is automatic with us, through the version tree)
        self.redo_stack = []

        # Keep the state of the execution button and menu items for the view
        self.execQueryEnabled = False
        self.execDiffEnabled = False
        self.execExploreEnabled = False
        self.execPipelineEnabled = False
        self.execDiffId1 = -1
        self.execDiffId2 = -1

    def updateCursorState(self, mode):
        """ updateCursorState(mode: Int) -> None 
        Change cursor state in all different modes.

        """
        self.pipelineTab.pipelineView.setDefaultCursorState(mode)
        self.versionTab.versionView.setDefaultCursorState(mode)
        self.queryTab.pipelineView.setDefaultCursorState(mode)
        if self.parent().parent().parent().pipViewAction.isChecked():
            self.pipelineTab.pipelineView.pipFrame.graphicsView.setDefaultCursorState(mode)
            self.versionTab.versionView.pipFrame.graphicsView.setDefaultCursorState(mode)


    def flush_changes(self):
        """Flush changes in the vistrail before closing or saving.
        """
        # Quick workaround for notes focus out bug (ticket #182)
        # There's probably a much better way to fix this.
        prop = self.versionTab.versionProp
        prop.versionNotes.commit_changes()

    def setup_view(self, version=None):
        """setup_view(version = None:int) -> None

        Sets up the correct view for a fresh vistrail.

        Previously, there was a method setInitialView and another
        setOpenView.

        They were supposed to do different things but the code was
        essentially identical.

        FIXME: this means that the different calls are being handled
        somewhere else in the code. Figure this out."""

        if version is None:
            self.controller.select_latest_version()
            version = self.controller.current_version
        else:
            self.versionSelected(version, True, True, False)
        self.controller.recompute_terse_graph()
        self.controller.invalidate_version_tree(True)
        self.setPIPMode(True)
        self.setQueryMode(False)
       
    def setPIPMode(self, on):
        """ setPIPMode(on: bool) -> None
        Set the PIP state for the view

        """
        self.pipelineTab.pipelineView.setPIPEnabled(on)
        self.versionTab.versionView.setPIPEnabled(on)

    def setQueryMode(self, on):
        """ setQueryMode(on: bool) -> None
        Set the Reset Query button mode for the view
        
        """
        self.pipelineTab.pipelineView.setQueryEnabled(on)
        self.versionTab.versionView.setQueryEnabled(on)
        self.queryTab.pipelineView.setQueryEnabled(on)

    def setMethodsMode(self, on):
        """ setMethodsMode(on: bool) -> None
        Set the methods panel state for the view

        """
        if on:
            self.pipelineTab.methodPalette.toolWindow().show()
        else:
            self.pipelineTab.methodPalette.toolWindow().hide()

    def setSetMethodsMode(self, on):
        """ setSetMethodsMode(on: bool) -> None
        Set the set methods panel state for the view

        """
        if on:
            self.pipelineTab.moduleMethods.toolWindow().show()
        else:
            self.pipelineTab.moduleMethods.toolWindow().hide()

    def setPropertiesMode(self, on):
        """ setPropertiesMode(on: bool) -> None
        Set the properties panel state for the view

        """
        if on:
            self.versionTab.versionProp.toolWindow().show()
        else:
            self.versionTab.versionProp.toolWindow().hide()

    def setPropertiesOverlayMode(self, on):
        """ setPropertiesMode(on: bool) -> None
        Set the properties overlay state for the view

        """
        if on:
            self.versionTab.versionView.versionProp.show()
        else:
            self.versionTab.versionView.versionProp.hide()
            
    def setModuleConfigMode(self, on):
        """ setModuleConfigMode(on: bool) -> None
        Set the Module configuration panel state for the view

        """
        if on:
            self.pipelineTab.moduleConfig.toolWindow().show()
        else:
            self.pipelineTab.moduleConfig.toolWindow().hide()
            
    def setVistrailVarsMode(self, on):
        """ setVistrailVarsMode(on: bool) -> None
        Set the vistrail variable panel state for the view

        """
        if on:
            self.pipelineTab.vistrailVars.toolWindow().show()
        else:
            self.pipelineTab.vistrailVars.toolWindow().hide()

    def viewModeChanged(self, index):
        """ viewModeChanged(index: int) -> None        
        Slot for switching different views when the tab's current
        widget is changed
        
        """
        if self.stackedWidget.count()>index:
            self.stackedWidget.setCurrentIndex(index)

    def pasteToCurrentTab(self):
        index = self.stackedWidget.currentIndex()
        if index == 0:
            self.pipelineTab.pipelineView.pasteFromClipboard()
        elif index == 2:
            self.queryTab.pipelineView.pasteFromClipboard()
            
    def selectAll(self):
        index = self.stackedWidget.currentIndex()
        if index == 0:
            self.pipelineTab.pipelineView.scene().selectAll()    
        elif index == 2:
            self.queryTab.pipelineView.scene().selectAll()
            
    def sizeHint(self):
        """ sizeHint(self) -> QSize
        Return recommended size of the widget
        
        """
        return QtCore.QSize(1024, 768)

    def set_vistrail(self, vistrail, locator=None, abstractions=None, 
                     thumbnails=None):
        """ set_vistrail(vistrail: Vistrail, locator: BaseLocator) -> None
        Assign a vistrail to this view, and start interacting with it
        
        """
        self.vistrail = vistrail
        self.locator = locator
        self.controller.set_vistrail(vistrail, locator, abstractions, thumbnails)
        self.versionTab.setController(self.controller)
        self.pipelineTab.setController(self.controller)
        self.peTab.setController(self.controller)

    def stateChanged(self):
        """ stateChanged() -> None

        Handles 'stateChanged' signal from VistrailController
        
        Update the window and tab title
        
        """
        title = self.controller.name
        if title=='':
            title = 'untitled%s'%vistrails_default_file_type()
        if self.controller.changed:
            title += '*'
        self.setWindowTitle(title)
        # propagate the state change to the version prop
        # maybe in the future we should propagate as a signal
        versionId = self.controller.current_version
        self.versionTab.versionProp.updateVersion(versionId)

    def emitDockBackSignal(self):
        """ emitDockBackSignal() -> None
        Emit a signal for the View Manager to take this widget back
        
        """
        self.emit(QtCore.SIGNAL('dockBack'), self)

    def closeEvent(self, event):
        """ closeEvent(event: QCloseEvent) -> None
        Only close if we save information
        
        """
        if self.closeEventHandler:
            if self.closeEventHandler(self):
                event.accept()
            else:
                event.ignore()
        else:
            #I think there's a problem with two pipeline views and the same
            #scene on Macs. After assigning a new scene just before deleting
            #seems to solve the problem
            self.peTab.annotatedPipelineView.setScene(QtGui.QGraphicsScene())
            return QDockContainer.closeEvent(self, event)
            # super(QVistrailView, self).closeEvent(event)

    def queryVistrail(self, on=True):
        """ queryVistrail(on: bool) -> None
        Inspecting the query tab to get a pipeline for querying
        
        """
        if on:
            queryPipeline = self.queryTab.controller.current_pipeline
            if queryPipeline:
                self.controller.query_by_example(queryPipeline)
                self.setQueryMode(True)
        else:
            self.controller.set_search(None)
            self.setQueryMode(False)

    def createPopupMenu(self):
        """ createPopupMenu() -> QMenu
        Create a pop up menu that has a list of all tool windows of
        the current tab of the view. Tool windows can be toggled using
        this menu
        
        """
        return self.stackedWidget.currentWidget().createPopupMenu()

    def executeParameterExploration(self):
        """ executeParameterExploration() -> None
        Execute the current parameter exploration in the exploration tab
        
        """
        self.peTab.performParameterExploration()

    def versionSelected(self, versionId, byClick, doValidate=True, 
                        fromRoot=False):
        """ versionSelected(versionId: int, byClick: bool) -> None
        A version has been selected/unselected, update the controller
        and the pipeline view
        
        """
        if self.controller:
            if byClick:
                if self.controller.current_version > 0:
                    if self.controller.has_move_actions():
                        self.controller.flush_delayed_actions()
                        self.controller.invalidate_version_tree(False)
                self.controller.reset_pipeline_view = byClick
                self.controller.change_selected_version(versionId, True,
                                                        doValidate, fromRoot)
                versionId = self.controller.current_version
                self.controller.current_pipeline_view.fitToAllViews(True)
                self.redo_stack = []
            self.versionTab.versionProp.updateVersion(versionId)
            self.versionTab.versionView.versionProp.updateVersion(versionId)
            self.emit(QtCore.SIGNAL('versionSelectionChange'),versionId)
            self.execPipelineEnabled = versionId>-1
            self.execExploreEnabled = \
                        self.controller.vistrail.get_paramexp(versionId) != None
            self.execDiffEnabled = False
            self.execExploreChange = False
            self.emit(QtCore.SIGNAL('execStateChange()'))

            return versionId

    def twoVersionsSelected(self, id1, id2):
        """ twoVersionsSelected(id1: Int, id2: Int) -> None
        Just echo the signal from the view
        
        """
        self.execDiffEnabled = True
        self.execDiffId1 = id1
        self.execDiffId2 = id2
        self.emit(QtCore.SIGNAL('execStateChange()'))

    def queryPipelineChange(self, notEmpty):
        """ queryPipelineChange(notEmpty: bool) -> None
        Update the status of tool bar buttons if there are
        modules on the query canvas
        
        """
        self.execQueryEnabled = notEmpty
        self.emit(QtCore.SIGNAL('execStateChange()'))
                  
    def exploreChange(self, notEmpty):
        """ exploreChange(notEmpty: bool) -> None
        Update the status of tool bar buttons if there are
        parameters in the exploration canvas
        
        """
        self.execExploreEnabled = notEmpty
        self.emit(QtCore.SIGNAL('execStateChange()'))
        
    def checkModuleConfigPanel(self):
        """ checkModuleConfigPanel(self) -> None 
        This will ask if user wants to save changes """
        self.pipelineTab.checkModuleConfigPanel()
         
    ##########################################################################
    # Undo/redo
        
    def set_pipeline_selection(self, old_action, new_action, optype):
        # need to check if anything on module changed or
        # any connections changed
        module_types = set(['module', 'group', 'abstraction'])
        module_child_types = set(['function', 'parameter', 'location', 
                                  'portSpec', 'annotation'])
        conn_types = set(['connection'])
        conn_child_types = set(['port'])

        pipeline_scene = self.pipelineTab.pipelineView.scene()

        if old_action is None:
            old_action_id = 0
        else:
            old_action_id = old_action.id
        if new_action is None:
            new_action_id = 0
        else:
            new_action_id = new_action.id
        action = self.controller.vistrail.general_action_chain(old_action_id,
                                                               new_action_id)

        def module_change():
            module_ids = set()
            function_ids = set()
            for op in action.operations:
                if op.what in module_types and \
                        (op.vtType == 'change' or op.vtType == 'add'):
                    module_ids.add(op.objectId)
                elif op.what in module_child_types and \
                        (op.vtType == 'change' or op.vtType == 'add' or
                         op.vtType == 'delete'):
                    if op.what == 'parameter':
                        function_ids.add(op.parentObjId)
                    else:
                        module_ids.add(op.parentObjId)
            if len(function_ids) > 0:
                for m_id, module in \
                        self.controller.current_pipeline.modules.iteritems():
                    to_discard = set()
                    for f_id in function_ids:
                        if module.has_function_with_real_id(f_id):
                            module_ids.add(m_id)
                            to_discard.add(f_id)
                    function_ids -= to_discard

            for id in module_ids:
                if id in pipeline_scene.modules:
                    pipeline_scene.modules[id].setSelected(True)

        def connection_change():
            conn_ids = set()
            for op in action.operations:
                if op.what in conn_types and \
                        (op.vtType == 'change' or op.vtType == 'add'):
                    conn_ids.add(op.objectId)
                elif op.what in conn_child_types and \
                        (op.vtType == 'change' or op.vtType == 'add' or 
                         op.vtType == 'delete'):
                    conn_ids.add(op.parentObjId)
            for id in conn_ids:
                if id in pipeline_scene.connections:
                    pipeline_scene.connections[id].setSelected(True)
                    
        module_change()
        connection_change()
        
    def undo(self):
        """Performs one undo step, moving up the version tree."""
        action_map = self.controller.vistrail.actionMap
        old_action = action_map.get(self.controller.current_version, None)
        self.redo_stack.append(self.controller.current_version)
        self.controller.show_parent_version()
        new_action = action_map.get(self.controller.current_version, None)
        self.set_pipeline_selection(old_action, new_action, 'undo')
        return self.controller.current_version
        
    def redo(self):
        """Performs one redo step if possible, moving down the version tree."""
        action_map = self.controller.vistrail.actionMap
        old_action = action_map.get(self.controller.current_version, None)
        if not self.can_redo():
            critical("Redo on an empty redo stack. Ignoring.")
            return
        next_version = self.redo_stack[-1]
        self.redo_stack = self.redo_stack[:-1]
        self.controller.show_child_version(next_version)
        new_action = action_map[self.controller.current_version]
        self.set_pipeline_selection(old_action, new_action, 'redo')
        return next_version

    def can_redo(self):
        return len(self.redo_stack) <> 0

    def new_action(self, action):
        """new_action

        Handler for VistrailController.new_action

        """
        self.redo_stack = []

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
