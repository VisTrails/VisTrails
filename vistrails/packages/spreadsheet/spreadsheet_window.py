################################################################################
# This file implements the main spreadsheet window:
#   SpreadsheetWindow
################################################################################
import sys
from PyQt4 import QtCore, QtGui
from spreadsheet_base import StandardSheetReference
from spreadsheet_event import BatchDisplayCellEventType, DisplayCellEventType
from spreadsheet_tabcontroller import StandardWidgetTabController
from core.modules import module_utils
from core.utils import trace_method

################################################################################
### 
class SpreadsheetWindow(QtGui.QMainWindow):
    """
    SpreadsheetWindow is the top-level main window containing a
    stacked widget of QTabWidget and its stacked widget for slideshow
    mode
    
    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ SpreadsheetWindow(parent: QWidget, f: WindowFlags)
                              -> SpreadsheetWindow
        Layout menu, status bar and tab widget
        
        """
        QtGui.QMainWindow.__init__(self,parent,f)
        self.createEventMap()
        self.setWindowTitle('VisTrails - Spreadsheet - Untitled')
        self.stackedCentralWidget = QtGui.QStackedWidget(self)
        self.tabController = StandardWidgetTabController(
            self.stackedCentralWidget)
        self.stackedCentralWidget.addWidget(self.tabController)
        self.fullScreenStackedWidget = QtGui.QStackedWidget(
            self.stackedCentralWidget)
        self.stackedCentralWidget.addWidget(self.fullScreenStackedWidget)
        self.setCentralWidget(self.stackedCentralWidget)
        self.setStatusBar(QtGui.QStatusBar(self))
        self.setupMenu()
        self.visApp = QtCore.QCoreApplication.instance()
        self.visApp.installEventFilter(self)
        self.connect(self.tabController,
                     QtCore.SIGNAL('needChangeTitle'),
                     self.setWindowTitle)
        self.file_pool = module_utils.FilePool()


    def destroy(self):
        del self.file_pool

    def setupMenu(self):
        """ setupMenu() -> None
        Add all available actions to the menu bar

        """
        self.setMenuBar(QtGui.QMenuBar(self))
        self.mainMenu = QtGui.QMenu('&Main', self.menuBar())
        self.menuBar().addAction(self.mainMenu.menuAction())
        self.mainMenu.addAction(self.tabController.saveAction())
        self.mainMenu.addAction(self.tabController.saveAsAction())
        self.mainMenu.addAction(self.tabController.openAction())
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.tabController.newSheetAction())
        self.mainMenu.addAction(self.tabController.deleteSheetAction())
        self.viewMenu = QtGui.QMenu('&View', self.menuBar())
        self.menuBar().addAction(self.viewMenu.menuAction())
        self.viewMenu.addAction(self.fullScreenAction())

    def fullScreenAction(self):
        """ fullScreenAction() -> QAction
        Return the fullscreen action
        
        """
        if not hasattr(self, 'fullScreenActionVar'):
            self.fullScreenActionVar = QtGui.QAction('&Full Screen\tF11', self)
            self.fullScreenActionVar.setStatusTip('Show sheets without any '
                                                  'menubar or statusbar')
            self.connect(self.fullScreenActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.fullScreenActivated)
            self.fullScreenAlternativeShortcuts = [QtGui.QShortcut('F11', self),
                                                   QtGui.QShortcut('Alt+Return',
                                                                   self),
                                                   QtGui.QShortcut('Alt+Enter',
                                                                   self)]
            for sc in self.fullScreenAlternativeShortcuts:
                self.connect(sc, QtCore.SIGNAL('activated()'),
                             self.fullScreenActivated)
        return self.fullScreenActionVar

    def fullScreenActivated(self):
        """ fullScreenActivated() -> None
        Alt+Enter has pressed, then go fullscreen now
        """
        fs = self.isFullScreen()
        fs = not fs
        if fs:
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowNoState)
        fs = self.isFullScreen()
        self.menuBar().setVisible(not fs)
        self.statusBar().setVisible(not fs)
        self.tabController.setupFullScreenWidget(fs,
                                                 self.fullScreenStackedWidget)
        self.stackedCentralWidget.setCurrentIndex(int(fs))
        
    def configShow(self):
        """ configShow() -> None
        Read VisTrails setting and show the spreadsheet window accordingly
        
        """
        if hasattr(self.visApp, 'configuration'):
            ### Multiheads
            desktop = QtGui.QApplication.desktop()
            if self.visApp.configuration.multiHeads and desktop.numScreens()>1:
                r = desktop.availableGeometry(desktop.primaryScreen())
                center = self.visApp.builderWindow.frameGeometry().center()
                self.visApp.builderWindow.move(self.visApp.builderWindow.pos()
                                               + r.center() - center)
                for i in range(desktop.numScreens()):
                    if i!=desktop.primaryScreen():
                        r = desktop.availableGeometry(i)
                        self.move(r.center()-self.rect().center())
                        break
            ### Maximize
            if self.visApp.configuration.maximizeWindows:
                self.showMaximized()
            else:
                self.show()

    def showEvent(self, e):
        """ showEvent(e: QShowEvent) -> None
        Make sure we show ourself for show event
        
        """
        self.show()

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None
        When close, just hide instead
        
        """
        e.ignore()
        self.hide()

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return a default size of the window
        
        """
        return QtCore.QSize(1024, 768)

    def eventFilter(self,q,e):
        """ eventFilter(q: QObject, e: QEvent) -> depends on event type
        An application-wide eventfilter to capture mouse/keyboard events
        
        """
        # Handle Show/Hide cell resizer/toolbars on KeyPress,
        # KeyRelease, MouseMove but avoid Shortcut event
        eType = e.type()
        if eType in [5, 6, 7, 117]:
            sheetWidget = self.tabController.tabWidgetUnderMouse()
            if sheetWidget:
                if eType!=117:
                    ctrl = (e.modifiers()&QtCore.Qt.ControlModifier
                            !=QtCore.Qt.NoModifier)
                else:
                    ctrl = False
                sheetWidget.showHelpers(ctrl, QtGui.QCursor.pos())

        # Slideshow mode
        if (eType==QtCore.QEvent.MouseButtonPress and
            self.isFullScreen() and
            e.buttons()&QtCore.Qt.RightButton):
            self.tabController.showPopupMenu()
            return True
                
        if (eType==QtCore.QEvent.KeyPress and
            self.isFullScreen()):
            if (e.key() in [QtCore.Qt.Key_Space,
                            QtCore.Qt.Key_PageDown,QtCore.Qt.Key_Right]):
                self.tabController.showNextTab()
                return True
            if (e.key() in [QtCore.Qt.Key_PageUp,QtCore.Qt.Key_Left]):
                self.tabController.showPrevTab()
                return True
                

        # Force to show status tip for top-level controller widgets
        if eType==112 and q.parent()==None:
            self.statusBar().showMessage(e.tip())
            
        return QtGui.QMainWindow.eventFilter(self,q,e)

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Handle all special events from spreadsheet controller
        
        """
        if self.eventMap.has_key(e.type()):
            self.tabController.addPipeline(e.vistrail)            
            self.eventMap[e.type()](e)
            return False
        return QtGui.QMainWindow.event(self, e)

    def createEventMap(self):
        """ createEventMap() -> None        
        Create the event map to call inside the event(). This must be
        called before anything else
        
        """
        self.eventMap = {
            DisplayCellEventType : self.displayCellEvent,
            BatchDisplayCellEventType : self.batchDisplayCellEvent
            }

    def displayCellEvent(self, e):
        """ displayCellEvent(e: DisplayCellEvent) -> None
        Display a cell when receive this event
        
        """
        cid = self.tabController.increasePipelineCellId(e.vistrail)
        pid = self.tabController.getCurrentPipelineId(e.vistrail)
        if self.tabController.isLoadingMode():
            locations = self.tabController.getMonitoredLocations((e.vistrail,
                                                                  pid, cid))
            for (sheet, row, col) in locations:
                sheet.setCellPipelineInfo(row, col, (e.vistrail, pid, cid))
                sheet.setCellByType(row, col, e.cellType, e.inputPorts)
        else:
            reference = e.sheetReference
            if reference==None:
                reference = StandardSheetReference()
            sheet = self.tabController.findSheet(reference)
            row = e.row
            col = e.col
            if row<0 or col<0:
                (row, col) = sheet.getFreeCell()
            sheet.setCellPipelineInfo(row, col, (e.vistrail, pid, cid))
            sheet.setCellByType(row, col, e.cellType, e.inputPorts)

    def batchDisplayCellEvent(self, batchEvent):
        """ batchDisplayCellEvent(batchEvent: BatchDisplayCellEvent) -> None
        Handle event where a series of cells are arrived
        
        """
        for e in batchEvent.displayEvents:
            e.vistrail = batchEvent.vistrail
            self.displayCellEvent(e)
