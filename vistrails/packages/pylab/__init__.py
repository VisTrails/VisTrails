############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
"""Matplotlib/pylab package for VisTrails.

This package wrap Matplotlib/pylab to provide a plotting tool for
VisTrails. We are going to use the 'Qt4Agg' backend of the library.

"""
import core.modules
import core.modules.module_registry
from core.modules.basic_modules import File, String, Boolean
from core.modules.vistrails_module import Module, NotCacheable, InvalidOutput
from plot import MplPlot, MplPlotConfigurationWidget
from core.modules.module_configure import PythonSourceConfigurationWidget
import pylab
import time
import urllib
        
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

    def compute(self):
        """ compute() -> None        
        Read all plot inputs and draw the figure. Then either passing
        the figure manager to a SpreadsheetCell or save the image to file

        """
        pylab.figure()
        scripts = self.forceGetInputListFromPort('Script')
        for script in scripts:
            if script:
                exec ('from pylab import *\n' + urllib.unquote(script))
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

################################################################################

def initialize(*args, **keywords):    

    reg = core.modules.module_registry
    reg.setCurrentPackageName('Matplotlib/pylab')
    
    reg.addModule(MplPlot, None, MplPlotConfigurationWidget)
    reg.addInputPort(MplPlot, 'source', String, True)
    reg.addOutputPort(MplPlot, 'source', String)
    
    reg.addModule(MplFigure)
    reg.addInputPort(MplFigure, 'Script', String)
    reg.addOutputPort(MplFigure, 'FigureManager', MplFigureManager)
    reg.addOutputPort(MplFigure, 'File', File)
    
    reg.registry.addModule(MplFigureManager)
    
    # Register a figure cell type if the spreadsheet is up
    if reg.registry.hasModule('SpreadsheetCell'):
        from figure_cell import MplFigureCell
        reg.registry.addModule(MplFigureCell)
        reg.registry.addInputPort(MplFigureCell, 'FigureManager', MplFigureManager)

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('spreadsheet'):
        return ['spreadsheet']
    else:
        return []
    
def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('matplotlib'):
        raise core.requirements.MissingRequirement('matplotlib')
    if not core.requirements.python_module_exists('pylab'):
        raise core.requirements.MissingRequirement('pylab')
    import matplotlib
    matplotlib.use('Qt4Agg')
    import pylab
