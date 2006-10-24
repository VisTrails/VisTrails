# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created: Wed Jun 14 15:02:34 2006
#      by: PyQt4 UI code generator vsnapshot-20060408
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,573,177).size()).expandedTo(Dialog.minimumSizeHint()))
        
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(470,35,79,91))
        self.layoutWidget.setObjectName("layoutWidget")
        
        self.vboxlayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.loginButton = QtGui.QPushButton(self.layoutWidget)
        self.loginButton.setObjectName("loginButton")
        self.vboxlayout.addWidget(self.loginButton)
        
        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.vboxlayout.addWidget(self.cancelButton)
        
        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)
        
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20,110,71,16))
        self.label_3.setObjectName("label_3")
        
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20,30,91,20))
        self.label.setObjectName("label")
        
        self.serverLine = QtGui.QLineEdit(Dialog)
        self.serverLine.setGeometry(QtCore.QRect(130,30,321,21))
        self.serverLine.setObjectName("serverLine")
        
        self.usernameLine = QtGui.QLineEdit(Dialog)
        self.usernameLine.setGeometry(QtCore.QRect(130,70,321,21))
        self.usernameLine.setObjectName("usernameLine")
        
        self.passwdLine = QtGui.QLineEdit(Dialog)
        self.passwdLine.setGeometry(QtCore.QRect(130,110,321,21))
        self.passwdLine.setAcceptDrops(True)
        self.passwdLine.setEchoMode(QtGui.QLineEdit.Password)
        self.passwdLine.setObjectName("passwdLine")
        
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20,70,81,41))
        self.label_2.setObjectName("label_2")
        
        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
    def tr(self, string):
        return QtGui.QApplication.translate("Dialog", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(self.tr("Dialog"))
        self.loginButton.setText(self.tr("OK"))
        self.cancelButton.setText(self.tr("Cancel"))
        self.label_3.setText(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:MS Shell Dlg; font-size:8.25pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">Password </span></p></body></html>"))
        self.label.setText(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:MS Shell Dlg; font-size:8.25pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><span style=\" font-size:9pt;\">Server</span></p></body></html>"))
        self.label_2.setText(self.tr("<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:MS Shell Dlg; font-size:8.25pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:Sans Serif; font-size:9pt;\">User name</p><p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:Sans Serif; font-size:9pt;\"></p></body></html>"))
