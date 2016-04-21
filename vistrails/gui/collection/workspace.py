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
from __future__ import division

from PyQt4 import QtCore, QtGui

import glob
from itertools import chain
import os
from datetime import datetime
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core import debug
from vistrails.core.collection import Collection, MashupEntity, ThumbnailEntity, \
    VistrailEntity, WorkflowEntity, WorkflowExecEntity, ParameterExplorationEntity
from vistrails.core.db.locator import FileLocator
from vistrails.core.system import time_strptime
from vistrails.db.services.locator import UntitledLocator
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.module_palette import QModuleTreeWidgetItemDelegate
from vistrails.gui.vis_diff import QDiffView

class QCollectionWidget(QtGui.QTreeWidget):
    """ This is an abstract class that contains functions for handling
    a core.collection.Collection object
    a subclass should provide a view of the collection
    """
    def __init__(self, collection, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.collection = collection
        self.collection.add_listener(self)
        self.setExpandsOnDoubleClick(False)
        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_selected)
        self.setIconSize(QtCore.QSize(16,16))

    def setup_widget(self, workspace=None):
        """ Adds the items from the current workspace """
        pass

    def updated(self):
        """ Called from the collection when committed """
        self.setup_widget()
            
    def run_search(self, search, items=None):
        top_level = items is None
        if top_level:
            items = [self.topLevelItem(i)
                     for i in xrange(self.topLevelItemCount())]
        for item in items:
            if search.match(item.entity):
                item.setHidden(False)
                parent = item.parent()
                while parent is not None:
                    if parent.isHidden():
                        parent.setHidden(False)
                    if not parent.isExpanded():
                        parent.setExpanded(True)
                    parent = parent.parent()
            else:
                item.setHidden(True)
            self.run_search(search, [item.child(i) 
                                     for i in xrange(item.childCount())])

    def reset_search(self, items=None):
        if items is None:
            items = [self.topLevelItem(i)
                     for i in xrange(self.topLevelItemCount())]
        for item in items:
            item.setHidden(False)
            self.reset_search([item.child(i) 
                               for i in xrange(item.childCount())])

    def item_selected(self, widget_item, column):
        locator = widget_item.entity.locator()
        import vistrails.gui.application
        app = vistrails.gui.application.get_vistrails_application()
        open_vistrail = app.builderWindow.open_vistrail_without_prompt
        args = {}
        args['version'] = locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None)
        if args['version']:
            # set vistrail name
            locator = widget_item.entity.parent.locator()

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
            locator = widget_item.entity.parent.parent.locator()
            locator.update_from_gui(self)

        locator.update_from_gui(self)
        open_vistrail(locator, **args)
        self.setItemSelected(widget_item, True)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        menu = QtGui.QMenu(self)
        if item:
            # find top level
            p = item
            while p.parent():
                p = p.parent()
            act = QtGui.QAction("&Update", self)
            act.setStatusTip("Update this object")
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   p.refresh_object)
            menu.addAction(act)
            act = QtGui.QAction("&Remove", self)
            act.setStatusTip("Remove from this list")
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   p.remove_object)
            menu.addAction(act)
            act = QtGui.QAction("", self)
            act.setSeparator(True)
            menu.addAction(act)
        act = QtGui.QAction("Check &All", self)
        act.setStatusTip("Removes deleted files")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.check_objects)
        menu.addAction(act)
        act = QtGui.QAction("Remove All", self)
        act.setStatusTip("Removes all files")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.remove_all)
        menu.addAction(act)
        act = QtGui.QAction("Add &File", self)
        act.setStatusTip("Add specified vistrail file")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.add_file)
        menu.addAction(act)
        act = QtGui.QAction("Add from &Directory", self)
        act.setStatusTip("Add all vistrail files in a directory")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.add_dir)
        menu.addAction(act)
        act = QtGui.QAction("", self)
        act.setSeparator(True)
        menu.addAction(act)
        act = QtGui.QAction("Add a new Workspace", self)
        act.setStatusTip("Create a new workspace")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.add_workspace)
        menu.addAction(act)
        if self.collection.currentWorkspace != 'Default':
            act = QtGui.QAction("Delete Workspace", self)
            act.setStatusTip("Remove current workspace")
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   self.delete_workspace)
            menu.addAction(act)
        menu.exec_(event.globalPos())

    def check_objects(self):
        items = [self.topLevelItem(i) 
                 for i in xrange(self.topLevelItemCount())]
        for item in items:
            item.entity.locator().update_from_gui(self)
            if not self.collection.urlExists(item.entity.url):
                self.collection.delete_entity(item.entity) 
        self.collection.commit()

    def remove_all(self):
        items = [self.topLevelItem(i) 
                 for i in xrange(self.topLevelItemCount())]
        for item in items:
            self.collection.del_from_workspace(item.entity) 
        self.collection.commit()

    def add_file(self):
        s = QtGui.QFileDialog.getOpenFileName(
                    self, "Choose a file",
                    "", "Vistrail files (*.vt *.xml)")
        if str(s):
            locator = FileLocator(str(s))
            url = locator.to_url()
            entity = self.collection.updateVistrail(url)
            # add to relevant workspace categories
            self.collection.add_to_workspace(entity)
            self.collection.commit()
        
    def add_dir(self):
        s = QtGui.QFileDialog.getExistingDirectory(
                    self, "Choose a directory",
                    "", QtGui.QFileDialog.ShowDirsOnly)
        if str(s):
            self.update_from_directory(str(s))
        
    def update_from_directory(self, s):
        filenames = glob.glob(os.path.join(s, '*.vt,*.xml'))
        
        progress = QtGui.QProgressDialog('', '', 0, len(filenames))
        progress.setWindowTitle('Adding files')
        progress.setMinimumDuration(500)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        i = 0
        for filename in filenames:
            progress.setValue(i)
            progress.setLabelText(filename)
            i += 1
            try:
                locator = FileLocator(filename)
                url = locator.to_url()
                entity = self.collection.updateVistrail(url)
                self.collection.add_to_workspace(entity)
            except Exception:
                debug.critical("Failed to add file '%s'" % filename)
        progress.setValue(len(filenames))
        self.collection.commit()

    def add_workspace(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Create workspace',
                      'Enter new workspace name:')
        workspace = str(text).strip()
        if ok and workspace != '':
            self.collection.currentWorkspace = workspace
            if workspace not in self.collection.workspaces:
                self.collection.add_workspace(workspace)
                self.collection.commit()
            self.emit(QtCore.SIGNAL("workspaceListUpdated()"))
                
    def delete_workspace(self):
        if self.collection.currentWorkspace != 'Default':
            self.collection.delete_workspace(self.collection.currentWorkspace)
            self.collection.currentWorkspace = 'Default'
            self.collection.commit()
            self.emit(QtCore.SIGNAL("workspaceListUpdated()"))

class QWorkspaceWidget(QCollectionWidget):
    """ This class implements QCollectionWidget as a side bar browser widget
    """
    def __init__(self, collection, parent=None):
        QCollectionWidget.__init__(self, collection, parent)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

    def setup_widget(self, workspace=None):
        """ Adds the items from the current workspace """
        while self.topLevelItemCount():
            self.takeTopLevelItem(0)
        if workspace:
            self.collection.currentWorkspace = workspace
        for entity in self.collection.workspaces[self.collection.currentWorkspace]:
            item = QBrowserWidgetItem(entity, self)
            self.addTopLevelItem(item)
        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

class QWorkflowsItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['Workflows'])

class QMashupsItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['Mashups'])

class QParamExplorationsItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['Parameter Explorations'])

class QBrowserWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, entity, parent=None):
        if not entity:
            # assuming an unsaved item
            QtGui.QTreeWidgetItem.__init__(self, parent)
            self.tag_to_item = {}
            self.workflowsItem = QWorkflowsItem()
            self.addChild(self.workflowsItem)
            self.mshp_to_item = {}
            self.mashupsItem = QMashupsItem()
            self.addChild(self.mashupsItem)
            self.pe_to_item = {}
            self.paramExplorationsItem = QParamExplorationsItem()
            self.addChild(self.paramExplorationsItem)
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
            return

        self.entity = entity
        QtGui.QTreeWidgetItem.__init__(self, parent, [entity.name])
        if entity.type_id == VistrailEntity.type_id:
            # vistrail - create Workflows and Mashups item
            self.workflowsItem = QWorkflowsItem()
            self.addChild(self.workflowsItem)
            self.mashupsItem = QMashupsItem()
            self.addChild(self.mashupsItem)
            self.mashupsItem.setHidden(True)
            self.paramExplorationsItem = QParamExplorationsItem()
            self.addChild(self.paramExplorationsItem)
            self.paramExplorationsItem.setHidden(True)
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
            self.tag_to_item = {}
            self.mshp_to_item = {}
            self.pe_to_item = {}
        elif entity.type_id == WorkflowEntity.type_id:
            self.setIcon(0, CurrentTheme.PIPELINE_ICON)
            self.executionList = []
        elif entity.type_id == WorkflowExecEntity.type_id:
            self.setIcon(0, CurrentTheme.EXECUTE_PIPELINE_ICON)

        tooltip = '<html>%s' % entity.url
            
        for child in entity.children:
            if child.type_id == ThumbnailEntity.type_id:
                # is a thumbnail
                # add to parent workflow item
                cache = ThumbnailCache.getInstance()
                path = cache.get_abs_name_entry(child.name)
                if path:
                    pixmap = QtGui.QPixmap(path)
                    if pixmap and not pixmap.isNull():
                        self.setIcon(0, QtGui.QIcon(pixmap.scaled(16, 16)))
                    tooltip += "<br/><img border=0 src='%(path)s'/>" % \
                               {'path': path}
            elif child.type_id == WorkflowEntity.type_id:
                # is a pipeline
                # only show tagged items
                # Add to 'Workflows' item

                if not child.name.startswith('Version #'):
                    childItem = QWorkflowEntityItem(child)
                    self.workflowsItem.addChild(childItem)
                    # keep list of tagged workflows
                    self.tag_to_item[child.name] = childItem
            elif child.type_id == WorkflowExecEntity.type_id:
                # is an execution
                childItem = QWorkflowExecEntityItem(child)
                # hidden by default
                self.executionList.append(childItem)
                self.addChild(childItem)
                childItem.setHidden(True)
            elif child.type_id == MashupEntity.type_id:
                # is a mashup
                childItem = QMashupEntityItem(child)
                self.mashupsItem.addChild(childItem)
                # keep list of tagged mashups
                self.mshp_to_item[child.name] = childItem
            elif child.type_id == ParameterExplorationEntity.type_id:
                # is a parameter exploration
                childItem = QParamExplorationEntityItem(child)
                self.paramExplorationsItem.addChild(childItem)
                # keep list of tagged pe:s
                self.pe_to_item[child.url] = childItem
            else:
                self.addChild(QBrowserWidgetItem(child))
        if entity.description:
            tooltip += '<br/>%s' % entity.description
        tooltip += '</html>'
        self.setToolTip(0, tooltip)

    def refresh_object(self):
        Collection.getInstance().updateVistrail(self.entity.url)
        Collection.getInstance().commit()

    def remove_object(self):
        Collection.getInstance().del_from_workspace(self.entity)
        Collection.getInstance().commit()
        
class QWorkflowEntityItem(QBrowserWidgetItem):
    def get_vistrail(self):
        parent = self.parent()
        while parent and type(parent) != QVistrailEntityItem:
            parent = parent.parent()
        return parent
    
    def open_workflow(self):
        self.treeWidget().item_selected(self, 0)

    def open_workflow_in_new_tab(self):
        self.get_vistrail().window.add_pipeline_view()
        self.open_workflow()

    def open_workflow_in_new_window(self):
        self.open_workflow_in_new_tab()
        self.get_vistrail().window.detach_view(
                                self.get_vistrail().window.tabs.currentIndex())

class QWorkflowExecEntityItem(QBrowserWidgetItem):
    pass

class QMashupEntityItem(QBrowserWidgetItem):
    def open_mashup(self):
        self.treeWidget().open_mashup(self.entity)
        
    def edit_mashup(self):
        self.treeWidget().edit_mashup(self.entity)

class QParamExplorationEntityItem(QBrowserWidgetItem):
    pass

class QExplorerWidget(QCollectionWidget):
    """ This class implements QCollectionWidget as a full-screen explorer widget
    """
    def __init__(self, collection, parent=None):
        QCollectionWidget.__init__(self, collection, parent)
        self.setColumnCount(6)
        self.setHeaderLabels(['name', 'user', 'mod_date', 'create_date', 'size', 'url'])

    def setup_widget(self, workspace=None):
        """ Adds the items from the current workspace """
        self.clear()
        if workspace:
            self.collection.currentWorkspace = workspace
        for entity in self.collection.workspaces[self.collection.currentWorkspace]:
            item = QExplorerWidgetItem(entity)
            self.addTopLevelItem(item)
        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

class QExplorerWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, entity, parent=None):
        l = list(str(x) for x in entity.save())
        l.pop(0) # remove identifier
        type = l.pop(0)
        desc = l.pop(5)
        QtGui.QTreeWidgetItem.__init__(self, parent, l)
        self.entity = entity
        if type == '1':
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
        elif type == '2':
            self.setIcon(0, CurrentTheme.PIPELINE_ICON)
        elif type == '3':
            self.setIcon(0, CurrentTheme.EXECUTE_PIPELINE_ICON)

        self.setToolTip(0, entity.url)
            
        for child in entity.children:
            l = child.save()
            if l[1] == 4:
                cache = ThumbnailCache.getInstance()
                path = cache.get_abs_name_entry(l[2])
                if path:
                    self.setIcon(0, QtGui.QIcon(path))
                continue
            else:
                self.addChild(QExplorerWidgetItem(child))

    def __lt__(self, other):
        sort_col = self.treeWidget().sortColumn()
        if sort_col in set([4]):
            return int(self.text(sort_col)) < int(other.text(sort_col))
        elif sort_col in set([2,3]):
            return datetime(*time_strptime(str(self.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6]) < datetime(*time_strptime(str(other.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6])
        return QtGui.QTreeWidgetItem.__lt__(self, other)

    def refresh_object(self):
        Collection.getInstance().updateVistrail(self.entity.url)
        Collection.getInstance().commit()

    def remove_object(self):
        Collection.getInstance().del_from_workspace(self.entity)
        Collection.getInstance().commit()

class QWorkspaceWindow(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Workspace')
        # make it possible to ignore updates during updating of workspace list
        self.updatingWorkspaceList = False
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)

        self.collection = Collection.getInstance()

        self.open_list = QVistrailList()
        self.open_list.collection = self.collection
        layout.addWidget(self.open_list)
        self.setLayout(layout)

        self.addButtonsToToolbar()

    def addButtonsToToolbar(self):
        # button for toggling executions
        self.execAction = QtGui.QAction(CurrentTheme.EXECUTE_PIPELINE_ICON,
                                        "Show/hide workflow executions",
                                        None,
                                        triggered=self.showWorkflowExecutions)
        self.execAction.setCheckable(True)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.execAction)
        # buttons for toggling list/tree views of workflows
        self.listAction = QtGui.QAction(CurrentTheme.LIST_VIEW_ICON,
                                        "View workflows in a list",
                                        None,
                                        triggered=self.viewAsList)
        self.listAction.setCheckable(True)
        self.listAction.setChecked(True)
        self.treeAction = QtGui.QAction(CurrentTheme.TREE_VIEW_ICON,
                                            "View workflows in a tree",
                                            None,
                                            triggered=self.viewAsTree)
        self.treeAction.setCheckable(True)
        self.workflowDisplayGroup = QtGui.QActionGroup(self)
        self.workflowDisplayGroup.setExclusive(True)
        self.workflowDisplayGroup.addAction(self.listAction)
        self.workflowDisplayGroup.addAction(self.treeAction)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.listAction)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.treeAction)
        # buttons for going to the search view to search all vistrails
        self.searchAction = QtGui.QAction("Search", self.toolWindow().toolbar,
                                          triggered=self.gotoSearch)
        self.searchAction.searchMode = False
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.searchAction)

    def state_changed(self, view):
        self.open_list.state_changed(view)
        
    def gotoSearch(self):
        from vistrails.gui.vistrails_window import _app
        if self.searchAction.searchMode:
            self.open_list.hide_search_results()
            self.searchAction.searchMode = False
            self.open_list.searchMode = False
            self.searchAction.setText("Search")

            _app.notify('query_changed', None)
        else:
            _app.qactions['search'].trigger()
 
    def updateSearchResults(self, search=None, result_list=None):
        if search is None:
            self.gotoSearch()
        elif not self.searchAction.searchMode:
            self.open_list.show_search_results()
            self.searchAction.searchMode = True
            self.open_list.searchMode = True
            self.searchAction.setText("Clear Search")
        self.open_list.update_search_results(search, result_list)

    def execution_updated(self):
        self.open_list.execution_updated()
       
    def showWorkflowExecutions(self, state):
        """ toggle show executions on/off """
        self.open_list.hideExecutions(not state)

    def viewAsList(self):
        """ Order workflow items as a flat list """
        self.open_list.isTreeView = False
        for i in xrange(self.open_list.openFilesItem.childCount()):
            item = self.open_list.openFilesItem.child(i)
            self.open_list.make_list(item)

    def viewAsTree(self):
        """ Order workflow items as a history tree """
        self.open_list.isTreeView = True
        for i in xrange(self.open_list.openFilesItem.childCount()):
            item = self.open_list.openFilesItem.child(i)
            self.open_list.make_tree(item)

    def update_workspace_list(self):
        """ Updates workspace list and highlights currentWorkspace
            Keeps 'Recent files' on top
        """
        self.updatingWorkspaceList = True
        self.workspace_list.clear()
        self.workspace_list.addItem('Default')
        if 'Default' == self.browser.collection.currentWorkspace:
            self.workspace_list.setCurrentIndex(self.workspace_list.count()-1)
        locations = self.browser.collection.workspaces.keys()
        
        workspaces = [ l for l in locations \
                         if not l.startswith('file') and \
                            not l.startswith('db') and \
                            not l == 'Default']
        workspaces.sort()
        for w in workspaces:
            self.workspace_list.addItem(w)
            if w == self.browser.collection.currentWorkspace:
                self.workspace_list.setCurrentIndex(self.workspace_list.count()-1)
        self.updatingWorkspaceList = False

    def workspace_changed(self, workspace):
        if not self.updatingWorkspaceList:
            self.browser.setup_widget(str(workspace))
    
    def reset_search(self):
        self.browser.reset_search()

    def set_results(self, results):
        pass

    def refine_mode(self, on):
        pass

    def change_vt_window(self, vistrail_window):
        self.open_list.change_vt_window(vistrail_window)

    def add_vt_window(self, vistrail_window):
        self.open_list.add_vt_window(vistrail_window)

    def remove_vt_window(self, vistrail_window):
        self.open_list.remove_vt_window(vistrail_window)

class QVistrailEntityItem(QBrowserWidgetItem):
    def __init__(self, entity, window=None):
        QBrowserWidgetItem.__init__(self, entity)
        if window:
            self.window = window
        self.entity = entity
        if not entity:
            self.setText(0, self.window.get_name())
        # make them draggable
        self.setFlags(self.flags() | QtCore.Qt.ItemIsDragEnabled
                                   | QtCore.Qt.ItemIsDropEnabled
                                   )

    def open_in_new_window(self):
        if hasattr(self, "window"):
            self.treeWidget().setSelected(self.window)
            self.treeWidget().parent().emit(QtCore.SIGNAL("detachVistrail"),
                                   self.window)

    def open_workflow(self):
        self.treeWidget().item_selected(self, 0)

    def open_workflow_in_new_tab(self):
        self.parent().parent().window.add_pipeline_view()
        self.open_workflow()

    def open_workflow_in_new_window(self):
        self.open_workflow_in_new_tab()
        self.parent().parent().window.detach_view(
                              self.parent().parent().window.tabs.currentIndex())
        
    def open_parameter_exploration(self):
        self.treeWidget().open_parameter_exploration(self.entity)
        
class QVistrailListLatestItem(QtGui.QTreeWidgetItem):
    def __init__(self):
        QtGui.QTreeWidgetItem.__init__(self)
        self.setIcon(0, CurrentTheme.PIPELINE_ICON)
        self.setText(0, '(latest)')

    def get_vistrail(self):
        return self.parent().parent()

    def open_workflow(self):
        self.treeWidget().item_selected(self, 0)

    def open_workflow_in_new_tab(self):
        self.parent().parent().window.add_pipeline_view()
        self.open_workflow()

    def open_workflow_in_new_window(self):
        self.open_workflow_in_new_tab()
        self.parent().parent().window.detach_view(
                                self.parent().parent().window.tabs.currentIndex())

class QVistrailList(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.searchMode = False
        self.search = None
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setSelectionMode(self.SingleSelection)
        self.setSelectionBehavior(self.SelectItems)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setExpandsOnDoubleClick(False)
        self.setRootIsDecorated(False)

        self.isTreeView = False
        self.executionsHidden = True

        self.collection = Collection.getInstance()
        self.items = {}

        self.delegate = QModuleTreeWidgetItemDelegate(self, self)
        self.setItemDelegate(self.delegate)

        self.openFilesItem = QtGui.QTreeWidgetItem(['Current Vistrails'])
        self.addTopLevelItem(self.openFilesItem)

        self.setup_closed_files()

        self.openFilesItem.setExpanded(True)
        self.closedFilesItem.setExpanded(True)

        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_selected)
        
        self.setIconSize(QtCore.QSize(16,16))

        self.connect(self,
                     QtCore.SIGNAL('itemPressed(QTreeWidgetItem *,int)'),
                     self.onItemPressed)
        self.updateHideExecutions()
        self.connect_current_changed()

    def setup_closed_files(self):
        self.closedFilesItem = QtGui.QTreeWidgetItem(['My Vistrails'])
        self.addTopLevelItem(self.closedFilesItem)
        closed_entities = self.collection.workspaces['Default']
        for entity in closed_entities:
            if entity.url.startswith('file://'):
                if not entity.locator().is_valid():
                    self.collection.del_from_workspace(entity)
                    self.collection.delete_entity(entity)
                    continue
            item = QVistrailEntityItem(entity)
            self.closedFilesItem.addChild(item)
            item.mashupsItem.setHidden(not item.mashupsItem.childCount())
            item.paramExplorationsItem.setHidden(
                             not item.paramExplorationsItem.childCount())

    def connect_current_changed(self):
        # using currentItemChanged makes sure a drag selects the dragged-from
        # vistrail
        self.connect(self, 
                     QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem*,"
                                   "QTreeWidgetItem*)"),
                     self.item_changed)
        # using item_clicked makes sure even selected items can be clicked
        self.connect(self, 
                     QtCore.SIGNAL("itemClicked(QTreeWidgetItem*,int)"),
                     self.item_changed)

    def disconnect_current_changed(self):
        self.disconnect(self, 
                        QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem*,"
                                      "QTreeWidgetItem*)"),
                        self.item_changed)
        self.disconnect(self, 
                        QtCore.SIGNAL("itemClicked(QTreeWidgetItem*,int)"),
                        self.item_changed)
    
    def show_search_results(self):
        self.searchResultsItem = QtGui.QTreeWidgetItem(['Search Results'])
        self.addTopLevelItem(self.searchResultsItem)
        self.openFilesItem.setHidden(True)
        self.closedFilesItem.setHidden(True)

    def hide_search_results(self):
        self.takeTopLevelItem(self.indexOfTopLevelItem(self.searchResultsItem))
        self.openFilesItem.setHidden(False)
        self.closedFilesItem.setHidden(False)

    def update_search_results(self, search=None, result_list=None):
        self.search = search
        self.searchResultsItem.takeChildren()
        if result_list is not None:
            for entity in result_list:
                item = QVistrailEntityItem(entity)
                self.searchResultsItem.addChild(item)
                item.setExpanded(True)
                item.workflowsItem.setExpanded(True)
                item.mashupsItem.setHidden(True)
                item.paramExplorationsItem.setHidden(True)
            self.searchResultsItem.setExpanded(True)

    def onItemPressed(self, item, column):
        """ onItemPressed(item: QTreeWidgetItem, column: int) -> None
        Expand/Collapse top-level item when the mouse is pressed
        
        """
        if item and item.parent() is None:
            self.setItemExpanded(item, not self.isItemExpanded(item))
            
    def search_result_selected(self, view, version):
        # need to signal the query view to change its version and vistrail
        from vistrails.gui.vistrails_window import _app
        _app.change_view(view)
        view.query_version_selected(self.search, version)

    def item_selected(self, widget_item, column):
        """ opens or displays the selected item if possible """            
        locator = None
        entity = None
        if hasattr(widget_item, 'entity') and widget_item.entity is not None:
            entity = widget_item.entity
            locator = entity.locator()
        elif isinstance(widget_item, QVistrailListLatestItem) and \
             hasattr(widget_item.parent().parent(), 'entity') and \
             widget_item.parent().parent().entity is not None:
            entity = widget_item.parent().parent().entity
            locator = entity.locator()
        elif not isinstance(widget_item, QVistrailListLatestItem):
            # no valid item selected
            return
        from vistrails.gui.vistrails_window import _app
        open_vistrail = _app.open_vistrail_without_prompt
        set_current_locator = _app.set_current_locator

        if not locator or isinstance(locator, UntitledLocator):
            # assuming an unsaved vistrail - need to use view
            vistrail_widget = widget_item
            view = None
            while view is None and vistrail_widget is not None:
                if hasattr(vistrail_widget, 'window'):
                    view = vistrail_widget.window
                    break
                elif (hasattr(vistrail_widget, 'entity') and
                      hasattr(vistrail_widget.entity, '_window')):
                    view = vistrail_widget.entity._window
                    break
                vistrail_widget = vistrail_widget.parent()

            if vistrail_widget == widget_item:
                # do nothing - view is already selected
                return
            is_execution = False
            version = None
            if isinstance(widget_item, QVistrailListLatestItem):
                version = view.controller.vistrail.get_latest_version()
            elif hasattr(widget_item, 'entity'):
                if hasattr(widget_item, 'executionList'):
                    version = widget_item.entity.name
                else:
                    is_execution = True
                    version = widget_item.parent().entity.name
            if not version:
                # assume execution
                version = str(widget_item.parent().text(0))
            if isinstance(version, str):
                try:
                    version = \
                        view.controller.vistrail.get_version_number(version)
                except Exception:
                    version = None
            if self.searchMode:
                self.search_result_selected(view, version)
            else:
                _app.change_view(view)
                if version:
                    view.version_selected(version, True, double_click=True)

            if is_execution:
                _app.qactions['provenance'].trigger()
                workflow_exec = widget_item.entity.name
                view.log_view.set_exec_by_id(workflow_exec) or \
                 view.log_view.set_exec_by_date(workflow_exec)
            return

        args = {}
        args['version'] = locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None)
        args['parameterExploration']=locator.kwargs.get('parameterExploration',
                                                        None)
        vistrail_widget = widget_item
        vistrail_entity = entity
        version = None
        if args['version']:
            vistrail_widget = widget_item.parent()
            vistrail_entity = entity.parent
            locator = vistrail_entity.locator()
            version = args['version']

        if args['parameterExploration']:
            args['parameterExploration'] = int(args['parameterExploration'])
            vistrail_widget = widget_item.parent().parent()
            vistrail_entity = entity.parent
            locator = vistrail_entity.locator()

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
            vistrail_widget = widget_item.parent().parent()
            vistrail_entity = entity.parent.parent
            locator = vistrail_entity.locator()
            locator.update_from_gui(self)

        if isinstance(widget_item, QVistrailListLatestItem):
            # find the latest item (max action id)
            vistrail = widget_item.parent().parent().window.controller.vistrail
            args['version'] = vistrail.get_latest_version()
            version = vistrail.get_latest_version()
        locator.update_from_gui(self)
        if not locator.is_valid():
            debug.critical("File not found: '%s'. Entry will be deleted." % locator.to_url())
            vistrail_widget.parent().removeChild(vistrail_widget)
            self.collection.delete_entity(vistrail_entity)
            self.collection.commit()

        view = _app.ensureVistrail(locator)
        if self.searchMode:
            self.search_result_selected(view, version)
        else:
            if view:
                self.ensureNotDiffView()
            open_vistrail(locator, **args)
            if view is None or not view.is_abstraction:
                set_current_locator(locator)
            if view and isinstance(entity, MashupEntity):
                # I am assuming that double-clicking a mashup, the user wants to
                # run the mashup
                # if it is doubele-clicked without the vistrail being open we 
                #should open the vistrail
                self.open_mashup(entity)
            if view and isinstance(entity, ParameterExplorationEntity):
                # I am assuming that double-clicking a p.e., the user wants to
                # run it
                # if it is double-clicked without the vistrail being open we 
                #should open the vistrail
                self.open_parameter_exploration(entity)

    def ensureNotDiffView(self):
        """ If current tab is a diff, create a new tab """
        from vistrails.gui.vistrails_window import _app
        view = _app.get_current_view()
        tab = view.get_current_tab()
        if isinstance(tab, QDiffView):
            view.add_pipeline_view()

    def open_mashup(self, entity):
        """open_mashup(entity:MashupEntity) -> None
        It will ask the Vistrail view to execute the mashup
        """
        self.ensureNotDiffView()
        from vistrails.gui.vistrails_window import _app
        _app.open_vistrail_without_prompt(entity.locator(),
                                          execute_workflow=True)
        
    def edit_mashup(self, entity):
        """open_mashup(entity:MashupEntity) -> None
        It will ask the Vistrail view to execute the mashup
        """
        from vistrails.gui.vistrails_window import _app
        _app.open_vistrail_without_prompt(entity.locator())

    def open_parameter_exploration(self, entity):
        """open_parameter_exploration(entity:ParameterExplorationEntity) -> None
        It will switch to the correct pipeline and pe, and open the pe
        """
        self.ensureNotDiffView()
        from vistrails.gui.vistrails_window import _app
        view = _app.get_current_view()
        if view.controller.current_version != entity.pe.action_id:
            view.version_selected(entity.pe.action_id, True)
        if entity.pe != view.controller.current_parameter_exploration:
            view.controller.current_parameter_exploration = entity.pe
            view.pe_view.setParameterExploration(entity.pe)
        _app.qactions['explore'].trigger()
        
    def mimeData(self, itemList):
        """ mimeData(itemList) -> None        
        Setup the mime data to contain itemList because Qt 4.2.2
        implementation doesn't instantiate QTreeWidgetMimeData
        anywhere as it's supposed to. It must have been a bug...
        
        """
        data = QtGui.QTreeWidget.mimeData(self, itemList)
        data.items = itemList
        return data

    def dropEvent( self, event):
        event.accept()
        destination = self.itemAt(event.pos())
        if not destination:
            return
        if isinstance(event.source(), QVistrailList):
            data = event.mimeData()
            if hasattr(data, 'items'):
                assert len(data.items) == 1
                source = data.items[0]
                if not source or source == destination:
                    return

                if hasattr(source, 'window') and hasattr(destination, 'window'):
                    # both are vistrails
                    self.merge_vistrails(source, destination)
                elif (isinstance(source, QVistrailListLatestItem) or
                      hasattr(source, 'executionList')) and \
                     (isinstance(destination, QVistrailListLatestItem) or
                      hasattr(destination, 'executionList')):
                    # workflows can be from diff vistrails
                    self.visual_diff(source, destination)

    def merge_vistrails(self, source, destination):
        if source.window.controller.changed or destination.window.controller.changed:
            text = ('Both Vistrails need to be saved before they can be merged.')
            QtGui.QMessageBox.information(None, 'Cannot perform merge',
                              text, '&OK')
            return
        res = QtGui.QMessageBox.question(None, 'Merge the histories of these 2 vistrails into a new vistrail?',
                          source.window.get_name() + '\n' + destination.window.get_name(),
                          buttons=QtGui.QMessageBox.Yes,
                          defaultButton=QtGui.QMessageBox.No)
        if res == QtGui.QMessageBox.Yes:
            from vistrails.gui.vistrails_window import _app
            _app.merge_vistrails(destination.window.controller, source.window.controller)

    def visual_diff(self, source, destination):
        source_parent = source.parent()
        while not hasattr(source_parent, 'window'):
            source_parent = source_parent.parent()
        destination_parent = destination.parent()
        while not hasattr(destination_parent, 'window'):
            destination_parent = destination_parent.parent()
        controller_1 = source_parent.window.controller
        controller_2 = destination_parent.window.controller
        if hasattr(source, 'entity'):
            v1 = source.entity.locator().kwargs.get('version_node', None)
        else:
            v1 = controller_1.vistrail.get_latest_version()
        if hasattr(destination, 'entity'):
            v2 = destination.entity.locator().kwargs.get('version_node', None)
        else:
            v2 = controller_2.vistrail.get_latest_version()
        
        # if we don't have the same vistrail, pass the second vistrail
        if id(controller_1) == id(controller_2):
            source_parent.window.diff_requested(v1, v2)
        else:
            source_parent.window.diff_requested(v1, v2, controller_2)
            
    def hideExecutions(self, hidden):
        self.executionsHidden = hidden
        self.updateHideExecutions()
        
    def updateHideExecutions(self):            
        for i in xrange(self.openFilesItem.childCount()):
            vt = self.openFilesItem.child(i)
            if not hasattr(vt, 'tag_to_item'):
                continue
            for item in vt.tag_to_item.itervalues():
                if not hasattr(item, 'executionList'):
                    continue
                for exec_item in item.executionList:
                    exec_item.setHidden(self.executionsHidden)
        for i in xrange(self.closedFilesItem.childCount()):
            vt = self.closedFilesItem.child(i)
            if not hasattr(vt, 'tag_to_item'):
                continue
            for item in vt.tag_to_item.itervalues():
                if not hasattr(item, 'executionList'):
                    continue
                for exec_item in item.executionList:
                    exec_item.setHidden(self.executionsHidden)

    def make_list(self, item):
        """ construct a list from the tagged workflows in a loaded vistrail
        """
        self.setSortingEnabled(False)
        if not (hasattr(item, 'tag_to_item') or hasattr(item, 'mshp_to_item')): 
            return
        for wf in item.tag_to_item.itervalues():
            index = wf.parent().indexOfChild(wf)
            wf = wf.parent().takeChild(index)
            item.workflowsItem.addChild(wf)
        self.updateHideExecutions()
        self.setSortingEnabled(True)

    def make_tree(self, item):
        """ construct a tree from the tagged workflows in a loaded vistrail
        """
        self.setSortingEnabled(False)
        if not hasattr(item, 'window'):
            return
        am = item.window.controller.vistrail.actionMap
        tm = item.window.controller.vistrail.get_tagMap()
        vm = dict((v,k) for k, v in tm.iteritems())
        # loop through tagged workflows and add to parent workflow
        if not hasattr(item, 'tag_to_item'):
            return
        for tag, wf in item.tag_to_item.iteritems():
            if tag not in vm:
                continue
            # find parent
            version = vm[tag]
            action = am[version]
            while action.parent in am:
                action = am[action.parent]
                if action.timestep in tm:
                    break
            if action.timestep not in tm or action.timestep == version:
                continue
            parent_tag = tm[action.timestep]
            if parent_tag in item.tag_to_item:
                parent_wf = item.tag_to_item[parent_tag]
                index = wf.parent().indexOfChild(wf)
                wf = wf.parent().takeChild(index)
                parent_wf.addChild(wf)
        self.updateHideExecutions()
        self.setSortingEnabled(True)


    def state_changed(self, view):
        """ update tags, mashups and parameter explorations """
        # sometimes references to closed views trigger a state_changed event
        if id(view) not in self.items:
            return
        item = self.items[id(view)]
        entity = item.entity
        
        (new_entity, was_updated) = \
            entity.update_vistrail(view.controller.vistrail)
        if was_updated:
            item.setText(0, entity.name)
        (added_wfs, deleted_wfs) = entity.update_workflows()
        (more_added_wfs, added_wf_execs) = entity.update_log()
        view.controller.vistrail.mashups = view.controller._mashups
        (added_mshps, deleted_mshps) = entity.update_mashups()
        (added_pes, deleted_pes) = entity.update_parameter_explorations()

        for wf_entity in deleted_wfs:
            assert(wf_entity.name in item.tag_to_item)
            child = item.tag_to_item[wf_entity.name]
            child_idx = child.parent().indexOfChild(child)
            child.parent().takeChild(child_idx)
            del item.tag_to_item[wf_entity.name]
        for wf_entity in chain(added_wfs, more_added_wfs):
            if not wf_entity.name.startswith('Version #'):
                childItem = QWorkflowEntityItem(wf_entity)
                item.workflowsItem.addChild(childItem)
                item.tag_to_item[wf_entity.name] = childItem

        for wf_exec_entity in added_wf_execs:
            parent_version = wf_exec_entity.workflow_exec.parent_version
            wf_entity = entity.wf_entity_map[parent_version]
            if not wf_entity.name.startswith('Version #'):
                assert(wf_entity.name in item.tag_to_item)
                wf_item = item.tag_to_item[wf_entity.name]
                child = QWorkflowExecEntityItem(wf_exec_entity)
                wf_item.addChild(child)
                wf_item.executionList.append(child)
        self.updateHideExecutions()
    
        for mshp_entity in deleted_mshps:
            assert(mshp_entity.name in item.mshp_to_item)
            child = item.mshp_to_item[mshp_entity.name]
            child_idx = child.parent().indexOfChild(child)
            child.parent().takeChild(child_idx)
            del item.mshp_to_item[mshp_entity.name]
        for mshp_entity in added_mshps:
            childItem = QMashupEntityItem(mshp_entity)
            item.mashupsItem.addChild(childItem)
            item.mshp_to_item[mshp_entity.name] = childItem
        item.mashupsItem.setHidden(not len(item.mshp_to_item))

        for pe_entity in deleted_pes:
            assert(pe_entity.url in item.pe_to_item)
            child = item.pe_to_item[pe_entity.url]
            child_idx = child.parent().indexOfChild(child)
            child.parent().takeChild(child_idx)
            del item.pe_to_item[pe_entity.url]
        for pe_entity in added_pes:
            childItem = QParamExplorationEntityItem(pe_entity)
            item.paramExplorationsItem.addChild(childItem)
            # keep list of tagged workflows
            item.pe_to_item[pe_entity.url] = childItem
        item.paramExplorationsItem.setHidden(not len(item.pe_to_item))

        if self.isTreeView:
            self.make_tree(item)
        else:
            self.make_list(item)

    def execution_updated(self):
        """ Add new executions to workflow """
        # get view and item
        from vistrails.gui.vistrails_window import _app
        view = _app.get_current_view()
        if id(view) not in self.items:
            return
        item = self.items[id(view)]

        entity = item.entity
        entity.set_vistrail(view.controller.vistrail)
        (added_wfs, added_wf_execs) = entity.update_log()
        for wf_entity in added_wfs:
            if not wf_entity.name.startswith('Version #'):
                childItem = QWorkflowEntityItem(wf_entity)
                item.workflowsItem.addChild(childItem)
                # keep list of tagged workflows
                item.tag_to_item[wf_entity.name] = childItem
            
        for wf_exec_entity in added_wf_execs:
            parent_version = wf_exec_entity.workflow_exec.parent_version
            wf_entity = entity.wf_entity_map[parent_version]
            if not wf_entity.name.startswith('Version #'):
                assert(wf_entity.name in item.tag_to_item)
                wf_item = item.tag_to_item[wf_entity.name]
                child = QWorkflowExecEntityItem(wf_exec_entity)
                wf_item.addChild(child)
                wf_item.executionList.append(child)
        self.updateHideExecutions()

    def add_vt_window(self, vistrail_window):
        locator = vistrail_window.controller.locator
        entity = None
        entity_was_none = False
        item_reused = False
        if locator:
            entity = self.collection.fromUrl(locator.to_url())
        if entity is None:
            entity = VistrailEntity(vistrail_window.controller.vistrail)
            entity_was_none = True

        # remove item from recent list
        for i in xrange(self.closedFilesItem.childCount()):
            recent = self.closedFilesItem.child(i)
            if entity and recent and recent.entity and \
                recent.entity.url == entity.url:
                self.setSelected(None)
                index = self.closedFilesItem.indexOfChild(recent)
                self.closedFilesItem.takeChild(index)
        item = QVistrailEntityItem(entity, vistrail_window)
        item.current_item = QVistrailListLatestItem()
        item.workflowsItem.addChild(item.current_item)
        if id(vistrail_window) in self.items:
            # window already exists  
            old_item = self.items[id(vistrail_window)]
            url = None
            if old_item.entity is not None:
                url = old_item.entity.url
            # if there was a change in the locator, we need to remove the old 
            # item and put in the closed vistrails area
            
            if url != vistrail_window.controller.locator.to_url():
                self.remove_vt_window(vistrail_window)
            else:
                # we will reuse the item
                if hasattr(item, 'entity'):
                    old_item.entity = item.entity
                old_item.window = item.window
                old_item.current_item = item.current_item
                old_item.workflowsItem = item.workflowsItem
                old_item.mashupsItem = item.mashupsItem
                old_item.paramExplorationsItem = item.paramExplorationsItem
                old_item.tag_to_item = item.tag_to_item
                old_item.mshp_to_item = item.mshp_to_item
                old_item.pe_to_item = item.pe_to_item
                old_item.setText(0, item.text(0))
                while old_item.childCount():
                    child = old_item.child(0)
                    index = old_item.indexOfChild(child)
                    old_item.takeChild(index)
                while item.childCount():
                    child = item.child(0)
                    index = item.indexOfChild(child)
                    child = item.takeChild(index)
                    old_item.addChild(child)
                item = old_item
                item_reused = True
        
        if not item_reused:
            self.items[id(vistrail_window)] = item        
            if entity_was_none:
                self.collection.add_temp_entity(entity)
            entity.is_open = True
            entity._window = vistrail_window
            self.openFilesItem.addChild(item)
            item.setExpanded(True)
            item.workflowsItem.setExpanded(True)
            item.mashupsItem.setExpanded(True)
            item.paramExplorationsItem.setExpanded(True)
        item.mashupsItem.setHidden(not item.mashupsItem.childCount())
        item.paramExplorationsItem.setHidden(
                             not item.paramExplorationsItem.childCount())
        if self.isTreeView:
            self.make_tree(item)
        else:
            self.make_list(item)
        self.item_changed(item, None)
        self.updateHideExecutions()

    def remove_vt_window(self, vistrail_window):
        if id(vistrail_window) not in self.items:
            return
        self.setSelected(None)
        item = self.items[id(vistrail_window)]
        del self.items[id(vistrail_window)]
        delattr(item, 'window')
        index = self.openFilesItem.indexOfChild(item)
        item = self.openFilesItem.takeChild(index)
        url = None
        if item.entity is not None:
            item.entity.is_open = False
            item.entity._window = None 
            url = item.entity.url
        item.current_item.parent().removeChild(item.current_item)
        # entity may have changed
        entity = None
        if url is None:
            locator = vistrail_window.controller.locator
            if locator and not isinstance(locator, UntitledLocator):
                entity = self.collection.fromUrl(locator.to_url())
        else:
            entity = self.collection.fromUrl(url)
            
        if entity and not self.collection.is_temp_entity(entity) and \
                not vistrail_window.is_abstraction:
            item = QVistrailEntityItem(entity)
            if self.isTreeView:
                self.make_tree(item)
            else:
                self.make_list(item)
            self.closedFilesItem.addChild(item)
            item.setText(0, entity.name)
        self.updateHideExecutions()

    def change_vt_window(self, vistrail_window):
        self.setSelected(vistrail_window)

    def setSelected(self, view):
        """ Highlights the vistrail item for the selected item"""
        self.disconnect_current_changed()

        def setBold(parent_item):
            """ """
            for i in xrange(parent_item.childCount()):
                item = parent_item.child(i)
                font = item.font(0)
                window = item.window if hasattr(item, 'window') else None
                font.setBold(bool(window and view and view == window))
                item.setFont(0, font)
                if window:
                    item.setText(0, window.get_name())
                
        if not self.openFilesItem.isHidden():
            setBold(self.openFilesItem)
        elif self.searchMode:
            setBold(self.searchResultsItem)
        self.connect_current_changed()
            
    def item_changed(self, item, prev_item):
        if not item:
            return
        vistrail = item
        while not hasattr(vistrail, 'window'):
            if not vistrail or not vistrail.parent:
                # parent node
                return
            vistrail = vistrail.parent()

        self.setSelected(vistrail.window)
        self.parent().emit(QtCore.SIGNAL("vistrailChanged(PyQt_PyObject)"), 
                           vistrail.window)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            items = self.selectedItems()
            if len(items) == 1:
                item = items[0]
                if item.parent() == self.openFilesItem:
                    # close current vistrail
                    from vistrails.gui.vistrails_window import _app
                    if hasattr(item, 'window'):
                        _app.close_vistrail(item.window)
                    else:
                        _app.close_vistrail()
                elif item.parent() == self.closedFilesItem:
                    # remove from closed list
                    self.closedFilesItem.removeChild(item)
                    self.collection.del_from_workspace(item.entity)
                    self.collection.delete_entity(item.entity)
                    self.collection.commit()
                elif isinstance(item,QParamExplorationEntityItem):
                    parent = item.parent()
                    while parent and not hasattr(parent, 'window'):
                        parent = parent.parent()
                    if parent:
                        # delete this parameter exploration
                        parent.window.controller.vistrail.delete_paramexp(
                                                               item.entity.pe)
                        parent.window.controller.set_changed(True)

        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)

    def close_vistrail(self, item):
        if item.parent() == self.openFilesItem and hasattr(item, 'window'):
            from vistrails.gui.vistrails_window import _app
            _app.close_vistrail(item.window)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QVistrailEntityItem):
            if item and self.openFilesItem.indexOfChild(item) == -1:
                # vistrail is not open
                return
            # item is vistrail
            menu = QtGui.QMenu(self)
            new_window = QtGui.QAction("Open in New Window", self,
                                       triggered=item.open_in_new_window)
            new_window.setStatusTip("Open specified vistrail file in another "
                                    "window")
            menu.addAction(new_window)
            close = QtGui.QAction("Close", self,
                                  triggered=lambda: self.close_vistrail(item))
            close.setStatusTip("Close the specified vistrail file")
            menu.addAction(close)
            menu.exec_(event.globalPos())
        elif (isinstance(item, QWorkflowEntityItem) or 
                isinstance(item, QVistrailListLatestItem)):
            if item and self.openFilesItem.indexOfChild(item.get_vistrail()) == -1:
                # vistrail is not open
                return
            # item is workflow
            menu = QtGui.QMenu(self)
            act = QtGui.QAction("Open", self,
                                triggered=item.open_workflow)
            act.setStatusTip("Open specified workflow in this window")
            menu.addAction(act)
            act = QtGui.QAction("Open in new Tab", self,
                                triggered=item.open_workflow_in_new_tab)
            act.setStatusTip("Open specified workflow in a new tab")
            menu.addAction(act)
            act = QtGui.QAction("Open in new Window", self,
                                triggered=item.open_workflow_in_new_window)
            act.setStatusTip("Open specified workflow in a new window")
            menu.addAction(act)
            menu.exec_(event.globalPos())
        elif isinstance(item, QMashupEntityItem):
            if item and self.openFilesItem.indexOfChild(item.parent().parent()) == -1:
                # vistrail is not open
                return
            # item is mashup
            menu = QtGui.QMenu(self)
            act = QtGui.QAction("Edit", self,
                                triggered=item.edit_mashup)
            act.setStatusTip("Edit the mashup")
            menu.addAction(act)
            act = QtGui.QAction("Execute", self,
                                triggered=item.open_mashup)
            act.setStatusTip("Execute the mashup")
            menu.addAction(act)
            menu.exec_(event.globalPos())
