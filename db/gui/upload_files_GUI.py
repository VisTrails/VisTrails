# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'upload_files_GUI.ui'
#
# Created: Thu Jun 15 18:45:37 2006
#      by: PyQt4 UI code generator vsnapshot-20060408
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Upload(object):
    def setupUi(self, Upload):
        Upload.setObjectName("Upload")
        Upload.resize(QtCore.QSize(QtCore.QRect(0,0,664,598).size()).expandedTo(Upload.minimumSizeHint()))
        
        self.gridlayout = QtGui.QGridLayout(Upload)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setMargin(0)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")
        
        self.lbl_user = QtGui.QLabel(Upload)
        self.lbl_user.setObjectName("lbl_user")
        self.gridlayout1.addWidget(self.lbl_user,2,0,1,1)
        
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        
        self.btn_find_files = QtGui.QPushButton(Upload)
        self.btn_find_files.setObjectName("btn_find_files")
        self.hboxlayout.addWidget(self.btn_find_files)
        
        self.btn_find_dir = QtGui.QPushButton(Upload)
        self.btn_find_dir.setObjectName("btn_find_dir")
        self.hboxlayout.addWidget(self.btn_find_dir)
        
        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridlayout1.addLayout(self.hboxlayout,1,1,1,1)
        
        self.txt_notes = QtGui.QTextEdit(Upload)
        self.txt_notes.setObjectName("txt_notes")
        self.gridlayout1.addWidget(self.txt_notes,3,1,1,1)
        
        self.lbl_notes = QtGui.QLabel(Upload)
        self.lbl_notes.setObjectName("lbl_notes")
        self.gridlayout1.addWidget(self.lbl_notes,3,0,1,1)
        
        self.lbl_file = QtGui.QLabel(Upload)
        self.lbl_file.setObjectName("lbl_file")
        self.gridlayout1.addWidget(self.lbl_file,0,0,1,1)
        
        self.txt_file = QtGui.QLineEdit(Upload)
        self.txt_file.setReadOnly(True)
        self.txt_file.setObjectName("txt_file")
        self.gridlayout1.addWidget(self.txt_file,0,1,1,1)
        
        self.label = QtGui.QLabel(Upload)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,1,0,1,1)
        
        self.txt_user = QtGui.QLineEdit(Upload)
        self.txt_user.setObjectName("txt_user")
        self.gridlayout1.addWidget(self.txt_user,2,1,1,1)
        self.vboxlayout.addLayout(self.gridlayout1)
        
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")
        
        spacerItem1 = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        
        self.btn_send = QtGui.QPushButton(Upload)
        self.btn_send.setObjectName("btn_send")
        self.hboxlayout1.addWidget(self.btn_send)
        
        self.btn_done = QtGui.QPushButton(Upload)
        self.btn_done.setObjectName("btn_done")
        self.hboxlayout1.addWidget(self.btn_done)
        self.vboxlayout.addLayout(self.hboxlayout1)
        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)
        
        self.retranslateUi(Upload)
        QtCore.QMetaObject.connectSlotsByName(Upload)
    
    def tr(self, string):
        return QtGui.QApplication.translate("Upload", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, Upload):
        Upload.setWindowTitle(self.tr("Upload"))
        self.lbl_user.setText(self.tr("User:"))
        self.btn_find_files.setText(self.tr("Find Files..."))
        self.btn_find_dir.setText(self.tr("Find Directory..."))
        self.lbl_notes.setText(self.tr("Notes:"))
        self.lbl_file.setText(self.tr("File:"))
        self.txt_file.setText(self.tr("< Please, use a \"Find...\" button >"))
        self.btn_send.setText(self.tr("Send"))
        self.btn_done.setText(self.tr("Done"))
