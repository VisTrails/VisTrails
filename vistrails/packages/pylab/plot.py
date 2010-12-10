############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
""" This file describe the plot script module and its configuration
widget

"""
from core.modules.basic_modules import PythonSource
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.source_configure import SourceConfigurationWidget
from core.modules.python_source_configure import PythonEditor
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
