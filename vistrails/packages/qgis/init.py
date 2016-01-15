###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import Module
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget

import qgis.core
import qgis.gui

import itertools
import os

class RasterLayer(Module):
    _input_ports = [('file', '(basic:File)'), 
                    ('name', '(basic:String)')]
    _output_ports = [('self', '(RasterLayer)')]

    def __init__(self):
        Module.__init__(self)
        self.qgis_obj = None

    def compute(self):
        fname = self.get_input('file').name
        if self.has_input('name'):
            name = self.get_input('name')
        else:
            name = os.path.splitext(os.path.basename(fname))[0]
        self.qgis_obj = qgis.core.QgsRasterLayer(fname, name)
        self.set_output('self', self)

class VectorLayer(Module):
    _input_ports = [('file', '(basic:File)'), 
                    ('name', '(basic:String)')]
    _output_ports = [('self', '(VectorLayer)')]

    def __init__(self):
        Module.__init__(self)
        self.qgis_obj = None

    def compute(self):
        fname = self.get_input('file').name
        if self.has_input('name'):
            name = self.get_input('name')
        else:
            name = os.path.splitext(os.path.basename(fname))[0]
        self.qgis_obj = qgis.core.QgsVectorLayer(fname, name, "ogr")
        self.set_output('self', self)

class QGISCell(SpreadsheetCell):
    """
    QGISCell is a VisTrails Module that can display QGIS inside a cell
    
    """
    _input_ports = [('rasterLayers', '(RasterLayer)'),
                    ('vectorLayers', '(VectorLayer)')]

    def __init__(self):
        SpreadsheetCell.__init__(self)
    
    def compute(self):
        rasterLayers = self.force_get_input_list('rasterLayers')
        vectorLayers = self.force_get_input_list('vectorLayers')
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

