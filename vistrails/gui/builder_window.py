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
from gui.shell import QShellDialog
from gui.theme import CurrentTheme
from gui.view_manager import QViewManager
import copy
import core.interpreter.cached
import sys

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
        
        self.bookmarksWindow = QBookmarksWindow(parent=self)
        
        self.createActions()
        self.createMenu()
        self.createToolBar()

        self.connectSignals()

        self.shell = None
        self.vistrailViewToolBar = None
        self.setSDIMode(self.sdiModeAction.isChecked())
        
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
       
        self.copyAction = QtGui.QAction('Copy\tCtrl+C', self)
        self.copyAction.setEnabled(False)
        self.copyAction.setStatusTip('Copy selected modules in '
                                     'the current pipeline view')

        self.pasteAction = QtGui.QAction('Paste\tCtrl+V', self)
        self.pasteAction.setEnabled(False)
        self.pasteAction.setStatusTip('Paste copied modules in the clipboard '
                                      'into the current pipeline view')
        
        self.shellAction = QtGui.QAction(CurrentTheme.CONSOLE_MODE_ICON,
                                         'VisTrails Console', self)
        self.shellAction.setCheckable(True)
        self.shellAction.setShortcut('Ctrl+H')

        self.bookmarksAction = QtGui.QAction(CurrentTheme.BOOKMARKS_ICON,
                                             'Bookmarks', self)
        self.bookmarksAction.setCheckable(True)
        self.bookmarksAction.setShortcut('Ctrl+D')

        self.sdiModeAction = QtGui.QAction('SDI Mode', self)
        self.sdiModeAction.setCheckable(True)
        self.sdiModeAction.setChecked(False)
        
        self.helpAction = QtGui.QAction(self.tr('About VisTrails...'), self)

        a = QtGui.QAction(self.tr('E&xecute Current Workflow\tCtrl+Enter'),
                          self)
        self.executeCurrentWorkflowAction = a
        self.flushCacheAction = QtGui.QAction(self.tr('Erase Cache Contents'),
                                              self)

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
        self.viewMenu.addAction(self.bookmarksAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.sdiModeAction)

        self.runMenu = self.menuBar().addMenu('&Run')
        self.runMenu.addAction(self.executeCurrentWorkflowAction)
        self.runMenu.addAction(self.flushCacheAction)
        

        self.vistrailMenu = self.menuBar().addMenu('Vis&trail')
        self.vistrailActionGroup = QtGui.QActionGroup(self)

        self.helpMenu = self.menuBar().addMenu('Help')
        self.helpMenu.addAction(self.helpAction)

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
        self.toolBar.addAction(self.bookmarksAction)

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
        
        self.connect(self.bookmarksAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showBookmarks)

        self.connect(self.helpAction,
                     QtCore.SIGNAL("triggered()"),
                     self.showAboutMessage)

        self.connect(self.bookmarksWindow,
                     QtCore.SIGNAL("bookmarksHidden()"),
                     self.bookmarksAction.toggle)

        self.connect(self.executeCurrentWorkflowAction,
                     QtCore.SIGNAL("triggered()"),
                     self.viewManager.executeCurrentPipeline)

        self.connect(self.flushCacheAction,
                     QtCore.SIGNAL("triggered()"),
                     self.flush_cache)
        
        for shortcut in self.executeShortcuts:
            self.connect(shortcut,
                         QtCore.SIGNAL('activated()'),
                         self.viewManager.executeCurrentPipeline)

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
            "Open Vistrail...",
            system.vistrailsDirectory(),
            "Vistrail files (*.xml)\nOther files (*)")
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
            self.viewManager.saveVistrail(None, str(fileName))

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
        view.versionTab.versionView.scene().fitToView(
            view.versionTab.versionView)

    def vistrailViewRemoved(self, view):
        """ vistrailViewRemoved(view: QVistrailView) -> None
        Remove this vistrail from the Vistrail menu
        
        """
        self.vistrailActionGroup.removeAction(view.viewAction)
        self.vistrailMenu.removeAction(view.viewAction)
        view.viewAction.view = None
        self.removeToolBar(self.vistrailViewToolBar)
        self.vistrailViewToolBar = None

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
                                self.tr(system.aboutString()))

    def flush_cache(self):
        core.interpreter.cached.CachedInterpreter.cleanup()
