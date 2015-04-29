# ****************************************************************************
# 
# ALPS Project: Algorithms and Libraries for Physics Simulations
# 
# ALPS Libraries
# 
# Copyright (C) 1994-2009 by Bela Bauer <bauerb@phys.ethz.ch>
# 
# This software is part of the ALPS libraries, published under the ALPS
# Library License; you can use, redistribute it and/or modify it under
# the terms of the license, either version 1 or (at your option) any later
# version.
#  
# You should have received a copy of the ALPS Library License along with
# the ALPS Libraries; see the file LICENSE.txt. If not, the license is also
# available from http://alps.comp-phys.org/.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT 
# SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE 
# FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
# 
# ****************************************************************************

from vistrails.core.modules.vistrails_module import Module
from vistrails.packages.matplotlib.bases import MplPlot, MplSource

class MplCustomPlot(MplPlot):
    if hasattr(MplSource, 'plot_figure'):
        # 2.2
        _output_ports = [('value', '(MplCustomPlot)')]
        def compute(self):
            self.set_output('value', lambda figure: self.plot())
    else:
        # 2.1
        _output_ports = [('self', Module, {'optional': True}),
                         ('value', '(MplCustomPlot)')]
        def compute(self):
            self.setResult('value', self)
            self.plot()

    def plot(self):
        raise NotImplementedError("Subclasses of MplCustomPlot must implement "
                                  "plot()")
