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
""" This file contains a dialog and widgets related to the module annotation
displaying a list of all pairs (key,value) for a module

QKeyValueDelegate
QModuleAnnotation
QModuleAnnotationTable
"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core import debug

################################################################################

class QModuleAnnotation(QtGui.QDialog):
    """
    QModuleAnnotation is a dialog for annotating modules

    """
    def __init__(self, module, controller, parent=None):
        """ 
        QModuleAnnotation(module: Module, controller: VistrailController)
        -> None

        """
        QtGui.QDialog.__init__(self, parent)
        self.module = module
        self.controller = controller
        self.setModal(True)
        self.setWindowTitle('Module Annotations')
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.scrollArea = QtGui.QScrollArea(self)
        self.layout().addWidget(self.scrollArea)
        self.scrollArea.setFrameStyle(QtGui.QFrame.NoFrame)
        self.annotationTable = QModuleAnnotationTable(self.module,
                                                      self.controller,
                                                      self)
        self.scrollArea.setWidget(self.annotationTable)
        self.scrollArea.setWidgetResizable(True)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.closeButton = QtGui.QPushButton('Close', self)
        self.closeButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.closeButton)
        self.closeButton.setShortcut('Esc')
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked(bool)'), self.close)

        
class QModuleAnnotationTable(QtGui.QTableWidget):
    """
    QModuleAnnotationTable is a table widget that can be dock inside a
    window. It has two columns for key and value pairs to view/edit at
    run-time
    
    """    
    def __init__(self, module=None, controller=None, parent=None):
        """ QModuleAnnotationTable(module: Module, controller: 
        VistrailController, parent: QWidget) -> QModuleAnnotationTable
        Construct the 1x2 table
        
        """
        QtGui.QTableWidget.__init__(self, 1, 2, parent)
        self.read_only = False
        self.setHorizontalHeaderLabels(['Key', 'Value'])
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        self.horizontalHeader().setMovable(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.verticalHeader().hide()
        self.delegate = QKeyValueDelegate(self)
        self.setItemDelegate(self.delegate)
        self.module = module
        self.controller = controller
        self.updateLocked = False
        self.updateModule()

    def set_controller(self, controller):
        self.controller = controller

    def setReadOnly(self, read_only):
        if read_only != self.read_only:
            self.read_only = read_only
            self.setEnabled(not read_only and self.module is not None)

    def updateModule(self, module=None):
        """ updateModule() -> None
        Update the widget to view the module annotations
        """

        self.module = module
        self.setSortingEnabled(False)
        if self.updateLocked: return
        self.clearContents()
        self.setRowCount(0)
        if self.module:
            self.setRowCount(len(self.module.annotations)+1)
            curRow = 0
            for annotation in self.module.annotations:
                if annotation.key == '__desc__':
                    # We don't display the '__desc__' annotation in the list
                    # anymore. If it's present we decrease the rowcount by 1
                    self.setRowCount(len(self.module.annotations))
                else:
                    self.setItem(curRow, 0, QtGui.QTableWidgetItem(annotation.key))
                    item = QtGui.QTableWidgetItem(annotation.value)
                    self.setItem(curRow, 1, item)
                    curRow += 1
            self.setEnabled(not self.read_only)
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
        self.model().setData(index, oldFont, QtCore.Qt.FontRole)

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

    def editNextAvailableCell(self):
        item = self.item(self.rowCount()-1, 0)
        self.editItem(item)
        
class QKeyValueDelegate(QtGui.QItemDelegate):
    """    
    QKeyValueDelegate tries to create a special control widget
    providing a simple interface for adding/deleting module
    annotations
    
    """

    def __init__(self, table):
        """ QKeyValueDelegate(table: QModuleAnnotationTable) -> QKeyValueDelegate
        Save a reference to table and perform a default initialization
        
        """
        self.table = table
        QtGui.QItemDelegate.__init__(self, None)
    
    def setEditorData(self, editor, index):
        """ setEditorData(editor: QWidget, index: QModelIndex) -> None
        Set the current item (at index) data into editor for editting
        
        """
        text = index.data(QtCore.Qt.DisplayRole)
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
                    self.table.controller.delete_annotation(key,
                                                            self.table.module.id)
                    self.table.unlockUpdate()
                return
            if text!='' and text!=key:
                if (self.table.module and
                    self.table.module.has_annotation_with_key(text)):
                    if text == '__desc__':
                        QtGui.QMessageBox.information(None,
                                                      "VisTrails",
                                    'Please use "Set Module Label..." menu option'
                                    ' to set the label for this module.')
                    else:
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
                    self.table.controller.add_annotation((key, text),
                                                         self.table.module.id)
                    self.table.unlockUpdate()
            if row == self.table.rowCount()-1:
                self.table.addRow()
            
        elif text!='' and self.table.controller and self.table.module:
            moduleId = self.table.module.id
            self.table.lockUpdate()
            self.table.controller.previousModuleIds = [moduleId]
            if key!=text and key!='':
                self.table.controller.delete_annotation(key, moduleId)
            self.table.controller.add_annotation((text, value),
                                                 moduleId)
            self.table.unlockUpdate()
        
        model.setData(index, text)        
