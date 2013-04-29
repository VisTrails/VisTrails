################################################################################
# ImageViewer widgets/toolbar implementation
################################################################################
from PyQt4 import QtCore, QtGui, QAxContainer
from core.modules.vistrails_module import Module
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from SahmSpatialViewerCell import Ui_Frame
#import imageviewer_rc
import os

import csv

from packages.sahm.pySAHM.utilities import mds_to_shape
from utils import getrasterminmax
################################################################################

def setQGIS(qgis):
    globals()["qgis"] = qgis

class SAHMSpatialOutputViewerCell(SpreadsheetCell):
    """
    SAHMModelOutputViewerCell displays the various output from a SAHM Model run

    """
    _input_ports = [("row", "(edu.utah.sci.vistrails.basic:Integer)"),
                    ("column", "(edu.utah.sci.vistrails.basic:Integer)"),
                    ('model_workspace', '(edu.utah.sci.vistrails.basic:File)')]

    def __init__(self):
        SpreadsheetCell.__init__(self)

#        globals()["qgis"] = qgis

    def compute(self):
        inputs = {}
        inputs["model_workspace"] = self.forceGetInputFromPort('model_workspace').name
        inputs["model_dir"] = os.path.split(inputs["model_workspace"])[0]

        inputs["prob_map"] = os.path.join(inputs["model_dir"],
                                self.find_file(inputs["model_dir"], "_prob_map.tif"))
        inputs["bin_map"] = os.path.join(inputs["model_dir"],
                               self.find_file(inputs["model_dir"], "_bin_map.tif"))
        inputs["res_map"] = os.path.join(inputs["model_dir"],
                               self.find_file(inputs["model_dir"], "_resid_map.tif"))
        try:
            inputs["mes_map"] = os.path.join(inputs["model_dir"],
                                   self.find_file(inputs["model_dir"], "_mess_map.tif"))
        except:
            inputs["mes_map"] = ""
        
        try:
            inputs["mod_map"] = os.path.join(inputs["model_dir"],
                               self.find_file(inputs["model_dir"], "_MoD_map.tif"))
        except:
            inputs["mod_map"] = ""

        mds = self.find_mds(inputs["model_dir"])
        shaperoot = self.gen_points_shp(mds)
        inputs["pres_points"] = shaperoot + "_pres.shp"
        inputs["abs_points"] = shaperoot + "_abs.shp"
        inputs["backs_points"] = shaperoot + "_backs.shp"

        inputs["model_tag"] = os.path.split(inputs["model_dir"])[1]

        if self.hasInputFromPort("row"):
            if not self.location:
                self.location = CellLocation()
            self.location.row = self.getInputFromPort('row') - 1
        
        if self.hasInputFromPort("column"):
            if not self.location:
                self.location = CellLocation()
            self.location.col = self.getInputFromPort('column') - 1

        self.displayAndWait(SAHMSpatialOutputViewerCellWidget,
                            inputs)


    def find_file(self, model_dir, suffix):
        return [file_name for file_name in os.listdir(model_dir)
                                    if file_name.endswith(suffix)][0]

    def find_mds(self, model_dir):
        model_text = os.path.join(model_dir,
                            self.find_file(model_dir, "_output.txt"))

        f = open(model_text, 'rb')
        lines = f.read().splitlines()

        # grab the line after "Data:"
        result = [lines[i + 1] for i in range(len(lines))
                  if lines[i].startswith("Data:")][0].strip()

        if os.path.exists(result):
            return result
        else:
            raise RuntimeError('Valid input MDS file not found in Model text output.')

    def gen_points_shp(self, mds):
        """I couldn't figure out how to use a render on a shapefile
        instead I split the shapefile into three separate files for each
        class.
        This split only occurs once per mds though.
        """
        parentfolder, filename = os.path.split(mds)
        filenoext = os.path.splitext(filename)[0]
        shpfolder = os.path.join(parentfolder, "PointShapefiles")

        if not os.path.exists(shpfolder):
            os.mkdir(shpfolder)
        fileroot = os.path.join(shpfolder, filenoext)

        pregenerated = True
        for type in ["_pres", "_abs", "_backs"]:
            shape_file = fileroot +  type + ".shp"
            if not os.path.exists(shape_file):
                pregenerated = False

        if not pregenerated:
            mds_to_shape(mds, shpfolder)

        return fileroot


class SAHMSpatialOutputViewerCellWidget(QCellWidget):
    """

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

#        self.setAnimationEnabled(True)

        self.Frame = QtGui.QFrame()
        self.ui = Ui_Frame()
        self.ui.setupUi(self.Frame)

        self.toolBarType = SAHMSpatialViewerToolBar
        self.controlBarType = SAHMSpatialViewerToolBar

        self.layout().addWidget(self.Frame)


    def updateContents(self, inputs):
        """ updateContents(inputs: dictionary) -> None
        Update the widget contents based on the input data
        """

        self.canvas = qgis.gui.QgsMapCanvas()
        self.canvas.show()

        self.ui.legend_label.setText(QtCore.QString(inputs["model_tag"]))

        self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)

        self.canvas.setMapTool(self.toolPan)
        self.canvas.setWheelAction(2)
        self.canvas.setCanvasColor(QtCore.Qt.white)
        self.canvas.enableAntiAliasing(True)

        self.all_layers = {}
        self.add_raster(inputs["prob_map"], "prob_map")
        self.add_raster(inputs["bin_map"], "bin_map")
        self.add_raster(inputs["res_map"], "res_map")
        self.add_raster(inputs["mes_map"], "mes_map")
        self.add_raster(inputs["mod_map"], "mod_map")

        self.add_vector(inputs['pres_points'], "pres_points", '255,0,0')
        self.add_vector(inputs['abs_points'], "abs_points", '0,255,0')
        self.add_vector(inputs['backs_points'], "backs_points", '0,0,0')

        self.canvas.setExtent(self.all_layers["prob_map"].layer().extent())
        self.canvas.setLayerSet([self.all_layers["pres_points"],
                                 self.all_layers["abs_points"],
                           self.all_layers["prob_map"]])

        self.ui.map_frame.layout().addWidget(self.canvas)
        legend = self.create_legend_ramp("prob_map", None, (0, 1), 6)

        self.ui.legend.layout().addWidget(legend)
        # Update the new figure canvas
        self.update()

    def dumpToFile(self, filename):
        pass

    def saveToPDF(self, filename):
        pass

    def add_raster(self, path, tag):
        if os.path.exists(path):
            fileInfo = QtCore.QFileInfo(path)
            baseName = fileInfo.baseName()
            raster = qgis.core.QgsRasterLayer(path, baseName)
    
            if tag=="res_map":
                min_max = getrasterminmax(path)
            else:
                min_max = None
    
            self.set_color_ramp(tag, raster)
            qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster)
            self.all_layers[tag] = qgis.gui.QgsMapCanvasLayer(raster)
        else:
            print "The file " + path + " could not be found on the file system."
            print "   tag will not be enabled"

    def set_color_ramp(self, layer_type, raster, min_max=None):
        QgsColorRampShader = qgis.core.QgsColorRampShader


        if layer_type == "mod_map":
            #raster.setDrawingStyle(qgis.core.QgsRasterLayer.PalettedColor)
            raster.setDrawingStyle(qgis.core.QgsRasterLayer.SingleBandPseudoColor)
            raster.setColorShadingAlgorithm(qgis.core.QgsRasterLayer.PseudoColorShader)

            #raster.setColorShadingAlgorithm(qgis.core.QgsRasterLayer.ColorRampShader)
#            raster.setDrawingStyle(qgis.core.QgsRasterLayer.SingleBandGray)
            return None
        else:
            raster.setDrawingStyle(qgis.core.QgsRasterLayer.SingleBandPseudoColor)

        csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "ColorBreaks.csv"))
        csvfile = open(csv_file, "r")
        reader = csv.reader(csvfile)
        header = reader.next() #skip the header

        color_ramp_items = []
        for row in reader:
            if row[0] == layer_type:
                r, g, b = [int(val) for val in row[2:5]]
                cur_color = QtGui.QColor(r, g, b)
                cur_val = float(row[1])
                color_item = QgsColorRampShader.ColorRampItem(cur_val, cur_color)
                color_ramp_items.append(color_item)

        raster.setColorShadingAlgorithm(qgis.core.QgsRasterLayer.ColorRampShader)
        fcn = raster.rasterShader().rasterShaderFunction()
        fcn.setColorRampType(QgsColorRampShader.INTERPOLATED)
        fcn.setColorRampItemList(color_ramp_items)

        if hasattr(raster, "setCacheImage"): raster.setCacheImage(None)
        raster.triggerRepaint()

        qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster)

        csvfile.close()

        return None

    def create_legend_ramp(self, layer_type, raster, min_max, num_tags):
        legend = QtGui.QFrame()
        legend.setObjectName(QtCore.QString.fromUtf8("legend"))
        mainlayout = QtGui.QVBoxLayout(legend)
        mainlayout.setSpacing(0)
        mainlayout.setMargin(0)

        frame_colorbar = QtGui.QFrame(legend)
        frame_colorbar.setObjectName(QtCore.QString.fromUtf8("frame_colorbar"))
        layout_colorbar = QtGui.QHBoxLayout(frame_colorbar)
        layout_colorbar.setSpacing(0)
        layout_colorbar.setContentsMargins(-1, 2, -1, 0)

        frame_ticks = QtGui.QFrame(legend)
        frame_ticks.setFrameShape(QtGui.QFrame.StyledPanel)
        frame_ticks.setFrameShadow(QtGui.QFrame.Raised)
        frame_ticks.setObjectName(QtCore.QString.fromUtf8("frame_ticks"))
        layout_ticks = QtGui.QHBoxLayout(frame_ticks)
        layout_ticks.setSpacing(0)
        layout_ticks.setContentsMargins(-1, 0, -1, 0)

        frame_labels = QtGui.QFrame(legend)
        frame_labels.setObjectName(QtCore.QString.fromUtf8("frame_labels"))
        layout_labels = QtGui.QHBoxLayout(frame_labels)
        layout_labels.setSpacing(0)
        layout_labels.setContentsMargins(4, 0, 4, 0)

        csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "ColorBreaks.csv"))
        csvfile = open(csv_file, "r")
        reader = csv.reader(csvfile)
        header = reader.next() #skip the header

        color_ramp_items = []
        prev_color = None
        for row in reader:
            if row[0] == layer_type:
                cur_color = ", ".join(row[2:5])

                if prev_color:
                    color_label = QtGui.QLabel(frame_colorbar)
                    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(color_label.sizePolicy().hasHeightForWidth())
                    color_label.setSizePolicy(sizePolicy)
                    color_label.setMinimumSize(QtCore.QSize(0, 4))
                    stylesheet = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba("
                    stylesheet += prev_color
                    stylesheet += ", 255), stop:1 rgba("
                    stylesheet += cur_color
                    stylesheet += ", 255));"
                    color_label.setStyleSheet(QtCore.QString.fromUtf8(stylesheet))
                    color_label.setText(QtCore.QString.fromUtf8(""))
                    layout_colorbar.addWidget(color_label)

                prev_color = cur_color

        min = min_max[0]
        max = min_max[1]
        step = float(max - min) / num_tags
        curStep = min

        while curStep <= max:
            line = QtGui.QFrame(frame_ticks)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(line.sizePolicy().hasHeightForWidth())
            line.setSizePolicy(sizePolicy)
            line.setMinimumSize(QtCore.QSize(0, 4))
            line.setSizeIncrement(QtCore.QSize(0, 0))
            line.setFrameShadow(QtGui.QFrame.Plain)
            line.setFrameShape(QtGui.QFrame.VLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            line.setObjectName(QtCore.QString.fromUtf8("line"))
            layout_ticks.addWidget(line)
            spacerItem = QtGui.QSpacerItem(133, 2, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
            layout_ticks.addItem(spacerItem)

            lbl = QtGui.QLabel(frame_labels)
            lbl.setMinimumSize(QtCore.QSize(0, 10))
            txt = "%.1f" %curStep
            lbl.setText(QtCore.QString.fromUtf8(txt))
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            #lbl.setObjectName(QtCore.QString.fromUtf8("lbl"))
            layout_labels.addWidget(lbl)
            spacerItem2 = QtGui.QSpacerItem(5, 5, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
            layout_labels.addItem(spacerItem2)

            curStep += step

        layout_ticks.removeItem(spacerItem)
        layout_labels.removeItem(spacerItem2)

        mainlayout.addWidget(frame_colorbar)
        mainlayout.addWidget(frame_ticks)
        mainlayout.addWidget(frame_labels)
        return legend


    def add_vector(self, path, tag, strcolor):
        fileInfo = QtCore.QFileInfo(path)
        baseName = fileInfo.baseName()
        points_layer = qgis.core.QgsVectorLayer(path, baseName, "ogr")

        props = {'color':strcolor, 'radius':'3' }
        s = qgis.core.QgsMarkerSymbolV2.createSimple(props)

        points_layer.setRendererV2( qgis.core.QgsSingleSymbolRendererV2( s ) )

        qgis.core.QgsMapLayerRegistry.instance().addMapLayer(points_layer)
        self.all_layers[tag] = qgis.gui.QgsMapCanvasLayer(points_layer)

#
#def update_displayed_layers(cellWidget):
#    pass
#
#
##        [qgis.gui.QgsMapCanvasLayer(layer) for layer in layers]

#    layer = cellWidget.cur_layers[layer]
#    layers = cellWidget.canvas.layers()
#
#    if visible:
#        layers.insert(0, layer.layer())
#    else:
#        layers.remove(layer.layer())
#
#    cellWidget.canvas.setLayerSet(layerset)
#    cellWidget.canvas.repaint()


class ViewLayerAction(QtGui.QAction):
    def __init__(self, action_dict, parent=None):
        icon = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), "Images", action_dict["icon"]))
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(icon),
                               action_dict["label"],
                               parent)
        self.setCheckable(True)
        self.setChecked(action_dict["checked"])
        self.tag = action_dict["tag"]
        self.group = action_dict["group"]

    def triggeredSlot(self, checked=False):
#        cellWidget = self.toolBar.getSnappedWidget()
        self.toggleOthers()
        self.displayLayer()

    def toggleOthers(self):
        for action in self.toolBar.actions():
            if "group" in dir(action) and \
                action.group == self.group and \
                action.tag <> self.tag:
                action.setChecked(False)

    def displayLayer(self):
        cellWidget = self.toolBar.getSnappedWidget()

        all_layers = cellWidget.all_layers
        layerset = []
        for action in self.toolBar.actions():
            if action.isChecked() and all_layers.has_key(action.tag):
                layer = all_layers[action.tag]
                layerset.append(qgis.gui.QgsMapCanvasLayer(layer))

        cellWidget.canvas.setLayerSet(layerset)
        cellWidget.canvas.repaint()


class SAHMSpatialViewerToolBar(QCellToolBar):
    """
    The toolbar that allows users to toggle layers on and off
    in the widget

    """
    def createToolBar(self):
        """ createToolBar() -> None
        This will get call initiallly to add customizable widgets

        """
        sw = self.getSnappedWidget()
        
        actions = [{"tag":"pres_points", "icon":"RedPoints.png",
                     "checked":True, "label":"Display presence points",
                     "group":"pres_points"},
                   {"tag":"abs_points", "icon":"GreenPoints.png",
                     "checked":True, "label":"Display absence points",
                     "group":"abs_points"},
                   {"tag":"backs_points", "icon":"BlackPoints.png",
                     "checked":False, "label":"Display background points",
                     "group":"backs_points"},
                   {"tag":"prob_map", "icon":"ProbMap.png",
                     "checked":True, "label":"Display probability map",
                     "group":"Grids"},
                   {"tag":"bin_map", "icon":"BinMap.png",
                     "checked":False, "label":"Display binary map",
                     "group":"Grids"},
                   {"tag":"res_map", "icon":"ResMap.png",
                     "checked":False, "label":"Display residuals map",
                     "group":"Grids"},
                   {"tag":"mes_map", "icon":"MesMap.png",
                     "checked":False, "label":"Display Multivariate Environmental Similarity Surface (Mess) map",
                     "group":"Grids"},
                    {"tag":"mod_map", "icon":"ModMap.png",
                     "checked":False, "label":"Display Most Dissimilar Variable (MoD) map",
                     "group":"Grids"}]


        for action_dict in actions:
            self.appendAction(ViewLayerAction(action_dict, self))
            
    def updateToolBar(self):
        QCellToolBar.updateToolBar(self)
        sw = self.getSnappedWidget()
        for action in self.actions():
            if type(action) == ViewLayerAction:
                #disenable all action refering to data we don't have
                action.setEnabled(action.tag in sw.all_layers)

        