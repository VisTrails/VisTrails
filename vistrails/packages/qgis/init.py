from PyQt4 import QtCore, QtGui
from core.modules.vistrails_module import Module
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar

import qgis.core
import qgis.gui

import itertools
import os

class RasterLayer(Module):
    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'), 
                    ('name', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('self', '(edu.utah.sci.vistrails.qgis:RasterLayer)')]

    def __init__(self):
        Module.__init__(self)
        self.qgis_obj = None

    def compute(self):
        fname = self.getInputFromPort('file').name
        if self.hasInputFromPort('name'):
            name = self.getInputFromPort('name')
        else:
            name = os.path.splitext(os.path.basename(fname))[0]
        self.qgis_obj = qgis.core.QgsRasterLayer(fname, name)
        self.setResult('self', self)

class VectorLayer(Module):
    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'), 
                    ('name', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('self', '(edu.utah.sci.vistrails.qgis:VectorLayer)')]

    def __init__(self):
        Module.__init__(self)
        self.qgis_obj = None

    def compute(self):
        fname = self.getInputFromPort('file').name
        if self.hasInputFromPort('name'):
            name = self.getInputFromPort('name')
        else:
            name = os.path.splitext(os.path.basename(fname))[0]
        self.qgis_obj = qgis.core.QgsVectorLayer(fname, name, "ogr")
        self.setResult('self', self)

class QGISCell(SpreadsheetCell):
    """
    QGISCell is a VisTrails Module that can display QGIS inside a cell
    
    """
    _input_ports = [('rasterLayers', '(edu.utah.sci.vistrails.qgis:RasterLayer)'),
                    ('vectorLayers', '(edu.utah.sci.vistrails.qgis:VectorLayer)')]

    def __init__(self):
        SpreadsheetCell.__init__(self)
    
    def compute(self):
        rasterLayers = self.forceGetInputListFromPort('rasterLayers')
        vectorLayers = self.forceGetInputListFromPort('vectorLayers')
        self.displayAndWait(QGISCellWidget, (rasterLayers, vectorLayers))

class QGISCellWidget(QCellWidget):
    """
    QGISCellWidget is the actual QWidget taking the FigureManager
    as a child for displaying figures
    
    """
    def __init__(self, parent=None):
        """ QGISCellWidget(parent: QWidget) -> QGISCellWidget
        Initialize the widget with its central layout
        
        """
        QCellWidget.__init__(self, parent)
        centralLayout = QtGui.QVBoxLayout()
        self.setLayout(centralLayout)
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Update the widget contents based on the input data
        
        """
        (rasterLayers, vectorLayers) = inputPorts

        canvas = qgis.gui.QgsMapCanvas()
        canvas.show()

        canvas.setCanvasColor(QtCore.Qt.white)
        canvas.enableAntiAliasing(True)

        for layer in itertools.chain(rasterLayers, vectorLayers):
            print 'adding layer', layer.qgis_obj
            qgis.core.QgsMapLayerRegistry.instance().addMapLayer(layer.qgis_obj)
        
        canvas.setExtent(rasterLayers[0].qgis_obj.extent())
        canvas.setLayerSet([qgis.gui.QgsMapCanvasLayer(layer.qgis_obj) 
                            for layer in itertools.chain(vectorLayers, 
                                                         rasterLayers)])

        # raster_fname = "/vistrails/local_packages/qgis/qgis_sample_data/raster/landcover.img"
        # raster = qgis.core.QgsRasterLayer(raster_fname, os.path.splitext(os.path.basename(raster_fname))[0])
        # qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster)

        # layer = qgis.core.QgsVectorLayer("/vistrails/local_packages/qgis/qgis_sample_data/vmap0_shapefiles/majrivers.shp", "Rivers", "ogr")
        # print layer.isValid()
        # qgis.core.QgsMapLayerRegistry.instance().addMapLayer(layer)
        # canvas.setLayerSet([qgis.gui.QgsMapCanvasLayer(layer), 
        #                     qgis.gui.QgsMapCanvasLayer(raster)])
    
        self.layout().addWidget(canvas)

        # Update the new figure canvas
        self.update()

    def grabWindowPixmap(self):
        """ grabWindowPixmap() -> QPixmap
        Widget special grabbing function
 	       
        """
        # return QtGui.QPixmap.grabWidget(self.figManager.canvas)
        return None

    def dumpToFile(self, filename):
        pass

    def saveToPDF(self, filename):
        pass

_modules = [RasterLayer, VectorLayer, QGISCell,]

def initialize():
    qgis.core.QgsApplication.setPrefixPath(
        "/vistrails/local_packages/qgis/QGIS.app/Contents/MacOS", True)
    qgis.core.QgsApplication.initQgis()

