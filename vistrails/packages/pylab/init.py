###############################################################################
##
## Copyright (C) 2011-2012, NYU-Poly.
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
##  - Neither the name of the University of Utah nor the names of its 
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
import vistrails.core.modules
import vistrails.core.modules.module_registry
from vistrails.core import debug
from vistrails.core.modules.basic_modules import Boolean, Color, File, Float, \
    Integer, String
from vistrails.core.modules.vistrails_module import Module, NotCacheable, InvalidOutput
from plot import MplPlot, MplPlotConfigurationWidget
import time
import urllib

from vistrails.core.bundles import py_import
try:
    mpl_dict = {'linux-ubuntu': 'python-matplotlib',
                'linux-fedora': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg', warn=False)
    pylab = py_import('pylab', mpl_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)

################################################################################

class MplFigureManager(Module):
    """
    MplFigureManager is the figure viewer available from
    Matplotlib. It supports pan/zoom, save and other plot
    interactions. It can be embedded in different backend. We are
    using Qt4Agg backend in this package.
    
    """

    def __init__(self):
        """ MplFigureManager() -> MplFigureManager
        Init the class as a storage structure
        
        """
        Module.__init__(self)
        self.figManager = None

class MplFigure(NotCacheable, Module):
    """
    MplFigure is a module representing a single figure (type Figure)
    in Matplotlib. It receive multiple MplPlot inputs
    
    """
    def update(self):
        """ update() -> None        
        Interfere into the update process to set the appropriate
        figure command before going upstream to the MplPlot
        
        """
        pylab.figure()
        Module.update(self)

    def compute(self):
        """ compute() -> None        
        Either passing the figure manager to a SpreadsheetCell or save
        the image to file

        """
        noOutput = True
        if self.outputPorts.has_key('FigureManager'):
            mfm = MplFigureManager()
            mfm.figManager = pylab.get_current_fig_manager()
            self.setResult('FigureManager', mfm)
            noOutput = False
        self.setResult('File', InvalidOutput)
        if 'File' in self.outputPorts:
            f = self.interpreter.filePool.create_file(suffix='.png')
            pylab.savefig(f.name)
            self.setResult('File', f)
            noOutput = False
        if noOutput:
            pylab.show()

class MplHistogram(NotCacheable, Module):
    _input_ports = [('columnData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('bins', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        data = [float(x) for x in self.getInputFromPort('columnData')]
        fig = pylab.figure()
        pylab.setp(fig, facecolor='w')
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xlabel'):
            pylab.xlabel(self.getInputFromPort('xlabel'))
        if self.hasInputFromPort('ylabel'):
            pylab.ylabel(self.getInputFromPort('ylabel'))
        if self.hasInputFromPort('bins'):
            bins = self.getInputFromPort('bins')
        else:
            bins = 10
        if self.hasInputFromPort('facecolor'):
            color = self.getInputFromPort('facecolor').tuple
        else:
            color = 'b'
        pylab.hist(data, bins, facecolor=color)
        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")

class MplScatterplot(NotCacheable, Module):
    _input_ports = [('xData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('yData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        x_data = [float(x) for x in self.getInputFromPort('xData')]
        y_data = [float(x) for x in self.getInputFromPort('yData')]
        fig = pylab.figure()
        # pylab.setp(fig, facecolor='w')
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xlabel'):
            pylab.xlabel(self.getInputFromPort('xlabel'))
        if self.hasInputFromPort('ylabel'):
            pylab.ylabel(self.getInputFromPort('ylabel'))
        if self.hasInputFromPort('facecolor'):
            color = self.getInputFromPort('facecolor').tuple
        else:
            color = 'r'
        pylab.scatter(x_data, y_data, marker='s', facecolor=color)
        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")

class NumPyArray(Module):
    """
    A Numpy Array, that can be loaded from a file.

    This is not currently used by the other modules that accept lists instead,
    but might be useful someday. It is also used by the DAT plot.
    """
    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'),
                    ('datatype', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('value', '(edu.utah.sci.vistrails.matplotlib:NumPyArray)')]

    FORMAT_MAP = dict(
          int8 = pylab.int8,
         uint8 = pylab.uint8,
         int16 = pylab.int16,
        uint16 = pylab.uint16,
         int32 = pylab.int32,
        uint32 = pylab.uint32,
         int64 = pylab.int64,
        uint64 = pylab.uint64,

         float32 = pylab.float32,
         float64 = pylab.float64,

         complex64 = pylab.complex64,
        complex128 = pylab.complex128,
    )

    def compute(self):
        if self.hasInputFromPort('datatype'):
            dtype = NumPyArray.FORMAT_MAP[self.getInputFromPort('datatype')]
        else:
            dtype = pylab.float32
        self.array = pylab.fromfile(self.getInputFromPort('file').name, dtype)
        self.setResult('value', self)

################################################################################

def initialize(*args, **keywords):    

    reg = vistrails.core.modules.module_registry.get_module_registry()
    
    reg.add_module(MplPlot, configureWidgetType=MplPlotConfigurationWidget)
#    reg.add_input_port(MplPlot, 'source', String, True)
    reg.add_input_port(MplPlot, 'Hide Toolbar', Boolean, True)
    reg.add_output_port(MplPlot, 'source', String)
    
    reg.add_module(MplFigureManager)

    reg.add_module(MplFigure)
    reg.add_input_port(MplFigure, 'Script', String)
    reg.add_output_port(MplFigure, 'FigureManager', MplFigureManager)
    reg.add_output_port(MplFigure, 'File', File)
    
    # Register a figure cell type if the spreadsheet is up
    if reg.has_module('edu.utah.sci.vistrails.spreadsheet',
                               'SpreadsheetCell'):
        from figure_cell import MplFigureCell
        reg.add_module(MplFigureCell)
        reg.add_input_port(MplFigureCell, 'FigureManager', MplFigureManager)

_modules = [MplScatterplot, MplHistogram, NumPyArray]

###############################################################################

# Define DAT plots
try:
    from dat.packages import Plot, DataPort, ConstantPort, Variable, \
        FileVariableLoader, VariableOperation, OperationArgument, \
        translate, derive_varname
except ImportError:
    pass # We are not running DAT; skip plot/variable/operation definition
else:
    from PyQt4 import QtGui

    _ = translate('packages.pylab')

    # Builds a DAT variable from a data file
    def build_variable(filename, dtype):
        var = Variable(type=NumPyArray)
        # We use the high-level interface to build the variable pipeline
        mod = var.add_module(NumPyArray)
        mod.add_function('file', File, filename)
        mod.add_function('datatype', String, dtype)
        # We select the 'value' output port of the NumPyArray module as the
        # port that will be connected to plots when this variable is used
        var.select_output_port(mod, 'value')
        return var

    ########################################
    # Defines a plot from a subworkflow file
    #
    _plots = [
        Plot(name="Matplotlib histogram",
             subworkflow='{package_dir}/dat-plots/histogram.xml',
             description=_("Build a histogram out of a numpy array"),
             ports=[
                     DataPort(name='np_array', type=NumPyArray,
                              multiple_values=True),
                     ConstantPort(name='xlabel', type=String, optional=True),
                     ConstantPort(name='ylabel', type=String, optional=True),
                     ConstantPort(name='color', type=Color, optional=True)])
    ]

    ########################################
    # Defines a variable loader
    #
    class NumPyArrayLoader(FileVariableLoader):
        """Loads a NumPy array using numpy:fromfile().
        """
        FORMATS = [
                ("%s (%s)" % (_("byte"), 'numpy.int8'),
                 'int8'),
                ("%s (%s)" % (_("unsigned byte"), 'numpy.uint8'),
                 'uint8'),
                ("%s (%s)" % (_("short"), 'numpy.int16'),
                 'int16'),
                ("%s (%s)" % (_("unsigned short"), 'numpy.uint16'),
                 'uint16'),
                ("%s (%s)" % (_("32-bit integer"), 'numpy.int32'),
                 'int32'),
                ("%s (%s)" % (_("32-bit unsigned integer"), 'numpy.uint32'),
                 'uint32'),
                ("%s (%s)" % (_("64-bit integer"), 'numpy.int64'),
                 'int64'),
                ("%s (%s)" % (_("64-bit unsigned integer"), 'numpy.uint64'),
                 'uint64'),

                ("%s (%s)" % (_("32-bit floating number"), 'numpy.float32'),
                 'float32'),
                ("%s (%s)" % (_("64-bit floating number"), 'numpy.float64'),
                 'float64'),
                ("%s (%s)" % (_("128-bit floating number"), 'numpy.float128'),
                 'float128'),

                ("%s (%s)" % (_("64-bit complex number"), 'numpy.complex64'),
                 'complex64'),
                ("%s (%s)" % (_("128-bit complex number"), 'numpy.complex128'),
                 'complex128'),
                ("%s (%s)" % (_("256-bit complex number"), 'numpy.complex256'),
                 'complex128'),
        ]

        @classmethod
        def can_load(cls, filename):
            return filename.lower().endswith('.dat')

        def __init__(self, filename):
            FileVariableLoader.__init__(self)
            self.filename = filename
            self._varname = derive_varname(filename, remove_ext=True,
                                          remove_path=True, prefix="nparray_")

            self._format_field = QtGui.QComboBox()
            for label, dtype in NumPyArrayLoader.FORMATS:
                self._format_field.addItem(label)

            layout = QtGui.QFormLayout()
            layout.addRow(_("Data &format:"), self._format_field)
            self.setLayout(layout)

        def load(self):
            return build_variable(
                    self.filename,
                    NumPyArrayLoader.FORMATS[
                            self._format_field.currentIndex()][1])

        def get_default_variable_name(self):
            return self._varname

    _variable_loaders = {
            NumPyArrayLoader: _("NumPy array"),
    }

    ########################################
    # Defines variable operations
    #
    _variable_operations = [
        VariableOperation(
            '*',
            subworkflow='{package_dir}/dat-operations/scale_array.xml',
            args=[
                OperationArgument('array', NumPyArray),
                OperationArgument('num', Float),
            ],
            return_type=NumPyArray,
            symmetric=True),
    ]
