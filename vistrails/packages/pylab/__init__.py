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
"""Matplotlib package for VisTrails.

This package wrap Matplotlib to provide a plotting tool for
VisTrails. We are going to use the 'Qt4Agg' backend of the library.

"""
import core.modules
import core.modules.module_registry
from core.modules.basic_modules import File, String, Boolean
from core.modules.vistrails_module import Module, NotCacheable, InvalidOutput
from plot import MplPlot, MplPlotConfigurationWidget
from core.modules.module_configure import PythonSourceConfigurationWidget
import time
import urllib

name = 'matplotlib'
version = '0.9.0'
identifier = 'edu.utah.sci.vistrails.matplotlib'

from core.bundles import py_import
try:
    mpl_dict = {'linux-ubuntu': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg')
    pylab = py_import('pylab', mpl_dict)
except Exception, e:
    print "EXCEPTION!"
    print e

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

################################################################################

def initialize(*args, **keywords):    

    reg = core.modules.module_registry
    
    reg.add_module(MplPlot, configureWidgetType=MplPlotConfigurationWidget)
    reg.add_input_port(MplPlot, 'source', String, True)
    reg.add_output_port(MplPlot, 'source', String)
    
    reg.add_module(MplFigure)
    reg.add_input_port(MplFigure, 'Script', String)
    reg.add_output_port(MplFigure, 'FigureManager', MplFigureManager)
    reg.add_output_port(MplFigure, 'File', File)
    
    reg.registry.add_module(MplFigureManager)
    
    # Register a figure cell type if the spreadsheet is up
    if reg.registry.has_module('edu.utah.sci.vistrails.spreadsheet',
                               'SpreadsheetCell'):
        from figure_cell import MplFigureCell
        reg.registry.add_module(MplFigureCell)
        reg.registry.add_input_port(MplFigureCell, 'FigureManager', MplFigureManager)

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
        return ['edu.utah.sci.vistrails.spreadsheet']
    else:
        return []
    
def package_requirements():    
    import core.requirements
    if not core.requirements.python_module_exists('matplotlib'):
        raise core.requirements.MissingRequirement('matplotlib')
    if not core.requirements.python_module_exists('pylab'):
        raise core.requirements.MissingRequirement('pylab')
