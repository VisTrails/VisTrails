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
################################################################################
# This file implements the main spreadsheet window:
#   SpreadsheetWindow
################################################################################
import sys
from PyQt4 import QtCore, QtGui
from spreadsheet_base import StandardSheetReference
from spreadsheet_event import BatchDisplayCellEventType, DisplayCellEventType, \
     RepaintCurrentSheetEventType
from spreadsheet_tabcontroller import StandardWidgetTabController
from core.modules import module_utils
from core.utils import trace_method

################################################################################
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
        QtGui.QMainWindow.__init__(self, parent, f)
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
        self.modeActionGroup = QtGui.QActionGroup(self)
        self.setupMenu()
        self.visApp = QtCore.QCoreApplication.instance()
        self.visApp.installEventFilter(self)
        self.connect(self.tabController,
                     QtCore.SIGNAL('needChangeTitle'),
                     self.setWindowTitle)
        self.file_pool = module_utils.FilePool()

    def destroy(self):
        self.tabController.cleanup()
        self.file_pool.cleanup()

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
        self.viewMenu.addAction(self.interactiveModeAction())
        self.viewMenu.addAction(self.editingModeAction())
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fullScreenAction())

        self.connect(self.modeActionGroup,
                     QtCore.SIGNAL('triggered(QAction*)'),
                     self.modeChanged)

    def fullScreenAction(self):
        """ fullScreenAction() -> QAction
        Return the fullscreen action
        
        """
        if not hasattr(self, 'fullScreenActionVar'):
            self.fullScreenActionVar = QtGui.QAction('&Full Screen', self)
            self.fullScreenActionVar.setShortcut('Ctrl+F')
            self.fullScreenActionVar.setCheckable(True)
            self.fullScreenActionVar.setChecked(False)
            self.fullScreenActionVar.setStatusTip('Show sheets without any '
                                                  'menubar or statusbar')
            self.connect(self.fullScreenActionVar,
                         QtCore.SIGNAL('triggered(bool)'),
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

    def fullScreenActivated(self, full=None):
        """ fullScreenActivated(full: bool) -> None
        if fullScreen has been requested has pressed, then go to fullscreen now
        
        """
        if full==None:
            fs = self.isFullScreen()
            fs = not fs
        else:
            fs = full
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
        
    def interactiveModeAction(self):
        """ interactiveModeAction() -> QAction
        Return the interactive mode action, this is the mode where users can
        interact with the content of the cells
        
        """
        if not hasattr(self, 'interactiveModeActionVar'):
            self.interactiveModeActionVar = QtGui.QAction('&Interactive Mode',
                                                          self.modeActionGroup)
            self.interactiveModeActionVar.setCheckable(True)
            self.interactiveModeActionVar.setChecked(True)
            self.interactiveModeActionVar.setShortcut('Ctrl+Shift+I')
            self.interactiveModeActionVar.setStatusTip('Use this mode to '
                                                       'interact with '
                                                       'the cell contents')
        return self.interactiveModeActionVar
    
    def editingModeAction(self):
        """ editingModeAction() -> QAction
        Return the editing mode action, this is the mode where users can
        interact with the content of the cells
        
        """
        if not hasattr(self, 'editingModeActionVar'):
            self.editingModeActionVar = QtGui.QAction('&Editing Mode',
                                                      self.modeActionGroup)
            self.editingModeActionVar.setCheckable(True)
            self.editingModeActionVar.setShortcut('Ctrl+Shift+E')
            self.editingModeActionVar.setStatusTip('Use this mode to '
                                                   'layout cells and '
                                                   'interact cells with '
                                                   'the builder')
        return self.editingModeActionVar

    def modeChanged(self, action):
        """ modeChanged(actoin: QAction) -> None        
        Handle the new mode (interactive or editing) based on the
        triggered action
        
        """
        editing = self.editingModeAction().isChecked()
        self.tabController.setEditingMode(editing)
    
    def configShow(self):
        """ configShow() -> None
        Read VisTrails setting and show the spreadsheet window accordingly
        
        """
        if hasattr(self.visApp, 'configuration'):
            ### Multiheads
            desktop = QtGui.QApplication.desktop()
            if self.visApp.configuration.multiHeads and desktop.numScreens()>1:
                builderScreen = desktop.screenNumber(self.visApp.builderWindow)
                r = desktop.availableGeometry(builderScreen)
                self.visApp.builderWindow.ensurePolished()
                self.visApp.builderWindow.updateGeometry()
                frame = self.visApp.builderWindow.frameGeometry()
                rect = self.visApp.builderWindow.rect()
                frameDiff = QtCore.QPoint((frame.width()-rect.width())/2,
                                          (frame.height()-rect.height())/2)
                self.visApp.builderWindow.move(
                    frame.topLeft()+r.center()-frame.center())
                for i in xrange(desktop.numScreens()):
                    if i!=builderScreen:
                        r = desktop.availableGeometry(i)
                        self.adjustSize()
                        self.move(r.center()-self.rect().center()-frameDiff)
                        break
            ### Maximize
            if self.visApp.configuration.maximizeWindows:
                self.showMaximized()
            else:
                self.show()
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
        if hasattr(self.visApp, 'builderWindow'):
            e.ignore()
            self.hide()
        else:
            QtGui.QMainWindow.closeEvent(self, e)

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
                    ctrl = (e.modifiers()==QtCore.Qt.ControlModifier)
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
                            
        return QtGui.QMainWindow.eventFilter(self,q,e)

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Handle all special events from spreadsheet controller
        
        """
        if self.eventMap.has_key(e.type()):
            if e.type() in [DisplayCellEventType, BatchDisplayCellEventType]:
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
            BatchDisplayCellEventType : self.batchDisplayCellEvent,
            RepaintCurrentSheetEventType: self.repaintCurrentSheetEvent
            }

    def displayCellEvent(self, e):
        """ displayCellEvent(e: DisplayCellEvent) -> None
        Display a cell when receive this event
        
        """
        cid = self.tabController.increasePipelineCellId(e.vistrail)
        pid = self.tabController.getCurrentPipelineId(e.vistrail)
        if self.tabController.isLoadingMode():
            locations = self.tabController.getMonitoredLocations((
                (e.vistrail), pid, cid))
            for (sheet, row, col) in locations:
                sheet.tabWidget.setCurrentWidget(sheet)
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
            sheet.tabWidget.setCurrentWidget(sheet)
            sheet.setCellPipelineInfo(row, col,
                                      (e.vistrail, pid, cid))
            sheet.setCellByType(row, col, e.cellType, e.inputPorts)
            QtCore.QCoreApplication.processEvents()
            if self.editingModeAction().isChecked():
                sheet.setCellEditingMode(row, col, True)

    def batchDisplayCellEvent(self, batchEvent):
        """ batchDisplayCellEvent(batchEvent: BatchDisplayCellEvent) -> None
        Handle event where a series of cells are arrived
        
        """
        for e in batchEvent.displayEvents:
            e.vistrail = batchEvent.vistrail
            self.displayCellEvent(e)

    def repaintCurrentSheetEvent(self, e):
        """ repaintCurrentSheetEvent(e: RepaintCurrentSheetEvent) -> None
        Repaint the current sheet
        
        """
        currentTab = self.tabController.currentWidget()
        if currentTab:
            (rCount, cCount) = currentTab.getDimension()
            for r in xrange(rCount):
                for c in xrange(cCount):
                    widget = currentTab.getCell(r, c)
                    if widget:
                        widget.repaint()
