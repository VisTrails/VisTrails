############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
################################################################################
# ImageViewer widgets/toolbar implementation
################################################################################
from PyQt4 import QtCore, QtGui
from core.modules.vistrails_module import Module
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
import imageviewer_rc

################################################################################

class ImageViewerCell(SpreadsheetCell):
    """
    ImageViewerCell is a custom Module to display labels, images, etc.
    
    """    
    def compute(self):
        """ compute() -> None
        Dispatch the display event to the spreadsheet with images and labels
        
        """
        if self.hasInputFromPort("File"):
            window = spreadsheetController.findSpreadsheetWindow()
            file_to_display = self.getInputFromPort("File")
            fileValue = window.file_pool.make_local_copy(file_to_display.name)
        else:
            fileValue = None
        self.cellWidget = self.displayAndWait(ImageViewerCellWidget, (fileValue, ))

class ImageViewerCellWidget(QCellWidget):
    """
    ImageViewerCellWidget is the actual QLabel that will draw
    labels/images on the spreadsheet
    
    """
    def __init__(self, parent=None):
        """ ImageViewerCellWidget(parent: QWidget) -> ImageViewerCellWidget
        Initialize the widget with its toolbar type and aligment
        
        """
        QCellWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.setAnimationEnabled(True)
        
        self.label = QtGui.QLabel()
        self.layout().addWidget(self.label)
        
        self.label.setAutoFillBackground(True)
        self.label.palette().setColor(QtGui.QPalette.Window, QtCore.Qt.white)
        self.label.setMouseTracking(False)
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.label.setScaledContents(False)
        self.toolBarType = ImageViewerToolBar
        self.originalPix = None
        self.setMinimumSize(1, 1)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Update the widget contents based on the input data
        
        """
        (fileValue, ) = inputPorts
        if fileValue:
            img = QtGui.QImage()
            if img.load(fileValue.name):
                self.originalPix = QtGui.QPixmap.fromImage(img)
                self.label.setPixmap(self.originalPix)
            else:
                self.label.setText("Invalid image file!")

        QCellWidget.updateContents(self, inputPorts)

    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> bool
        Save the current widget contents to an image file
        
        """
        pixmap = self.label.pixmap()
        if pixmap and (not pixmap.isNull()):
            return pixmap.save(filename)
        return False

    def resizeEvent(self, e):
        if self.originalPix!=None:
            self.label.setPixmap(self.originalPix.scaled(self.label.size(),
                                                         QtCore.Qt.KeepAspectRatio,
                                                         QtCore.Qt.SmoothTransformation))
                
class ImageViewerFitToCellAction(QtGui.QAction):
    """
    ImageViewerFitToCellAction is the action to stretch the image to
    fit inside a cell
    
    """
    def __init__(self, parent=None):
        """ ImageViewerFitToCellAction(parent: QWidget)
                                       -> ImageViewerFitToCellAction
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/fittocell.png"),
                               "&Fit To Cell",
                               parent)
        self.setStatusTip("Scale image content to fit cell frame")
        self.setCheckable(True)
        self.setChecked(True)

    def toggledSlot(self, checked):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is toggled
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        cellWidget.label.setScaledContents(checked)
        self.toolBar.slider.updateStatus((self.toolBar.sheet,
                                          self.toolBar.row,
                                          self.toolBar.col,
                                          cellWidget))
        
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        self.setChecked(cellWidget.label.hasScaledContents())

class ImageViewerSaveAction(QtGui.QAction):
    """
    ImageViewerSaveAction is the action to save the image to file
    
    """
    def __init__(self, parent=None):
        """ ImageViewerSaveAction(parent: QWidget) -> ImageViewerSaveAction
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/save.png"),
                               "&Save image as...",
                               parent)
        self.setStatusTip("Save image to file")
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        if not cellWidget.label.pixmap() or cellWidget.label.pixmap().isNull():
            return
        fn = QtGui.QFileDialog.getSaveFileName(None, "Save image as...",
                                               "screenshot.png",
                                               "Images (*.png)")
        if not fn:
            return
        cellWidget.label.pixmap().toImage().save(fn, "png")

class ImageViewerZoomSlider(QtGui.QSlider):
    """
    ImageViewerZoomSlider is a slider that allows user to zoom in and
    out by dragging it
    
    """
    def __init__(self, parent=None):
        """ ImageViewerZoomSlider(parent: QWidget) -> ImageViewerZoomSlider
        Setup the ranges, status tip, etc. of the slider
        
        """
        QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
        self.setRange(100, 300)
        self.setValue(100)
        self.setTracking(True)
        self.setStatusTip("Zoom in the image")
        self.connect(self, QtCore.SIGNAL("valueChanged(int)"), self.updateZoom)
        self.connect(self, QtCore.SIGNAL("needUpdateStatus"), self.updateStatus)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Expanding)
        
    def updateZoom(self, value):
        """ updateZoom(value: int) -> None
        Update the image when the slider value changed
        
        """
        if self.toolBar:
            cellWidget = self.toolBar.getSnappedWidget()
            if not cellWidget.label.hasScaledContents():
                newWidth = cellWidget.originalPix.width()*value/100
                pixmap = cellWidget.originalPix.scaledToWidth(newWidth)
                cellWidget.label.setPixmap(pixmap)

    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            if not cellWidget.label.hasScaledContents():
                self.setEnabled(True)
                originalWidth = cellWidget.originalPix.width()
                self.setValue(cellWidget.label.pixmap().width()*100/originalWidth)
            else:
                self.setEnabled(False)
                self.setValue(100)
                
class ImageViewerZoomLabel(QtGui.QLabel):
    """
    ImageViewerZoomLabel is the label sitting next to the ImageViewerZoomSlider
    
    """
    def __init__(self, parent=None):
        """ ImageViewerZoomSlider(parent: QWidget) -> None
        Setup the label with a status tip
        
        """
        QtGui.QLabel.__init__(self, "100%", parent)
        self.setStatusTip("Zoom in the image")
        
    def updateValue(self, value):
        """ updateValue(value: int)
        Updates the label with the new percentage value
        """
        self.setText(str(value)+"%")
                
class ImageViewerRotateAction(QtGui.QAction):
    """
    ImageViewerRotateAction is the action to rotate the image
    
    """
    def __init__(self, parent=None):
        """ ImageViewerRotateAction(parent: QWidget)
                                       -> ImageViewerRotateAction
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/rotate.png"),
                               "&Rotate CW...",
                               parent)
        self.setStatusTip("Rotate 90 degrees CW")
        self.rotationMatrix = QtGui.QMatrix(0,1,-1,0,0,0)
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        if not cellWidget.label.pixmap() or cellWidget.label.pixmap().isNull():
            return
        cellWidget.originalPix = cellWidget.originalPix.transformed(
            self.rotationMatrix)
        cellWidget.label.setPixmap(cellWidget.label.pixmap().transformed(
            self.rotationMatrix))

class ImageViewerFlipAction(QtGui.QAction):
    """
    ImageViewerFlipAction is the action to flip the image
    
    """
    def __init__(self, parent=None):
        """ ImageViewerFlipAction(parent: QWidget) -> ImageViewerFlipAction
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/flip.png"),
                               "&Flip Horizontal...",
                               parent)
        self.setStatusTip("Flip the image horizontally")
        self.flipMatrix = QtGui.QMatrix(-1,0,0,1,0,0)
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        label = cellWidget.label
        if not label.pixmap() or label.pixmap().isNull():
            return
        cellWidget.originalPix = labeloriginalPix.transformed(
            self.flipMatrix)
        label.setPixmap(label.pixmap().transformed(self.flipMatrix))

class ImageViewerToolBar(QCellToolBar):
    """
    ImageViewerToolBar derives from CellToolBar to give the ImageViewerCellWidget
    a customizable toolbar
    
    """
    def createToolBar(self):
        """ createToolBar() -> None
        This will get call initiallly to add customizable widgets
        
        """
        self.appendAction(ImageViewerFitToCellAction(self))
        self.appendAction(ImageViewerSaveAction(self))
        self.appendAction(ImageViewerRotateAction(self))
        self.appendAction(ImageViewerFlipAction(self))
        self.slider = ImageViewerZoomSlider(self)
        label = ImageViewerZoomLabel(self)
        self.connect(self.slider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     label.updateValue)
        self.appendWidget(self.slider)
        self.appendWidget(label)
        self.addAnimationButtons()
