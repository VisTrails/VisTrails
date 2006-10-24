import modules
from modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_helpers import *
import imageviewer_rc

# A custom widget to output labels, images...
class ImageViewerCell(SpreadsheetCell):
    
    def compute(self):
        if self.hasInputFromPort("File"): fileValue = self.getInputFromPort("File")
        else: fileValue = None
        self.display(ImageViewerCellWidget, (fileValue, ))

### Image Viewer widget type
class ImageViewerCellWidget(QtGui.QLabel):
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.palette().setColor(QtGui.QPalette.Window, QtCore.Qt.white)
        self.setMouseTracking(False)
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.toolBarType = ImageViewerToolBar
        self.setScaledContents(True)
        self.originalPix = None

    def updateContents(self, inputPorts):
        (fileValue, ) = inputPorts
        if fileValue:
            img = QtGui.QImage()
            if img.load(fileValue.name):
                self.originalPix = QtGui.QPixmap.fromImage(img)
                self.setPixmap(self.originalPix)
            else:
                self.setText("Invalid image file!")
                
### Setting up the customized toolbar for static label cell
class ImageViewerFitToCellAction(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/fittocell.png"),
                               "&Fit To Cell",
                               parent)
        self.setStatusTip("Scale image content to fit cell frame")
        self.setCheckable(True)
        self.setChecked(True)

    def toggledSlot(self, checked):
        cellWidget = self.toolBar.getSnappedWidget()
        cellWidget.setScaledContents(checked)
        self.toolBar.slider.updateStatus((self.toolBar.sheet,
                                          self.toolBar.row,
                                          self.toolBar.col,
                                          cellWidget))
        
    def updateStatus(self, info):
        (sheet, row, col, cellWidget) = info
        self.setChecked(cellWidget.hasScaledContents())

class ImageViewerSaveAction(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/save.png"),
                               "&Save image as...",
                               parent)
        self.setStatusTip("Save image to file")
        
    def triggeredSlot(self, checked=False):
        cellWidget = self.toolBar.getSnappedWidget()
        if not cellWidget.pixmap() or cellWidget.pixmap().isNull():
            return
        fn = QtGui.QFileDialog.getSaveFileName(None, "Save image as...", "screenshot.png", "Images (*.png)")
        if not fn:
            return
        cellWidget.pixmap().toImage().save(fn, "png")

class ImageViewerZoomSlider(QtGui.QSlider):
    def __init__(self, parent=None):
        QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
        self.setRange(100, 300)
        self.setValue(100)
        self.setTracking(True)
        self.setStatusTip("Zoom in the image")
        self.connect(self, QtCore.SIGNAL("valueChanged(int)"), self.updateZoom)
        self.connect(self, QtCore.SIGNAL("needUpdateStatus"), self.updateStatus)
        
    def updateZoom(self, value):
        if self.toolBar:
            cellWidget = self.toolBar.getSnappedWidget()
            if not cellWidget.hasScaledContents():
                cellWidget.setPixmap(cellWidget.originalPix.scaledToWidth(cellWidget.originalPix.width()*value/100))

    def updateStatus(self, info):
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            if not cellWidget.hasScaledContents():
                self.setEnabled(True)
                self.setValue(cellWidget.pixmap().width()*100/cellWidget.originalPix.width())
            else:
                self.setEnabled(False)
                self.setValue(100)
                
class ImageViewerZoomLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, "100%", parent)
        self.setStatusTip("Zoom in the image")
        
    def updateValue(self, value):
        self.setText(str(value)+"%")
                
class ImageViewerRotateAction(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/rotate.png"),
                               "&Rotate CW...",
                               parent)
        self.setStatusTip("Rotate 90 degrees CW")
        self.rotationMatrix = QtGui.QMatrix(0,1,-1,0,0,0)
        
    def triggeredSlot(self, checked=False):
        cellWidget = self.toolBar.getSnappedWidget()
        if not cellWidget.pixmap() or cellWidget.pixmap().isNull():
            return
        cellWidget.originalPix = cellWidget.originalPix.transformed(self.rotationMatrix)
        cellWidget.setPixmap(cellWidget.pixmap().transformed(self.rotationMatrix))        

class ImageViewerFlipAction(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/flip.png"),
                               "&Flip Horizontal...",
                               parent)
        self.setStatusTip("Flip the image horizontally")
        self.flipMatrix = QtGui.QMatrix(-1,0,0,1,0,0)
        
    def triggeredSlot(self, checked=False):
        cellWidget = self.toolBar.getSnappedWidget()
        if not cellWidget.pixmap() or cellWidget.pixmap().isNull():
            return
        cellWidget.originalPix = cellWidget.originalPix.transformed(self.flipMatrix)
        cellWidget.setPixmap(cellWidget.pixmap().transformed(self.flipMatrix))        

class ImageViewerToolBar(CellToolBar):
    def createToolBar(self):
        self.appendAction(ImageViewerFitToCellAction(self))
        self.appendAction(ImageViewerSaveAction(self))
        self.appendAction(ImageViewerRotateAction(self))
        self.appendAction(ImageViewerFlipAction(self))
        self.slider = ImageViewerZoomSlider(self)
        label = ImageViewerZoomLabel(self)
        self.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"), label.updateValue)
        self.appendWidget(self.slider)
        self.appendWidget(label)
