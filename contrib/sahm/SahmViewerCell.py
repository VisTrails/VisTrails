# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SahmViewerCell.ui'
#
# Created: Thu Sep 29 18:41:54 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(546, 402)
        Frame.setWindowTitle(QtCore.QCoreApplication.translate("Frame", "Frame", None))
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(Frame)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setObjectName("tabWidget")
        self.text_output = QtWidgets.QWidget()
        self.text_output.setObjectName("text_output")
        self.text_output_layout = QtWidgets.QHBoxLayout(self.text_output)
        self.text_output_layout.setSpacing(0)
        self.text_output_layout.setContentsMargins(0, 0, 0, 0)
        self.text_output_layout.setObjectName("text_output_layout")
        self.tabWidget.addTab(self.text_output, "")
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.text_output), QtCore.QCoreApplication.translate("Frame", "Textual model output ", None))
        self.response_curves = QtWidgets.QWidget()
        self.response_curves.setObjectName("response_curves")
        self.response_curves_layout = QtWidgets.QHBoxLayout(self.response_curves)
        self.response_curves_layout.setSpacing(0)
        self.response_curves_layout.setContentsMargins(0, 0, 0, 0)
        self.response_curves_layout.setObjectName("response_curves_layout")
        self.tabWidget.addTab(self.response_curves, "")
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.response_curves), QtCore.QCoreApplication.translate("Frame", "Response curves", None))
        self.auc = QtWidgets.QWidget()
        self.auc.setObjectName("auc")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.auc)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gv_auc = QtWidgets.QGraphicsView(self.auc)
        self.gv_auc.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.gv_auc.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.gv_auc.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.gv_auc.setObjectName("gv_auc")
        self.horizontalLayout_4.addWidget(self.gv_auc)
        self.tabWidget.addTab(self.auc, "")
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.auc), QtCore.QCoreApplication.translate("Frame", "Area under the curve (AUC)", None))
        self.horizontalLayout.addWidget(self.tabWidget)

        self.retranslateUi(Frame)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.text_output), QtCore.QCoreApplication.translate("Frame", "Model Results", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.response_curves), QtCore.QCoreApplication.translate("Frame", "Response", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.auc), QtCore.QCoreApplication.translate("Frame", "AUC", None))

