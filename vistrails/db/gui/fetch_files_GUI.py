# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fetch_files_GUI.ui'
#
# Created: Thu Jun 15 18:46:28 2006
#      by: PyQt4 UI code generator vsnapshot-20060408
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Fetch(object):
    def setupUi(self, Fetch):
        Fetch.setObjectName("Fetch")
        Fetch.resize(QtCore.QSize(QtCore.QRect(0,0,527,427).size()).expandedTo(Fetch.minimumSizeHint()))
        
        self.gridlayout = QtGui.QGridLayout(Fetch)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        
        self.lbl_favoriteQueries = QtGui.QLabel(Fetch)
        self.lbl_favoriteQueries.setObjectName("lbl_favoriteQueries")
        self.hboxlayout.addWidget(self.lbl_favoriteQueries)
        
        self.cmb_queries = QtGui.QComboBox(Fetch)
        self.cmb_queries.setObjectName("cmb_queries")
        self.hboxlayout.addWidget(self.cmb_queries)
        
        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.vboxlayout.addLayout(self.hboxlayout)
        
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")
        
        self.txt_query = QtGui.QLineEdit(Fetch)
        self.txt_query.setObjectName("txt_query")
        self.hboxlayout1.addWidget(self.txt_query)
        
        self.btn_search = QtGui.QPushButton(Fetch)
        self.btn_search.setObjectName("btn_search")
        self.hboxlayout1.addWidget(self.btn_search)
        self.vboxlayout.addLayout(self.hboxlayout1)
        
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")
        
        self.tbl_results = QtGui.QTableWidget(Fetch)
        self.tbl_results.setObjectName("tbl_results")
        self.hboxlayout2.addWidget(self.tbl_results)
        self.vboxlayout.addLayout(self.hboxlayout2)
        
        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")
        
        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem1)
        
        self.btn_getSelectedFiles = QtGui.QPushButton(Fetch)
        self.btn_getSelectedFiles.setObjectName("btn_getSelectedFiles")
        self.hboxlayout3.addWidget(self.btn_getSelectedFiles)
        
        self.btn_done = QtGui.QPushButton(Fetch)
        self.btn_done.setObjectName("btn_done")
        self.hboxlayout3.addWidget(self.btn_done)
        self.vboxlayout.addLayout(self.hboxlayout3)
        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)
        
        self.retranslateUi(Fetch)
        QtCore.QMetaObject.connectSlotsByName(Fetch)
    
    def tr(self, string):
        return QtGui.QApplication.translate("Fetch", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, Fetch):
        Fetch.setWindowTitle(self.tr("Fetch Files"))
        self.lbl_favoriteQueries.setText(self.tr("Sample Queries:"))
        self.btn_search.setText(self.tr("Search"))
        self.tbl_results.clear()
        self.tbl_results.setColumnCount(0)
        self.tbl_results.setRowCount(0)
        self.btn_getSelectedFiles.setText(self.tr("Get Selected Files"))
        self.btn_done.setText(self.tr("Done"))
