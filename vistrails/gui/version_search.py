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
""" This file describe a widget for search and refine the version tree

QVersionProp
QVersionNotes
"""

from PyQt4 import QtCore, QtGui
from core.query.version import SearchCompiler, SearchParseError, TrueSearch
from gui.common_widgets import QToolWindowInterface
from gui.theme import CurrentTheme
from core.query.visual import VisualQuery

################################################################################

class QVersionSearch(QtGui.QWidget, QToolWindowInterface):
    """
    QVersionSearch is a widget that can perform a search/refine on
    version tree
    
    """    
    def __init__(self, parent=None):
        """ QVersionSearch(parent: QWidget) -> QVersionSearch
        Initialize the main layout
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Query')

        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(5)
        self.setLayout(vLayout)
        
        self.statementEdit = QtGui.QLineEdit()
        vLayout.addWidget(self.statementEdit)

        hLayout = QtGui.QHBoxLayout()
        hLayout.setMargin(5)
        hLayout.setSpacing(5)
        vLayout.addLayout(hLayout)
        
        self.searchButton = QtGui.QPushButton('Search')
        hLayout.addWidget(self.searchButton)

        self.resetButton = QtGui.QPushButton('Reset')
        hLayout.addWidget(self.resetButton)
        
        self.saveButton = QtGui.QPushButton('Save')
        self.saveButton.setEnabled(False)
        hLayout.addWidget(self.saveButton)

        self.refineCheckBox = QtGui.QCheckBox('Refine')
        vLayout.addWidget(self.refineCheckBox)

        savedQueriesTitle = QtGui.QGroupBox('Saved Queries', self)
        savedQueriesTitle.setFlat(True)
        vLayout.addWidget(savedQueriesTitle)

        self.savedQueries = QSavedQueries()
        vLayout.addWidget(self.savedQueries)
        self.connect(self.savedQueries,
                     QtCore.SIGNAL('itemClicked(QTreeWidgetItem *,int)'),
                     self.selectionChanged)
        self.connect(self.savedQueries,
                     QtCore.SIGNAL('currentItemChanged(QTreeWidgetItem *,'
                                   'QTreeWidgetItem *)'),
                     self.selectionChanged)
        self.connect(self.savedQueries,
                     QtCore.SIGNAL('listChanged'),
                     self.queryListChanged)

        self.connect(self.statementEdit,
                     QtCore.SIGNAL('returnPressed()'),
                     self.searchButton.click)

        self.connect(self.searchButton,
                     QtCore.SIGNAL('clicked()'),
                     self.search)

        self.connect(self.refineCheckBox,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.refine)

        self.connect(self.resetButton,
                     QtCore.SIGNAL('clicked()'),
                     self.reset)

        self.connect(self.saveButton,
                     QtCore.SIGNAL('clicked()'),
                     self.save)

        self.controller = None

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None
        Assign the vistrail controller to this search and add its
        saved queries
        
        """
        if self.controller:
            self.disconnect(self.controller,
                            QtCore.SIGNAL('searchChanged'),
                            self.searchChanged)
        self.controller = controller
        if self.controller:
            self.savedQueries.clear()
            for (qType, qName, qText) in self.controller.vistrail.savedQueries:
                if qType=='string':
                    try:
                        search = SearchCompiler(qText).searchStmt
                    except SearchParseError, e:
                        search = None
                else:
                    print 'Loading visual query not yet supported'
                self.savedQueries.addTopLevelItem(
                    QSavedQueriesItem(qName, search, qText))
            self.connect(self.controller,
                         QtCore.SIGNAL('searchChanged'),
                         self.searchChanged)

    def searchChanged(self):
        """ searchChanged() -> None
        Update the status of the saved buton
        
        """
        if self.controller:
            self.saveButton.setEnabled(self.controller.search!=None)

    def search(self):
        """ search() -> None
        Search and update the version tree
        
        """
        if self.controller:
            s = str(self.statementEdit.text())
            try:
                search = SearchCompiler(s).searchStmt
            except SearchParseError, e:
                QtGui.QMessageBox.warning(self,
                                          QtCore.QString("Search Parse Error"),
                                          QtCore.QString(str(e)),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.NoButton,
                                          QtGui.QMessageBox.NoButton)
                search = None
            self.controller.setSearch(search, s)

    def refine(self, state):
        """ refine(state: int) -> None
        Refine and update the version tree
        
        """
        if self.controller:
            self.controller.setRefine(state==QtCore.Qt.Checked)

    def reset(self):
        """ reset() -> None
        Reset the version tree to include everything
        
        """
        if self.controller:
            self.controller.setSearch(None)

    def save(self):
        """ save() -> None
        Save the current query into the list
        
        """
        if self.controller:            
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Query Name',
                                                    'Enter the query alias',
                                                    QtGui.QLineEdit.Normal,
                                                    self.controller.searchStr)
            self.savedQueries.addTopLevelItemEmit(
                QSavedQueriesItem(text,
                                  self.controller.search,
                                  self.controller.searchStr))            
            
    def selectionChanged(self, item, column):
        """ selectionChanged(item: QTreeWidgetItem, column: int) -> None
        Apply the query of the selected item
        
        """
        if self.controller:
            if item==None:
                self.controller.setSearch(None)
            else:
                self.controller.setSearch(item.search,
                                          item.searchStr)

    def queryListChanged(self):
        """ queryListChanged() -> None
        Handling the saved query changed
        
        """
        if self.controller:
            queries = self.savedQueries.getSavedQueries()
            self.controller.setSavedQueries(queries)
            
class QSavedQueries(QtGui.QTreeWidget):
    """ QSavedQueries is a tree widget containing previous saved
    queries. For each QBE item, there will be an icon next to it
    indicating that it is a visual query.
    
    """
    def __init__(self, parent=None):
        """ QSavedQueries(parent: QWidget) -> QSavedQueries
        Set to the icon mode view
        
        """
        QtGui.QTreeWidget.__init__(self, parent)
        self.setRootIsDecorated(False)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.header().hide()

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Handling 'Delete' event
        
        """
        if event.key()==QtCore.Qt.Key_Delete:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.currentItem()))
            self.emit(QtCore.SIGNAL('listChanged'))
        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)

    def addTopLevelItemEmit(self, item):
        """ addTopLevelItemEmit(item: QTreeWidgetItem) -> None
        Override to emit the listChanged signal
        
        """
        QtGui.QTreeWidget.addTopLevelItem(self, item)
        self.setCurrentItem(item)
        self.emit(QtCore.SIGNAL('listChanged'))

    def getSavedQueries(self):
        """ getSavedQueries() -> [list of (type, name, text)]
        Return all the saved queries in the widget
        
        """
        result = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            qType = 'string'
            if type(item.search)==VisualQuery:
                qType = 'visual'
            qName = item.text(0)
            qText = item.searchStr
            result.append((qType, qName, qText))
        return result

class QSavedQueriesItem(QtGui.QTreeWidgetItem):
    """ QSavedQueriesItem is the tree widget item containing its label
    and query template
    
    """
    def __init__(self, label, search, searchStr):
        """ QSavedQueriesItem(label: str,
                              search: SearchStmt,
                              searchStr: str) -> QSavedQueriesItem
        Set up the columns and store the query template
        
        """
        QtGui.QTreeWidgetItem.__init__(self, QtCore.QStringList(label))        
        self.search = search
        self.searchStr = searchStr
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        if type(search)==VisualQuery:        
            icon = CurrentTheme.VISUAL_QUERY_ICON
        else:
            pix = QtGui.QPixmap(32,32)
            pix.fill(QtCore.Qt.transparent)
            icon = QtGui.QIcon(pix)
        self.setIcon(0, icon)

class QSavedQueriesControlWidget(QtGui.QWidget):
    """ QSavedQueriesControlWidget is a custom widget display control
    buttons for a query item.
    
    """
    def __init__(self, parent=None):        
        """ QSavedQueriesControlWidget(parent: QWidget)
                                       -> QSavedQueriesControlWidget
        Initialize a horizontal layout with 3 buttons
        
        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.previewButton = QtGui.QPushButton(CurrentTheme.ZOOM_ICON)
        
        self.editButton = QtGui.QPushButton('Edit')
        self.editButton.setFlat(True)
        layout.addWidget(self.editButton)
        
