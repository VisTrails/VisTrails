###########################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
from core.configuration import get_vistrails_configuration
from core.db.locator import DBLocator, FileLocator, XMLFileLocator, untitled_locator
from core.packagemanager import get_package_manager
import core.interpreter.cached
import core.system
from core.vistrail.pipeline import Pipeline
from core.vistrail.vistrail import Vistrail
from gui.application import VistrailsApplication
from gui.graphics_view import QInteractiveGraphicsView
from gui.module_palette import QModulePalette
from gui.open_db_window import QOpenDBWindow
from gui.preferences import QPreferencesDialog
from gui.repository import QRepositoryDialog
from gui.shell import QShellDialog
from gui.debugger import QDebugger
from gui.pipeline_view import QPipelineView
from gui.theme import CurrentTheme
from gui.view_manager import QViewManager
from gui.vistrail_toolbar import QVistrailViewToolBar, QVistrailInteractionToolBar
from gui.vis_diff import QVisualDiff
from gui.utils import build_custom_window
import sys
import db.services.vistrail
from gui import merge_gui
from db.services.io import SaveBundle
from core.thumbnails import ThumbnailCache
import gui.debug


################################################################################

class QBuilderWindow(QtGui.QMainWindow):
    """
    QBuilderWindow is a main widget containing an editin area for
    VisTrails and several tool windows. Also remarks that almost all
    of QBuilderWindow components are floating dockwidget. This mimics
    a setup of an IDE

    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ QBuilderWindow(parent: QWidget) -> QBuilderWindow
        Construct the main window with menus, toolbar, and floating toolwindow

        """
        QtGui.QMainWindow.__init__(self, parent, f)
        self.title = 'VisTrails Builder'
        self.setWindowTitle(self.title)
        self.setStatusBar(QtGui.QStatusBar(self))
        self.setDockNestingEnabled(True)

        self.viewManager = QViewManager()
        self.setCentralWidget(self.viewManager)

        self.modulePalette = QModulePalette(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.modulePalette.toolWindow())

        self.viewIndex = 0
        self.dbDefault = False

        self.createActions()
        self.createMenu()
        self.createToolBar()

        self.connectSignals()

        gui.debug.DebugView.getInstance(self)

        self.shell = None
        self.debugger = None
        
        # If this is true, we're currently executing a pipeline, so
        # We can't allow other executions.
        self._executing = False

        # This keeps track of the menu items for each package
        self._package_menu_items = {}

        self.detachedHistoryView = getattr(get_vistrails_configuration(), 'detachHistoryView')

    def create_first_vistrail(self):
        """ create_first_vistrail() -> None
        Create untitled vistrail in interactive mode
        """
        # FIXME: when interactive and non-interactive modes are separated,
        # this autosave code can move to the viewManager
        if not self.dbDefault and untitled_locator().has_temporaries():
            if not FileLocator().prompt_autosave(self):
                untitled_locator().clean_temporaries()
        if self.viewManager.newVistrail(True):
            self.viewModeChanged(0)
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
        self.newVistrailAction.setStatusTip('Create a new vistrail')

        self.openFileAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_ICON,
                                            '&Open', self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setStatusTip('Open an existing vistrail from '
                                         'a file')

        self.importFileAction = QtGui.QAction(CurrentTheme.OPEN_VISTRAIL_DB_ICON,
                                              'From DB...', self)
        self.importFileAction.setStatusTip('Import an existing vistrail from '
                                           'a database')

        self.saveFileAction = QtGui.QAction(CurrentTheme.SAVE_VISTRAIL_ICON,
                                                '&Save', self)
        self.saveFileAction.setShortcut('Ctrl+S')
        self.saveFileAction.setStatusTip('Save the current vistrail '
                                         'to a file')
        self.saveFileAction.setEnabled(False)

        self.saveFileAsAction = QtGui.QAction('Save as...', self)
        self.saveFileAsAction.setShortcut('Ctrl+Shift+S')
        self.saveFileAsAction.setStatusTip('Save the current vistrail '
                                           'to a different file location')
        self.saveFileAsAction.setEnabled(False)

        self.exportFileAction = QtGui.QAction('To DB...', self)
        self.exportFileAction.setStatusTip('Export the current vistrail to '
                                           'a database')
        self.exportFileAction.setEnabled(False)

        self.closeVistrailAction = QtGui.QAction('Close', self)
        self.closeVistrailAction.setShortcut('Ctrl+W')
        self.closeVistrailAction.setStatusTip('Close the current vistrail')
        self.closeVistrailAction.setEnabled(False)

        self.exportStableAction = QtGui.QAction('To Stable Version...', 
                                                self)
        self.exportStableAction.setStatusTip('Save vistrail as XML according '
                                             'to the older (stable) schema')
        self.exportStableAction.setEnabled(True)

        self.saveOpmAction = QtGui.QAction('OPM XML...', self)
        self.saveOpmAction.setStatusTip('Saves provenance according to the'
                                        'Open Provenance Model in XML')
        self.saveOpmAction.setEnabled(True)

        self.saveLogAction = QtGui.QAction('Log To XML...', self)
        self.saveLogAction.setStatusTip('Save the execution log to '
                                        'a file')
        self.saveLogAction.setEnabled(True)

        self.exportLogAction = QtGui.QAction('Log To DB...', self)
        self.exportLogAction.setStatusTip('Save the execution log to '
                                          'a database')
        self.exportLogAction.setEnabled(True)

        self.importWorkflowAction = QtGui.QAction('Workflow...', self)
        self.importWorkflowAction.setStatusTip('Import a workflow from an '
                                               'xml file')
        self.importWorkflowAction.setEnabled(True)

        self.saveWorkflowAction = QtGui.QAction('Workflow To XML...', self)
        self.saveWorkflowAction.setStatusTip('Save the current workflow to '
                                             'a file')
        self.saveWorkflowAction.setEnabled(True)

        self.exportWorkflowAction = QtGui.QAction('Workflow To DB...', self)
        self.exportWorkflowAction.setStatusTip('Save the current workflow to '
                                               'a database')
        self.exportWorkflowAction.setEnabled(True)

        self.saveRegistryAction = QtGui.QAction('Registry To XML...', self)
        self.saveRegistryAction.setStatusTip('Save the current registry to '
                                             'a file')
        self.saveRegistryAction.setEnabled(True)

        self.exportRegistryAction = QtGui.QAction('Registry To DB...', self)
        self.exportRegistryAction.setStatusTip('Save the current registry to '
                                               'a database')
        self.exportRegistryAction.setEnabled(True)

        self.savePDFAction = QtGui.QAction('PDF...', self)
        self.savePDFAction.setStatusTip('Save the current view'
                                                     'to a PDF file')
        self.savePDFAction.setEnabled(True)

        self.quitVistrailsAction = QtGui.QAction('Quit', self)
        self.quitVistrailsAction.setShortcut('Ctrl+Q')
        self.quitVistrailsAction.setStatusTip('Exit Vistrails')

        self.undoAction = QtGui.QAction(CurrentTheme.UNDO_ICON,
                                        'Undo', self)
        self.undoAction.setEnabled(False)
        self.undoAction.setStatusTip('Undo the previous action')
        self.undoAction.setShortcut('Ctrl+Z')

        self.redoAction = QtGui.QAction(CurrentTheme.REDO_ICON,
                                        'Redo', self)
        self.redoAction.setEnabled(False)
        self.redoAction.setStatusTip('Redo an undone action')
        self.redoAction.setShortcut('Ctrl+Y')

        self.copyAction = QtGui.QAction('Copy\tCtrl+C', self)
        self.copyAction.setEnabled(False)
        self.copyAction.setStatusTip('Copy selected modules in '
                                     'the current pipeline view')

        self.pasteAction = QtGui.QAction('Paste\tCtrl+V', self)
        self.pasteAction.setEnabled(False)
        self.pasteAction.setStatusTip('Paste copied modules in the clipboard '
                                      'into the current pipeline view')

        self.groupAction = QtGui.QAction('Group', self)
        self.groupAction.setShortcut('Ctrl+G')
        self.groupAction.setEnabled(False)
        self.groupAction.setStatusTip('Group the '
                                      'selected modules in '
                                      'the current pipeline view')
        self.ungroupAction = QtGui.QAction('Ungroup', self)
        self.ungroupAction.setShortcut('Ctrl+Shift+G')
        self.ungroupAction.setEnabled(False)
        self.ungroupAction.setStatusTip('Ungroup the '
                                      'selected groups in '
                                      'the current pipeline view')
        self.showGroupAction = QtGui.QAction('Show Group Pipeline', self)
        self.showGroupAction.setEnabled(True)
        self.showGroupAction.setStatusTip('Show the underlying pipelines '
                                          'for the selected groups in '
                                          'the current pipeline view')

        self.makeAbstractionAction = QtGui.QAction('Make SubWorkflow', self)
        self.makeAbstractionAction.setStatusTip('Create a subworkflow '
                                                'from the selected modules')
        self.convertToAbstractionAction = \
            QtGui.QAction('Convert to SubWorkflow', self)
        self.convertToAbstractionAction.setStatusTip('Convert selected group '
                                                     'to a subworkflow')
        self.editAbstractionAction = QtGui.QAction("Edit SubWorkflow", self)
        self.editAbstractionAction.setStatusTip("Edit a subworkflow")
        self.importAbstractionAction = QtGui.QAction('Import SubWorkflow', self)
        self.importAbstractionAction.setStatusTip('Import subworkflow from '
                                                  'a vistrail to local '
                                                  'subworkflows')
        self.exportAbstractionAction = QtGui.QAction('Export SubWorkflows', self)
        self.exportAbstractionAction.setStatusTip('Export subworkflows from '
                                                  'local subworkflows for '
                                                  'use in a package')
        self.selectAllAction = QtGui.QAction('Select All\tCtrl+A', self)
        self.selectAllAction.setEnabled(False)
        self.selectAllAction.setStatusTip('Select all modules in '
                                          'the current pipeline view')

        self.repositoryOptions = QtGui.QAction('Web Repository Options', self)
        self.repositoryOptions.setEnabled(True)
        self.repositoryOptions.setStatusTip('Add this VisTrail to VisTrails Repository')

        self.editPreferencesAction = QtGui.QAction('Preferences...', self)
        self.editPreferencesAction.setEnabled(True)
        self.editPreferencesAction.setStatusTip('Edit system preferences')

        self.shellAction = QtGui.QAction(CurrentTheme.CONSOLE_MODE_ICON,
                                         'VisTrails Console', self)
        self.shellAction.setCheckable(True)
        self.shellAction.setShortcut('Ctrl+H')

        self.debugAction = QtGui.QAction('VisTrails Debugger', self)
        self.debugAction.setCheckable(True)
        self.debugAction.setChecked(False)

        self.messagesAction = QtGui.QAction('VisTrails Messages', self)
        self.messagesAction.setCheckable(True)
        self.messagesAction.setChecked(False)

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

        self.propertiesOverlayAction = QtGui.QAction('Properties Overlay', self)
        self.propertiesOverlayAction.setCheckable(True)
        self.propertiesOverlayAction.setChecked(False)

        self.expandBranchAction = QtGui.QAction('Expand Branch', self)
        self.expandBranchAction.setEnabled(True)
        self.expandBranchAction.setStatusTip('Expand all versions in the tree below the current version')

        self.collapseBranchAction = QtGui.QAction('Collapse Branch', self)
        self.collapseBranchAction.setEnabled(True)
        self.collapseBranchAction.setStatusTip('Collapse all expanded versions in the tree below the current version')

        self.collapseAllAction = QtGui.QAction('Collapse All', self)
        self.collapseAllAction.setEnabled(True)
        self.collapseAllAction.setStatusTip('Collapse all expanded branches of the tree')

        self.hideBranchAction = QtGui.QAction('Hide Branch', self)
        self.hideBranchAction.setEnabled(True)
        self.hideBranchAction.setStatusTip('Hide all versions in the tree including and below the current version')

        self.showAllAction = QtGui.QAction('Show All', self)
        self.showAllAction.setEnabled(True)
        self.showAllAction.setStatusTip('Show all hidden versions')
            
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
        
        self.vistrailActionGroup = QtGui.QActionGroup(self)
        self.mergeActionGroup = QtGui.QActionGroup(self)



    def createMenu(self):
        """ createMenu() -> None
        Initialize menu bar of builder window

        """
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.newVistrailAction)
        self.fileMenu.addAction(self.openFileAction)
        self.fileMenu.addAction(self.saveFileAction)
        self.fileMenu.addAction(self.saveFileAsAction)
        self.fileMenu.addAction(self.closeVistrailAction)
        self.fileMenu.addSeparator()
        self.importMenu = self.fileMenu.addMenu('Import')
        self.importMenu.addAction(self.importFileAction)
        self.importMenu.addSeparator()
        self.importMenu.addAction(self.importWorkflowAction)
        self.exportMenu = self.fileMenu.addMenu('Export')
        self.exportMenu.addAction(self.exportFileAction)
        self.exportMenu.addAction(self.exportStableAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.savePDFAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.saveWorkflowAction)
        self.exportMenu.addAction(self.exportWorkflowAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.saveOpmAction)
        self.exportMenu.addAction(self.saveLogAction)
        self.exportMenu.addAction(self.exportLogAction)
        self.exportMenu.addSeparator()
        self.exportMenu.addAction(self.saveRegistryAction)
        self.exportMenu.addAction(self.exportRegistryAction)
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
        self.editMenu.addAction(self.groupAction)
        self.editMenu.addAction(self.ungroupAction)
        self.editMenu.addAction(self.showGroupAction)
        self.editMenu.addAction(self.makeAbstractionAction)
        self.editMenu.addAction(self.convertToAbstractionAction)
        self.editMenu.addAction(self.editAbstractionAction)
        self.editMenu.addAction(self.importAbstractionAction)
        self.editMenu.addAction(self.exportAbstractionAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.repositoryOptions)
        self.mergeMenu = self.editMenu.addMenu('Merge with')
        self.mergeMenu.menuAction().setEnabled(False)
        self.mergeMenu.menuAction().setStatusTip('Merge another VisTrail into the current VisTrail')
        self.editMenu.addAction(self.repositoryOptions)
        self.editMenu.addSeparator()        
        self.editMenu.addAction(self.editPreferencesAction)

        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(self.shellAction)
        self.viewMenu.addAction(self.debugAction)
        self.viewMenu.addAction(self.messagesAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.expandBranchAction)
        self.viewMenu.addAction(self.collapseBranchAction)
        self.viewMenu.addAction(self.collapseAllAction)
        #self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.hideBranchAction)
        self.viewMenu.addAction(self.showAllAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.pipViewAction)
        self.viewMenu.addAction(
            self.modulePalette.toolWindow().toggleViewAction())
        self.viewMenu.addAction(self.methodsViewAction)
        self.viewMenu.addAction(self.setMethodsViewAction)
        self.viewMenu.addAction(self.propertiesViewAction)
        self.viewMenu.addAction(self.propertiesOverlayAction)

        self.runMenu = self.menuBar().addMenu('&Run')
        self.runMenu.addAction(self.executeCurrentWorkflowAction)
        self.runMenu.addAction(self.executeDiffAction)
        self.runMenu.addAction(self.executeQueryAction)
        self.runMenu.addAction(self.executeExplorationAction)
        self.runMenu.addSeparator()
        self.runMenu.addAction(self.flushCacheAction)

        self.vistrailMenu = self.menuBar().addMenu('Vis&trail')
        self.vistrailMenu.menuAction().setEnabled(False)

        self.packagesMenu = self.menuBar().addMenu('Packages')
        self.packagesMenu.menuAction().setEnabled(False)

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
        self.toolBar.addAction(self.undoAction)
        self.toolBar.addAction(self.redoAction)

        self.viewToolBar = QVistrailViewToolBar(self)
        self.addToolBar(self.viewToolBar)

        self.interactionToolBar = QVistrailInteractionToolBar(self)
        self.addToolBar(self.interactionToolBar)

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
            (self.selectAllAction, self.viewManager.selectAllModules),
            (self.groupAction, self.viewManager.group),
            (self.ungroupAction, self.viewManager.ungroup),
            (self.showGroupAction, self.showGroup),
            (self.makeAbstractionAction, 
             self.viewManager.makeAbstraction),
            (self.convertToAbstractionAction,
             self.viewManager.convertToAbstraction),
            (self.editAbstractionAction, self.editAbstraction),
            (self.importAbstractionAction, self.viewManager.importAbstraction),
            (self.exportAbstractionAction, self.viewManager.exportAbstraction),
            (self.newVistrailAction, self.newVistrail),
            (self.openFileAction, self.open_vistrail_default),
            (self.importFileAction, self.import_vistrail_default),
            (self.saveFileAction, self.save_vistrail_default),
            (self.saveFileAsAction, self.save_vistrail_default_as),
            (self.exportFileAction, self.export_vistrail_default),
            (self.closeVistrailAction, self.viewManager.closeVistrail),
            (self.exportStableAction, self.viewManager.export_stable),
            (self.saveOpmAction, self.viewManager.save_opm),
            (self.saveLogAction, self.save_log_default),
            (self.exportLogAction, self.export_log_default),
            (self.importWorkflowAction, self.import_workflow_default),
            (self.saveWorkflowAction, self.save_workflow_default),
            (self.exportWorkflowAction, self.export_workflow_default),
            (self.saveRegistryAction, self.save_registry_default),
            (self.exportRegistryAction, self.export_registry_default),
            (self.savePDFAction, self.save_pdf),
            (self.expandBranchAction, self.expandBranch),
            (self.collapseBranchAction, self.collapseBranch),
            (self.collapseAllAction, self.collapseAll),
            (self.hideBranchAction, self.hideBranch),
            (self.showAllAction, self.showAll),
            (self.helpAction, self.showAboutMessage),
            (self.repositoryOptions, self.showRepositoryOptions),
            (self.editPreferencesAction, self.showPreferences),
            (self.executeCurrentWorkflowAction,
             self.execute_current_pipeline),
            (self.executeDiffAction, self.showDiff),
            (self.executeQueryAction, self.queryVistrail),
            (self.executeExplorationAction,
             self.execute_current_exploration),
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

        self.connect(self.propertiesOverlayAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.viewManager.setPropertiesOverlayMode)

        self.connect(self.vistrailActionGroup,
                     QtCore.SIGNAL('triggered(QAction *)'),
                     self.vistrailSelectFromMenu)

        self.connect(self.mergeActionGroup,
                     QtCore.SIGNAL('triggered(QAction *)'),
                     self.vistrailMergeFromMenu)

        self.connect(self.shellAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showShell)

        self.connect(self.debugAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showDebugger)

        self.connect(self.messagesAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.showMessages)

        self.connect(gui.debug.DebugView.getInstance(),
                     QtCore.SIGNAL("messagesView(bool)"),
                     self.messagesAction.setChecked)

        for shortcut in self.executeShortcuts:
            self.connect(shortcut,
                         QtCore.SIGNAL('activated()'),
                         self.execute_current_pipeline)

        self.connect_package_manager_signals()

    def connect_package_manager_signals(self):
        """ connect_package_manager_signals()->None
        Connect specific signals related to the package manager """
        pm = get_package_manager()
        self.connect(pm,
                     pm.add_package_menu_signal,
                     self.add_package_menu_items)
        self.connect(pm,
                     pm.remove_package_menu_signal,
                     self.remove_package_menu_items)
        self.connect(pm,
                     pm.package_error_message_signal,
                     self.show_package_error_message)

    def add_package_menu_items(self, pkg_id, pkg_name, items):
        """add_package_menu_items(pkg_id: str,pkg_name: str,items: list)->None
        Add a pacckage menu entry with submenus defined by 'items' to
        Packages menu.

        """
        if len(self._package_menu_items) == 0:
            self.packagesMenu.menuAction().setEnabled(True)

        # we don't support a menu hierarchy yet, only a flat list
        # this can be added later
        if not self._package_menu_items.has_key(pkg_id):
            pkg_menu = self.packagesMenu.addMenu(str(pkg_name))
            self._package_menu_items[pkg_id] = pkg_menu
        else:
            pkg_menu = self._package_menu_items[pkg_id]
            pkg_menu.clear()
        for item in items:
            (name, callback) = item
            action = QtGui.QAction(name,self)
            self.connect(action, QtCore.SIGNAL('triggered()'),
                         callback)
            pkg_menu.addAction(action)

    def remove_package_menu_items(self, pkg_id):
        """remove_package_menu_items(pkg_id: str)-> None
        removes all menu entries from the Packages Menu created by pkg_id """
        if self._package_menu_items.has_key(pkg_id):
            pkg_menu = self._package_menu_items[pkg_id]
            del self._package_menu_items[pkg_id]
            pkg_menu.clear()
            pkg_menu.deleteLater()
        if len(self._package_menu_items) == 0:
            self.packagesMenu.menuAction().setEnabled(False)

    def show_package_error_message(self, pkg_id, pkg_name, msg):
        """show_package_error_message(pkg_id: str, pkg_name: str, msg:str)->None
        shows a message box with the message msg.
        Because the way initialization is being set up, the messages will be
        shown after the builder window is shown.

        """
        msgbox = build_custom_window("Package %s (%s) says:"%(pkg_name,pkg_id),
                                    msg,
                                    modal=True,
                                    parent=self)
        #we cannot call self.msgbox.exec_() or the initialization will hang
        # creating a modal window and calling show() does not cause it to hang
        # and forces the messages to be shown on top of the builder window after
        # initialization
        msgbox.show()

    def setDBDefault(self, on):
        """ setDBDefault(on: bool) -> None
        The preferences are set to turn on/off read/write from db instead of
        file. Update the state accordingly.

        """
        self.dbDefault = on
        if self.dbDefault:
            self.openFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_DB_ICON)
            self.openFileAction.setStatusTip('Open an existing vistrail from '
                                             'a database')
            self.importFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_ICON)
            self.importFileAction.setText('From XML File...')
            self.importFileAction.setStatusTip('Import an existing vistrail '
                                               ' from a file')
            self.saveFileAction.setStatusTip('Save the current vistrail '
                                             'to a database')
            self.saveFileAsAction.setStatusTip('Save the current vistrail to a '
                                               'different database location')
            self.exportFileAction.setText('To XML File...')
            self.exportFileAction.setStatusTip('Save the current vistrail to '
                                               ' a file')
            self.exportLogAction.setText('Log To XML File...')
            self.exportLogAction.setStatusTip('Save the execution log to '
                                              'a file')
            self.saveLogAction.setText('Log To DB...')
            self.saveLogAction.setStatusTip('Save the execution log to '
                                            'a database')
            self.exportWorkflowAction.setText('Workflow To XML File...')
            self.exportWorkflowAction.setStatusTip('Save the current workflow '
                                                   'to a file')
            self.importWorkflowAction.setStatusTip('Import a workflow from a '
                                                   'database')
            self.saveWorkflowAction.setText('Workflow To DB...')
            self.saveWorkflowAction.setStatusTip('Save the current workflow '
                                                 'to a database')
            self.exportRegistryAction.setText('Registry To XML File...')
            self.exportRegistryAction.setStatusTip('Save the current registry '
                                                   'to a file')
            self.saveRegistryAction.setText('Registry To DB...')
            self.saveRegistryAction.setStatusTip('Save the current registry '
                                                 'to a database')


        else:
            self.openFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_ICON)
            self.openFileAction.setStatusTip('Open an existing vistrail from '
                                             'a file')
            self.importFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_DB_ICON)
            self.importFileAction.setText('From DB...')
            self.importFileAction.setStatusTip('Import an existing vistrail '
                                               ' from a database')
            self.saveFileAction.setStatusTip('Save the current vistrail '
                                             'to a file')
            self.saveFileAsAction.setStatusTip('Save the current vistrail to a '
                                               'different file location')
            self.exportFileAction.setStatusTip('Save the current vistrail to '
                                               ' a database')
            self.saveLogAction.setText('Log To XML...')
            self.saveLogAction.setStatusTip('Save the execution log to '
                                            'a file')
            self.exportLogAction.setText('Log To DB...')
            self.exportLogAction.setStatusTip('Export the execution log to '
                                              'a database')
            self.importWorkflowAction.setStatusTip('Import a workflow from an '
                                                   'xml file')
            self.saveWorkflowAction.setText('Workflow To XML File...')
            self.saveWorkflowAction.setStatusTip('Save the current workflow '
                                                 'to a file')
            self.exportWorkflowAction.setText('Worfklow To DB...')
            self.exportWorkflowAction.setStatusTip('Save the current workflow '
                                                   'to a database')
            self.saveRegistryAction.setText('Registry To XML File...')
            self.saveRegistryAction.setStatusTip('Save the current registry '
                                                 'to a file')
            self.exportRegistryAction.setText('Registry To DB...')
            self.exportRegistryAction.setStatusTip('Save the current registry '
                                                   'to a database')

    def moduleSelectionChange(self, selection):
        """ moduleSelectionChange(selection: list[id]) -> None
        Update the status of tool bar buttons if there is module selected

        """
        self.copyAction.setEnabled(len(selection)>0)
        self.groupAction.setEnabled(len(selection)>0)
        self.ungroupAction.setEnabled(len(selection)>0)

    def versionSelectionChange(self, versionId):
        """ versionSelectionChange(versionId: int) -> None
        Update the status of tool bar buttons if there is a version selected

        """
        self.undoAction.setEnabled(versionId>0)
        self.selectAllAction.setEnabled(self.viewManager.canSelectAll())
        currentView = self.viewManager.currentWidget()
        if currentView:
            self.redoAction.setEnabled(currentView.can_redo())
        else:
            self.redoAction.setEnabled(False)

    def execStateChange(self):
        """ execStateChange() -> None
        Something changed on the canvas that effects the execution state,
        update interface accordingly.

        """
        currentView = self.viewManager.currentWidget()
        if currentView:
            # Update toolbars
            if self.viewIndex == 2:
                self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                          currentView.execQueryEnabled) 
            elif self.viewIndex == 3:
                self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                          currentView.execExploreEnabled)
            else: 
                self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                          currentView.execPipelineEnabled)

            # Update menu
            self.executeCurrentWorkflowAction.setEnabled(
                currentView.execPipelineEnabled)
            self.executeDiffAction.setEnabled(currentView.execDiffEnabled)
            self.executeQueryAction.setEnabled(currentView.execQueryEnabled)
            self.executeExplorationAction.setEnabled(currentView.execExploreEnabled)
        else:
            self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                      False)
            self.executeCurrentWorkflowAction.setEnabled(False)
            self.executeDiffAction.setEnabled(False)
            self.executeQueryAction.setEnabled(False)
            self.executeExplorationAction.setEnabled(False)

    def viewModeChanged(self, index):
        """ viewModeChanged(index: int) -> None
        Update the state of the view buttons

        """
        if self.detachedHistoryView and index==1:
            index = 0
        self.emit(QtCore.SIGNAL("changeViewState(int)"), index)
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
            self.setWindowTitle(self.title + ' - ' +
                                vistrailView.windowTitle())
            self.saveFileAction.setEnabled(True)
            self.closeVistrailAction.setEnabled(True)
            self.saveFileAsAction.setEnabled(True)
            self.exportFileAction.setEnabled(True)
            self.vistrailMenu.menuAction().setEnabled(True)
            self.mergeMenu.menuAction().setEnabled(True)
        else:
            self.setWindowTitle(self.title)
            self.saveFileAction.setEnabled(False)
            self.closeVistrailAction.setEnabled(False)
            self.saveFileAsAction.setEnabled(False)
            self.exportFileAction.setEnabled(False)
            self.vistrailMenu.menuAction().setEnabled(False)
            self.mergeMenu.menuAction().setEnabled(False)

        if vistrailView and vistrailView.viewAction:
            vistrailView.viewAction.setText(vistrailView.windowTitle())
            if not vistrailView.viewAction.isChecked():
                vistrailView.viewAction.setChecked(True)

        if vistrailView and vistrailView.mergeAction:
            vistrailView.mergeAction.setText(vistrailView.windowTitle())
        for mergeAction in self.mergeActionGroup.actions():
            if mergeAction == vistrailView.mergeAction:
                mergeAction.setVisible(False)
            else:
                mergeAction.setVisible(True)

        self.update_shell()
        self.update_debugger()

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        An action was performed on the current vistrail

        """
        self.saveFileAction.setEnabled(True)
        self.saveFileAsAction.setEnabled(True)
        self.exportFileAction.setEnabled(True)
        self.update_shell()
        self.update_debugger()
        
    def newVistrail(self):
        """ newVistrail() -> None
        Start a new vistrail, unless user cancels during interaction.

        FIXME: There should be a separation between the interactive
        and non-interactive parts.

        """
        if self.viewManager.newVistrail(False):
            self.viewModeChanged(0)

    def open_vistrail(self, locator_class):
        """ open_vistrail(locator_class) -> None
        Prompt user for information to get to a vistrail in different ways,
        depending on the locator class given.
        """
        locator = locator_class.load_from_gui(self, Vistrail.vtType)
        if locator:
            if locator.has_temporaries():
                if not locator_class.prompt_autosave(self):
                    locator.clean_temporaries()
            self.open_vistrail_without_prompt(locator)

    def open_vistrail_without_prompt(self, locator, version=None,
                                     execute_workflow=False, 
                                     is_abstraction=False):
        """open_vistrail_without_prompt(locator_class, version: int or str,
                                        execute_workflow: bool,
                                        is_abstraction: bool) -> None
        Open vistrail depending on the locator class given.
        If a version is given, the workflow is shown on the Pipeline View.
        If execute_workflow is True the workflow will be executed.
        If is_abstraction is True, the vistrail is flagged as abstraction
        """
        if not locator.is_valid():
            ok = locator.update_from_gui()
        else:
            ok = True
        if ok:
            self.viewManager.open_vistrail(locator, version, is_abstraction)
            self.closeVistrailAction.setEnabled(True)
            self.saveFileAsAction.setEnabled(True)
            self.exportFileAction.setEnabled(True)
            self.vistrailMenu.menuAction().setEnabled(True)
            self.mergeMenu.menuAction().setEnabled(True)
            if version:
                self.viewModeChanged(0)
            else:
                self.viewModeChanged(1)
            if execute_workflow:
                self.execute_current_pipeline()
                
        
    def open_vistrail_default(self):
        """ open_vistrail_default() -> None
        Opens a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail(DBLocator)
        else:
            self.open_vistrail(FileLocator())

    def import_vistrail_default(self):
        """ import_vistrail_default() -> None
        Imports a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail(FileLocator)
        else:
            self.open_vistrail(DBLocator)

    def save_vistrail(self):
        """ save_vistrail() -> None
        Save the current vistrail to file

        """
        current_view = self.viewManager.currentWidget()
        locator = current_view.controller.locator
        if locator is None:
            class_ = FileLocator()
        else:
            class_ = type(locator)
        self.viewManager.save_vistrail(class_)

    def save_vistrail_default(self):
        """ save_vistrail_default() -> None
        Save the current vistrail to the file/db

        """
        if self.dbDefault:
            self.viewManager.save_vistrail(DBLocator)
        else:
            self.viewManager.save_vistrail(FileLocator())

    def save_vistrail_default_as(self):
        """ save_vistrail_file_as() -> None
        Save the current vistrail to the file/db

        """
        if self.dbDefault:
            self.viewManager.save_vistrail(DBLocator,
                                           force_choose_locator=True)
        else:
            self.viewManager.save_vistrail(FileLocator(),
                                           force_choose_locator=True)

    def export_vistrail_default(self):
        """ export_vistrail_default() -> None
        Export the current vistrail to the file/db

        """
        if self.dbDefault:
            self.viewManager.save_vistrail(FileLocator(),
                                           force_choose_locator=True)
        else:
            self.viewManager.save_vistrail(DBLocator,
                                           force_choose_locator=True)

    def save_log(self, invert=False, choose=True):
        # want xor of invert and dbDefault
        if (invert and not self.dbDefault) or (not invert and self.dbDefault):
            self.viewManager.save_log(DBLocator,
                                      force_choose_locator=choose)
        else:
            self.viewManager.save_log(XMLFileLocator,
                                      force_choose_locator=choose)
    def save_log_default(self):
        self.save_log(False)
    def export_log_default(self):
        self.save_log(True)

    def import_workflow(self, locator_class):
        locator = locator_class.load_from_gui(self, Pipeline.vtType)
        if locator:
            if not locator.is_valid():
                ok = locator.update_from_gui()
            else:
                ok = True
            if ok:
                self.viewManager.open_workflow(locator)
                self.closeVistrailAction.setEnabled(True)
                self.saveFileAsAction.setEnabled(True)
                self.exportFileAction.setEnabled(True)
                self.vistrailMenu.menuAction().setEnabled(True)
                self.mergeMenu.menuAction().setEnabled(True)
                self.viewModeChanged(1)

    def import_workflow_default(self):
        self.import_workflow(XMLFileLocator)

    def save_workflow(self, invert=False, choose=True):
        # want xor of invert and dbDefault
        if (invert and not self.dbDefault) or (not invert and self.dbDefault):
            self.viewManager.save_workflow(DBLocator,
                                           force_choose_locator=choose)
        else:
            self.viewManager.save_workflow(XMLFileLocator,
                                           force_choose_locator=choose)
    def save_workflow_default(self):
        self.save_workflow(False)
    def export_workflow_default(self):
        self.save_workflow(True)

    def save_registry(self, invert=False, choose=True):
        # want xor of invert and dbDefault
        if (invert and not self.dbDefault) or (not invert and self.dbDefault):
            self.viewManager.save_registry(DBLocator,
                                           force_choose_locator=choose)
        else:
            self.viewManager.save_registry(XMLFileLocator,
                                           force_choose_locator=choose)
    def save_registry_default(self):
        self.save_registry(False)
    def export_registry_default(self):
        self.save_registry(True)

    def save_pdf(self):
        active_window = VistrailsApplication.activeWindow()
        view = None
        if active_window and active_window.centralWidget() and \
                hasattr(active_window.centralWidget(), 'saveToPDF'):
            view = active_window.centralWidget()
        elif active_window and hasattr(active_window, 'viewManager') and \
                hasattr(active_window.viewManager.currentView().\
                            stackedWidget.currentWidget().centralWidget(),
                        'saveToPDF'):
            view = active_window.viewManager.currentView().stackedWidget.\
                currentWidget().centralWidget()

        if view is not None:
            fileName = QtGui.QFileDialog.getSaveFileName(
                active_window,
                "Save PDF...",
                core.system.vistrails_file_directory(),
                "PDF files (*.pdf)",
                None)

            if fileName.isEmpty():
                return None
            f = str(fileName)
            view.saveToPDF(f)

    def quitVistrails(self):
        """ quitVistrails() -> bool
        Quit Vistrail, return False if not succeeded

        """
        if self.viewManager.closeAllVistrails():            
            QtCore.QCoreApplication.quit()
            # In case the quit() failed (when Qt doesn't have the main
            # event loop), we have to return True still
            return True
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
            view.versionTab.versionView, True)
        # create merge action
        view.mergeAction = QtGui.QAction(view.windowTitle(), self)
        view.mergeAction.view = view
        self.mergeActionGroup.addAction(view.mergeAction)
        self.mergeMenu.addAction(view.mergeAction)

    def vistrailViewRemoved(self, view):
        """ vistrailViewRemoved(view: QVistrailView) -> None
        Remove this vistrail from the Vistrail menu

        """
        self.vistrailActionGroup.removeAction(view.viewAction)
        self.vistrailMenu.removeAction(view.viewAction)
        view.viewAction.view = None
        # delete merge action
        self.mergeActionGroup.removeAction(view.mergeAction)
        self.mergeMenu.removeAction(view.mergeAction)
        view.mergeAction.view = None

    def vistrailSelectFromMenu(self, menuAction):
        """ vistrailSelectFromMenu(menuAction: QAction) -> None
        Handle clicked from the Vistrail menu

        """
        self.viewManager.setCurrentWidget(menuAction.view)

    def vistrailMergeFromMenu(self, mergeAction):
        """ vistrailSelectFromMenu(menuAction: QAction) -> None
        Handle clicked from the Vistrail menu

        """
        thumb_cache = ThumbnailCache.getInstance()
        c1 = self.viewManager.currentView().controller
        t1 = c1.find_thumbnails(tags_only=thumb_cache.conf.tagsOnly) \
            if thumb_cache.conf.autoSave else []
        s1 = SaveBundle(c1.vistrail.vtType, c1.vistrail, c1.log, thumbnails=t1)
        l1 = c1.locator._name if c1.locator is not None else ''
        c2 = mergeAction.view.controller
        t2 = c2.find_thumbnails(tags_only=thumb_cache.conf.tagsOnly) \
            if thumb_cache.conf.autoSave else []
        s2 = SaveBundle(c2.vistrail.vtType, c2.vistrail, c2.log, thumbnails=t2)
        l2 = c2.locator._name if c2.locator is not None else ''
        if c1.changed or c2.changed:
            text = ('Both Vistrails need to be saved before they can be merged.')
            QtGui.QMessageBox.information(None, 'Cannot perform merge',
                                      text, '&OK')
            return
        db.services.vistrail.merge(s1, s2, "", merge_gui, l1, l2)
        vistrail = c1.vistrail.do_copy()
        vistrail.locator = c1.locator
        self.viewManager.currentView().set_vistrail(vistrail, c1.locator,
                                                   thumbnails=s1.thumbnails)
        self.viewManager.currentView().setup_view()

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
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                               self.shell)
            self.shell.show()
            currentView = self.viewManager.currentWidget()
            if currentView:
                controller = currentView.controller
                pipeline = controller.current_pipeline
                self.shell.shell.add_controller(controller)
                self.shell.shell.add_pipeline(pipeline)
        else:
            if self.shell:
                self.shell.hide()
            self.recoverPythonPrompt()

    def update_shell(self):
        try:
            if not self.shell:
                self.shell = QShellDialog(self)
                self.connect(self.shell, QtCore.SIGNAL("shellHidden()"),
                             self.shellAction.toggle)
                self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                                   self.shell)
            
            self.shell.shell.add_controller(self.viewManager.currentWidget().controller)
            if self.shell.isVisible():
                self.shell.show()
            else:
                self.shell.hide()
        except:
            pass

    def showDebugger(self, checked=True):
        ctrlr = self.viewManager.currentWidget().controller
        if checked:
            if not self.debugger:
                self.debugger = QDebugger(self, ctrlr)
                self.connect(self.debugger, QtCore.SIGNAL("debuggerHidden()"),
                             self.debugAction.toggle)
            self.debugger.setWindowTitle("Debugger")
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                               self.debugger)
            self.debugger.show()
        elif self.debugger and self.debugger.isVisible():
            self.debugger.hide()

    def update_debugger(self):
        if self.viewManager.currentWidget() is None:
            return
        ctrlr = self.viewManager.currentWidget().controller
        if not self.debugger:
            self.debugger = QDebugger(self, ctrlr)
            self.connect(self.debugger, QtCore.SIGNAL("debuggerHidden()"),
                         self.debugAction.toggle)
            self.debugger.setWindowTitle("Debugger")
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                               self.debugger)

        self.debugger.set_controller(ctrlr)
        if self.debugger.isVisible():
            self.debugger.show()
        else:
            self.debugger.hide()

    def showMessages(self, checked=True):
        debugView = gui.debug.DebugView.getInstance()
        if checked:
            debugView.show()
        else:
            debugView.hide()

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

    def showAboutMessage(self):
        """showAboutMessage() -> None
        Displays Application about message

        """
        class About(QtGui.QLabel):
            def mousePressEvent(self, e):
                self.emit(QtCore.SIGNAL("clicked()"))

        dlg = QtGui.QDialog(self, QtCore.Qt.FramelessWindowHint)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        bgimage = About(dlg)
        bgimage.setPixmap(CurrentTheme.DISCLAIMER_IMAGE)
        layout.addWidget(bgimage)
        dlg.setLayout(layout)
        text = "<font color=\"white\"><b>%s</b></font>" % \
               system.short_about_string()
        version = About(text, dlg)
        version.setGeometry(11,20,450,30)
        self.connect(bgimage,
                     QtCore.SIGNAL('clicked()'),
                     dlg,
                     QtCore.SLOT('accept()'))
        self.connect(version,
                     QtCore.SIGNAL('clicked()'),
                     dlg,
                     QtCore.SLOT('accept()'))
        dlg.setSizeGripEnabled(False)
        dlg.exec_()

        #QtGui.QMessageBox.about(self,self.tr("About VisTrails..."),
        #                        self.tr(system.about_string()))

    def showRepositoryOptions(self):
        """ Displays Repository Options for authentication and pushing VisTrail to Repository """
        dialog = QRepositoryDialog(self)
        dialog.exec_()

    def showPreferences(self):
        """showPreferences() -> None
        Display Preferences dialog

        """
        dialog = QPreferencesDialog(self)
        retval = dialog.exec_()
        if retval != 0:
            self.flush_cache()
            currentView = self.viewManager.currentWidget()
            if currentView:
                current_pipeline = currentView.controller.current_pipeline
                current_pipeline.validate()
            
        # Update the state of the icons if changing between db and file
        # support
        dbState = getattr(get_vistrails_configuration(), 'dbDefault')
        if self.dbDefault != dbState:
            self.setDBDefault(dbState)

    def showDiff(self):
        """showDiff() -> None
        Show the visual difference interface

        """
        currentView = self.viewManager.currentWidget()
        if (currentView and currentView.execDiffId1 >= 0 and
            currentView.execDiffId2 >= 0):
            visDiff = QVisualDiff(currentView.controller.vistrail,
                                  currentView.execDiffId1,
                                  currentView.execDiffId2,
                                  currentView.controller,
                                  self)
            visDiff.show()

    def showGroup(self):
        """showGroup() -> None
        Show the pipeline underlying a group module
        
        """
        class DummyController(object):
            def __init__(self, pip):
                self.current_pipeline = pip
                self.search = None
#             def copy_modules_and_connections(self, module_ids, connection_ids):
#                 """copy_modules_and_connections(module_ids: [long],
#                                              connection_ids: [long]) -> str
#                 Serializes a list of modules and connections
#                 """

#                 pipeline = Pipeline()
# #                 pipeline.set_abstraction_map( \
# #                     self.current_pipeline.abstraction_map)
#                 for module_id in module_ids:
#                     module = self.current_pipeline.modules[module_id]
# #                     if module.vtType == Abstraction.vtType:
# #                         abstraction = \
# #                             pipeline.abstraction_map[module.abstraction_id]
# #                         pipeline.add_abstraction(abstraction)
#                     pipeline.add_module(module)
#                 for connection_id in connection_ids:
#                     connection = self.current_pipeline.connections[connection_id]
#                     pipeline.add_connection(connection)
#                 return core.db.io.serialize(pipeline)

        currentView = self.viewManager.currentWidget()
        if currentView:
            currentScene = currentView.pipelineTab.pipelineView.scene()
            if currentScene.controller:
                selected_items = currentScene.get_selected_item_ids()
                selected_module_ids = selected_items[0]
                if len(selected_module_ids) > 0:
                    for id in selected_module_ids:
                        group = \
                            currentScene.controller.current_pipeline.modules[id]
                        if (group.vtType == 'group' or 
                            group.vtType == 'abstraction'):
                            pipelineMainWindow = QtGui.QMainWindow(self)
                            pipelineView = QPipelineView()
                            controller = DummyController(group.pipeline)
                            pipelineView.controller = controller
                            pipelineMainWindow.setCentralWidget(pipelineView)
                            pipelineView.scene().controller = \
                                controller
                            controller.current_pipeline_view = \
                                pipelineView.scene()
                            group.pipeline.ensure_connection_specs()
                            pipelineView.scene().setupScene(group.pipeline)
                            pipelineView.scene().fitToView(pipelineView, True)
                            self.groupPipelineView = pipelineView
                            pipelineView.show()
                            pipelineMainWindow.show()

    def openAbstraction(self, filename):
        locator = XMLFileLocator(filename)
        self.open_vistrail_without_prompt(locator, None, False, True)

    def editAbstraction(self):
        currentView = self.viewManager.currentWidget()
        if currentView:
            currentScene = currentView.pipelineTab.pipelineView.scene()
            if currentScene.controller:
                selected_items = currentScene.get_selected_item_ids()
                selected_module_ids = selected_items[0]
                if len(selected_module_ids) > 0:
                    for id in selected_module_ids:
                        abstraction = \
                            currentScene.controller.current_pipeline.modules[id]
                        if abstraction.vtType == 'abstraction':
                            desc = abstraction.module_descriptor
                            filename = desc.module.vt_fname
                            self.openAbstraction(filename)

    def expandBranch(self):
        """ expandBranch() -> None
        Expand branch of tree

        """
        controller = self.viewManager.currentWidget().controller
        controller.expand_or_collapse_all_versions_below(controller.current_version, True)

    def collapseBranch(self):
        """ collapseBranch() -> None
        Collapse branch of tree

        """
        controller = self.viewManager.currentWidget().controller
        controller.expand_or_collapse_all_versions_below(controller.current_version, False)

    def collapseAll(self):
        """ collapseAll() -> None
        Collapse all branches of tree

        """
        controller = self.viewManager.currentWidget().controller
        controller.collapse_all_versions()

    def hideBranch(self):
        """ hideBranch() -> None
        Hide node and all children

        """
        controller = self.viewManager.currentWidget().controller
        controller.hide_versions_below(controller.current_version)

    def showAll(self):
        """ showAll() -> None
        Show all hidden nodes

        """
        controller = self.viewManager.currentWidget().controller
        controller.show_all_versions()
        
    def execute(self, index):
        """ execute(index: int) -> None
        Execute something depending on the view

        """
        if index == 2:
            self.queryVistrail()
        elif index == 3:
            self.execute_current_exploration()
        else:
            self.execute_current_pipeline()

    def queryVistrail(self):
        """ queryVistrail() -> None
        Execute a query and switch to history view if in query or explore mode

        """
        if self.viewIndex > 1:
            self.viewModeChanged(1)
        self.viewManager.queryVistrail()

    def flush_cache(self):
        core.interpreter.cached.CachedInterpreter.flush()

    def execute_current_exploration(self):
        """execute_current_exploration() -> None
        Executes the current parameter exploration, if possible.

        """
        if self._executing:
            return
        self._executing = True
        try:
            self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                      False)
            self.viewManager.executeCurrentExploration()
        finally:
            self._executing = False
            self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                      True)

    def execute_current_pipeline(self):
        """execute_current_pipeline() -> None
        Executes the current pipeline, if possible.

        """
        if self._executing:
            return
        self._executing = True
        try:
            self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                      False)
            self.viewManager.executeCurrentPipeline()
        finally:
            self._executing = False
            self.emit(QtCore.SIGNAL("executeEnabledChanged(bool)"),
                      True)

    def interactiveExportCurrentPipeline(self):
        """ interactiveExportPipeline()
        Hide the builder window and show the spreadsheet window with
        only cells belonging to the pipeline specified by locator:version
        
        """
        from packages.spreadsheet.spreadsheet_controller import spreadsheetController
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
        
        from core.inspector import PipelineInspector
        currentView = self.viewManager.currentWidget()
        controller = currentView.controller
        inspector = PipelineInspector()
        pipeline = controller.current_pipeline
        inspector.inspect_spreadsheet_cells(pipeline)
        inspector.inspect_ambiguous_modules(pipeline)
        vCol = 0
        cells = {}
        for mId in inspector.spreadsheet_cells:
            name = pipeline.modules[mId].name
            if inspector.annotated_modules.has_key(mId):
                idx = inspector.annotated_modules[mId]
            else:
                idx = -1                
            cells[(name, idx)] = (0, vCol)
            vCol += 1
            
        self.hide()
        spreadsheetWindow.prepareReviewingMode(vCol)
        from gui.paramexplore.virtual_cell import _positionPipelines
        [newPipeline] = _positionPipelines('Pipeline Review',
                                           1, 1, 1, [pipeline],
                                           (1, vCol, cells), pipeline)
        controller.execute_workflow_list([(controller.locator,
                                           controller.current_version,
                                           newPipeline,
                                           controller.current_pipeline_view,
                                           None)])
        
        spreadsheetWindow.startReviewingMode()

################################################################################


# import unittest
# import api

# class TestBuilderWindow(unittest.TestCase):

#     def test_close_actions_enabled(self):
        
