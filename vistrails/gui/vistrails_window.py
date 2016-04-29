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
""" The file describes a container widget consisting of a pipeline
view and a version tree for each opened Vistrail """
from __future__ import division

from PyQt4 import QtCore, QtGui
import copy

from vistrails.core.configuration import (get_vistrails_configuration,
                                get_vistrails_persistent_configuration)
from vistrails.core.db.locator import FileLocator, XMLFileLocator, DBLocator, \
    UntitledLocator
from vistrails.core.interpreter.cached import CachedInterpreter
from vistrails.core.recent_vistrails import RecentVistrailList
import vistrails.core.system
import vistrails.core.db.action
from vistrails.core.reportusage import record_vistrail
from vistrails.core.system import vistrails_default_file_type
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core import debug

from vistrails.gui.application import get_vistrails_application
from vistrails.gui.preferences import QPreferencesDialog
from vistrails.gui.base_view import BaseView
from vistrails.gui.common_widgets import QToolWindow
from vistrails.gui.repository import QRepositoryDialog
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.utils import build_custom_window
from vistrails.gui.vistrail_view import QVistrailView
from vistrails.gui import merge_gui
from vistrails.gui.vistrail_variables import QVistrailVariables
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
from vistrails.gui.modules.constant_configuration import ConstantWidgetMixin
from vistrails.gui.paramexplore.pe_view import QParamExploreView
from vistrails.gui.mashups.alias_inspector import QAliasInspector
from vistrails.gui.mashups.mashup_view import QMashupViewTab
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget
from vistrails.db.services.io import SaveBundle
import vistrails.db.services.vistrail
from vistrails.db import VistrailsDBException

class QBaseViewWindow(QtGui.QMainWindow):
    def __init__(self, view=None, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
       
        self.view = view

        if self.view is not None:
            self.setCentralWidget(view)
            self.view.setVisible(True)
        
        self.create_actions_and_toolbar()
        
    def create_actions_and_toolbar(self):
        self.create_actions()
        self.init_toolbar()
        
    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("viewWasClosed"), self.view)
        event.accept()
    
    def init_toolbar(self):
        pass
    
    def get_current_view(self):
        if self.view is None:
            return None
        return self.view.vistrail_view
    
    def get_current_tab(self):
        return self.view
    
    def get_current_scene(self):
        return self.get_current_tab().scene()
    
    def get_current_controller(self):
        if self.get_current_view() is None:
            return None
        return self.get_current_view().get_controller()
    
    def process_list(self, action_list, parent, qactions, qmenus):
        for data in action_list:
            if data == "---":
                if parent is not None:
                    parent.addSeparator()
                continue
            name, title, options = data
            if isinstance(options, list):
                # menu
                if parent is not None:
                    qmenu = parent.addMenu(title)
                qmenus[name] = qmenu
                self.process_list(options, qmenu, qactions, qmenus)
            else:
                qaction = QtGui.QAction(title, self)
                callback = None
                if 'callback' in options:
                    callback = options['callback']
                    del options['callback']
                for option, value in options.iteritems():
                    method = getattr(qaction, 'set%s' % \
                                         option[0].capitalize() + \
                                         option[1:])
                    method(value)
                qactions[name] = qaction
                if parent is not None:
                    parent.addAction(qaction)
                if callback is not None:
                    if 'checkable' in options and \
                            options['checkable'] is True:
                        self.connect(qaction, 
                                     QtCore.SIGNAL("toggled(bool)"),
                                     callback)
                    else:
                        self.connect(qaction, QtCore.SIGNAL("triggered()"),
                                     callback)

    def init_action_list(self):
        self._actions = [("file", "&File",
                   [("export", "Export",
                      [('savePDF', "PDF...",
                        {'statusTip': "Save the current view to a PDF file",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_tab,
                                                       'save_pdf')}),
                       ('saveDOT', "Version tree to Graphviz DOT...",
                        {'statusTip': "Save the version view to a Graphviz "
                             "DOT file",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_view,
                                                       'save_version_graph')}),
                       "---",
                       ('saveWorkflow', "Workflow To XML...",
                        {'statusTip': "Save the current workflow to a file",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       FileLocator())}),
                       ('exportWorkflow', "Workflow to DB...",
                        {'statusTip': "Save the current workflow to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       DBLocator)})]),
                       "---",
                       ('close', "Close",
                        {'shortcut': QtGui.QKeySequence.Close,
                        'statusTip': "Close the current window",
                         'enabled': True,
                         'callback': self.close})]),
                   ("edit", "&Edit",
                    [("undo", "Undo",
                      {'statusTip': "Undo the previous action",
                       'shortcut': QtGui.QKeySequence.Undo,
                       'callback': _app.pass_through(self.get_current_view,
                                                     'undo'),
                       'enabled': False}),
                     ("redo", "Redo",
                      {'statusTip': "Redo an undone action",
                       'shortcut': QtGui.QKeySequence.Redo,
                       'callback': _app.pass_through(self.get_current_view,
                                                     'redo'),
                       'enabled': False}),
                     "---",
                     ("copy", "Copy",
                      {'statusTip': "Copy the selected modules in the " \
                           "current pipeline view",
                       'shortcut': QtGui.QKeySequence.Copy,
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'copySelection')}),
                     ("paste", "Paste",
                      {'statusTip': "Paste modules from the clipboard into " \
                           "the current pipeline view",
                       'shortcut': QtGui.QKeySequence.Paste,
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'pasteFromClipboard')}),
                     ("selectAll", "Select All",
                      {'statusTip': "Select all modules in the current " \
                           "pipeline view",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.SelectAll,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'selectAll')}),
                     "---",
                     ("controlFlowAssist", "Control Flow Assistant",
                      {'callback': _app.pass_through(self.get_current_tab,
                                                     'run_control_flow_assist'),
                       'statusTip': "Create a loop over the selected modules",
                       })]),
                   ("run", "&Workflow",
                    [("execute", "Execute",
                      {'icon': CurrentTheme.EXECUTE_PIPELINE_ICON,
                       'shortcut': 'Ctrl+Return',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_view,
                                                     'execute')}),
                     ("stop_on_error", "Stop on first error",
                      {'checkable': True,
                       'callback': _app.set_stop_on_error}),
                     ("flushCache", "Erase Cache Contents", 
                      {'enabled': True,
                       'callback': _app.flush_cache}),
                     "---",
                     ("layout", "Re-Layout",
                      {'statusTip': "Move all modules to create a clean " \
                           "layout for the workflow",
                       'shortcut': 'Ctrl+L',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'layout')}),
                     ("group", "Group",
                      {'statusTip': "Group the selected modules in the " \
                           "current pipeline view",
                       'shortcut': 'Ctrl+G',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'group')}),
                     ("ungroup", "Ungroup",
                      {'statusTip': "Ungroup the selected groups in the " \
                           "current pipeline view",
                       'shortcut': 'Ctrl+Shift+G',
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'ungroup')}),
                     ("showGroup", "Show Pipeline",
                      {'statusTip': "Show the underlying pipeline for the " \
                           "selected group in the current pipeline view",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_view, 
                                                     'show_group')}),
                     "---",
                     ("makeAbstraction", "Create Subworkflow",
                      {'statusTip': "Create a subworkflow from the selected " \
                           "modules",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'makeAbstraction')}),
                     ("convertToAbstraction", "Convert to Subworkflow",
                      {'statusTip': "Convert selected group to a subworkflow",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'convertToAbstraction')}),
                     ("editAbstraction", "Edit Subworkflow",
                      {'statusTip': "Edit a subworkflow",
                       'enabled': False,
                       'callback': _app.edit_abstraction}),
                     ("importAbstraction", "Import Subworkflow",
                      {'statusTip': "Import subworkflow from a vistrail to " \
                           "local subworkflows",
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'importAbstraction')}),
                     ("exportAbstraction", "Export Subworkflow",
                      {'statusTip': "Export subworkflow from local " \
                           "subworkflows for use in a package",
                       'enabled': False,
                       'callback': _app.pass_through(_app.get_current_scene,
                                                     'exportAbstraction')}),
                     "---",
                     ("configureModule", "Configure Module...",
                      {'shortcut': "Ctrl+E",
                       'enabled': False,
                       'callback': _app.configure_module}),
                     ("documentModule", "Module Documentation...",
                      {'enabled': False,
                       'callback': _app.show_documentation})]),
                   ("view", "&Views",
                    [("zoomToFit", "Zoom To Fit",
                      {'enabled': True,
                       'shortcut': "Ctrl+R",
                       'statusTip': "Fit current view to window",
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomToFit')}),
                     ("zoomIn", "Zoom In",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomIn,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomIn')}),
                     ("zoomOut", "Zoom Out",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomOut,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomOut')})]),
                   ("publish", "Publish",
                    [("publishPaper", "To Paper...", 
                      {'enabled': True,
                       'statusTip': \
                           "Embed workflow and results into a paper",
                        'callback': _app.pass_through(self.get_current_view,
                                                      'publish_to_paper')}),
                     ("publishWeb", "To Wiki...",
                      {'enabled': True,
                       'statusTip': "Embed workflow in wiki",
                       'callback' : _app.pass_through(self.get_current_view,
                                                      'publish_to_web')}),
                     ("publishCrowdLabs", "To crowdLabs...",
                      {'enabled': True,
                       'statusTip': "Publish workflows on crowdlabs.org",
                       'callback': _app.publish_to_crowdlabs})]),
                    ("window", "Window", 
                      []),
                   ("help", "Help",
                    [("help", "About VisTrails...", 
                      {'callback': _app.showAboutMessage}),
                     ("checkUpdate", "Check for Updates", 
                      {'callback': _app.showUpdatesMessage})])]
                    
    def create_actions(self):
        self.init_action_list()

        self.qactions = {}
        self.qmenus = {}

        menu_bar = self.menuBar()
        #print 'menu_bar:', menu_bar
        self.process_list(self._actions, menu_bar, self.qactions, self.qmenus)
        #print 'done processing list'
        
class QVistrailViewWindow(QBaseViewWindow):
    def __init__(self, view=None, parent=None, f=QtCore.Qt.WindowFlags()):
        QBaseViewWindow.__init__(self, view, parent, f)
        
        self.setDocumentMode(True)
        self.view = view

        if self.view is not None:
            self.setCentralWidget(view)
            self.view.setVisible(True)
            self.setWindowTitle('%s - VisTrails' % self.view.get_name())

    def close_vistrail(self):
        return _app.close_vistrail(self.view)
        
    def closeEvent(self, event):
        if not self.close_vistrail():
            event.ignore()
        else:
            self.emit(QtCore.SIGNAL("window_closed"), self.view)
            event.accept()
        
    def get_current_controller(self):
        return self.view.get_controller()

    def get_current_view(self):
        return self.view
    
    def get_current_tab(self):
        return self.view.get_current_tab()

    def get_current_scene(self):
        return self.get_current_tab().scene()
        
    def init_toolbar(self):
        def create_spacer():
            spacer = QtGui.QWidget()
            spacer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                                  QtGui.QSizePolicy.Preferred)
            return spacer
        def create_separator():
            sep = QtGui.QWidget()
            sep.setMinimumWidth(50)
            return sep

        self.selected_mode = None
        self.toolbar = QtGui.QToolBar(self)
        
        #left side
        for action in [self.qactions[n] 
                       for n in ['newVistrail', 'openFile', 'saveFile']]:
            self.toolbar.addAction(action)
        
        self.toolbar.addWidget(create_spacer())
        
        #second group
        self.view_action_group = QtGui.QActionGroup(self)
        for action in [self.qactions[n] 
                       for n in ['pipeline', 'history', 
                                 'search', 'explore', 'provenance', 'mashup']]:
            self.toolbar.addAction(action)
            self.view_action_group.addAction(action)
        self.toolbar.addWidget(create_separator())
        # self.connect(self.view_action_group, 
        #              QtCore.SIGNAL("triggered(QAction*)"),
        #              self.view_triggered)
        #third group
        for action in [self.qactions[n] 
                       for n in ['execute']]:
            self.toolbar.addAction(action)
            
        
        self.toolbar.addWidget(create_spacer())
        self.toolbar.addWidget(create_spacer())
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        self.setUnifiedTitleAndToolBarOnMac(True)

    def set_title(self, title):
        self.setWindowTitle('%s - VisTrails' % title)
        
    def get_name(self):
        return self.windowTitle()

    def set_name(self):
        if self.view:
            self.set_title(self.view.get_name())
        else:
            self.set_title('(empty)')

    def build_packages_menu_from_main_app(self):
        if len(self._package_menu_items) == 0:
            self.qmenus['packages'].menuAction().setEnabled(True)
            
        for (pkg_id, d) in _app._package_menu_items.iteritems():
            self._package_menu_items[pkg_id] = {}
            for pkg_name,items in d['items']:
                pkg_menu = self.qmenus['packages'].addMenu(str(pkg_name))
                self._package_menu_items[pkg_id]['menu'] = pkg_menu
                self._package_menu_items[pkg_id]['items'] = (pkg_name, items)
                for item in items:
                    (name, callback) = item
                    action = QtGui.QAction(name, self,
                                           triggered=callback)
                    pkg_menu.addAction(action)

    def init_action_list(self):
        # This keeps track of the menu items for each package
        self._package_menu_items = {}
        
        self.all_palette_actions =  _app.create_palette_actions()
        tools_actions = []
        palette_actions = []
        for a,p in self.all_palette_actions:
            if p.toolWindow().window() == _app.palette_window:
                tools_actions.append(a)
            else:
                palette_actions.append(a)
        
        QBaseViewWindow.init_action_list(self)
        #FIXME: 
        #The menus that are different from the base class' menus are being 
        # replaced in place. It would be much cleaner to create a function 
        # to add/replace a menu item of a menu.
        
        self._actions[0] = ("file", "&File",
                    [('newVistrail', "&New",
                      {'icon': CurrentTheme.NEW_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.New,
                       'statusTip': 'Create a new vistrail',
                       'callback': _app.new_vistrail}),
                     ('openFile', "&Open",
                      {'icon': CurrentTheme.OPEN_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.Open,
                       'statusTip': 'Open an existing vistrail from a file',
                       'callback': _app.open_vistrail_default}),
                     ("openRecent", "Open Recent", 
                      []),
                     ('saveFile', "&Save",
                      {'icon': CurrentTheme.SAVE_VISTRAIL_ICON,
                       'shortcut': QtGui.QKeySequence.Save,
                       'statusTip': "Save the current vistrail to a file",
                       'enabled': False,
                       'callback': \
                           _app.pass_through_locator(self.get_current_view,
                                                     'save_vistrail')}),
                     ('saveFileAs', "Save as...",
                      {'shortcut': QtGui.QKeySequence.SaveAs,
                       'statusTip': "Save the current vistrail to a " \
                           "different file location",
                       'enabled': False,
                       'callback': \
                           _app.pass_through_locator(self.get_current_view,
                                                     'save_vistrail_as')}),
                     ('saveToOther', "Save To DB...",
                      {'statusTip': "Save the current vistrail to a " \
                           "database",
                       'enabled': True,
                       'callback': \
                           _app.pass_through_locator(self.get_current_view,
                                                     'save_vistrail_as', 
                                                     reverse=True)}),
                     ('closeVistrail', "Close",
                      {'shortcut': QtGui.QKeySequence.Close,
                       'statusTip': "Close the current vistrail",
                       'enabled': False,
                       'callback': _app.close_vistrail}),
                     "---",
                     ("import", "Import",
                      [('importFile', "From DB...",
                        {'icon': CurrentTheme.OPEN_VISTRAIL_DB_ICON,
                         'statusTip': "Import an existing vistrail " \
                             "from a database",
                         'callback': \
                             _app.import_vistrail_default}),
                       "---",
                       ('importWorkflow', "Workflow...",
                        {'statusTip': "Import a workflow from an XML file",
                         'enabled': True,
                         'callback': _app.import_workflow_default}),
                       ('importWorkflowDB', "Workflow from DB...",
                        {'statusTip': "Import a workflow from a database",
                         'enabled': True,
                         'callback': _app.import_workflow_from_db})]),
                     ("export", "Export",
                      [('exportFile', "To DB...",
                        {'statusTip': "Export the current vistrail to a " \
                             "database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'export_vistrail', 
                                                       reverse=True)}),
                       "---",
                       ('savePDF', "PDF...",
                        {'statusTip': "Save the current view to a PDF file",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_tab,
                                                       'save_pdf')}),
                       ('saveDOT', "Version tree to Graphviz DOT...",
                        {'statusTip': "Save the version view to a Graphviz "
                             "DOT file",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_view,
                                                       'save_version_graph')}),
                       "---",
                       ('saveWorkflow', "Workflow To XML...",
                        {'statusTip': "Save the current workflow to a file",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       FileLocator())}),
                       ('exportWorkflow', "Workflow to DB...",
                        {'statusTip': "Save the current workflow to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_workflow',
                                                       DBLocator)}),
                       ('exportStable', "Workflow to VisTrails 2.1 XML...",
                        {'statusTip': "Save workflow as XML according to " \
                             "the previous schema",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'export_stable')}),
                       "---",
                       ('saveOpm', "OPM XML...",
                        {'statusTip': "Save provenance according to the " \
                             "Open Provenance Model in XML",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_view,
                                                       'save_opm')}),
                       ('saveProv', "PROV Document...",
                        {'statusTip': "Saves provenance according to " \
                             "PROV-DM in XML",
                         'enabled': True,
                         'callback': _app.pass_through(self.get_current_view,
                                                       'save_prov')}),
                       ('saveLog', "Log to XML...",
                        {'statusTip': "Save the execution log to a file",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_log',
                                                       FileLocator())}),
                       ('exportLog', "Log to DB...",
                        {'statusTip': "Save the execution log to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_log',
                                                       DBLocator)}),
                       "---",
                       ('saveRegistry', "Registry to XML...",
                        {'statusTip': "Save the current registry to a file",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_registry',
                                                       FileLocator())}),
                       ('exportRegistry', "Registry to DB...",
                        {'statusTip': "Save the current registry to a database",
                         'enabled': True,
                         'callback': \
                             _app.pass_through_locator(self.get_current_view,
                                                       'save_registry',
                                                       DBLocator)})]),
                     "---",
                     ('quitVistrails', "Quit",
                      {'shortcut': QtGui.QKeySequence.Quit,
                       'statusTip': "Exit VisTrails",
                       'callback': _app.quit})])
        
        self._actions[1] = ("edit", "&Edit",
                    [("undo", "Undo",
                      {'statusTip': "Undo the previous action",
                       'shortcut': QtGui.QKeySequence.Undo,
                       'callback': _app.pass_through(self.get_current_view,
                                                     'undo'),
                       'enabled': False}),
                     ("redo", "Redo",
                      {'statusTip': "Redo an undone action",
                       'shortcut': QtGui.QKeySequence.Redo,
                       'callback': _app.pass_through(self.get_current_view,
                                                     'redo'),
                       'enabled': False}),
                     "---",
                     ("copy", "Copy",
                      {'statusTip': "Copy the selected modules in the " \
                           "current pipeline view",
                       'shortcut': QtGui.QKeySequence.Copy,
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'copySelection')}),
                     ("paste", "Paste",
                      {'statusTip': "Paste modules from the clipboard into " \
                           "the current pipeline view",
                       'shortcut': QtGui.QKeySequence.Paste,
                       'enabled': False,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'pasteFromClipboard')}),
                     ("selectAll", "Select All",
                      {'statusTip': "Select all modules in the current " \
                           "pipeline view",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.SelectAll,
                       'callback': _app.pass_through(self.get_current_scene,
                                                     'selectAll')}),
                     "---",
                     ("controlFlowAssist", "Control Flow Assistant",
                      {'callback': _app.pass_through(self.get_current_tab,
                                                     'run_control_flow_assist'),
                       'statusTip': "Create a loop over the selected modules",
                       }),
                     ("merge", "Merge with...", 
                      []),
                     "---",
                     ("editPreferences", "Preferences...",
                      {'statusTip': "Edit system preferences",
                       'enabled': True,
                       'shortcut': QtGui.QKeySequence.Preferences,
                       'callback': _app.showPreferences}),
                     ])
        self._actions.insert(3, ("vistrail", "Vis&trail",
                    [("tag", "Tag...",
                      {'statusTip': "Tag the current pipeline",
                       'shortcut': "Ctrl+Shift+T",
                       'enabled': True,
                       'callback': _app.add_tag}),
                     "---",
                     ("reLayout", "Re-Layout",
                      {'statusTip': "Re-layouts the version tree",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'invalidate_version_tree')}),
                     ("expandBranch", "Expand Branch",
                      {'statusTip': "Expand all versions in the tree below " \
                           "the current version",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'expand_all_versions_below')}),
                     ("collapseBranch", "Collapse Branch",
                      {'statusTip': "Collapse all expanded versions of the " \
                           "tree",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'collapse_all_versions_below')}),
                     ("collapseAll", "Collapse All",
                      {'statusTip': "Collapse all expanded branches of the " \
                           "tree",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'collapse_all_versions')}),
                     ("hideBranch", "Hide Branch",
                      {'statusTip': "Hide all versions in the tree including " \
                           "and below the current version",
                       'enabled': True,
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'hide_versions_below')}),
                     ("showAll", "Show All",
                      {'enabled': True,
                       'statusTip': "Show all hidden versions",
                       'callback': \
                           _app.pass_through(self.get_current_controller,
                                             'show_all_versions')})]))
        
        self._actions[4] = ("view", "&Views",
                    [("newView", "New Pipeline View",
                      {'shortcut': QtGui.QKeySequence.AddTab,
                       'enabled': True,
                       'statusTip': "Create a new pipeline view",
                       'callback': _app.pass_through(self.get_current_view,
                                                     'add_pipeline_view')}),
                     ("newDiff", "New Visual Difference",
                      {'enabled': True,
                       'statusTip': "Create a new visual difference for two" \
                           "pipelines",
                       'callback': _app.new_diff}),
                     "---",
                     ("zoomToFit", "Zoom To Fit",
                      {'enabled': True,
                       'shortcut': "Ctrl+R",
                       'statusTip': "Fit current view to window",
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomToFit')}),
                     ("zoomIn", "Zoom In",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomIn,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomIn')}),
                     ("zoomOut", "Zoom Out",
                      {'enabled': True,
                       'shortcut': QtGui.QKeySequence.ZoomOut,
                       'callback': _app.pass_through(self.get_current_tab,
                                                     'zoomOut')}),
                     "---",
                     ("pipeline", "Pipeline",
                      {'icon': CurrentTheme.PIPELINE_ICON,
                       'checkable': True,
                       'checked': True,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'pipeline_change')}),
                     ("history", "History",
                      {'icon': CurrentTheme.HISTORY_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'history_change')}),
                     ("search", "Search",
                      {'icon': CurrentTheme.QUERY_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'search_change')}),
                     ("explore", "Explore",
                      {'icon': CurrentTheme.EXPLORE_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'explore_change')}),
                     ("provenance", "Provenance",
                      {'icon': CurrentTheme.PROVENANCE_ICON,
                       'checkable': True,
                       'checked': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'provenance_change')}),
                    ("mashup", "Mashup",
                      {'icon': CurrentTheme.MASHUP_ICON,
                       'checkable': True,
                       'checked': False,
                       'enabled': False,
                       'callback': \
                           _app.pass_through_bool(self.get_current_view,
                                                  'mashup_change')}),
                     "---"] +
                    palette_actions + 
                    ["---"] + 
                    tools_actions + 
                    ["---", 
                     ("dockPalettes", "Dock Palettes", 
                      {'enabled': True,
                       'statusTip': "Dock palettes on active window",
                       'callback': _app.dock_palettes})])
        self._actions.insert(6, ("packages", "Packages", 
                                     []))
    
    def create_actions(self):
        """ createActions() -> None 

        Construct all menu/toolbar actions for window.

        """

        # format of each item in the list is:
        # item: reference, title, options
        # where options is either a list of subitems or
        # a dictionary of options to be set for an action
        # Also, "---" denotes a separator

        is_main_window = False
        if self == _app:
            is_main_window = True

        #global _global_menubar
        
        # palettes = []
        # palette_actions = []

        self.init_action_list()

        self.qactions = {}
        self.qmenus = {}

        #if is_main_window and core.system.systemType in ['Darwin']:
            # menu_bar = QtGui.QMenuBar()
            #_global_menubar = menu_bar
        #else:
        menu_bar = self.menuBar()
        #print 'menu_bar:', menu_bar
        self.process_list(self._actions, menu_bar, self.qactions, self.qmenus)
        #print 'done processing list'
        
        if is_main_window:
            for action_tuple, palette in self.all_palette_actions:
                palette.set_action(self.qactions[action_tuple[0]])
            _app.connect_package_manager_signals()
        else:
            self.build_packages_menu_from_main_app()

        self.qactions['stop_on_error'].setChecked(
                getattr(get_vistrails_configuration(), 'stopOnError'))

        # view_menu = self.qmenus["view"]
        # for action_name, action in self.create_palette_actions():
        #     self.qactions[action_name] = action
        #     view_menu.addAction(action)

class QVistrailsWindow(QVistrailViewWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        global _app
        _app = self

        QVistrailViewWindow.__init__(self, None, parent, f)

        self.stack = QtGui.QStackedWidget()
        self.vistrail_widgets = []
        self.setCentralWidget(self.stack)        
        self.auto_view = True

        self._focus_owner = None
        self._previous_view = None
        self._is_quitting = False
        self._first_view = True
        self.connect(QtGui.QApplication.clipboard(),
                     QtCore.SIGNAL('dataChanged()'),
                     self.clipboard_changed)
        self.connect(QtGui.QApplication.instance(),
                     QtCore.SIGNAL("focusChanged(QWidget*,QWidget*)"),
                     self.applicationFocusChanged)

        self.preferencesDialog = QPreferencesDialog(self)

        # To track the current view we need to track all mouse clicks
        builder = self
        class FocusEvent(QtGui.QWidget):
            def __init__(self):
                QtGui.QWidget.__init__(self)
                self.old_focus = None
                self.vt_app = get_vistrails_application()
            def eventFilter(self, object, event):
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    # object may be the old one when this window gets focus
                    object = self.vt_app.widgetAt(QtGui.QCursor.pos())
                    if object != self.old_focus:
                        builder.applicationFocusChanged(self.old_focus, object)
                        self.old_focus = object
                return False
        self.focusEvent = FocusEvent()
        self.focusEvent.vt_app.installEventFilter(self.focusEvent)

        if get_vistrails_configuration().detachHistoryView:
            self.history_view = QBaseViewWindow(parent=None)
            self.history_view.resize(800, 600)
            from vistrails.gui.version_prop import QVersionProp
            inst = QVersionProp.instance().toolWindow()
            self.history_view.addDockWidget(QtCore.Qt.RightDockWidgetArea,inst)
            self.history_view.stack = QtGui.QStackedWidget()
            self.history_view.setCentralWidget(self.history_view.stack)
            self.history_view.show()
            self.history_view.move(self.rect().center())
            self.history_view.setWindowTitle('Version Tree')

    def create_actions_and_toolbar(self):
        self.current_view = None
        self.windows = {}
        self.base_view_windows = {}
        self.notifications = {}
        self.view_notifications = {}
        self.view_notifications[-1] = {}
        self.action_links = {}
        self.dbDefault = False

        self.init_palettes()
        self.create_menus()
        self.setup_recent_vistrails()
        self.init_toolbar()

    def create_view(self, vistrail, locator,  abstraction_files=None, 
                    thumbnail_files=None, mashups=None):
        view = QVistrailView(vistrail, locator, abstraction_files,
                             thumbnail_files, mashups)
        self.vistrail_widgets.append(view)
        index = self.stack.addWidget(view)
        self.stack.setCurrentIndex(index)
        self.view_notifications[view] = {}
        for notification_id, method_list in \
                view.get_notifications().iteritems():
            for method in method_list:
                self.register_notification(notification_id, method, True, view)
        return view

    def remove_view(self, view):
        from vistrails.gui.collection.workspace import QWorkspaceWindow
        if view not in self.windows:
            if view in self.view_notifications:
                del self.view_notifications[view]
            self.stack.removeWidget(view)
        else:
            window = self.windows[view]
            window.close()
        QWorkspaceWindow.instance().remove_vt_window(view)

        # DK: **Do not** set current_view here because remove_vistrail
        # calls change_view which sends notifications that there is
        # not current controller
        #
        # self.current_view = None

    def view_triggered(self, action):
        #print "VIEW_TRIGGERED", action
        if self.selected_mode == action:
            if action is not None:
                #print "SETTING CHECKED FALSE"
                action.setChecked(False)
            self.selected_mode = None
        else:
            self.selected_mode = action
        current_view = self.stack.currentWidget()
        current_view.tab_state[current_view.tabs.currentIndex()] = \
            self.selected_mode
        current_view.view_changed()

    def action_triggered(self, action):
        if self.selected_mode is not None:
            self.selected_mode.un_method()
        if self.selected_mode != action:
            self.selected_mode = action
            if action is not None:
                action.method()
        elif self.selected_mode is not None:
            self.selected_mode = None
            action.setChecked(False)
        current_view = self.stack.currentWidget()
        current_view.tab_state[current_view.tabs.currentIndex()] = \
            self.selected_mode
        current_view.view_changed()

    # enumeration for dock areas
    (UPPER_LEFT_DOCK_AREA, LOWER_LEFT_DOCK_AREA, RIGHT_DOCK_AREA,
     UTILITY_WINDOW_AREA) = range(4)
    DOCK_AREA_MAP = {UPPER_LEFT_DOCK_AREA: QtCore.Qt.LeftDockWidgetArea,
                     LOWER_LEFT_DOCK_AREA: QtCore.Qt.LeftDockWidgetArea,
                     RIGHT_DOCK_AREA: QtCore.Qt.RightDockWidgetArea,
                     UTILITY_WINDOW_AREA: QtCore.Qt.NoDockWidgetArea}

    def init_palettes(self):
        # palettes are global!
        from vistrails.gui.debug import DebugView
        from vistrails.gui.job_monitor import QJobView
        from vistrails.gui.debugger import QDebugger
        from vistrails.gui.module_configuration import QModuleConfiguration
        from vistrails.gui.module_documentation import QModuleDocumentation
        from vistrails.gui.module_options import QModuleOptions
        from vistrails.gui.module_palette import QModulePalette
        from vistrails.gui.module_info import QModuleInfo
        from vistrails.gui.paramexplore.param_view import QParameterView
        from vistrails.gui.paramexplore.pe_inspector import QParamExploreInspector
        from vistrails.gui.shell import get_shell_dialog
        from vistrails.gui.version_prop import QVersionProp
        from vistrails.gui.vis_diff import QDiffProperties
        from vistrails.gui.collection.explorer import QExplorerWindow
        from vistrails.gui.collection.workspace import QWorkspaceWindow
        from vistrails.gui.collection.vis_log import QLogDetails
        from vistrails.gui.mashups.mashups_inspector import QMashupsInspector
        from vistrails.gui.mashups.alias_parameter_view import QAliasParameterView
        from vistrails.gui.publishing import QVersionEmbed
        self.palettes = []
        self.palette_window = None

        self.palette_layout = \
            [(self.UPPER_LEFT_DOCK_AREA,
              [((QWorkspaceWindow,True),
                (('search_changed', 'updateSearchResults'),
                 ('execution_updated', 'execution_updated'),
                 ('state_changed', 'state_changed')))]),
             (self.LOWER_LEFT_DOCK_AREA,
              [(QModulePalette, True),
               ((QParamExploreInspector, False),
                (('controller_changed', 'set_controller'),)),
               ((QMashupsInspector, False),
                (('controller_changed', 'updateVistrailController'),
                 ('mshpcontroller_changed', 'updateMshpController'),
                 ('mshpversion_changed', 'updateMshpVersion'),
                 ('version_changed', 'updateVistrailVersion')))]),
             (self.RIGHT_DOCK_AREA,
              [((QModuleInfo, True),
                (('controller_changed', 'set_controller'),
                 ('module_changed', 'update_module'),
                 ('entry_klass_changed', 'update_entry_klass'))),
               ((QVersionProp, True),
                (('controller_changed', 'updateController'),
                 ('version_changed', 'updateVersion'))),
               ((QDiffProperties, False),
                (('controller_changed', 'set_controller'),
                 ('module_changed', 'update_module'))),
               ((QParameterView, False),
                (('pipeline_changed', 'set_pipeline'),
                 ('controller_changed', 'set_controller'))),
               ((QLogDetails, False),
                (('controller_changed', 'set_controller'),
                 ('execution_updated', 'execution_updated'),
                 ('execution_changed', 'execution_changed'))),
               ((QAliasParameterView, False),
                (('mshpcontroller_changed', 'updateMshpController'),
                 ('mshpversion_changed', 'updateMshpVersion'))),
               ((QVistrailVariables, False),
                (('controller_changed', 'updateController'),))]),
             (self.UTILITY_WINDOW_AREA,
              [((QModuleConfiguration, True),
                (('controller_changed', 'set_controller'),
                 ('module_changed', 'updateModule'))),
               ((QModuleDocumentation, True),
                (('controller_changed', 'set_controller'),
                 ('module_changed', 'update_module'),
                 ('descriptor_changed', 'update_descriptor'))),
               ((QModuleOptions, True),
                (('controller_changed', 'set_controller'),
                 ('module_changed', 'update_module')))] +
              ([] if not get_shell_dialog() else [
               ((get_shell_dialog(), True),
                (('controller_changed', 'set_controller'),))]) +
              [((QDebugger, True),
                (('controller_changed', 'set_controller'),)),
               (DebugView, True),
               ((QJobView, True),
                (('controller_changed', 'set_controller'),)),
               (QExplorerWindow, True),
#               ((QLatexAssistant, True),
#                (('controller_changed', 'set_controller'),)),
               ((QVersionEmbed, True),
                (('controller_changed', 'set_controller'),
                 ('vistrail_saved', 'updateEmbedText'),
                 ('version_changed', 'updateVersion')))])]
        
        left_added = None
        self.palette_window = QPaletteMainWindow()
        self.palette_window.setWindowTitle('VisTrails - Tools')
        self.palette_window.setGeometry(200, 200, 768, 512)
        self.palette_window.setDocumentMode(True)
        for dock_area, p_group in self.palette_layout:
            first_added = None
            for p_klass in p_group:
                notifications = []
                if isinstance(p_klass, tuple):
                    p_klass, visible = p_klass
                    if isinstance(p_klass, tuple):
                        notifications = visible
                        p_klass, visible = p_klass      
                #print "generating instance", p_klass
                palette = p_klass.instance()
                #print 'palette:', palette
                self.palettes.append(palette)
                for n_tuple in notifications:
                    #print "n_tuple:", n_tuple
                    if isinstance(n_tuple, tuple):
                        if len(n_tuple) > 1:
                            n_id, method_name = n_tuple
                        else:
                            n_id = n_tuple[0]
                            method_name = n_tuple[0]
                    else:
                        n_id = n_tuple
                        method_name = n_tuple
                    method = getattr(palette, method_name)
                    self.register_notification(n_id, method)

                # palette.toolWindow().show()
                # palette.toolWindow().setFloating(True)
                if dock_area != self.UTILITY_WINDOW_AREA:
                    palette.set_pin_status(visible)
                    qt_dock_area = self.DOCK_AREA_MAP[dock_area]
                    if first_added is None:
                        if qt_dock_area == QtCore.Qt.LeftDockWidgetArea and \
                                left_added is not None:
                            if dock_area == self.UPPER_LEFT_DOCK_AREA:
                                self.splitDockWidget(palette.toolWindow(),
                                                     left_added,
                                                     QtCore.Qt.Vertical)
                            else:
                                self.splitDockWidget(left_added,
                                                     palette.toolWindow(),
                                                     QtCore.Qt.Vertical)
                        else:
                            self.addDockWidget(qt_dock_area,
                                               palette.toolWindow())
                        first_added = palette.toolWindow()
                        if qt_dock_area == QtCore.Qt.LeftDockWidgetArea and \
                                left_added is None:
                            left_added = first_added
                    else:   
                        self.tabifyDockWidget(first_added, palette.toolWindow())
                    if not visible:
                        palette.toolWindow().close()
                else:
                    self.palette_window.addPalette(palette)
                    palette.set_main_window(self.palette_window)
                    
        if self.palette_window:
            self.palette_window.hide()
                        
        self.connect(QWorkspaceWindow.instance(), 
                     QtCore.SIGNAL("vistrailChanged(PyQt_PyObject)"),
                     self.change_view)
        self.connect(QWorkspaceWindow.instance(), 
                     QtCore.SIGNAL("detachVistrail"),
                     self.detach_view)

    def dock_palettes(self, window=None):
        if not window:
            window = QtGui.QApplication.activeWindow()
        if window == self or window in self.windows.values():
            left_first_added = None
            right_first_added = None
            for dock_area, p_group in self.palette_layout:
                for p_klass in p_group:
                
                    assert isinstance(p_klass, tuple)
                    p_klass, visible = p_klass
                    if isinstance(p_klass, tuple):
                        notifications = visible
                        p_klass, visible = p_klass
                    palette = p_klass.instance()
                    if dock_area == QtCore.Qt.RightDockWidgetArea:
                        pin_status = palette.get_pin_status()
                        palette.toolWindow().setParent(window)
                        if right_first_added is None:
                            window.addDockWidget(dock_area, palette.toolWindow())
                            right_first_added = palette.toolWindow()
                        else:
                            window.tabifyDockWidget(right_first_added, palette.toolWindow())
                    elif dock_area == QtCore.Qt.LeftDockWidgetArea:
                        pin_status = palette.get_pin_status()
                        palette.toolWindow().setParent(window)
                        if left_first_added is None:
                            window.addDockWidget(dock_area, palette.toolWindow())
                            left_first_added = palette.toolWindow()
                        else:
                            window.tabifyDockWidget(left_first_added, palette.toolWindow())
                    if not visible:
                        palette.toolWindow().close()
                    else:
                        palette.toolWindow().show()
                        
    def create_notification(self, notification_id, link_view=False, view=None):
        vt_app = get_vistrails_application()
        vt_app.create_notification(notification_id, self, view)
        # if link_view:
        #     if view is not None:
        #         notifications = self.view_notifications[view]
        # else:
        #     notifications = self.notifications
        # if notification_id not in notifications:
        #     notifications[notification_id] = set()
        # else:
        #     print "already added notification", notification_id

    def register_notification(self, notification_id, method, link_view=False,
                              view=None):
        vt_app = get_vistrails_application()
        vt_app.register_notification(notification_id, method, self, view)
        # if link_view:
        #     if view is not None:
        #         notifications = self.view_notifications[view]
        #         #print '>>> LOCAL adding notification', notification_id, view, method
        #     #print id(notifications), notifications
        #     #for n, o in notifications.iteritems():
        #     #    print "    ", n , "(%s)"%len(o)
        #     #    for m in o:
        #     #        print "        ", m
        # else:
        #     notifications = self.notifications     
        #     #print '>>> GLOBAL adding notification', notification_id, method  
        #     #print id(notifications), notifications
        # if notification_id not in notifications:
        #     self.create_notification(notification_id, link_view, view)
        # notifications[notification_id].add(method)

    def unregister_notification(self, notification_id, method, link_view=False,
                                view=None):
        vt_app = get_vistrails_application()
        vt_app.unregister_notification(notification_id, method, self, view)
        
#         if link_view:
#             notifications = {}
#             if view in self.view_notifications:
#                 notifications = self.view_notifications[view]
#                 #print '>>> LOCAL remove notification', notification_id, view
            
#             #print id(notifications), notifications
# #            for n, o in notifications.iteritems():
# #                print "    ", n , "(%s)"%len(o)
# #                for m in o:
# #                    print "        ", m
#         else:
#             notifications = self.notifications    
#             #print '>>> GLOBAL remove notification', notification_id, method   
#             #print id(notifications), notifications           
#         if notification_id in notifications:
#             notifications[notification_id].remove(method)

    def notify(self, notification_id, *args):
        vt_app = get_vistrails_application()
        vt_app.send_notification(notification_id, *args)

    def clipboard_changed(self):
        self.notify("clipboard_changed")

    def set_action_links(self, action_links, obj, view):
        link_list = []
        def get_method(_qaction, _check):
            def do_check_and_set(*args, **kwargs):
                _qaction.setEnabled(_check(*args, **kwargs))
            return do_check_and_set
        for action, (notification_id, check) in action_links.iteritems():
            window = obj.window()
            if isinstance(window, BaseView):
                window = window.vistrail_view.window()
            if action in window.qactions:
                qaction = window.qactions[action]
                method = get_method(qaction, check)
                notification = (notification_id, method, True, view)
                self.register_notification(*notification)
                link_list.append(notification)
        self.action_links[id(obj)] = link_list
    
    def unset_action_links(self, obj):
        if id(obj) in self.action_links:
            for notification in self.action_links[id(obj)]:
                self.unregister_notification(*notification)
        
    def set_action_defaults(self, obj):
        window = obj.window()
        if isinstance(window, BaseView):
            window = window.vistrail_view.window()
        qactions = window.qactions
        for action, mlist in obj.action_defaults.iteritems():
            if action in qactions:
                qaction = qactions[action]
                for (method, is_callback, value) in mlist:
                    if is_callback:
                        getattr(qaction, method)(value())
                    else:
                        getattr(qaction, method)(value)
            
    def set_name(self):
        widget = self.stack.currentWidget()
        if widget:
            self.set_title(widget.get_name())
        else:
            self.set_title('(empty)')

    # def action_triggered(self, action):
    #     if self.selected_mode is not None:
    #         self.selected_mode.un_method()
    #     if self.selected_mode != action:
    #         self.selected_mode = action
    #         if action is not None:
    #             action.method()
    #     elif self.selected_mode is not None:
    #         self.selected_mode = None
    #         action.setChecked(False)
    #     current_view = self.stack.currentWidget()
    #     current_view.tab_state[current_view.tabs.currentIndex()] = \
    #         self.selected_mode
    #     current_view.view_changed()

    # def create_pass_actions(self):
    #     actions = ['history_selected', 'history_unselected',
    #                'query_selected', 'query_unselected',
    #                'explore_selected', 'explore_unselected']
    #     def create_action(action_str):
    #         def new_action():
    #             getattr(self.stack.currentWidget(), action_str)()
    #         return new_action
    #     for action_str in actions:
    #         method = create_action(action_str)
    #         setattr(self, action_str, method)

    def sizeHint(self):
        return QtCore.QSize(1280, 768)

    def create_first_vistrail(self):
        #print 'calling create_first_vistrail'
        if self.get_current_view():
            return
        if not self.dbDefault:
            untitled_temps = UntitledLocator.all_untitled_temporaries()
            if len(untitled_temps) > 0:
                if FileLocator.prompt_autosave(self):
                    for locator in untitled_temps:
                        self.open_vistrail(locator)
                    return
                else:
                    for locator in untitled_temps:
                        locator.clean_temporaries()
        self._first_view = None
        self.new_vistrail(True)
        self._first_view = self.get_current_view()

    def change_view(self, view):
        if isinstance(view, QVistrailView) or view is None:
            self.view_changed(view)
            if view and view not in self.windows:
                if self.stack.currentWidget() != view:
                    self.stack.setCurrentWidget(view)
                    view.reset_tab_state()
            if view and get_vistrails_configuration().detachHistoryView:
                self.history_view.stack.setCurrentIndex(view.version_index)
                self.history_view.view = view.controller
        else:
            debug.warning("change_view() got a wrong view type:'%s'"%view)            

    def detach_view(self, view):
        if view not in self.windows:
            index = self.stack.indexOf(view)
            self.stack.removeWidget(view)
            window = QVistrailViewWindow(view, parent=None)
            self.windows[view] = window
            self.connect(window, QtCore.SIGNAL("window_closed"),
                         self.window_closed)
            window.qactions['history'].setChecked(True)
            window.show()
            # this is needed to make dropping modules work
            self.dock_palettes(window)
            self.dock_palettes(self)
            self.view_changed(view)
        else:
            self.view_changed(view)

    def attach_view(self, view=None):
        if not view:
            view = self.current_view
        if view not in self.windows:
            return
        window = view.window()
        self.disconnect(window, QtCore.SIGNAL("window_closed"),
                        self.window_closed)
        self.stack.addWidget(view)
        del self.windows[view]
        # disable save_vistrail call
        window.closeEvent = lambda event: event.accept()
        window.close()
        self.stack.setCurrentWidget(view)
        self.view_changed(view)
            
    def window_closed(self, view):
        if view in self.windows:
            del self.windows[view]
            
    def view_changed(self, new_view):
        """ Updates the controller when the view changes and 
            updates buttons when """
        if self.current_view != new_view:
            self.current_view = new_view
            if new_view is not None:
                self.notify('controller_changed', new_view.get_controller())
                if new_view.current_tab:
                    self.set_action_defaults(new_view.current_tab)
            else:
                self.notify('controller_changed', None)
        
        if new_view is not None:
            window = None
            if new_view in self.windows:
                window = self.windows[new_view]
            if window is None:
                if self.current_view.has_changes():
                    self.qactions['saveFile'].setEnabled(True)
                    # un-remember first view when it is changed
                    if self._first_view:
                        self._first_view = None
                else:
                    self.qactions['saveFile'].setEnabled(False)
                self.qactions['saveFileAs'].setEnabled(True)
                self.qactions['closeVistrail'].setEnabled(True)
            else:
                window.set_name()
                window.activateWindow()
                window.raise_()
                if self.current_view.has_changes():
                    window.qactions['saveFile'].setEnabled(True)
                else:
                    window.qactions['saveFile'].setEnabled(False)
                window.qactions['saveFileAs'].setEnabled(True)
                window.qactions['closeVistrail'].setEnabled(True)
        else:
            self.qactions['saveFile'].setEnabled(False)
            self.qactions['saveFileAs'].setEnabled(False)
            self.qactions['closeVistrail'].setEnabled(False)

        from vistrails.gui.collection.workspace import QWorkspaceWindow
        QWorkspaceWindow.instance().change_vt_window(new_view)
        self.update_merge_menu()
        self.update_window_menu()
        self.update_recent_vistrail_menu()
        self.set_name()

    def reset_toolbar_for_view(self, view):
        if view:
            window = view.window()
        else:
            window = self
        for action in window.view_action_group.actions():
            action.setChecked(False)
            
    def state_changed(self, view):
        """ state for the view changed so we need to update buttons"""
        self.view_changed(view)

    def new_vistrail(self, recover_files=False):
        # if self.single_document_mode and self.currentView():
        #     if not self.closeVistrail():
        #         return None
        self._first_view = None

        locator = None
        if recover_files:
            untitled_temps = UntitledLocator.all_untitled_temporaries()
            if len(untitled_temps) > 0:
                # FIXME how do we choose which one? -- really should open all
                locator = untitled_temps[0]

        self.open_vistrail(locator)
        self.qactions['pipeline'].trigger()

    def close_first_vistrail_if_necessary(self):
        # Close first vistrail of no change was made
        if not self._first_view:
            return
        if self._first_view is True:
            view = self.get_current_view()
            if not view:
                return
            vt = view.controller.vistrail
        else:
            vt = self._first_view.controller.vistrail
        if vt.get_version_count() == 0:
            #print "closing first vistrail"
            self.close_vistrail(self._first_view)
            self._first_view = None
        else:
            # We set it to none, since it's been changed, so
            # we don't want to ever close it again.
            self._first_view = None

    def ensureController(self, controller):
        """ ensureController(controller: VistrailController) -> QVistrailView        
        This will first find among the opened vistrails to see if
        controller is open. If not, it will try to open it if a locator exist.

        This should be used when you have a controller and want to open the
        associated vistrail 
        """
        if controller is None:
            return None
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            if view.controller is controller:
                self.change_view(view)
                return view
        for (view, window) in self.windows.iteritems():
            if view.controller == controller:
                window.activateWindow()
                window.raise_()
                return view
        # try to open it
        if controller.locator:
            return self.open_vistrail(controller.locator)
        return None

    def getViewFromLocator(self, locator):
        """ getViewFromLocator(locator: VistrailLocator) -> QVistrailView
        This will find the view associated with the locator. If not, it will
        return None.

        """
        if locator is None:
            return None
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            if view.controller.vistrail.locator == locator:
                return view
        for (view, window) in self.windows.iteritems():
            if view.controller.vistrail.locator == locator:
                return view
        return None

    def getAllViews(self):
        """ getAllViews() ->[QVistrailView]
        Returns all open views.

        """
        views = []
        for i in xrange(self.stack.count()):
            views.append(self.stack.widget(i))
        views.extend(self.windows)
        return views

    def ensureVistrail(self, locator):
        """ ensureVistrail(locator: VistrailLocator) -> QVistrailView        
        This will first find among the opened vistrails to see if
        vistrails from locator has been opened. If not, it will return None.
        
        """
        if locator is None:
            return None
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            if view.controller.vistrail.locator == locator:
                self.change_view(view)
                return view
        for (view, window) in self.windows.iteritems():
            if view.controller.vistrail.locator == locator:
                window.activateWindow()
                window.raise_()
                return view
        return None

    def add_vistrail(self, *objs):
        view = self.create_view(*objs)
        # view.is_abstraction = is_abstraction
        self.view_changed(view)
        self.reset_toolbar_for_view(view)
        self.qactions['history'].trigger()
        view.version_view.zoomToFit()
        return view.controller

    def remove_vistrail(self, locator):
        for view in copy.copy(self.vistrail_widgets):
            if view.controller.locator == locator:
                view.closeDetachedViews()
                self.remove_view(view)
                self.vistrail_widgets.remove(view)
                if view == self._first_view:
                    self._first_view = None
                elif not self.stack.count() and not self._is_quitting and \
                     self.auto_view:
                    self.create_first_vistrail()
                view = self.get_next_view()
                self.change_view(view)

    def select_version(self, version):
        view = self.get_current_view()
        if view is not None:
            view.version_selected(version, True, double_click=True)
            return True
        return False

    def open_vistrail(self, locator, version=None, is_abstraction=False):
        """open_vistrail(locator: Locator, version = None: int or str,
                         is_abstraction: bool)

        opens a new vistrail from the given locator, selecting the
        given version.

        """
        old_view = self.getViewFromLocator(locator)
        
        if not get_vistrails_application().open_vistrail(locator, version, 
                                                         is_abstraction):
            return None
        self.close_first_vistrail_if_necessary()
        view = self.get_current_view()
        view.is_abstraction = view.controller.is_abstraction
        if not old_view:
            # it was not already open
            from vistrails.gui.collection.workspace import QWorkspaceWindow
            QWorkspaceWindow.instance().add_vt_window(view)
        return view

    def open_vistrail_from_locator(self, locator_class):
        """ open_vistrail(locator_class) -> None
        Prompt user for information to get to a vistrail in different ways,
        depending on the locator class given.
        """
        locator = locator_class.load_from_gui(self, Vistrail.vtType)
        if locator:
            version = None
            if not self.getViewFromLocator(locator):
                if locator.has_temporaries():
                    if not locator_class.prompt_autosave(self):
                        locator.clean_temporaries()
            if hasattr(locator,'_vtag'):
                # if a tag is set, it should be used instead of the
                # version number
                if locator._vtag != '':
                    version = locator._vtag
            elif hasattr(locator, '_vnode'):
                version = locator._vnode
            mashuptrail = None
            mashupversion = None
            execute = False
            if hasattr(locator, '_mshptrail'):
                mashuptrail = locator._mshptrail
            if hasattr(locator, '_mshpversion'):
                mashupversion = locator._mshpversion
                if mashupversion:
                    execute = True
            self.open_vistrail_without_prompt(locator, version,
                                              mashuptrail=mashuptrail,
                                              mashupVersion=mashupversion,
                                              execute_workflow=execute)
            self.set_current_locator(locator)

    def executeParameterExploration(self, pe_id):
        vistrail = self.current_view.controller.vistrail
        try:
            pe_id = int(pe_id)
            pe = vistrail.get_paramexp(pe_id)
        except ValueError:
            pe= vistrail.get_named_paramexp(pe_id)
        except Exception, e:
            debug.unexpected_exception(e)
            return
        self.current_view.open_parameter_exploration(pe.id)
        self.qactions['execute'].trigger()

    def open_vistrail_without_prompt(self, locator, version=None,
                                     execute_workflow=False, 
                                     is_abstraction=False, workflow_exec=None,
                                     mashuptrail=None, mashupVersion=None,
                                     parameterExploration=None):
        """open_vistrail_without_prompt(locator_class, version: int or str,
                                        execute_workflow: bool,
                                        is_abstraction: bool) -> None
        Open vistrail depending on the locator class given.
        If a version is given, the workflow is shown on the Pipeline View.
        If execute_workflow is True the workflow will be executed.
        If is_abstraction is True, the vistrail is flagged as abstraction
        If mashuptrail is not None and mashupVersion is not None, the mashup 
        will be executed.
        If parameterExploration is not None, it will be opened.
        
        """
        
        # move additional information from locator to variables
        if 'version_node' in locator.kwargs:
            if locator.kwargs['version_node']:
                version = locator.kwargs['version_node']
            del locator.kwargs['version_node']
        if 'version_tag' in locator.kwargs:
            if locator.kwargs['version_tag']:
                version = locator.kwargs['version_tag']
            del locator.kwargs['version_tag']
        if not parameterExploration:
            if 'parameterExploration' in locator.kwargs:
                parameterExploration = locator.kwargs['parameterExploration']
                del locator.kwargs['parameterExploration']
        if not mashuptrail:
            if 'mashuptrail' in locator.kwargs:
                mashuptrail = locator.kwargs['mashuptrail']
                del locator.kwargs['mashuptrail']
        if not mashupVersion:
            if 'mashupVersion' in locator.kwargs:
                mashupVersion = locator.kwargs['mashupVersion']
                del locator.kwargs['mashupVersion']
            if 'mashup' in locator.kwargs:
                if not mashupVersion:
                    mashupVersion = locator.kwargs['mashup']
                del locator.kwargs['mashup']
            
        if not locator.is_valid():
            ok = locator.update_from_gui(self)
        else:
            ok = True
        if ok:
            if locator and not self.getViewFromLocator(locator):
                if locator.has_temporaries():
                    if not locator.prompt_autosave(self):
                        locator.clean_temporaries()
            view = self.open_vistrail(locator, version, is_abstraction)
            if view is None:
                return
            view.version_view.select_current_version()
            conf = get_vistrails_configuration()
            if version:
                self.qactions['pipeline'].trigger()
            elif conf.check('viewOnLoad') and conf.viewOnLoad == 'history':
                self.qactions['history'].trigger()
            elif conf.check('viewOnLoad') and conf.viewOnLoad == 'pipeline':
                self.qactions['pipeline'].trigger()
            else:
                # appropriate
                has_tag = len(view.controller.vistrail.get_tagMap()) > 0
                if has_tag:
                    self.qactions['history'].trigger()
                else:
                    self.qactions['pipeline'].trigger()
                            
            if mashuptrail is not None and mashupVersion is not None:
                mashup = view.get_mashup_from_mashuptrail_id(mashuptrail,
                                                             mashupVersion)
                if mashup is None:
                    debug.critical("Mashup not found. If workflow has been "
                                   "upgraded, try executing it first.")
                    return
                if execute_workflow:
                    view.open_mashup(mashup)
                else:
                    view.edit_mashup(mashup)
            elif parameterExploration is not None:
                view.open_parameter_exploration(parameterExploration)
            elif execute_workflow:
                self.qactions['execute'].trigger()
            
            # self.closeVistrailAction.setEnabled(True)
            # self.saveFileAsAction.setEnabled(True)
            # self.exportFileAction.setEnabled(True)
            # self.vistrailMenu.menuAction().setEnabled(True)
            # self.mergeMenu.menuAction().setEnabled(True)
            # self.viewManager.changeCursor(self.interactionToolBar.cursorMode)
            # if version:
            #     self.viewModeChanged(0)
            # else:
            #     self.viewModeChanged(1)
            if workflow_exec:
                self.qactions['provenance'].trigger()
                self.current_view.log_view.set_exec_by_id(workflow_exec) or \
                 self.current_view.log_view.set_exec_by_date(workflow_exec)

    def open_vistrail_default(self):
        """ open_vistrail_default() -> None
        Opens a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail_from_locator(DBLocator)
        else:
            self.open_vistrail_from_locator(FileLocator())

    def import_vistrail_default(self):
        """ import_vistrail_default() -> None
        Imports a vistrail from the file/db

        """
        if self.dbDefault:
            self.open_vistrail_from_locator(FileLocator())
        else:
            self.open_vistrail_from_locator(DBLocator)

    def import_workflow(self, locator_class):
        locator = locator_class.load_from_gui(self, Pipeline.vtType)
        if locator:
            if not locator.is_valid():
                ok = locator.update_from_gui(self, Pipeline.vtType)
            else:
                ok = True
            if ok:
                self.open_workflow(locator)

    def import_workflow_default(self):
        self.import_workflow(XMLFileLocator)

    def import_workflow_from_db(self):
        """ import_workflow_from_db() -> None
        Imports a workflow from the db

        """
        self.import_workflow(DBLocator)

    def open_workflow(self, locator):
        self.close_first_vistrail_if_necessary()
        get_vistrails_application().open_workflow(locator)
        view = self.get_current_view()
        view.controller.recompute_terse_graph()
        view.controller.invalidate_version_tree()
        from vistrails.gui.collection.workspace import QWorkspaceWindow
        QWorkspaceWindow.instance().add_vt_window(view)
        self.qactions['pipeline'].trigger()
    
    def close_vistrail(self, current_view=None, quiet=False):
        locator = None
        if not current_view:
            current_view = self.get_current_view()
        if current_view:
            locator = current_view.controller.locator

        SAVE_BUTTON, DISCARD_BUTTON, CANCEL_BUTTON = 0, 1, 2

        if not quiet and current_view and current_view.has_changes():
            window = current_view.window()
            name = current_view.controller.name
            if name=='':
                name = 'Untitled%s'%vistrails.core.system.vistrails_default_file_type()
            text = ('Vistrail ' +
                    QtCore.Qt.escape(name) +
                    ' contains unsaved changes.\n Do you want to '
                    'save changes before closing it?')
            res = QtGui.QMessageBox.information(window,
                                                'Vistrails',
                                                text, 
                                                '&Save', 
                                                '&Discard',
                                                'Cancel',
                                                0,
                                                2)
        else:
            res = DISCARD_BUTTON
        
        if res == SAVE_BUTTON:
            if locator is None or locator.is_untitled():
                class_ = FileLocator()
            else:
                class_ = type(locator)
            locator = current_view.save_vistrail(class_)
            if not locator:
                return False
        elif res == CANCEL_BUTTON:
            return False
        
        if locator is not None:
            get_vistrails_application().close_vistrail(locator, current_view.controller)
        record_vistrail('close', current_view.controller)
        return True

    def close_all_vistrails(self, quiet=False):
        self.current_view = None
        for view in [self.stack.widget(i) for i in xrange(self.stack.count())]:
            if not self.close_vistrail(view, quiet=quiet):
                return False
        while len(self.windows) > 0:
            window = self.windows.values()[0]
            window.activateWindow()
            window.raise_()
            if not window.close():
                return False
        return True

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None
        Close the whole application when the builder is closed

        """
        if not self.quit():
            e.ignore()

    def quit(self):
        self._is_quitting = True
        if self.close_all_vistrails():
            QtCore.QCoreApplication.quit()
            # In case the quit() failed (when Qt doesn't have the main
            # event loop), we have to return True still
            return True
        self._is_quitting = False
        return False

    def link_registry(self):
        from vistrails.gui.module_palette import QModulePalette
        QModulePalette.instance().link_registry()
       
    def get_current_view(self):
        # return the current global view
        return self.current_view

    def get_next_view(self):
        # return an available view if one exist
        # this can be used after closing a vistrail to get a new current one
        if self.stack.count() > 0:
            return self.stack.currentWidget()
        else:
            if len(self.windows) > 0:
                return next(self.windows.iterkeys())
        return None
        
    def get_current_controller(self):
        if self.get_current_view() is None:
            return None
        return self.get_current_view().get_controller()

    def get_current_tab(self):
        view = self.get_current_view()
        if not view:
            return None
        return view.get_current_tab()

    def get_current_scene(self):
        return self.get_current_tab().scene()

    def pass_through(self, accessor, method_name):
        def method():
            obj = accessor()
            if obj is not None:
                if hasattr(obj, method_name):
                    getattr(obj, method_name)()
        return method

    def pass_through_bool(self, accessor, method_name):
        def method(checked):
            obj = accessor()
            if obj is not None:
                getattr(obj, method_name)(checked)
        return method

    def pass_through_locator(self, accessor, method_name, locator_klass=None,
                             reverse=False):
        def method():
            obj = accessor()
            obj_method = getattr(obj, method_name)
            if locator_klass is not None:
                obj_method(locator_klass)
            elif self.dbDefault ^ reverse:
                obj_method(DBLocator)
            else:
                obj_method(FileLocator())
        return method

    def create_menus(self):
        self.create_actions()
        # self.fileMenu = _menu_bar.addMenu('&File')
        # self.newVistrailAction = QtGui.QAction('&New', self)
        # self.newVistrailAction.setShortcut('Ctrl+N')
        # self.newVistrailAction.setStatusTip('Create a new vistrail')
        # self.openFileAction = QtGui.QAction('&Open', self)
        # self.openFileAction.setShortcut('Ctrl+O')
        # self.openFileAction.setStatusTip('Open an existing vistrail from '
        #                                  'a file')
        
        # self.fileMenu.addAction(self.newVistrailAction)
        # self.fileMenu.addAction(self.openFileAction)

        # trigger_actions = [(self.newVistrailAction, self.new_vistrail),
        #                    (self.openFileAction, self.open_vistrail_default)]
        # for (emitter, receiver) in trigger_actions:
        #     self.connect(emitter, QtCore.SIGNAL('triggered()'), receiver)


    def create_palette_actions(self):
        palette_actions = []
        for palette in self.palettes:
            # palette_actions.append((palette.get_title(), palette.get_action()))
            palette_actions.append((palette.get_action_tuple(), palette))
        palette_actions.sort()
        return palette_actions

    def connect_package_manager_signals(self):
        """ connect_package_manager_signals()->None
        Connect specific signals related to the package manager """
        self.register_notification("pm_add_package_menu", 
                                   self.add_package_menu_items)
        self.register_notification("pm_remove_package_menu",
                                   self.remove_package_menu_items)
        self.register_notification("pm_package_error_message",
                                   self.show_package_error_message)
        # pm = get_package_manager()
        # self.connect(pm,
        #              pm.add_package_menu_signal,
        #              self.add_package_menu_items)
        # self.connect(pm,
        #              pm.remove_package_menu_signal,
        #              self.remove_package_menu_items)
        # self.connect(pm,
        #              pm.package_error_message_signal,
        #              self.show_package_error_message)

    def add_package_menu_items(self, pkg_id, pkg_name, items):
        """add_package_menu_items(pkg_id: str,pkg_name: str,items: list)->None
        Add a pacckage menu entry with submenus defined by 'items' to
        Packages menu.

        """
        if len(self._package_menu_items) == 0:
            self.qmenus['packages'].menuAction().setEnabled(True)

        # we don't support a menu hierarchy yet, only a flat list
        # this can be added later
        def update_menu(d, packagesMenu):
            if pkg_id not in d:
                pkg_menu = packagesMenu.addMenu(str(pkg_name))
                d[pkg_id] = {}
                d[pkg_id]['menu'] = pkg_menu
                d[pkg_id]['items'] = []
            else:
                pkg_menu = d[pkg_id]['menu']
                pkg_menu.clear()
            d[pkg_id]['items'] = [(pkg_name,items)]
            
            for item in items:
                (name, callback) = item
                action = QtGui.QAction(name,self,
                                       triggered=callback)
                pkg_menu.addAction(action)
                
        update_menu(self._package_menu_items,self.qmenus['packages'])    
        
        for w in self.windows.values():
            update_menu(w._package_menu_items, w.qmenus['packages'])

    def remove_package_menu_items(self, pkg_id):
        """remove_package_menu_items(pkg_id: str)-> None
        removes all menu entries from the Packages Menu created by pkg_id """
        def update_menu(items, menu):
            if pkg_id in items:
                pkg_menu = items[pkg_id]['menu']
                del items[pkg_id]
                pkg_menu.clear()
                pkg_menu.deleteLater()
            if len(items) == 0:
                menu.menuAction().setEnabled(False)
            
        update_menu(self._package_menu_items, self.qmenus['packages'])
        for w in self.windows.values():
            update_menu(w._package_menu_items, w.qmenus['packages'])
            
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
            vistrails.core.system.short_about_string()
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

    def showUpdatesMessage(self):
        """ showUpdatesMessage() -> None
        Displays Check for Updates message.
        This queries vistrails.org for new VisTrails Versions

        """

        new_version_exists, version = vistrails.core.system.new_vistrails_release_exists()
        if new_version_exists:
            msg = 'Version %s of VisTrails is available at ' \
                '<a href="%s">%s</a>' % \
                (version, "http://www.vistrails.org/index.php/Downloads", \
                     "http://www.vistrails.org/index.php/Downloads")
        else:
            msg = "Your VisTrails installation is up-to-date."
        QtGui.QMessageBox.information(self, "Check for VisTrails Updates",
                                      msg)
                                      
    def showRepositoryOptions(self):
        """ Displays Repository Options for authentication and pushing VisTrail to Repository """
        self.publish_to_crowdlabs()

    def setDBDefault(self, dbState):
        """ setDBDefault(on: bool) -> None
        The preferences are set to turn on/off read/write from db instead of
        file. Update the state accordingly.

        """
        self.dbDefault = dbState
        if self.dbDefault:
            openFileAction = self.qactions['openFile']
            openFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_DB_ICON)
            openFileAction.setStatusTip('Open an existing vistrail from '
                                        'a database')
            importFileAction = self.qactions['importFile']
            importFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_ICON)
            importFileAction.setText('From XML File...')
            importFileAction.setStatusTip('Import an existing vistrail '
                                          'from a file')
            saveFileAction = self.qactions['saveFile']
            saveFileAction.setStatusTip('Save the current vistrail '
                                        'to a database')
            saveFileAsAction = self.qactions['saveFileAs']
            saveFileAsAction.setStatusTip('Save the current vistrail to a '
                                          'different database location')
            saveToOtherAction = self.qactions['saveToOther']
            saveToOtherAction.setText('Save To File...')
            saveToOtherAction.setStatusTip('Save the current vistrail to '
                                          'a file')
            exportFileAction = self.qactions['exportFile']
            exportFileAction.setText('To File...')
            exportFileAction.setStatusTip('Export the current vistrail to '
                                          'a file')
        else:
            openFileAction = self.qactions['openFile']
            openFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_ICON)
            openFileAction.setStatusTip('Open an existing vistrail from '
                                             'a file')
            importFileAction = self.qactions['importFile']
            importFileAction.setIcon(CurrentTheme.OPEN_VISTRAIL_DB_ICON)
            importFileAction.setText('From DB...')
            importFileAction.setStatusTip('Import an existing vistrail '
                                          'from a database')
            saveFileAction = self.qactions['saveFile']
            saveFileAction.setStatusTip('Save the current vistrail '
                                             'to a file')
            saveFileAsAction = self.qactions['saveFileAs']
            saveFileAsAction.setStatusTip('Save the current vistrail to a '
                                          'different file location')
            saveToOtherAction = self.qactions['saveToOther']
            saveToOtherAction.setText('Save To DB...')
            saveToOtherAction.setStatusTip('Save the current vistrail to '
                                          'a database')
            exportFileAction = self.qactions['exportFile']
            exportFileAction.setText('Export To DB...')
            exportFileAction.setStatusTip('Export the current vistrail to '
                                          'a database')

    def flush_cache(self):
        CachedInterpreter.flush()

    def set_stop_on_error(self, stop):
        setattr(get_vistrails_persistent_configuration(), 'stopOnError', stop)
        setattr(get_vistrails_configuration(), 'stopOnError', stop)

    def showPreferences(self):
        """showPreferences() -> None
        Display Preferences dialog

        """
        self.preferencesDialog.show()

    def new_diff(self):
        selected_items = \
            self.get_current_view().version_view.scene().selectedItems()
        if len(selected_items) == 2:
            selected_ids = [item.id for item in selected_items]
            self.get_current_view().diff_requested(*selected_ids)

    def setup_recent_vistrails(self):
        conf = get_vistrails_configuration()
        if conf.check('recentVistrailList'):
            self.recentVistrailLocators = \
                RecentVistrailList.unserialize(conf.recentVistrailList)
        else:
            self.recentVistrailLocators = RecentVistrailList()
        conf.subscribe('maxRecentVistrails', self.max_recent_vistrails_changed)
        self.update_recent_vistrail_actions()

    def open_recent_vistrail(self):
        """ open_recent_vistrail() -> None
        Opens a vistrail from Open Recent menu list
        
        """
        action = self.sender()
        if action:
            self.open_vistrail_without_prompt(action.locator)
            self.set_current_locator(action.locator)
            
    def update_recent_vistrail_menu(self):
        #check if we have enough actions
        def update_menu(openRecentMenu):
            openRecentMenu.clear()
            for i, locator in enumerate(self.recentVistrailLocators.locators):
                action = QtGui.QAction(self)
                self.connect(action, QtCore.SIGNAL("triggered()"),
                             self.open_recent_vistrail)
                action.locator = locator
                action.setText("&%d %s" % (i+1, locator.name))
                openRecentMenu.addAction(action)
        update_menu(self.qmenus['openRecent'])
        for w in self.windows.values():
            update_menu(w.qmenus['openRecent'])

    def update_window_menu(self):
        def compute_action_items():
            actions = []
            action = QtGui.QAction(
                    "Main Window", self,
                    triggered=lambda checked=False: self.activateWindow())
            action.setCheckable(True)
            
            base_view_windows = {}
            if current_view is None or \
               QtGui.QApplication.activeWindow() == self:
                action.setChecked(True)
            actions.append(action)
            if current_view and current_view.window() == self:
                for i in range(self.stack.count()):
                    view = self.stack.widget(i)
                    for dview, dw in current_view.detached_views.iteritems():
                        base_view_windows[dview] = dw
            if len(self.windows) > 0:
                windowactions = []
                for view, w in self.windows.iteritems():
                    action = QtGui.QAction(view.get_name(), self,
                           triggered=lambda checked=False: w.activateWindow())
                    action.setCheckable(True)
                    if w == QtGui.QApplication.activeWindow():
                        action.setChecked(True)
                    windowactions.append(action)
                    for dview, dw in view.detached_views.iteritems():
                        base_view_windows[dview] = dw
                actions.append(windowactions)
            if len(base_view_windows) > 0:
                base_view_actions = []
                for view, w in base_view_windows.iteritems():
                    action = QtGui.QAction(w.windowTitle(), self,
                           triggered=lambda checked=False: w.activateWindow())
                    action.setCheckable(True)
                    if w == QtGui.QApplication.activeWindow():
                        action.setChecked(True)
                    base_view_actions.append(action)
                actions.append(base_view_actions)
            return actions
        
        def update_menu(windowMenu):
            actions = compute_action_items()
            windowMenu.clear()
            if len(actions) > 0:
                windowMenu.addAction(actions[0])
                if len(actions) > 1:
                    windowMenu.addSeparator()
                    for action in actions[1]:
                        windowMenu.addAction(action)
                if len(actions) > 2:
                    windowMenu.addSeparator()
                    for action in actions[2]:
                        windowMenu.addAction(action)

        current_view = self.get_current_view()
        update_menu(self.qmenus['window'])
        if current_view and current_view.window() == self:
            for i in range(self.stack.count()):
                view = self.stack.widget(i)
                for dw in view.detached_views.values():
                    update_menu(dw.qmenus['window'])
        for v, w in self.windows.iteritems():
            update_menu(w.qmenus['window'])
            for dw in v.detached_views.values():
                update_menu(dw.qmenus['window'])
                
        if current_view and current_view.window() in self.windows.values():
            # add detach action
            current_view.window().qmenus['window'].addSeparator()
            action = QtGui.QAction(
                    "Re-attach Vistrail View", self,
                    triggered=lambda b=None: self.attach_view())
            current_view.window().qmenus['window'].addAction(action)
            
            
    def update_merge_menu(self):
        #check if we have enough actions
        def update_menu(mergeMenu):
            mergeMenu.clear()
            for i in xrange(self.stack.count()):
                view = self.stack.widget(i)
                # skip merge with self and not saved views
                if view == self.current_view or not view.controller.vistrail.locator:
                    continue
                action = QtGui.QAction(self)
                self.connect(action, QtCore.SIGNAL("triggered()"),
                             self.merge_vistrail)
                action.controller = view.controller
                action.setText("%s" % view.controller.vistrail.locator.name)
                mergeMenu.addAction(action)
            for view, w in self.windows.iteritems():
                # skip merge with self and not saved views
                if view == self.current_view or not view.controller.vistrail.locator:
                    continue
                action = QtGui.QAction(self)
                self.connect(action, QtCore.SIGNAL("triggered()"),
                             self.merge_vistrail)
                action.controller = view.controller
                action.setText("%s" % view.controller.vistrail.locator.name)
                mergeMenu.addAction(action)
                
        update_menu(self.qmenus['merge'])
        for w in self.windows.values():
            update_menu(w.qmenus['merge'])

    def update_recent_vistrail_actions(self):
        maxRecentVistrails = \
            int(get_vistrails_configuration().maxRecentVistrails)
        self.recentVistrailLocators.ensure_no_more_than_max(maxRecentVistrails)
        self.update_recent_vistrail_menu()
        
        conf = get_vistrails_persistent_configuration()
        tconf = get_vistrails_configuration()
        conf.recentVistrailList = self.recentVistrailLocators.serialize()
        tconf.recentVistrailList = conf.recentVistrailList
        get_vistrails_application().save_configuration()
        
    def set_current_locator(self, locator):
        """ set_current_locator(locator: CoreLocator)
        Updates the list of recent files in the gui and in the configuration
        
        """
        if locator:
            self.recentVistrailLocators.add_locator(locator)
            self.update_recent_vistrail_actions()
    
    def max_recent_vistrails_changed(self, field, value):
        """max_recent_vistrails_changed()-> obj
        callback to create an object to be used as a subscriber when the 
        configuration changed.
        
        """
        self.update_recent_vistrail_actions()
                
    def configure_module(self):
        from vistrails.gui.module_configuration import QModuleConfiguration
        action_name = QModuleConfiguration.instance().get_title()
        if action_name[-1] == '*':
            action_name = action_name[:-1]
        # easy way to make sure that configuration window is raised
        self.qactions[action_name].setChecked(False)
        self.qactions[action_name].setChecked(True)

    def show_documentation(self):
        from vistrails.gui.module_documentation import QModuleDocumentation
        action_name = QModuleDocumentation.instance().get_title()
        # easy way to make sure that documentation window is raised
        self.qactions[action_name].setChecked(False)
        self.qactions[action_name].setChecked(True)

    def show_looping_options(self):
        from vistrails.gui.module_options import QModuleOptions
        action_name = QModuleOptions.instance().get_title()
        # easy way to make sure that looping options window is raised
        self.qactions[action_name].setChecked(False)
        self.qactions[action_name].setChecked(True)

#    def show_group(self):
#        class DummyController(object):
#            def __init__(self, pip):
#                self.current_pipeline = pip
#                self.search = None
#        #FIXME: this should be delegated to QVistrailView
#        current_scene = self.get_current_scene()
#        selected_module_ids = current_scene.get_selected_module_ids()
#        if len(selected_module_ids) > 0:
#            for m_id in selected_module_ids:
#                module = current_scene.current_pipeline.modules[m_id]
#                if module.is_group() or module.is_abstraction():
#                    pipelineView = QPipelineView()
#                    controller = DummyController(module.pipeline)
#                    pipelineView.controller = controller
#                   pipelineMainWindow = QBaseViewWindow(pipelineView)
#                    #pipelineMainWindow.setCentralWidget(pipelineView)
#                    pipelineView.scene().controller = \
#                        controller
#                    controller.current_pipeline_view = \
#                        pipelineView.scene()
#                    module.pipeline.ensure_connection_specs()
#                    pipelineView.scene().setupScene(module.pipeline)
#                    pipelineView.scene().current_pipeline = module.pipeline
#                    pipelineView.scene().fitToView(pipelineView, True)
#                    pipelineView.show()
#                    pipelineMainWindow.show()

    def openAbstraction(self, filename):
        locator = XMLFileLocator(filename)
        self.open_vistrail_without_prompt(locator, None, False, True)

    def edit_abstraction(self):
        current_scene = self.get_current_tab().scene()
        selected_module_ids = current_scene.get_selected_module_ids()
        if len(selected_module_ids) > 0:
            for m_id in selected_module_ids:
                module = current_scene.current_pipeline.modules[m_id]
                if module.is_abstraction():
                    from vistrails.core.modules.abstraction import identifier as \
                        abstraction_pkg                    
                    ann_get = module.vistrail.get_annotation
                    if module.package == abstraction_pkg and \
                            ann_get('__abstraction_descriptor_info__') is None:
                        desc = module.module_descriptor
                        filename = desc.module.vt_fname
                        self.openAbstraction(filename)
                    else:
                        debug.critical('Subworkflow is from a package and is '
                                       'read-only',
                                       "This subworkflow is from a package and "
                                       "cannot be modified.  You can create an "
                                       "editable copy in 'My Subworkflows' "
                                       "using 'Workflow->Import Subworkflow'")
    def merge_vistrail(self):
        action = self.sender()
        if action:
            self.merge_vistrails(self.current_view.controller, action.controller)

    def merge_vistrails(self, c1, c2):
        """ merge_vistrails(c1: VistrailController, c2: VistrailController) -> None
            hamdle merge vistrail from 2 controller into new vistrail

        """
        thumb_cache = ThumbnailCache.getInstance()
        
        l1 = c1.locator._name if c1.locator is not None else ''
        t1 = c1.find_thumbnails(tags_only=thumb_cache.conf.tagsOnly) \
            if thumb_cache.conf.autoSave else []
        s1 = SaveBundle(c1.vistrail.vtType, c1.vistrail.do_copy(), c1.log, thumbnails=t1)

        l2 = c2.locator._name if c2.locator is not None else ''
        t2 = c2.find_thumbnails(tags_only=thumb_cache.conf.tagsOnly) \
            if thumb_cache.conf.autoSave else []
        s2 = SaveBundle(c2.vistrail.vtType, c2.vistrail, c2.log, thumbnails=t2)

        vistrails.db.services.vistrail.merge(s1, s2, "", merge_gui, l1, l2)
        vistrail = s1.vistrail
        vistrail.locator = UntitledLocator()
        vistrail.set_defaults()
        view = self.create_view(vistrail, None)
        # FIXME need to figure out what to do with this !!!
        view.controller.set_vistrail(vistrail, None, thumbnails=s1.thumbnails)
        view.controller.set_changed(True)
        self.view_changed(view)
        from vistrails.gui.collection.workspace import QWorkspaceWindow
        QWorkspaceWindow.instance().add_vt_window(view)
        self.reset_toolbar_for_view(view)
        self.qactions['history'].trigger()
        view.version_view.scene().fitToView(view.version_view, True)


        
    def do_tag_prompt(self, name="", exists=False):
        if exists:
            prompt = "'%s' already exists.  Enter a new tag" % name
        else:
            prompt = "Enter a tag"
            
        (text, ok) = QtGui.QInputDialog.getText(None, 
                                                'Tag Version',
                                                prompt,
                                                QtGui.QLineEdit.Normal,
                                                name)
        if ok and text:
            return str(text).strip().rstrip()
        if not ok:
            return None
        return ""

    def add_tag(self, check_exists=True):
        controller = self.get_current_controller()
        vistrail = controller.vistrail
        name = self.do_tag_prompt()
        if name is None:
            return None
        while name == "" or (check_exists and vistrail.has_tag_str(name)):
            name = self.do_tag_prompt(name, name != "")
            if name is None:
                return None
        controller.update_current_tag(name)
        
    def publish_to_crowdlabs(self):
        dialog = QRepositoryDialog(self)
        if QRepositoryDialog.cookiejar:
            dialog.exec_()

    def invalidate_pipelines(self):
        """ invalidate_pipelines() -> None
            Clears the cache and reloads the current pipelines in all views
            This should be called when a module in the module registry
            is changed/added/deleted
        """
        
        def reload_view(view):
            view.version_selected(view.controller.current_version,
                                  True, from_root=True)
        
        for i in xrange(self.stack.count()):
            view = self.stack.widget(i)
            reload_view(view)
        for view in self.windows:
            reload_view(view)
    
    def closeNotPinPalettes(self):
        if (QtGui.QApplication.activeWindow() == self or 
            QtGui.QApplication.activeWindow() in self.windows.values()):
            for p in self.palettes:
                if p.toolWindow().window() == QtGui.QApplication.activeWindow():
                    if (p.toolWindow().isVisible() and 
                        not p.toolWindow().isFloating() and not p.get_pin_status()):
                        p.toolWindow().close()
                 
    def applicationFocusChanged(self, old, current):
        """ This method updates the current vistrail view when needed
            Clicking a vistrail view selects it as the current unless clicking
            in a vistrail palette widget which are global
        """
        if self._is_quitting:
            return
        # focus owner is used to prevent view update when re-clicking a detached view
        focus_owner = self._focus_owner
        self._focus_owner = None

        vt_app = get_vistrails_application()
        # sometimes the correct widget is not selected
        current = vt_app.widgetAt(QtGui.QCursor.pos())
        
        if current is not None:
            owner = current.window()
            #print "\n\n\n >>>>>> applicationfocuschanged"
            #print "owner: ", owner, " current: ", current
            def is_or_has_parent_of_types(widget, types):
                while widget is not None:
                    for _type in types:
                        if isinstance(widget, _type):
                            return True
                    widget = widget.parent()
                return False
            allowed_widgets = [ConstantWidgetMixin,
                               QParamExploreView,
                               QAliasInspector,
                               QCellWidget,
                               QMashupViewTab,
                               QVistrailsPaletteInterface,
                               QToolWindow]
            old_view = self.get_current_view()
            view = None
            if self.isAncestorOf(current):
                view = self.stack.currentWidget()
            elif  owner in self.windows.values():
                view = owner.get_current_view()
            if view:
                # owner is a vistrail view
                if not is_or_has_parent_of_types(current, allowed_widgets):
                    # clicked in a valid view, so update it
                    #print "generating view_changed", view
                    self.change_view(view)
                    if view != old_view:
                        self.update_window_menu()
                    self._previous_view = self.current_view.current_tab
                    view.reset_tab_view_to_current()
                    view.view_changed()    
                return
            if isinstance(owner, QBaseViewWindow):
                # this is a pipeline view
                self._focus_owner = owner
                view = owner.get_current_view()
                if (view and owner != focus_owner and 
                    not is_or_has_parent_of_types(current, allowed_widgets)):
                    #print "generating view changed2", view
                    self.change_view(view)
                    if view != old_view:
                        self.update_window_menu()
                    self._previous_view = self.current_view.current_tab
                    view.set_to_current(owner.get_current_tab())
                    view.view_changed()
_app = None
#_global_menubar = None
    
            
class QPaletteMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
        self.palettes = []
        self.windows = []
        
    def addPalette(self, palette):
        if palette not in self.palettes:
            self.palettes.append(palette)
        if len(self.palettes) == 1:
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, palette.toolWindow())
        else:
            self.tabifyDockWidget(self.palettes[0].toolWindow(),
                                  palette.toolWindow())
        palette.toolWindow().close()
        
    def closeDockedPalettes(self):
        for p in self.palettes:
            if (p.toolWindow().isVisible() and 
                    not p.toolWindow().isFloating()):
                p.toolWindow().close()
            
    def closeEvent(self, event):
        if not QtCore.QCoreApplication.closingDown():
            self.closeDockedPalettes()
            self.hide()
            event.ignore()

    def showEvent(self, event):
        for p in self.palettes:
            if (not p.toolWindow().isVisible() and 
                not p.toolWindow().isFloating() and p.get_pin_status()):
                p.set_visible(True)
    
