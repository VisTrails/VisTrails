###############################################################################
##
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

import urllib

from vistrails.core.modules.basic_modules import CodeRunnerMixin
from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module, NotCacheable, ModuleError

from vistrails.core.bundles import py_import
try:
    mpl_dict = {'pip': 'matplotlib',
                'linux-debian': 'python-matplotlib',
                'linux-ubuntu': 'python-matplotlib',
                'linux-fedora': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg', warn=False)
    pylab = py_import('pylab', mpl_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)

################################################################################

class MplProperties(Module):
    _output_ports = [("self", "(MplProperties)")]
    
    def update_props(self, objs):
        # must implement in subclass
        pass
        

#base class for 2D plots
class MplPlot(NotCacheable, Module):
    # _input_ports = [("subfigRow", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]}),
    #                 ("subfigCol", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]})]
    _output_ports = [("self", "(MplPlot)")]

    def __init__(self):
        Module.__init__(self)
        self.figInstance = None

    def set_figure(self, fig):
        if self.figInstance is None:
            self.figInstance = fig
        else:
            raise ModuleError(self,
                              "matplotlib plots can only be in one figure")

    def compute(self):
        matplotlib.pyplot.figure(self.figInstance.number)

class MplSource(CodeRunnerMixin, MplPlot):
    """
    MplSource is a module similar to PythonSource. The user can enter
    Matplotlib code into this module. This will then get connected to
    MplFigure to draw the figure. Please note that, codes entered in
    this module should limit to subplot() scope only. Using
    Figure-level commands, e.g. figure() or show(), the result will be
    unknown
    
    """
    _input_ports = [('source', '(basic:String)')]

    def compute(self):
        """ compute() -> None
        """
        source = self.getInputFromPort('source')
        s = ('from pylab import *\n'
             'from numpy import *\n' +
             'figure(%d)' % self.figInstance.number +
             urllib.unquote(source))

        self.run_code(s, use_input=True, use_output=True)

class MplFigure(Module):
    # _input_ports = [("addPlot", "(MplPlot)"),
    #                 ("numSubfigRows", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]}),
    #                 ("numSubfigCols", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]}),
    #                 ]
    _input_ports = [("addPlot", "(MplPlot)"),
                    ("axesProperties", "(MplAxesProperties)"),
                    ("figureProperties", "(MplFigureProperties)"),
                    ("setLegend", "(MplLegend)")]

    _output_ports = [("file", "(basic:File)"),
                     ("self", "(MplFigure)")]

    def __init__(self):
        Module.__init__(self)
        self.figInstance = None

    def updateUpstream(self):
        # Create a figure
        if self.figInstance is None:
            self.figInstance = pylab.figure()
        pylab.hold(True)

        # Set it on the plots
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                connector.obj.set_figure(self.figInstance)

        # Now we can run upstream modules
        super(MplFigure, self).updateUpstream()

    def compute(self):
        plots = self.getInputListFromPort("addPlot")

        if self.hasInputFromPort("figureProperties"):
            figure_props = self.getInputFromPort("figureProperties")
            figure_props.update_props(self.figInstance)
        if self.hasInputFromPort("axesProperties"):
            axes_props = self.getInputFromPort("axesProperties")
            axes_props.update_props(self.figInstance.gca())
        if self.hasInputFromPort("setLegend"):
            legend = self.getInputFromPort("setLegend")
            self.figInstance.gca().legend()

        #FIXME write file out if File port is attached!

        self.setResult("self", self)

class MplContourSet(Module):
    pass

class MplQuadContourSet(MplContourSet):
    pass
        
_modules = [(MplProperties, {'abstract': True}),
            (MplPlot, {'abstract': True}), 
            (MplSource, {'configureWidgetType': \
                             ('vistrails.packages.matplotlib.widgets',
                              'MplSourceConfigurationWidget')}),
            MplFigure,
            MplContourSet,
            MplQuadContourSet]
