###########################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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

from PyQt4 import QtCore, QtGui

from datetime import datetime
from time import strptime
from gui.theme import CurrentTheme
from core.thumbnails import ThumbnailCache
from core.collection import Collection

class QBrowserWidget(QtGui.QTreeWidget):
    def __init__(self, collection, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.collection = collection
        self.entities = {}
        self.collection.add_listener(self)
#        self.setColumnCount(7)
#        self.setHeaderLabels(['name', 'user', 'mod_date', 'create_date', 'size', 'description', 'url'])
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        #self.setHeaderLabels(['Vistrail Browser'])
        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_selected)
        self.setIconSize(QtCore.QSize(16,16))

    def setup_widget(self):
        self.clear()
        for entity in self.collection.entities.itervalues():
            if entity.parent is None:
                item = QBrowserWidgetItem(entity)
                self.entities[entity.id] = item
                self.addTopLevelItem(item)
        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

    def entityCreated(self, entity):
        self.setup_widget()

    def entityDeleted(self, entity):
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
        print '*** opening'
        print locator.to_url()
        print locator.name
        print '***'
        
#         fname = str(widget_item.data(2, QtCore.Qt.DisplayRole).toString())
#         tag = str(widget_item.data(1, QtCore.Qt.DisplayRole).toString())
#         print "parent emiting", fname, tag
        import gui.application
        app = gui.application.VistrailsApplication
        open_vistrail = app.builderWindow.open_vistrail_without_prompt
        open_vistrail(locator, locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None))
                                                       
        # self.parent().parent().parent().emit(QtCore.SIGNAL('callGlobalMethod'),
        #                                      'open_vistrail_without_prompt', 
        #                                      locator,
        #                                      locator.kwargs.get('version_node', None) or
        #                                      locator.kwargs.get('version_tag', None))

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            # find top level
            p = item
            while p.parent():
                p = p.parent()
            menu = QtGui.QMenu(self)
            ref = QtGui.QAction("&Refresh", self)
            ref.setStatusTip("Refresh the selected object")
            QtCore.QObject.connect(ref,
                                   QtCore.SIGNAL("triggered()"),
                                   p.refresh_object)
            menu.addAction(ref)
            refAll = QtGui.QAction("Check &All", self)
            refAll.setStatusTip("Removes deleted files")
            QtCore.QObject.connect(refAll,
                                   QtCore.SIGNAL("triggered()"),
                                   self.check_objects)
            menu.addAction(refAll)
            addDir = QtGui.QAction("Add workflows from &directory", self)
            addDir.setStatusTip("Add all vistrail files in the current directory")
            QtCore.QObject.connect(addDir,
                                   QtCore.SIGNAL("triggered()"),
                                   self.add_dir)
            menu.addAction(addDir)
            menu.exec_(event.globalPos())

    def check_objects(self):
        items = [self.topLevelItem(i) 
                 for i in xrange(self.topLevelItemCount())]
        collection = Collection.getInstance()
        for item in items:
            if not collection.urlExists(item.entity.url):
                collection.delete_entity(item.entity) 

    def add_dir(self):
        # TODO dir selector
        s = QtGui.QFileDialog.getExistingDirectory(
                    self, "Choose a directory",
                    "", QtGui.QFileDialog.ShowDirsOnly);
        if str(s):
            Collection.getInstance().update_from_directory(str(s))

class QBrowserWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, entity, parent=None):
        self.entity = entity
        l = list(str(x) for x in self.entity.save())
        l.pop(0) # remove identifier
        type = l.pop(0)
        desc = l[5]
        if len(desc) > 20:
            l[5] = desc[:20] + '...'
        QtGui.QTreeWidgetItem.__init__(self, parent, [l[0]])
        if type == '1':
            self.setIcon(0, CurrentTheme.HISTORY_ICON)
        elif type == '2':
            self.setIcon(0, CurrentTheme.PIPELINE_ICON)
        elif type == '3':
            self.setIcon(0, CurrentTheme.EXECUTE_PIPELINE_ICON)
            
        for child in entity.children:
            l = child.save()
            if l[1] == 4:
                cache = ThumbnailCache.getInstance() #.get_directory()
                path = cache.get_abs_name_entry(l[2])
                if path:
                    self.setIcon(0, QtGui.QIcon(path))
                continue
            else:
                self.addChild(QBrowserWidgetItem(child))

    def __lt__(self, other):
        sort_col = self.treeWidget().sortColumn()
        if sort_col in set([4]):
            return int(self.text(sort_col)) < int(other.text(sort_col))
        elif sort_col in set([2,3]):
            return datetime(*strptime(str(self.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6]) < datetime(*strptime(str(other.text(sort_col)), '%d %b %Y %H:%M:%S')[0:6])
        return QtGui.QTreeWidgetItem.__lt__(self, other)

    def refresh_object(self):
        Collection.getInstance().updateVistrail(self.entity.url)

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
    widget.setup_widget()
    widget.show()
    sys.exit(app.exec_())
