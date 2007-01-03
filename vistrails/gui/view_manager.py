""" This holds a customized QTabWidget for controlling different
vistrail views and tools

QViewManager
"""

from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from gui.view_tabbar import QInteractiveTabBar
from gui.vistrail_view import QVistrailView
from core.xml_parser import XMLParser
from core import system
from core.vistrail import Vistrail

################################################################################

class QViewManager(QtGui.QTabWidget):
    """
    QViewManger is a tabbed widget to containing multiple Vistrail
    views. It takes care of emiting useful signals to the builder
    window
    
    """
    def __init__(self, parent=None):
        """ QViewManager(view: QVistrailView) -> QViewManager
        Create an empty tab widget
        
        """
        QtGui.QTabWidget.__init__(self, parent)
        self.setTabBar(QInteractiveTabBar(self))
        self.closeButton = QtGui.QToolButton(self)
        self.closeButton.setIcon(CurrentTheme.VIEW_MANAGER_CLOSE_ICON)
        self.closeButton.setAutoRaise(True)
        self.setCornerWidget(self.closeButton)
        self.sdiMode = False
        self.splittedViews = {}

        self.connect(self, QtCore.SIGNAL('currentChanged(int)'),
                     self.currentChanged)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self.closeVistrail)
        
        self.connect(self.tabBar(),
                     QtCore.SIGNAL('tabMoveRequest(int,int)'),
                     self.moveTab)

        self.connect(self.tabBar(),
                     QtCore.SIGNAL('tabSplitRequest(int,QPoint)'),
                     self.splitTab)

    def addVistrailView(self, view):
        """ addVistrailView(view: QVistrailView) -> None
        Add a vistrail view to the tab, and connect to the right signals
        
        """
        if self.indexOf(view)!=-1:
            return
        if self.sdiMode:
            view.savedToolBarArea = view.toolBarArea(view.toolBar)
            view.removeToolBar(view.toolBar)
        self.addTab(view, view.windowTitle())
        view.installEventFilter(self)
        self.connect(view.pipelineTab,
                     QtCore.SIGNAL('moduleSelectionChange'),
                     self.moduleSelectionChange)
        self.emit(QtCore.SIGNAL('vistrailViewAdded'), view)
        if self.count()==1:
            self.emit(QtCore.SIGNAL('currentChanged(int)'), 0)

    def removeVistrailView(self, view):
        """ removeVistrailView(view: QVistrailView) -> None
        Remove the current vistrail view and destroy it
        
        """
        if view:
            view.removeEventFilter(self)
            self.disconnect(view.pipelineTab,
                            QtCore.SIGNAL('moduleSelectionChange'),
                            self.moduleSelectionChange)
            self.emit(QtCore.SIGNAL('vistrailViewRemoved'), view)
            if self.indexOf(view)!=-1:
                self.removeTab(self.currentIndex())
            elif self.splittedViews.has_key(view):
                del self.splittedViews[view]
            view.close()

    def moduleSelectionChange(self, selection):
        """ moduleSelectionChange(selection: list[id]) -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('moduleSelectionChange'), selection)

    def copySelection(self):
        """ copySelection() -> None
        Copy the current selected pipeline modules
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().copySelection()

    def pasteToCurrentPipeline(self):
        """ pasteToCurrentPipeline() -> None
        Paste what is on the clipboard to the current pipeline
        
        """        
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().pasteFromClipboard()

    def newVistrail(self):
        """ newVistrail() -> None
        Create a new vistrail with no name
        
        """
        vistrailView = QVistrailView()
        vistrailView.setVistrail(Vistrail())
        self.addVistrailView(vistrailView)
        self.setCurrentWidget(vistrailView)

    def openVistrail(self, fileName):
        """ openVistrail(fileName) -> QVistrailView
        Open a new vistrail and return a QVistrailView        
        
        """        
        parser = XMLParser()
        parser.openVistrail(fileName)
        vistrail = parser.getVistrail()
        vistrailView = QVistrailView()
        vistrailView.setVistrail(vistrail, fileName)
        self.addVistrailView(vistrailView)
        self.setCurrentWidget(vistrailView)
        return vistrailView

    def saveVistrail(self, vistrailView=None, fileName=''):
        """ openVistrail(vistrailView: QVistrailView) -> QVistrailView
        Save the current active vistrail to a file
        
        """
        if not vistrailView:
            vistrailView = self.currentWidget()
        if vistrailView:
            if fileName=='':
                fileName = vistrailView.controller.fileName
            if fileName=='':
                fileName = QtGui.QFileDialog.getSaveFileName(
                    self,
                    "Save Vistrail",
                    system.vistrailsDirectory(),
                    "XML files (*.xml)")
            if fileName!='' and fileName!=None:
                vistrailView.controller.writeVistrail(str(fileName))
                
    def closeVistrail(self, vistrailView=None, quiet=False):
        """ closeVistrail(vistrailView: QVistrailView, quiet: bool) -> bool
        Close the current active vistrail
        
        """
        if not vistrailView:
            vistrailView = self.currentWidget()
        if vistrailView:
            if not quiet and vistrailView.controller.changed:
                text = vistrailView.controller.name
                if text=='':
                    text = 'Untitled.xml'
                text = ('Vistrail ' +
                        QtCore.Qt.escape(text) +
                        ' contains unsaved changes.\n Do you want to '
                        'save changes before closing it?')
                res = QtGui.QMessageBox.information(None,
                                                    'Vistrails',
                                                    text, 
                                                    '&Save', 
                                                    '&Discard',
                                                    'Cancel',
                                                    0,
                                                    2)
            else:
                res = 1
            if res == 0:
                self.saveVistrail(vistrailView)
            elif res == 2:
                return False
            self.removeVistrailView(vistrailView)
        return True
    
    def closeAllVistrails(self):
        """ closeAllVistrails() -> bool        
        Attemps to close every single vistrail, return True if
        everything is closed correctly
        
        """
        for view in self.splittedViews.keys():
            if not self.closeVistrail(view):
                return False
        while self.count()>0:
            if not self.closeVistrail():
                return False
        return True

    def currentChanged(self, index):
        """ currentChanged(index: int):        
        Emit signal saying a different vistrail has been chosen to the
        builder
        
        """
        self.emit(QtCore.SIGNAL('currentVistrailChanged'),
                  self.currentWidget())

    def eventFilter(self, object, event):
        """ eventFilter(object: QVistrailView, event: QEvent) -> None
        Filter the window title change event for the view widget
        
        """
        if event.type()==QtCore.QEvent.WindowTitleChange:
            if object==self.currentWidget():
                self.setTabText(self.currentIndex(), object.windowTitle())
                self.currentChanged(self.currentIndex())
        return QtGui.QTabWidget.eventFilter(self, object, event)

    def getCurrentVistrailFileName(self):
        """ getCurrentVistrailFileName() -> str        
        Return the filename of the current vistrail or None if it
        doesn't have one
        
        """        
        vistrailView = self.currentWidget()
        if vistrailView and vistrailView.controller.name!='':
            return vistrailView.controller.name
        else:
            return None

    def switchToSDIMode(self):
        """ switchToSDIMode() -> None        
        Detach the toolbars of all view widgets
        
        """
        self.sdiMode = True
        self.tabBar().hide()
        for viewIndex in range(self.count()):            
            vistrailView = self.widget(viewIndex)
            vistrailView.savedToolBarArea = vistrailView.toolBarArea(
                vistrailView.toolBar)
            vistrailView.removeToolBar(vistrailView.toolBar)

    def switchToTabMode(self):
        """ switchToTabMode() -> None        
        Attach back all the toolbars of all view widgets
        
        """
        self.sdiMode = False
        self.tabBar().show()
        for viewIndex in range(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.addToolBar(vistrailView.savedToolBarArea,
                                    vistrailView.toolBar)
            vistrailView.toolBar.show()

    def getCurrentToolBar(self):
        """ getCurrentToolBar() -> QToolBar
        Return the toolbar of the current toolbar
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            return vistrailView.toolBar
        return None

    def moveTab(self, oldIndex, newIndex):
        """ moveTab(oldIndex: int, newIndex: int) -> None
        Move a tab from index oldIndex to newIndex
        
        """
        self.setUpdatesEnabled(False)
        widget = self.widget(oldIndex)
        label = self.tabText(oldIndex)
        self.removeTab(oldIndex)
        self.insertTab(newIndex, widget, label)
        self.setCurrentIndex(newIndex)
        self.setUpdatesEnabled(True)        
        
    def splitTab(self, index, pos):
        """ moveTab(index: int, pos: QPoint) -> None
        Move a tab out of the tabwidget to become a tool window
        
        """
        widget = self.widget(index)
        label = self.tabText(index)
        self.removeTab(index)
        dockBackAction = QtGui.QAction(CurrentTheme.DOCK_BACK_ICON,
                                       'Merge to VisTrails Builder',
                                       self)
        dockBackAction.setToolTip('Bring this window back to the '
                                  'VisTrails Builder')
        self.connect(dockBackAction, QtCore.SIGNAL('triggered()'),
                     widget.emitDockBackSignal)
        
        self.splittedViews[widget] = dockBackAction

        widget.closeEventHandler = self.closeVistrail
        widget.toolBar.addAction(dockBackAction)
        widget.setParent(None)
        widget.move(pos)
        widget.show()

        self.connect(widget, QtCore.SIGNAL('dockBack'),
                     self.mergeTab)

    def mergeTab(self, view):
        """ mergeTab(view: QVistrailView) -> None
        Merge the view from a top-level into a tab
        
        """
        self.disconnect(view, QtCore.SIGNAL('dockBack'),
                        self.mergeTab)
        dockBackAction = self.splittedViews[view]
        self.disconnect(dockBackAction, QtCore.SIGNAL('triggered()'),
                        view.emitDockBackSignal)
        view.toolBar.removeAction(dockBackAction)
        del self.splittedViews[view]
        view.closeEventHandler = None
        self.addTab(view, view.windowTitle())
        self.setCurrentWidget(view)        
