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

"""Widgets to display/edit configuration objects."""

from PyQt4 import QtGui, QtCore
from gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget
from core.configuration import ConfigurationObject

##############################################################################

class QConfigurationTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self, parent, obj, name):
        lst = QtCore.QStringList(name)
        t = type(obj)
        self._obj_type = t
        if t == ConfigurationObject:
            lst << '' << ''
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags(self.flags() & ~(QtCore.Qt.ItemIsDragEnabled |
                                           QtCore.Qt.ItemIsSelectable |
                                           QtCore.Qt.ItemIsEnabled))
        elif t == tuple and obj[0] is None and type(obj[1]) == type:
            self._obj_type = obj[1]
            lst << '' << obj[1].__name__
            QtGui.QTreeWidget.__init__(self, parent, lst)
            self.setFlags((self.flags() & ~QtCore.Qt.ItemIsDragEnabled) |
                          QtCore.Qt.ItemIsEditable)
        else:
            lst << str(obj) << type(obj).__name__
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags((self.flags() & ~QtCore.Qt.ItemIsDragEnabled) |
                          QtCore.Qt.ItemIsEditable)

class QConfigurationTreeWidgetItemDelegate(QtGui.QItemDelegate):
    """
    QConfigurationTreeWidgetItemDelegate allows a custom editor for
    each column of the QConfigurationTreeWidget    
    """
    
    def createEditor(self, parent, option, index):
        """ createEditor(parent: QWidget,
                         option: QStyleOptionViewItem,
                         index: QModelIndex) -> QWidget
        Return the editing widget depending on columns
        
        """
        # We only allow users to edit the  second column
        if index.column()==1:
            dataType = str(index.sibling(index.row(), 2).data().toString())
            
            # Create the editor based on dataType
            if dataType=='int':
                editor = QtGui.QLineEdit(parent)
                editor.setValidator(QtGui.QIntValidator(parent))
            elif dataType=='bool':
                editor = QtGui.QComboBox(parent)
                editor.addItem('True')
                editor.addItem('False')
            else:
                editor = QtGui.QItemDelegate.createEditor(self, parent,
                                                          option, index)
            return editor            
        return None

    def setEditorData(self, editor, index):
        """ setEditorData(editor: QWidget, index: QModelIndex) -> None
        Set the editor to reflects data at index
        
        """
        if type(editor)==QtGui.QComboBox:           
            editor.setCurrentIndex(editor.findText(index.data().toString()))
        else:
            QtGui.QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """ setModelData(editor: QStringEdit,
                         model: QAbstractItemModel,
                         index: QModelIndex) -> None
        Set the text of the editor back to the item model
        
        """
        if type(editor)==QtGui.QComboBox:
            model.setData(index, QtCore.QVariant(editor.currentText()))
        else:
            model.setData(index, QtCore.QVariant(editor.text()))
    

class QConfigurationTreeWidget(QSearchTreeWidget):

    def __init__(self, parent):
        QSearchTreeWidget.__init__(self, parent)
        self.setMatchedFlags(QtCore.Qt.ItemIsEnabled)
        self.setColumnCount(3)
        lst = QtCore.QStringList()
        lst << 'Name'
        lst << 'Value'
        lst << 'Type'
        self.setHeaderLabels(lst)
        self.create_tree()
        self.expandAll()
        self.resizeColumnToContents(0)

    def create_tree(self):
        def create_item(parent, obj, name):
            item = QConfigurationTreeWidgetItem(parent, obj, name)
            if type(obj) == ConfigurationObject:
                for key in sorted(obj.keys()):
                    create_item(item, getattr(obj, key), key)
        from gui.application import VistrailsApplication
        c = VistrailsApplication.vistrailsStartup.configuration
        create_item(self, c, 'configuration')

class QConfigurationTreeWindow(QSearchTreeWindow):

    def createTreeWidget(self):
        self.setWindowTitle('Configuration')
        treeWidget = QConfigurationTreeWidget(self)
        
        # The delegate has to be around (self._delegate) to
        # work, else the instance will be clean by Python...
        self._delegate = QConfigurationTreeWidgetItemDelegate()
        treeWidget.setItemDelegate(self._delegate)
        return treeWidget

class QConfigurationWidget(QtGui.QWidget):

    def __init__(self, parent, status_bar):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)
        self._status_bar = status_bar

        self._tree = QConfigurationTreeWindow()
        lbl = QtGui.QLabel("Set configuration variables for VisTrails here.", self)
        layout.addWidget(lbl)
        layout.addWidget(self._tree)
