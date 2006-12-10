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
#        self.addAction(self.tabbedViewAction())
#        self.addAction(self.horizontalViewAction())
#        self.addAction(self.verticalViewAction())
#        self.addAction(self.dockViewAction())
        self.addSeparator()
        self.addAction(self.pipViewAction())
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

    def viewActionGroup(self):
        """ viewActionGroup() -> None        
        A group for all view actions in order to have only one
        selected at a time
        
        """
        if not hasattr(self, '_viewActionGroup'):
            self._viewActionGroup = QtGui.QActionGroup(self)
        return self._viewActionGroup

    def tabbedViewAction(self):
        """ tabbedViewAction() -> QAction        
        Returns the action for laying pipeline and version views in
        tabbed layout
        
        """
        if not hasattr(self, '_tabbedViewAction'):
            self._tabbedViewAction = QtGui.QAction(
                CurrentTheme.TABBED_VIEW_ICON,
                'Tabbed View',
                self.viewActionGroup())
            self._tabbedViewAction.setCheckable(True)
            self._tabbedViewAction.setToolTip('Layout the views in '
                                              'tabbed mode')
            self._tabbedViewAction.setStatusTip(
                self._tabbedViewAction.toolTip())
            self._tabbedViewAction.setChecked(True)
            self.connect(self._tabbedViewAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.viewToggled)
        return self._tabbedViewAction

    def horizontalViewAction(self):
        """ horizontalViewAction() -> QAction        
        Returns the action for laying pipeline and version views side
        by side horizontally
        
        """
        if not hasattr(self, '_horizontalViewAction'):
            self._horizontalViewAction = QtGui.QAction(
                CurrentTheme.HORIZONTAL_VIEW_ICON,
                'Horizontal View',
                self.viewActionGroup())
            self._horizontalViewAction.setCheckable(True)
            self._horizontalViewAction.setToolTip('Layout the views side-'
                                                  'by-side horizontally')
            self._horizontalViewAction.setStatusTip(
                self._horizontalViewAction.toolTip())
            self.connect(self._horizontalViewAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.viewToggled)
        return self._horizontalViewAction

    def verticalViewAction(self):
        """ verticalViewAction() -> QAction        
        Returns the action for laying pipeline and version views side
        by side vertically
        
        """
        if not hasattr(self, '_verticalViewAction'):
            self._verticalViewAction = QtGui.QAction(
                CurrentTheme.VERTICAL_VIEW_ICON,
                'Vertical View',
                self.viewActionGroup())
            self._verticalViewAction.setCheckable(True)
            self._verticalViewAction.setToolTip('Layout the views side-'
                                                  'by-side vertically')
            self._verticalViewAction.setStatusTip(
                self._verticalViewAction.toolTip())
            self.connect(self._verticalViewAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.viewToggled)
        return self._verticalViewAction

    def dockViewAction(self):
        """ dockViewAction() -> QAction        
        Returns the action for laying pipeline and version views side
        by side horizontally but all views can be dockable
        
        """
        if not hasattr(self, '_dockViewAction'):
            self._dockViewAction = QtGui.QAction(
                CurrentTheme.DOCK_VIEW_ICON,
                'Docking View',
                self.viewActionGroup())
            self._dockViewAction.setCheckable(True)
            self._dockViewAction.setToolTip('Allow all the views to be '
                                            'dock widgets')
            self._dockViewAction.setStatusTip(
                self._dockViewAction.toolTip())
            self.connect(self._dockViewAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.viewToggled)
        return self._dockViewAction

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

    def viewToggled(self, checked=True):
        """ viewToggled(checked: bool) -> None        
        Slot to handle view actions toggled. This will in turn emit
        another signal to specify which view
        
        """
        viewMode = -1
        if self.tabbedViewAction().isChecked():
            viewMode = 0
            self.tabBar.setCurrentIndex(1)
            self.tabBar.show()
        elif self.horizontalViewAction().isChecked():
            viewMode = 1
            self.tabBar.hide()
        elif self.verticalViewAction().isChecked():
            viewMode = 2
            self.tabBar.hide()
        elif self.dockViewAction().isChecked():
            viewMode = 3
            self.tabBar.hide()
        self.emit(QtCore.SIGNAL('viewChanged(int)'), viewMode)

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
        self.invisible = False
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                QtGui.QSizePolicy.Maximum)
        self.setCurrentIndex(1)
