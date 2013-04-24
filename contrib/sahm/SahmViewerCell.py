# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SahmViewerCell.ui'
#
# Created: Thu Sep 29 18:41:54 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName(_fromUtf8("Frame"))
        Frame.resize(546, 402)
        Frame.setWindowTitle(QtGui.QApplication.translate("Frame", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        Frame.setFrameShape(QtGui.QFrame.StyledPanel)
        Frame.setFrameShadow(QtGui.QFrame.Raised)
        self.horizontalLayout = QtGui.QHBoxLayout(Frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabWidget = QtGui.QTabWidget(Frame)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.text_output = QtGui.QWidget()
        self.text_output.setObjectName(_fromUtf8("text_output"))
        self.text_output_layout = QtGui.QHBoxLayout(self.text_output)
        self.text_output_layout.setSpacing(0)
        self.text_output_layout.setMargin(0)
        self.text_output_layout.setObjectName(_fromUtf8("text_output_layout"))
        self.tabWidget.addTab(self.text_output, _fromUtf8(""))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.text_output), QtGui.QApplication.translate("Frame", "Textual model output ", None, QtGui.QApplication.UnicodeUTF8))
        self.response_curves = QtGui.QWidget()
        self.response_curves.setObjectName(_fromUtf8("response_curves"))
        self.response_curves_layout = QtGui.QHBoxLayout(self.response_curves)
        self.response_curves_layout.setSpacing(0)
        self.response_curves_layout.setMargin(0)
        self.response_curves_layout.setObjectName(_fromUtf8("response_curves_layout"))
        self.tabWidget.addTab(self.response_curves, _fromUtf8(""))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.response_curves), QtGui.QApplication.translate("Frame", "Response curves", None, QtGui.QApplication.UnicodeUTF8))
        self.auc = QtGui.QWidget()
        self.auc.setObjectName(_fromUtf8("auc"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.auc)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.gv_auc = QtGui.QGraphicsView(self.auc)
        self.gv_auc.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.gv_auc.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.gv_auc.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.gv_auc.setObjectName(_fromUtf8("gv_auc"))
        self.horizontalLayout_4.addWidget(self.gv_auc)
        self.tabWidget.addTab(self.auc, _fromUtf8(""))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.auc), QtGui.QApplication.translate("Frame", "Area under the curve (AUC)", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontalLayout.addWidget(self.tabWidget)

        self.retranslateUi(Frame)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.text_output), QtGui.QApplication.translate("Frame", "Model Results", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.response_curves), QtGui.QApplication.translate("Frame", "Response", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.auc), QtGui.QApplication.translate("Frame", "AUC", None, QtGui.QApplication.UnicodeUTF8))

