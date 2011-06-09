###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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
import os
from datetime import datetime
from time import strptime
from core import debug
from core.thumbnails import ThumbnailCache
from core.collection import Collection
from core.collection.search import SearchCompiler, SearchParseError
from core.db.locator import FileLocator
from gui.common_widgets import QToolWindowInterface, QToolWindow, QSearchBox
from gui.vistrails_palette import QVistrailsPaletteInterface
from gui.theme import CurrentTheme

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
        print 'item_selected'
        locator = widget_item.entity.locator()
        print "locator", locator
        import gui.application
#        if not locator.is_valid():
#            debug.critical("Locator is not valid:" % locator.to_url())
#            return
        app = gui.application.VistrailsApplication
        open_vistrail = app.builderWindow.open_vistrail_without_prompt
        args = {}
        args['version'] = locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None)
        print "version is", args['version']
        if args['version']:
            # set vistrail name
            locator = widget_item.entity.parent.locator()
            print "locator set to", locator
            pass
            #locator._name = widget_item.entity.parent.name

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        print "wfexec", workflow_exec
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
            locator = widget_item.entity.parent.parent.locator()
            print "locator set to", locator
            locator.update_from_gui(self)
            # set vistrail name
            #locator._name = widget_item.entity.parent.parent.name
            
        locator.update_from_gui(self)
        print '*** opening'
        print locator.to_url()
        print locator.name
        print '***'
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

class QBrowserWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, entity, parent=None):
        if not entity:
            QtGui.QTreeWidgetItem.__init__(self, parent)
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
            return
        l = list(str(x) for x in entity.save())
        l.pop(0) # remove identifier
        type = l.pop(0)
        desc = l[5]
        if len(desc) > 20:
            l[5] = desc[:20] + '...'
        QtGui.QTreeWidgetItem.__init__(self, parent, [l[0]])
        self.entity = entity
        if type == '1':
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
        elif type == '2':
            self.setIcon(0, CurrentTheme.PIPELINE_ICON)
        elif type == '3':
            self.setIcon(0, CurrentTheme.EXECUTE_PIPELINE_ICON)

        tooltip = '<html>%s' % entity.url
            
        for child in entity.children:
            l = child.save()
            # handle thumbnails
            if l[1] == 4:
                cache = ThumbnailCache.getInstance() #.get_directory()
                path = cache.get_abs_name_entry(l[2])
                if path:
                    self.setIcon(0, QtGui.QIcon(path))
                    tooltip += """<br/><img border=0 src='%(path)s'/>
                        """ % {'path':path}
                continue
            elif not child.name.startswith('Version #'):
                self.addChild(QBrowserWidgetItem(child))
        if entity.description:
            tooltip += '<br/>%s' % entity.description
        tooltip += '</html>'
        self.setToolTip(0, tooltip)

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

class QVistrailListItem(QBrowserWidgetItem):
    def __init__(self, entity, window):
        QBrowserWidgetItem.__init__(self, entity)
        self.window = window
        if not entity:
            self.setText(0, self.window.get_name())
        # make them draggable
        self.setFlags(self.flags() | QtCore.Qt.ItemIsDragEnabled
                                   | QtCore.Qt.ItemIsDropEnabled
#                                   | QtCore.Qt.ItemIsSelectable
                                   )

class QVistrailList(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setExpandsOnDoubleClick(False)
        self.connect(self, 
                     QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem*,"
                                   "QTreeWidgetItem*)"),
                     self.item_changed)
        self.collection = Collection.getInstance()
        self.items = {}

        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_selected)
        self.setIconSize(QtCore.QSize(16,16))

    def item_selected(self, widget_item, column):
        print 'item_selected'
        if not hasattr(widget_item, 'entity'):
            return
        locator = widget_item.entity.locator()
        print "locator", locator
        import gui.application
#        if not locator.is_valid():
#            debug.critical("Locator is not valid:" % locator.to_url())
#            return
        app = gui.application.VistrailsApplication
        open_vistrail = app.builderWindow.open_vistrail_without_prompt
        args = {}
        args['version'] = locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None)
        print "version is", args['version']
        if args['version']:
            # set vistrail name
            locator = widget_item.entity.parent.locator()
            print "locator set to", locator
            pass
            #locator._name = widget_item.entity.parent.name

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        print "wfexec", workflow_exec
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
            locator = widget_item.entity.parent.parent.locator()
            print "locator set to", locator
            locator.update_from_gui(self)
            # set vistrail name
            #locator._name = widget_item.entity.parent.parent.name
            
        locator.update_from_gui(self)
        print '*** opening'
        print locator.to_url()
        print locator.name
        print '***'
        open_vistrail(locator, **args)

    def mimeData(self, itemList):
        """ mimeData(itemList) -> None        
        Setup the mime data to contain itemList because Qt 4.2.2
        implementation doesn't instantiate QTreeWidgetMimeData
        anywhere as it's supposed to. It must have been a bug...
        
        """
        data = QtGui.QTreeWidget.mimeData(self, itemList)
        print "mimeData called", itemList
        data.items = itemList
        return data

    def dropEvent( self, event):
        event.accept()
        destination = self.itemAt(event.pos())
        if not destination or type(destination) != QVistrailListItem:
            return
        if type(event.source())==QVistrailList:
            data = event.mimeData()
            if hasattr(data, 'items'):
                assert len(data.items) == 1
                source = data.items[0]
                if not source or type(source) != QVistrailListItem or source == destination:
                    return
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


    def add_vt_window(self, vistrail_window):
        entity = None
        locator = vistrail_window.controller.locator
        if locator:
            entity = self.collection.fromUrl(locator.to_url())
        item = QVistrailListItem(entity, vistrail_window)
        self.addTopLevelItem(item)
        self.items[id(vistrail_window)] = item
        self.setSelected(vistrail_window)

    def remove_vt_window(self, vistrail_window):
        self.takeTopLevelItem(self.indexOfTopLevelItem(
                self.items[id(vistrail_window)]))

    def change_vt_window(self, vistrail_window):
        self.setSelected(vistrail_window)

    def setSelected(self, view):
        for i in xrange(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            font = item.font(0)
            font.setBold(view == item.window)
            item.setFont(0, font)
            item.setText(0, item.window.get_name())
                
    def item_changed(self, item, prev_item):
        if not item:
            return
        vistrail = item
        while not hasattr(vistrail, 'window'):
            vistrail = vistrail.parent()
        print "*** item clicked", id(vistrail.window)

        self.setSelected(vistrail.window)
        self.parent().emit(QtCore.SIGNAL("vistrailChanged(PyQt_PyObject)"), 
                           vistrail.window)

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
