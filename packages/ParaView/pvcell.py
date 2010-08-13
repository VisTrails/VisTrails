from PyQt4 import QtCore
from core.modules.module_registry import get_module_registry
from packages.vtk.vtkcell import QVTKWidget
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget
from PVBase import PVModule, PVRenderable
import paraview.simple as pvsp
import paraview.servermanager as pvsm
import vtk

class PVCell(SpreadsheetCell):
    def __init__(self):
        SpreadsheetCell.__init__(self)
        self.cellWidget = None
    
    def compute(self):
        """ compute() -> None
        Dispatch the vtkRenderer to the actual rendering widget
        """
        proxies = self.forceGetInputListFromPort('Proxy')
        self.cellWidget = self.displayAndWait(QParaViewWidget, (proxies,))

class QParaViewWidget(QVTKWidget):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QVTKWidget.__init__(self, parent, f)
        self.view = None
        self.reps = []
    
    def updateContents(self, inputPorts):
        for rep in self.reps:
            self.view.SMProxy.RemoveRepresentation(rep.SMProxy)
            self.view.Representations.remove(rep)
        
        if self.view==None:
            self.view = pvsm.CreateRenderView()
            renWin = self.view.GetRenderWindow()
            self.SetRenderWindow(renWin)
            iren = renWin.GetInteractor()
            iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        (proxies, ) = inputPorts
        self.reps = []
        for p in proxies:
            rep = pvsp.GetDisplayProperties(p.pvInstance, self.view)

            ar = rep.Input.PointData.GetArray(0).Name
#            print "SCALAR RANGE", rep.Input.PointData.ScalarRange
            rep.Visibility = 1
            rep.ColorAttributeType = "POINT_DATA"
            rep.Representation = p.pvMode
            if p.pvMode == "Volume":
                rep.ScalarOpacityFunction = p.pvolut
            else:
                rep.Opacity = p.alpha
#            rep.ScalarOpacityFunction = p.pvolut
            rep.LookupTable = p.pvclut
            rep.ColorArrayName = ar
            self.reps.append(rep)

        self.view.ResetCamera()
        self.view.StillRender()

        QCellWidget.updateContents(self, inputPorts)


    def deleteLater(self):
        QCellWidget.deleteLater(self)

        

def registerSelf():
    registry = get_module_registry()
    registry.add_module(PVCell)
    registry.add_input_port(PVCell, "Location", CellLocation)
    registry.add_input_port(PVCell, "Proxy", PVRenderable)
    registry.add_output_port(PVCell, "self", PVCell)
