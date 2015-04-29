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
from gui.modules.python_source_configure import PythonSourceConfigurationWidget

import urllib, copy
import numpy as np

# version = "0.0.3"
# name = "dataset"
# identifier = "org.comp-phys.alps.dataset"

from dataset_exceptions import *
from dataset_core import *
from dataset_evaluate import *
from dataset_fit import *
from dataset_load import *
from dataset_plot import *
from dataset_tools import *
from dataset_select import *

def register(m,ns,abst=False):
    reg = vistrails.core.modules.module_registry.registry
    
    ups = False
    for input_port in m.my_input_ports:
        if input_port.use_python_source:
            ups = True
    if ups:
        reg.add_module(m, namespace=ns, configureWidgetType=PythonSourceConfigurationWidget, abstract=abst)
    else:
        reg.add_module(m, namespace=ns, abstract=abst)
    
    for input_port in m.my_input_ports:
        if input_port.porttype == SelftypePlaceholder:
            input_port.porttype = m
        
        if ups and input_port.hidden:
            if input_port.use_python_source:
                reg.add_input_port(m, input_port.name, (input_port.porttype, input_port.description), True)
            else:
                reg.add_input_port(m, input_port.name, (input_port.porttype, input_port.description))
        elif input_port.use_python_source or input_port.hidden:
            reg.add_input_port(m, input_port.name, (input_port.porttype, input_port.description), True)
        else:
            reg.add_input_port(m, input_port.name, (input_port.porttype, input_port.description))
    
    for output_port in m.my_output_ports:
        if output_port.porttype == SelftypePlaceholder:
            output_port.porttype = m
        
        if output_port.hidden:
            reg.add_output_port(m, output_port.name, (output_port.porttype, output_port.description), True)
        else:
            reg.add_output_port(m, output_port.name, (output_port.porttype, output_port.description))
    
    if Descriptor in m.__bases__ or Predicate in m.__bases__ or m == Predicate:
        reg.add_output_port(m, 'output', (m,''))

def initialize(): pass

def selfRegister():

    # We'll first create a local alias for the module registry so that
    # we can refer to it in a shorter way.
    reg = vistrails.core.modules.module_registry.registry

    register(DataSets,'DataSet',abst=True)
    register(ConcatenateDataSets,'DataSet')
    register(ResultFiles,'DataSet')
    
    register(ConstantDataSet,'DataSet|Load')
    register(PrepareDataSets,'DataSet|Load')
    register(LoadDataSetsFromTextFile,'DataSet|Load')
    register(LoadCustomFile,'DataSet|Load')
    register(CollectDataSets,'DataSet|Load')
    register(LoadAlpsProperties,'DataSet|Load')
    register(LoadAlpsMeasurements,'DataSet|Load')
    register(LoadTimeEvolution,'DataSet|Load')
    register(LoadAlpsSpectra,'DataSet|Load')
    register(LoadBinningAnalysis,'DataSet|Load')
    register(LoadAlpsEigenstateMeasurements,'DataSet|Load')
    register(LoadAlpsIterationMeasurements,'DataSet|Load')
    register(LoadDMFTIterations,'DataSet|Load')

    register(TransformEachDataSet,'DataSet|Evaluate')
    register(TransformProperties,'DataSet|Evaluate')
    AddDataSetsInputPorts(CombineDataSets, 5)
    register(CombineDataSets,'DataSet|Tools')
    AddDataSetsInputPorts(TransformN, 5)
    register(TransformN,'DataSet|Evalute',abst=True)
    register(Reduce,'DataSet|Evaluate')
    register(GeneralTransform,'DataSet|Evaluate',abst=True)
    register(ComputeSelfenergy,'DataSet|Evaluate')
    
    register(Axis,'DataSet|Plot')
    register(Legend,'DataSet|Plot')
    register(Plotter,'DataSet|Plot',abst=True)
    register(PreparePlot,'DataSet|Plot')
    register(MplXYPlot,'DataSet|Plot')
    reg.add_module(WriteTextFile,namespace='DataSet|Plot')
    reg.add_module(WriteGraceFile,namespace='DataSet|Plot')
    reg.add_module(WriteGnuplotFile,namespace='DataSet|Plot')
    reg.add_module(LoadXMLPlot,namespace='DataSet|Plot')
    register(SetLabels,'DataSet|Plot')
    
    register(FitPrototype,'DataSet|Fit',abst=True)
    register(DoPolynomialFit,'DataSet|Fit')
    register(DoNonlinearFit,'DataSet|Fit')
    
    register(SortEachDataSet,'DataSet|Tools')
    register(RestrictXRange,'DataSet|Tools')
    register(RestrictYRange,'DataSet|Tools')
    register(SortByProps,'DataSet|Tools')
    register(PickleDataSets,'DataSet|Tools')
    register(UnpickleDataSets,'DataSet|Tools')
    register(WriteTxt,'DataSet|Tools',abst=True)
    register(CacheErasure,'DataSet|Tools',abst=True)
    register(PrepareDictionary,'Tools')
    register(SetPlotStyle,'DataSet|Plot')
    register(CycleColors,'DataSet|Plot')
    register(CycleMarkers,'DataSet|Plot')
    
    register(Predicate,'DataSet|Select',abst=True)
    register(PropertyPredicate,'DataSet|Select')
    register(PropertyRangePredicate,'DataSet|Select')
    register(ObservablePredicate,'DataSet|Select')
    register(And,'DataSet|Select',abst=True)
    register(Or,'DataSet|Select',abst=True)
    register(Select,'DataSet|Select')
    register(SelectFiles,'DataSet|Select')
    
    register(SelectBy,'DataSet|Select',abst=True)
    register(SelectByProperty,'DataSet|Select')
    register(SelectByPropertyRange,'DataSet|Select')
    register(SelectByObservable,'DataSet|Select')
    
    register(GroupDataSets,'DataSet|Hierarchy')
    register(TransformGroupedDataSets,'DataSet|Hierarchy')
    register(Flatten,'DataSet|Hierarchy')
    register(PrintHierarchyStructure,'DataSet|Hierarchy')
