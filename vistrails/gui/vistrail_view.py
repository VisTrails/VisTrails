""" The file describes a container widget consisting of a pipeline
view and a version tree for each opened Vistrail """

from PyQt4 import QtCore, QtGui
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.pipeline_tab import QPipelineTab
from gui.version_tab import QVersionTab
from gui.vistrail_controller import VistrailController
from gui.vistrail_toolbar import QVistrailViewToolBar
import os.path

################################################################################

class QVistrailView(QDockContainer):
    """
    QVistrailView is a widget containing two tabs: Pipeline View and
    Version Tree View for manipulating VisTrails
    
    """
    def __init__(self, parent=None):
        """ QVistrailItem(parent: QWidget) -> QVistrailItem
        Make it a main window with dockable area
        
        """
        QDockContainer.__init__(self, parent)
        
        # The window title is the name of the vistrail file
        self.setWindowTitle('Untitle.xml')

        # Create the views
        self.pipelineTab = QPipelineTab()
        self.versionTab = QVersionTab()

        self.pipelineTab.pipelineView.setPIPScene(
            self.versionTab.versionView.scene())
        self.versionTab.versionView.setPIPScene(
            self.pipelineTab.pipelineView.scene())

        # Setup a central stacked widget for pipeline view and version
        # tree view in tabbed mode
        self.stackedWidget = QtGui.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.stackedWidget.addWidget(self.pipelineTab)
        self.stackedWidget.addWidget(self.versionTab)
        self.stackedWidget.setCurrentIndex(1)

        # Add the customized toolbar at the bottom
        self.toolBar = QVistrailViewToolBar(self)
        self.connect(self.toolBar, QtCore.SIGNAL('viewChanged(int)'),
                     self.viewChanged)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        self.toolBar)

        # Initialize the vistrail controller
        self.controller = VistrailController()
        self.connect(self.controller,
                     QtCore.SIGNAL('stateChanged'),
                     self.stateChanged)

        # Make sure we can change view when requested
        self.connect(self.toolBar.tabBar,
                     QtCore.SIGNAL('currentChanged(int)'),
                     self.tabChanged)

        # Capture PIP state changed
        self.connect(self.toolBar.pipViewAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.pipChanged)

        # Send to spreadsheet action
        self.connect(self.toolBar.executePipelineAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.controller.sendToSpreadsheet)

        # Space-storage for the builder window
        self.savedToolBarArea = None
        self.viewAction = None
        self.closeEventHandler = None
        
    def viewChanged(self, viewMode):
        """ viewChanged(viewId: int) -> None        
        When the view mode changed to viewId, make sure to layout the
        pipeline tabs and version tree view accordingly
        
        """
        tabs = [self.pipelineTab, self.versionTab]
        if viewMode!=0:
            self.stackedWidget.hide()
        for tabOrder in range(len(tabs)):
            tab = tabs[tabOrder]
            
            if viewMode==3:
                tab.toolWindow().setFeatures(
                    QtGui.QDockWidget.DockWidgetFloatable |
                    QtGui.QDockWidget.DockWidgetMovable)
            else:
                tab.toolWindow().setFeatures(
                    QtGui.QDockWidget.NoDockWidgetFeatures)

            # Tabbed view
            if viewMode==0:
                if self.stackedWidget.indexOf(tab)==-1:
                    self.removeDockWidget(tab.toolWindow())
                self.stackedWidget.insertWidget(tabOrder,tab)
            # Horizontal view
            elif viewMode in [1,3]:
                if self.stackedWidget.indexOf(tab)!=-1:
                    self.stackedWidget.removeWidget(tab)
                tab.toolWindow().setParent(self)
                tab.show()
                tab.toolWindow().show()
                self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                                   tab.toolWindow())
            # Vertical view
            elif viewMode==2:
                if self.stackedWidget.indexOf(tab)!=-1:
                    self.stackedWidget.removeWidget(tab)
                tab.toolWindow().setParent(self)
                tab.show()
                tab.toolWindow().show()
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                                   tab.toolWindow())
        if viewMode==0:
            self.stackedWidget.setCurrentIndex(1)
            self.stackedWidget.show()

        # Somehow we have to re-add all dock widgets to get an even
        # width/height
        for tab in tabs:
            if viewMode in [1,3]:
                self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                                   tab.toolWindow())
            elif viewMode==2:
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                                   tab.toolWindow())

    def tabChanged(self, index):
        """ tabChanged(index: int) -> None        
        Slot for switching different views when the tab's current
        widget is changed
        
        """
        if self.stackedWidget.count()>index:
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

    def setVistrail(self, vistrail, name=''):
        """ setVistrail(vistrail: Vistrail) -> None
        Assign a vistrail to this view, and start interacting with it
        
        """
        self.vistrail = vistrail
        self.controller.setVistrail(vistrail, name)
        self.versionTab.setController(self.controller)
        self.pipelineTab.setController(self.controller)

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
            return QDockContainer.closeEvent(self, event)

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
