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

""" File for Interacting with Bookmarks, a more user-friendly way of 
using Vistrails

QMedleyWindow

"""
import sys
from PyQt4 import QtCore, QtGui
from ...gui.theme import CurrentTheme
#from bookmark_panel import BookmarkPanel
#from component_panel import MedleyComponentPanel
#from medley_explore import MedleyExplorationPanel
    
################################################################################

class MedleyWindow(QtGui.QMainWindow):
    """
    QMedleyWindow is a main widget containing several tool windows
    for interacting with workflow views without having to use 
    the builder.
    It is based on QBuilderWindow visual style.
        
    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ __init__(manager: MedleyManager, parent: QWidget, f: WindowFlags)
                                                                 -> MedleyWindow
        Construct a window with menus, toolbar, and floating toolwindow
        
        """
        QtGui.QMainWindow.__init__(self, parent, f)
        
        self.setWindowTitle('Workflow Medleys')
        self.setStatusBar(QtGui.QStatusBar(self))
        self.setDockNestingEnabled(True)

#        self.viewManager = QMedleyViewManager(self)
#        self.setCentralWidget(self.viewManager)
        
        # self.bookmarkPanel = BookmarkPanel(self, MedleyManager)
#         self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
#                            self.bookmarkPanel.toolWindow())

#         self.componentPanel = QMedleyComponentPanel(self,MedleyManager)
#         self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
#                            self.componentPanel.toolWindow())

#        self.setStatusBar(QtGui.QStatusBar(self))
#        self.setupMenu()
#        self.createToolBar()

#        self.connectSignals()
        self.setVisible(False)
   
    def sizeHint(self):
        """ sizeHint() -> QRect
        Return the recommended size of the bookmarks window
        
        """
        return QtCore.QSize(800, 600)
                
    def setupMenu(self):
        """ setupMenu() -> None
        Add all available actions to the menu bar
        
        """
        self.setMenuBar(QtGui.QMenuBar(self))
        self.medleyMenu = self.menuBar().addMenu('&Medley')
        self.medleyMenu.addAction(self.openMedleyAction())
        self.medleyMenu.addAction(self.saveMedleyAction())
        self.medleyMenu.addAction(self.exportMedleyAction())

        # TODO: Add bookmark menu
        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(
            self.bookmarkPanel.toolWindow().toggleViewAction())
        self.viewMenu.addAction(
            self.componentPanel.toolWindow().toggleViewAction())
        
    def createToolBar(self):
        """ createToolBar() -> None
        Create a default toolbar for bookmarks window
        
        """
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setWindowTitle('Workflow Medleys')
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolBar.addAction(self.executeAction())
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.canvasViewAction())
        self.toolBar.addAction(self.exploreViewAction())
        self.toolBar.addSeparator()
        self.addToolBar(self.toolBar)

    def executeAction(self):
        """ executeAction() -> QAction        
        Returns the execute pipeline action that can be used in any
        menu or toolbar
        
        """
        if not hasattr(self, '_executeAction'):
            self._executeAction = QtGui.QAction(
                CurrentTheme.EXECUTE_PIPELINE_ICON,
                '&Execute',
                self)
            self._executeAction.setToolTip('Execute the current '
                                           'medley')
            self._executeAction.setStatusTip(
                self._executeAction.toolTip())
            self._executeAction.setEnabled(False)
        return self._executeAction

    def canvasViewAction(self):
        """ canvasViewAction() -> QAction
         Returns the action for using the canvas view
        
        """
        if not hasattr(self, '_canvasViewAction'):
            self._canvasViewAction = QtGui.QAction(
                CurrentTheme.PIPELINE_ICON,
                'Medley Canvas',
                self.viewActionGroup())
            self._canvasViewAction.setCheckable(True)
            self._canvasViewAction.setToolTip('Edit the medley')
            self._canvasViewAction.setStatusTip(
                self._canvasViewAction.toolTip())
            self.connect(self._canvasViewAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.viewChanged)
        return self._canvasViewAction

    def exploreViewAction(self):
        """ exploreViewAction() -> QAction
         Returns the action for using the explore view
        
        """
        if not hasattr(self, '_exploreViewAction'):
            self._exploreViewAction = QtGui.QAction(
                CurrentTheme.EXPLORE_ICON,
                'Exploration',
                self.viewActionGroup())
            self._exploreViewAction.setCheckable(True)
            self._exploreViewAction.setToolTip('Edit a parameter exploration')
            self._exploreViewAction.setStatusTip(
                self._exploreViewAction.toolTip())
            self.connect(self._exploreViewAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.viewChanged)
        return self._exploreViewAction
    
    def viewActionGroup(self):
        """ viewActionGroup() -> None        
        A group for all view actions in order to have only one
        selected at a time
        
        """
        if not hasattr(self, '_viewActionGroup'):
            self._viewActionGroup = QtGui.QActionGroup(self)
        return self._viewActionGroup

    def changeView(self, viewIndex):
        """ changeView(viewIndex: int) -> None
        Change the active view action
        
        """
        if viewIndex == 0:
            self.pipelineViewAction().setChecked(True)
        else:
            self.exploreViewAction().setChecked(True)
        self.viewChanged()

    def viewChanged(self, checked=True):
        """ viewChanged(checked: bool) -> None
        The view has changed, emit a signal

        """
        if self.pipelineViewAction().isChecked():
            self.currentViewIndex = 0
        else:
            self.currentViewIndex = 1

        self.changeExecuteButtonState(self.currentViewIndex)
        self.emit(QtCore.SIGNAL('viewModeChanged(int)'), 
                  self.currentViewIndex)
        
    def closeEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the window is about to close."""
        self.hide()
        self.emit(QtCore.SIGNAL("bookmarksHidden()"))
            
    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between various GUI components        
        
        """
        self.connect(MedleyManager, 
                     QtCore.SIGNAL("updateAliasGUI"),
                     self.bookmarkAliasPanel.updateAliasTable)
        self.connect(MedleyManager, 
                     QtCore.SIGNAL("updateBookmarksGUI"),
                     self.bookmarkPanel.updateBookmarkPalette)

    def changeExecuteButtonState(self, index):
        """ changeExecuteButtonState(index: int) -> None
        Change icon, tooltip, and enabled state for different view modes

        """
        if index == 1: # parameter explore
            self.executeAction().setIcon(
                CurrentTheme.EXECUTE_EXPLORE_ICON)
            self.executeAction().setToolTip('Execute the parameter'
                                            'exploration on current medley')
        else:
            self.executeAction().setIcon(
                CurrentTheme.EXECUTE_PIPELINE_ICON)
            self.executeAction().setToolTip('Execute the current '
                                            'medley')
