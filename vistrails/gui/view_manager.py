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
from core.vistrail.vistrail import Vistrail
import db.services.io

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
        self.activeIndex = -1
        
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

        self._views = {}

    def addVistrailView(self, view):
        """ addVistrailView(view: QVistrailView) -> None
        Add a vistrail view to the tab, and connect to the right signals
        
        """
        self._views[view] = view.controller
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
        self.connect(view.versionTab,
                     QtCore.SIGNAL('versionSelectionChange'),
                     self.versionSelectionChange)
        self.connect(view.versionTab,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.vistrailChanged)
        self.connect(view.queryTab,
                     QtCore.SIGNAL('queryPipelineChange'),
                     self.queryPipelineChange)
        self.emit(QtCore.SIGNAL('vistrailViewAdded'), view)
        if self.count()==1:
            self.emit(QtCore.SIGNAL('currentChanged(int)'), 0)

    def removeVistrailView(self, view):
        """ removeVistrailView(view: QVistrailView) -> None
        Remove the current vistrail view and destroy it
        
        """
        if view:
            del self._views[view]
            view.removeEventFilter(self)
            self.disconnect(view.pipelineTab,
                            QtCore.SIGNAL('moduleSelectionChange'),
                            self.moduleSelectionChange)
            self.disconnect(view.versionTab,
                            QtCore.SIGNAL('versionSelectionChange'),
                            self.versionSelectionChange)
            self.disconnect(view.versionTab,
                            QtCore.SIGNAL('vistrailChanged()'),
                            self.vistrailChanged)
            self.emit(QtCore.SIGNAL('vistrailViewRemoved'), view)
            index = self.indexOf(view) 
            if index !=-1:
                self.removeTab(self.currentIndex())
                if self.currentIndex()  >= 0:
                    self.updateViewMenu(self.currentIndex(), -1)
                self.activeIndex = self.currentIndex()
            elif self.splittedViews.has_key(view):
                del self.splittedViews[view]
            view.controller.cleanup()
            view.close()
            view.deleteLater()

    def moduleSelectionChange(self, selection):
        """ moduleSelectionChange(selection: list[id]) -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('moduleSelectionChange'), selection)

    def versionSelectionChange(self, versionId):
        """ versionSelectionChange(versionId: int) -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('versionSelectionChange'), versionId)

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('vistrailChanged()'))

    def queryPipelineChange(self, notEmpty):
        """ versionSelectionChange(notEmpty: bool) -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('queryPipelineChange'), notEmpty)

    def copySelection(self):
        """ copySelection() -> None
        Copy the current selected pipeline modules
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().copySelection()

    def currentView(self):
        """currentView() -> VistrailView. Returns the current vistrail view."""
        return self.currentWidget()

    def pasteToCurrentPipeline(self):
        """ pasteToCurrentPipeline() -> None
        Paste what is on the clipboard to the current pipeline
        
        """        
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().pasteFromClipboard()

    def selectAllModules(self):
        """ selectAllModules() -> None
        Select all modules in the current view
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().selectAll()

    def canSelectAll(self):
        """ canSelectAll() -> bool        
        Check to see if there is any module in the pipeline view to be
        selected
        
        """
        vistrailView = self.currentWidget()
        if vistrailView and vistrailView.controller.currentPipeline:
            return len(vistrailView.controller.currentPipeline.modules)>0
        return False

    def redo(self):
        """ redo() -> none
        Performs a redo step.

        """
        vistrailView = self.currentWidget()
        if not vistrailView:
            return
        new_version = vistrailView.redo()
        self.emit(QtCore.SIGNAL('versionSelectionChange'), new_version)

    def undo(self):
        """ undo() -> None
        Performs an undo step.

        """
        vistrailView = self.currentWidget()
        if not vistrailView:
            return
        new_version = vistrailView.undo()
        self.emit(QtCore.SIGNAL('versionSelectionChange'), new_version)

    def newVistrail(self):
        """ newVistrail() -> None
        Create a new vistrail with no name
        
        """
        vistrailView = QVistrailView()
        vistrailView.setVistrail(Vistrail())
        self.addVistrailView(vistrailView)
        self.setCurrentWidget(vistrailView)
        vistrailView.setInitialView()
        vistrailView.versionTab.vistrailChanged()

    def close_first_vistrail_if_necessary(self):
        # Close first vistrail of no change was made
        if not self._first_view:
            return
        vt = self._first_view.controller.vistrail
        if vt.get_version_count() == 0:
            self.closeVistrail(self._first_view)
            self._first_view = None
        else:
            # We set it to none, since it's been changed, so
            # we don't want to ever close it again.
            self._first_view = None

    def setVistrailView(self, vistrail, name, origin='FILESYSTEM', conn_id=-1):
        """setVistrailView(vistrai: Vistrail, name: String, origin: str)
                          -> QVistrailView
        Sets a new vistrail view for the vistrail object
        origin can be 'FILESYSTEM' or 'DB'
        """
        vistrailView = QVistrailView()
        vistrailView.setVistrail(vistrail, name)
        vistrailView.origin = origin
        vistrailView.conn_id = conn_id
        self.addVistrailView(vistrailView)
        self.setCurrentWidget(vistrailView)
        vistrailView.controller.inspectAndImportModules()        
        # Make sure to select the latest time step
        vistrailView.controller.selectLatestVersion()
        vistrailView.versionTab.vistrailChanged()
        
        return vistrailView
    
    def openVistrail(self, fileName):
        """ openVistrail(fileName) -> QVistrailView
        Open a new vistrail and return a QVistrailView        
        
        """
        self.close_first_vistrail_if_necessary()
        view = self.ensureVistrailFile(fileName)
        if view:
            return view
        try:
            vistrail = db.services.io.openVistrailFromXML(fileName)
            Vistrail.convert(vistrail)
            return self.setVistrailView(vistrail,fileName)
        
        except Exception, e:
            QtGui.QMessageBox.critical(None,
                                       'Vistrails',
                                       str(e))

    def openVistrailFromDB(self, config, vt_id):
        """openVistrailFromDB(config: dict, vt_id: int) -> QVistrailView
        Open a new vistrail and return a QVistrailView
        
        """
        self.close_first_vistrail_if_necessary()
        view = self.ensureVistrailDB(config, vt_id)
        if view:
            return view
        id = -1
        
        try:
            if config.has_key('id'):
                id = config['id']
            vistrail = db.services.io.open_from_db(config, vt_id)
            Vistrail.convert(vistrail)
            
            return self.setVistrailView(vistrail,vistrail.db_name,'DB',id)
        
        except Exception, e:
            QtGui.QMessageBox.critical(None,
                                       'Vistrails',
                                       str(e))
            
    def saveVistrailFile(self, vistrailView=None, fileName=''):
        """ saveVistrail(vistrailView: QVistrailView) -> Bool
        Save the current active vistrail to a file
        It returns True if file was written successfully.
        
        """
        if not vistrailView:
            vistrailView = self.currentWidget()
        if vistrailView:
            if fileName=='':
                fileName = vistrailView.controller.fileName
            if fileName=='':
                fileName = QtGui.QFileDialog.getSaveFileName(
                    self,
                    "Save Vistrail...",
                    system.vistrails_directory(),
                    "Vistrail files (*.xml)\nOther files (*)")
            if fileName!='' and fileName!=None:
                vistrailView.controller.writeVistrail(str(fileName))
                vistrailView.origin == 'FILESYSTEM'
                return True
            else:
                return False
            
    def saveVistrailDB(self, vistrailView=None, name='', config=None):
        """saveVistrailDB(vistrailView: QVistrailView) -> Boolean
        Save vistrailView or the current active vistrail to the database
        It returns True if the operation was successful
        
        """
        if not vistrailView:
            vistrailView = self.currentWidget()
        if vistrailView:
            if name == '':
                name = vistrailView.controller.fileName
            if name == '':
                ok = False
                name = QtGui.QInputDialog.getText(self,
                                                  "Save Vistrail...",
                                                  "Vistrail name:",
                                                  QtGui.QLineEdit.Normal,
                                                  "",
                                                  ok)
                
            if name != '' and name != None:
                if config != None:
                    if config.has_key('id'):
                        vistrailView.conn_id = config['id']
                    
                vistrailView.controller.writeVistrailDB(vistrailView.conn_id,
                                                        name)        
                vistrailView.origin == 'DB'
                return True
            else:
                return False
            
    def saveVistrail(self, vistrailView=None, fileName=''):
        """ saveVistrail(vistrailView: QVistrailView) -> Bool
        Save the current active vistrail to a file
        It returns True if file was written successfully.
        
        """
        if not vistrailView:
            vistrailView = self.currentWidget()
        if vistrailView:
            if vistrailView.origin == 'FILESYSTEM':
                return self.saveVistrailFile(vistrailView,fileName)
            elif vistrailView.origin == 'DB':
                return self.saveVistrailDB(vistrailView)
            
                
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
                return self.saveVistrail(vistrailView)
            elif res == 2:
                return False
            self.removeVistrailView(vistrailView)
            if self.count()==0:
                self.emit(QtCore.SIGNAL('currentVistrailChanged'), None)
        if vistrailView == self._first_view:
            self._first_view = None
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
        self.updateViewMenu(index, -1)
        self.activeIndex = index
        self.emit(QtCore.SIGNAL('currentVistrailChanged'),
                  self.currentWidget())

    def updateViewMenu(self, index, internal_index):
        """updateViewMenu(index: int, internal_index:int) -> None
           Tell previous tab to remove menu entries and current tab to
           add menu entries
           internal_index indicates which tab will be the current tab of
           the vistrail view.
           
        """
        if (self.activeIndex != -1 and self.count() > 1
            and self.activeIndex < self.count()) :
            previousTab = self.widget(self.activeIndex)
            previousTab.updateViewMenu(internal_index)
            previousTab.activeIndex = -1
        if index != -1 and self.count() > 0:
            currentTab = self.widget(index)
            currentTab.updateViewMenu()
        
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

    def executeCurrentPipeline(self):
        """ executeCurrentPipeline() -> None
        Execute the active pipeline if exists
        
        """
        view = self.currentView()
        if view:
            view.toolBar.executePipelineAction().trigger()
        
    def ensureVistrailFile(self, filename):
        """ ensureVistrailFile(filename: str) -> QVistrailView        
        This will first find among the opened vistrails to see if
        'filename' has been opened. If not, it will return None.
        
        """
        for view in self.splittedViews.keys():
            if view.controller.fileName==filename:
                self.setCurrentWidget(view)
                return view
        for i in range(self.count()):
            view = self.widget(i)
            if view.controller.fileName==filename:
                self.setCurrentWidget(view)
                return view
        return None

    def ensureVistrailDB(self, config, vt_id):
        """ ensureVistrailDB(config: dict, vt_id: int) -> QVistrailView        
        This will first find among the opened vistrails to see if
        vt_id from config has been opened. If not, it will return None.
        
        """
        for view in self.splittedViews.keys():
            vt = view.controller.vistrail
            if vt.db_id == vt_id:
                if(vt.db_dbHost == config['host'] and
                   vt.db_dbPort == config['port'] and
                   vt.db_dbName == config['db']):
                    self.setCurrentWidget(view)
                    return view
        for i in range(self.count()):
            view = self.widget(i)
            vt = view.controller.vistrail
            if vt.db_id == vt_id:
                if(vt.db_dbHost == config['host'] and
                   vt.db_dbPort == config['port'] and
                   vt.db_dbName == config['db']):
                    self.setCurrentWidget(view)
                    return view
        return None
    
    def set_first_view(self, view):
        self._first_view = view
