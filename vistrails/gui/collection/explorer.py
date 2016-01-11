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


from PyQt5 import QtCore, QtGui, QtWidgets


from vistrails.core import debug
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core.collection.search import SearchCompiler, SearchParseError
from vistrails.core.db.locator import FileLocator, DBLocator
from vistrails.core.system import default_connections_file
from vistrails.core.external_connection import ExtConnectionList
from vistrails.db import VistrailsDBException
from vistrails.db.services.io import test_db_connection
from vistrails.db.services.query import runLogQuery, runWorkflowQuery
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.open_db_window import QDBConnectionList, QConnectionDBSetupWindow
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
import vistrails.gui

class QExplorerWindow(QtWidgets.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.splitter)
        self.connectionList = QDBConnectionList(self)
        dbGrid = QtWidgets.QGridLayout(self)
        dbGrid.setContentsMargins(0, 0, 0, 0)
        dbGrid.setSpacing(0)
        dbGrid.addWidget(self.connectionList, 2, 1, QtCore.Qt.AlignLeft)
        self.addAct = QtWidgets.QAction("Add Database", self)
        self.removeAct = QtWidgets.QAction("Remove Database", self)
        self.addButton = QtWidgets.QToolButton()
        self.addButton.setToolTip("Create a new database connection")
        self.addButton.setDefaultAction(self.addAct)
        self.addButton.setAutoRaise(True)
        self.removeButton = QtWidgets.QToolButton()
        self.removeButton.setToolTip("Remove the selected connection from list")
        self.removeButton.setDefaultAction(self.removeAct)
        self.removeButton.setAutoRaise(True)
        self.removeButton.setEnabled(False)
        panelButtonsLayout = QtWidgets.QHBoxLayout()
        panelButtonsLayout.setContentsMargins(0, 0, 0, 0)
        panelButtonsLayout.setSpacing(0)
        panelButtonsLayout.addWidget(self.addButton)
        panelButtonsLayout.addWidget(self.removeButton)
        dbGrid.addLayout(panelButtonsLayout, 1, 1, QtCore.Qt.AlignLeft)
        dbWidget = QDBWidget(parent, self.connectionList)
        dbWidget.setLayout(dbGrid)
        self.splitter.addWidget(dbWidget)
        self.addAct.triggered.connect(self.showConnConfig)
        self.removeAct.triggered.connect(self.connectionList.removeConnection)
        self.connectionList.itemSelectionChanged.connect(self.updateEditButtons)
        self.connectionList.itemSelectionChanged.connect(self.checkConnection)
        self.tabView = QtWidgets.QTabWidget()
        self.tabView.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.tabView)
#        self.workflowSearch = WorkflowSearchWidget(self.connectionList)
#        self.tabView.addTab(self.workflowSearch, "Search for Workflows")
        self.executionSearch = ExecutionSearchWidget(self.connectionList)
        self.tabView.addTab(self.executionSearch, "Search for Workflow Executions")
        self.setLayout(self.layout)
        self.setWindowTitle('Provenance Browser')
        self.resize(QtCore.QSize(800, 600))
#        self.workflowSearch.setup_results()
        self.executionSearch.setup_results()

    def showConnConfig(self, *args, **keywords):
        return showConnConfig(self.connectionList, *args, **keywords)

    def updateEditButtons(self):
        """updateEditButtons() -> None
        It will enable/disable the connections buttons according to the
        selection

        """
        self.workflowSearch.setup_results()
        self.executionSearch.setup_results()
        id = self.connectionList.getCurrentItemId()
        if id != -1:
            self.removeButton.setEnabled(True)
        else:
            self.removeButton.setEnabled(False)

    def checkConnection(self):
        checkConnection(self.connectionList)

        
    def getConnectionInfo(self, id):
        return getConnectionInfo(self.connectionList, id)

def showConnConfig(connectionList, *args, **keywords):
    """showConnConfig(*args, **keywords) -> None
    shows a window to configure the connection. The valid keywords
    are defined in QConnectionDBSetupWindow.__init__()
    
    """
    dialog = QConnectionDBSetupWindow(**keywords)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        config = {'id': int(dialog.id),
                  'name': str(dialog.nameEdt.text()),
                  'host': str(dialog.hostEdt.text()),
                  'port': int(dialog.portEdt.value()),
                  'user': str(dialog.userEdt.text()),
                  'passwd': str(dialog.passwdEdt.text()),
                  'db': str(dialog.databaseEdt.text())}
        id = connectionList.setConnectionInfo(**config)
        connectionList.setCurrentId(id)
        return True
    else:
        return False

def getConnectionInfo(connectionList, id):
    """getConnectionInfo(connectionList: QDBConnectionList, id: int) -> dict
    Returns info of ExtConnection """
    conn = connectionList.get_connection(id)
    key = str(conn.id) + "." + conn.name + "." + conn.host
    passwd = DBLocator.keyChain.get_key(key)
    if conn is not None:
        config = {'id': conn.id,
                  'name': conn.name,
                  'host': conn.host,
                  'port': conn.port,
                  'user': conn.user,
                  'passwd': passwd,
                  'db': conn.database}
    else:
        config = None
    return config

def checkConnection(connectionList):
    """checkConnection() -> None
    It will try if the connection works or if a password is necessary

    """
    conn_id = connectionList.getCurrentItemId()
    if conn_id != -1:
        conn = connectionList.get_connection(conn_id)
        config = getConnectionInfo(connectionList, conn_id)
        if config is not None:
            config_name = config['name']
            config_id = config['id']
            try:
                test_db_connection(config)
            except VistrailsDBException:
                # assume connection is wrong
                config["create"] = False
                showConnConfig(connectionList, **config)
            else:
                del config['name']
                del config['id']

class QDBWidget(QtWidgets.QWidget):
    """ Custom widget for handling the showConnConfig """

    def __init__(self, parent, connectionList):
        QtWidgets.QWidget.__init__(self, parent)
        self.connectionList = connectionList

    def showConnConfig(self, *args, **keywords):
        return showConnConfig(self.connectionList, *args, **keywords)

class ExecutionSearchWidget(QtWidgets.QSplitter):
    def __init__(self, connectionList):
        QtWidgets.QSplitter.__init__(self)
        self.connectionList = connectionList
        self.conn = None
        self.config = None
        self.offset = 0
        self.limit = 50
        self.numRows = None
        self.vistrail = None
        self.version = None
        self.fromTime = None
        self.toTime = None
        self.user = None
        self.thumbs = None
        self.completed = None
        self.modules = []
        self.setOrientation(QtCore.Qt.Vertical)
        self.searchLayout = QtWidgets.QGridLayout()
        self.vistrailEditCheckBox = QtWidgets.QCheckBox()
        self.vistrailEditCheckBox.setToolTip('Check to enable this search option')
        self.vistrailEdit = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.vistrailEditCheckBox, 0,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('Vistrail:'), 0,1)
        self.searchLayout.addWidget(self.vistrailEdit,         0,2)
        self.versionEditCheckBox = QtWidgets.QCheckBox()
        self.versionEditCheckBox.setToolTip('Check to enable this search option')
        self.versionEdit = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.versionEditCheckBox, 0,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('Version:'), 0,4)
        self.searchLayout.addWidget(self.versionEdit,         0,5)
        self.fromTimeEditCheckBox = QtWidgets.QCheckBox()
        self.fromTimeEditCheckBox.setToolTip('Check to enable this search option')
        self.fromTimeEdit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime().addDays(-1))
        self.fromTimeEdit.setDisplayFormat('yyyy-MM-d H:mm:ss')
        self.fromTimeEdit.setCalendarPopup(True)
        self.searchLayout.addWidget(self.fromTimeEditCheckBox,  1,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('From time:'), 1,1)
        self.searchLayout.addWidget(self.fromTimeEdit,          1,2)
        self.toTimeEditCheckBox = QtWidgets.QCheckBox()
        self.toTimeEditCheckBox.setToolTip('Check to enable this search option')
        self.toTimeEdit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.toTimeEdit.setDisplayFormat('yyyy-MM-d H:mm:ss')
        self.toTimeEdit.setCalendarPopup(True)
        self.searchLayout.addWidget(self.toTimeEditCheckBox,  1,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('To time:'), 1,4)
        self.searchLayout.addWidget(self.toTimeEdit,          1,5)
        self.userEditCheckBox = QtWidgets.QCheckBox()
        self.userEditCheckBox.setToolTip('Check to enable this search option')
        self.userEdit = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.userEditCheckBox, 2,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('User:'), 2,1)
        self.searchLayout.addWidget(self.userEdit,         2,2)
        self.completedEditCheckBox = QtWidgets.QCheckBox()
        self.completedEditCheckBox.setToolTip('Check to enable this search option')
        self.completedEdit = QtWidgets.QComboBox()
        self.completedEdit.addItems(['Yes', 'No', 'Error'])
        self.searchLayout.addWidget(self.completedEditCheckBox, 2,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('Completed:'), 2,4)
        self.searchLayout.addWidget(self.completedEdit,         2,5)
        
        self.moduleEditCheckBox = QtWidgets.QCheckBox()
        self.moduleEditCheckBox.setToolTip('Check to enable this search option')
        self.moduleEdit = QtWidgets.QLineEdit()
        self.moduleEdit.setToolTip('Add module names separated by ,\nResult type can be specified by using: ModuleName:Yes/No/Error')
        self.searchLayout.addWidget(self.moduleEditCheckBox,  3,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('Modules:'), 3,1)
        self.searchLayout.addWidget(self.moduleEdit,          3,2)
        self.thumbsCheckBox = QtWidgets.QCheckBox()
        self.thumbsCheckBox.setToolTip('Check to view result thumbnails (may be slow)')
        self.searchLayout.addWidget(self.thumbsCheckBox,  3,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('View thumbs'), 3,4)
        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.setStatusTip("Search the database for executions")
        self.searchLayout.addWidget(self.searchButton, 3, 5)
        self.searchWidget = QtWidgets.QWidget()
        self.searchWidget.setLayout(self.searchLayout)
        self.addWidget(self.searchWidget)
        self.itemView = QtWidgets.QTreeWidget(self.parent())
        self.addWidget(self.itemView)
        statusGrid = QtWidgets.QGridLayout()
        statusGrid.setContentsMargins(0, 0, 0, 0)
        statusGrid.setSpacing(0)
        statusWidget = QtWidgets.QWidget()
        statusWidget.setLayout(statusGrid)
        self.addWidget(statusWidget)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setStretchFactor(2, 0)
        statusLayout = QtWidgets.QHBoxLayout()
        statusLayout.setSpacing(5)
        statusGrid.addLayout(statusLayout, 2, 1, QtCore.Qt.AlignLeft)
        
        self.prevButton = QtWidgets.QPushButton("Previous")
        self.prevButton.setStatusTip("Show previous results")
        self.prevButton.hide()
        statusLayout.addWidget(self.prevButton)

        self.nextButton = QtWidgets.QPushButton("Next")
        self.nextButton.setStatusTip("Show next results")
        self.nextButton.hide()
        statusLayout.addWidget(self.nextButton)

        self.statusText = QtWidgets.QLabel('No query specified')
        statusLayout.addWidget(self.statusText)
        self.searchButton.clicked.connect(self.newQuery)
        self.prevButton.clicked.connect(self.gotoPrevious)
        self.nextButton.clicked.connect(self.gotoNext)
        self.itemView.itemDoubleClicked[QTreeWidgetItem, int].connect(self.showItem)

    def newQuery(self):
        self.offset = 0
        self.vistrail = None
        if self.vistrailEditCheckBox.isChecked():
            self.vistrail = str(self.vistrailEdit.text()).strip()
        self.version = None
        if self.versionEditCheckBox.isChecked():
            self.version = str(self.versionEdit.text()).strip()
        self.fromTime = None
        if self.fromTimeEditCheckBox.isChecked():
            self.fromTime = str(
                self.fromTimeEdit.dateTime().toString('yyyy-MM-d H:mm:ss'))
        self.toTime = None
        if self.toTimeEditCheckBox.isChecked():
            self.toTime = str(
                self.toTimeEdit.dateTime().toString('yyyy-MM-d H:mm:ss'))
        self.user = None
        if self.userEditCheckBox.isChecked():
            self.user = str(self.userEdit.text()).strip()
        self.completed = None
        if self.completedEditCheckBox.isChecked():
            self.completed = str(self.completedEdit.currentText()).strip()
        self.modules = []
        if self.moduleEditCheckBox.isChecked():
            # create list of [moduleType, completed] pairs
            modules = str(self.moduleEdit.text()).strip()
            for k in [i.strip() for i in modules.split(',')]:
                v = k.split(':')
                if len(v)>1:
                    self.modules.append((v[0].strip(), v[1].strip()))
                else:
                    self.modules.append((v[0].strip(), None))
        self.thumbs = self.thumbsCheckBox.isChecked()
        conn_id = self.connectionList.getCurrentItemId()
        self.conn = self.connectionList.get_connection(conn_id)
        self.config = getConnectionInfo(self.connectionList, conn_id)
        
        self.searchDatabase()

    def searchDatabase(self):
        self.statusText.setText("Running query...")
        self.repaint()
        # create connection
        conn = self.conn
        config = self.config
        if conn.dbtype == 'MySQL':
            #removing extra keyword arguments for MySQldb
            config_name = config.pop('name')
            config_id = config.pop('id')
            
        wf_exec_list = runLogQuery(config,
                                vistrail=self.vistrail, version=self.version,
                                fromTime=self.fromTime, toTime=self.toTime,
                                user=self.user, completed=self.completed,
                                offset=self.offset, limit=self.limit,
                                modules=self.modules, thumbs=self.thumbs)
        if 0 == self.offset:
            wf_exec_list, self.numRows = wf_exec_list
        if conn.dbtype == 'MySQL':
            config['name'] = config_name
            config['id'] = config_id
        self.setup_results(wf_exec_list)
        self.updateStatus()

    def gotoPrevious(self):
        self.offset = max(self.offset - self.limit, 0)
        self.searchDatabase()

    def gotoNext(self):
        self.offset = min(self.offset + self.limit, self.numRows)
        self.searchDatabase()
        
    def updateStatus(self):
        if self.offset > 0:
            self.prevButton.show()
        else:
            self.prevButton.hide()
        last = self.offset + self.limit
        if last < self.numRows:
            self.nextButton.show()
        else:
            self.nextButton.hide()
            last = self.numRows
        if self.numRows:
            self.statusText.setText("Showing %s-%s out of %s results" %
                                    (self.offset+1, last, self.numRows))
        else:
            self.statusText.setText("No matching results found")

    def setup_results(self, wf_exec_list=[]):
        self.itemView.clear()
        self.itemView.setIconSize(QtCore.QSize(32,32))
        columns = ['Vistrail', 'Version', 'Start time', 'End time', 'Completed']
        self.itemView.setColumnCount(len(columns))
        self.itemView.setHeaderLabels(columns)
        self.itemView.setSortingEnabled(True)
        for wf_exec in wf_exec_list:
            item = QExecutionItem(wf_exec)
            self.itemView.addTopLevelItem(item)
        self.itemView.header().setResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.itemView.header().setResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.itemView.header().resizeSections(QtWidgets.QHeaderView.Stretch)
        conn_id = self.connectionList.getCurrentItemId()
        if conn_id < 0:
            self.statusText.setText("Select a database")
            
    def showItem(self, item, col):
        (v_name, v_id, log_id, v_version, version_name, e_id,
         ts_start, ts_end, user, completed, thumb) = item.wf_exec
        config = self.config
        locator = \
           DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     config['name'],
                     obj_id=v_id,
                     obj_type='vistrail',
                     workflow_exec=ts_start,
                     connection_id=config.get('id', None))
        #print "url:", locator.to_url()
        import vistrails.gui.application
        app = vistrails.gui.application.get_vistrails_application()
        open_vistrail = app.builderWindow.open_vistrail_without_prompt

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        args = {}
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
        args['version'] = version_name if version_name else v_version
        open_vistrail(locator, **args)

class QExecutionItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, wf_exec, parent=None):
        (v_name, v_id, log_id, v_version, version_name, e_id,
         ts_start, ts_end, user, completed, thumb) = wf_exec
        version = version_name if version_name else v_version
        completed = {'-1':'Error', '0':'No', '1':'Yes'}.get(str(completed), 'Unknown')
        labels = (str(v_name), str(version),
                  str(ts_start), str(ts_end), str(completed))
        QtWidgets.QTreeWidgetItem.__init__(self, labels)
        self.wf_exec = wf_exec
        self.setToolTip(0, 'vistrail:%s version:%s log:%s wf_exec:%s user:%s' %
                           (v_id, v_version, log_id, e_id, user))
        if thumb:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(thumb)
            self.setIcon(1, QtGui.QIcon(pixmap))
            tooltip = """<img border=0 src="data:image/png;base64,%s">""" % thumb.encode('base64')
            self.setToolTip(1, tooltip)
            
    def __lt__(self, other):
        sort_col = self.treeWidget().sortColumn()
        if sort_col in set([1]):
            try:
                return int(self.text(sort_col)) < int(other.text(sort_col))
            except ValueError:
                pass
        return QtWidgets.QTreeWidgetItem.__lt__(self, other)

class WorkflowSearchWidget(QtWidgets.QSplitter):
    def __init__(self, connectionList):
        QtWidgets.QSplitter.__init__(self)
        self.connectionList = connectionList
        self.conn = None
        self.config = None
        self.offset = 0
        self.limit = 50
        self.numRows = None
        self.vistrail = None
        self.version = None
        self.fromTime = None
        self.toTime = None
        self.user = None
        self.thumbs = None
        self.modules = []
        self.setOrientation(QtCore.Qt.Vertical)
        self.searchLayout = QtWidgets.QGridLayout()
        self.vistrailEditCheckBox = QtWidgets.QCheckBox()
        self.vistrailEditCheckBox.setToolTip('Check to enable this search option')
        self.vistrailEdit = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.vistrailEditCheckBox, 0,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('Vistrail:'), 0,1)
        self.searchLayout.addWidget(self.vistrailEdit,         0,2)
        self.versionEditCheckBox = QtWidgets.QCheckBox()
        self.versionEditCheckBox.setToolTip('Check to enable this search option')
        self.versionEdit = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.versionEditCheckBox, 0,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('Version:'), 0,4)
        self.searchLayout.addWidget(self.versionEdit,         0,5)
        self.fromTimeEditCheckBox = QtWidgets.QCheckBox()
        self.fromTimeEditCheckBox.setToolTip('Check to enable this search option')
        self.fromTimeEdit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime().addDays(-1))
        self.fromTimeEdit.setDisplayFormat('yyyy-MM-d H:mm:ss')
        self.fromTimeEdit.setCalendarPopup(True)
        self.searchLayout.addWidget(self.fromTimeEditCheckBox,  1,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('From time:'), 1,1)
        self.searchLayout.addWidget(self.fromTimeEdit,          1,2)
        self.toTimeEditCheckBox = QtWidgets.QCheckBox()
        self.toTimeEditCheckBox.setToolTip('Check to enable this search option')
        self.toTimeEdit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.toTimeEdit.setDisplayFormat('yyyy-MM-d H:mm:ss')
        self.toTimeEdit.setCalendarPopup(True)
        self.searchLayout.addWidget(self.toTimeEditCheckBox,  1,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('To time:'), 1,4)
        self.searchLayout.addWidget(self.toTimeEdit,          1,5)
        self.userEditCheckBox = QtWidgets.QCheckBox()
        self.userEditCheckBox.setToolTip('Check to enable this search option')
        self.userEdit = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.userEditCheckBox, 2,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('User:'), 2,1)
        self.searchLayout.addWidget(self.userEdit,         2,2)
      
        self.moduleEditCheckBox = QtWidgets.QCheckBox()
        self.moduleEditCheckBox.setToolTip('Check to enable this search option')
        self.moduleEdit = QtWidgets.QLineEdit()
        self.moduleEdit.setToolTip('Add module names separated by ,\nConnected modules can be specified by using: ModuleA->ModuleB')
        self.searchLayout.addWidget(self.moduleEditCheckBox,  3,0)
        self.searchLayout.addWidget(QtWidgets.QLabel('Modules:'), 3,1)
        self.searchLayout.addWidget(self.moduleEdit,          3,2)
        self.thumbsCheckBox = QtWidgets.QCheckBox()
        self.thumbsCheckBox.setToolTip('Check to view result thumbnails (may be slow)')
        self.searchLayout.addWidget(self.thumbsCheckBox,  3,3)
        self.searchLayout.addWidget(QtWidgets.QLabel('View thumbs'), 3,4)
        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.setStatusTip("Search the database for executions")
        self.searchLayout.addWidget(self.searchButton, 3, 5)
        self.searchWidget = QtWidgets.QWidget()
        self.searchWidget.setLayout(self.searchLayout)
        self.addWidget(self.searchWidget)
        self.itemView = QtWidgets.QTreeWidget(self.parent())
        self.addWidget(self.itemView)
        statusGrid = QtWidgets.QGridLayout()
        statusGrid.setContentsMargins(0, 0, 0, 0)
        statusGrid.setSpacing(0)
        statusWidget = QtWidgets.QWidget()
        statusWidget.setLayout(statusGrid)
        self.addWidget(statusWidget)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setStretchFactor(2, 0)
        statusLayout = QtWidgets.QHBoxLayout()
        statusLayout.setSpacing(5)
        statusGrid.addLayout(statusLayout, 2, 1, QtCore.Qt.AlignLeft)
        
        self.prevButton = QtWidgets.QPushButton("Previous")
        self.prevButton.setStatusTip("Show previous results")
        self.prevButton.hide()
        statusLayout.addWidget(self.prevButton)

        self.nextButton = QtWidgets.QPushButton("Next")
        self.nextButton.setStatusTip("Show next results")
        self.nextButton.hide()
        statusLayout.addWidget(self.nextButton)

        self.statusText = QtWidgets.QLabel('No query specified')
        statusLayout.addWidget(self.statusText)
        self.searchButton.clicked.connect(self.newQuery)
        self.prevButton.clicked.connect(self.gotoPrevious)
        self.nextButton.clicked.connect(self.gotoNext)
        self.itemView.itemDoubleClicked[QTreeWidgetItem, int].connect(self.showItem)

    def newQuery(self):
        self.offset = 0
        self.vistrail = None
        if self.vistrailEditCheckBox.isChecked():
            self.vistrail = str(self.vistrailEdit.text()).strip()
        self.version = None
        if self.versionEditCheckBox.isChecked():
            self.version = str(self.versionEdit.text()).strip()
        self.fromTime = None
        if self.fromTimeEditCheckBox.isChecked():
            self.fromTime = str(
                self.fromTimeEdit.dateTime().toString('yyyy-MM-d H:mm:ss'))
        self.toTime = None
        if self.toTimeEditCheckBox.isChecked():
            self.toTime = str(
                self.toTimeEdit.dateTime().toString('yyyy-MM-d H:mm:ss'))
        self.user = None
        if self.userEditCheckBox.isChecked():
            self.user = str(self.userEdit.text()).strip()
        self.modules = []
        if self.moduleEditCheckBox.isChecked():
            # create list of [moduleType, connected to previous] pairs
            groups = str(self.moduleEdit.text()).strip()
            groups = [i.strip() for i in groups.split(',')]
            for group in [i.split('->') for i in groups]:
                if len(group):
                    module = group.pop(0).strip()
                    if len(module):
                        self.modules.append((module, False))
                while len(group):
                    module = group.pop(0).strip()
                    if len(module):
                        self.modules.append((module, True))
        self.thumbs = self.thumbsCheckBox.isChecked()
        conn_id = self.connectionList.getCurrentItemId()
        self.conn = self.connectionList.get_connection(conn_id)
        self.config = getConnectionInfo(self.connectionList, conn_id)
        
        self.searchDatabase()

    def searchDatabase(self):
        self.statusText.setText("Running query...")
        self.repaint()
        # create connection
        conn = self.conn
        config = self.config
        if conn.dbtype == 'MySQL':
            #removing extra keyword arguments for MySQldb
            config_name = config.pop('name')
            config_id = config.pop('id')
            
        workflow_list = runWorkflowQuery(config,
                                vistrail=self.vistrail, version=self.version,
                                fromTime=self.fromTime, toTime=self.toTime,
                                user=self.user,
                                offset=self.offset, limit=self.limit,
                                modules=self.modules,
                                thumbs=self.thumbs)
        if 0 == self.offset:
            workflow_list, self.numRows = workflow_list
        if conn.dbtype == 'MySQL':
            config['name'] = config_name
            config['id'] = config_id
        self.setup_results(workflow_list)
        self.updateStatus()

    def gotoPrevious(self):
        self.offset = max(self.offset - self.limit, 0)
        self.searchDatabase()

    def gotoNext(self):
        self.offset = min(self.offset + self.limit, self.numRows)
        self.searchDatabase()
        
    def updateStatus(self):
        if self.offset > 0:
            self.prevButton.show()
        else:
            self.prevButton.hide()
        last = self.offset + self.limit
        if last < self.numRows:
            self.nextButton.show()
        else:
            self.nextButton.hide()
            last = self.numRows
        if self.numRows:
            self.statusText.setText("Showing %s-%s out of %s results" %
                                    (self.offset+1, last, self.numRows))
        else:
            self.statusText.setText("No matching results found")

    def setup_results(self, workflow_list=[]):
        self.itemView.clear()
        self.itemView.setIconSize(QtCore.QSize(32,32))
        columns = ['Vistrail', 'Version', 'Time', 'User']
        self.itemView.setColumnCount(len(columns))
        self.itemView.setHeaderLabels(columns)
        self.itemView.setSortingEnabled(True)
        for workflow in workflow_list:
            item = QWorkflowItem(workflow)
            self.itemView.addTopLevelItem(item)
        self.itemView.header().setResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.itemView.header().setResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.itemView.header().resizeSections(QtWidgets.QHeaderView.Stretch)
        conn_id = self.connectionList.getCurrentItemId()
        if conn_id < 0:
            self.statusText.setText("Select a database")

    def showItem(self, item, col):
        (v_name, v_id, v_version, version_name, time, user, thumb) = \
         item.workflow
        config = self.config
        locator = \
           DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     config['name'],
                     obj_id=v_id,
                     obj_type='vistrail',
                     connection_id=config.get('id', None))
        #print "url:", locator.to_url()
        import vistrails.gui.application
        app = vistrails.gui.application.get_vistrails_application()
        open_vistrail = app.builderWindow.open_vistrail_without_prompt
        args = {}
        args['version'] = version_name if version_name else v_version
        #print "args", args
        open_vistrail(locator, **args)

class QWorkflowItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, workflow, parent=None):
        (v_name, v_id, v_version, version_name, time, user, thumb) = workflow
        version = version_name if version_name else v_version
        labels = (str(v_name), str(version), str(time), str(user))
        QtWidgets.QTreeWidgetItem.__init__(self, labels)
        self.workflow = workflow
        self.setToolTip(0, 'vistrail:%s version:%s' % (v_id, v_version))
        if thumb:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(thumb)
            self.setIcon(1, QtGui.QIcon(pixmap))
            tooltip = """<img border=0 src="data:image/png;base64,%s">""" % thumb.encode('base64')
            self.setToolTip(1, tooltip)
            
    def __lt__(self, other):
        sort_col = self.treeWidget().sortColumn()
        if sort_col in set([1]):
            try:
                return int(self.text(sort_col)) < int(other.text(sort_col))
            except ValueError:
                pass
        return QtWidgets.QTreeWidgetItem.__lt__(self, other)
