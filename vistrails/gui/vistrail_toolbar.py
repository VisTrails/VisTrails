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
""" This holds a customized toolbar class for QVistrailView

QVistrailViewPaddedTabBar
QVistrailViewTabBar
QVistrailViewToolBar
"""

from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme

################################################################################

class QVistrailViewToolBar(QtGui.QToolBar):
    """
    QVistrailViewToolBar is a special toolbar for vistrail view. It
    has a number of tool buttons, e.g. Execute, View Mode...., on the
    left and a tab bar on the right. The tab bar for now contains two
    tab to switch back and forth between pipeline view and version
    tree view in the tabbed mode
    
    """
    def __init__(self, view=None):
        """ QVistrailViewToolBar(view: QVistrailView) -> QVistrailViewToolBar
        Construct default buttons and tabbar for the toolbar
        """
        QtGui.QToolBar.__init__(self, view)
        self.setWindowTitle('Vistrail Controller')        

        # First, add all the tool buttons on the left
        self.addAction(self.executePipelineAction())
        self.addSeparator()
        self.addAction(self.visualQueryAction())
        self.addAction(self.viewFullTreeAction())
        self.addSeparator()
        self.addAction(self.pipViewAction())
        self.addSeparator()
        self.addAction(self.selectCursorAction())
        self.addAction(self.panCursorAction())
        self.addAction(self.zoomCursorAction())
        self.addSeparator()

        # Then take care of the tab bar on the right
        self.tabBar = QVistrailViewTabBar()
        self.paddedTabBar = QVistrailViewPaddedTabBar(self.tabBar, self)
        self.addWidget(self.paddedTabBar)

    def executePipelineAction(self):
        """ executePipelineAction() -> QAction        
        Returns the execute pipeline action that can be used in any
        menu or toolbar
        
        """
        if not hasattr(self, '_executePipelineAction'):
            self._executePipelineAction = QtGui.QAction(
                CurrentTheme.EXECUTE_PIPELINE_ICON,
                '&Execute',
                self)
            self._executePipelineAction.setToolTip('Execute the current '
                                                   'pipeline')
            self._executePipelineAction.setStatusTip(
                self._executePipelineAction.toolTip())
        return self._executePipelineAction

    def visualQueryAction(self):
        """ visualQueryAction() -> QAction        
        Returns the query vistrail action that can be used in any
        menu or toolbar
        
        """
        if not hasattr(self, '_visualQueryAction'):
            self._visualQueryAction = QtGui.QAction(
                CurrentTheme.VISUAL_QUERY_ICON,
                '&Query',
                self)
            self._visualQueryAction.setCheckable(True)
            self._visualQueryAction.setToolTip('Query vistrail by example')
            self._visualQueryAction.setStatusTip(
                self._visualQueryAction.toolTip())
        return self._visualQueryAction

    def viewFullTreeAction(self):
        """ viewFullTreeAction() -> QAction        
        View the full tree with all move actions
        
        """
        if not hasattr(self, '_viewFullTreeAction'):
            self._viewFullTreeAction = QtGui.QAction(
                CurrentTheme.VIEW_FULL_TREE_ICON,
                '&View Full Tree',
                self)
            self._viewFullTreeAction.setCheckable(True)
            self._viewFullTreeAction.setToolTip('View the whole version '
                                               'tree with all move actions')
            self._viewFullTreeAction.setStatusTip(
                self._viewFullTreeAction.toolTip())
        return self._viewFullTreeAction

    def cursorMenu(self):
        """ cursorMenu() -> None        
        A menu of different cursor shapes
        
        """
        if not hasattr(self, '_cursorMenu'):
            menu = QtGui.QMenu("Select an action for the cursor", self)
            menu.addAction(self.selectCursorAction())
            menu.addAction(self.panCursorAction())
            menu.addAction(self.zoomCursorAction())
            checkedAction = self.cursorActionGroup().checkedAction()
            self._cursorMenu = menu
            self.assignCursorMenuAction(checkedAction)
        return self._cursorMenu

    def assignCursorMenuAction(self, action):
        """ assignCursorMenuAction(action: QAction) -> None
        Assign one of the three cursor actions to be the default one
        
        """
        menu = self.cursorMenu()
        menu.setIcon(action.icon())
        menu.setTitle(action.toolTip())
        menu.menuAction().setStatusTip(action.statusTip())                

    def cursorActionGroup(self):
        """ cursorActionGroup() -> None        
        A group for all cursor actions in order to have only one
        selected at a time
        
        """
        if not hasattr(self, '_cursorActionGroup'):
            self._cursorActionGroup = QtGui.QActionGroup(self)
        return self._cursorActionGroup

    def selectCursorAction(self):
        """ selectCursorAction() -> QAction        
        Returns the action for using the cursor as a selection tool by
        default (an arrow shape)
        
        """
        if not hasattr(self, '_selectCursorAction'):
            self._selectCursorAction = QtGui.QAction(
                CurrentTheme.SELECT_ICON,
                'Select',
                self.cursorActionGroup())
            self._selectCursorAction.setCheckable(True)
            self._selectCursorAction.setToolTip('Selecting components '
                                                'inside the view ')
            self._selectCursorAction.setStatusTip(
                self._selectCursorAction.toolTip())
            self._selectCursorAction.setChecked(True)
            self.connect(self._selectCursorAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.cursorToggled)
        return self._selectCursorAction

    def panCursorAction(self):
        """ panCursorAction() -> QAction        
        Returns the action for using the cursor as a panning tool
        
        """
        if not hasattr(self, '_panCursorAction'):
            self._panCursorAction = QtGui.QAction(
                CurrentTheme.PAN_ICON,
                'Pan',
                self.cursorActionGroup())
            self._panCursorAction.setCheckable(True)
            self._panCursorAction.setToolTip('Pan the view (Shift+Click)')
            self._panCursorAction.setStatusTip(
                self._panCursorAction.toolTip())
            self.connect(self._panCursorAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.cursorToggled)
        return self._panCursorAction

    def zoomCursorAction(self):
        """ zoomCursorAction() -> QAction        
        Returns the action for using the cursor as a zooming tool
        
        """
        if not hasattr(self, '_zoomCursorAction'):
            self._zoomCursorAction = QtGui.QAction(
                CurrentTheme.ZOOM_ICON,
                'Zoom',
                self.cursorActionGroup())
            self._zoomCursorAction.setCheckable(True)
            self._zoomCursorAction.setToolTip('Zoom in/out the view '
                                              '(Meta[Shift+Alt]+Click)')
            self._zoomCursorAction.setStatusTip(
                self._zoomCursorAction.toolTip())
            self.connect(self._zoomCursorAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.cursorToggled)
        return self._zoomCursorAction

    def pipViewAction(self):
        """ pipViewAction() -> QAction        
        Returns the action for displaying a thumbnail of version tree
        view on the pipeline view and vice versa
        
        """
        if not hasattr(self, '_pipViewAction'):
            self._pipViewAction = QtGui.QAction('PIP', self)
            self._pipViewAction.setCheckable(True)
            self._pipViewAction.setToolTip('Picture-In-Picture')
            self._pipViewAction.setStatusTip(
                self._pipViewAction.toolTip())
        return self._pipViewAction

    def resizeEvent(self, event):
        """ resizeEvent(event: QResizeEvent) -> None        
        Make sure to update the tabbar shape when this toolbar is
        resized. Use Resize and Move Event to track down geometry
        change for detecting toolbar location
        
        """
        self.updateTabBarShape()
        return QtGui.QToolBar.resizeEvent(self, event)

    def moveEvent(self, event):
        """ moveEvent(event: QMoveEvent) -> None        
        Make sure to update the tabbar shape when this toolbar is
        moved. Use Resize and Move Event to track down geometry
        change for detecting toolbar location
        
        """
        self.updateTabBarShape()
        return QtGui.QToolBar.moveEvent(self, event)

    def updateTabBarShape(self):
        """ updateTabBarShape() -> None        
        Update self.tabBar to have an appropriate shape depending on
        the current location of this toolbar
        
        """
        if self.parent()!=None:
            tabBarShapeMap = {
                QtCore.Qt.NoToolBarArea: QtGui.QTabBar.RoundedNorth,
                QtCore.Qt.LeftToolBarArea: QtGui.QTabBar.RoundedWest,
                QtCore.Qt.RightToolBarArea: QtGui.QTabBar.RoundedEast,
                QtCore.Qt.TopToolBarArea: QtGui.QTabBar.RoundedNorth,
                QtCore.Qt.BottomToolBarArea: QtGui.QTabBar.RoundedSouth
                }
            area = self.parent().toolBarArea(self)
            self.tabBar.setShape(tabBarShapeMap[area])
            self.paddedTabBar.updateSizePolicy()

    def cursorToggled(self, checked=True):
        """ cursorToggled(checked: bool) -> None        
        Slot to handle cursor actions toggled. This will in turn emit
        another signal to specify cursor has been selected
        
        """
        cursorMode = -1
        action = None
        if self.selectCursorAction().isChecked():
            cursorMode = 0
            action = self.selectCursorAction()
        elif self.panCursorAction().isChecked():
            cursorMode = 1
            action = self.panCursorAction()
        elif self.zoomCursorAction().isChecked():
            cursorMode = 2
            action = self.zoomCursorAction()
        if action:
            self.assignCursorMenuAction(action)
        self.emit(QtCore.SIGNAL('cursorChanged(int)'), cursorMode)

class QVistrailViewPaddedTabBar(QtGui.QWidget):
    """
    QVistrailViewPaddedTabBar is a special class containing
    QVistrailViewTabBar in the center and has 4 padded widget on the
    side to help put QVistrailViewTabBar to the right position
    
    """
    def __init__(self, tabBar, parent=None):
        """ QVistrailViewPaddedTabBar(parent: QWidget,
                                      tabBar: QVistrailViewTabBar)
                                      -> QVistrailViewPaddedTabBar
        Construct a grid layout with 4 padded widget
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.north = QtGui.QWidget()  
        self.south = QtGui.QWidget()
        self.west = QtGui.QWidget()
        self.east = QtGui.QWidget()
        self.central = tabBar
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.addWidget(self.north, 0, 0, 1, 3)
        self.gridLayout.addWidget(self.west, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.central, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.east, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.south, 2, 0, 1, 3)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setMargin(0)
        self.setLayout(self.gridLayout)
        self.updateSizePolicy()

    def updateSizePolicy(self):
        """ updateSizePolicy() -> None        
        Based on the tabbar shape, update the 4 padded widgets size
        policy to fit the tabbar
        
        """
        if self.central.shape() in [QtGui.QTabBar.RoundedSouth,
                                    QtGui.QTabBar.TriangularSouth]:
            self.north.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
            self.south.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Expanding)
            self.east.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Ignored)
            self.west.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
        elif self.central.shape() in [QtGui.QTabBar.RoundedNorth,
                                    QtGui.QTabBar.TriangularNorth]:
            self.north.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Expanding)
            self.south.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
            self.east.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Ignored)
            self.west.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
        elif self.central.shape() in [QtGui.QTabBar.RoundedWest,
                                    QtGui.QTabBar.TriangularWest]:
            self.north.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Expanding)
            self.south.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
            self.east.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
            self.west.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Ignored)
        elif self.central.shape() in [QtGui.QTabBar.RoundedEast,
                                    QtGui.QTabBar.TriangularEast]:
            self.north.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Expanding)
            self.south.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
            self.east.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Ignored)
            self.west.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                     QtGui.QSizePolicy.Ignored)
        else:
            print 'Unknown QTabBar shape!'

class QVistrailViewTabBar(QtGui.QTabBar):
    """
    QVistrailTabBar is special tabbar staying, by default, at the
    bottom right corner of the vistrail view
    
    """
    def __init__(self, parent=None):
        """ QVistrailViewTabBar(parent: QWidget) -> QVistrailViewTabBar
        By default create a tabbar facing up with two tabs
        
        """
        QtGui.QTabBar.__init__(self, parent)
        self.setShape(QtGui.QTabBar.RoundedSouth)
        self.addTab('Pipeline')
        self.addTab('Version Tree')
        self.addTab('Query')
#        self.addTab('Parameter Exploration (In Progress)')
        self.invisible = False
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                           QtGui.QSizePolicy.Maximum)
        self.setCurrentIndex(1)
