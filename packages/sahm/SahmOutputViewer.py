################################################################################
# ImageViewer widgets/toolbar implementation
################################################################################
from PyQt4 import QtCore, QtGui, QAxContainer
from core.modules.vistrails_module import Module
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from SahmViewerCell import Ui_Frame
#import imageviewer_rc
import os
################################################################################

class SAHMModelOutputViewerCell(SpreadsheetCell):
    """
    SAHMModelOutputViewerCell displays the various non-spatial
    outputs from a SAHM Model run
    """
    _input_ports = [("row", "(edu.utah.sci.vistrails.basic:Integer)"),
                    ("column", "(edu.utah.sci.vistrails.basic:Integer)"),
                    ('ModelWorkspace', '(edu.utah.sci.vistrails.basic:File)')]
     
    def compute(self):
        """ compute() -> None
        Dispatch the display event to the spreadsheet with images and labels
        
        """
        if self.hasInputFromPort("ModelWorkspace"):
            window = spreadsheetController.findSpreadsheetWindow()
            model_workspace = self.getInputFromPort("ModelWorkspace").name
            model_dir_full = os.path.normcase(os.path.split(model_workspace)[0])
            model_dir = os.path.split(model_dir_full)[1]
            model_name = model_dir[:model_dir.index('output')]
            
#            prob_map_path = os.path.join(model_dir_full, model_name + '_prob_map.jpeg')
#            prob_map = window.file_pool.make_local_copy(prob_map_path)
            
            auc_graph_path = os.path.join(model_dir_full, model_name + '_auc_plot.jpg')
            auc_graph = window.file_pool.make_local_copy(auc_graph_path)
            
            text_output_path = os.path.join(model_dir_full, model_name + '_output.txt')
            text_output = window.file_pool.make_local_copy(text_output_path)
            
            response_path = os.path.join(model_dir_full, model_name + '_response_curves.pdf')
            response_curves = window.file_pool.make_local_copy(response_path)
            
            model_label = model_dir.capitalize().replace('output', 'Output')
            
            
            if self.hasInputFromPort("row"):
                if not self.location:
                    self.location = CellLocation()
                self.location.row = self.getInputFromPort('row') - 1
            
            if self.hasInputFromPort("column"):
                if not self.location:
                    self.location = CellLocation()
                self.location.col = self.getInputFromPort('column') - 1
            
        else:
            fileValue = None
        self.cellWidget = self.displayAndWait(SAHMOutputViewerCellWidget, (auc_graph, 
                                                                      text_output,
                                                                      response_curves,
                                                                      model_label))

class SAHMOutputViewerCellWidget(QCellWidget):
    """
    SAHMOutputViewerCellWidget is the widget that will display the various
    non spatial outputs from a model run
    """
    def __init__(self, parent=None):
        QCellWidget.__init__(self, parent)
        
        centralLayout = QtGui.QVBoxLayout()
        self.setLayout(centralLayout)
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)

        
#        self.setAnimationEnabled(True)
        
        self.Frame = QtGui.QFrame()
        self.ui = Ui_Frame()
        self.ui.setupUi(self.Frame)
        
#        #add scenes to our graphicViews
#        self.gs_prob_map = QtGui.QGraphicsScene()
#        self.ui.gv_prob_map.setScene(self.gs_prob_map)
#        self.gs_prob_map.wheelEvent = self.wheel_event_prob
        
        self.gs_auc_graph = QtGui.QGraphicsScene()
        self.ui.gv_auc.setScene(self.gs_auc_graph)
        self.gs_auc_graph.wheelEvent = self.wheel_event_auc
        
        #add in ie browsers for the text and response
        self.text_browser = QAxContainer.QAxWidget(self)
        self.text_browser.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.text_browser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.ui.text_output_layout.addWidget(self.text_browser)
        self.text_urlSrc = None
        
        self.response_browser = QAxContainer.QAxWidget(self)
        self.response_browser.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.response_browser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.ui.response_curves_layout.addWidget(self.response_browser)
        self.response_urlSrc = None
        
        
        self.layout().addWidget(self.Frame)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Update the widget contents based on the input data
        
        """
        (auc_graph, text_output, response_curves, model_label) = inputPorts
        
        self.images = {}
#        if prob_map:
#            #Value = (full image, sized image, scene, view, max_height)
#            pixmap = QtGui.QPixmap(prob_map.name)
#            max_size = self.getMaxSize(self.ui.gv_prob_map)
#            scaled_pixmap = pixmap.scaled(max_size, max_size, 
#                                            QtCore.Qt.KeepAspectRatio, 
#                                            QtCore.Qt.FastTransformation)
#            
#            self.images['prob_map'] = [pixmap,
#                                       scaled_pixmap,
#                                       self.gs_prob_map,
#                                       self.ui.gv_prob_map,
#                                       max_size]
        
        if auc_graph:
            pixmap = QtGui.QPixmap(auc_graph.name)
            max_size = self.getMaxSize(self.ui.gv_auc)
            scaled_pixmap = pixmap.scaled(max_size, max_size, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.SmoothTransformation)
            
            self.images['auc_graph'] = [pixmap,
                                       scaled_pixmap,
                                       self.gs_auc_graph,
                                       self.ui.gv_auc,
                                       max_size]
        
        

        self.text_urlSrc = QtCore.QUrl.fromLocalFile(text_output.name)
        if self.text_urlSrc!=None:
            self.text_browser.dynamicCall('Navigate(const QString&)', self.text_urlSrc.toString())
        else:
            self.text_browser.dynamicCall('Navigate(const QString&)', QtCore.QString('about:blank'))

        self.response_urlSrc = QtCore.QUrl.fromLocalFile(response_curves.name)
        if self.response_urlSrc!=None:
            self.response_browser.dynamicCall('Navigate(const QString&)', self.response_urlSrc.toString())
        else:
            self.response_browser.dynamicCall('Navigate(const QString&)', QtCore.QString('about:blank'))

        self.view_current()

        #QCellWidget.updateContents(self, inputPorts)

    def getMaxSize(self, view):
        return self.Frame.size().width() - 10
#        if view.size().width()  <= view.size().height(): 
#            return view.size().width() * 0.95
#        else: 
#            return view.size().height() * 0.95
    
    def view_current(self):
        for k,v in self.images.iteritems():
            size_img = v[1].size() 
            wth, hgt = QtCore.QSize.width(size_img), QtCore.QSize.height(size_img) 
            v[2].clear() 
            v[2].setSceneRect(0, 0, wth, hgt) 
            v[2].addPixmap(v[1]) 
        QtCore.QCoreApplication.processEvents() 

    def wheel_event_prob(self, event):
        self.wheel_event(event, 'prob_map', QtCore.Qt.FastTransformation)

    def wheel_event_auc(self, event):
        self.wheel_event(event, 'auc_graph', QtCore.Qt.SmoothTransformation)

    def wheel_event (self, event, id, transform):
        numDegrees = event.delta() / 8 
        numSteps = numDegrees / 15.0 
        self.zoom(numSteps, self.images[id], transform) 
        event.accept() 

    def zoom(self, step, images, transform):
        zoom_step = 0.06
        images[2].clear() 
        w = images[1].size().width() 
        h = images[1].size().height() 
        w, h = w * (1 + zoom_step*step), h * (1 + zoom_step*step) 
        images[1] = images[0].scaled(w, h, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            transform) 
        self.view_current() 

    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> bool
        Save the current widget contents to an image file
        
        """

        pixmap = QtGui.QPixmap(self.Frame.size())
        painter = QtGui.QPainter(pixmap)
        self.Frame.render(painter)
        painter.end()
        
        if pixmap and (not pixmap.isNull()):
            return pixmap.save(filename)
        return False
    
    def saveToPDF(self, filename):
        """ saveToPDF(filename: str) -> bool
        Save the current widget contents to a pdf file
        
        """
        printer = QtGui.QPrinter()
        
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        painter = QtGui.QPainter()
        painter.begin(printer)
        rect = painter.viewport()
        pixmap = self.label.pixmap()
        size = pixmap.size()
        size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
#
#    def resizeEvent(self, e):
#        if self.originalPix!=None:
#            self.label.setPixmap(self.originalPix.scaled(self.label.size(),
#                                                         QtCore.Qt.KeepAspectRatio,
#                                                         QtCore.Qt.SmoothTransformation))
#                

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
                                               "Images (*.png);;PDF files (*.pdf)")
        if not fn:
            return
        if fn.endsWith(QtCore.QString("png"), QtCore.Qt.CaseInsensitive):
            cellWidget.label.pixmap().toImage().save(fn, "png")
        elif fn.endsWith(QtCore.QString("pdf"), QtCore.Qt.CaseInsensitive):
            cellWidget.saveToPDF(str(fn))

#class testButton(QtGui.QAction):
#     def __init__(self, parent=None):
#        """ ImageViewerRotateAction(parent: QWidget)
#                                       -> ImageViewerRotateAction
#        Setup the image, status tip, etc. of the action
#        
#        """
#        QtGui.QAction.__init__(self,
#                               QtGui.QIcon(":/images/grass_split_line.png"),
#                               "&Do Something...",
#                               parent)
#        self.setStatusTip("We'll do something with this soon")
#        self.rotationMatrix = QtGui.QMatrix(0,1,-1,0,0,0)
#
#class ModelLabel(QtGui.QLabel):
#    def __init__(self, parent=None):
#        """A lable to indicate which model the output pertains to
#        """
#        self.text = QtCore.QString("testing")
#        
#class ImageViewerZoomSlider(QtGui.QSlider):
#    """
#    ImageViewerZoomSlider is a slider that allows user to zoom in and
#    out by dragging it
#    """
#    def __init__(self, parent=None):
#        """ ImageViewerZoomSlider(parent: QWidget) -> ImageViewerZoomSlider
#        Setup the ranges, status tip, etc. of the slider
#        
#        """
#        QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
#        self.setRange(100, 600)
#        self.setValue(100)
#        self.setTracking(True)
#        self.setStatusTip("Zoom in the image")
#        self.connect(self, QtCore.SIGNAL("valueChanged(int)"), self.updateZoom)
#        self.connect(self, QtCore.SIGNAL("needUpdateStatus"), self.updateStatus)
#        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
#                           QtGui.QSizePolicy.Expanding)
#        
#    def updateZoom(self, value):
#        """ updateZoom(value: int) -> None
#        Update the image when the slider value changed
#        
#        """
#        if self.toolBar:
#            cellWidget = self.toolBar.getSnappedWidget()
#            if not cellWidget.label.hasScaledContents():
#                newWidth = cellWidget.originalPix.width()*value/100
#                pixmap = cellWidget.originalPix.scaledToWidth(newWidth)
#                cellWidget.label.setPixmap(pixmap)
#
#    def updateStatus(self, info):
#        """ updateStatus(info: tuple) -> None
#        Updates the status of the button based on the input info
#        
#        """
#        (sheet, row, col, cellWidget) = info
#        if cellWidget:
#            if (not cellWidget.label.hasScaledContents() and
#                not cellWidget._playing):
#                self.setEnabled(True)
#                originalWidth = cellWidget.originalPix.width()
#                self.setValue(cellWidget.label.pixmap().width()*100/originalWidth)
#            else:
#                self.setEnabled(False)
#                self.setValue(100)
#                
#class ImageViewerZoomLabel(QtGui.QLabel):
#    """
#    ImageViewerZoomLabel is the label sitting next to the ImageViewerZoomSlider
#    
#    """
#    def __init__(self, parent=None):
#        """ ImageViewerZoomSlider(parent: QWidget) -> None
#        Setup the label with a status tip
#        
#        """
#        QtGui.QLabel.__init__(self, "100%", parent)
#        self.setStatusTip("Zoom in the image")
#        
#    def updateValue(self, value):
#        """ updateValue(value: int)
#        Updates the label with the new percentage value
#        """
#        self.setText(str(value)+"%")
#                
#class ImageViewerRotateAction(QtGui.QAction):
#    """
#    ImageViewerRotateAction is the action to rotate the image
#    
#    """
#    def __init__(self, parent=None):
#        """ ImageViewerRotateAction(parent: QWidget)
#                                       -> ImageViewerRotateAction
#        Setup the image, status tip, etc. of the action
#        
#        """
#        QtGui.QAction.__init__(self,
#                               QtGui.QIcon(":/images/rotate.png"),
#                               "&Rotate CW...",
#                               parent)
#        self.setStatusTip("Rotate 90 degrees CW")
#        self.rotationMatrix = QtGui.QMatrix(0,1,-1,0,0,0)
#        
#    def triggeredSlot(self, checked=False):
#        """ toggledSlot(checked: boolean) -> None
#        Execute the action when the button is clicked
#        
#        """
#        cellWidget = self.toolBar.getSnappedWidget()
#        if not cellWidget.label.pixmap() or cellWidget.label.pixmap().isNull():
#            return
#        cellWidget.originalPix = cellWidget.originalPix.transformed(
#            self.rotationMatrix)
#        cellWidget.label.setPixmap(cellWidget.label.pixmap().transformed(
#            self.rotationMatrix))
#
#class ImageViewerFlipAction(QtGui.QAction):
#    """
#    ImageViewerFlipAction is the action to flip the image
#    
#    """
#    def __init__(self, parent=None):
#        """ ImageViewerFlipAction(parent: QWidget) -> ImageViewerFlipAction
#        Setup the image, status tip, etc. of the action
#        
#        """
#        QtGui.QAction.__init__(self,
#                               QtGui.QIcon(":/images/flip.png"),
#                               "&Flip Horizontal...",
#                               parent)
#        self.setStatusTip("Flip the image horizontally")
#        self.flipMatrix = QtGui.QMatrix(-1,0,0,1,0,0)
#        
#    def triggeredSlot(self, checked=False):
#        """ toggledSlot(checked: boolean) -> None
#        Execute the action when the button is clicked
#        
#        """
#        cellWidget = self.toolBar.getSnappedWidget()
#        label = cellWidget.label
#        if not label.pixmap() or label.pixmap().isNull():
#            return
#        cellWidget.originalPix = cellWidget.originalPix.transformed(
#            self.flipMatrix)
#        label.setPixmap(label.pixmap().transformed(self.flipMatrix))
#
#class ImageViewerToolBar(QCellToolBar):
#    """
#    ImageViewerToolBar derives from CellToolBar to give the ImageViewerCellWidget
#    a customizable toolbar
#    
#    """
#    def createToolBar(self):
#        """ createToolBar() -> None
#        This will get call initiallly to add customizable widgets
#        
#        """
#        global SAHMModelOutputViewerCell
#        
##        self.appendAction(QtCore.QString(SAHMModelOutputViewerCell.model_label))
#        self.appendAction(testButton(self))
#        self.appendAction(ImageViewerFitToCellAction(self))
#        self.appendAction(ImageViewerSaveAction(self))
#        self.appendAction(ImageViewerRotateAction(self))
#        self.appendAction(ImageViewerFlipAction(self))
#        self.slider = ImageViewerZoomSlider(self)
#        label = ImageViewerZoomLabel(self)
#        self.connect(self.slider,
#                     QtCore.SIGNAL("valueChanged(int)"),
#                     label.updateValue)
#        self.appendWidget(self.slider)
#        self.appendWidget(label)
#        self.addAnimationButtons()