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
""" File for the builder window, the workspace of Vistrails

QBuilderWindow
"""
from PyQt4 import QtCore, QtGui
from core import system
from gui.bookmark_window import QBookmarksWindow
from gui.graphics_view import QInteractiveGraphicsView
from gui.module_palette import QModulePalette
from gui.open_db_window import QOpenDBWindow
from gui.preferences import QPreferencesDialog
from gui.shell import QShellDialog
from gui.theme import CurrentTheme
from gui.view_manager import QViewManager
from gui.vistrail_toolbar import QVistrailViewToolBar
from gui.preferences import QPreferencesDialog
from gui.vis_diff import QVisualDiff
from db.services.io import XMLFileLocator, DBLocator
import copy
import core.interpreter.cached
import os
import sys

################################################################################

class QBuilderWindow(QtGui.QMainWindow):
    """
    QBuilderWindow is a main widget containing an editin area for
    VisTrails and several tool windows. Also remarks that almost all
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
        
        self.bookmarksWindow = QBookmarksWindow(parent=self)
        
        self.viewIndex = 0
        
        self.createActions()
        self.createMenu()
        self.createToolBar()

        self.connectSignals()

        self.shell = None
        self.newVistrailAction.trigger()

        self.viewManager.set_first_view(self.viewManager.currentView())
        
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

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None        
        Capture modifiers (Ctrl, Alt, Shift) and send them to one of
        the widget under the mouse cursor. It first starts at the
        widget directly under the mouse and check if the widget has
        property named captureModifiers. If yes, it calls
        'modifiersPressed' function
        
        """
        if event.key() in [QtCore.Qt.Key_Control,
                           QtCore.Qt.Key_Alt,
                           QtCore.Qt.Key_Shift,
                           QtCore.Qt.Key_Meta]:
            widget = QtGui.QApplication.widgetAt(QtGui.QCursor.pos())
            if widget:
                while widget:
                    if widget.property('captureModifiers').isValid():
                        if hasattr(widget, 'modifiersPressed'):
                            widget.modifiersPressed(event.modifiers())
                        break
                    widget = widget.parent()
        QtGui.QMainWindow.keyPressEvent(self, event)
        # super(QBuilderWindow, self).keyPressEvent(event)
            
    def keyReleaseEvent(self, event):
        """ keyReleaseEvent(event: QKeyEvent) -> None
        Capture modifiers (Ctrl, Alt, Shift) and send them to one of
        the widget under the mouse cursor. It first starts at the
        widget directly under the mouse and check if the widget has
        property named captureModifiers. If yes, it calls
        'modifiersReleased' function
        
        """
        if event.key() in [QtCore.Qt.Key_Control,
                           QtCore.Qt.Key_Alt,
                           QtCore.Qt.Key_Shift,
                           QtCore.Qt.Key_Meta]:
            widget = QtGui.QApplication.widgetAt(QtGui.QCursor.pos())
            if widget:
                while widget:
                    if widget.property('captureModifiers').isValid():
                        if hasattr(widget, 'modifiersReleased'):
                            widget.modifiersReleased()
                        break
                    widget = widget.parent()
        QtGui.QMainWindow.keyReleaseEvent(self, event)
            
    def createActions(self):
        """ createActions() -> None
        Construct all menu/toolbar actions for builder window
        
        """
        self.newVistrailAction = QtGui.QAction(CurrentTheme.NEW_VISTRAIL_ICON,
                                               '&New', self)
        self.newVistrailAction.setShortcut('Ctrl+N')
        self.newVistrailAction.setStatusTip('Create a new Vistrail')
        
        self.openFileAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_ICON,
                                            '&Open', self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setStatusTip('Open an existing VisTrail from '
                                         'the filesystem')

        self.openDBAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_DB_ICON,
                                          '&Open', self)
        self.openDBAction.setShortcut('Ctrl+Shift+O')
        self.openDBAction.setStatusTip('Open an existing VisTrail from '
                                             'database')
        self.openVistrailDefaultAction = self.openFileAction
        
        self.saveFileAction = QtGui.QAction(CurrentTheme.SAVE_VISTRAIL_ICON,
                                                '&Save', self)
        self.saveFileAction.setShortcut('Ctrl+S')
        self.saveFileAction.setStatusTip('Save the current VisTrail')
        self.saveFileAction.setEnabled(False)
        
        self.saveFileAsAction = QtGui.QAction('Save as file...', self)
        self.saveFileAsAction.setShortcut('Ctrl+Shift+S')
        self.saveFileAsAction.setStatusTip('Save the current VisTrail at '
                                             'a different disk location')
        self.saveFileAsAction.setEnabled(False)

        self.saveDBAction = QtGui.QAction('Save to database...', self)
        self.saveDBAction.setStatusTip('Save the current VisTrail on '
                                             'the database')
        self.saveDBAction.setEnabled(False)

        self.closeVistrailAction = QtGui.QAction('Close', self)
        self.closeVistrailAction.setShortcut('Ctrl+W')
        self.closeVistrailAction.setStatusTip('Close the current VisTrail')
        self.closeVistrailAction.setEnabled(False)

        self.quitVistrailsAction = QtGui.QAction('Quit', self)
        self.quitVistrailsAction.setShortcut('Ctrl+Q')
        self.quitVistrailsAction.setStatusTip('Exit Vistrails')
       
        self.undoAction = QtGui.QAction('Undo', self)
        self.undoAction.setEnabled(False)
        self.undoAction.setStatusTip('Go back to the previous version')
        self.undoAction.setShortcut('Ctrl+Z')

        self.redoAction = QtGui.QAction('Redo', self)
        self.redoAction.setEnabled(False)
        self.redoAction.setStatusTip('Redo an undone version')
        self.redoAction.setShortcut('Ctrl+Y')

        self.copyAction = QtGui.QAction('Copy\tCtrl+C', self)
        self.copyAction.setEnabled(False)
        self.copyAction.setStatusTip('Copy selected modules in '
                                     'the current pipeline view')

        self.pasteAction = QtGui.QAction('Paste\tCtrl+V', self)
        self.pasteAction.setEnabled(False)
        self.pasteAction.setStatusTip('Paste copied modules in the clipboard '
                                      'into the current pipeline view')
        
        self.selectAllAction = QtGui.QAction('Select All\tCtrl+A', self)
        self.selectAllAction.setEnabled(False)
        self.selectAllAction.setStatusTip('Select all modules in '
                                          'the current pipeline view')

        self.editPreferencesAction = QtGui.QAction('Preferences...', self)
        self.editPreferencesAction.setEnabled(True)
        self.editPreferencesAction.setStatusTip('Edit system preferences')
        
        self.shellAction = QtGui.QAction(CurrentTheme.CONSOLE_MODE_ICON,
                                         'VisTrails Console', self)
        self.shellAction.setCheckable(True)
        self.shellAction.setShortcut('Ctrl+H')

        self.bookmarksAction = QtGui.QAction(CurrentTheme.BOOKMARKS_ICON,
                                             'Bookmarks', self)
        self.bookmarksAction.setCheckable(True)
        self.bookmarksAction.setShortcut('Ctrl+D')

        self.pipViewAction = QtGui.QAction('Picture-in-Picture', self)
        self.pipViewAction.setCheckable(True)
        self.pipViewAction.setChecked(True)

        self.methodsViewAction = QtGui.QAction('Methods Panel', self)
        self.methodsViewAction.setCheckable(True)
        self.methodsViewAction.setChecked(True)

        self.setMethodsViewAction = QtGui.QAction('Set Methods Panel', self)
        self.setMethodsViewAction.setCheckable(True)
        self.setMethodsViewAction.setChecked(True)

        self.propertiesViewAction = QtGui.QAction('Properties Panel', self)
        self.propertiesViewAction.setCheckable(True)
        self.propertiesViewAction.setChecked(True)

        self.helpAction = QtGui.QAction(self.tr('About VisTrails...'), self)

        a = QtGui.QAction(self.tr('Execute Current Workflow\tCtrl+Enter'),
                          self)
        self.executeCurrentWorkflowAction = a
        self.executeCurrentWorkflowAction.setEnabled(False)

        self.executeDiffAction = QtGui.QAction('Execute Version Difference', self)
        self.executeDiffAction.setEnabled(False)
        self.flushCacheAction = QtGui.QAction(self.tr('Erase Cache Contents'),
                                              self)

        self.executeQueryAction = QtGui.QAction('Execute Visual Query', self)
        self.executeQueryAction.setEnabled(False)

        self.executeExplorationAction = QtGui.QAction(
            'Execute Parameter Exploration', self)
        self.executeExplorationAction.setEnabled(False)

        self.executeShortcuts = [
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.ControlModifier +
                                               QtCore.Qt.Key_Return), self),
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.ControlModifier +
                                               QtCore.Qt.Key_Enter), self)
            ]
            
        
    def createMenu(self):
        """ createMenu() -> None
        Initialize menu bar of builder window
        
        """
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.newVistrailAction)
        self.openMenu = self.fileMenu.addMenu('Open...')
        self.openMenu.addAction(self.openFileAction)
        self.openMenu.addAction(self.openDBAction)
        #self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveFileAction)
        self.saveAsMenu = self.fileMenu.addMenu('Save As...')
        self.saveAsMenu.addAction(self.saveFileAsAction)
        self.saveAsMenu.addAction(self.saveDBAction)
        self.fileMenu.addAction(self.closeVistrailAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitVistrailsAction)

        self.editMenu = self.menuBar().addMenu('&Edit')
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.pasteAction)
        self.editMenu.addAction(self.selectAllAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.editPreferencesAction)
        
        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(self.bookmarksAction)
        self.viewMenu.addAction(self.shellAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.pipViewAction)
        self.viewMenu.addAction(
            self.modulePalette.toolWindow().toggleViewAction())
        self.viewMenu.addAction(self.methodsViewAction)
        self.viewMenu.addAction(self.setMethodsViewAction)
        self.viewMenu.addAction(self.propertiesViewAction)

        self.runMenu = self.menuBar().addMenu('&Run')
        self.runMenu.addAction(self.executeCurrentWorkflowAction)
        self.runMenu.addAction(self.executeDiffAction)
        self.runMenu.addAction(self.executeQueryAction)
        self.runMenu.addAction(self.executeExplorationAction)
        self.runMenu.addSeparator()
        self.runMenu.addAction(self.flushCacheAction)

        self.vistrailMenu = self.menuBar().addMenu('Vis&trail')
        self.vistrailMenu.menuAction().setEnabled(False)
        self.vistrailActionGroup = QtGui.QActionGroup(self)

        self.helpMenu = self.menuBar().addMenu('Help')
        self.helpMenu.addAction(self.helpAction)

    def createToolBar(self):
        """ createToolBar() -> None
        Create a default toolbar for this builder window
        
        """
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setWindowTitle('Vistrail File')
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolBar)
        self.toolBar.addAction(self.newVistrailAction)
        self.toolBar.addAction(self.openFileAction)
        self.toolBar.addAction(self.saveFileAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.bookmarksAction)

        self.viewToolBar = QVistrailViewToolBar(self)
        self.addToolBar(self.viewToolBar)

    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between various GUI components        
        
        """
        self.connect(self.viewManager,
                     QtCore.SIGNAL('moduleSelectionChange'),
                     self.moduleSelectionChange)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('versionSelectionChange'),
                     self.versionSelectionChange)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('execStateChange()'),
                     self.execStateChange)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('currentVistrailChanged'),
                     self.currentVistrailChanged)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.vistrailChanged)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('vistrailViewAdded'),
                     self.vistrailViewAdded)
        self.connect(self.viewManager,
                     QtCore.SIGNAL('vistrailViewRemoved'),
                     self.vistrailViewRemoved)
                     
        self.connect(QtGui.QApplication.clipboard(),
                     QtCore.SIGNAL('dataChanged()'),
                     self.clipboardChanged)

        trigger_actions = [
            (self.redoAction, self.viewManager.redo),
            (self.undoAction, self.viewManager.undo),
            (self.copyAction, self.viewManager.copySelection),
            (self.pasteAction, self.viewManager.pasteToCurrentPipeline),
            (self.pasteAction, self.viewManager.selectAllModules),
            (self.newVistrailAction, self.newVistrail),
            (self.openFileAction, self.open_vistrail_from_file),
            (self.openDBAction, self.open_vistrail_from_db),
            (self.saveFileAction, self.save_vistrail),
            (self.saveFileAsAction, self.save_vistrail_file_as),
            (self.saveDBAction, self.save_vistrail_db_as),
            (self.closeVistrailAction, self.viewManager.closeVistrail),
            (self.helpAction, self.showAboutMessage),
            (self.editPreferencesAction, self.showPreferences),
            (self.executeCurrentWorkflowAction,
             self.viewManager.executeCurrentPipeline),
            (self.executeDiffAction, self.showDiff),
            (self.executeQueryAction, self.viewManager.queryVistrail),
            (self.executeExplorationAction,
             self.viewManager.executeCurrentExploration),
            (self.flushCacheAction, self.flush_cache),
            (self.quitVistrailsAction, self.quitVistrails),
            ]

        for (emitter, receiver) in trigger_actions:
            self.connect(emitter, QtCore.SIGNAL('triggered()'), receiver)

        self.connect(self.pipViewAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.setPIPMode)

        self.connect(self.methodsViewAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.setMethodsMode)

        self.connect(self.setMethodsViewAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.setSetMethodsMode)

        self.connect(self.propertiesViewAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.setPropertiesMode)

        self.connect(self.vistrailActionGroup,
                     QtCore.SIGNAL('triggered(QAction *)'),
                     self.vistrailSelectFromMenu)
        
        self.connect(self.shellAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showShell)
        
        self.connect(self.bookmarksAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showBookmarks)

        self.connect(self.bookmarksWindow,
                     QtCore.SIGNAL("bookmarksHidden()"),
                     self.bookmarksAction.toggle)
        
        for shortcut in self.executeShortcuts:
            self.connect(shortcut,
                         QtCore.SIGNAL('activated()'),
                         self.viewManager.executeCurrentPipeline)

                
        # Make sure we can change view when requested
        self.connect(self.viewToolBar,
                     QtCore.SIGNAL('viewModeChanged(int)'),
                     self.viewModeChanged)
        
        # Change cursor action
        self.connect(self.viewToolBar,
                     QtCore.SIGNAL('cursorChanged(int)'),
                     self.viewManager.changeCursor)

        # Execute action
        self.connect(self.viewToolBar.executeAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.execute)

        # Undo action
        self.connect(self.viewToolBar.undoAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.undo)

        # Redo action
        self.connect(self.viewToolBar.redoAction(),
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.redo)

    def moduleSelectionChange(self, selection):
        """ moduleSelectionChange(selection: list[id]) -> None
        Update the status of tool bar buttons if there is module selected
        
        """
        self.copyAction.setEnabled(len(selection)>0)

    def versionSelectionChange(self, versionId):
        """ versionSelectionChange(versionId: int) -> None
        Update the status of tool bar buttons if there is a version selected
        
        """
        self.undoAction.setEnabled(versionId>0)
        self.viewToolBar.undoAction().setEnabled(versionId>0)
        self.selectAllAction.setEnabled(self.viewManager.canSelectAll())
        currentView = self.viewManager.currentWidget()
        if currentView:
            self.redoAction.setEnabled(currentView.can_redo())
            self.viewToolBar.redoAction().setEnabled(currentView.can_redo())
        else:
            self.redoAction.setEnabled(False)
            self.viewToolBar.redoAction().setEnabled(False)

    def execStateChange(self):
        """ execStateChange() -> None
        Something changed on the canvas that effects the execution state,
        update interface accordingly.
        
        """
        currentView = self.viewManager.currentWidget()        
        if currentView:
            # Update toolbar
            if self.viewIndex == 2:
                self.viewToolBar.executeAction().setEnabled(
                    currentView.execQueryEnabled)
            elif self.viewIndex == 3:
                self.viewToolBar.executeAction().setEnabled(
                    currentView.execExploreEnabled)
            else:
                self.viewToolBar.executeAction().setEnabled(
                    currentView.execPipelineEnabled)
            # Update menu
            self.executeCurrentWorkflowAction.setEnabled(
                currentView.execPipelineEnabled)
            self.executeDiffAction.setEnabled(currentView.execDiffEnabled)
            self.executeQueryAction.setEnabled(currentView.execQueryEnabled)
            self.executeExplorationAction.setEnabled(currentView.execExploreEnabled)
        else:
            self.viewToolBar.executeAction().setEnabled(False)
            self.executeCurrentWorkflowAction.setEnabled(False)
            self.executeDiffAction.setEnabled(False)
            self.executeQueryAction.setEnabled(False)
            self.executeExplorationAction.setEnabled(False)

    def viewModeChanged(self, index):
        """ viewModeChanged(index: int) -> None
        Update the state of the view buttons
        
        """
        self.viewIndex = index
        self.execStateChange()
        self.viewManager.viewModeChanged(index)

    def clipboardChanged(self, mode=QtGui.QClipboard.Clipboard):
        """ clipboardChanged(mode: QClipboard) -> None        
        Update the status of tool bar buttons when the clipboard
        contents has been changed
        
        """
        clipboard = QtGui.QApplication.clipboard()
        self.pasteAction.setEnabled(not clipboard.text().isEmpty())

    def currentVistrailChanged(self, vistrailView):
        """ currentVistrailChanged(vistrailView: QVistrailView) -> None
        Redisplay the new title of vistrail
        
        """
        self.execStateChange()
        if vistrailView:
            self.setWindowTitle('VisTrails Builder - ' +
                                vistrailView.windowTitle())
        else:
            self.setWindowTitle('VisTrails Builder')
            self.saveFileAction.setEnabled(False)
            self.closeVistrailAction.setEnabled(False)
            self.saveFileAsAction.setEnabled(False)
            self.saveDBAction.setEnabled(False)
            self.vistrailMenu.menuAction().setEnabled(False)

        if vistrailView and vistrailView.viewAction:
            vistrailView.viewAction.setText(vistrailView.windowTitle())
            if not vistrailView.viewAction.isChecked():
                vistrailView.viewAction.setChecked(True)

    
    def vistrailChanged(self):
        """ vistrailChanged() -> None
        An action was performed on the current vistrail
        
        """
        self.saveFileAction.setEnabled(True)
        self.saveFileAsAction.setEnabled(True)
        self.saveDBAction.setEnabled(True)

    def newVistrail(self):
        """ newVistrail() -> None
        Start a new vistrail
        
        """
        self.viewManager.newVistrail()
        self.viewToolBar.changeView(0)

    def open_vistrail(self, locator_class):
        """ open_vistrail(locator_class) -> None
        Prompt user for information to get to a vistrail in different ways,
        depending on the locator class given.
        """
        locator = locator_class.load_from_gui(self)
        if locator:
            self.open_vistrail_without_prompt(locator)
            
    def open_vistrail_without_prompt(self, locator):
        """open_vistrail_without_prompt(locator_class) -> None
        Open vistrail depending on the locator class given.
        """
        self.viewManager.open_vistrail(locator)
        self.closeVistrailAction.setEnabled(True)
        self.saveFileAsAction.setEnabled(True)
        self.saveDBAction.setEnabled(True)
        self.vistrailMenu.menuAction().setEnabled(True)
        self.viewToolBar.changeView(1)
        
    def open_vistrail_from_file(self):
        """ open_vistrail_from_file() -> None
        Opens a vistrail from the file system
        
        """
        self.open_vistrail(XMLFileLocator)

    def open_vistrail_from_db(self):
        """ open_vistrail_from_db() -> None
        Opens a vistrail from the database

        """
        self.open_vistrail(DBLocator)

    def save_vistrail(self):
        """ save_vistrail() -> None
        Save the current vistrail to file
        
        """
        current_view = self.viewManager.currentWidget()
        locator = current_view.controller.locator
        if locator is None:
            class_ = XMLFileLocator
        else:
            class_ = type(locator)
        self.viewManager.save_vistrail(class_)

    def save_vistrail_file_as(self):
        """ save_vistrail_file_as() -> None
        Save the current vistrail to a different file
        
        """
        self.viewManager.save_vistrail(XMLFileLocator,
                                       force_choose_locator=True)

    def save_vistrail_db_as(self):
        self.viewManager.save_vistrail(DBLocator,
                                       force_choose_locator=True)
    
    def quitVistrails(self):
        """ quitVistrails() -> bool
        Quit Vistrail, return False if not succeeded
        
        """
        if self.viewManager.closeAllVistrails():
            QtCore.QCoreApplication.quit()
        return False

    def vistrailViewAdded(self, view):
        """ vistrailViewAdded(view: QVistrailView) -> None
        Add this vistrail to the Vistrail menu
        
        """
        view.viewAction = QtGui.QAction(view.windowTitle(), self)
        view.viewAction.view = view
        view.viewAction.setCheckable(True)
        self.vistrailActionGroup.addAction(view.viewAction)
        self.vistrailMenu.addAction(view.viewAction)
        view.versionTab.versionView.scene().fitToView(
            view.versionTab.versionView)

    def vistrailViewRemoved(self, view):
        """ vistrailViewRemoved(view: QVistrailView) -> None
        Remove this vistrail from the Vistrail menu
        
        """
        self.vistrailActionGroup.removeAction(view.viewAction)
        self.vistrailMenu.removeAction(view.viewAction)
        view.viewAction.view = None

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
            self.savePythonPrompt()
            if not self.shell:
                self.shell = QShellDialog(self)
                self.connect(self.shell,QtCore.SIGNAL("shellHidden()"),
                             self.shellAction.toggle)
            self.shell.show()
        else:
            if self.shell:
                self.shell.hide()
            self.recoverPythonPrompt()

    def savePythonPrompt(self):
        """savePythonPrompt() -> None
        Keep system standard input and output internally

        """
        self.stdout = sys.stdout
        self.stdin = sys.stdin
        self.stderr = sys.stderr
    
    def recoverPythonPrompt(self):
        """recoverPythonPrompt() -> None
        Reassign system standard input and output to previous saved state.

        """
        sys.stdout = self.stdout
        sys.stdin = self.stdin
        sys.stderr = self.stderr

    def showBookmarks(self, checked=True):
        """ showBookmarks() -> None
        Display Bookmarks Interactor Window
        
        """
        if checked:
            if self.bookmarksWindow:
                self.bookmarksWindow.show()
        else:
            if self.bookmarksWindow:
                self.bookmarksWindow.hide()
        
    def showAboutMessage(self):
        """showAboutMessage() -> None
        Displays Application about message

        """
        QtGui.QMessageBox.about(self,self.tr("About VisTrails..."),
                                self.tr(system.about_string()))

    def showPreferences(self):
        """showPreferences() -> None
        Display Preferences dialog

        """
        dialog = QPreferencesDialog(self)
        dialog.exec_()

    def showDiff(self):
        """showDiff() -> None
        Show the visual difference interface
        
        """
        currentView = self.viewManager.currentWidget()
        if (currentView and currentView.execDiffId1 > 0 and 
            currentView.execDiffId2 > 0):
            visDiff = QVisualDiff(currentView.controller.vistrail,
                                  currentView.execDiffId1,
                                  currentView.execDiffId2,
                                  currentView.controller,
                                  self)
            visDiff.show()

    def execute(self):
        """ execute() -> None
        Execute something depending on the view
        
        """
        if self.viewToolBar.currentViewIndex == 2:
            self.viewManager.queryVistrail(True)
        elif self.viewToolBar.currentViewIndex == 3:
            self.viewManager.executeCurrentExploration()
        else:
            self.viewManager.executeCurrentPipeline()

    def flush_cache(self):
        core.interpreter.cached.CachedInterpreter.flush()

