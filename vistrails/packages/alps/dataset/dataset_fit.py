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
from scipy import optimize, polyfit
import pyalps.fit_wrapper as fw
#from pyalps.fit_wrapper import 

from dataset_core import *
from dataset_exceptions import *

from pyalps.hlist import flatten

class FitPrototype(Module):
    my_input_ports = [
        PortDescriptor("input",DataSets)
    ]
    my_output_ports = [
        PortDescriptor("output",DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('input'):
            q = copy.deepcopy(self.getInputFromPort('input'))
            for s in flatten(q):
                s = self.transform(s)

            self.setResult('output',q)
        else:
            raise EmptyInputPort('input')
    
    def property_compute(self):
        if self.hasInputFromPort('input'):
            newsets = []
            q = self.getInputFromPort('input')
            for s in flatten(q):
                newsets.append(DataSet())
                newsets[-1].x = s.x
                newsets[-1].y = s.y
                newsets[-1].props = copy.deepcopy(s.props)
                self.transform(newsets[-1])
            self.setResult('output',newsets)

class DoPolynomialFit(FitPrototype):
    """
    Perform a polynomial fit using the polyfit function in SciPy.
    
    The user only needs to supply the degree of the desired polynomial form. The output
    will contain the same x values as the input and the y values of the fitted polynomial form.
    The fit parameters are stored into the property 'fit_parameters' as a list of floating
    point numbers, with the highest power first.
    """
    my_input_ports = FitPrototype.my_input_ports + [PortDescriptor("degree",basic.Integer)]
    my_output_ports = FitPrototype.my_output_ports
    
    def transform(self, data):
        degree = 0
        if self.hasInputFromPort('degree'):
            degree = self.getInputFromPort('degree')
        else:
            degree = 1
        
        fit_parms = polyfit(data.x, data.y, degree)
        data.props['fit_parameters'] = fit_parms
        
        data.y = 0*data.x
        for deg in range(0,degree+1):
            data.y = data.y + fit_parms[deg]*data.x**(degree-deg)
        
        return data

class DoNonlinearFit(FitPrototype):
    """
    Perform a non-linear fit, using the fit_wrapper of pyalps, which in turn makes use
    of SciPy.optimize.
    
    The input ports are:
     * parameters: This is a list of initial values for the parameters. The length of this
                   determines the number of parameters.
     * source: The user needs to provide a function (x,A)->y, with A being the list of
               parameters. The parameters at this point are *not* floating point numbers,
               but are stored in a special class Parameter. To access the numeric value,
               use the () operator, i.e. the first parameter should be accessed as
                 A[0]()
               x should be expected to be a Numpy array, so should the return value.
               
               Ex 1: exponential form
               return A[0]()+A[1]()*np.exp(A[2]()*x)
               
               Ex 2: power law decay to zero
               return A[0]()*x**A[1]()
     
    The output dataset will contain the x values along an equidistant grid of 1000
    points in the range of the original data and the y values at those points.
    The list of parameters is stored into the property 'fit'; to access, use the
    get() method of the Parameter instances, e.g.
      props['fit][0].get()
    A label will be created automatically from the fit parameters.
    """
    my_input_ports = FitPrototype.my_input_ports + \
    [
        PortDescriptor('parameters',basic.List),
        PortDescriptor('source',basic.String,use_python_source=True),
    ]
    
    def transform(self, data):
        pars0 = self.getInputFromPort('parameters')
        A = [fw.Parameter(q) for q in pars0]
        
        code = self.getInputFromPort('source')
        proc_code = urllib.unquote(str(code))
        cmd = 'def f(self,x,A):\n'
        for line in proc_code.splitlines():
            cmd += '\t' + line + '\n'
        exec cmd
        
        fw.fit(self, f, A, data.y, data.x)
        
        data.props['label'] = ''
        for i in range(0,len(A)):
            data.props['label'] += 'A%s=%s ' % (i,A[i].get())
        data.props['fit'] = A
        
        data.x = np.linspace(min(data.x), max(data.x), 1000)
        data.y = f(self,data.x,A)
        
        return data
