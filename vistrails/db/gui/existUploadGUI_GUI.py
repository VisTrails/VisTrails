# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uploadVistrailExist.ui'
#
# Created: Wed Jun 28 12:26:06 2006
#      by: PyQt4 UI code generator vsnapshot-20060408
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,564,415).size()).expandedTo(Dialog.minimumSizeHint()))
        
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20,370,511,36))
        self.layoutWidget.setObjectName("layoutWidget")
        
        self.hboxlayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        
        spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        
#        self.exportButton = QtGui.QPushButton(self.layoutWidget)
#        self.exportButton.setObjectName("exportButton")
#        self.hboxlayout.addWidget(self.exportButton)
        
#        self.saveButton = QtGui.QPushButton(self.layoutWidget)
#        self.saveButton.setObjectName("saveButton")
#        self.hboxlayout.addWidget(self.saveButton)
        
        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        
        self.upButton = QtGui.QToolButton(Dialog)
        self.upButton.setGeometry(QtCore.QRect(460,30,31,29))
        self.upButton.setObjectName("upButton")
        
        self.folderTable = QtGui.QTableWidget(Dialog)
        self.folderTable.setGeometry(QtCore.QRect(10,10,441,141))
        self.folderTable.setObjectName("folderTable")
        
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30,340,41,21))
        self.label.setObjectName("label")
        
        self.filenameToSave = QtGui.QLineEdit(Dialog)
        self.filenameToSave.setGeometry(QtCore.QRect(80,340,471,21))
        self.filenameToSave.setObjectName("filenameToSave")
        
        self.openFolderButton = QtGui.QPushButton(Dialog)
        self.openFolderButton.setGeometry(QtCore.QRect(450,70,111,41))
        self.openFolderButton.setObjectName("openFolderButton")
        
        self.fileTable = QtGui.QTableWidget(Dialog)
        self.fileTable.setGeometry(QtCore.QRect(10,170,541,161))
        self.fileTable.setObjectName("fileTable")
        
        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Dialog"))
        self.cancelButton.setText(self.tr("Done"))
        self.upButton.setText(self.tr(".."))
        self.folderTable.clear()
        self.folderTable.setColumnCount(0)
        self.folderTable.setRowCount(0)
        self.label.setText(self.tr("File name\n"
        ""))
        self.openFolderButton.setText(self.tr("Open Folder"))
        self.fileTable.clear()
        self.fileTable.setColumnCount(0)
        self.fileTable.setRowCount(0)
