# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logout.ui'
#
# Created: Thu Jun 22 15:48:06 2006
#      by: PyQt4 UI code generator vsnapshot-20060408
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,389,173).size()).expandedTo(Dialog.minimumSizeHint()))
        
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20,120,351,36))
        self.layoutWidget.setObjectName("layoutWidget")
        
        self.hboxlayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        
        spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        
        self.logoutButton = QtGui.QPushButton(self.layoutWidget)
        self.logoutButton.setObjectName("logoutButton")
        self.hboxlayout.addWidget(self.logoutButton)
        
        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)
        
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(100,30,178,51))
        self.label.setObjectName("label")
        
        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Dialog"))
        self.logoutButton.setText(self.tr("Log out"))
        self.cancelButton.setText(self.tr("Cancel"))
        self.label.setText(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:Sans Serif; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:17pt;\">Do you wish to log out?</span></p></body></html>"))
