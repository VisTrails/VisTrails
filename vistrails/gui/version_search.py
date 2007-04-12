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
from gui.pipeline_view import QPipelineScene
from core.query.visual import VisualQuery
from core.vistrail.pipeline import Pipeline

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

        self.connect(self.savedQueries,
                     QtCore.SIGNAL('editQueryReEmit'),
                     self.editQuery)

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
                    pipeline = Pipeline.loadFromString(qText)
                    search = VisualQuery(pipeline)
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
            if type(self.controller.search)==VisualQuery:
                name = 'Query By Example'
            else:
                name = self.controller.searchStr
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Query Name',
                                                    'Enter the query alias',
                                                    QtGui.QLineEdit.Normal,
                                                    name)
            self.savedQueries.addTopLevelItemEmit(
                QSavedQueriesItem(text,
                                  self.controller.search,
                                  self.controller.searchStr))            
            
    def selectionChanged(self, item, column):
        """ selectionChanged(item: QTreeWidgetItem, column: int) -> None
        Apply the query of the selected item
        
        """
        if self.controller:
            items =  self.savedQueries.selectedItems()
            if len(items)==0:
                self.controller.setSearch(None)
            else:
                item = items[0]
                self.controller.setSearch(item.search,
                                          item.searchStr)

    def queryListChanged(self):
        """ queryListChanged() -> None
        Handling the saved query changed
        
        """
        if self.controller:
            queries = self.savedQueries.getSavedQueries()
            self.controller.setSavedQueries(queries)
            
    def editQuery(self, queryData):
        """ editQuery(queryData: str or Pipeline) -> None        
        Bring the queryData to the right place (template edit box or
        the query pipeline view) for editing
        
        """
        if type(queryData)==Pipeline:
            vistrailView = self.controller.vistrailView
            queryTab = vistrailView.queryTab
            queryController = queryTab.controller
            queryController.setPipeline(queryData)
            vistrailView.stackedWidget.setCurrentIndex(2)
            queryTab.pipelineView.scene().fitToAllViews()
        else:
            self.statementEdit.setText(queryData)
            self.statementEdit.setFocus(QtCore.Qt.TabFocusReason)
            
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
        self.setColumnCount(2)
        iconSize = self.style().pixelMetric(QtGui.QStyle.PM_SmallIconSize)
        self.setIconSize(QtCore.QSize(iconSize, iconSize))
        self.header().resizeSection(0, iconSize*2+4)
        self.header().hide()

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Handling 'Delete' event
        
        """
        if event.key()==QtCore.Qt.Key_Delete:
            self.removeQuery(self.currentItem())
            self.emit(QtCore.SIGNAL('listChanged'))
        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)

    def addTopLevelItemEmit(self, item):
        """ addTopLevelItemEmit(item: QTreeWidgetItem) -> None
        Override to emit the listChanged signal
        
        """
        self.addTopLevelItem(item)
        self.setCurrentItem(item)
        self.emit(QtCore.SIGNAL('listChanged'))

    def addTopLevelItem(self, item):
        """ addTopLevelItem(item: QTreeWidgetItem) -> None
        Beside adding the item into the widget, also create the
        control widget of the item on the second column
        
        """
        QtGui.QTreeWidget.addTopLevelItem(self, item)
        row = self.indexOfTopLevelItem(item)
        index = self.model().index(row, 0)
        controlWidget = QSavedQueriesControlWidget(item, self)
        self.setIndexWidget(index, controlWidget)
        self.connect(controlWidget, QtCore.SIGNAL('editQueryRequest'),
                     self.editQueryReEmit)
        self.connect(controlWidget, QtCore.SIGNAL('removeQueryRequest'),
                     self.removeQuery)

    def getSavedQueries(self):
        """ getSavedQueries() -> [list of (type, name, text)]
        Return all the saved queries in the widget
        
        """
        result = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if type(item.search)==VisualQuery:
                qType = 'visual'
            else:
                qType = 'string'
            qName = str(item.text(1))
            qText = item.searchStr
            result.append((qType, qName, qText))
        return result

    def editQueryReEmit(self, queryData):
        """ editQueryPass(queryData: str or Pipeline) -> None        
        Re-emit the signal to the higher level
        
        """
        self.emit(QtCore.SIGNAL('editQueryReEmit'), queryData)

    def removeQuery(self, item):
        """ removeQuery(item: QSavedQueriesItem) -> None
        Remove the top-level item item from the query list
        
        """
        self.takeTopLevelItem(self.indexOfTopLevelItem(item))

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
        texts = QtCore.QStringList() << '' << label
        QtGui.QTreeWidgetItem.__init__(self, texts)
        self.search = search
        self.searchStr = searchStr
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        if type(search)==VisualQuery:        
            icon = CurrentTheme.VISUAL_QUERY_ICON
        else:
            pix = QtGui.QPixmap(32,32)
            pix.fill(QtCore.Qt.transparent)
            icon = QtGui.QIcon(pix)
        self.setIcon(1, icon)

class QQueryPreviewMenu(QtGui.QMenu):
    """ QQueryPreviewMenu is a menu that either has a pipeline pixmap in
    the background or just a query text
    
    """

    def __init__(self, queryData, parent=None):
        """ QQueryPreviewMenu(queryData: Pipeline, parent: QWidget)
                             -> QQueryPreviewMenu
        Create the query pixmap based on the pipeline
        
        """
        QtGui.QMenu.__init__(self, parent)
        self._pixmap = QtGui.QPixmap()
        if type(queryData)==Pipeline:
            scene = QPipelineScene()
            scene.setupScene(queryData)
            image = QtGui.QImage(CurrentTheme.QUERY_PREVIEW_SIZE[0],
                                 CurrentTheme.QUERY_PREVIEW_SIZE[1],
                                 QtGui.QImage.Format_ARGB32_Premultiplied)
            painter = QtGui.QPainter()
            painter.begin(image)
            painter.setRenderHints(QtGui.QPainter.Antialiasing |
                                   QtGui.QPainter.TextAntialiasing |
                                   QtGui.QPainter.SmoothPixmapTransform)
            scene.render(painter, QtCore.QRectF(), scene.sceneBoundingRect)
            painter.end()
            self._pixmap = QtGui.QPixmap.fromImage(image)

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the size of the preview menu
        
        """
        fw = self.style().pixelMetric(QtGui.QStyle.PM_MenuBarPanelWidth)
        return QtCore.QSize(fw*2 + CurrentTheme.QUERY_PREVIEW_SIZE[0],
                            fw*2 + CurrentTheme.QUERY_PREVIEW_SIZE[0])

    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Paint the pixmap (if available) into the menu
        
        """
        QtGui.QMenu.paintEvent(self, event)
        if self._pixmap:
            rect = self.rect()
            fw = self.style().pixelMetric(QtGui.QStyle.PM_MenuBarPanelWidth)
            rect.adjust(fw, fw, -fw, fw)
            painter = QtGui.QPainter(self)
            painter.drawPixmap(rect, self._pixmap)

class QSavedQueriesControlWidget(QtGui.QWidget):
    """ QSavedQueriesControlWidget is a custom widget display control
    buttons for a query item.
    
    """
    def __init__(self, item, parent=None):
        """ QSavedQueriesControlWidget(item: QSavedQueriesItem, parent: QWidget)
                                       -> QSavedQueriesControlWidget
        Initialize a horizontal layout with 3 buttons based on the query item
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.item = item

        if type(item.search)==VisualQuery:
            self.queryData = item.search.queryPipeline
        else:
            self.queryData = item.searchStr

        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.previewButton = QtGui.QToolButton()
        self.previewButton.setIcon(CurrentTheme.QUERY_VIEW_ICON)
        self.previewButton.setAutoRaise(True)
        self.previewButton.setToolTip('Click to preview the query')
        self.previewButton.setStatusTip(self.previewButton.toolTip())
        layout.addWidget(self.previewButton)
        
        self.editButton = QtGui.QToolButton()
        self.editButton.setIcon(CurrentTheme.QUERY_EDIT_ICON)
        self.editButton.setAutoRaise(True)
        self.editButton.setToolTip('Click to edit the query')
        self.editButton.setStatusTip(self.editButton.toolTip())
        layout.addWidget(self.editButton)

        layout.addStretch()

        if parent and hasattr(parent, 'iconSize'):
            iconSize = parent.iconSize()
            self.previewButton.setIconSize(iconSize)
            self.editButton.setIconSize(iconSize)

        self.connect(self.previewButton, QtCore.SIGNAL('clicked()'),
                     self.previewQuery)
        self.connect(self.editButton, QtCore.SIGNAL('clicked()'),
                     self.editQuery)

    def previewQuery(self):
        """ editQuery() -> None
        Preview the query in a popup menu
        
        """
        if type(self.queryData)==Pipeline:
            if self.previewButton.menu()==None:
                menu = QQueryPreviewMenu(self.queryData)
                self.previewButton.setMenu(menu)
            self.previewButton.showMenu()
        else:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(QtGui.QCursor.pos(),
                                    self.queryData)

    def editQuery(self):
        """ editQuery() -> None
        Bring the query to edit
        
        """    
        self.emit(QtCore.SIGNAL('editQueryRequest'), self.queryData)
