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

from dataset_core import *
from dataset_exceptions import *

from pyalps.hlist import flatten, happly, hmap

class ConstantDataSet(Module):
    """Create a constant dataset and store into DataSets"""
    my_input_ports = [
        PortDescriptor("value",basic.Float),
        PortDescriptor("length",basic.Integer)
    ]

    my_output_ports = [
        PortDescriptor("value",DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('value') and self.hasInputFromPort('length'):
            value = self.getInputFromPort('value')
            length = self.getInputFromPort('length')

            d = DataSet()
            d.x = np.arange(0,length)
            d.y = value + 0*d.x

            self.setResult('value',[d])
        else:
            raise EmptyInputPort('value || source')

class PrepareDataSets(Module):
    """
    Prepare a DataSet or a list of DataSets using some user-provided code.
    
    The user code (entered into the PythonSource widget) is expected to create a variable
    called result which may contain either a single DataSet instance or a list of
    DataSet instances. In the first case, it will implicitly be converted to a list of
    length 1.
    """
    
    my_input_ports = [PortDescriptor('source',basic.String,use_python_source=True)]
    my_output_ports = [PortDescriptor('output',DataSets)]
    
    def compute(self):
        if self.hasInputFromPort('source'):
            code = self.getInputFromPort('source')
            proc_code = urllib.unquote(str(code))
            exec proc_code
            
            try:
                if type(result) == list:
                    self.setResult('output',result)
                else:
                    self.setResult('output',[result])
            except NameError:
                raise InvalidInput("Generate result!")
                
        else:
            raise EmptyInputPort('source')

class ComputeSelfenergy(Module):
    """
    Performs the Dyson equation on lists of G_omega and G0_omega.
    
    @G_omega: list of datasets containing G_omega (for possibly many iterations and independent simulations)
    @G0_omega: list of datasets containing G0_omega (for possibly many iterations and independent simulations)
    output: list of datasets containing selfenergy in Matsubara represention (complex-valued)
    """
    my_input_ports = [
        PortDescriptor("G_omega",DataSets),
        PortDescriptor("G0_omega",DataSets)
    ]
    my_output_ports = [
        PortDescriptor("Selfenergy",DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('G_omega') and self.hasInputFromPort('G0_omega'):
            G = self.getInputFromPort('G_omega')
            G0 = copy.deepcopy(self.getInputFromPort('G0_omega'))
            for g0 in flatten(G0):
                del g0.props['hdf5_path']
            Sigma = []
            for g in flatten(G):
                props = copy.deepcopy(g.props)
                del props['hdf5_path']
                g0 = [s for s in flatten(G0) if props==s.props][0]
                Sigma.append(DataSet())
                Sigma[-1].x = copy.deepcopy(g.x)
                # Dyson equation
                Sigma[-1].y = np.array([1./g0.y[w] - 1./g.y[w] for w in range(len(g.y))])
                Sigma[-1].props = props
            print len(Sigma)
            self.setResult('Selfenergy',Sigma)
        else:
            raise EmptyInputPort('G_omega || G0_omega')

class TransformEachDataSet(Module):
    """
    Perform a transformation on all DataSets in the input separately.
    
    The user-supplied code should make use of the three input variables x,y,props and
    perform in-place transformations on those. The module will perform the iteration
    over all DataSet instances in the input list, tacitly flattening that list if
    it is hierarchical. The output will be a flat list.
    """
    my_input_ports = [
        PortDescriptor("input",DataSets),
        PortDescriptor("source",basic.String,use_python_source=True)
    ]
    my_output_ports = [
        PortDescriptor("output",DataSets)
    ]
    deepcopy_all = True

    def compute(self):
        if self.hasInputFromPort('input') and self.hasInputFromPort('source'):
            if self.deepcopy_all:
                q = copy.deepcopy(self.getInputFromPort('input'))
            else:
                q = self.getInputFromPort('input')
                newsets = []
            for s in flatten(q):
                x = s.x
                y = s.y
                if self.deepcopy_all:
                    props = s.props
                else:
                    props = copy.deepcopy(s.props)

                code = self.getInputFromPort('source')
                proc_code = urllib.unquote(str(code))
                exec proc_code
                
                if self.deepcopy_all:
                    s.x = x
                    s.y = y
                else:
                    newsets.append(DataSet())
                    newsets[-1].x = x
                    newsets[-1].y = y
                    newsets[-1].props = props

            if self.deepcopy_all:
                self.setResult('output',q)
            else:
                self.setResult('output',newsets)
        else:
            raise EmptyInputPort('input || source')

class TransformGroupedDataSets(Module):
    """
    Transform a structured list into a structured list, possibly changing the structure.
    
    This module generalizes the functionality of TransformEachDataSet and allows more
    specific control over actions taken on hierarchical list. The user-supplied code can
    make use of the input variable data, which is either a DataSet or a (possibly hierarchical)
    list of DataSet instances, depending on the depth of the hierarchy in the input and the
    level provided by the user.
    
    The code should make use of the return statement to yield either a list of a single
    DataSet instance.
    
    The level parameters works identically as for the pyalps.happly() function.
    
    For more introduction to hierarchical lists, refer to the documentation of the
    GroupDataSets module.
    """
    
    my_input_ports = [
        PortDescriptor("input",DataSets),
        PortDescriptor("source",basic.String,use_python_source=True),
        PortDescriptor("level",basic.Integer)
    ]
    my_output_ports = [
        PortDescriptor("output",DataSets)
    ]

    def compute(self):
        level = 1
        if self.hasInputFromPort('level'):
            level = self.getInputFromPort('level')
        
        if self.hasInputFromPort('input') and self.hasInputFromPort('source'):
            q = copy.deepcopy(self.getInputFromPort('input'))
            
            code = self.getInputFromPort('source')
            proc_code = urllib.unquote(str(code))
            cmd = 'def f(data, self):\n'
            for line in proc_code.splitlines():
                cmd += '\t' + line + '\n'
            exec cmd
            
            if level > 0:
                happly(f, q, level, self)
            else:
                q = f(q, self)

            self.setResult('output',q)
        else:
            raise EmptyInputPort('input || source')

class TransformProperties(TransformEachDataSet):
    """
    This module works just as the TransformEachDataSet module, but should perform operations
    only on the properties of each DataSet. It will generally be faster.
    """
    deepcopy_all = False

def AddDataSetsInputPorts(m, Nmax):
    for i in range(0,Nmax):
        m.my_input_ports.append(PortDescriptor('input'+str(i),DataSets))

class CombineDataSets(Module):
    my_input_ports = []
    my_output_ports = [PortDescriptor("output",DataSets)]
    
    def compute(self):
        Nports = len(self.my_input_ports)
        inputs = []
        for i in range(Nports):
            port = 'input'+str(i)
            if self.hasInputFromPort(port):
                r = self.getInputFromPort(port)
                inputs.append(copy.deepcopy(r))
        self.setResult('output', inputs)

class Reduce(Module):
    my_input_ports = [
        PortDescriptor("input",DataSets),
        PortDescriptor("source",basic.String,use_python_source=True)
    ]
    my_output_ports = [
        PortDescriptor("output",DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('input') and self.hasInputFromPort('source'):
            result = DataSet()
            
            for s in flatten(self.getInputFromPort('input')):
                code = self.getInputFromPort('source')
                proc_code = urllib.unquote(str(code))
                exec proc_code
            
            self.setResult('output',[result])
        else:
            raise EmptyInputPort('input || source')

class GeneralTransform(Module):
    my_input_ports = [
        PortDescriptor("input",DataSets),
        PortDescriptor("source",basic.String,use_python_source=True)
    ]
    my_output_ports = [
        PortDescriptor("output",DataSets)
    ]
    
    def compute(self):
        if self.hasInputFromPort('input') and self.hasInputFromPort('source'):
            data = copy.deepcopy( self.getInputFromPort('input') )
            
            code = self.getInputFromPort('source')
            proc_code = urllib.unquote(str(code))
            exec proc_code
            
            self.setResult('output', data)
        else:
            raise EmptyInputPort('input || source')

class TransformN(Module):
    my_input_ports = [
        PortDescriptor("source",basic.String,use_python_source=True)
    ]
    my_output_ports = [
        PortDescriptor("output",DataSets)
    ]
    
    def compute(self):
        if self.hasInputFromPort('source'):
            Nports = len(self.my_input_ports)-1
            
            inputs = []
            for i in range(0,Nports):
                port = 'input'+str(i)
                if self.hasInputFromPort(port):
                    r = self.getInputFromPort(port)
                    inputs.append(flatten(copy.deepcopy(r)))
            Ninputs = len(inputs)
            
            results = []
            
            for i in range(1,Ninputs):
                if len(inputs[0]) != len(inputs[i]):
                    raise InvalidInput("Input lengths don't match")
            
            for iset in range(0,len(inputs[0])):
                for iport in range(0,Ninputs):
                    cmd = 'set' + str(iport) + ' = inputs[' + str(iport) + '][' + str(iset) + ']'
                    exec cmd
                
                result = DataSet()
                
                code = self.getInputFromPort('source')
                proc_code = urllib.unquote(str(code))
                exec proc_code
                
                results.append(result)
            
            self.setResult('output',results)
        else:
            raise EmptyInputPort('source')
