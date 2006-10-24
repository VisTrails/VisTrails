from PyQt4 import QtCore, QtGui, QtOpenGL
from qframebox import *
from qmodulefunctiongroupbox import *
from qgroupboxscrollarea import *
from qbuildertreewidget import *

class ModuleAnnotations(object):
    def __init__(self, builder):
        self.builder = builder
        self.buildModuleAnnotations()
    def buildModuleAnnotations(_self):
        """Builds the module annotation frame and table."""
        self = _self.builder        
        table = KeyValueTable(_self.builder)
        labels = QtCore.QStringList()
        labels << self.tr("Key") << self.tr("Value")
        table.setHorizontalHeaderLabels(labels)
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        table.horizontalHeader().setMovable(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.verticalHeader().hide()
        self.delegate = KeyValueDelegate(table)
        table.setItemDelegate(self.delegate)
        self.moduleAnnotations = table

class KeyValueTable(QtGui.QTableWidget):
    def __init__(self, builder):
        self.builder = builder
        QtGui.QTableWidget.__init__(self,1,2)

    def resetTable(self):
        self.setRowCount(0)
        if self.builder.pipeline and self.builder.selectedModule!=-1:
            annotations = self.builder.pipeline.getModuleById(self.builder.selectedModule).annotations
            self.setRowCount(len(annotations)+1)
            curRow = 0
            for key,value in annotations.iteritems():
                self.setItem(curRow, 0, QtGui.QTableWidgetItem(key))
                self.setItem(curRow, 1, QtGui.QTableWidgetItem(value))
                curRow += 1
            self.setEnabled(True)
        else:
            self.setRowCount(1)
            self.setEnabled(False)
        self.setItem(self.rowCount()-1, 0, QtGui.QTableWidgetItem(''))
        self.setItem(self.rowCount()-1, 1, QtGui.QTableWidgetItem(''))

class KeyValueDelegate(QtGui.QItemDelegate):

    def __init__(self, table):
        self.table = table
        QtGui.QItemDelegate.__init__(self, None)
    
    def setEditorData(self, editor, index):
        text = index.model().data(index, QtCore.Qt.DisplayRole).toString()
        editor.setText(text)

    def setModelData(self, editor, model, index):
        text = str(editor.text())
        row = index.row()
        col = index.column()
        key = str(self.table.item(row, 0).text())
        value = str(self.table.item(row, 1).text())
        builder = self.table.builder
        moduleId = builder.selectedModule
    
        annotations = builder.pipeline.getModuleById(moduleId).annotations
        controller = builder.controllers[builder.currentControllerName]
        
        if col==0:
            if not text and row<self.table.rowCount()-1:
                self.table.removeRow(row)
                controller.deleteAnnotation(key, moduleId)
            if text and text!=key and annotations.has_key(text):
                QtGui.QMessageBox.information(None,
                                              "VisTrails",
                                              QtCore.QString("'%1' already exists in the annotations.").arg(text))
                return

        if col==1 and not key:
            QtGui.QMessageBox.information(None,
                                          "VisTrails",
                                          "Must provide a key first.")
            return
            
            
        if (row==self.table.rowCount()-1) and text:
            self.table.insertRow(row+1)
            self.table.setItem(self.table.rowCount()-1, 0, QtGui.QTableWidgetItem(''))
            self.table.setItem(self.table.rowCount()-1, 1, QtGui.QTableWidgetItem(''))
                    
        if col==1:
            if text!=value:
                controller.addAnnotation((key, text), moduleId)
        elif text:
            if key!=text and key:
                controller.deleteAnnotation(key, moduleId)
            controller.addAnnotation((text, value), moduleId)
        
        model.setData(index, QtCore.QVariant(text))

