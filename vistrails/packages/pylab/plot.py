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
""" This file describe the plot script module and its configuration
widget

"""
from core.modules.basic_modules import PythonSource
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
from gui.modules.module_configure import StandardModuleConfigurationWidget
from gui.modules.python_source_configure import PythonEditor
from gui.modules.source_configure import SourceConfigurationWidget
import urllib

############################################################################

class MplPlot(PythonSource):
    """
    MplPlot is a module similar to PythonSource. The user can enter
    Matplotlib code into this module. This will then get connected to
    MplFigure to draw the figure. Please note that, codes entered in
    this module should limit to subplot() scope only. Using
    Figure-level commands, e.g. figure() or show(), the result will be
    unknown
    
    """

    def compute(self):
        """ compute() -> None        
        We postpone the computation of the plot script to the
        MplFigure module for a unified execution.
        
        """
        hide_toolbar = self.forceGetInputFromPort("Hide Toolbar", False)
        if self.hasInputFromPort('source'):
            if self.outputPorts.has_key('source'):
                source = self.getInputFromPort('source')
                s = ('from pylab import *\n' +
                     'from numpy import *\n' +
                     urllib.unquote(source))
                if hide_toolbar:
                    s += '\nget_current_fig_manager().toolbar.hide()\n'
                self.run_code(s, use_input=True, use_output=True)

class MplPlotConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        """ MplPlotConfigurationWidget(module: Module,
                                       controller: VistrailController,
                                       parent: QWidget)
                                       -> MplPlotConfigurationWidget
        Setup the dialog to similar to PythonSource but with a
        different name
        
        """
        SourceConfigurationWidget.__init__(self, module, controller, 
                                           PythonEditor, True, False, parent)
