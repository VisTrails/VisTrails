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

from PyQt4 import QtCore, QtGui

import os
from datetime import datetime
from time import strptime
from core import debug
from core.thumbnails import ThumbnailCache
from core.collection import Collection
from core.collection.search import SearchCompiler, SearchParseError
from core.db.locator import FileLocator, DBLocator
from core.system import default_connections_file
from core.external_connection import ExtConnectionList
from db import VistrailsDBException
from db.services.io import test_db_connection
from db.services.query import retrieve
from gui.common_widgets import QToolWindowInterface, QToolWindow, QSearchBox
from gui.theme import CurrentTheme
from gui.open_db_window import QDBConnectionList, QConnectionDBSetupWindow

class QExplorerWindow(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        
        self.conn = None
        self.config = None
        self.offset = 0
        self.limit = 100
        self.numRows = None
        self.vistrail = None
        self.version = None
        self.fromTime = None
        self.toTime = None
        self.user = None
        self.completed = None
        self.modules = []
        self.layout = QtGui.QVBoxLayout()

        self.splitter = QExplorerSplitter(self)
        self.layout.addWidget(self.splitter)
        self.connectionList = QDBConnectionList(self)
        dbGrid = QtGui.QGridLayout()
        dbGrid.setMargin(0)
        dbGrid.setSpacing(0)
        dbGrid.addWidget(self.connectionList, 1, 1, QtCore.Qt.AlignLeft)
        self.addAct = QtGui.QAction("+", self)
        self.addAct.setStatusTip("Create a new connection")
        self.removeAct = QtGui.QAction("-", self)
        self.removeAct.setStatusTip("Remove the selected connection from list")
        self.addButton = QtGui.QToolButton()
        self.addButton.setDefaultAction(self.addAct)
        self.addButton.setAutoRaise(True)
        self.removeButton = QtGui.QToolButton()
        self.removeButton.setDefaultAction(self.removeAct)
        self.removeButton.setAutoRaise(True)
        self.removeButton.setEnabled(False)
        panelButtonsLayout = QtGui.QHBoxLayout()
        panelButtonsLayout.setMargin(0)
        panelButtonsLayout.setSpacing(0)
        panelButtonsLayout.addWidget(self.addButton)
        panelButtonsLayout.addWidget(self.removeButton)
        dbGrid.addLayout(panelButtonsLayout, 2, 1, QtCore.Qt.AlignLeft)
        dbWidget = QtGui.QWidget()
        dbWidget.setLayout(dbGrid)
        self.splitter.addWidget(dbWidget)

        self.vSplitter = QExplorerSplitter(self)
        self.vSplitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.vSplitter)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

        self.searchButton = QtGui.QPushButton("Search")
        self.searchButton.setStatusTip("Search the database for executions")

        self.searchLayout = QtGui.QGridLayout()
        self.vistrailEditCheckBox = QtGui.QCheckBox()
        self.vistrailEditCheckBox.setToolTip('Check to enable this search option')
        self.vistrailEdit = QtGui.QLineEdit()
        self.searchLayout.addWidget(self.vistrailEditCheckBox, 0,0)
        self.searchLayout.addWidget(QtGui.QLabel('Vistrail:'), 0,1)
        self.searchLayout.addWidget(self.vistrailEdit,         0,2)
        self.versionEditCheckBox = QtGui.QCheckBox()
        self.versionEditCheckBox.setToolTip('Check to enable this search option')
        self.versionEdit = QtGui.QLineEdit()
        self.searchLayout.addWidget(self.versionEditCheckBox, 0,3)
        self.searchLayout.addWidget(QtGui.QLabel('Version:'), 0,4)
        self.searchLayout.addWidget(self.versionEdit,         0,5)
        self.fromTimeEditCheckBox = QtGui.QCheckBox()
        self.fromTimeEditCheckBox.setToolTip('Check to enable this search option')
        self.fromTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime().addDays(-1))
        self.fromTimeEdit.setDisplayFormat('yyyy-MM-d H:mm:ss')
        self.fromTimeEdit.setCalendarPopup(True)
        self.searchLayout.addWidget(self.fromTimeEditCheckBox,  1,0)
        self.searchLayout.addWidget(QtGui.QLabel('From time:'), 1,1)
        self.searchLayout.addWidget(self.fromTimeEdit,          1,2)
        self.toTimeEditCheckBox = QtGui.QCheckBox()
        self.toTimeEditCheckBox.setToolTip('Check to enable this search option')
        self.toTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.toTimeEdit.setDisplayFormat('yyyy-MM-d H:mm:ss')
        self.toTimeEdit.setCalendarPopup(True)
        self.searchLayout.addWidget(self.toTimeEditCheckBox,  1,3)
        self.searchLayout.addWidget(QtGui.QLabel('To time:'), 1,4)
        self.searchLayout.addWidget(self.toTimeEdit,          1,5)
        self.userEditCheckBox = QtGui.QCheckBox()
        self.userEditCheckBox.setToolTip('Check to enable this search option')
        self.userEdit = QtGui.QLineEdit()
        self.searchLayout.addWidget(self.userEditCheckBox, 2,0)
        self.searchLayout.addWidget(QtGui.QLabel('User:'), 2,1)
        self.searchLayout.addWidget(self.userEdit,         2,2)
        self.completedEditCheckBox = QtGui.QCheckBox()
        self.completedEditCheckBox.setToolTip('Check to enable this search option')
        self.completedEdit = QtGui.QComboBox()
        self.completedEdit.addItems(['Yes', 'No', 'Error'])
        self.searchLayout.addWidget(self.completedEditCheckBox, 2,3)
        self.searchLayout.addWidget(QtGui.QLabel('Completed:'), 2,4)
        self.searchLayout.addWidget(self.completedEdit,         2,5)
        
        self.searchLayout.addWidget(self.searchButton, 3, 1)
        self.moduleEditCheckBox = QtGui.QCheckBox()
        self.moduleEditCheckBox.setToolTip('Check to enable this search option')
        self.moduleEdit = QtGui.QLineEdit()
        self.moduleEdit.setToolTip('Add module names separated by ,\nResult type can be specified by using: ModuleName:Yes/No/Error')
        self.searchLayout.addWidget(self.moduleEditCheckBox,  3,3)
        self.searchLayout.addWidget(QtGui.QLabel('Modules:'), 3,4)
        self.searchLayout.addWidget(self.moduleEdit,          3,5)
        self.searchWidget = QtGui.QWidget()
        self.searchWidget.setLayout(self.searchLayout)
        self.vSplitter.addWidget(self.searchWidget)
        self.itemView = QtGui.QTreeWidget(parent)
        self.vSplitter.addWidget(self.itemView)
        statusGrid = QtGui.QGridLayout()
        statusGrid.setMargin(0)
        statusGrid.setSpacing(0)
        statusWidget = QtGui.QWidget()
        statusWidget.setLayout(statusGrid)
        self.vSplitter.addWidget(statusWidget)
        self.vSplitter.setStretchFactor(0, 0)
        self.vSplitter.setStretchFactor(1, 1)
        self.vSplitter.setStretchFactor(2, 0)
        statusLayout = QtGui.QHBoxLayout()
        statusLayout.setSpacing(5)
        statusGrid.addLayout(statusLayout, 2, 1, QtCore.Qt.AlignLeft)
        
        self.prevButton = QtGui.QPushButton("Previous")
        self.prevButton.setStatusTip("Show previous results")
        self.prevButton.hide()
        statusLayout.addWidget(self.prevButton)

        self.nextButton = QtGui.QPushButton("Next")
        self.nextButton.setStatusTip("Show next results")
        self.nextButton.hide()
        statusLayout.addWidget(self.nextButton)

        self.statusText = QtGui.QLabel('No query specified')
        statusLayout.addWidget(self.statusText)
 
        self.connect(self.addAct,
                     QtCore.SIGNAL('triggered()'),
                     self.showConnConfig)
        self.connect(self.removeAct,
                     QtCore.SIGNAL('triggered()'),
                     self.connectionList.removeConnection)
        self.connect(self.connectionList,
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateEditButtons)
        self.connect(self.connectionList,
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.checkConnection)
        self.connect(self.searchButton,
                     QtCore.SIGNAL('clicked()'),
                     self.newQuery)
        self.connect(self.prevButton,
                     QtCore.SIGNAL('clicked()'),
                     self.gotoPrevious)
        self.connect(self.nextButton,
                     QtCore.SIGNAL('clicked()'),
                     self.gotoNext)
        self.connect(self.itemView,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *,int)'),
                     self.showItem)

        self.setLayout(self.layout)
        self.setWindowTitle('Workflow Execution Explorer')
        self.resize(QtCore.QSize(800, 600))
        self.setup_results()
        
    def showConnConfig(self, *args, **keywords):
        """showConnConfig(*args, **keywords) -> None
        shows a window to configure the connection. The valid keywords
        are defined in QConnectionDBSetupWindow.__init__()
        
        """
        keywords["parent"] = self
        
        dialog = QConnectionDBSetupWindow(**keywords)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            config = {'id': int(dialog.id),
                      'name': str(dialog.nameEdt.text()),
                      'host': str(dialog.hostEdt.text()),
                      'port': int(dialog.portEdt.value()),
                      'user': str(dialog.userEdt.text()),
                      'passwd': str(dialog.passwdEdt.text()),
                      'db': str(dialog.databaseEdt.text())}
            id = self.connectionList.setConnectionInfo(**config)
            self.connectionList.setCurrentId(id)
            return True
        else:
            return False

    def updateEditButtons(self):
        """updateEditButtons() -> None
        It will enable/disable the connections buttons according to the
        selection

        """
        self.setup_results()
        id = self.connectionList.getCurrentItemId()
        if id != -1:
            self.removeButton.setEnabled(True)
        else:
            self.removeButton.setEnabled(False)

    def checkConnection(self):
        """checkConnection() -> None
        It will try if the connection works or if a password is necessary

        """
        conn_id = self.connectionList.getCurrentItemId()
        if conn_id != -1:
            conn = self.connectionList.get_connection(conn_id)
            config = self.getConnectionInfo(conn_id)
            if config != None:
                try:
                    config_name = config['name']
                    del config['name']
                    config_id = config['id']
                    del config['id']
                    test_db_connection(config)
                except VistrailsDBException:
                    # assume connection is wrong
                    config['name'] = config_name
                    config['id'] = config_id
                    config["create"] = False
                    self.showConnConfig(**config)

        
    def getConnectionInfo(self, id):
        """getConnectionInfo(id: int) -> dict
        Returns info of ExtConnection """
        conn = self.connectionList.get_connection(id)
        key = str(conn.id) + "." + conn.name + "." + conn.host
        passwd = DBLocator.keyChain.get_key(key)
        if conn != None:
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
            print "Modules:", self.modules

        conn_id = self.connectionList.getCurrentItemId()
        self.conn = self.connectionList.get_connection(conn_id)
        self.config = self.getConnectionInfo(conn_id)
        
        self.searchDatabase()

    
    def searchDatabase(self):
        self.statusText.setText("Running query...")
        self.repaint()
        # create connection
        conn = self.conn
        config = self.config
        if conn.dbtype == 'MySQL':
            #removing extra keyword arguments for MySQldb
            config_name = config['name']
            del config['name']
            config_id = config['id']
            del config['id']
            
        wf_exec_list = retrieve(config,
                                vistrail=self.vistrail, version=self.version,
                                fromTime=self.fromTime, toTime=self.toTime,
                                user=self.user, completed=self.completed,
                                offset=self.offset, limit=self.limit,
                                modules=self.modules )
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
        columns = ['Vistrail', 'Version', 'Start time', 'End time', 'Completed']
        self.itemView.setColumnCount(len(columns))
        self.itemView.setHeaderLabels(columns)
        self.itemView.setSortingEnabled(True)
        for wf_exec in wf_exec_list:
            item = QExplorerWidgetItem(wf_exec)
            self.itemView.addTopLevelItem(item)
        self.itemView.header().setResizeMode(4, QtGui.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.itemView.header().setResizeMode(1, QtGui.QHeaderView.Interactive)
        self.itemView.header().setResizeMode(0, QtGui.QHeaderView.Interactive)
        self.itemView.header().resizeSections(QtGui.QHeaderView.Stretch)

    def showItem(self, item, col):
        print "showing", item.wf_exec
        (v_name, v_id, log_id, v_version, version_name, e_id,
         ts_start, ts_end, user, completed) = item.wf_exec
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
        print "url:", locator.to_url()
        import gui.application
        app = gui.application.VistrailsApplication
        open_vistrail = app.builderWindow.open_vistrail_without_prompt

        workflow_exec = locator.kwargs.get('workflow_exec', None)
        args = {}
        if workflow_exec:
            args['workflow_exec'] = workflow_exec
        args['version'] = locator.kwargs.get('version_node', None) or \
                          locator.kwargs.get('version_tag', None)
        open_vistrail(locator, **args)


class QExplorerWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, wf_exec, parent=None):
        (v_name, v_id, log_id, v_version, version_name, e_id,
         ts_start, ts_end, user, completed) = wf_exec
        version = version_name if version_name else v_version
        completed = {'-1':'Error', '0':'No', '1':'Yes'}.get(str(completed), 'Unknown')
        labels = (str(v_name), str(version),
                  str(ts_start), str(ts_end), str(completed))
        QtGui.QTreeWidgetItem.__init__(self, labels)
        self.wf_exec = wf_exec
        self.setToolTip(0, 'vistrail:%s version:%s log:%s wf_exec:%s user:%s' %
                           (v_id, v_version, log_id, e_id, user))

    def __lt__(self, other):
        sort_col = self.treeWidget().sortColumn()
        if sort_col in set([1]):
            try:
                return int(self.text(sort_col)) < int(other.text(sort_col))
            except ValueError:
                pass
        return QtGui.QTreeWidgetItem.__lt__(self, other)
    
class QExplorerSplitter(QtGui.QSplitter):
    """ Custom splitter for propagating the showConnConfig to the correct parent """
    def __init__(self, parent):
        QtGui.QSplitter.__init__(self, parent)

    def showConnConfig(self, *args, **keywords):
        parent = self.parent()
        if hasattr(parent, "showConnConfig"):
            parent.showConnConfig(*args, **keywords)
