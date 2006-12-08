""" The file describes the pipeline tab widget to manage a single
vistrail version tree"""

from PyQt4 import QtCore, QtGui
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.version_prop import QVersionProp
from gui.version_search import QVersionSearch
from gui.version_view import QVersionTreeView

################################################################################
        
class QVersionTab(QDockContainer, QToolWindowInterface):
    """
    QVersionTab is a tab widget setting QVersionTreeView in a
    center while having surrounding tool windows
    
    """
    def __init__(self, parent=None):
        """ QVersionTab(parent: QWidget) -> QVersionTab        
        Make it a main window with dockable area and a
        QVersionTreeView in the middle
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Version Tree')
        self.versionView = QVersionTreeView()
        self.setCentralWidget(self.versionView)
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()

        self.versionSearch = QVersionSearch(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.versionSearch.toolWindow())        
        self.versionProp = QVersionProp(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.versionProp.toolWindow())        
        
        self.controller = None
        self.connect(self.toolWindow(),
                     QtCore.SIGNAL('topLevelChanged(bool)'),
                     self.updateWindowTitle)
        self.connect(self.versionView.scene(),
                     QtCore.SIGNAL('versionSelected(int,bool)'),
                     self.versionSelected)

    def updateWindowTitle(self, topLevel):
        """ updateWindowTitle(topLevel: bool) -> None
        Change the current widget title depends on the top level status
        
        """
        if topLevel:
            self.setWindowTitle('Version Tree <' +
                                self.toolWindow().parent().windowTitle()+'>')
        else:
            self.setWindowTitle('Pipeline')

    def versionSelected(self, versionId, byClick):
        """ versionSelected(versionId: int, byClick: bool) -> None
        A version has been selected/unselected, update the controller
        and the pipeline view
        
        """
        if self.controller:
            self.controller.resetPipelineView = byClick
            self.controller.changeSelectedVersion(versionId)
            self.versionProp.updateVersion(versionId)

    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a vistrail controller to this version tree view
        
        """
        oldController = self.versionView.scene().controller
        if oldController!=controller:
            if oldController!=None:
                self.disconnect(oldController,
                                QtCore.SIGNAL('vistrailChanged()'),
                                self.vistrailChanged)
            self.controller = controller
            self.versionView.scene().controller = controller
            self.connect(controller,
                         QtCore.SIGNAL('vistrailChanged()'),
                         self.vistrailChanged)
            if controller:
                self.vistrailChanged()
                self.versionProp.updateController(controller)
                self.versionSearch.controller = controller

    def vistrailChanged(self):
        """ vistrailChanged() -> None        
        Update the version tree when the vistrail of the controller
        has changed
        
        """
        self.versionView.scene().setupScene(self.controller)
        if self.controller and self.controller.resetVersionView:
            self.versionView.scene().fitToAllViews()
