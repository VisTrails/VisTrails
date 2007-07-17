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
""" This file contains widgets related to the module annotation
displaying a list of all pairs (key,value) for a module

QKeyValueDelegate
QModuleAnnotation
"""

from PyQt4 import QtCore, QtGui
from gui.common_widgets import QToolWindowInterface
from core.modules.module_registry import registry

################################################################################

class QModuleAnnotation(QtGui.QTableWidget, QToolWindowInterface):
    """
    QModuleAnnotation is a table widget that can be dock inside a
    window. It has two columns for key and value pairs to view/edit at
    run-time
    
    """    
    def __init__(self, parent=None):
        """ QModuleAnnotation(parent: QWidget) -> QModuleAnnotation
        Construct the 1x2 table
        
        """
        QtGui.QTableWidget.__init__(self, 1, 2, parent)
        self.setWindowTitle('Annotations')
        self.setHorizontalHeaderLabels(QtCore.QStringList() << 'Key' << 'Value')
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        self.horizontalHeader().setMovable(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.verticalHeader().hide()
        self.delegate = QKeyValueDelegate(self)
        self.setItemDelegate(self.delegate)
        self.module = None
        self.controller = None
        self.updateLocked = False

    def updateModule(self, module):
        """ updateModule(module: Module) -> None
        Update the widget to view the module annotations
        
        """
        self.setSortingEnabled(False)
        self.module = module
        if self.updateLocked: return
        self.clear()
        self.setRowCount(0)
        if module:
            self.setRowCount(len(module.annotations)+1)
            curRow = 0
            for (key, value) in module.annotations.items():
                self.setItem(curRow, 0, QtGui.QTableWidgetItem(key))
                item = QtGui.QTableWidgetItem(value)
                self.setItem(curRow, 1, item)
                curRow += 1
            self.setEnabled(True)
        else:
            self.setRowCount(1)
            self.setEnabled(False)
        self.setItem(self.rowCount()-1, 0, QtGui.QTableWidgetItem(''))
        self.setItem(self.rowCount()-1, 1, QtGui.QTableWidgetItem(''))
        self.setSortingEnabled(True)

    def makeItemBold(self, index):
        """ makeItemBold(index: QModelIndex) -> None
        Make the item at index to have a bold face
        
        """
        oldFont = QtGui.QFont(self.model().data(index, QtCore.Qt.FontRole))
        oldFont.setBold(True)
        oldFont.setPointSize(20)
        self.model().setData(index, QtCore.QVariant(oldFont),
                             QtCore.Qt.FontRole)

    def lockUpdate(self):
        """ lockUpdate() -> None
        Do not allow updateModule()
        
        """
        self.updateLocked = True
        
    def unlockUpdate(self):
        """ unlockUpdate() -> None
        Allow updateModule()
        
        """
        self.updateLocked = False

    def addRow(self):
        """ addRow() -> None
        Adds a new empty row to the table

        """
        self.setSortingEnabled(False)
        self.resizeRowsToContents()
        self.insertRow(self.rowCount())
        self.setItem(self.rowCount()-1, 0,
                     QtGui.QTableWidgetItem(''))
        self.setItem(self.rowCount()-1, 1,
                     QtGui.QTableWidgetItem(''))
        self.setSortingEnabled(False)

class QKeyValueDelegate(QtGui.QItemDelegate):
    """    
    QKeyValueDelegate tries to create a special control widget
    providing a simple interface for adding/deleting module
    annotations
    
    """

    def __init__(self, table):
        """ QKeyValueDelegate(table: QModuleAnnotation) -> QKeyValueDelegate
        Save a reference to table and perform a default initialization
        
        """
        self.table = table
        QtGui.QItemDelegate.__init__(self, None)
    
    def setEditorData(self, editor, index):
        """ setEditorData(editor: QWidget, index: QModelIndex) -> None
        Set the current item (at index) data into editor for editting
        
        """
        text = index.data(QtCore.Qt.DisplayRole).toString()
        editor.setText(text)

    def setModelData(self, editor, model, index):
        """ setModelData(editor: QWidget, model: QAbstractItemModel,
                         index: QModelIndex) -> None                         
        Assign the value of the editor back into the model and emit a
        signal to update vistrail
        
        """
        text = str(editor.text())
        row = index.row()
        col = index.column()
        keyItem = self.table.item(row, 0)
        if keyItem:
            key = str(keyItem.text())
        else:
            key = ''
            
        valueItem = self.table.item(row, 1)
        if valueItem:
            value = str(valueItem.text())
        else:
            value = ''
            
        if col==0:
            if text=='' and row<self.table.rowCount()-1:
                self.table.removeRow(row)
                if self.table.controller and self.table.module:
                    self.table.lockUpdate()
                    self.table.controller.previousModuleIds = [self.table.module.id]
                    self.table.controller.deleteAnnotation(key,
                                                           self.table.module.id)
                    self.table.unlockUpdate()
                return
            if text!='' and text!=key:
                if (self.table.module and
                    self.table.module.annotations.has_key(text)):
                    QtGui.QMessageBox.information(None,
                                                  "VisTrails",
                                                  text + ' already exists in '
                                                  'the annotations.')
                    return

        if col==1 and key=='':
            QtGui.QMessageBox.information(None,
                                          "VisTrails",
                                          "Must provide a key first.")
            return
            
            
        if col==0 and key=='' and text!='' and value!='':
            self.table.addRow()
                    
        if col==1:
            if text!=value:
                if self.table.controller and self.table.module:
                    self.table.lockUpdate()
                    self.table.controller.previousModuleIds = [self.table.module.id]
                    self.table.controller.addAnnotation((key, text),
                                                        self.table.module.id)
                    self.table.unlockUpdate()
            if row == self.table.rowCount()-1:
                self.table.addRow()
            
        elif text!='' and self.table.controller and self.table.module:
            moduleId = self.table.module.id
            self.table.lockUpdate()
            self.table.controller.previousModuleIds = [moduleId]
            if key!=text and key!='':
                self.table.controller.deleteAnnotation(key, moduleId)
            self.table.controller.addAnnotation((text, value),
                                                moduleId)
            self.table.unlockUpdate()
        
        model.setData(index, QtCore.QVariant(text))        
