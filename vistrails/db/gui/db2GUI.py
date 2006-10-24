# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unknown'
#
# Created: Mon Aug 14 14:51:03 2006
#      by: PyQt4 UI code generator 4-snapshot-20060607
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_DB2InteractionDialog(object):
    def setupUi(self, DB2InteractionDialog):
        DB2InteractionDialog.setObjectName("DB2InteractionDialog")
        DB2InteractionDialog.resize(QtCore.QSize(QtCore.QRect(0,0,653,508).size()).expandedTo(DB2InteractionDialog.minimumSizeHint()))

        self.layoutWidget = QtGui.QWidget(DB2InteractionDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(290,470,351,33))
        self.layoutWidget.setObjectName("layoutWidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.okButton = QtGui.QPushButton(self.layoutWidget)
        self.okButton.setObjectName("okButton")
        self.hboxlayout.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.hboxlayout.addWidget(self.cancelButton)

        self.labelConnection = QtGui.QLabel(DB2InteractionDialog)
        self.labelConnection.setGeometry(QtCore.QRect(20,480,101,16))
        self.labelConnection.setObjectName("labelConnection")

        self.labelConnectionStatus = QtGui.QLabel(DB2InteractionDialog)
        self.labelConnectionStatus.setGeometry(QtCore.QRect(140,480,101,16))
        self.labelConnectionStatus.setObjectName("labelConnectionStatus")

        self.tabs = QtGui.QTabWidget(DB2InteractionDialog)
        self.tabs.setGeometry(QtCore.QRect(10,20,631,441))
        self.tabs.setObjectName("tabs")

        self.tabConnect = QtGui.QWidget()
        self.tabConnect.setObjectName("tabConnect")

        self.labelHost = QtGui.QLabel(self.tabConnect)
        self.labelHost.setGeometry(QtCore.QRect(20,10,51,20))
        self.labelHost.setObjectName("labelHost")

        self.editHostname = QtGui.QLineEdit(self.tabConnect)
        self.editHostname.setGeometry(QtCore.QRect(110,10,221,22))
        self.editHostname.setAcceptDrops(False)
        self.editHostname.setObjectName("editHostname")

        self.editUsername = QtGui.QLineEdit(self.tabConnect)
        self.editUsername.setGeometry(QtCore.QRect(110,50,113,22))
        self.editUsername.setAcceptDrops(False)
        self.editUsername.setObjectName("editUsername")

        self.editPassword = QtGui.QLineEdit(self.tabConnect)
        self.editPassword.setGeometry(QtCore.QRect(110,90,113,22))
        self.editPassword.setAcceptDrops(False)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.editPassword.setObjectName("editPassword")

        self.labelUser = QtGui.QLabel(self.tabConnect)
        self.labelUser.setGeometry(QtCore.QRect(20,50,48,16))
        self.labelUser.setObjectName("labelUser")

        self.labelPassword = QtGui.QLabel(self.tabConnect)
        self.labelPassword.setGeometry(QtCore.QRect(20,90,51,16))
        self.labelPassword.setObjectName("labelPassword")

        self.buttonLogin = QtGui.QPushButton(self.tabConnect)
        self.buttonLogin.setGeometry(QtCore.QRect(20,140,111,24))
        self.buttonLogin.setObjectName("buttonLogin")

        self.buttonLogout = QtGui.QPushButton(self.tabConnect)
        self.buttonLogout.setGeometry(QtCore.QRect(20,180,111,24))
        self.buttonLogout.setObjectName("buttonLogout")
        self.tabs.addTab(self.tabConnect, "")

        self.tabBasic = QtGui.QWidget()
        self.tabBasic.setObjectName("tabBasic")

        self.labelQueryResults = QtGui.QLabel(self.tabBasic)
        self.labelQueryResults.setGeometry(QtCore.QRect(10,240,181,21))
        self.labelQueryResults.setObjectName("labelQueryResults")

        self.editSaveTo = QtGui.QLineEdit(self.tabBasic)
        self.editSaveTo.setGeometry(QtCore.QRect(100,10,311,22))
        self.editSaveTo.setObjectName("editSaveTo")

        self.buttonSaveTo = QtGui.QPushButton(self.tabBasic)
        self.buttonSaveTo.setGeometry(QtCore.QRect(10,10,75,24))
        self.buttonSaveTo.setObjectName("buttonSaveTo")

        self.buttonBasicRunQuery = QtGui.QPushButton(self.tabBasic)
        self.buttonBasicRunQuery.setGeometry(QtCore.QRect(480,130,131,24))
        self.buttonBasicRunQuery.setObjectName("buttonBasicRunQuery")

        self.derivedBGroup = QtGui.QGroupBox(self.tabBasic)
        self.derivedBGroup.setGeometry(QtCore.QRect(340,40,120,151))
        self.derivedBGroup.setObjectName("derivedBGroup")

        self.edit_BDerivDate = QtGui.QLineEdit(self.derivedBGroup)
        self.edit_BDerivDate.setGeometry(QtCore.QRect(10,120,101,22))
        self.edit_BDerivDate.setObjectName("edit_BDerivDate")

        self.label_BDerivDate = QtGui.QLabel(self.derivedBGroup)
        self.label_BDerivDate.setGeometry(QtCore.QRect(10,100,46,14))
        self.label_BDerivDate.setObjectName("label_BDerivDate")

        self.checkBox_BDerivICA = QtGui.QCheckBox(self.derivedBGroup)
        self.checkBox_BDerivICA.setGeometry(QtCore.QRect(10,60,70,19))
        self.checkBox_BDerivICA.setObjectName("checkBox_BDerivICA")

        self.checkBox_BDerivPCA = QtGui.QCheckBox(self.derivedBGroup)
        self.checkBox_BDerivPCA.setGeometry(QtCore.QRect(10,40,70,19))
        self.checkBox_BDerivPCA.setObjectName("checkBox_BDerivPCA")

        self.checkBox_BDerivPSD = QtGui.QCheckBox(self.derivedBGroup)
        self.checkBox_BDerivPSD.setGeometry(QtCore.QRect(10,20,70,19))
        self.checkBox_BDerivPSD.setObjectName("checkBox_BDerivPSD")

        self.rawBGroup = QtGui.QGroupBox(self.tabBasic)
        self.rawBGroup.setGeometry(QtCore.QRect(210,40,121,151))
        self.rawBGroup.setObjectName("rawBGroup")

        self.label_BRawDate = QtGui.QLabel(self.rawBGroup)
        self.label_BRawDate.setGeometry(QtCore.QRect(10,100,46,14))
        self.label_BRawDate.setObjectName("label_BRawDate")

        self.edit_BRawDate = QtGui.QLineEdit(self.rawBGroup)
        self.edit_BRawDate.setGeometry(QtCore.QRect(10,120,101,22))
        self.edit_BRawDate.setObjectName("edit_BRawDate")

        self.checkBox_BRawEEG = QtGui.QCheckBox(self.rawBGroup)
        self.checkBox_BRawEEG.setGeometry(QtCore.QRect(10,20,70,19))
        self.checkBox_BRawEEG.setObjectName("checkBox_BRawEEG")

        self.checkBox_BRawMEG = QtGui.QCheckBox(self.rawBGroup)
        self.checkBox_BRawMEG.setGeometry(QtCore.QRect(10,40,70,19))
        self.checkBox_BRawMEG.setObjectName("checkBox_BRawMEG")

        self.checkBox_BRawMRI = QtGui.QCheckBox(self.rawBGroup)
        self.checkBox_BRawMRI.setGeometry(QtCore.QRect(10,60,70,19))
        self.checkBox_BRawMRI.setObjectName("checkBox_BRawMRI")

        self.checkBox_BRawGenetic = QtGui.QCheckBox(self.rawBGroup)
        self.checkBox_BRawGenetic.setGeometry(QtCore.QRect(10,80,70,19))
        self.checkBox_BRawGenetic.setObjectName("checkBox_BRawGenetic")

        self.editPID = QtGui.QLineEdit(self.tabBasic)
        self.editPID.setGeometry(QtCore.QRect(480,40,131,22))
        self.editPID.setObjectName("editPID")

        self.labelPID = QtGui.QLabel(self.tabBasic)
        self.labelPID.setGeometry(QtCore.QRect(480,10,91,21))
        self.labelPID.setObjectName("labelPID")

        self.demoBGroup = QtGui.QGroupBox(self.tabBasic)
        self.demoBGroup.setGeometry(QtCore.QRect(10,40,191,201))
        self.demoBGroup.setObjectName("demoBGroup")

        self.edit_BDemoSex = QtGui.QLineEdit(self.demoBGroup)
        self.edit_BDemoSex.setGeometry(QtCore.QRect(80,50,91,22))
        self.edit_BDemoSex.setObjectName("edit_BDemoSex")

        self.edit_BDemoEthnicity = QtGui.QLineEdit(self.demoBGroup)
        self.edit_BDemoEthnicity.setGeometry(QtCore.QRect(80,80,91,22))
        self.edit_BDemoEthnicity.setObjectName("edit_BDemoEthnicity")

        self.edit_BDemoTag = QtGui.QLineEdit(self.demoBGroup)
        self.edit_BDemoTag.setGeometry(QtCore.QRect(80,140,91,22))
        self.edit_BDemoTag.setObjectName("edit_BDemoTag")

        self.edit_BDemoDate = QtGui.QLineEdit(self.demoBGroup)
        self.edit_BDemoDate.setGeometry(QtCore.QRect(80,170,91,22))
        self.edit_BDemoDate.setObjectName("edit_BDemoDate")

        self.edit_BDemoAge = QtGui.QLineEdit(self.demoBGroup)
        self.edit_BDemoAge.setGeometry(QtCore.QRect(80,20,91,22))
        self.edit_BDemoAge.setObjectName("edit_BDemoAge")

        self.edit_BDemoBday = QtGui.QLineEdit(self.demoBGroup)
        self.edit_BDemoBday.setGeometry(QtCore.QRect(80,110,91,22))
        self.edit_BDemoBday.setObjectName("edit_BDemoBday")

        self.labelBDemoSex = QtGui.QLabel(self.demoBGroup)
        self.labelBDemoSex.setGeometry(QtCore.QRect(10,50,46,14))
        self.labelBDemoSex.setObjectName("labelBDemoSex")

        self.labelBDemoEthnicity = QtGui.QLabel(self.demoBGroup)
        self.labelBDemoEthnicity.setGeometry(QtCore.QRect(10,80,51,16))
        self.labelBDemoEthnicity.setObjectName("labelBDemoEthnicity")

        self.labelBDemoBday = QtGui.QLabel(self.demoBGroup)
        self.labelBDemoBday.setGeometry(QtCore.QRect(10,110,52,16))
        self.labelBDemoBday.setObjectName("labelBDemoBday")

        self.labelBDemoTag = QtGui.QLabel(self.demoBGroup)
        self.labelBDemoTag.setGeometry(QtCore.QRect(10,140,46,14))
        self.labelBDemoTag.setObjectName("labelBDemoTag")

        self.labelBDemoDate = QtGui.QLabel(self.demoBGroup)
        self.labelBDemoDate.setGeometry(QtCore.QRect(10,170,61,16))
        self.labelBDemoDate.setObjectName("labelBDemoDate")

        self.labelBDemoAge = QtGui.QLabel(self.demoBGroup)
        self.labelBDemoAge.setGeometry(QtCore.QRect(10,20,46,14))
        self.labelBDemoAge.setObjectName("labelBDemoAge")

        self.buttonBasicResetQuery = QtGui.QPushButton(self.tabBasic)
        self.buttonBasicResetQuery.setGeometry(QtCore.QRect(480,70,131,24))
        self.buttonBasicResetQuery.setObjectName("buttonBasicResetQuery")

        self.buttonBasicResetResults = QtGui.QPushButton(self.tabBasic)
        self.buttonBasicResetResults.setGeometry(QtCore.QRect(480,100,131,24))
        self.buttonBasicResetResults.setObjectName("buttonBasicResetResults")

        self.buttonBasicFetch = QtGui.QPushButton(self.tabBasic)
        self.buttonBasicFetch.setGeometry(QtCore.QRect(260,210,171,31))
        self.buttonBasicFetch.setObjectName("buttonBasicFetch")

        self.resultsBTable = QtGui.QTableWidget(self.tabBasic)
        self.resultsBTable.setGeometry(QtCore.QRect(10,260,601,141))
        self.resultsBTable.setAlternatingRowColors(True)
        self.resultsBTable.setShowGrid(False)
        self.resultsBTable.setObjectName("resultsBTable")
        self.tabs.addTab(self.tabBasic, "")

        self.tabAdd = QtGui.QWidget()
        self.tabAdd.setObjectName("tabAdd")

        self.groupAssoc = QtGui.QGroupBox(self.tabAdd)
        self.groupAssoc.setGeometry(QtCore.QRect(10,10,201,341))
        self.groupAssoc.setObjectName("groupAssoc")

        self.radio_AssocRawMEG = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocRawMEG.setGeometry(QtCore.QRect(10,60,81,19))
        self.radio_AssocRawMEG.setObjectName("radio_AssocRawMEG")

        self.radio_AssocRawMRI = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocRawMRI.setGeometry(QtCore.QRect(10,80,81,19))
        self.radio_AssocRawMRI.setObjectName("radio_AssocRawMRI")

        self.radio_AssocEEGPCA = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocEEGPCA.setGeometry(QtCore.QRect(10,120,81,19))
        self.radio_AssocEEGPCA.setObjectName("radio_AssocEEGPCA")

        self.radio_AssocEEGICA = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocEEGICA.setGeometry(QtCore.QRect(10,140,81,19))
        self.radio_AssocEEGICA.setObjectName("radio_AssocEEGICA")

        self.radio_AssocMEGPCA = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocMEGPCA.setGeometry(QtCore.QRect(10,180,81,19))
        self.radio_AssocMEGPCA.setObjectName("radio_AssocMEGPCA")

        self.radio_AssocRawEEG = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocRawEEG.setGeometry(QtCore.QRect(10,40,81,19))
        self.radio_AssocRawEEG.setObjectName("radio_AssocRawEEG")

        self.radio_AssocMEGICA = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocMEGICA.setGeometry(QtCore.QRect(10,200,81,19))
        self.radio_AssocMEGICA.setObjectName("radio_AssocMEGICA")

        self.radio_AssocSegMRI = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocSegMRI.setGeometry(QtCore.QRect(10,220,101,19))
        self.radio_AssocSegMRI.setObjectName("radio_AssocSegMRI")

        self.radio_AssocRawGenetic = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocRawGenetic.setGeometry(QtCore.QRect(10,240,91,19))
        self.radio_AssocRawGenetic.setObjectName("radio_AssocRawGenetic")

        self.radio_AssocProcGenetic = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocProcGenetic.setGeometry(QtCore.QRect(10,260,121,19))
        self.radio_AssocProcGenetic.setObjectName("radio_AssocProcGenetic")

        self.radio_AssocOther = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocOther.setGeometry(QtCore.QRect(10,280,81,19))
        self.radio_AssocOther.setObjectName("radio_AssocOther")

        self.edit_AssocOther = QtGui.QLineEdit(self.groupAssoc)
        self.edit_AssocOther.setGeometry(QtCore.QRect(10,310,171,22))
        self.edit_AssocOther.setObjectName("edit_AssocOther")

        self.checkBox_AssocNew = QtGui.QCheckBox(self.groupAssoc)
        self.checkBox_AssocNew.setGeometry(QtCore.QRect(10,20,111,19))
        self.checkBox_AssocNew.setCheckable(True)
        self.checkBox_AssocNew.setObjectName("checkBox_AssocNew")

        self.radio_AssocEEGPSD = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocEEGPSD.setGeometry(QtCore.QRect(10,100,81,19))
        self.radio_AssocEEGPSD.setObjectName("radio_AssocEEGPSD")

        self.radio_AssocMEGPSD = QtGui.QRadioButton(self.groupAssoc)
        self.radio_AssocMEGPSD.setGeometry(QtCore.QRect(10,160,81,19))
        self.radio_AssocMEGPSD.setObjectName("radio_AssocMEGPSD")

        self.buttonAddFrom = QtGui.QPushButton(self.tabAdd)
        self.buttonAddFrom.setGeometry(QtCore.QRect(10,380,101,24))
        self.buttonAddFrom.setObjectName("buttonAddFrom")

        self.buttonClear = QtGui.QPushButton(self.tabAdd)
        self.buttonClear.setGeometry(QtCore.QRect(260,320,131,24))
        self.buttonClear.setObjectName("buttonClear")

        self.buttonAdd = QtGui.QPushButton(self.tabAdd)
        self.buttonAdd.setGeometry(QtCore.QRect(450,320,121,24))
        self.buttonAdd.setObjectName("buttonAdd")

        self.editAddFrom = QtGui.QLineEdit(self.tabAdd)
        self.editAddFrom.setGeometry(QtCore.QRect(120,380,491,22))
        self.editAddFrom.setObjectName("editAddFrom")

        self.groupDemo = QtGui.QGroupBox(self.tabAdd)
        self.groupDemo.setGeometry(QtCore.QRect(220,10,391,291))
        self.groupDemo.setObjectName("groupDemo")

        self.edit_DemoSex = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoSex.setGeometry(QtCore.QRect(110,80,181,22))
        self.edit_DemoSex.setObjectName("edit_DemoSex")

        self.edit_DemoEthnicity = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoEthnicity.setGeometry(QtCore.QRect(110,110,181,22))
        self.edit_DemoEthnicity.setObjectName("edit_DemoEthnicity")

        self.edit_DemoBday = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoBday.setGeometry(QtCore.QRect(110,140,181,22))
        self.edit_DemoBday.setObjectName("edit_DemoBday")

        self.edit_DemoTag = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoTag.setGeometry(QtCore.QRect(110,170,181,22))
        self.edit_DemoTag.setObjectName("edit_DemoTag")

        self.edit_DemoDate = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoDate.setGeometry(QtCore.QRect(110,200,181,22))
        self.edit_DemoDate.setObjectName("edit_DemoDate")

        self.edit_DemoPID = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoPID.setGeometry(QtCore.QRect(110,20,181,22))
        self.edit_DemoPID.setObjectName("edit_DemoPID")

        self.edit_DemoAge = QtGui.QLineEdit(self.groupDemo)
        self.edit_DemoAge.setGeometry(QtCore.QRect(110,50,181,22))
        self.edit_DemoAge.setObjectName("edit_DemoAge")

        self.label_savePID = QtGui.QLabel(self.groupDemo)
        self.label_savePID.setGeometry(QtCore.QRect(20,20,65,16))
        self.label_savePID.setObjectName("label_savePID")

        self.label_saveAge = QtGui.QLabel(self.groupDemo)
        self.label_saveAge.setGeometry(QtCore.QRect(20,50,51,16))
        self.label_saveAge.setObjectName("label_saveAge")

        self.label_saveSex = QtGui.QLabel(self.groupDemo)
        self.label_saveSex.setGeometry(QtCore.QRect(20,80,41,16))
        self.label_saveSex.setObjectName("label_saveSex")

        self.label_saveEthnicity = QtGui.QLabel(self.groupDemo)
        self.label_saveEthnicity.setGeometry(QtCore.QRect(20,110,41,16))
        self.label_saveEthnicity.setObjectName("label_saveEthnicity")

        self.label_saveBday = QtGui.QLabel(self.groupDemo)
        self.label_saveBday.setGeometry(QtCore.QRect(20,140,41,16))
        self.label_saveBday.setObjectName("label_saveBday")

        self.label_saveTag = QtGui.QLabel(self.groupDemo)
        self.label_saveTag.setGeometry(QtCore.QRect(20,170,41,16))
        self.label_saveTag.setObjectName("label_saveTag")

        self.label_saveDate = QtGui.QLabel(self.groupDemo)
        self.label_saveDate.setGeometry(QtCore.QRect(20,200,41,16))
        self.label_saveDate.setObjectName("label_saveDate")
        self.tabs.addTab(self.tabAdd, "")

        self.tabAdvanced = QtGui.QWidget()
        self.tabAdvanced.setObjectName("tabAdvanced")

        self.labelQuery = QtGui.QLabel(self.tabAdvanced)
        self.labelQuery.setGeometry(QtCore.QRect(10,10,111,20))
        self.labelQuery.setObjectName("labelQuery")

        self.buttonRunQuery = QtGui.QPushButton(self.tabAdvanced)
        self.buttonRunQuery.setGeometry(QtCore.QRect(480,100,121,24))
        self.buttonRunQuery.setObjectName("buttonRunQuery")

        self.buttonQueryReset = QtGui.QPushButton(self.tabAdvanced)
        self.buttonQueryReset.setGeometry(QtCore.QRect(480,20,121,24))
        self.buttonQueryReset.setObjectName("buttonQueryReset")

        self.buttonResultReset = QtGui.QPushButton(self.tabAdvanced)
        self.buttonResultReset.setGeometry(QtCore.QRect(480,60,121,24))
        self.buttonResultReset.setObjectName("buttonResultReset")

        self.textEditQuery = QtGui.QTextEdit(self.tabAdvanced)
        self.textEditQuery.setGeometry(QtCore.QRect(10,40,441,81))
        self.textEditQuery.setObjectName("textEditQuery")

        self.labelResults = QtGui.QLabel(self.tabAdvanced)
        self.labelResults.setGeometry(QtCore.QRect(20,140,131,16))
        self.labelResults.setObjectName("labelResults")

        self.resultsBTable_2 = QtGui.QTableWidget(self.tabAdvanced)
        self.resultsBTable_2.setGeometry(QtCore.QRect(10,160,601,211))
        self.resultsBTable_2.setAlternatingRowColors(True)
        self.resultsBTable_2.setShowGrid(False)
        self.resultsBTable_2.setObjectName("resultsBTable_2")

        self.buttonFetchFiles = QtGui.QPushButton(self.tabAdvanced)
        self.buttonFetchFiles.setGeometry(QtCore.QRect(410,380,201,23))
        self.buttonFetchFiles.setObjectName("buttonFetchFiles")
        self.tabs.addTab(self.tabAdvanced, "")

        self.retranslateUi(DB2InteractionDialog)
        self.tabs.setCurrentIndex(0)
        QtCore.QObject.connect(self.okButton,QtCore.SIGNAL("clicked()"),DB2InteractionDialog.accept)
        QtCore.QObject.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),DB2InteractionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DB2InteractionDialog)

    def tr(self, string):
        return QtGui.QApplication.translate("DB2InteractionDialog", string, None, QtGui.QApplication.UnicodeUTF8)

    def retranslateUi(self, DB2InteractionDialog):
        DB2InteractionDialog.setWindowTitle(self.tr("DB2 Interaction"))
        self.okButton.setText(self.tr("OK"))
        self.cancelButton.setText(self.tr("Cancel"))
        self.labelConnection.setText(self.tr("Connection Status:"))
        self.labelConnectionStatus.setText(self.tr("Disconnected"))
        self.labelHost.setText(self.tr("Hostname"))
        self.labelUser.setText(self.tr("Username"))
        self.labelPassword.setText(self.tr("Password"))
        self.buttonLogin.setText(self.tr("Connect"))
        self.buttonLogout.setText(self.tr("Disconnect"))
        self.tabs.setTabText(self.tabs.indexOf(self.tabConnect), self.tr("Connection"))
        self.labelQueryResults.setText(self.tr("Query Results:"))
        self.buttonSaveTo.setText(self.tr("Save To"))
        self.buttonBasicRunQuery.setText(self.tr("Run Query"))
        self.derivedBGroup.setTitle(self.tr("Derived Data"))
        self.label_BDerivDate.setText(self.tr("Date:"))
        self.checkBox_BDerivICA.setText(self.tr("ICA"))
        self.checkBox_BDerivPCA.setText(self.tr("PCA"))
        self.checkBox_BDerivPSD.setText(self.tr("SPD"))
        self.rawBGroup.setTitle(self.tr("Raw Data"))
        self.label_BRawDate.setText(self.tr("Date:"))
        self.checkBox_BRawEEG.setText(self.tr("EEG"))
        self.checkBox_BRawMEG.setText(self.tr("MEG"))
        self.checkBox_BRawMRI.setText(self.tr("MRI"))
        self.checkBox_BRawGenetic.setText(self.tr("Genetic"))
        self.labelPID.setText(self.tr("Participant ID:"))
        self.demoBGroup.setTitle(self.tr("Demographics"))
        self.labelBDemoSex.setText(self.tr("Sex:"))
        self.labelBDemoEthnicity.setText(self.tr("Ethnicity:"))
        self.labelBDemoBday.setText(self.tr("Birth Date:"))
        self.labelBDemoTag.setText(self.tr("Tag:"))
        self.labelBDemoDate.setText(self.tr("Date:"))
        self.labelBDemoAge.setText(self.tr("Age:"))
        self.buttonBasicResetQuery.setText(self.tr("Reset Query"))
        self.buttonBasicResetResults.setText(self.tr("Reset Results"))
        self.buttonBasicFetch.setText(self.tr("Fetch Selected Files"))
        self.resultsBTable.clear()
        self.resultsBTable.setColumnCount(7)
        self.resultsBTable.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(self.tr("ID"))
        self.resultsBTable.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(self.tr("Age"))
        self.resultsBTable.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(self.tr("Sex"))
        self.resultsBTable.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(self.tr("Ethnicity"))
        self.resultsBTable.setHorizontalHeaderItem(3,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(self.tr("Birthday"))
        self.resultsBTable.setHorizontalHeaderItem(4,headerItem4)

        headerItem5 = QtGui.QTableWidgetItem()
        headerItem5.setText(self.tr("Tag"))
        self.resultsBTable.setHorizontalHeaderItem(5,headerItem5)

        headerItem6 = QtGui.QTableWidgetItem()
        headerItem6.setText(self.tr("Date Added"))
        self.resultsBTable.setHorizontalHeaderItem(6,headerItem6)
        self.tabs.setTabText(self.tabs.indexOf(self.tabBasic), self.tr("Basic Queries"))
        self.groupAssoc.setTitle(self.tr("Association Type"))
        self.radio_AssocRawMEG.setText(self.tr("Raw MEG"))
        self.radio_AssocRawMRI.setText(self.tr("Raw MRI"))
        self.radio_AssocEEGPCA.setText(self.tr("EEG PCA"))
        self.radio_AssocEEGICA.setText(self.tr("EEG ICA"))
        self.radio_AssocMEGPCA.setText(self.tr("MEG PCA"))
        self.radio_AssocRawEEG.setText(self.tr("Raw EEG"))
        self.radio_AssocMEGICA.setText(self.tr("MEG ICA"))
        self.radio_AssocSegMRI.setText(self.tr("Segmented MRI"))
        self.radio_AssocRawGenetic.setText(self.tr("Raw Genetic"))
        self.radio_AssocProcGenetic.setText(self.tr("Processed Genetic"))
        self.radio_AssocOther.setText(self.tr("Other:"))
        self.checkBox_AssocNew.setText(self.tr("New Participant"))
        self.radio_AssocEEGPSD.setText(self.tr("EEG SPD"))
        self.radio_AssocMEGPSD.setText(self.tr("MEG SPD"))
        self.buttonAddFrom.setText(self.tr("Add Files From:"))
        self.buttonClear.setText(self.tr("Clear Options"))
        self.buttonAdd.setText(self.tr("Add File(s)"))
        self.groupDemo.setTitle(self.tr("Demographics"))
        self.label_savePID.setText(self.tr("Participant ID"))
        self.label_saveAge.setText(self.tr("Age"))
        self.label_saveSex.setText(self.tr("Sex"))
        self.label_saveEthnicity.setText(self.tr("Ethnicity"))
        self.label_saveBday.setText(self.tr("Birthday"))
        self.label_saveTag.setText(self.tr("Tag"))
        self.label_saveDate.setText(self.tr("Date"))
        self.tabs.setTabText(self.tabs.indexOf(self.tabAdd), self.tr("Add Files To Database"))
        self.labelQuery.setText(self.tr("Query Statement:"))
        self.buttonRunQuery.setText(self.tr("Run Query"))
        self.buttonQueryReset.setText(self.tr("Reset Query"))
        self.buttonResultReset.setText(self.tr("Reset Results"))
        self.labelResults.setText(self.tr("Query Results:"))
        self.resultsBTable_2.clear()
        self.resultsBTable_2.setColumnCount(7)
        self.resultsBTable_2.setRowCount(0)

        headerItem7 = QtGui.QTableWidgetItem()
        headerItem7.setText(self.tr("ID"))
        self.resultsBTable_2.setHorizontalHeaderItem(0,headerItem7)

        headerItem8 = QtGui.QTableWidgetItem()
        headerItem8.setText(self.tr("Age"))
        self.resultsBTable_2.setHorizontalHeaderItem(1,headerItem8)

        headerItem9 = QtGui.QTableWidgetItem()
        headerItem9.setText(self.tr("Sex"))
        self.resultsBTable_2.setHorizontalHeaderItem(2,headerItem9)

        headerItem10 = QtGui.QTableWidgetItem()
        headerItem10.setText(self.tr("Ethnicity"))
        self.resultsBTable_2.setHorizontalHeaderItem(3,headerItem10)

        headerItem11 = QtGui.QTableWidgetItem()
        headerItem11.setText(self.tr("Birthday"))
        self.resultsBTable_2.setHorizontalHeaderItem(4,headerItem11)

        headerItem12 = QtGui.QTableWidgetItem()
        headerItem12.setText(self.tr("Tag"))
        self.resultsBTable_2.setHorizontalHeaderItem(5,headerItem12)

        headerItem13 = QtGui.QTableWidgetItem()
        headerItem13.setText(self.tr("Date Added"))
        self.resultsBTable_2.setHorizontalHeaderItem(6,headerItem13)
        self.buttonFetchFiles.setText(self.tr("Fetch Selected Files"))
        self.tabs.setTabText(self.tabs.indexOf(self.tabAdvanced), self.tr("Advanced"))
