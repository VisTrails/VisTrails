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

""" This file contains widgets related to the bookmark palette
displaying a list of all user's bookmarks in Vistrails

QBookmarkPanel
QBookmarkPalette
QBookmarkTreeWidget
QBookmarkTreeWidgetItem
"""

from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from gui.common_widgets import (QSearchTreeWindow,
                                QSearchTreeWidget,
                                QToolWindowInterface)

################################################################################
class QBookmarkPanel(QtGui.QFrame, QToolWindowInterface):
    """
    QBookmarkPanel contains a Bookmark palette and a toolbar for interacting
    with the bookmarks.
    
    """
    def __init__(self, parent=None, manager=None):
        """ QBookmarkPanel(parent: QWidget) -> QBookmarkPanel
        Creates a panel with a palette of bookmarks and a toolbar.
        Set bookmark manager
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Panel|QtGui.QFrame.Sunken)
        self.manager = manager
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.bookmarkPalette = QBookmarkPalette(None, self.manager)
        layout.addWidget(self.bookmarkPalette, 1)
        self.setWindowTitle('Bookmarks')
        
        self.createActions()
        self.createToolBar()
        self.connectSignals()
        
    def createActions(self):
        """ createActions() -> None
        Construct all menu/toolbar actions for bookmarks  window
        
        """
        self.executeAction = QtGui.QAction(CurrentTheme.EXECUTE_PIPELINE_ICON,
                                       'Execute', self)
        self.executeAction.setToolTip('Execute checked bookmarks')
        self.executeAction.setStatusTip(self.executeAction.toolTip())

        self.removeAction = QtGui.QAction(CurrentTheme.BOOKMARKS_REMOVE_ICON,
                                          'Remove', self)
        self.removeAction.setToolTip('Remove selected bookmark')
        self.removeAction.setStatusTip(self.removeAction.toolTip())

    def createToolBar(self):
        """ createToolBar() -> None
        Create a default toolbar for bookmarks panel
        
        """
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setIconSize(QtCore.QSize(32,32))
        self.toolBar.setWindowTitle('Bookmarks controls')
        self.layout().addWidget(self.toolBar)
        self.toolBar.addAction(self.executeAction)
        self.toolBar.addAction(self.removeAction)

    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between  GUI components        
        
        """
        self.connect(self.executeAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.bookmarkPalette.executeCheckedWorkflows)
        self.connect(self.removeAction,
                     QtCore.SIGNAL('triggered(bool)'),
                     self.bookmarkPalette.treeWidget.removeCurrentItem)

    def updateBookmarkPalette(self):
        """updateBookmarkPalette() -> None
        Reload bookmarks from the collection
        
        """
        self.bookmarkPalette.treeWidget.updateFromBookmarkCollection()

class QBookmarkPalette(QSearchTreeWindow):
    """
    QBookmarkPalette just inherits from QSearchTreeWindow to have its
    own type of tree widget

    """
    def __init__(self, parent=None, manager=None):
        """ QBookmarkPalette(parent: QWidget) -> QBookmarkPalette
        Set bookmark manager
        """
        QSearchTreeWindow.__init__(self, parent)
        self.manager = manager
        self.checkedList = []
        self.connect(self.treeWidget,
                     QtCore.SIGNAL("itemChanged(QTreeWidgetItem*,int)"),
                     self.processItemChanges)
        self.connect(self.treeWidget,
                     QtCore.SIGNAL("itemRemoved(int)"),
                     self.removeBookmark)
        
    def createTreeWidget(self):
        """ createTreeWidget() -> QBookmarkTreeWidget
        Return the search tree widget for this window
        
        """
        return QBookmarkTreeWidget(self)

    def executeCheckedWorkflows(self):
        """ executeCheckedWorkflows() -> None
        get the checked bookmark ids and send them to the manager

        """
        if len(self.checkedList) > 0:
            self.manager.executeWorkflows(self.checkedList)

    def processItemChanges(self, item, col):
        """processItemChanges(item: QBookmarkTreeWidgetItem, col:int)
        Event handler for propagating bookmarking changes to the collection. 
        
        """
        if col == 0 and item != self.treeWidget.headerItem():
            if item.bookmark.type == 'item':
                id = item.bookmark.id
                if item.checkState(0) ==QtCore.Qt.Unchecked:
                    if id in self.checkedList:
                        self.checkedList.remove(id)
                        self.manager.loadPipelines(self.checkedList)
                elif item.checkState(0) ==QtCore.Qt.Checked:
                    if id not in self.checkedList:
                        self.checkedList.append(id)
                        self.manager.loadPipelines(self.checkedList)
            if str(item.text(0)) != item.bookmark.name:
                item.bookmark.name = str(item.text(0))
                self.manager.writeBookmarks()    
    
    def removeBookmark(self, id):
        """removeBookmark(id: int) -> None 
        Tell manager to remove bookmark with id 

        """
        if id in self.checkedList:
            self.checkedList.remove(id)
            self.manager.loadPipelines(self.checkedList)
        self.manager.removeBookmark(id)
        
class QBookmarkTreeWidget(QSearchTreeWidget):
    """
    QBookmarkTreeWidget is a subclass of QSearchTreeWidget to display all
    user's Vistrails Bookmarks 
    
    """
    def __init__(self, parent=None):
        """ __init__(parent: QWidget) -> QBookmarkTreeWidget
        Set up size policy and header

        """
        QSearchTreeWidget.__init__(self, parent)
        self.setColumnCount(1)
        self.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.header().hide()
        
    def updateFromBookmarkCollection(self):
        """ updateFromBookmarkCollection() -> None        
        Setup this tree widget to show bookmarks currently inside
        BookmarksManager.bookmarks
        
        """
        def createBookmarkItem(parentFolder, bookmark):
            """ createBookmarkItem(parentFolder: QBookmarkTreeWidgetItem,
                                   bookmark: BookmarkTree) 
                                                    -> QBookmarkTreeWidgetItem
            Traverse a bookmark to create items recursively. Then return
            its bookmark item
            
            """
            labels = QtCore.QStringList()
            bObj = bookmark.bookmark
            labels << bObj.name
            bookmarkItem = QBookmarkTreeWidgetItem(bookmark.bookmark,
                                                   parentFolder,
                                                   labels)
            if bObj.type == "item":
                bookmarkItem.setToolTip(0,bObj.filename)
                bookmarkItem.setCheckState(0,QtCore.Qt.Unchecked)
            
            for child in bookmark.children:
                createBookmarkItem(bookmarkItem, child)
            
        if self.parent().manager:
            self.clear()
            bookmark = self.parent().manager.collection.bookmarks
            createBookmarkItem(self, bookmark)
            self.sortItems(0,QtCore.Qt.AscendingOrder)
            self.expandAll()

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Delete or 
            event.key() == QtCore.Qt.Key_Backspace):
            if self.isVisible():      
                self.removeCurrentItem()
        QtGui.QTreeWidget.keyPressEvent(self, event)

    def removeCurrentItem(self):
        """removeCurrentItem() -> None Removes from the GUI and Collection """
        item = self.currentItem()
        parent = item.parent()
        parent.takeChild(parent.indexOfChild(item))
        id = item.bookmark.id
        del item
        self.emit(QtCore.SIGNAL("itemRemoved(int)"),id)
         

class QBookmarkTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QBookmarkTreeWidgetItem represents bookmark on QBookmarkTreeWidget
    
    """
    def __init__(self, bookmark, parent, labelList):
        """ QBookmarkTreeWidgetItem(bookmark: Bookmark,
                                  parent: QTreeWidgetItem
                                  labelList: QStringList)
                                  -> QBookmarkTreeWidget                                  
        Create a new tree widget item with a specific parent and
        labels

        """
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)
        self.bookmark = bookmark
        self.setFlags((QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
                       | QtCore.Qt.ItemIsEnabled | 
                       QtCore.Qt.ItemIsUserCheckable))
