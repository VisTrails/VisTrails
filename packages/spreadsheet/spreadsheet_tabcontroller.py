from spreadsheet_tab import *

################################################################################
################################################################################
### StandardWidgetTabController: inherited from QTabWidget to contain
### a list of StandardWidgetSheetTab
class StandardWidgetTabController(QtGui.QTabWidget):

    ### Init all properties
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.operatingWidget = self
        self.setTabBar(StandardWidgetTabBar(self))
        self.setTabShape(QtGui.QTabWidget.Triangular)
        self.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidgets = []
        self.floatingTabWidgets = []
        self.addTabWidget(StandardWidgetSheetTab(self), 'Sheet 1')
        self.connect(self.tabBar(),
                     QtCore.SIGNAL('tabMoveRequest(int,int)'),
                     self.moveTab)
        self.connect(self.tabBar(),
                     QtCore.SIGNAL('tabSplitRequest(int,QPoint)'),
                     self.splitTab)
        self.connect(self.tabBar(),
                     QtCore.SIGNAL('tabTextChanged(int,QString)'),
                     self.changeTabText)
        self.addAction(self.showNextTabAction())
        self.addAction(self.showPrevTabAction())
        self.executedPipelines = [[],{},{}]
        self.monitoredPipelines = {}
        self.spreadsheetFileName = None
        self.loadingMode = False

    ### Checking if the controller is in loading mode
    def isLoadingMode(self):
        return self.loadingMode

    ### Return the monitored location associated with spec
    def getMonitoredLocations(self, spec):
        if spec in self.monitoredPipelines:
            return self.monitoredPipelines[spec]
        else:
            return []

    ### Return the new sheet action:
    def newSheetAction(self):
        if not hasattr(self, 'newSheetActionVar'):
            self.newSheetActionVar = QtGui.QAction(QtGui.QIcon(':/images/newsheet.png'),
                                                '&New sheet', self)
            self.newSheetActionVar.setToolTip('Create a new sheet')
            self.newSheetActionVar.setStatusTip('Create and show a new sheet')
            self.newSheetActionVar.setShortcut(QtGui.QKeySequence('Ctrl+N'))
            self.connect(self.newSheetActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.newSheetActionTriggered)
        return self.newSheetActionVar

    ### Return the new sheet action:
    def deleteSheetAction(self):
        if not hasattr(self, 'deleteSheetActionVar'):
            self.deleteSheetActionVar = QtGui.QAction(QtGui.QIcon(':/images/deletesheet.png'),
                                                '&Delete sheet', self)
            self.deleteSheetActionVar.setToolTip('Delete the current sheet')
            self.deleteSheetActionVar.setStatusTip('Delete the current sheet if there are more than one')
            self.deleteSheetActionVar.setShortcut(QtGui.QKeySequence('Ctrl+Backspace'))
            self.connect(self.deleteSheetActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.deleteSheetActionTriggered)
        return self.deleteSheetActionVar

    ### Return the show next tab action
    def showNextTabAction(self):
        if not hasattr(self, 'showNextTabActionVar'):
            self.showNextTabActionVar = QtGui.QAction(QtGui.QIcon(':/images/forward.png'),
                                                      '&Next sheet', self)
            self.showNextTabActionVar.setToolTip('Show the next sheet')
            self.showNextTabActionVar.setStatusTip('Show the next sheet if it is available')
            self.showNextTabActionShortcut = QtGui.QShortcut(self)
            self.showNextTabActionVar.setShortcut('Ctrl+PgDown')
            self.connect(self.showNextTabActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showNextTab)
        return self.showNextTabActionVar

    ### Return the show prev tab action
    def showPrevTabAction(self):
        if not hasattr(self, 'showPrevTabActionVar'):
            self.showPrevTabActionVar = QtGui.QAction(QtGui.QIcon(':/images/back.png'),
                                                      '&Prev sheet', self)
            self.showPrevTabActionVar.setToolTip('Show the previous sheet')
            self.showPrevTabActionVar.setStatusTip('Show the previous sheet if it is available')
            self.showPrevTabActionVar.setShortcut('Ctrl+PgUp')
            self.connect(self.showPrevTabActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showPrevTab)
        return self.showPrevTabActionVar

    ### Return the save action
    def saveAction(self):
        if not hasattr(self, 'saveActionVar'):
            self.saveActionVar = QtGui.QAction(QtGui.QIcon(':/images/save.png'), '&Save', self)
            self.saveActionVar.setStatusTip('Save the current spreadsheet')
            self.saveActionVar.setShortcut('Ctrl+S')
            self.connect(self.saveActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.saveSpreadsheet)
        return self.saveActionVar

    ### Return the save as action
    def saveAsAction(self):
        if not hasattr(self, 'saveAsActionVar'):
            self.saveAsActionVar = QtGui.QAction(QtGui.QIcon(':/images/saveas.png'),
                                                 'Save &As...', self)
            self.saveAsActionVar.setStatusTip('Save the current spreadsheet at a new location')
            self.connect(self.saveAsActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.saveSpreadsheetAs)
        return self.saveAsActionVar

    ### Return the open action
    def openAction(self):
        if not hasattr(self, 'openActionVar'):
            self.openActionVar = QtGui.QAction(QtGui.QIcon(':/images/open.png'),
                                               '&Open...', self)
            self.openActionVar.setStatusTip('Open a new spreadsheet')
            self.openActionVar.setShortcut('Ctrl+O')
            self.connect(self.openActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.openSpreadsheetAs)
        return self.openActionVar

    ### Actually code to create a new sheet
    def newSheetActionTriggered(self, checked=False):
        self.setCurrentIndex(self.addTabWidget(StandardWidgetSheetTab(self),
                                               'Sheet %d' % (self.count()+1)))
        self.currentWidget().sheet.stretchCells()

    ### Actually code to delete the current sheet
    def deleteSheetActionTriggered(self, checked=False):
        if self.count()>0:
            widget = self.currentWidget()
            self.tabWidgets.remove(widget)
            self.removeTab(self.currentIndex())
            widget.deleteLater()

    ### Clear the whole controller
    def clearTabs(self):
        self.executedPipelines = [[], {}, {}]
        while self.count()>0:
            self.removeTab(self.count()-1)
        for i in reversed(range(len(self.tabWidgets))):
            t = self.tabWidgets[i]
            del self.tabWidgets[i]
            t.deleteLater()

    ### Redirect insertTab command to operatingWidget
    def insertTab(self, idx, tabWidget, tabText):
        if self.operatingWidget!=self:
            ret = self.operatingWidget.insertWidget(idx, tabWidget)
            self.operatingWidget.setCurrentIndex(ret)
            return ret
        else:
            return QtGui.QTabWidget.insertTab(self, idx, tabWidget, tabText)

    ### Find/Create a sheet that meets a certen sheet reference
    def findSheet(self, sheetReference):
        if not sheetReference:
            return None
        sheetReference.clearCandidate()
        for idx in range(len(self.tabWidgets)):
            tabWidget = self.tabWidgets[idx]
            tabLabel = tabWidget.windowTitle()
            sheetReference.checkCandidate(tabWidget, tabLabel, idx, self.operatingWidget.currentIndex())
        return sheetReference.setupCandidate(self)

    ### A tab text has been updated
    def changeTabText(self, tabIdx, newTabText):
        self.operatingWidget.widget(tabIdx).setWindowTitle(newTabText)

    ### Move a tab to a different position
    def moveTab(self, tabIdx, destination):
        if (tabIdx<0 or tabIdx>self.count() or
            destination<0 or destination>self.count()):
            return
        tabText = self.tabText(tabIdx)
        tabWidget = self.widget(tabIdx)
        self.removeTab(tabIdx)
        self.insertTab(destination, tabWidget, tabText)
        if tabIdx==self.currentIndex():
            self.setCurrentIndex(destination)

    ### Split a tab to be  a stand alone window
    def splitTab(self, tabIdx, pos=None):
        if tabIdx<0 or tabIdx>self.count() or self.count()==0:
            return
        tabWidget = self.widget(tabIdx)
        self.removeTab(tabIdx)
        
        frame = StandardTabDockWidget(tabWidget.windowTitle(), tabWidget, self.tabBar(), self)
        if pos:
            frame.move(pos)
        frame.show()        
        self.floatingTabWidgets.append(frame)

    ### Merge a tab dock widget back to the controller
    def mergeTab(self, frame, tabIdx):
        if tabIdx<0 or tabIdx>self.count():
            return
        if tabIdx==self.count(): tabIdx = -1
        tabWidget = frame.widget()
        frame.setWidget(None)
        while frame in self.floatingTabWidgets:
            self.floatingTabWidgets.remove(frame)
        frame.deleteLater()
        tabWidget.setParent(None)
        newIdx = self.insertTab(tabIdx, tabWidget, tabWidget.windowTitle())
        self.setCurrentIndex(newIdx)

    ### Add a new tab widget to the controller
    def addTabWidget(self, tabWidget, sheetLabel):
        return self.insertTabWidget(-1, tabWidget, sheetLabel)

    ### Insert a tab widget to the controller at some location
    def insertTabWidget(self, index, tabWidget, sheetLabel):
        if sheetLabel==None:
            sheetLabel = 'Sheet %d' % (len(self.tabWidgets)+1)
        if not tabWidget in self.tabWidgets:
            self.tabWidgets.append(tabWidget)
            tabWidget.setWindowTitle(sheetLabel)
        return self.insertTab(index, tabWidget, sheetLabel)

    ### Return the tab widget that is under mouse, hide helpers for the rest
    def tabWidgetUnderMouse(self):
        result = None
        for t in self.tabWidgets:
            if t.underMouse():
                result = t
            else:
                t.showHelpers(False, QtCore.QPoint(-1,-1))
        return result

    ### Prepare/Clean up full screen mode
    def setupFullScreenWidget(self, fs, stackedWidget):
        if fs:
            idx = self.currentIndex()
            for i in range(self.count()):
                widget = self.widget(0)
                self.removeTab(0)
                self.tabTrueParent = widget.parent()
                widget.setParent(stackedWidget)
                stackedWidget.addWidget(widget)
            stackedWidget.setCurrentIndex(idx)
            self.operatingWidget = stackedWidget
        else:
            idx = stackedWidget.currentIndex()
            for i in range(stackedWidget.count()):
                widget = stackedWidget.widget(0)
                stackedWidget.removeWidget(widget)
                widget.setParent(self.tabTrueParent)
                self.addTab(widget, widget.windowTitle())
            self.setCurrentIndex(idx)
            self.operatingWidget = self

    ### Bring the next tab up
    def showNextTab(self):
        if self.operatingWidget.currentIndex()<self.operatingWidget.count()-1:
            self.operatingWidget.setCurrentIndex(self.operatingWidget.currentIndex()+1)

    ### Bring the prev tab up
    def showPrevTab(self):
        if self.operatingWidget.currentIndex()>0:
            self.operatingWidget.setCurrentIndex(self.operatingWidget.currentIndex()-1)

    ### Tab list popup menu
    def tabPopupMenu(self):
        menu = QtGui.QMenu(self)
        self.showNextTabAction().setEnabled(self.operatingWidget.currentIndex()<self.operatingWidget.count()-1)
        menu.addAction(self.showNextTabAction())
        self.showPrevTabAction().setEnabled(self.operatingWidget.currentIndex()>0)
        menu.addAction(self.showPrevTabAction())
        menu.addSeparator()
        for idx in range(self.operatingWidget.count()):
            t = self.operatingWidget.widget(idx)
            action = menu.addAction(t.windowTitle())
            action.setData(QtCore.QVariant(idx))
            if t==self.operatingWidget.currentWidget():
                action.setIcon(QtGui.QIcon(':/images/ok.png'))
        return menu

    ### Activate the tab list
    def showPopupMenu(self):
        menu = self.tabPopupMenu()
        action = menu.exec_(QtGui.QCursor.pos())
        self.showNextTabAction().setEnabled(True)
        self.showPrevTabAction().setEnabled(True)
        if not action: return
        if not action in self.actions():
            self.operatingWidget.setCurrentIndex(action.data().toInt()[0])
        menu.deleteLater()

    def changeSpreadsheetFileName(self, fileName):
        self.spreadsheetFileName = fileName
        if self.spreadsheetFileName:
            displayName = self.spreadsheetFileName
        else:
            displayName = 'Untitled'
        self.emit(QtCore.SIGNAL('needChangeTitle'),
                  'VisTrails - Spreadsheet - %s' % displayName)

    ### Add vistrail pipeline executions to history
    def addPipeline(self, vistrail):
        self.executedPipelines[0].append(vistrail)
        if not vistrail in self.executedPipelines[1]:
            self.executedPipelines[1][vistrail] = 0
        else:
            self.executedPipelines[1][vistrail] += 1
        self.executedPipelines[2][vistrail] = 0

    ### Get the current pipeline id
    def getCurrentPipelineId(self, vistrail):
        return self.executedPipelines[1][vistrail]

    ### Increase the current cell pipeline id
    def increasePipelineCellId(self, vistrail):
        cid = self.executedPipelines[2][vistrail]
        self.executedPipelines[2][vistrail] += 1
        return cid
        
    ### Get current pipeline cell id
    def getCurrentPipelineCellId(self, vistrail):
        return self.executedPipelines[2][vistrail]
        
    ### Add vistrail pipeline executions to history
    def addPipelineCell(self, vistrail):
        self.executedPipelines[0].append(vistrail)
        if not vistrail in self.executedPipelines[1]:
            self.executedPipelines[1][vistrail] = 0
        else:
            self.executedPipelines[1][vistrail] += 1


    ### Save the current spreadsheet
    def saveSpreadsheet(self, fileName=None):
        if fileName==None:
            fileName = self.spreadsheetFileName
        if fileName:
            import os
            import os.path
            indexFile = open(fileName, 'w')
            try:
                try:
                    indexFile.write(str(len(self.tabWidgets))+'\n')
                    for t in self.tabWidgets:
                        dim = t.getDimension()
                        indexFile.write('%s\n'%str((str(t.windowTitle()),
                                                    spreadsheetRegistry.getSheetByType(type(t)),
                                                    dim[0], dim[1])))
                        for r in range(dim[0]):
                            for c in range(dim[1]):
                                info = t.getCellPipelineInfo(r,c)
                                if info:
                                    indexFile.write('%s\n'
                                                    %str((r, c, info[0], info[1], info[2])))
                        indexFile.write('---\n')
                    indexFile.write(str(len(self.executedPipelines[0]))+'\n')
                    for vistrail in self.executedPipelines[0]:
                        indexFile.write('%s\n'%str(vistrail))
                    self.changeSpreadsheetFileName(fileName)
                except:
                    QtGui.QMessageBox.warning(self,
                                              'Save Spreadsheet Error',
                                              'Cannot save spreadsheet to %s' % fileName)
            finally:
                indexFile.close()
        else:
            self.saveSpreadsheetAs()
        
    ### Save the current spreadsheet to a new folder
    def saveSpreadsheetAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                       'Choose a spreadsheet name',
                                                       '',
                                                       'VisTrails Spreadsheet (*.vss)')
        if not fileName.isNull():
            fileName = str(fileName)
            import os.path
            (root,ext) = os.path.splitext(fileName)
            if ext=='':
                fileName += '.vss'
            self.saveSpreadsheet(fileName)
        
    ### Open a saved spreadsheet
    def openSpreadsheet(self, fileName):
        try:
            try:
                import os
                import os.path
                indexFile = open(fileName, 'r')
                contents = indexFile.read()
                self.clearTabs()
                lidx = 0
                lines = contents.split('\n')
                tabCount = int(lines[lidx])
                lidx += 1
                for tabIdx in range(tabCount):
                    tabInfo = eval(lines[lidx])
                    lidx += 1
                    sheet = spreadsheetRegistry.getSheet(tabInfo[1])(self)
                    sheet.setDimension(tabInfo[2], tabInfo[3])
                    self.addTabWidget(sheet, tabInfo[0])
                    while lines[lidx]!='---':
                        (r, c, vistrail, pid, cid) = eval(lines[lidx])
                        if not (vistrail,pid,cid) in self.monitoredPipelines:                            
                            self.monitoredPipelines[(vistrail,pid,cid)] = []
                        self.monitoredPipelines[(vistrail,pid,cid)].append((sheet,r,c))
                        lidx += 1
                    lidx += 1
                pipelineCount = int(lines[lidx])
                lidx += 1
                self.loadingMode = True
                progress = QtGui.QProgressDialog("Loading spreadsheet...",
                                                 "&Cancel", 0, pipelineCount, self,
                                                 QtCore.Qt.WindowStaysOnTopHint);
                progress.show()
                for pipelineIdx in range(pipelineCount):
                    (vistrailFileName, version) = eval(lines[lidx])
                    from xml_parser import XMLParser
                    parser = XMLParser()
                    parser.openVistrail(vistrailFileName)
                    vistrail = parser.getVistrail()
                    pipeline = vistrail.getPipeline(version)
                    from interpreter import Interpreter
                    execution = Interpreter()
                    progress.setValue(pipelineIdx)
                    QtCore.QCoreApplication.processEvents()
                    if progress.wasCanceled():
                        parser.closeVistrail()
                        break
                    pipeline.resolveAliases()
                    execution.execute(pipeline, vistrailFileName, version, None, None)
                    parser.closeVistrail()
                    lidx += 1
                progress.setValue(pipelineCount)
                QtCore.QCoreApplication.processEvents()
                self.changeSpreadsheetFileName(fileName)
            except:
                QtGui.QMessageBox.warning(self,
                                          'Open Spreadsheet Error',
                                          'Cannot open spreadsheet to %s' % fileName)
        finally:
            self.loadingMode = False
            indexFile.close()

    ### Open a saved spreadsheet
    def openSpreadsheetAs(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                       'Choose a spreadsheet',
                                                       '',
                                                       'VisTrails Spreadsheet (*.vss)',
                                                       )
        if not fileName.isNull():
            self.openSpreadsheet(fileName)
