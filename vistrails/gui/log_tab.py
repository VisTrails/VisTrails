from PyQt4 import QtCore, QtGui, QtOpenGL
from qframebox import *
from qmodulefunctiongroupbox import *
from qgroupboxscrollarea import *
from qbuildertreewidget import *
import vis_application

class LogTab(QtGui.QWidget):
    def __init__(self, builder, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.builder = builder
        self.logger = vis_application.logger
        self.vistrail_id = -1
        self.module_id = -1
        self.buildLogTab()

    def buildLogTab(self):
        """Builds the module annotation frame and table."""
                       
        table = LogTable(self)
        labels = QtCore.QStringList()
        labels << self.tr("start") << self.tr("duration") << self.tr("user")
        table.setHorizontalHeaderLabels(labels)
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        table.horizontalHeader().setMovable(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        table.verticalHeader().hide()
        self.logTable = table
        
        self.connect(self.logTable,QtCore.SIGNAL("logDetailsRequested"),self.showDetails)
        self.connect(self.builder, QtCore.SIGNAL("hasLogExecution"), self.set_entry)
        self.connect(self.builder, QtCore.SIGNAL("hideLog"), self.hideInfo)
        self.detailsTable = DetailsTable()
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.addWidget(table)
        layout.addWidget(self.detailsTable)
        self.setLayout(layout)
        self.detailsTable.setVisible(False)
        self.logTable.setVisible(False)
        
    def set_entry(self, vistrail_id, module_id):
        if self.vistrail_id != vistrail_id or self.module_id != module_id:
            self.logTable.resetTable()
            controller = self.builder.controllers[self.builder.currentControllerName]
            exec_ids = controller.versionTree.search.executionInstances(vistrail_id, module_id)
            if exec_ids:
                for exec_id in exec_ids:
                    info = self.logger.getExecIdInfo(exec_id)
                    self.logTable.addEntry(exec_id, info['ts_start'], info['duration'], info['user'])
                self.detailsTable.setVisible(False)
                self.logTable.setVisible(True)
            else:
                self.detailsTable.setVisible(False)
                self.logTable.setVisible(False)
            self.vistrail_id = vistrail_id
            self.module_id = module_id

    def showDetails(self, exec_id):
        info = self.logger.getExecIdDetails(exec_id)
        self.detailsTable.addEntry(info['machine'], info['os'], info['architecture'], info['processor'],
                                   info['ram'], info['ip'], info['vis_version'])
        self.detailsTable.setVisible(True)
    
    def hideInfo(self):
        self.detailsTable.setVisible(False)
        self.logTable.setVisible(False)

class LogTable(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self,1,3)
        self.logTab = parent

    def resetTable(self):
        self.setRowCount(0)
        
    def addEntry(self, exec_id, ts_start, duration, user):
        row = self.rowCount()
        self.insertRow(row)
        item = LogItem(ts_start, exec_id)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.setItem(row, 0, item )
        item = LogItem(duration, exec_id)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.setItem(row, 1, item)
        item = LogItem(user, exec_id)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.setItem(row, 2, item)
    
    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            item = None
            item = self.itemAt(event.x(),event.y())
            if not item:
                if len(self.selectedItems()):
                    item = self.selectedItems()[0]
            if item:
                exec_id = item.exec_id
                self.emit(QtCore.SIGNAL("logDetailsRequested"), exec_id)
            else:
                self.logTab.detailsTable.setVisible(False)

            QtGui.QTableWidget.mousePressEvent(self,event)

class LogItem(QtGui.QTableWidgetItem):
    def __init__(self, text, exec_id):
        QtGui.QTableWidgetItem.__init__(self,str(text))
        self.exec_id = exec_id

class DetailsTable(QtGui.QTableWidget):
    def __init__(self):
        QtGui.QTableWidget.__init__(self,7,1)
        labels = QtCore.QStringList()
        labels << self.tr("Machine") << self.tr("OS") << self.tr("Architecture") << self.tr("Processor") << self.tr("RAM") << self.tr("IP") << self.tr("VisTrails Version")
        self.setVerticalHeaderLabels(labels)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        self.verticalHeader().setMovable(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        labels << self.tr("") << self.tr("Details") 
        self.setHorizontalHeaderLabels(labels)
    
    def resetTable():
        self.setItem(0, 0, QtGui.QTableWidgetItem('') )
        self.setItem(1, 0, QtGui.QTableWidgetItem('') )
        self.setItem(2, 0, QtGui.QTableWidgetItem('') )
        self.setItem(3, 0, QtGui.QTableWidgetItem('') )
        self.setItem(4, 0, QtGui.QTableWidgetItem('') )
        self.setItem(5, 0, QtGui.QTableWidgetItem('') )
        self.setItem(6, 0, QtGui.QTableWidgetItem('') )

    def addEntry(self, machine, oSystem, architecture, processor, ram, ip, vis_version ):
        item = QtGui.QTableWidgetItem(machine)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(0, 0, item )

        item = QtGui.QTableWidgetItem(oSystem)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(1, 0, item )

        item = QtGui.QTableWidgetItem(str(architecture) + ' bits')
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(2, 0, item )

        item = QtGui.QTableWidgetItem(processor)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(3, 0, item )

        item = QtGui.QTableWidgetItem(str(ram) + ' MB')
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(4, 0, item )

        item = QtGui.QTableWidgetItem(ip)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(5, 0, item )

        item = QtGui.QTableWidgetItem(vis_version)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(6, 0, item )

