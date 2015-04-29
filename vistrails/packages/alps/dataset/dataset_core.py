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
import numpy as np

from pyalps import DataSet,ResultFile

class PortDescriptor:
    def __init__(self, name, porttype, description='', use_python_source=False, hidden=False):
        self.name = name
        self.porttype = porttype
        self.description = description
        self.use_python_source = use_python_source
        self.hidden = hidden
    
    name = ''
    porttype = basic.String
    description = ''
    use_python_source = False
    hidden = False

class DataSets(basic.List):
    my_input_ports = []
    my_output_ports = []

    def __init__(self):
        Module.__init__(self)

class SelftypePlaceholder:
    is_placeholder = True

class ResultFiles(basic.List):
    my_input_ports = [
        PortDescriptor('filenames', basic.List),
        PortDescriptor('resultfiles', SelftypePlaceholder)
    ]
    my_output_ports = [
        PortDescriptor('filenames', basic.List),
        PortDescriptor('resultfiles', SelftypePlaceholder)
    ]
    
    def __init__(self):
        Module.__init__(self)
    
    def compute(self):
        rf = []
        if self.hasInputFromPort('resultfiles'):
            rf += self.getInputFromPort('resultfiles')
        if self.hasInputFromPort('filenames'):
            rf += [ResultFile(x) for x in self.getInputFromPort('filenames')]
        
        self.setResult('resultfiles', rf)
        self.setResult('filenames',[x.props['filename'] for x in rf])

class ConcatenateDataSets(Module):
    """
    Takes two DataSets (i.e. lists of DataSet instances) and concatenates the lists.
    """
    my_input_ports = [
        PortDescriptor('input',DataSets)
    ]

    my_output_ports = [
        PortDescriptor('value',DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('input'):
            inps = self.forceGetInputListFromPort('input')
            sets = []
            for inp in inps:
                sets = sets + inp
            self.setResult('value',sets)

class Descriptor:
    my_input_ports = []
    my_output_ports = []
    
    def __init__(self):
        Module.__init__(self)
    
    def compute(self):
        ret = {}
        for ip in self.my_input_ports:
            if self.hasInputFromPort(ip.name):
                ret[ip.name] = self.getInputFromPort(ip.name)
        self.setResult('output',ret)
