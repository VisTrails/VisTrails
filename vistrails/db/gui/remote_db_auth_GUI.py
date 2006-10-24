# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remote_db_auth_GUI.ui'
#
# Created: Thu Jun 15 18:48:59 2006
#      by: PyQt4 UI code generator vsnapshot-20060408
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Database(object):
    def setupUi(self, Database):
        Database.setObjectName("Database")
        Database.resize(QtCore.QSize(QtCore.QRect(0,0,481,100).size()).expandedTo(Database.minimumSizeHint()))
        
        self.gridlayout = QtGui.QGridLayout(Database)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        
        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)
        
        self.label = QtGui.QLabel(Database)
        self.label.setObjectName("label")
        self.vboxlayout.addWidget(self.label)
        
        self.label_2 = QtGui.QLabel(Database)
        self.label_2.setObjectName("label_2")
        self.vboxlayout.addWidget(self.label_2)
        
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        
        self.label_3 = QtGui.QLabel(Database)
        self.label_3.setObjectName("label_3")
        self.hboxlayout.addWidget(self.label_3)
        
        self.txt_dbpassword = QtGui.QLineEdit(Database)
        self.txt_dbpassword.setEchoMode(QtGui.QLineEdit.Password)
        self.txt_dbpassword.setObjectName("txt_dbpassword")
        self.hboxlayout.addWidget(self.txt_dbpassword)
        
        self.btn_submit = QtGui.QPushButton(Database)
        self.btn_submit.setObjectName("btn_submit")
        self.hboxlayout.addWidget(self.btn_submit)
        
        self.btn_quit = QtGui.QPushButton(Database)
        self.btn_quit.setObjectName("btn_quit")
        self.hboxlayout.addWidget(self.btn_quit)
        self.vboxlayout.addLayout(self.hboxlayout)
        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)
        
        self.retranslateUi(Database)
        QtCore.QMetaObject.connectSlotsByName(Database)
    
    def tr(self, string):
        return QtGui.QApplication.translate("Database", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, Database):
        Database.setWindowTitle(self.tr("Dialog"))
        self.label.setText(self.tr("You need to provide a valid password to access this feature."))
        self.label_2.setText(self.tr("Please, read the instructions provided at \"vistrails.cfg\" file."))
        self.label_3.setText(self.tr("DB Password:"))
        self.btn_submit.setText(self.tr("Submit"))
        self.btn_quit.setText(self.tr("Quit"))
