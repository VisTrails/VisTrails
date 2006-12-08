""" File for the builder window, the workspace of Vistrails

QBuilderWindow
"""

from PyQt4 import QtCore, QtGui
from gui.module_palette import QModulePalette
from gui.shell import QShellDialog
from gui.theme import CurrentTheme
from gui.view_manager import QViewManager
from core import system

################################################################################

class QBuilderWindow(QtGui.QMainWindow):
    """
    QBuilderWindow is a main widget containing an editin area for
    Vistrails and several tool windows. Also remarks that almost all
    of QBuilderWindow components are floating dockwidget. This mimics
    a setup of an IDE
    
    """
    def __init__(self, parent=None):
        """ QBuilderWindow(parent: QWidget) -> QBuilderWindow
        Construct the main window with menus, toolbar, and floating toolwindow
        
        """
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('VisTrails Builder')
        self.setStatusBar(QtGui.QStatusBar(self))
        self.setDockNestingEnabled(True)
        
        self.viewManager = QViewManager()
        self.setCentralWidget(self.viewManager)

        self.modulePalette = QModulePalette(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.modulePalette.toolWindow())
        
        self.createActions()
        self.createMenu()
        self.createToolBar()

        self.connectSignals()

        self.shell = None
        self.vistrailViewToolBar = None
        self.viewManager.newVistrail()

    def sizeHint(self):
        """ sizeHint() -> QRect
        Return the recommended size of the builder window
        
        """
        return QtCore.QSize(1280, 768)

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None
        Close the whole application when the builder is closed
        
        """
        if not self.quitVistrails():
            e.ignore()

    def createActions(self):
        """ createActions() -> None
        Construct all menu/toolbar actions for builder window
        
        """
        self.newVistrailAction = QtGui.QAction(CurrentTheme.NEW_VISTRAIL_ICON,
                                               '&New', self)
        self.newVistrailAction.setShortcut('Ctrl+N')
        self.newVistrailAction.setStatusTip('Create a new Vistrail')

        self.openVistrailAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_ICON,
                                                '&Open...', self)
        self.openVistrailAction.setShortcut('Ctrl+O')
        self.openVistrailAction.setStatusTip('Open an existing VisTrail')

        self.saveVistrailAction = QtGui.QAction(CurrentTheme.SAVE_VISTRAIL_ICON,
                                                '&Save', self)
        self.saveVistrailAction.setShortcut('Ctrl+S')
        self.saveVistrailAction.setStatusTip('Save the current VisTrail')

        self.saveVistrailAsAction = QtGui.QAction('Save &as...', self)
        self.saveVistrailAsAction.setShortcut('Ctrl+Shift+S')
        self.saveVistrailAction.setStatusTip('Save the current VisTrail at '
                                             'a different location')

        self.closeVistrailAction = QtGui.QAction('Close', self)
        self.closeVistrailAction.setShortcut('Ctrl+W')
        self.closeVistrailAction.setStatusTip('Close the current VisTrail')

        self.quitVistrailsAction = QtGui.QAction('Quit', self)
        self.quitVistrailsAction.setShortcut('Ctrl+Q')
        self.quitVistrailsAction.setStatusTip('Exit Vistrails')
       
        self.copyAction = QtGui.QAction('Copy', self)
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.setEnabled(False)
        self.copyAction.setStatusTip('Copy selected modules in '
                                     'the current pipeline view')

        self.pasteAction = QtGui.QAction('Paste', self)
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.setEnabled(False)
        self.pasteAction.setStatusTip('Paste copied modules in the clipboard '
                                      'into the current pipeline view')
        
        self.shellAction = QtGui.QAction(CurrentTheme.CONSOLE_MODE_ICON,
                                         'VisTrails Console', self)
        self.shellAction.setCheckable(True)
        self.shellAction.setShortcut('Ctrl+H')

        self.sdiModeAction = QtGui.QAction('SDI Mode', self)
        self.sdiModeAction.setCheckable(True)
        
        self.helpAction = QtGui.QAction(self.tr('About VisTrails...'), self)        

    def createMenu(self):
        """ createMenu() -> None
        Initialize menu bar of builder window
        
        """
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.newVistrailAction)
        self.fileMenu.addAction(self.openVistrailAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveVistrailAction)
        self.fileMenu.addAction(self.saveVistrailAsAction)
        self.fileMenu.addAction(self.closeVistrailAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitVistrailsAction)

        self.editMenu = self.menuBar().addMenu('&Edit')
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.pasteAction)

        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(self.shellAction)
        self.viewMenu.addAction(
            self.modulePalette.toolWindow().toggleViewAction())
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.sdiModeAction)

        self.vistrailMenu = self.menuBar().addMenu('Vis&trail')
        self.vistrailActionGroup = QtGui.QActionGroup(self)
        
    def createToolBar(self):
        """ createToolBar() -> None
        Create a default toolbar for this builder window
        
        """
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setWindowTitle('Vistrail File')
        self.addToolBar(self.toolBar)
        self.toolBar.addAction(self.newVistrailAction)
        self.toolBar.addAction(self.openVistrailAction)
        self.toolBar.addAction(self.saveVistrailAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.shellAction)
        self.toolBar.addAction(self.sdiModeAction)

    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between various GUI components        
        
        """
        self.connect(self.viewManager,
                     QtCore.SIGNAL('moduleSelectionChange'),
                     self.moduleSelectionChange)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('currentVistrailChanged'),
                     self.currentVistrailChanged)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('vistrailViewAdded'),
                     self.vistrailViewAdded)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('vistrailViewRemoved'),
                     self.vistrailViewRemoved)
                     
        self.connect(QtGui.QApplication.clipboard(),
                     QtCore.SIGNAL('dataChanged()'),
                     self.clipboardChanged)
        
        self.connect(self.copyAction,
                     QtCore.SIGNAL('triggered()'),
                     self.copySelectedModules)                     
        self.connect(self.pasteAction,
                     QtCore.SIGNAL('triggered()'),
                     self.pasteToCurrentPipeline)
        
        self.connect(self.newVistrailAction,
                     QtCore.SIGNAL('triggered()'),
                     self.viewManager.newVistrail)
        
        self.connect(self.openVistrailAction,
                     QtCore.SIGNAL('triggered()'),
                     self.openVistrail)
        
        self.connect(self.saveVistrailAction,
                     QtCore.SIGNAL('triggered()'),
                     self.saveVistrail)
        
        self.connect(self.saveVistrailAsAction,
                     QtCore.SIGNAL('triggered()'),
                     self.saveVistrailAs)
        
        self.connect(self.closeVistrailAction,
                     QtCore.SIGNAL('triggered()'),
                     self.viewManager.closeVistrail)

        self.connect(self.sdiModeAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.setSDIMode)
        
        self.connect(self.vistrailActionGroup,
                     QtCore.SIGNAL('triggered(QAction *)'),
                     self.vistrailSelectFromMenu)
        
        self.connect(self.quitVistrailsAction,
                     QtCore.SIGNAL('triggered()'),
                     self.quitVistrails)
        
        self.connect(self.shellAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showShell)
        
    def moduleSelectionChange(self, selection):
        """ moduleSelectionChange(selection: list[id]) -> None
        Update the status of tool bar buttons if there is module selected
        
        """
        self.copyAction.setEnabled(len(selection)>0)

    def clipboardChanged(self, mode=QtGui.QClipboard.Clipboard):
        """ clipboardChanged(mode: QClipboard) -> None        
        Update the status of tool bar buttons when the clipboard
        contents has been changed
        
        """
        clipboard = QtGui.QApplication.clipboard()
        self.pasteAction.setEnabled(not clipboard.text().isEmpty())

    def copySelectedModules(self):
        """ copySelectedModules() -> None
        Copy the selected modules of the active pipeline into memory
        
        """
        self.viewManager.copySelection()

    def pasteToCurrentPipeline(self):
        """ pasteToCurrentPipeline() -> None
        Paste what is on the clipboard to the current pipeline
        
        """        
        self.viewManager.pasteToCurrentPipeline()

    def currentVistrailChanged(self, vistrailView):
        """ currentVistrailChanged(vistrailView: QVistrailView) -> None
        Redisplay the new title of vistrail
        
        """
        if vistrailView:
            self.setWindowTitle('VisTrails Builder - ' +
                                vistrailView.windowTitle())
        else:
            self.setWindowTitle('VisTrails Builder')
            
        if self.viewManager.sdiMode:
            if self.vistrailViewToolBar:
                area = self.toolBarArea(self.vistrailViewToolBar)
                self.removeToolBar(self.vistrailViewToolBar)
            else:
                area = self.toolBarArea(self.toolBar)                
            self.vistrailViewToolBar = self.viewManager.getCurrentToolBar()
            if self.vistrailViewToolBar:
                self.addToolBar(area, self.vistrailViewToolBar)
                self.vistrailViewToolBar.show()
                
        if vistrailView and vistrailView.viewAction:
            vistrailView.viewAction.setText(vistrailView.windowTitle())
            if not vistrailView.viewAction.isChecked():
                vistrailView.viewAction.setChecked(True)

    def openVistrail(self):
        """ openVistrail() -> None
        Open a new vistrail
        
        """
        fileName = QtGui.QFileDialog.getOpenFileName(
            self,
            "Open VisTrail...",
            system.vistrailsDirectory(),
            "Vistrail files (*.xml)")
        if not fileName.isEmpty():
            self.viewManager.openVistrail(str(fileName))

    def saveVistrail(self):
        """ saveVistrail() -> None
        Save the current vistrail to file
        
        """
        self.viewManager.saveVistrail()

    def saveVistrailAs(self):
        """ saveVistrailAs() -> None
        Save the current vistrail to a different file
        
        """
        fileName = QtGui.QFileDialog.getSaveFileName(
            self,
            "Save Vistrail As..",
            system.vistrailsDirectory(),
            "XML files (*.xml)")
            
        if not fileName:
            return
        else:
            self.viewManager.saveVistrail(str(fileName))

    def quitVistrails(self):
        """ quitVistrails() -> bool
        Quit Vistrail, return False if not succeeded
        
        """
        if self.viewManager.closeAllVistrails():
            QtCore.QCoreApplication.quit()
        return False

    def setSDIMode(self, checked=True):
        """ setSDIMode(checked: bool)
        Switch/Unswitch to Single Document Interface
        
        """
        if checked:
            self.viewManager.switchToSDIMode()
            self.vistrailViewToolBar = self.viewManager.getCurrentToolBar()
            if self.vistrailViewToolBar:
                self.addToolBar(self.toolBarArea(self.toolBar),
                                self.vistrailViewToolBar)
                self.vistrailViewToolBar.show()
        else:
            if self.vistrailViewToolBar:
                self.removeToolBar(self.vistrailViewToolBar)
                self.vistrailViewToolBar = None
            self.viewManager.switchToTabMode()
                
    def vistrailViewAdded(self, view):
        """ vistrailViewAdded(view: QVistrailView) -> None
        Add this vistrail to the Vistrail menu
        
        """
        view.viewAction = QtGui.QAction(view.windowTitle(), self)
        view.viewAction.view = view
        view.viewAction.setCheckable(True)
        self.vistrailActionGroup.addAction(view.viewAction)
        self.vistrailMenu.addAction(view.viewAction)

    def vistrailViewRemoved(self, view):
        """ vistrailViewRemoved(view: QVistrailView) -> None
        Remove this vistrail from the Vistrail menu
        
        """
        self.vistrailActionGroup.removeAction(view.viewAction)
        self.vistrailMenu.removeAction(view.viewAction)

    def vistrailSelectFromMenu(self, menuAction):
        """ vistrailSelectFromMenu(menuAction: QAction) -> None
        Handle clicked from the Vistrail menu
        
        """
        self.viewManager.setCurrentWidget(menuAction.view)

    def showShell(self, checked=True):
        """ showShell() -> None
        Display the shell console
        
        """
        if checked:
            if not self.shell:
                self.shell = QShellDialog(self)
            self.shell.show()
        else:
            if self.shell:
                self.shell.hide()
        
