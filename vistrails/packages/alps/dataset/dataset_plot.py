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

import vistrails.core.modules.module_registry
import vistrails.core.modules.basic_modules as basic
from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable
from vistrails.gui.modules.python_source_configure import PythonSourceConfigurationWidget
from vistrails.packages.matplotlib.bases import MplPlot


import urllib, copy
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
from dataset_exceptions import *
from dataset_core import *
from pyalps import executeCommand
from pyalps.plot_core import *
from pyalps.plot import *

class Axis(Descriptor, Module):
    """
    Connect this to a PreparePlot module to add an axis.
    """
    my_input_ports = [
        PortDescriptor('label',basic.String),
        PortDescriptor('min',basic.Float),
        PortDescriptor('max',basic.Float),
        PortDescriptor('logarithmic',basic.Boolean),
        PortDescriptor('fontsize',basic.Integer)
    ]

class Legend(Descriptor, Module):
    """
   Connect this to a PreparePlot module to add a legend.
   """
    my_input_ports = [
        PortDescriptor('location',basic.Integer),
        PortDescriptor('fontsize',basic.Integer),
        PortDescriptor('scatter_labels',basic.Boolean),
        PortDescriptor('show_frame',basic.Boolean)
    ]

class PreparePlot(Descriptor, Module):
    """
    Prepare a plot.
    """
    my_input_ports = [
        PortDescriptor('xaxis',Axis),
        PortDescriptor('yaxis',Axis),
        PortDescriptor('legend',Legend),
        PortDescriptor('data',DataSets),
        PortDescriptor('title',basic.String),
        PortDescriptor('grid',basic.Boolean),
    ]

class MplXYPlot(MplPlot):
    my_input_ports = [
        PortDescriptor('plot',PreparePlot),
        PortDescriptor('hide_buttons',basic.Boolean),
        PortDescriptor('source',basic.String,use_python_source=True)
    ]
    my_output_ports = [PortDescriptor('self',MplPlot)]
  
    def __init__(self):
        MplPlot.__init__(self)
        self.colors = ['k','b','g','m','c','y']
        self.worker = MplXYPlot_core()
    
    def hifp(self,m):
        return self.hasInputFromPort(m)
    def gifp(self,m):
        return self.getInputFromPort(m)
            
    def compute(self):
            MplPlot.compute(self)
            if self.hifp('plot'):
                self.plt = self.gifp('plot')
            else:
                raise EmptyInputPort('plot')
            
            self.worker(self.plt)
            
            if self.hifp('hide_buttons') and self.gifp('hide_buttons') == True:
                plt.get_current_fig_manager().toolbar.hide()
            
            if self.hasInputFromPort('source'):
                code = self.getInputFromPort('source')
                exec urllib.unquote(str(code))
        
class WriteTextFile(Module): 
    _input_ports = [('plot',[(PreparePlot,'the plot')])]
    _output_ports = [('file',[(basic.File, 'the plot file')]),
                     ('value_as_string',[(basic.String, 'the plot as string')])]
    
    def compute(self):
        desc = self.getInputFromPort('plot')
        res = convert_to_text(desc)
        o = self.interpreter.filePool.create_file()
        f = file(o.name,'w')
        f.write(res)
        f.close()
        self.setResult('value_as_string',res)
        self.setResult('file',o)

class WriteGraceFile(Module): 
    _input_ports = [('plot',[(PreparePlot,'the plot')])]
    _output_ports = [('file',[(basic.File, 'the plot file')]),
                     ('value_as_string',[(basic.String, 'the plot as string')])]
    
    def compute(self):
        desc = self.getInputFromPort('plot')
        res = convert_to_grace(desc)
        o = self.interpreter.filePool.create_file()
        f = file(o.name,'w')
        f.write(res)
        f.close()
        self.setResult('value_as_string',res)
        self.setResult('file',o)

class LoadXMLPlot(Module): 
    _input_ports = [('file',[(basic.File, 'the plot file')])]
    _output_ports = [('plot',[(PreparePlot,'the plot')])]
    
    def compute(self):
        self.setResult('plot',read_xml(self.getInputFromPort('file').name))
        
class WriteGnuplotFile(Module): 
    _input_ports = [('plot',[(PreparePlot,'the plot')]),('filename',[(basic.String, 'the output filename')]),('terminal',[(basic.String, 'the gnuplot terminal')]) ]
    _output_ports = [('file',[(basic.File, 'the plot file')]),
                     ('value_as_string',[(basic.String, 'the plot as string')])]
    
    def compute(self):
        description = self.getInputFromPort('plot')
        outputname = None
        term=None
        if self.hasInputFromPort('filename'):
            outputname = self.getInputFromPort('filename')
        if self.hasInputFromPort('terminal'):
            term = self.getInputFromPort('terminal')
        res = convert_to_gnuplot(desc=description, outfile=outputname, terminal=term)
        o = self.interpreter.filePool.create_file()
        f = file(o.name,'w')
        f.write(res)
        f.close()
        self.setResult('value_as_string',res)
        self.setResult('file',o)
        if term == 'x11':
            executeCommand(['nohup','gnuplot', '-persist' , o.name,'&'])
            
        
        

class Plotter(MplPlot):
    my_input_ports = [
        PortDescriptor('data',DataSets),
        PortDescriptor('title',basic.String,hidden=True),
        PortDescriptor('xaxis',Axis),
        PortDescriptor('yaxis',Axis),
        PortDescriptor('legend',Legend),
        PortDescriptor('hide_buttons',basic.Boolean,hidden=True),
        PortDescriptor('source',basic.String,use_python_source=True)
    ]
    my_output_ports = [PortDescriptor('self',MplPlot)]
    def hifp(self,m):
        return self.hasInputFromPort(m)
    def gifp(self,m):
        return self.getInputFromPort(m)

    def compute(self):
        self.colors = ['k','b','g','m','c','y']
        
        if self.hifp('data'):
            s = self.gifp('data')
            lines = []
            icolor = 0
            for q in s:
                lines.append(plt.plot(q.x,q.y,self.colors[icolor]))
                icolor = (icolor+1)%len(self.colors)

                if 'label' in q.props:
                    label = q.props['label']
                    if label != 'none':
                        lines[-1][0].set_label(q.props['label'])
                elif 'filename' in q.props:
                    lines[-1][0].set_label(q.props['filename'])

            if self.hifp('title'):
                plt.title(self.gifp('title'))
            
            if self.hifp('xaxis'):
                xaxis = self.gifp('xaxis')
                if 'label' in xaxis:
                    plt.xlabel(xaxis['label'])
            
                if 'min' in xaxis and 'max' in xaxis:
                    if xaxis['min'] != xaxis['max']:
                        plt.xlim(xaxis['min'],xaxis['max'])
            
            if self.hifp('yaxis'):
                yaxis = self.gifp('yaxis')
                if 'label' in yaxis:
                    plt.ylabel(yaxis['label'])
                
                if 'min' in yaxis and 'max' in yaxis:
                    if yaxis['min'] != yaxis['max']:
                        plt.ylim(yaxis['min'],yaxis['max'])
            
            if self.hifp('legend'):
                legend = self.gifp('legend')
                if 'location' in legend:
                    plt.legend(loc=legend['location'])
                else:
                    plt.legend()
            
            if self.hifp('hide_buttons') and self.gifp('hide_buttons') == True:
                plt.get_current_fig_manager().toolbar.hide()
            
            if self.hasInputFromPort('source'):
                code = self.getInputFromPort('source')
                exec urllib.unquote(str(code))

            self.setResult('source','foo')
        else:
            raise EmptyInputPort('data')
