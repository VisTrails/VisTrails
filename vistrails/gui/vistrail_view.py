############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

import os.path
from PyQt4 import QtCore, QtGui
from core.debug import critical
from core.utils import VistrailLocator
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.pe_tab import QParameterExplorationTab
from gui.pipeline_tab import QPipelineTab
from gui.query_tab import QQueryTab
from gui.version_tab import QVersionTab
from gui.vistrail_controller import VistrailController
from gui.vistrail_toolbar import QVistrailViewToolBar


################################################################################

class QVistrailView(QDockContainer):
    """
    QVistrailView is a widget containing four tabs: Pipeline View,
    Version Tree View, Query View and Parameter Exploration view
    for manipulating vistrails.
    """
    def __init__(self, parent=None):
        """ QVistrailItem(parent: QWidget) -> QVistrailItem
        Make it a main window with dockable area
        
        """
        QDockContainer.__init__(self, parent)
        
        # The window title is the name of the vistrail file
        self.setWindowTitle('Untitled.xml')

        # Create the views
        self.pipelineTab = QPipelineTab()
        self.versionTab = QVersionTab()

        self.pipelineTab.pipelineView.setPIPScene(
            self.versionTab.versionView.scene())
        self.versionTab.versionView.setPIPScene(            
            self.pipelineTab.pipelineView.scene())

        self.queryTab = QQueryTab()

        self.peTab = QParameterExplorationTab()
        self.peTab.annotatedPipelineView.setScene(
            self.pipelineTab.pipelineView.scene())
        
        # Setup a central stacked widget for pipeline view and version
        # tree view in tabbed mode
        self.stackedWidget = QtGui.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.stackedWidget.addWidget(self.pipelineTab)
        self.stackedWidget.addWidget(self.versionTab)
        self.stackedWidget.addWidget(self.queryTab)
        self.stackedWidget.addWidget(self.peTab)
        self.stackedWidget.setCurrentIndex(1)

        #Keeping track of previous active tab to update menus accordingly
        self.activeIndex = 1
        
        # Add the customized toolbar at the top
        self.toolBar = QVistrailViewToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea,
                        self.toolBar)

        # Initialize the vistrail controller
        self.controller = VistrailController()
        self.controller.vistrailView = self
        self.connect(self.controller,
                     QtCore.SIGNAL('stateChanged'),
                     self.stateChanged)

        # We also keep track where this vistrail comes from
        # So we can save in the right place
        self.locator = VistrailLocator()
        
        # Make sure we can change view when requested
        self.connect(self.toolBar.tabBar,
                     QtCore.SIGNAL('currentChanged(int)'),
                     self.tabChanged)

        # Capture PIP state changed
        self.connect(self.toolBar.pipViewAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.pipChanged)

        # Execute pipeline action
        self.connect(self.toolBar.executePipelineAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.executeCurrentWorkflow)

        # Undo action
        self.connect(self.toolBar.undoAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.undo)

        # Redo action
        self.connect(self.toolBar.redoAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.redo)

        # Query pipeline action
        self.connect(self.toolBar.visualQueryAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.queryVistrail)

        # View full version tree
        self.connect(self.toolBar.viewFullTreeAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.controller.setFullTree)

        #Toolbar buttons state
        self.connect(self.versionTab,
                     QtCore.SIGNAL('versionSelectionChange'),
                     self.versionSelectionChange)
        self.connect(self.queryTab,
                     QtCore.SIGNAL('queryPipelineChange'),
                     self.queryPipelineChange)

        # Space-storage for the builder window
        self.savedToolBarArea = None
        self.viewAction = None
        self.closeEventHandler = None

        # PIP enabled by default.
        self.toolBar.pipViewAction().trigger()

        # Make sure to connect all graphics view to cursor mode of the
        # toolbar
        pipelineView = self.pipelineTab.pipelineView
        versionView = self.versionTab.versionView
        self.connect(self.toolBar, QtCore.SIGNAL('cursorChanged(int)'),
                     pipelineView.setDefaultCursorState)
        self.connect(self.toolBar, QtCore.SIGNAL('cursorChanged(int)'),
                     versionView.setDefaultCursorState)
        self.connect(self.toolBar, QtCore.SIGNAL('cursorChanged(int)'),
                     self.queryTab.pipelineView.setDefaultCursorState)
        if self.toolBar.pipViewAction().isChecked():
            pipelinePIPView = pipelineView.pipFrame.graphicsView
            self.connect(self.toolBar, QtCore.SIGNAL('cursorChanged(int)'),
                         pipelinePIPView.setDefaultCursorState)
            versionPIPView = versionView.pipFrame.graphicsView
            self.connect(self.toolBar, QtCore.SIGNAL('cursorChanged(int)'),
                         versionPIPView.setDefaultCursorState)

        # the redo stack stores the undone action ids 
        # (undo is automatic with us, through the version tree)
        self.redo_stack = []


    def changeView(self, viewIndex):
        """changeView(viewIndex) -> None. Changes the view between
        pipeline, version and query."""
        self.toolBar.tabBar.setCurrentIndex(viewIndex)

    def updateViewMenu(self, viewIndex = None):
        """updateViewMenu(viewIndex: int) -> None
        Update the Builder View Menu to be consistent with the current tab
        being shown.
        
        """
        if viewIndex == None:
            viewIndex = self.toolBar.tabBar.currentIndex()
        builderMenu = self.parent().parent().parent().viewMenu
        if self.activeIndex == 0: #pipelineTab
            self.pipelineTab.removeViewActionsFromMenu(builderMenu)
        elif self.activeIndex == 1: #versionTab
            self.versionTab.removeViewActionsFromMenu(builderMenu)
        elif self.activeIndex == 2: #queryTab
            self.queryTab.removeViewActionsFromMenu(builderMenu)
        elif self.activeIndex == 3: #peTab
            self.peTab.removeViewActionsFromMenu(builderMenu)
        currentTab = None
        if viewIndex == 0:
            currentTab = self.pipelineTab
        elif viewIndex == 1:
            currentTab = self.versionTab
        elif viewIndex == 2:
            currentTab = self.queryTab
        elif viewIndex == 3:
            currentTab = self.peTab
            
        if currentTab:
            currentTab.addViewActionsToMenu(builderMenu)

        self.activeIndex = viewIndex
        
    def setInitialView(self):
        """setInitialView(): sets up the correct initial view for a
        new vistrail, that is, select empty version and focus on pipeline view."""
        self.controller.changeSelectedVersion(0)
        self.changeView(0)
        
    def tabChanged(self, index):
        """ tabChanged(index: int) -> None        
        Slot for switching different views when the tab's current
        widget is changed
        
        """
        if self.stackedWidget.count()>index:
            self.updateViewMenu(index)
            self.stackedWidget.setCurrentIndex(index)

    def pipChanged(self, checked=True):
        """ pipChanged(checked: bool) -> None        
        Slot for switching PIP mode on/off
        
        """
        self.pipelineTab.pipelineView.setPIPEnabled(checked)
        self.versionTab.versionView.setPIPEnabled(checked)

    def sizeHint(self):
        """ sizeHint(self) -> QSize
        Return recommended size of the widget
        
        """
        return QtCore.QSize(1024, 768)

    def setVistrail(self, vistrail, locator=None):
        """ setVistrail(vistrail: Vistrail, locator: VistrailLocator) -> None
        Assign a vistrail to this view, and start interacting with it
        
        """
        self.vistrail = vistrail
        self.locator = locator
        self.controller.setVistrail(vistrail, locator)
        self.versionTab.setController(self.controller)
        self.pipelineTab.setController(self.controller)
        self.peTab.setController(self.controller)

    def stateChanged(self):
        """ stateChanged() -> None
        Need to update the window and tab title
        
        """
        title = self.controller.name
        if title=='':
            title = 'Untitled.xml'
        if self.controller.changed:
            title += '*'
        self.setWindowTitle(title)
        self.redo_stack = []

    def versionSelectionChange(self, versionId):
        """ versionSelectionChange(versionId: int) -> None
        Update the status of tool bar buttons if there is a version selected
        
        """
        self.toolBar.executePipelineAction().setEnabled(versionId>-1)
        self.toolBar.undoAction().setEnabled(versionId>0)
        self.toolBar.redoAction().setEnabled(self.can_redo())

    def queryPipelineChange(self, notEmpty):
        """ versionSelectionChange(notEmpty: bool) -> None
        Update the status of tool bar buttons if there are
        modules on the query canvas
        
        """
#        if not notEmpty and self.toolBar.visualQueryAction().isChecked():
#            self.toolBar.visualQueryAction().trigger()
        self.toolBar.visualQueryAction().setChecked(False)
        self.toolBar.visualQueryAction().setEnabled(notEmpty)

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

    def queryVistrail(self, checked=True):
        """ queryVistrail(checked: bool) -> None
        Inspecting the query tab to get a pipeline for querying
        
        """
        if checked:
            queryPipeline = self.queryTab.controller.currentPipeline
            if queryPipeline:
                self.controller.queryByExample(queryPipeline)
        else:
            self.controller.setSearch(None)

    def executeCurrentWorkflow(self):
        """ executeCurrentWorkflow() -> None
        Make sure to get focus for QModuleMethods to update
        
        """
        self.setFocus(QtCore.Qt.MouseFocusReason)
        self.controller.executeCurrentWorkflow()

    def createPopupMenu(self):
        """ createPopupMenu() -> QMenu
        Create a pop up menu that has a list of all tool windows of
        the current tab of the view. Tool windows can be toggled using
        this menu
        
        """
        return self.stackedWidget.currentWidget().createPopupMenu()

    ##########################################################################
    # Undo/redo

    def undo(self):
        """Performs one undo step, moving up the version tree."""
        self.redo_stack.append(self.controller.currentVersion) 
        self.controller.showPreviousVersion()
        return self.controller.currentVersion

    def redo(self):
        """Performs one redo step if possible, moving down the version tree."""
        if not self.can_redo():
            critical("Redo on an empty redo stack. Ignoring.")
            return
        next_version = self.redo_stack[-1]
        self.redo_stack = self.redo_stack[:-1]
        self.controller.changeSelectedVersion(next_version)
        self.controller.resetVersionView = False
        self.controller.invalidate_version_tree()
        self.controller.resetVersionView = True
        return next_version

    def can_redo(self):
        return len(self.redo_stack) <> 0

################################################################################

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
