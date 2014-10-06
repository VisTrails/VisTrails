###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
################################################################################
# This file implements the main spreadsheet window:
#   SpreadsheetWindow
################################################################################
from PyQt4 import QtCore, QtGui
from spreadsheet_base import StandardSheetReference
from spreadsheet_event import BatchDisplayCellEventType, DisplayCellEventType, \
     RepaintCurrentSheetEventType
from spreadsheet_tabcontroller import StandardWidgetTabController
from spreadsheet_sheet import StandardWidgetSheet
from spreadsheet_cell import QCellContainer
from spreadsheet_config import configuration
from vistrails.core.modules import module_utils
from vistrails.core.utils import trace_method
import ctypes
import os.path
import sys
import tempfile

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
        self.setWindowTitle('Untitled - VisTrails Spreadsheet')
        self.shownConfig = False #flag to control the window setup code is done only once
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
        
        self.visApp = QtCore.QCoreApplication.instance()
        self.visApp.installEventFilter(self)
        
        self.setupMenu()
        
        self.connect(self.tabController,
                     QtCore.SIGNAL('needChangeTitle'),
                     self.setWindowTitle)
        self.file_pool = module_utils.FilePool()
        self.echoMode = False
        self.echoCellEvents = []

        if hasattr(self.visApp, 'builderWindow'):
            self.quitAction = QtGui.QAction('&Quit VisTrails', self)
            self.addAction(self.quitAction)
            self.quitAction.setShortcut('Ctrl+Q')
            self.connect(self.quitAction,
                         QtCore.SIGNAL('triggered()'),
                         self.quitActionTriggered)

        # if the spreadsheet has one row and 2 columns
        # this will cause the spreadsheet to have each cell
        # 550 x 450 size in the server
        #self.resize(1156, 599)

    def quitActionTriggered(self):
        if self.visApp and hasattr(self.visApp, 'builderWindow') and \
           self.visApp.builderWindow.isVisible():
            self.visApp.builderWindow.quit()

    
    def cleanup(self):
        if self.visApp!=None:
            self.visApp.removeEventFilter(self)
        self.file_pool.cleanup()
        self.tabController.cleanup()

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
        self.viewMenu.addAction(self.fitToWindowAction())
        self.viewMenu.addAction(self.fullScreenAction())
        self.windowMenu = QtGui.QMenu('&Window', self.menuBar())
        self.menuBar().addAction(self.windowMenu.menuAction())
        self.windowMenu.addAction(self.showBuilderWindowAction())

        self.connect(self.modeActionGroup,
                     QtCore.SIGNAL('triggered(QAction*)'),
                     self.modeChanged)

    def fitToWindowAction(self):
        """ fitToWindowAction() -> QAction
        Return the fit to window action
        
        """
        if not hasattr(self, 'fitAction'):
            self.fitAction = QtGui.QAction('Fit to window', self)
            self.fitAction.setStatusTip('Stretch spreadsheet cells '
                                        'to fit the window size')
            self.fitAction.setCheckable(True)
            checked = self.tabController.currentWidget().sheet.fitToWindow
            self.fitAction.setChecked(checked)
            self.connect(self.fitAction,
                         QtCore.SIGNAL('toggled(bool)'),
                         self.fitActionToggled)
        return self.fitAction

    def fitActionToggled(self, checked):
        """ fitActionToggled(checked: boolean) -> None
        Handle fitToWindow Action toggled
        
        """
        self.tabController.currentWidget().sheet.setFitToWindow(checked)
        
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
                             self.fullScreenActionVar.trigger)
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

    def showBuilderWindowAction(self):
        """ showBuilderWindowAction() -> QAction
        Return the show builder action, this is used to show the builder window
        when only the spreadsheet window is visible.
        
        """
        if not hasattr(self, 'showBuilderWindowActionVar'):
            self.showBuilderWindowActionVar = \
                                        QtGui.QAction('&Show Builder Window',
                                                      self)
            self.showBuilderWindowActionVar.setShortcut('Ctrl+Shift+B')
            self.showBuilderWindowActionVar.setStatusTip('Show the '
                                                         'Builder Window')
            if hasattr(self.visApp, 'builderWindow'):
                self.showBuilderWindowActionVar.setEnabled(True)
            else:
                self.showBuilderWindowActionVar.setEnabled(False)
                
            self.connect(self.showBuilderWindowActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showBuilderWindowActionTriggered)
            
        return self.showBuilderWindowActionVar
    
    def modeChanged(self, action):
        """ modeChanged(action: QAction) -> None        
        Handle the new mode (interactive or editing) based on the
        triggered action
        
        """
        editing = self.editingModeAction().isChecked()
        self.tabController.setEditingMode(editing)
    
    def configShow(self, show=False):
        """ configShow() -> None
        Read VisTrails setting and show the spreadsheet window accordingly
        
        """
        if hasattr(self.visApp, 'configuration'):
            if self.shownConfig:
                self.show()
            ### Multiheads
            desktop = QtGui.QApplication.desktop()
            if self.visApp.temp_configuration.multiHeads and desktop.numScreens()>1:
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
            if self.visApp.temp_configuration.batch:
                self.shownConfig = True
                if show:
                    self.show()
                return
            ### Maximize
            if self.visApp.temp_configuration.maximizeWindows:
                self.showMaximized()
                ### When the builder is hidden, the spreadsheet window does
                ### not have focus. We have to force it
                if not self.visApp.temp_configuration.showWindow:
                    self.raise_()
            else:
                self.show()
                ### When the builder is hidden, the spreadsheet window does
                ### not have focus. We have to force it to have the focus
                if not self.visApp.temp_configuration.showWindow:
                    self.raise_()                
        else:
            self.show()
            
        self.shownConfig = True

    def showEvent(self, e):
        """ showEvent(e: QShowEvent) -> None
        Make sure we show ourself for show event
        
        """
        self.show()
        # Without this Ubuntu Unity will not show the menu bar
        self.raise_()

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None
        When close, just hide instead
        
        """
        if hasattr(self.visApp, 'builderWindow'):
            if self.visApp.builderWindow.isVisible():
                e.ignore()
                self.hide()
            else:
                #if the window is not visible, we need to quit the application
                QtCore.QCoreApplication.quit()
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
        eType = e.type()
        # Handle Show/Hide cell resizer on MouseMove
        if eType==QtCore.QEvent.MouseMove:
            sheetWidget = self.tabController.tabWidgetUnderMouse()
            if sheetWidget:
                sheetWidget.showHelpers(True, QtGui.QCursor.pos())

        # Slideshow mode
        if (eType==QtCore.QEvent.MouseButtonPress and
            self.isFullScreen() and
            e.buttons()&QtCore.Qt.RightButton):
            self.tabController.showPopupMenu()
            return True
                
        # Handle slideshow shortcuts
        if (eType==QtCore.QEvent.KeyPress and
            self.isFullScreen()):
            if (e.key() in [QtCore.Qt.Key_Space,
                            QtCore.Qt.Key_PageDown,QtCore.Qt.Key_Right]):
                self.tabController.showNextTab()
                return True
            if (e.key() in [QtCore.Qt.Key_PageUp,QtCore.Qt.Key_Left]):
                self.tabController.showPrevTab()
                return True
            if (e.key()==QtCore.Qt.Key_Escape or
                (e.key()==QtCore.Qt.Key_F and e.modifiers()&QtCore.Qt.ControlModifier)):
                self.fullScreenAction().trigger()
                return True

        # Perform single-click event on the spread sheet
        if (not self.tabController.editingMode and
            eType==QtCore.QEvent.MouseButtonPress):
            if isinstance(q, QCellContainer):
                return q.containedWidget!=None
            p = q
            while (p and (not p.isModal()) and not isinstance(p, StandardWidgetSheet) and p.parent):
                p = p.parent()
            if p and isinstance(p, StandardWidgetSheet) and not p.isModal():
                pos = p.viewport().mapFromGlobal(e.globalPos())
                p.emit(QtCore.SIGNAL('cellActivated(int, int, bool)'),
                       p.rowAt(pos.y()), p.columnAt(pos.x()),
                       e.modifiers()==QtCore.Qt.ControlModifier)
        return False
        #return QtGui.QMainWindow.eventFilter(self,q,e)

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Handle all special events from spreadsheet controller
        
        """
        if self.eventMap.has_key(e.type()):
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
        if self.echoMode:
            self.echoCellEvents.append(e)
            return None 
        self.tabController.addPipeline(e.vistrail)
        cid = self.tabController.increasePipelineCellId(e.vistrail)
        pid = self.tabController.getCurrentPipelineId(e.vistrail)
        if self.tabController.isLoadingMode():
            locations = self.tabController.getMonitoredLocations((
                (e.vistrail), pid, cid))
            for (sheet, row, col) in locations:
                sheet.tabWidget.setCurrentWidget(sheet)
                sheet.setCellPipelineInfo(row, col, (e.vistrail, pid, cid))
                sheet.setCellByType(row, col, e.cellType, e.inputPorts)
            return None
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
            if e.rowSpan>=1 or e.colSpan>=1:
                sheet.setSpan(row, col, e.rowSpan, e.colSpan)
            if e.inputPorts!=None:
                sheet.setCellByType(row, col, e.cellType, e.inputPorts)
            else:
                sheet.setCellByWidget(row, col, e.cellType)
            QtCore.QCoreApplication.processEvents()
            cell = sheet.getCell(row, col) 
            if self.editingModeAction().isChecked():
                sheet.setCellEditingMode(row, col, True)
            #If a cell has to dump its contents to a file, it will be in the
            #extra_info dictionary
            if cell and e.vistrail.has_key('extra_info'):
                dump_as_pdf = False
                extra_info = e.vistrail['extra_info']
                if extra_info.has_key('pathDumpCells'):
                    dumppath = extra_info['pathDumpCells']
                    if extra_info.has_key('nameDumpCells'):
                        name = extra_info['nameDumpCells']
                        base_fname = os.path.join(dumppath,
                                                  name)
                    else:
                        locator = e.vistrail['locator']
                        if locator is not None:
                            name = e.vistrail['locator'].short_name
                        else:
                            name = 'untitled'
                        version = e.vistrail['version']
                        if version is None:
                            version = 0L
                        base_fname = os.path.join(dumppath,"%s_%s" % \
                                                  (name, e.vistrail['version']))

                    if configuration.dumpfileType == 'PNG':
                        dump_as_pdf = False
                    elif configuration.dumpfileType == 'PDF':
                        dump_as_pdf = True
                        
                    #extra_info configuration overwrites global configuration    
                    if extra_info.has_key('pdf'):
                        dump_as_pdf = extra_info['pdf']
                    
                    file_extension = '.png'
                    if dump_as_pdf == True:
                        file_extension = '.pdf'
                            
                    # add cell location by default
                    if not extra_info.has_key('nameDumpCells'):
                        base_fname = base_fname + "_%d_%d" % (row, col)
                    # make a unique filename
                    filename = base_fname + file_extension
                    counter = 2
                    while os.path.exists(filename):
                        filename = base_fname + "_%d%s" % (counter,
                                                           file_extension)
                        counter += 1
                    if not dump_as_pdf:
                        cell.dumpToFile(filename)
                    else:
                        cell.saveToPDF(filename)
            #if the cell was already selected, then we need to update 
            #the toolbar with this new cell
            if hasattr(sheet, 'sheet'):
                if sheet.sheet.activeCell == (row,col):
                    sheet.sheet.setActiveCell(row,col)
            return cell 

    def batchDisplayCellEvent(self, batchEvent):
        """ batchDisplayCellEvent(batchEvent: BatchDisplayCellEvent) -> None
        Handle event where a series of cells are arrived
        
        """
        self.tabController.addPipeline(batchEvent.vistrail)
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
    
    def showBuilderWindowActionTriggered(self):
        """showBuilderWindowActionTriggered() -> None
        This will show the builder window """
        self.visApp.builderWindow.show()

    def prepareReviewingMode(self, vCol):
        """ Trim down most of the spreadsheet window """
        self.menuBar().hide()
        self.statusBar().hide()
        self.tabController.tabBar().hide()
        self.tabController.clearTabs()
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Pipeline Review - VisTrails Spreadsheet')
        self.resize(560*vCol, 512)
        self.show()

    def startReviewingMode(self):
        """ startReviewingMode()
        Reorganize the spreadsheet to contain only cells executed from locator:version
        
        """
        currentTab = self.tabController.currentWidget()
        if currentTab:
            currentTab.toolBar.hide()
            buttonLayout = QtGui.QHBoxLayout()
            buttons = [QtGui.QPushButton('&Accept'),
                       QtGui.QPushButton('&Discard')]
            buttonLayout.addStretch()
            buttonLayout.addWidget(buttons[0])
            buttonLayout.addWidget(buttons[1])
            buttonLayout.addStretch()
            currentTab.layout().addLayout(buttonLayout)
            self.connect(buttons[0], QtCore.SIGNAL('clicked()'),
                         self.acceptReview)
            self.connect(buttons[1], QtCore.SIGNAL('clicked()'),
                         self.discardReview)

    def discardReview(self):
        """ Just quit the program """
        QtCore.QCoreApplication.quit()

    def acceptReview(self):
        """ Copy image of all cells to the clipboard and then exit """
        currentTab = self.tabController.currentWidget()
        height = 0
        width = 0
        pixmaps = []
        version = -1
        if currentTab:
            (rCount, cCount) = currentTab.getDimension()
            for r in xrange(rCount):
                for c in xrange(cCount):
                    widget = currentTab.getCell(r, c)
                    if widget:
                        version = currentTab.getCellPipelineInfo(r, c)[0]['version']
                        pix = widget.grabWindowPixmap()
                        pixmaps.append(pix)
                        width += pix.width()
                        height = max(height, pix.height())
        finalImage = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(finalImage)
        x = 0
        for pix in pixmaps:
            painter.drawPixmap(x, 0, pix)
            x += pix.width()
        painter.end()
        filename = tempfile.gettempdir() + '/' + 'vtexport.png'
        finalImage.save(filename, 'PNG')
        sm = QtCore.QSharedMemory('VisTrailsPipelineImage')
        sm.create(32768)
        sm.attach()
        sm.lock()
        pfn = ctypes.c_char_p(filename)
        ctypes.memmove(int(sm.data()), pfn, len(filename))
        pfn = ctypes.c_char_p(str(version))
        ctypes.memmove(int(sm.data())+256, pfn, len(str(version)))
        sm.unlock()
        sm.detach()
        QtCore.QCoreApplication.quit()

    def setEchoMode(self, echo):
        """ setEchoMode(echo: bool)
        Instruct the spreadsheet to dispatch (echo) all cell widgets
        instead of managing them on the spreadsheet

        """
        self.echoMode = echo

    def getEchoCellEvents(self):
        """ getEchoCellEvents() -> [DisplayCellEvent]
        Echo back the list of all cell events that have been captured
        earlier
        
        """
        return self.echoCellEvents

    def clearEchoCellEvents(self):
        """ clearEchoCellEvents()
        Erase the list of echoed events 

        """
        self.echoCellEvents = []

    
