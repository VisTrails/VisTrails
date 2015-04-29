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

import urllib, copy
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import copy
import string
import pickle

from dataset_core import *
from dataset_exceptions import *
from dataset_fit import *

from pyalps.hlist import deep_flatten, flatten, happly, hmap, depth
from pyalps.dict_intersect import dict_difference, dict_intersect

class SortEachDataSet(FitPrototype):
    """
    Sort the x,y lists in each DataSet according to x.
    """
    def transform(self,data):
        order = np.argsort(data.x)
        data.x = data.x[order]
        data.y = data.y[order]

class RestrictXRange(FitPrototype):
    my_input_ports = [
        PortDescriptor('min',basic.Float),
        PortDescriptor('max',basic.Float)
    ]
    
    def transform(self,data):
        min = self.getInputFromPort('min')
        max = self.getInputFromPort('max')
        
        selection = (data.x >= min) & (data.x <= max)
        data.x = data.x[selection]
        data.y = data.y[selection]

class RestrictYRange(FitPrototype):
    my_input_ports = [
        PortDescriptor('min',basic.Float),
        PortDescriptor('max',basic.Float)
    ]
    
    def transform(self,data):
        min = self.getInputFromPort('min')
        max = self.getInputFromPort('max')
        
        selection = (data.y >= min) & (data.y <= max)
        data.x = data.x[selection]
        data.y = data.y[selection]

class SortByProps(Module):
    """
    Sort datasets according to the list of props in 'sort_props'.
    """
    my_input_ports = [
        PortDescriptor('input',DataSets),
        PortDescriptor('sort_props',basic.List)
    ]
    my_output_ports = [
        PortDescriptor('output',DataSets)
    ]
    
    def compute(self):
        sets = self.getInputFromPort('input')
        sortprops = self.getInputFromPort('sort_props')
        
        q2 = []
        for d in flatten(sets):
            q2.append(d)
        for sp in reversed(sortprops):
            q2 = sorted(q2, key=lambda d: d.props[sp])
        self.setResult('output', q2)

class WriteTxt(Module):
    my_input_ports = [PortDescriptor('input',DataSets)]
    my_output_ports = []
    
    def compute(self):
        if self.hasInputFromPort('input'):
            for s in self.getInputFromPort('input'):
                if 'filename' in s.props:
                    data = np.array([s.x,s.y]).transpose()
                    np.savetxt(s.props['filename'],data)

class PickleDataSets(Module):
    my_input_ports = [PortDescriptor('input',DataSets)]
    my_output_ports = [PortDescriptor('file',basic.File)]
    
    def compute(self):
        sets = self.getInputFromPort('input')
        f = self.interpreter.filePool.create_file()
        with open(f.name, 'w') as out:
            pickle.dump(sets, out)
        self.setResult('file', f)

class UnpickleDataSets(Module):
    my_input_ports = [PortDescriptor('file',basic.File)]
    my_output_ports = [PortDescriptor('output',DataSets)]
    
    def compute(self):
        f = self.getInputFromPort('file')
        with open(f.name) as ifile:
            sets = pickle.load(ifile)
        self.setResult('output', sets)

class CacheErasure(NotCacheable,Module):
    my_input_ports = [PortDescriptor('input',DataSets)]
    my_output_ports = [PortDescriptor('output',DataSets)]
    
    def compute(self):
        self.setResult('output', self.getInputFromPort('input'))
    
class SetLabels(Module):
    """
    Set labels according to the properties given in 'label_props'.
    """
    my_input_ports = [
        PortDescriptor('input',DataSets),
        PortDescriptor('label_props',basic.List)
    ]
    my_output_ports = [
        PortDescriptor('output',DataSets)
    ]
    
    # overwrite default behaviour to deepcopy everything
    def compute(self):
        q = self.getInputFromPort('input')
        labels = self.getInputFromPort('label_props')
        
        def f(x):
            ret = DataSet()
            ret.x = x.x
            ret.y = x.y
            ret.props = copy.deepcopy(x.props)
            labelstr = ''
            for label in labels:
                val = 'unknown'
                try:
                    if type(x.props[label]) == str:
                        val = x.props[label]
                    else:
                        val = '%.4s' % x.props[label]
                except KeyError:
                    pass
                if label != labels[0]:
                    labelstr += ', '
                labelstr += '%s = %s' % (label,val)
            ret.props['label'] = labelstr
            return ret
        
        q2 = hmap(f, q)
        self.setResult('output', q2)

class CycleColors(Module):
    """
    Cyclically assign colors to the lines/markers that will be used to
    display the DataSets, based on the properties in 'for-each'. This means
    that DataSet instances that have the same values for the properties
    in 'for-each' will receive the same color.
    """
    my_input_ports = [
        PortDescriptor('input',DataSets),
        PortDescriptor('for-each',basic.List),
        PortDescriptor('colors',basic.List)
    ]
    my_output_ports = [
        PortDescriptor('output',DataSets)
    ]
    
    def compute(self):
        colors = ['k','b','g','m','c','y']
        if self.hasInputFromPort('colors'):
            colors = self.getInputFromPort('colors')
        
        input = self.getInputFromPort('input')
        foreach = self.getInputFromPort('for-each')
        
        all = {}
        for q in flatten(input):
            key = tuple([q.props[k] for k in foreach])
            all[key] = ''
        
        icolor = 0
        for k in all.keys():
            all[k] = colors[icolor]
            icolor = (icolor+1)%len(colors)
        
        for q in flatten(input):
            key = tuple([q.props[k] for k in foreach])
            q.props['color'] = all[key]
        
        self.setResult('output', input)

class CycleMarkers(Module):
    """
    Cyclically assign markers to the lines/markers that will be used to
    display the DataSets, based on the properties in 'for-each'. This means
    that DataSet instances that have the same values for the properties
    in 'for-each' will receive the same marker.
    """
    my_input_ports = [
        PortDescriptor('input',DataSets),
        PortDescriptor('for-each',basic.List),
        PortDescriptor('markers',basic.List)
    ]
    my_output_ports = [
        PortDescriptor('output',DataSets)
    ]
    
    def compute(self):
        markers = ['s', 'o', '^', '>', 'v', '<', 'd', 'p', 'h', '8', '+', 'x']
        if self.hasInputFromPort('markers'):
            markers = self.getInputFromPort('markers')
        
        input = self.getInputFromPort('input')
        foreach = self.getInputFromPort('for-each')
        
        all = {}
        for q in flatten(input):
            key = tuple([q.props[k] for k in foreach])
            all[key] = ''
        
        imarker = 0
        for k in all.keys():
            all[k] = markers[imarker]
            imarker = (imarker+1)%len(markers)
        
        for q in flatten(input):
            key = tuple([q.props[k] for k in foreach])
            q.props['marker'] = all[key]
            if 'line' in q.props:
                ll = list(q.props['line'])
                ll[0] = all[key]
                q.props['line'] = string.join(ll, sep='')
            else:
                q.props['line'] = all[key] + '-'
        
        self.setResult('output', input)

class SetPlotStyle(FitPrototype):
    """
    Choose plot style (line/scatter).
    
    It is possible to choose both, which will lead to a line plot with markers.
    """
    my_input_ports = FitPrototype.my_input_ports + [
        PortDescriptor('scatter',basic.Boolean),
        PortDescriptor('line',basic.Boolean)
    ]
    
    def transform(self,data):
        line = False
        scatter = False
        if self.hasInputFromPort('scatter') and self.getInputFromPort('scatter') == True:
            scatter = True
        if self.hasInputFromPort('line') and self.getInputFromPort('line') == True:
            line = True
        
        if not line and not scatter:
            line = True
        if line and not scatter:
            data.props['line'] = '-'
        elif scatter and not line:
            data.props['line'] = 'scatter'
        elif scatter and line:
            data.props['line'] = '.-'
        else:
            pass # impossible

class Flatten(Module):
    my_input_ports = [PortDescriptor('input',DataSets)]
    my_output_ports = [PortDescriptor('output',DataSets)]
    
    def compute(self):
        self.setResult('output', deep_flatten(self.getInputFromPort('input')))

class PrepareDictionary(Module):
    my_input_ports = [PortDescriptor('source',basic.String,use_python_source=True)]
    my_output_ports = [PortDescriptor('output',basic.Dictionary)]
    
    def compute(self):
        lines = self.getInputFromPort('source')
        lines = urllib.unquote(str(lines)).splitlines()
        lines1 = []
        for line in lines:
            if line.startswith('#'):
                continue
            else:
                lines1.append(line.strip())
        
        d = {}
        for line in lines1:
            pair = line.split('=')
            if len(pair) == 2:
                d[pair[0]] = pair[1]
        
        self.setResult('output', d)

class PrintHierarchyStructure(Module):
    my_input_ports = [PortDescriptor('input',DataSets)]
    my_output_ports = []
    
    def compute(self):
        q = self.getInputFromPort('input')
        
        all_props = [v.props for v in flatten(q)]
        diff_props = dict_difference(all_props)
        
        def f(x):
            d = {}
            for k in diff_props:
                d[k] = x.props[k]
            return d
        
        q2 = hmap(f, q)
