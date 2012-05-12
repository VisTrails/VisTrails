###############################################################################
##
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

from PyQt4 import QtCore, QtGui

import glob
from itertools import chain
import os
from datetime import datetime
from time import strptime
from core.thumbnails import ThumbnailCache
from core import debug
from core.collection import Collection, MashupEntity, ThumbnailEntity, \
    VistrailEntity, WorkflowEntity, WorkflowExecEntity
from core.collection.search import SearchCompiler, SearchParseError
from core.db.locator import FileLocator
from gui.common_widgets import QToolWindowInterface, QToolWindow, QSearchBox
from gui.vistrails_palette import QVistrailsPaletteInterface
from gui.theme import CurrentTheme
from gui.module_palette import QModuleTreeWidgetItemDelegate
from gui.vis_diff import QDiffView
from core.collection.entity import Entity

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
        # FIXME only uses top level items
        if items is None:
            items = [self.topLevelItem(i) 
                     for i in xrange(self.topLevelItemCount())]
        for item in items:
            if search.match(item.entity):
                item.setHidden(False)
                parent = item.parent()
                while parent is not None:
                    if parent.isHidden():
                        parent.setHidden(False)
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
        #print 'item_selected'
        locator = widget_item.entity.locator()
        #print "locator", locator
        import gui.application
#        if not locator.is_valid():
#            debug.critical("Locator is not valid:" % locator.to_url())
#            return
        app = gui.application.get_vistrails_application()
        open_vistrail = app.builderWindow.open_vistrail_without_prompt
        args = {}
        args['version'] = locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None)
        if args['version']:
            # set vistrail name
            locator = widget_item.entity.parent.locator()
            pass
            #locator._name = widget_item.entity.parent.name

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
            locator = widget_item.entity.parent.parent.locator()
            locator.update_from_gui(self)
            # set vistrail name
            #locator._name = widget_item.entity.parent.parent.name
            
        locator.update_from_gui(self)
#        print '*** opening'
#        print locator.to_url()
#        print locator.name
#        print '***'
        open_vistrail(locator, **args)
                                                       
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
                    "", "Vistrail files (*.vt *.xml)");
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
                    "", QtGui.QFileDialog.ShowDirsOnly);
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
            except:
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
#        if self.collection.currentWorkspace != 'Default':
        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

class QWorkflowsItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['Workflows'])

class QMashupsItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['Mashups'])

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
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
            return
        
        # # old, esoteric code
        #
        # l = list(str(x) for x in entity.save())
        # l.pop(0) # remove identifier
        # type = l.pop(0)
        # desc = l[5]
        # if len(desc) > 20:
        #     l[5] = desc[:20] + '...'
        klass = self.__class__
        self.entity = entity
        QtGui.QTreeWidgetItem.__init__(self, parent, [entity.name])
        if entity.type_id == VistrailEntity.type_id:
            # vistrail - create Workflows and Mashups item
            self.workflowsItem = QWorkflowsItem()
            self.addChild(self.workflowsItem)
            self.mashupsItem = QMashupsItem()
            self.addChild(self.mashupsItem)
#            self.mashupsItem.setHidden(True)
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
            self.tag_to_item = {}
            self.mshp_to_item = {}
        elif entity.type_id == WorkflowEntity.type_id:
            self.setIcon(0, CurrentTheme.PIPELINE_ICON)
            self.executionList = []
        elif entity.type_id == WorkflowExecEntity.type_id:
            self.setIcon(0, CurrentTheme.EXECUTE_PIPELINE_ICON)

        tooltip = '<html>%s' % entity.url
            
        for child in entity.children:
            # l = child.save()
            if child.type_id == ThumbnailEntity.type_id:
                # is a thumbnail
                # add to parent workflow item
                cache = ThumbnailCache.getInstance()
                path = cache.get_abs_name_entry(child.name)
                if path:
                    pixmap = QtGui.QPixmap(path)
                    if pixmap and not pixmap.isNull():
                        self.setIcon(0, QtGui.QIcon(pixmap.scaled(16, 16)))
                    tooltip += """<br/><img border=0 src='%(path)s'/>
                        """ % {'path':path}
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
                if not child.name.startswith('Version #'):
                    childItem = QMashupEntityItem(child)
                    self.mashupsItem.addChild(childItem)
                    # keep list of tagged workflows
                    self.mshp_to_item[child.name] = childItem
            else:
                self.addChild(QBrowserWidgetItem(child))
        if entity.description:
            tooltip += '<br/>%s' % entity.description
        tooltip += '</html>'
        self.setToolTip(0, tooltip)

    #def __lt__(self, other):
    #    sort_col = self.treeWidget().sortColumn()
    #    if sort_col in set([4]):
    #        return int(self.text(sort_col)) < int(other.text(sort_col))
    #    elif sort_col in set([2,3]):
    #        return datetime(*strptime(str(self.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6]) < datetime(*strptime(str(other.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6])
    #    return QtGui.QTreeWidgetItem.__lt__(self, other)

    def refresh_object(self):
        Collection.getInstance().updateVistrail(self.entity.url)
        Collection.getInstance().commit()

    def remove_object(self):
        Collection.getInstance().del_from_workspace(self.entity)
        Collection.getInstance().commit()
        
class QWorkflowEntityItem(QBrowserWidgetItem):
    pass

class QWorkflowExecEntityItem(QBrowserWidgetItem):
    pass

class QMashupEntityItem(QBrowserWidgetItem):
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
#        if self.collection.currentWorkspace != 'Default':
        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

class QExplorerWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, entity, parent=None):
        l = list(str(x) for x in entity.save())
        l.pop(0) # remove identifier
        type = l.pop(0)
        desc = l.pop(5)
#        l.pop(7)
#        if len(desc) > 20:
#            l[5] = desc[:20] + '...'
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
            return datetime(*strptime(str(self.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6]) < datetime(*strptime(str(other.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6])
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

#        self.workspace_list = QtGui.QComboBox()
#        self.titleWidget = QtGui.QWidget()
#        self.titleLayout = QtGui.QHBoxLayout()
#        self.titleLayout.setMargin(0)
#        self.titleLayout.setSpacing(5)
#        self.titleLayout.addWidget(QtGui.QLabel('Project:'), 0)
#        self.titleLayout.addWidget(self.workspace_list, 1)
#        self.titleWidget.setLayout(self.titleLayout)
#        self.setTitleBarWidget(self.titleWidget)
        self.setWindowTitle('Workspace')
        # make it possible to ignore updates during updating of workspace list
        self.updatingWorkspaceList = False
#        self.connect(self.workspace_list,
#                     QtCore.SIGNAL("currentIndexChanged(QString)"),
#                     self.workspace_changed)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
#        self.search_box = QSearchBox(True, False, self)
#        layout.addWidget(self.search_box)

        self.collection = Collection.getInstance()

        self.open_list = QVistrailList()
        self.open_list.collection = self.collection
        layout.addWidget(self.open_list)
#        layout.addWidget(self.titleWidget)

#        self.browser = QWorkspaceWidget(self.collection)
#        layout.addWidget(self.browser)
#        self.browser.setup_widget('Default')
#        self.connect(self.search_box, QtCore.SIGNAL('resetSearch()'),
#                     self.reset_search)
#        self.connect(self.search_box, QtCore.SIGNAL('executeSearch(QString)'),
#                     self.execute_search)
#        self.connect(self.search_box, QtCore.SIGNAL('refineMode(bool)'),
#                     self.refine_mode)
#        self.connect(self.browser, QtCore.SIGNAL('workspaceListUpdated()'),
#                     self.update_workspace_list)
        self.setLayout(layout)
#        self.update_workspace_list()

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
        if self.searchAction.searchMode:
            self.open_list.hide_search_results()
            self.searchAction.searchMode = False
            self.open_list.searchMode = False
            self.searchAction.setText("Search")

            from gui.vistrails_window import _app
            _app.notify('query_changed', None)
        else:
            from gui.vistrails_window import _app
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

    def execute_search(self, text):
        s = str(text)
        try:
            search = SearchCompiler(s).searchStmt
        except SearchParseError, e:
            debug.warning("Search Parse Error", str(e))
            search = None

        self.browser.run_search(search)

    def refine_mode(self, on):
        pass

    def change_vt_window(self, vistrail_window):
        self.open_list.change_vt_window(vistrail_window)

    def add_vt_window(self, vistrail_window):
        self.open_list.add_vt_window(vistrail_window)

    def remove_vt_window(self, vistrail_window):
        self.open_list.remove_vt_window(vistrail_window)

class QExplorerDialog(QToolWindow, QToolWindowInterface):
    def __init__(self, parent=None):
        QToolWindow.__init__(self, parent=parent)

        self.widget = QtGui.QWidget()
        self.setWidget(self.widget)
        self.workspace_list = QtGui.QComboBox()
        self.setTitleBarWidget(self.workspace_list)
        # make it possible to ignore updates during updating of workspace list
        self.updatingWorkspaceList = False
        self.connect(self.workspace_list,
                     QtCore.SIGNAL("currentIndexChanged(QString)"),
                     self.workspace_changed)
        layout = QtGui.QVBoxLayout()
#        layout.setMargin(0)
#        layout.setSpacing(5)
        self.search_box = QSearchBox(True, False, self)
        layout.addWidget(self.search_box)

        self.collection = Collection.getInstance()
        self.browser = QExplorerWidget(self.collection, self)
        layout.addWidget(self.browser)
        self.browser.setup_widget('Recent files')
        self.connect(self.search_box, QtCore.SIGNAL('resetSearch()'),
                     self.reset_search)
        self.connect(self.search_box, QtCore.SIGNAL('executeSearch(QString)'),
                     self.execute_search)
        self.connect(self.search_box, QtCore.SIGNAL('refineMode(bool)'),
                     self.refine_mode)
        self.connect(self.browser, QtCore.SIGNAL('workspaceListUpdated()'),
                     self.update_workspace_list)
        self.widget.setLayout(layout)
        self.update_workspace_list()
 
    def update_workspace_list(self):
        """ Updates workspace list and highlights currentWorkspace
            Keeps 'Default' on top
        """
        self.updatingWorkspaceList = True
        self.workspace_list.clear()
        self.workspace_list.addItem('Default')
        if 'Default' == self.browser.collection.currentWorkspace:
            self.workspace_list.setCurrentIndex(self.workspace_list.count()-1)
        sorted_workspaces = self.browser.collection.workspaces.keys()
        if 'Default' in sorted_workspaces:
            sorted_workspaces.remove('Default')
        sorted_workspaces.sort()
        for p in sorted_workspaces:
            self.workspace_list.addItem(p)
            if p == self.browser.collection.currentWorkspace:
                self.workspace_list.setCurrentIndex(self.workspace_list.count()-1)
        self.updatingWorkspaceList = False

    def workspace_changed(self, workspace):
        if not self.updatingWorkspaceList:
            self.browser.setup_widget(str(workspace))
    
    def reset_search(self):
        self.browser.reset_search()

    def set_results(self, results):
        pass

    def execute_search(self, text):
        s = str(text)
        try:
            search = SearchCompiler(s).searchStmt
        except SearchParseError, e:
            debug.warning("Search Parse Error", str(e))
            search = None

        self.browser.run_search(search)

    def refine_mode(self, on):
        pass

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
#                                   | QtCore.Qt.ItemIsSelectable
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
        
    def open_mashup(self):
        self.treeWidget().open_mashup(self.entity)
        
    def edit_mashup(self):
        self.treeWidget().edit_mashup(self.entity)

class QVistrailListLatestItem(QtGui.QTreeWidgetItem):
    def __init__(self):
        QtGui.QTreeWidgetItem.__init__(self)
        self.setIcon(0, CurrentTheme.PIPELINE_ICON)
        self.setText(0, '(latest)')

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
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
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
                     QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem*,"
                                   "QTreeWidgetItem*)"),
                     self.item_changed)

        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_selected)
        self.setIconSize(QtCore.QSize(16,16))

        self.connect(self,
                     QtCore.SIGNAL('itemPressed(QTreeWidgetItem *,int)'),
                     self.onItemPressed)
        self.updateHideExecutions()

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
            self.closedFilesItem.addChild(QVistrailEntityItem(entity))
            
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
            self.searchResultsItem.setExpanded(True)

    def onItemPressed(self, item, column):
        """ onItemPressed(item: QTreeWidgetItem, column: int) -> None
        Expand/Collapse top-level item when the mouse is pressed
        
        """
        if item and item.parent() == None:
            self.setItemExpanded(item, not self.isItemExpanded(item))
            
    def search_result_selected(self, view, version):
        # need to signal the query view to change its version and vistrail
        from gui.vistrails_window import _app
        _app.change_view(view)
        view.query_version_selected(self.search, version)

    def item_selected(self, widget_item, column):
        """ opens or displays the selected item if possible """            
        locator = None
        entity = None
        if hasattr(widget_item, 'entity') and widget_item.entity is not None:
            entity = widget_item.entity
            locator = entity.locator()
        elif type(widget_item) == QVistrailListLatestItem and \
             hasattr(widget_item.parent().parent(), 'entity') and \
             widget_item.parent().parent().entity is not None:
            entity = widget_item.parent().parent().entity
            locator = entity.locator()
        elif not type(widget_item) == QVistrailListLatestItem:
            # no valid item selected
            return
            
        from gui.vistrails_window import _app
        open_vistrail = _app.open_vistrail_without_prompt
        set_current_locator = _app.set_current_locator

        if not locator:
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
            if type(widget_item) == QVistrailListLatestItem:
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
            if type(version) == str:
                try:
                    version = \
                        view.controller.vistrail.get_version_number(version)
                except:
                    version = None
            if self.searchMode:
                self.search_result_selected(view, version)
            else:
                # _app.view_changed(view)
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

        vistrail_widget = widget_item
        vistrail_entity = entity
        version = None
        if args['version']:
            vistrail_widget = widget_item.parent()
            vistrail_entity = entity.parent
            locator = vistrail_entity.locator()
            version = args['version']

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
            vistrail_widget = widget_item.parent().parent()
            vistrail_entity = entity.parent.parent
            locator = vistrail_entity.locator()
            locator.update_from_gui(self)
            # set vistrail name
            #locator._name = widget_item.entity.parent.parent.name
            
        if type(widget_item) == QVistrailListLatestItem:
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

    def ensureNotDiffView(self):
        """ If current tab is a diff, create a new tab """
        from gui.vistrails_window import _app
        view = _app.get_current_view()
        tab = view.get_current_tab()
        if type(tab) == QDiffView:
            view.add_pipeline_view()

    def open_mashup(self, entity):
        """open_mashup(entity:MashupEntity) -> None
        It will ask the Vistrail view to execute the mashup
        """
        self.ensureNotDiffView()
        from gui.vistrails_window import _app
        view = _app.get_current_view()
        view.open_mashup(entity.mashup)
        
    def edit_mashup(self, entity):
        """open_mashup(entity:MashupEntity) -> None
        It will ask the Vistrail view to execute the mashup
        """
        from gui.vistrails_window import _app
        view = _app.get_current_view()
        view.edit_mashup(entity.mashup)
        
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
        if type(event.source())==QVistrailList:
            data = event.mimeData()
            if hasattr(data, 'items'):
                assert len(data.items) == 1
                source = data.items[0]
                if not source or source == destination:
                    return

                if hasattr(source, 'window') and hasattr(destination, 'window'):
                    # both are vistrails
                    self.merge_vistrails(source, destination)
                elif (type(source) == QVistrailListLatestItem or
                      hasattr(source, 'executionList')) and \
                     (type(destination) == QVistrailListLatestItem or
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
            from gui.vistrails_window import _app
            _app.merge_vistrails(destination.window.controller, source.window.controller)

    def visual_diff(self, source, destination):
        source_parent = source.parent()
        while not hasattr(source_parent, 'window'):
            source_parent = source_parent.parent()
        destination_parent = destination.parent()
        while not hasattr(destination_parent, 'window'):
            destination_parent = destination_parent.parent()
        vistrail_1 = source_parent.window.controller.vistrail
        vistrail_2 = destination_parent.window.controller.vistrail
        if hasattr(source, 'entity'):
            v1 = source.entity.locator().kwargs.get('version_node', None)
        else:
            v1 = vistrail_1.get_latest_version()
        if hasattr(destination, 'entity'):
            v2 = destination.entity.locator().kwargs.get('version_node', None)
        else:
            v2 = vistrail_2.get_latest_version()
        
        # if we don't have the same vistrail, pass the second vistrail
        if id(vistrail_1) == id(vistrail_2):
            source_parent.window.diff_requested(v1, v2)
        else:
            source_parent.window.diff_requested(v1, v2, vistrail_2)
            
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
        for tag, wf in item.tag_to_item.iteritems():
            index = wf.parent().indexOfChild(wf)
            wf = wf.parent().takeChild(index)
            item.workflowsItem.addChild(wf)
        for tag, mshp in item.mshp_to_item.iteritems():
            index = mshp.parent().indexOfChild(mshp)
            mshp = mshp.parent().takeChild(index)
            item.mashupsItem.addChild(mshp)
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
        """ update tags and mashups """
        item = self.items[id(view)]
        entity = item.entity
        
        (new_entity, was_updated) = \
            entity.update_vistrail(view.controller.vistrail)
        if new_entity:
            Collection.getInstance().create_vistrail_entity(
                view.controller.vistrail)
            self.add_vt_window(view)
            return
        elif was_updated:
            item.setText(0, entity.name)
        (added_wfs, deleted_wfs) = entity.update_workflows()
        (more_added_wfs, added_wf_execs) = entity.update_log()
        (added_mshps, deleted_mshps) = entity.update_mashups()

        for wf_entity in deleted_wfs:
            assert(wf_entity.name in item.tag_to_item)
            child = item.tag_to_item[wf_entity.name]
            child_idx = child.parent().indexOfChild(child)
            child.parent().takeChild(child_idx)
            del item.tag_to_item[wf_entity.name]
        for wf_entity in chain(added_wfs, more_added_wfs):
            # this is from the original code...
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
    
        for mshp_entity in deleted_mshps:
            assert(mshp_entity.name in item.mshp_to_item)
            child = item.mshp_to_item[mshp_entity.name]
            child_idx = child.parent().indexOfChild(child)
            child.parent().takeChild(child_idx)
            del item.mshp_to_item[mshp_entity.name]
        for mshp_entity in added_mshps:
            if not mshp_entity.name.startswith('Version #'):
                childItem = QMashupEntityItem(mshp_entity)
                item.mashupsItem.addChild(childItem)
                # keep list of tagged workflows
                item.mshp_to_item[mshp_entity.name] = childItem

        self.make_tree(item) if self.isTreeView else self.make_list(item)

    def execution_updated(self):
        """ Add new executions to workflow """
        # get view and item
        from gui.vistrails_window import _app
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
                item = self.closedFilesItem.takeChild(index)
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
                old_item.tag_to_item = item.tag_to_item
                old_item.mshp_to_item = item.mshp_to_item
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
                # why is this all the way down here?!?
                # moving the create stmt up much earlier so it is set
                # on the item!
                # entity = VistrailEntity(vistrail_window.controller.vistrail)
                self.collection.add_temp_entity(entity)
            entity.is_open = True
            entity._window = vistrail_window
            self.openFilesItem.addChild(item)
        self.make_tree(item) if self.isTreeView else self.make_list(item)
        item.workflowsItem.setExpanded(True)
        item.mashupsItem.setExpanded(True)
        self.setSelected(vistrail_window)
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
            if locator:
                entity = self.collection.fromUrl(locator.to_url())
        else:
            entity = self.collection.fromUrl(url)
            
        if entity and not self.collection.is_temp_entity(entity) and \
                not vistrail_window.is_abstraction:
            item = QVistrailEntityItem(entity)
            self.make_tree(item) if self.isTreeView else self.make_list(item)
            self.closedFilesItem.addChild(item)
            item.setText(0, entity.name)
        self.updateHideExecutions()

    def change_vt_window(self, vistrail_window):
        self.setSelected(vistrail_window)

    def setSelected(self, view):
        for item in self.selectedItems():
            item.setSelected(False)

        def setBold(parent_item):
            for i in xrange(parent_item.childCount()):
                item = parent_item.child(i)
                font = item.font(0)
                window = item.window if hasattr(item, 'window') else None
                font.setBold(view == window if window and view else False)
                item.setFont(0, font)
                if window:
                    item.setText(0, window.get_name())
                # item.setSelected(view == item.window 
                #                  if window and view else False)
                
        if not self.openFilesItem.isHidden():
            setBold(self.openFilesItem)
        elif self.searchMode:
            setBold(self.searchResultsItem)
            
    def item_changed(self, item, prev_item):
        if not item:
            return
        vistrail = item
        while not hasattr(vistrail, 'window'):
            if not vistrail or not vistrail.parent:
                # parent node
                return
            vistrail = vistrail.parent()
        #print "*** item clicked", id(vistrail.window)

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
                    from gui.vistrails_window import _app
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
        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item and self.openFilesItem.indexOfChild(item) != -1:
            # item is vistrail
            menu = QtGui.QMenu(self)
            act = QtGui.QAction("Open in New Window", self,
                                triggered=item.open_in_new_window)
            act.setStatusTip("Open specified vistrail file in another window")
            menu.addAction(act)
            menu.exec_(event.globalPos())
        elif item and (isinstance(item, QVistrailEntityItem) or 
                       isinstance(item, QVistrailListLatestItem)):
            vtparent = item.parent().parent()
            if (self.openFilesItem.indexOfChild(vtparent) != -1 and
                isinstance(item.parent(),QWorkflowsItem)):
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
            elif (self.openFilesItem.indexOfChild(vtparent) != -1 and
                  isinstance(item.parent(),QMashupsItem)):  
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

if __name__ == '__main__':
    import sys
    sys.path.append('/vistrails/src/query/vistrails')
    from core.collection import Collection
    
#     vt_1 = load_vistrail(ZIPFileLocator('/vistrails/examples/spx.vt'))[0]
#     vt_2 = load_vistrail(DBLocator('vistrails.sci.utah.edu', 3306,
#                                    'vistrails', 'vistrails', '8edLj4',
#                                    obj_id=9, obj_type='vistrail'))[0]

    c = Collection('test.db')
    # c.clear()
    # e_1 = c.create_vistrail_entity(vt_1)
    # e_2 = c.create_vistrail_entity(vt_2)
    
    c.entities = {}
    c.load_entities()

    app = QtGui.QApplication(sys.argv)
    widget = QBrowserWidget(c)
    widget.setup_widget('Recent items')
    widget.show()
    sys.exit(app.exec_())
