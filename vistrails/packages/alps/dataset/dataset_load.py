# ****************************************************************************
# 
# ALPS Project: Algorithms and Libraries for Physics Simulations
# 
# ALPS Libraries
# 
# Copyright (C) 1994-2010 by Bela Bauer <bauerb@phys.ethz.ch>
#                            Brigitte Surer <surerb@phys.ethz.ch> 
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
from vistrails.core import debug

import urllib, copy
import traceback
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

from dataset_core import *
from dataset_exceptions import *
from pyalps.load import Hdf5Loader
from pyalps.hlist import flatten, depth
import pyalps
import pyalps.hdf5 as h5

class Loader:
    def __init__(self,filename,label,xcolumn,ycolumns,props={}):
        self.sets = []
        self.read_set(filename,label,xcolumn,ycolumns,props)
    
    def __init__(self):
        self.sets = []
    
    def read_set(self,filename,label,xcolumn,ycolumns,props={}):
        raw = np.loadtxt(filename).transpose()
        
        if len(raw.shape) == 0:
            res = DataSet()
            res.x = np.array([0])
            res.y = np.array([raw])
            res.props.update(props)
            res.props.update({'column':0,'label':copy.deepcopy(label),'filename':filename})
            self.sets.append(res)
            return
        
        for iyc in ycolumns:
            res = DataSet()
            res.props['filename'] = filename
            
            if xcolumn >= 0:
                res.x = raw[xcolumn]
                res.y = raw[iyc]
            else:
                if len(raw.strides) == 1:
                    res.x = np.arange(0,len(raw))
                    res.y = raw
                else:
                    res.y = raw[iyc]
                    res.x = np.arange(0,len(res.y))
            
            res.props['column'] = iyc
            res.props['label'] = copy.deepcopy(label)
            res.props.update(props)
            
            self.sets.append(res)

class LoadDataSetsFromTextFile(Module):
    """Load dataset from text data. Description of input ports:
    @file: The file, of which only the name is used.
    @label: A possible label for the dataset
    @x-column: The column of the data used for x data. Default: 0
    @y-columns: A basic.List of the columns. Default: 1
    Catch: if the file only has one columns, set x-column to -1!
    The following properties are set: filename, [label], column"""
    my_input_ports = [
        PortDescriptor("file",basic.File),
        PortDescriptor("label",basic.String),
        PortDescriptor("x-column",basic.Integer),
        PortDescriptor("y-columns",basic.List)
    ]

    my_output_ports = [
        PortDescriptor("data",DataSets)
    ]

    def compute(self):
        if self.hasInputFromPort('file'):
            f = self.getInputFromPort('file')
            filename = f.name
            
            xc = 0
            yc = [1]
            if self.hasInputFromPort('x-column'):
                xc = int(self.getInputFromPort('x-column'))
                if xc < 0:
                    yc = [0]
            if self.hasInputFromPort('y-columns'):
                yc = self.getInputFromPort('y-columns')
                yc = [int(x) for x in yc]
            
            label = ''
            if self.hasInputFromPort('label'):
                label = self.getInputFromPort('label')
            
            l = Loader()
            l.read_set(filename,label,xc,yc)
            self.setResult('data', l.sets)

class LoadCustomFile(Module):
    my_input_ports = [
        PortDescriptor("source",basic.String,use_python_source=True),
        PortDescriptor("base_path",basic.String),
        PortDescriptor("base_dir",basic.Directory)
    ]
    my_output_ports = [
        PortDescriptor("data",DataSets)
    ]
    
    def compute(self):
        if self.hasInputFromPort('source'):
            code = self.getInputFromPort('source')
            proc_code = urllib.unquote(str(code))
            exec proc_code

class LoadAlpsProperties(Module):
    my_input_ports = [
        PortDescriptor('ResultFiles', ResultFiles),
        PortDescriptor('PropertyPath',basic.String) 
    ]
    
    my_output_ports = [
        PortDescriptor('Props', ResultFiles)
    ]    
    
    def compute(self):
        propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
        if self.hasInputFromPort('ResultFiles'):
            flist = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
        loader = Hdf5Loader()
        dictlist = loader.GetProperties(flist,proppath=propPath)
        self.setResult('Props', dictlist)
    
class LoadAlpsMeasurements(Module):
    """Load the data from a Monte Carlo simulation from hdf5-files. Description of input ports:
      @ResultFiles: The hdf5-files.
      @Measurements: List of observables to load
      @PropertyPath: Hdf5-path to the parameters stored. Default: /parameters
      @ResultPath: Hdf5-path to the observables stored. Default: /simulation/results"""
  
    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('Measurements',basic.List),
        PortDescriptor('PropertyPath',basic.String),
        PortDescriptor('ResultPath',basic.String)
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
            propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
            resPath= self.getInputFromPort('ResultPath') if self.hasInputFromPort('ResultPath') else "/simulation/results"
            loader = Hdf5Loader()
            if self.hasInputFromPort('ResultFiles'):
                files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
            datasets = []
            if self.hasInputFromPort('Measurements'):
                datasets = loader.ReadMeasurementFromFile(files,measurements=self.getInputFromPort('Measurements'),proppath=propPath,respath=resPath)
            else:
                datasets = loader.ReadMeasurementFromFile(files,measurements=None,proppath=propPath,respath=resPath)
            self.setResult('data',datasets)

class LoadDMFTIterations(Module):
    """Load the data from successive DMFT-Iterations. Description of input ports:
      @ResultFiles: The list of hdf5-files.
      @Observable: Observable to load
      @Measurements: List of measurements of the observable to load
      @PropertyPath: Hdf5-path to the parameters stored. Default: /parameters
      @ResultPath: Hdf5-path to the observables stored. Default: /simulation/iteration"""

    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('Observable',basic.String),
        PortDescriptor('Measurements',basic.List),
        PortDescriptor('PropertyPath',basic.String),
        PortDescriptor('ResultPath',basic.String)
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
            propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
            resPath= self.getInputFromPort('ResultPath') if self.hasInputFromPort('ResultPath') else "/simulation/iteration"
            loader = Hdf5Loader()
            if self.hasInputFromPort('ResultFiles'):
                files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
            if self.hasInputFromPort('Observable'):
                obs = self.getInputFromPort('Observable')
            if self.hasInputFromPort('Measurements'):
                datasets = loader.ReadDMFTIterations(files,observable=obs,measurements=self.getInputFromPort('Measurements'),proppath=propPath,respath=resPath)
            else:
                datasets = loader.ReadDMFTIterations(files,observable=obs,proppath=propPath,respath=resPath)
            self.setResult('data',datasets)

class LoadTimeEvolution(Module):
    """Load the data from successive TEBD-Iterations. Description of input ports:
      @ResultFiles: The hdf5-files.
      @Measurements: List of observables to load
      @GlobalPropertyPath: Hdf5-path to the global parameters stored. Default: /parameters/
      @LocalPropertySuffix: Hdf5-path to the parameters for each timestep. Default: /parameters
      @ResultPath: Hdf5-path to the observables stored. Default: /timesteps/"""

    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('Measurements',basic.List),
        PortDescriptor('GlobalPropertyPath',basic.String),
        PortDescriptor('LocalPropertySuffix',basic.String),
        PortDescriptor('ResultPath',basic.String)
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
            globalproppath= self.getInputFromPort('GlobalPropertyPath') if self.hasInputFromPort('GlobalPropertyPath') else "/parameters"
            localpropsuffix= self.getInputFromPort('LocalPropertySuffix') if self.hasInputFromPort('LocalPropertySuffix') else "/parameters"
            resroot= self.getInputFromPort('ResultPath') if self.hasInputFromPort('ResultPath') else "/timesteps/"
            loader = Hdf5Loader()
            self.getInputFromPort('ResultFiles')
            if self.hasInputFromPort('ResultFiles'):
                files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
            datasets = []
            if self.hasInputFromPort('Measurements'):
                #loop over files
                for f in files:
                    try:
                        #open the file and open the results root group
                        h5file = h5.archive(f, 'r')
                        #enumerate the subgroups
                        L=h5file.list_children(resroot)
                        #Create an iterator of length the number of subgroups
                        stepper=[i+1 for i in range(len(L))]
                        #Read in global props
                        globalprops=loader.GetProperties([f],globalproppath)
                        for d in stepper:
                            #Get the measurements from the numbered subgroups
                            locdata=loader.ReadMeasurementFromFile([f],proppath=resroot+str(d)+localpropsuffix, \
                            respath=resroot+str(d)+'/results', measurements=self.getInputFromPort('Measurements'))
                            #Append the global props to the local props
                            for i in range(len(locdata[0])):
                                  locdata[0][i].props.update(globalprops[0].props)
                            #Extend the total dataset with this data
                            datasets.extend(locdata)
                    except Exception, e:
                        debug.log(traceback.format_exc())
            else:
                #loop over files
                for f in files:
                    try:
                        #open the file and open the results root group
                        h5file = h5.archive(f, 'r')
                        #enumerate the subgroups
                        L=h5file.list_children(resroot)
                        #Create an iterator of length the number of subgroups
                        stepper=[i+1 for i in range(len(L))]
                        #Read in global props
                        globalprops=loader.GetProperties([f],globalproppath)
                        for d in stepper:
                            #Get the measurements from the numbered subgroups
                            locdata=loader.ReadMeasurementFromFile([f],proppath=resroot+str(d)+localpropsuffix, \
                            respath=resroot+str(d)+'/results', measurements=None)
                            #Append the global props to the local props
                            for i in range(len(locdata[0])):
                                  locdata[0][i].props.update(globalprops[0].props)
                            #Extend the total dataset with this data
                            datasets.extend(locdata)
                    except Exception, e:
                        debug.log(traceback.format_exc())
            self.setResult('data',datasets)


class LoadBinningAnalysis(Module):
    """Load the Binning Analysis from hdf5 files. Description of input ports:
      @ResultFiles: The hdf5-files.
      @Measurements: List of observables to load
      @PropertyPath: Hdf5-path to the parameters stored. Default: /parameters
      @ResultPath: Hdf5-path to the observables stored. Default: None"""

    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('Measurements',basic.List),
        PortDescriptor('PropertyPath',basic.String),
        PortDescriptor('ResultPath',basic.String)
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
        propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
        resPath= self.getInputFromPort('ResultPath') if self.hasInputFromPort('ResultPath') else None
        loader = Hdf5Loader()
        if self.hasInputFromPort('ResultFiles'):
            files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
        datasets = []
        if self.hasInputFromPort('Measurements'):
            datasets = loader.ReadBinningAnalysis(files,self.getInputFromPort('Measurements'),propPath,resPath)
        else:
            datasets = loader.ReadMeasurementFromFile(files,propPath,resPath)
        self.setResult('data',datasets)


class LoadAlpsSpectra(Module):
    """Load the Spectrum from hdf5 files. Description of input ports:
      @ResultFiles: The hdf5-files.
      @PropertyPath: Hdf5-path to the parameters stored. Default: /parameters
      @SpectrumPath: Hdf5-path to the spectrum stored. Default: /spectrum"""

    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('PropertyPath',basic.String),
        PortDescriptor('SpectrumPath',basic.String)
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
        propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
        resPath= self.getInputFromPort('SpectrumPath') if self.hasInputFromPort('SpectrumPath') else "/spectrum"
        loader = Hdf5Loader()
        if self.hasInputFromPort('ResultFiles'):
            files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
        datasets = []
        datasets = loader.ReadSpectrumFromFile(files,propPath,resPath)
        self.setResult('data',datasets)
        
class LoadAlpsEigenstateMeasurements(Module):
    """Load the observables of an ED or DMRG-simulation from hdf5 files. Description of input ports:
      @ResultFiles: The hdf5-files.
      @Measurements: List of observables to load
      @PropertyPath: Hdf5-path to the parameters stored. Default: /parameters
      @SpectrumPath: Hdf5-path to the spectrum stored. Default: /spectrum"""

    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('PropertyPath',basic.String),
        PortDescriptor('SpectrumPath',basic.String),
        PortDescriptor('Measurements',basic.List),
        PortDescriptor('index',basic.Integer)        
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
        propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
        resPath= self.getInputFromPort('SpectrumPath') if self.hasInputFromPort('SpectrumPath') else "/spectrum"
        loader = Hdf5Loader()
        if self.hasInputFromPort('ResultFiles'):
            files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
        datasets = []
        if self.hasInputFromPort('Measurements') and self.hasInputFromPort('index'):
            datasets = loader.ReadDiagDataFromFile(files,propPath,resPath, self.getInputFromPort('Measurements'),self.getInputFromPort('index'))
        elif self.hasInputFromPort('Measurements'):
            datasets = loader.ReadDiagDataFromFile(files,propPath,resPath, self.getInputFromPort('Measurements'))
        elif self.hasInputFromPort('index'):
            datasets = loader.ReadDiagDataFromFile(files,propPath,resPath,None,self.getInputFromPort('index'))
        else:
            datasets = loader.ReadDiagDataFromFile(files,propPath,resPath)
            
        self.setResult('data',datasets)

class LoadAlpsIterationMeasurements(Module):
    """Load the data from successive MPS-Iterations. Description of input ports:
      @ResultFiles: The hdf5-files.
      @Measurements: List of observables to load
      @PropertyPath: Hdf5-path to the parameters stored. Default: /parameters
      @SpectrumPath: Hdf5-path to the spectrum stored. Default: /spectrum"""

    my_input_ports = [
        PortDescriptor('ResultFiles',ResultFiles),
        PortDescriptor('PropertyPath',basic.String),
        PortDescriptor('SpectrumPath',basic.String),
        PortDescriptor('Measurements',basic.List)
    ]
    
    my_output_ports = [
        PortDescriptor('data',DataSets)
    ]    
    
    def compute(self):
        propPath= self.getInputFromPort('PropertyPath') if self.hasInputFromPort('PropertyPath') else "/parameters"
        resPath= self.getInputFromPort('SpectrumPath') if self.hasInputFromPort('SpectrumPath') else "/spectrum"
        loader = Hdf5Loader()
        if self.hasInputFromPort('ResultFiles'):
            files = [f.props["filename"] for f in self.getInputFromPort('ResultFiles')]
        what = None
        if self.hasInputFromPort('Measurements'):
            what = self.getInputFromPort('Measurements')
        
        datasets = loader.ReadDiagDataFromFile(files,proppath=propPath,respath=resPath,
                                               measurements=what,loadIterations=True)
        self.setResult('data',datasets)

class GroupDataSets(Module):
    """
    Group a list of DataSet instances into a hierchical list according to some choice of properties.
    
    HIERARCHICAL LISTS
    
    Hierarchical lists (hlists) allow a more structured storage of a set of DataSets using nested lists.
    For example, a simulation could be performed for a range of two parameters, t \in {1,2}, V \in {-1,-2}.
    The results could then be organized by 't':
    [
     [x=[] y=[] props={'t': 2, 'V': -1},
      x=[] y=[] props={'t': 2, 'V': -2}
     ], [
      x=[] y=[] props={'t': 1, 'V': -1},
      x=[] y=[] props={'t': 1, 'V': -2}
     ]
    ]
    This would simplify operations such as finding the minimal y for a given t etc.
    
    The ALPS VisTrails package provides several modules to deal with such lists:
     * GroupDataSets deepends the hierarchy by grouping according to some property.
     * Flatten will make a flat list of a hierarchical list of any depth.
     * TransformGroupedDataSets can perform operations at a controllable depth of the hierarchy.
    
    The GroupDataSets module
    
    This module will group DataSet instances at the lowest level of the existing list, according
    to the properties given in 'for-each'.
    Note that regardless of how many properties are provided, the depth of the list will
    only grow by one level. If you want a separate level for each property, you will need
    to use several GroupDataSets modules connected in a chain.
    """
    my_input_ports = [
        PortDescriptor('for-each',basic.List),
        PortDescriptor('input',DataSets)
    ]
    my_output_ports = [
        PortDescriptor('output',DataSets)
    ]
    
    def compute(self):
        if self.hasInputFromPort('input'):
            groups = self.getInputFromPort('input')
            dd = depth(groups)
            
            if dd > 1:
                hgroups = flatten(groups, -1)
                hgroups_idcs = hgroups.indices()
            else:
                hgroups = [groups]
                hgroups_idcs = [0]
            
            for idx in hgroups_idcs:
                sets = hgroups[idx]
                
                for_each = []
                if self.hasInputFromPort('for-each'):
                    for_each = self.getInputFromPort('for-each')
                
                for_each_sets = {}
                for iset in sets:
                    fe_par_set = tuple((iset.props[m] for m in for_each))
                    
                    if fe_par_set in for_each_sets:
                        for_each_sets[fe_par_set].append(iset)
                    else:
                        for_each_sets[fe_par_set] = [iset]
                
                hgroups[idx] = for_each_sets.values()
            
            if dd > 1:
                self.setResult('output', groups)
            else:
                self.setResult('output', hgroups[0])
                
        else:
            raise EmptyInputPort('for-each || observable')

class CollectDataSets(Module):
    """
    Collect data from a list of DataSet instances to obtain XY plot.
    
    An example of the usage of CollectDataSets is the following: given the results
    of a simulation for of some parameters V, L, we would like
    to make a plot of the energy versus the parameter V, for each possible value of L
    The input is a list of DataSets:
    [
      x=[0] y=[-0.13] props={'observable': 'energy', 'V':0, 'L':8},
      x=[0] y=[-0.15] props={'observable': 'energy', 'V':1, 'L':8},
      x=[0] y=[0.28] props={'observable': 'magnetization', 'V':0, 'L':8},
      x=[0] y=[0.31] props={'observable': 'magnetization', 'V':1, 'L':8},
      
      x=[0] y=[-0.18] props={'observable': 'energy', 'V':0, 'L':12},
      x=[0] y=[-0.2] props={'observable': 'energy', 'V':1, 'L':12},
      x=[0] y=[0.33] props={'observable': 'magnetization', 'V':0, 'L':12},
      x=[0] y=[0.41] props={'observable': 'magnetization', 'V':1, 'L':12},
    ]
    We would like to collect this into the list:
    [
      x=[0, 1] y=[-0.13, -0.15] props={'observable': 'energy, 'L': 8}
      x=[0, 1] y=[-0.18, -0.2] props={'observable': 'energy, 'L': 12}
    ]
    which we can plot as two lines in a plot E vs V.
    
    This can be achieved by providing the following parameters to CollectDataSets:
     * for-each: ['L']
     * y: 'energy'
     * x: 'V'
    
    A label will automatically be generated.
    """
    my_input_ports = [
        PortDescriptor('for-each',basic.List),
        PortDescriptor('y',basic.String),
        PortDescriptor('x',basic.String),
        PortDescriptor('input',DataSets)
    ]
    my_output_ports = [
        PortDescriptor('output',DataSets)
    ]
    
    def compute(self):
        if self.hasInputFromPort('y') \
        and self.hasInputFromPort('x') \
        and self.hasInputFromPort('input'):
            # find all possible values for each for-each
            sets = self.getInputFromPort('input')
            observable = self.getInputFromPort('y')
            versus = self.getInputFromPort('x')
            
            for_each = []
            if self.hasInputFromPort('for-each'):
                for_each = self.getInputFromPort('for-each')
            
            self.setResult('output',pyalps.collectXY(sets,versus,observable,for_each))
                
        else:
            raise EmptyInputPort('for-each || observable')
