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
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.pe_tab import QParameterExplorationTab
from gui.pipeline_tab import QPipelineTab
from gui.query_tab import QQueryTab
from gui.version_tab import QVersionTab
from gui.vistrail_controller import VistrailController


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
        self.controller.vistrailView = self
        self.connect(self.controller,
                     QtCore.SIGNAL('stateChanged'),
                     self.stateChanged)

        # We also keep track where this vistrail comes from
        # So we can save in the right place
        self.locator = None
        
        self.closeEventHandler = None

        # the redo stack stores the undone action ids 
        # (undo is automatic with us, through the version tree)
        self.redo_stack = []

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


    def setInitialView(self):
        """setInitialView() -> None
        Sets up the correct initial view for a new vistrail, that is, 
        select empty version and focus on pipeline view.
        
        """
        self.controller.changeSelectedVersion(0)
        self.setPIPMode(True)

    def setOpenView(self):
        """setOpenView() -> None
        Sets up the correct view for an opened
        vistrail, that is, select latest version and focus on version view.
        
        """
        self.controller.selectLatestVersion()
        self.setPIPMode(True)
       
    def setPIPMode(self, on):
        """ setPIPMode(on: bool) -> None
        Set the PIP state for the view

        """
        self.pipelineTab.pipelineView.setPIPEnabled(on)
        self.versionTab.versionView.setPIPEnabled(on)

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

    def viewModeChanged(self, index):
        """ viewModeChanged(index: int) -> None        
        Slot for switching different views when the tab's current
        widget is changed
        
        """
        if self.stackedWidget.count()>index:
            self.stackedWidget.setCurrentIndex(index)

    def sizeHint(self):
        """ sizeHint(self) -> QSize
        Return recommended size of the widget
        
        """
        return QtCore.QSize(1024, 768)

    def setVistrail(self, vistrail, locator=None):
        """ setVistrail(vistrail: Vistrail, locator: BaseLocator) -> None
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
