from PyQt4 import QtCore, QtGui
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.modules.basic_modules import Constant
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_event import DisplayCellEvent
#from cdatwrap.coreappwrap import VCSQtManager
import vcs
import genutil
import cdutil
import time
import api
import re
import MV2

""" This file contains all of the classes related to the Vistrails Modules (the
boxes).  Eventually Variable and GraphicsMethod should be replaced by generating
the proper graphics method, cdms2, MV2, etc... modules """

# Index into the VCSQtManager window array so we can communicate with the
# C++ Qt windows which the plots show up in.  If this number is no longer
# consistent with the number of C++ Qt windows due to adding or removing
# vcs.init() calls, then when you plot, it will plot into a
# separate window instead of in the cell and may crash.
windowIndex = 1 

class Variable(Module):
    """ Get the updated transient variable """
    
    def compute(self):
        # *** IMPORTANT ***
        # Once someone figures out how to pass the tvariable object, to this
        # module none of the computation in this method is necessary 
        
        # Check ports
        if not self.hasInputFromPort('cdmsfile'):
            raise ModuleError(self, "'cdmsfile' is mandatory.")
        if not self.hasInputFromPort('id'):
            raise ModuleError(self, "'id' is mandatory.")

        # Get input from ports
        cdmsfile = self.get_input('cdmsfile')
        id = self.get_input('id')
        axes = self.forceGetInputFromPort('axes') # None if no input
        axesOperations = self.forceGetInputFromPort('axesOperations') # None if no input

        # Get the variable
        varType = self.getVarType(id, cdmsfile)
        if (varType == 'variable'):
            var = cdmsfile.__call__(id)
        elif (varType == 'axis'):
            varID = self.getAxisID(id)            
            axis = getattr(cdmsfile, 'axes')[varID]
            var = MV2.array(axis)
            var.setAxis(0, axis)
        elif (varType == 'weighted-axis'):
            varID, axisID = self.getVarAndAxisID(id)
            var = cdmsfile.__call__(varID)            
            var = genutil.getAxisWeightByName(var, axisID)
            var.id = varID +'_' + axisID + '_weight'
        else:
            var = None

        # Eval the variable with the axes
        if axes is not None and var is not None:
            try:
                kwargs = eval(axes)
                var = var(**kwargs)
            except:
                raise ModuleError(self, "Invalid 'axes' specification", axes)

        # Apply axes ops to the variable
        if axesOperations is not None:
            var = self.applyAxesOperations(var, axesOperations)

        self.setResult('variable', var)

    def applyAxesOperations(self, var, axesOperations):
        """ Apply axes operations to update the slab """
        try:
            axesOperations = eval(axesOperations)
        except:
            raise TypeError("Invalid string 'axesOperations'")

        for axis in list(axesOperations):
            if axesOperations[axis] == 'sum':
                var = cdutil.averager(var, axis="(%s)" % axis, weight='equal',
                                      action='sum')
            elif axesOperations[axis] == 'avg':
                var = cdutil.averager(var, axis="(%s)" % axis, weight='equal')
            elif axesOperations[axis] == 'wgt':
                var = cdutil.averager(var, axis="(%s)" % axis)
            elif axesOperations[axis] == 'gtm':
                var = genutil.statistics.geometricmean(var, axis="(%s)" % axis)
            elif axesOperations[axis] == 'std':
                var = genutil.statistics.std(var, axis="(%s)" % axis)                
                
        return var

    def getVarType(self, varID, file):
        if varID in list(getattr(file, 'variables')):
            return 'variable'
        elif varID in list(getattr(file, 'axes')):
            return 'axis'
        elif re.compile('(.+)(_)(.+)(_)axis').match(varID):
            return 'axis'
        elif re.compile('(.+)(_)(.+)(_)weight').match(varID):
            return 'weighted-axis'        

    def getVarAndAxisID(self, varID):
        """ Get the varID and axisID from a string with format:
        varID_axisID_weight """
        
        match = re.compile('(.+)(_)(.+)(_)(weight)').match(varID)
        if match:
            return (match.group(1), match.group(3))

        return None

    def getAxisID(self, varID):
        """ Get the axisID from a string with format: varID_axisID_axis """

        match = re.compile('(.+)(_)(.+)(_)(axis)').match(varID)
        if match:
            return match.group(3)

        return varID

class Quickplot(Variable):
    """ Quickplot is identical to Variable except we will only have a single
    quickplot module in a pipeline. """

    def foo(self):
        return

class GraphicsMethod(Module, NotCacheable):
    """ GraphicsMethod initializes the vcs canvas and gets the graphics method
    and modify it's attributes """
    
    def compute(self):
        # Check required input ports
        if not self.hasInputFromPort('gmName'):
            return
        if not self.hasInputFromPort('plotType'):
            return
        if not self.hasInputFromPort('slab1'):
            return
        
        # Get required input
        gmName = self.get_input('gmName')
        plotType = self.get_input('plotType')

        # GraphicsMethod doesn't need slab1/slab2 as input.  It can be passed
        # directly to CDATCell but I pass it to graphics method so it looks
        # nicer in the pipeline.
        slab1 = self.get_input('slab1')
        if self.hasInputFromPort('slab2'):
            self.setResult('slab2', self.get_input('slab2'))
                           
        # Initialize the canvas and get the graphics method
        canvas = vcs.init()
        gm = canvas.get_gm(plotType.lower(), gmName)

        # Modify the graphics method's attributes
        if self.hasInputFromPort('color_1'):
            gm.color_1 = self.get_input('color_1')
        if self.hasInputFromPort('color_2'):
            gm.color_2 = self.get_input('color_2')
        if self.hasInputFromPort('level_1'):
            gm.level_1 = self.get_input('level_1')
        if self.hasInputFromPort('level_2'):
            gm.level_2 = self.get_input('level_2')
        # TODO: more gm attributes ...

        # Add canvas / slab to output Ports
        self.setResult('slab1', slab1)
        self.setResult('canvas', canvas)

class CDATCell(SpreadsheetCell, NotCacheable):
    def __init__(self):
        SpreadsheetCell.__init__(self)
        self.cellWidget = None
    
    def compute(self):
        """ compute() -> None
        Dispatch the vtkRenderer to the actual rendering widget
        """
        # Check required input ports
        if self.hasInputFromPort('canvas'):
            canvas = self.get_input('canvas')
        else:
            self.cellWidget = self.displayAndWait(QCDATWidget, (None,))
            self.setResult('canvas', self.cellWidget.canvas)
            return
        self.setResult('canvas', canvas)
        if not self.hasInputFromPort('gmName'):
            return
        if not self.hasInputFromPort('plotType'):
            return
        if not self.hasInputFromPort('slab1'):
            return
        if not self.hasInputFromPort('template'):
            return

        # Build up the argument list
        args = []
        slab1 = self.get_input('slab1')
        args.append(self.get_input('slab1'))
        if self.hasInputFromPort('slab2'):
            args.append(self.get_input('slab2'))
        args.append(self.get_input('template'))
        args.append(self.get_input('plotType'))
        args.append(self.get_input('gmName'))

        # Build up plot keyword args ...
        kwargs = {}
        if self.hasInputFromPort('continents'):
            kwargs['continents'] = self.get_input('continents')
        
        # Set the cell row / col
        self.location = CellLocation()
        if self.hasInputFromPort('row'):
            self.location.row = self.get_input('row')
        if self.hasInputFromPort('col'):
            self.location.col = self.get_input('col')

        # Plot into the cell
        inputPorts = (canvas, args, kwargs)
        self.displayAndWait(QCDATWidget, inputPorts)        

class QCDATWidget(QCellWidget):
    """ QCDATWidget is the spreadsheet cell widget where the plots are displayed.
    The widget interacts with the underlying C++, VCSQtManager through SIP.
    This enables QCDATWidget to get a reference to the Qt MainWindow that the
    plot will be displayed in and send signals (events) to that window widget.
    """
    
    def __init__(self, parent=None):
        QCellWidget.__init__(self, parent)
        self.window = None        
        self.canvas =  None
        self.windowIndex = self.getWindowIndex() #index to get QT Window from VCSQtManager

    def getWindowIndex(self):
        """ Return the index into the VCSQtManager's array of Qt Windows which
        plots will be displayed in.
        """
        global windowIndex

        windowIndex += 1
        maxWindows = 8
        if windowIndex > maxWindows:
            windowIndex = 1
        return windowIndex

    def updateContents(self, inputPorts):
        """ Get the vcs canvas, setup the cell's layout, and plot """        
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
        spreadsheetWindow.setUpdatesEnabled(False)

        # Set the canvas
        self.canvas = inputPorts[0]
        if self.canvas is None:
            self.canvas = vcs.init()
        self.canvas.clear()

        # Place the mainwindow that the plot will be displayed in, into this
        # cell widget's layout
        self.window = VCSQtManager.window(self.windowIndex)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.window)
        self.setLayout(layout)        

        # Plot
        if len(inputPorts) > 2:
            args = inputPorts[1]
            kwargs = inputPorts[2]
            self.canvas.plot(*args, **kwargs)

        spreadsheetWindow.setUpdatesEnabled(True)

    def deleteLater(self):
        """ deleteLater() -> None        
        Make sure to free render window resource when
        deallocating. Overriding PyQt deleteLater to free up
        resources
        """
        self.canvas = None
        QCellWidget.deleteLater(self)    

