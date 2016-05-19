###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

"""This file implements the Spreadsheet Tab Controller, to manages tabs:
StandardWidgetTabController
"""

from __future__ import division

from ast import literal_eval
import copy
import gc
import os.path
from PyQt4 import QtCore, QtGui

from vistrails.core.db.locator import FileLocator, _DBLocator as DBLocator
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.utils import DummyView
from vistrails.core.utils.uxml import XMLWrapper, named_elements
from vistrails.db.services.io import SaveBundle
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.utils import show_warning

from .spreadsheet_registry import spreadsheetRegistry
from .spreadsheet_tab import StandardWidgetTabBar, StandardWidgetSheetTab, \
    StandardTabDockWidget


class StandardWidgetTabController(QtGui.QTabWidget):
    """
    StandardWidgetTabController inherits from QTabWidget to contain a
    list of StandardWidgetSheetTab. This is the major component that
    will handle most of the spreadsheet actions

    """
    def __init__(self, parent=None):
        """ StandardWidgetTabController(parent: QWidget)
                                        -> StandardWidgetTabController
        Initialize signals/slots and widgets for the tab bar

        """

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
        self.editingMode = False
        self.closeButton = QtGui.QToolButton(self)
        self.closeButton.setIcon(CurrentTheme.VIEW_MANAGER_CLOSE_ICON)
        self.closeButton.setAutoRaise(True)
        self.setCornerWidget(self.closeButton)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self.deleteSheetAction().trigger)

    def isLoadingMode(self):
        """ isLoadingMode() -> boolean
        Checking if the controller is in loading mode

        """
        return self.loadingMode

    def getMonitoredLocations(self, spec):
        """ getMonitoredLocations(spec: tuple) -> location
        Return the monitored location associated with spec

        """
        key = ((spec[0]['locator'], spec[0]['version']), spec[1], spec[2])
        if key in self.monitoredPipelines:
            return self.monitoredPipelines[key]
        else:
            return []

    def appendMonitoredLocations(self, spec, value):
        """ getMonitoredLocations(spec: tuple, value: location) -> None
        Return the monitored location associated with spec

        """
        key = ((spec[0]['locator'], spec[0]['version']), spec[1], spec[2])
        if key in self.monitoredPipelines:
            self.monitoredPipelines[key].append(value)
        else:
            self.monitoredPipelines[key] = [value]

    def newSheetAction(self):
        """ newSheetAction() -> QAction
        Return the 'New Sheet' action

        """
        if not hasattr(self, 'newSheetActionVar'):
            icon = QtGui.QIcon(':/images/newsheet.png')
            self.newSheetActionVar = QtGui.QAction(icon, '&New sheet', self)
            self.newSheetActionVar.setToolTip('Create a new sheet')
            self.newSheetActionVar.setStatusTip('Create and show a new sheet')
            self.newSheetActionVar.setShortcut(QtGui.QKeySequence('Ctrl+N'))
            self.connect(self.newSheetActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.newSheetActionTriggered)
        return self.newSheetActionVar

    def deleteSheetAction(self):
        """ deleteSheetAction() -> QAction
        Return the 'Delete Sheet' action:

        """
        if not hasattr(self, 'deleteSheetActionVar'):
            icon = QtGui.QIcon(':/images/deletesheet.png')
            self.deleteSheetActionVar = QtGui.QAction(icon, '&Delete sheet',
                                                      self)
            self.deleteSheetActionVar.setToolTip('Delete the current sheet')
            self.deleteSheetActionVar.setStatusTip('Delete the current sheet '
                                                   'if there are more than one')
            key = QtGui.QKeySequence('Ctrl+Backspace')
            self.deleteSheetActionVar.setShortcut(key)
            self.connect(self.deleteSheetActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.deleteSheetActionTriggered)
        return self.deleteSheetActionVar

    def showNextTabAction(self):
        """ showNextTabAction() -> QAction
        Return the 'Next Sheet' action

        """
        if not hasattr(self, 'showNextTabActionVar'):
            icon = QtGui.QIcon(':/images/forward.png')
            self.showNextTabActionVar = QtGui.QAction(icon, '&Next sheet', self)
            self.showNextTabActionVar.setToolTip('Show the next sheet')
            self.showNextTabActionVar.setStatusTip('Show the next sheet if it '
                                                   'is available')
            self.showNextTabActionShortcut = QtGui.QShortcut(self)
            self.showNextTabActionVar.setShortcut('Ctrl+PgDown')
            self.connect(self.showNextTabActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showNextTab)
        return self.showNextTabActionVar

    def showPrevTabAction(self):
        """ showPrevTabAction() -> QAction
        Return the 'Prev Sheet' action

        """
        if not hasattr(self, 'showPrevTabActionVar'):
            icon = QtGui.QIcon(':/images/back.png')
            self.showPrevTabActionVar = QtGui.QAction(icon, '&Prev sheet', self)
            self.showPrevTabActionVar.setToolTip('Show the previous sheet')
            self.showPrevTabActionVar.setStatusTip('Show the previous sheet if '
                                                   'it is available')
            self.showPrevTabActionVar.setShortcut('Ctrl+PgUp')
            self.connect(self.showPrevTabActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showPrevTab)
        return self.showPrevTabActionVar

    def saveAction(self):
        """ saveAction() -> QAction
        Return the 'Save' action

        """
        if not hasattr(self, 'saveActionVar'):
            self.saveActionVar = QtGui.QAction(QtGui.QIcon(':/images/save.png'),
                                               '&Save', self)
            self.saveActionVar.setStatusTip('Save the current spreadsheet')
            self.saveActionVar.setShortcut('Ctrl+S')
            self.connect(self.saveActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.saveSpreadsheet)
        return self.saveActionVar

    def saveAsAction(self):
        """ saveAsAction() -> QAction
        Return the 'Save As...' action

        """
        if not hasattr(self, 'saveAsActionVar'):
            icon = QtGui.QIcon(':/images/saveas.png')
            self.saveAsActionVar = QtGui.QAction(icon, 'Save &As...', self)
            self.saveAsActionVar.setStatusTip('Save the current spreadsheet '
                                              'at a new location')
            self.connect(self.saveAsActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.saveSpreadsheetAs)
        return self.saveAsActionVar

    def openAction(self):
        """ openAction() -> QAction
        Return the 'Open...' action

        """
        if not hasattr(self, 'openActionVar'):
            self.openActionVar = QtGui.QAction(QtGui.QIcon(':/images/open.png'),
                                               '&Open...', self)
            self.openActionVar.setStatusTip('Open a saved spreadsheet')
            self.openActionVar.setShortcut('Ctrl+O')
            self.connect(self.openActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.openSpreadsheetAs)
        return self.openActionVar

    def exportSheetToImageAction(self):
        """ exportSheetToImageAction() -> QAction
        Export the current sheet to an image

        """
        if not hasattr(self, 'exportSheetToImageVar'):
            self.exportSheetToImageVar = QtGui.QAction('Export Sheet', self)
            self.exportSheetToImageVar.setStatusTip(
                'Export all cells in the spreadsheet to a montaged image')

            exportMenu = QtGui.QMenu(self)
            singleAction = exportMenu.addAction('As a Single Image')
            multiAction = exportMenu.addAction('Separately')
            self.exportSheetToImageVar.setMenu(exportMenu)

            self.connect(self.exportSheetToImageVar,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.exportSheetToSingleImageActionTriggered)

            self.connect(singleAction,
                         QtCore.SIGNAL('triggered()'),
                         self.exportSheetToSingleImageActionTriggered)
            self.connect(multiAction,
                         QtCore.SIGNAL('triggered()'),
                         self.exportSheetToSeparateImagesActionTriggered)
        return self.exportSheetToImageVar

    def exportSheetToSingleImageActionTriggered(self, action=None):
        """ exportSheetToSingleImageActionTriggered() -> None
        Exports the sheet as a big image
        """
        filename = QtGui.QFileDialog.getSaveFileName(
            self, "Select a File to Export the Sheet",
            ".", "Images (*.png *.xpm *.jpg)")
        if filename:
            self.currentWidget().exportSheetToImage(filename)

    def exportSheetToSeparateImagesActionTriggered(self, action=None):
        """ exportSheetToSeparateImagesActionTriggered() -> None
        Exports the cells as separate images
        """
        dirname = QtGui.QFileDialog.getExistingDirectory(
            self, 'Select a Directory to Export Images', ".",
            QtGui.QFileDialog.ShowDirsOnly)
        if dirname:
            self.currentWidget().exportSheetToImages(dirname)

    def newSheetActionTriggered(self, checked=False):
        """ newSheetActionTriggered(checked: boolean) -> None
        Actual code to create a new sheet

        """
        self.setCurrentIndex(self.addTabWidget(StandardWidgetSheetTab(self),
                                               'Sheet %d' % (self.count()+1)))
        self.currentWidget().sheet.stretchCells()

    def tabInserted(self, index):
        """tabInserted(index: int) -> None
        event handler to get when sheets are inserted """
        self.deleteSheetAction().setEnabled(True)
        self.saveAction().setEnabled(True)
        self.saveAsAction().setEnabled(True)

    def tabRemoved(self, index):
        """tabInserted(index: int) -> None
        event handler to get when sheets are removed """
        if self.count() == 0:
            self.deleteSheetAction().setEnabled(False)
            self.saveAction().setEnabled(False)
            self.saveAsAction().setEnabled(False)

    def removeSheetReference(self, sheet):
        """ removeSheetReference(sheet: StandardWidgetSheetTab) -> None
        Remove references of a sheet from the spreadsheet
        """
        for (code, locations) in self.monitoredPipelines.iteritems():
            for lid in reversed(xrange(len(locations))):
                if sheet==locations[lid][0]:
                    del locations[lid]

    def deleteSheetActionTriggered(self, checked=False):
        """ deleteSheetActionTriggered(checked: boolean) -> None
        Actual code to delete the current sheet

        """
        if self.count()>0:
            widget = self.currentWidget()
            self.tabWidgets.remove(widget)
            self.removeTab(self.currentIndex())
            self.removeSheetReference(widget)
            widget.deleteAllCells()
            widget.deleteLater()
            QtCore.QCoreApplication.processEvents()
            gc.collect()

    def clearTabs(self):
        """ clearTabs() -> None
        Clear and reset the controller

        """
        self.executedPipelines = [[], {}, {}]
        while self.count()>0:
            self.deleteSheetActionTriggered()
        for i in reversed(range(len(self.tabWidgets))):
            t = self.tabWidgets[i]
            del self.tabWidgets[i]
            self.removeSheetReference(t)
            t.deleteAllCells()
            t.deleteLater()

    def insertTab(self, idx, tabWidget, tabText):
        """ insertTab(idx: int, tabWidget: QWidget, tabText: str)
                      -> QTabWidget
        Redirect insertTab command to operatingWidget, this can either be a
        QTabWidget or a QStackedWidget

        """
        if self.operatingWidget!=self:
            ret = self.operatingWidget.insertWidget(idx, tabWidget)
            self.operatingWidget.setCurrentIndex(ret)
            return ret
        else:
            return QtGui.QTabWidget.insertTab(self, idx, tabWidget, tabText)

    def findSheet(self, sheetReference):
        """ findSheet(sheetReference: subclass(SheetReference)) -> Sheet widget
        Find/Create a sheet that meets a certen sheet reference

        """
        if not sheetReference:
            return None
        sheetReference.clearCandidate()
        for idx in xrange(len(self.tabWidgets)):
            tabWidget = self.tabWidgets[idx]
            tabLabel = tabWidget.windowTitle()
            sheetReference.checkCandidate(tabWidget, tabLabel, idx,
                                          self.operatingWidget.currentIndex())
        return sheetReference.setupCandidate(self)

    def changeTabText(self, tabIdx, newTabText):
        """ changeTabText(tabIdx: int, newTabText: str) -> None
        Update window title on the operating widget when the tab text
        has changed

        """
        self.operatingWidget.widget(tabIdx).setWindowTitle(newTabText)

    def moveTab(self, tabIdx, destination):
        """ moveTab(tabIdx: int, destination: int) -> None
        Move a tab at tabIdx to a different position at destination

        """
        if (tabIdx<0 or tabIdx>self.count() or
            destination<0 or destination>self.count()):
            return
        tabText = self.tabText(tabIdx)
        tabWidget = self.widget(tabIdx)
        self.removeTab(tabIdx)
        self.insertTab(destination, tabWidget, tabText)
        if tabIdx==self.currentIndex():
            self.setCurrentIndex(destination)

    def splitTab(self, tabIdx, pos=None):
        """ splitTab(tabIdx: int, pos: QPoint) -> None
        Split a tab to be  a stand alone window and move to position pos

        """
        if tabIdx<0 or tabIdx>self.count() or self.count()==0:
            return
        tabWidget = self.widget(tabIdx)
        self.removeTab(tabIdx)

        frame = StandardTabDockWidget(tabWidget.windowTitle(), tabWidget,
                                      self.tabBar(), self)
        if pos:
            frame.move(pos)
        frame.show()
        self.floatingTabWidgets.append(frame)

    def mergeTab(self, frame, tabIdx):
        """ mergeTab(frame: StandardTabDockWidget, tabIdx: int) -> None
        Merge a tab dock widget back to the controller at position tabIdx

        """
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

    def addTabWidget(self, tabWidget, sheetLabel):
        """ addTabWidget(tabWidget: QWidget, sheetLabel: str) -> int
        Add a new tab widget to the controller

        """
        return self.insertTabWidget(-1, tabWidget, sheetLabel)

    def insertTabWidget(self, index, tabWidget, sheetLabel):
        """ insertTabWidget(index: int, tabWidget: QWidget, sheetLabel: str)
                            -> int
        Insert a tab widget to the controller at some location

        """
        if sheetLabel==None:
            sheetLabel = 'Sheet %d' % (len(self.tabWidgets)+1)
        if not tabWidget in self.tabWidgets:
            self.tabWidgets.append(tabWidget)
            tabWidget.setWindowTitle(sheetLabel)
        return self.insertTab(index, tabWidget, sheetLabel)

    def tabWidgetUnderMouse(self):
        """ tabWidgetUnderMouse() -> QWidget
        Return the tab widget that is under mouse, hide helpers for the rest

        """
        result = None
        for t in self.tabWidgets:
            if t.underMouse():
                result = t
            else:
                t.showHelpers(False, QtCore.QPoint(-1,-1))
        return result

    def setupFullScreenWidget(self, fs, stackedWidget):
        """ setupFullScreenWidget(fs: boolean, stackedWidget: QStackedWidget)
                                  -> None
        Prepare(fs=True)/Clean(fs=False) up full screen mode

        """
        if fs:
            idx = self.currentIndex()
            for i in xrange(self.count()):
                widget = self.widget(0)
                self.removeTab(0)
                self.tabTrueParent = widget.parent()
                widget.setParent(stackedWidget)
                stackedWidget.addWidget(widget)
            stackedWidget.setCurrentIndex(idx)
            self.operatingWidget = stackedWidget
        else:
            idx = stackedWidget.currentIndex()
            for i in xrange(stackedWidget.count()):
                widget = stackedWidget.widget(0)
                stackedWidget.removeWidget(widget)
                widget.setParent(self.tabTrueParent)
                self.addTab(widget, widget.windowTitle())
            self.setCurrentIndex(idx)
            self.operatingWidget = self

    def showNextTab(self):
        """ showNextTab() -> None
        Bring the next tab up

        """
        if self.operatingWidget.currentIndex()<self.operatingWidget.count()-1:
            index = self.operatingWidget.currentIndex()+1
            self.operatingWidget.setCurrentIndex(index)

    def showPrevTab(self):
        """ showPrevTab() -> None
        Bring the previous tab up

        """
        if self.operatingWidget.currentIndex()>0:
            index = self.operatingWidget.currentIndex()-1
            self.operatingWidget.setCurrentIndex(index)

    def tabPopupMenu(self):
        """ tabPopupMenu() -> QMenu
        Return a menu containing a list of all tabs

        """
        menu = QtGui.QMenu(self)
        en = self.operatingWidget.currentIndex()<self.operatingWidget.count()-1
        self.showNextTabAction().setEnabled(en)
        menu.addAction(self.showNextTabAction())
        en = self.operatingWidget.currentIndex()>0
        self.showPrevTabAction().setEnabled(en)
        menu.addAction(self.showPrevTabAction())
        menu.addSeparator()
        for idx in xrange(self.operatingWidget.count()):
            t = self.operatingWidget.widget(idx)
            action = menu.addAction(t.windowTitle())
            action.setData(idx)
            if t==self.operatingWidget.currentWidget():
                action.setIcon(QtGui.QIcon(':/images/ok.png'))
        menu.addAction(self.parent().parent().fullScreenAction())
        return menu

    def showPopupMenu(self):
        """ showPopupMenu() -> None
        Activate the tab list and show the popup menu

        """
        menu = self.tabPopupMenu()
        action = menu.exec_(QtGui.QCursor.pos())
        self.showNextTabAction().setEnabled(True)
        self.showPrevTabAction().setEnabled(True)
        if not action: return
        if not action in self.actions():
            self.operatingWidget.setCurrentIndex(action.data()[0])
        menu.deleteLater()

    def changeSpreadsheetFileName(self, fileName):
        """ changeSpreadsheetFileName(fileName: str) -> None
        Change the current spreadsheet filename and reflect it on the
        window title

        """
        self.spreadsheetFileName = fileName
        if self.spreadsheetFileName:
            displayName = self.spreadsheetFileName
        else:
            displayName = 'Untitled'
        self.emit(QtCore.SIGNAL('needChangeTitle'),
                  '%s - VisTrails Spreadsheet' % displayName)

    def pipelineId(self, pipelineInfo):
        return (pipelineInfo['controller'], pipelineInfo['version'])

    def addPipeline(self, pipelineInfo):
        """ addPipeline(pipelineInfo: dict) -> None
        Add vistrail pipeline executions to history

        """
        vistrail = self.pipelineId(pipelineInfo)
        self.executedPipelines[0].append(vistrail)
        if not vistrail in self.executedPipelines[1]:
            self.executedPipelines[1][vistrail] = 0
        else:
            self.executedPipelines[1][vistrail] += 1
        self.executedPipelines[2][vistrail] = 0

    def getCurrentPipelineId(self, pipelineInfo):
        """ getCurrentPipelineId(pipelineInfo: dict) -> Int
        Get the current pipeline id

        """
        vistrail = self.pipelineId(pipelineInfo)
        return self.executedPipelines[1][vistrail]

    def increasePipelineCellId(self, pipelineInfo):
        """ increasePipelineCellId(pipelineInfo: dict) -> int
        Increase the current cell pipeline id

        """
        vistrail = self.pipelineId(pipelineInfo)
        cid = self.executedPipelines[2][vistrail]
        self.executedPipelines[2][vistrail] += 1
        return cid

    def getCurrentPipelineCellId(self, pipelineInfo):
        """ getCurrentPipelineCellId(pipelineInfo: dict) -> int
        Get current pipeline cell id

        """
        vistrail = self.pipelineId(pipelineInfo)
        return self.executedPipelines[2][vistrail]

    def addPipelineCell(self, pipelineInfo):
        """ addPipelineCell(pipelineInfo: dict) -> None
        Add vistrail pipeline executions to history

        """
        vistrail = self.pipelineId(pipelineInfo)
        self.executedPipelines[0].append(vistrail)
        if not vistrail in self.executedPipelines[1]:
            self.executedPipelines[1][vistrail] = 0
        else:
            self.executedPipelines[1][vistrail] += 1


    def saveSpreadsheet(self, fileName=None):
        """ saveSpreadsheet(fileName: str) -> None
        Save the current spreadsheet to a file if fileName is not
        None. Else, pop up a dialog to ask for a file name.

        """
        def serialize_locator(locator):
            wrapper = XMLWrapper()
            dom = wrapper.create_document('spreadsheet_locator')
            root = dom.documentElement
            root.setAttribute("version", "1.0")
            locator.serialize(dom,root)
            return dom.toxml()

        def need_save():
            from vistrails.gui.vistrails_window import _app
            need_save_vt = False
            for t in self.tabWidgets:
                dim = t.getDimension()
                for r in xrange(dim[0]):
                    for c in xrange(dim[1]):
                        info = t.getCellPipelineInfo(r,c)
                        if info:
                            controller = info[0]['controller']
                            view = _app.ensureController(controller)
                            if view:
                                controller = view.get_controller()
                                if controller.changed:
                                    need_save_vt = True
            return need_save_vt

        if need_save():
            show_warning('Save Spreadsheet', 'Please save your vistrails and try again.')
            return

        if fileName==None:
            fileName = self.spreadsheetFileName
        if fileName:
            indexFile = open(fileName, 'w')
            indexFile.write(str(len(self.tabWidgets))+'\n')
            for t in self.tabWidgets:
                dim = t.getDimension()
                sheet = spreadsheetRegistry.getSheetByType(type(t))
                indexFile.write('%s\n'%str((str(t.windowTitle()),
                                            sheet,
                                            dim[0], dim[1])))
                for r in xrange(dim[0]):
                    for c in xrange(dim[1]):
                        info = t.getCellPipelineInfo(r,c)
                        if info:
                            newinfo0 = copy.copy(info[0])
                            newinfo0['pipeline'] = None
                            newinfo0['actions'] = []
                            newinfo0['locator'] = \
                                          serialize_locator(newinfo0['controller'].locator)
                            newinfo0['controller'] = None
                            indexFile.write('%s\n'
                                            %str((r, c,
                                                  newinfo0,
                                                  info[1], info[2])))
                indexFile.write('---\n')
            indexFile.write(str(len(self.executedPipelines[0]))+'\n')
            for vistrail in self.executedPipelines[0]:
                indexFile.write('%s\n'%str((serialize_locator(vistrail[0].locator),
                                            vistrail[1])))
            self.changeSpreadsheetFileName(fileName)
            indexFile.close()
        else:
            self.saveSpreadsheetAs()

    def saveSpreadsheetAs(self):
        """ saveSpreadsheetAs() -> None
        Asking a file name before saving the spreadsheet

        """
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Choose a spreadsheet '
                                                     'name',
                                                     '',
                                                     'VisTrails Spreadsheet '
                                                     '(*.vss)')
        if fileName:
            (root, ext) = os.path.splitext(fileName)
            if ext=='':
                fileName += '.vss'
            self.saveSpreadsheet(fileName)

    def openSpreadsheet(self, fileName):
        """ openSpreadsheet(fileName: str) -> None
        Open a saved spreadsheet assuming that all VTK files must exist and have
        all the version using the saved spreadsheet

        """
        def parse_locator(text):
            locator = None
            wrapper = XMLWrapper()
            dom = wrapper.create_document_from_string(text)
            root = dom.documentElement
            version = None
            version = root.getAttribute('version')
            if version == '1.0':
                for element in named_elements(root, 'locator'):
                    if str(element.getAttribute('type')) == 'file':
                        locator = FileLocator.parse(element)
                    elif str(element.getAttribute('type')) == 'db':
                        locator = DBLocator.parse(element)
            return locator
        locators = {}
        indexFile = open(fileName, 'r')
        contents = indexFile.read()
        self.clearTabs()
        lidx = 0
        lines = contents.split('\n')
        tabCount = int(lines[lidx])
        lidx += 1
        for tabIdx in xrange(tabCount):
            # FIXME: eval should pretty much never be used
            tabInfo = literal_eval(lines[lidx])
            lidx += 1
            sheet = spreadsheetRegistry.getSheet(tabInfo[1])(self)
            sheet.setDimension(tabInfo[2], tabInfo[3])
            self.addTabWidget(sheet, tabInfo[0])
            while lines[lidx]!='---':
                (r, c, vistrail, pid, cid) = literal_eval(lines[lidx])
                locator = vistrail['locator']
                if locators.has_key(locator):
                    vistrail['locator'] = locators[locator]
                else:
                    locators[locator] = parse_locator(vistrail['locator'])
                    vistrail['locator'] = locators[locator]
                self.appendMonitoredLocations((vistrail, pid, cid),
                                              (sheet, r, c))
                lidx += 1
            lidx += 1
        pipelineCount = int(lines[lidx])
        lidx += 1
        self.loadingMode = True
        progress = QtGui.QProgressDialog("Loading spreadsheet...",
                                         "&Cancel", 0, pipelineCount,
                                         self,
                                         QtCore.Qt.WindowStaysOnTopHint
                                         )
        progress.show()
        for pipelineIdx in xrange(pipelineCount):
            # FIXME: eval should pretty much never be used
            (serializedLocator, version) = literal_eval(lines[lidx])
            try:
                locator = locators[serializedLocator]
            except KeyError:
                locator = parse_locator(serializedLocator)
            if locator:
                bundle = locator.load()
                if isinstance(bundle, SaveBundle):
                    pipeline = bundle.vistrail.getPipeline(version)
                else:
                    pipeline = bundle.getPipeline(version)
                execution = get_default_interpreter()
                progress.setValue(pipelineIdx)
                QtCore.QCoreApplication.processEvents()
                if progress.wasCanceled():
                    break
                kwargs = {'locator': locator,
                          'current_version': version,
                          'view': DummyView(),
                          }
                execution.execute(pipeline, **kwargs)
            else:
                raise RuntimeError("Couldn't load spreadsheet")
            lidx += 1
        progress.setValue(pipelineCount)
        QtCore.QCoreApplication.processEvents()
        self.changeSpreadsheetFileName(fileName)
        self.loadingMode = False
        indexFile.close()

    def openSpreadsheetAs(self):
        """ openSpreadsheetAs() -> None
        Open a saved spreadsheet and set its filename in the dialog box

        """
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Choose a spreadsheet',
                                                     '',
                                                     'VisTrails Spreadsheet '
                                                     '(*.vss)',
                                                     )
        if fileName:
            self.openSpreadsheet(fileName)

    def cleanup(self):
        """ cleanup() -> None
        Clear reference of non-collectable objects/temp files for gc

        """
        self.clearTabs()

    def setEditingMode(self, editing=True):
        """ setEditingMode(editing: bool) -> None
        Turn on/off the editing mode of the whole spreadsheet

        """
        self.editingMode = editing
        for w in self.tabWidgets:
            w.setEditingMode(editing)
