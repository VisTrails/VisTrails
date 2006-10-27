from PyQt4 import QtCore, QtGui
import sys
from spreadsheet_base import *
from spreadsheet_tabcontroller import *
from spreadsheet_tab import *
from spreadsheet_sheet import *
import spreadsheet_event

################################################################################
################################################################################
### SpreadsheetWindow: the top-level main window containing a
### QTabWidget of SheetTab
class SpreadsheetWindow(QtGui.QMainWindow):

    ### Layout menu, status bar and tab widget
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self,parent,f)
        self.createEventMap()
        self.setWindowTitle('VisTrails - Spreadsheet - Untitled')
        self.stackedCentralWidget = QtGui.QStackedWidget(self)
        self.tabController = StandardWidgetTabController(self.stackedCentralWidget)
        self.stackedCentralWidget.addWidget(self.tabController)
        self.fullScreenStackedWidget = QtGui.QStackedWidget(self.stackedCentralWidget)
        self.stackedCentralWidget.addWidget(self.fullScreenStackedWidget)
        self.setCentralWidget(self.stackedCentralWidget)
        self.setStatusBar(QtGui.QStatusBar(self))
        self.setupMenu()
        self.visApp = QtCore.QCoreApplication.instance()
        self.visApp.installEventFilter(self)
        self.connect(self.tabController,
                     QtCore.SIGNAL('needChangeTitle'),
                     self.setWindowTitle)

    ### Set up the menu bar
    def setupMenu(self):
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

    ### Return the fullscreen action
    def fullScreenAction(self):
        if not hasattr(self, 'fullScreenActionVar'):
            self.fullScreenActionVar = QtGui.QAction('&Full Screen\tF11', self)
            self.fullScreenActionVar.setStatusTip('Show sheets without any menubar or statusbar')
            self.connect(self.fullScreenActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.fullScreenActivated)
            self.fullScreenAlternativeShortcuts = [QtGui.QShortcut('F11', self),
                                                   QtGui.QShortcut('Alt+Return', self),
                                                   QtGui.QShortcut('Alt+Enter', self)]
            for sc in self.fullScreenAlternativeShortcuts:
                self.connect(sc, QtCore.SIGNAL('activated()'), self.fullScreenActivated)
        return self.fullScreenActionVar

    ### Alt+Enter has pressed, fullscreen?
    def fullScreenActivated(self):
        fs = self.isFullScreen()
        fs = not fs
        if fs:
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowNoState)
        fs = self.isFullScreen()
        self.menuBar().setVisible(not fs)
        self.statusBar().setVisible(not fs)
        self.tabController.setupFullScreenWidget(fs, self.fullScreenStackedWidget)
        self.stackedCentralWidget.setCurrentIndex(int(fs))
        
    ### Read VisTrails setting and show accordingly
    def configShow(self):
        if hasattr(self.visApp, 'configuration'):
            ### Multiheads
            desktop = QtGui.QApplication.desktop()
            if self.visApp.configuration.multiHeads and desktop.numScreens()>1:
                r = desktop.availableGeometry(desktop.primaryScreen())
                self.visApp.builderWindow.move(self.visApp.builderWindow.pos() + r.center()-
                                               self.visApp.builderWindow.frameGeometry().center())
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

    ### Make sure we show ourself for show event
    def showEvent(self, e):
        self.show()

    ### When close, just hide instead
    def closeEvent(self, e):
        e.ignore()
        self.hide()

    ### A default size of the window
    def sizeHint(self):
        return QtCore.QSize(1024, 768)

    ### An application-wide eventfilter to capture mouse/keyboard events
    def eventFilter(self,q,e):
        # Handle Show/Hide cell resizer/toolbars on KeyPress,
        # KeyRelease, MouseMove but avoid Shortcut event
        eType = e.type()
        if eType in [5, 6, 7, 117]:
            sheetWidget = self.tabController.tabWidgetUnderMouse()
            if sheetWidget:
                if eType!=117:
                    ctrl = e.modifiers()&QtCore.Qt.ControlModifier!=QtCore.Qt.NoModifier
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
            if (e.key() in [QtCore.Qt.Key_Space,QtCore.Qt.Key_PageDown,QtCore.Qt.Key_Right]):
                self.tabController.showNextTab()
                return True
            if (e.key() in [QtCore.Qt.Key_PageUp,QtCore.Qt.Key_Left]):
                self.tabController.showPrevTab()
                return True
                

        # Force to show status tip for top-level controller widgets
        if eType==112 and q.parent()==None:
            self.statusBar().showMessage(e.tip())
            
        return QtGui.QMainWindow.eventFilter(self,q,e)


    ### Handle all special events from spreadsheet controller
    def event(self, e):
        if self.eventMap.has_key(e.type()):
            self.tabController.addPipeline(e.vistrail)            
            self.eventMap[e.type()](e)
            return False
        return QtGui.QMainWindow.event(self, e)

    ### Create event map
    def createEventMap(self):
        self.eventMap = {
            spreadsheet_event.DisplayCellEventType : self.displayCellEvent,
            spreadsheet_event.BatchDisplayCellEventType : self.batchDisplayCellEvent
            }

    ### Handle event where a new cell is arrived
    def displayCellEvent(self, e):
        cid = self.tabController.increasePipelineCellId(e.vistrail)
        pid = self.tabController.getCurrentPipelineId(e.vistrail)
        if self.tabController.isLoadingMode():
            locations = self.tabController.getMonitoredLocations((e.vistrail, pid, cid))
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

    ### Handle event where a series of cells are arrived
    def batchDisplayCellEvent(self, batchEvent):
        for e in batchEvent.displayEvents:
            e.vistrail = batchEvent.vistrail
            self.displayCellEvent(e)
