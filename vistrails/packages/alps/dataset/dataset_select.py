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

from dataset_core import *
from dataset_exceptions import *

from pyalps.hlist import flatten

class Predicate(Module):
    my_input_ports = []
    my_output_ports = []
    
    def compute(self):
        for inp in self.my_input_ports:
            if not self.hasInputFromPort(inp.name):
                raise EmptyInputPort(inp.name)
        self.setResult('output',self)

class SelectBy(Module):
    my_input_ports = [PortDescriptor('input', DataSets)]
    my_output_ports = [
        PortDescriptor('kept', DataSets),
        PortDescriptor('discarded', DataSets)
    ]
    
    def compute(self):
        q = copy.deepcopy(self.getInputFromPort('input'))
        kept_sets = []
        disc_sets = []
        
        for iq in flatten(q):
            if self.decide(iq):
                kept_sets.append(iq)
            else:
                disc_sets.append(iq)
        
        self.setResult('kept',kept_sets)
        self.setResult('discarded',disc_sets)

class PropertyPredicate(Predicate):
    my_input_ports = [
        PortDescriptor('property_name',basic.String),
        PortDescriptor('property_value',basic.String)
    ]
    
    @staticmethod
    def decide(self,ds):
        pn = self.getInputFromPort('property_name')
        if pn in ds.props:
            pv = type(ds.props[pn])(self.getInputFromPort('property_value'))
            return ds.props[pn] == pv
        return False

class PropertyRangePredicate(Predicate):
    my_input_ports = [
        PortDescriptor('property_name',basic.String),
        PortDescriptor('min',basic.String),
        PortDescriptor('max',basic.String)
    ]
    
    @staticmethod
    def decide(self,ds):
        pn = self.getInputFromPort('property_name')
        if pn in ds.props:
            if self.hasInputFromPort('min') and self.hasInputFromPort('max'):
                pmin = type(ds.props[pn])(self.getInputFromPort('min'))
                pmax = type(ds.props[pn])(self.getInputFromPort('max'))
                if ds.props[pn] >= pmin and ds.props[pn] <= pmax:
                    return True
            elif self.hasInputFromPort('min'):
                pmin = type(ds.props[pn])(self.getInputFromPort('min'))
                if ds.props[pn] >= pmin:
                    return True
            elif self.hasInputFromPort('max'):
                pmax = type(ds.props[pn])(self.getInputFromPort('max'))
        return False

class ObservablePredicate(Predicate):
    my_input_ports = [
        PortDescriptor('observable',basic.String)
    ]
    
    @staticmethod
    def decide(self,ds):
        if ds.props['observable'] == self.getInputFromPort('observable'):
            return True
        return False

class SelectByProperty(SelectBy):
    my_input_ports = SelectBy.my_input_ports + PropertyPredicate.my_input_ports
    my_output_ports = SelectBy.my_output_ports
    
    decide = PropertyPredicate.decide

class SelectByPropertyRange(SelectBy):
    my_input_ports = SelectBy.my_input_ports + PropertyRangePredicate.my_input_ports
    my_output_ports = SelectBy.my_output_ports
    
    decide = PropertyRangePredicate.decide

class SelectByObservable(SelectBy):
    my_input_ports = SelectBy.my_input_ports + ObservablePredicate.my_input_ports
    my_output_ports = SelectBy.my_output_ports
    
    decide = ObservablePredicate.decide

class Select(Module):
    """
    Select from a list of DataSet instances based on either a user-provided source code
    or some predefined predicate.
    
    The user-provided code should make use of the variables x,y,props and return True
    or False.
    
    Alternatively, connecting a Predicate to the appropriate input port can be used. This
    usage is discouraged and should be replaced by the SelectByXXX modules.
    """
    my_input_ports = [
        PortDescriptor("input",DataSets),
        PortDescriptor("source",basic.String,use_python_source=True),
        PortDescriptor("select",Predicate,hidden=True)
    ]
    my_output_ports = [
        PortDescriptor("kept",DataSets),
        PortDescriptor("discarded",DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('input') and self.hasInputFromPort('source'):
            q = copy.deepcopy(self.getInputFromPort('input'))
            kept_sets = []
            disc_sets = []
            
            code = self.getInputFromPort('source')
            proc_code = urllib.unquote(str(code))
            
            cmd = 'def fn(x,y,props):\n'
            for line in proc_code.splitlines():
                cmd = cmd + '\t' + line + '\n'
            exec cmd
                
            for s in flatten(q):
                if fn(s.x,s.y,s.props):
                    kept_sets.append(s)
                else:
                    disc_sets.append(s)
                    
            self.setResult('kept',kept_sets)
            self.setResult('discarded',disc_sets)
        elif self.hasInputFromPort('input') and self.hasInputFromPort('select'):
            s = self.getInputFromPort('select')
            q = copy.deepcopy(self.getInputFromPort('input'))
            kept_sets = []
            disc_sets = []
            
            for iq in flatten(q):
                if s.decide(s, iq): # please don't ask why it wants to be called like this...
                    kept_sets.append(iq)
                else:
                    disc_sets.append(iq)
            
            self.setResult('kept',kept_sets)
            self.setResult('discarded',disc_sets)
        else:
            raise EmptyInputPort('input || source')

class SelectFiles(Select):
    my_input_ports = [
        PortDescriptor("input",ResultFiles),
        PortDescriptor("source",basic.String,use_python_source=True),
        PortDescriptor("select",Predicate,hidden=True)
    ]
    my_output_ports = [
        PortDescriptor("kept",ResultFiles),
        PortDescriptor("discarded",ResultFiles)
    ]

class And(Predicate):
    my_input_ports = [
        PortDescriptor('selectors',Predicate)
    ]
    
    def compute(self):
        self.selectors = []
        if self.hasInputFromPort('selectors'):
            self.selectors = self.forceGetInputListFromPort('selectors')
        self.setResult('output',self)
    
    @staticmethod
    def decide(self,ds):
        for selector in self.selectors:
            if selector.decide(selector, ds) == False:
                return False
        return True

class Or(And):
    @staticmethod
    def decide(self,ds):
        for selector in self.selectors:
            if selector.decide(selector, ds):
                return True
        return False
