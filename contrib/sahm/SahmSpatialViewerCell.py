# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\SahmSpatialViewerCell.ui'
#
# Created: Tue Oct 11 16:20:25 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(734, 706)
        Frame.setWindowTitle(QtCore.QCoreApplication.translate("Frame", "Frame", None))
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.gridLayout = QtWidgets.QGridLayout(Frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(Frame)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.legend_frame_2 = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.legend_frame_2.sizePolicy().hasHeightForWidth())
        self.legend_frame_2.setSizePolicy(sizePolicy)
        self.legend_frame_2.setMinimumSize(QtCore.QSize(0, 0))
        self.legend_frame_2.setBaseSize(QtCore.QSize(0, 0))
        self.legend_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.legend_frame_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.legend_frame_2.setObjectName("legend_frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.legend_frame_2)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setContentsMargins(9, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.legend_label = QtWidgets.QLabel(self.legend_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.legend_label.sizePolicy().hasHeightForWidth())
        self.legend_label.setSizePolicy(sizePolicy)
        self.legend_label.setText(QtCore.QCoreApplication.translate("Frame", "TextLabel", None))
        self.legend_label.setObjectName("legend_label")
        self.horizontalLayout_2.addWidget(self.legend_label)
        self.legend = QtWidgets.QFrame(self.legend_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.legend.sizePolicy().hasHeightForWidth())
        self.legend.setSizePolicy(sizePolicy)
        self.legend.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.legend.setFrameShadow(QtWidgets.QFrame.Plain)
        self.legend.setLineWidth(0)
        self.legend.setObjectName("legend")
        self.legend_layout = QtWidgets.QHBoxLayout(self.legend)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setObjectName("legend_layout")
        self.horizontalLayout_2.addWidget(self.legend)
        self.map_frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.map_frame.sizePolicy().hasHeightForWidth())
        self.map_frame.setSizePolicy(sizePolicy)
        self.map_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.map_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.map_frame.setObjectName("map_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.map_frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        pass

