# VisTrails package for ALPS, Algorithms and Libraries for Physics Simulations
#
# Copyright (C) 2009 - 2010 by Matthias Troyer <troyer@itp.phys.ethz.ch>,
#                              Synge Todo <wistaria@comp-phys.org>
#
# Distributed under the Boost Software License, Version 1.0. (See accompany-
# ing file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
#
##############################################################################

import core.bundles
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry

import alpscore
import alpsparameters
import plots
import tools
import os
import system
import glob
import copy

from packages.vtlcreator.init import VtlFileCreator
from vistrails.core.modules.vistrails_module import ModuleError
from plots import PlotFile
from pyalps.plot_core import *
from dataset import DataSets, ResultFiles

basic = vistrails.core.modules.basic_modules

##############################################################################


class RunAlpsApplication(alpscore.SystemCommandLogged):
    """ Runs an ALPS application using a set of XML files as input """

    def get_path(self,appname):
        return alpscore._get_path(appname)

    def get_app_name(self):
        if self.hasInputFromPort('application'):
          fn = self.getInputFromPort('application')
          return self.get_path(fn.name)
        else:
          if self.appname != '':
            return self.get_path(self.appname)
          else: 
             raise ModuleError(self, 'No application specified')

    def num_procs(self):
        if self.hasInputFromPort('num_processes'):
          np = self.getInputFromPort('num_processes')
        else:
          np = alpscore._get_default_mpi_procs()
        return np

    def getoptions(self):
        options = copy.deepcopy(self.options)
        if self.hasInputFromPort('tmin'):
            options += ['--Tmin', str(self.getInputFromPort('tmin'))]
        if self.hasInputFromPort('tmax'):
            options += ['--Tmax', str(self.getInputFromPort('tmax'))]
        if self.hasInputFromPort('write_xml'):
          if self.getInputFromPort('write_xml'):
            options += ['--write-xml']
        return options
    
    def compute(self):
        input_file = self.getInputFromPort('input_file')
        result = basic.File()
        result.name = input_file.name.replace('.in.xml', '.out.xml')
        resultdir = basic.Directory()
        resultdir.name = os.path.dirname(result.name)
        an = self.get_app_name()
        if not os.path.isfile(an):
            raise ModuleError(self, "Application '%s' not existent" % an)
        if self.num_procs()>1:
            cmdline = alpscore._get_mpi_run()+[str(self.num_procs()),an,"--mpi"]
        else:
            cmdline = [an]
        cmdline += self.getoptions()
        if self.hasInputFromPort('continue'):
            cmdline += [result.name]
        else:
            cmdline += [input_file.name]
        f = file(os.path.join(resultdir.name,'workflow.vtl'),'w')
        f.write(VtlFileCreator.generate_vtl(self.moduleInfo['locator'],self.moduleInfo['version'],self.moduleInfo['pipeline']))
        f.close()
        self.execute(cmdline)
        self.setResult('output_file', result)
        self.setResult('output_dir', resultdir)
        
    _input_ports = [('input_file', [basic.File]),
                    ('tmin', [basic.Integer]),
                    ('tmax', [basic.Integer]),
                    ('continue', [basic.Boolean]),
                    ('application', [basic.File]),
                    ('num_processes',[basic.Integer]),
                    ('write_xml',[basic.Boolean])
                    ]
    _output_ports = [('output_file', [basic.File]),
                     ('output_dir', [basic.Directory]),
                     ('log_file',[basic.File])]
    appname=''
    options=[]
                         
class RunSpinMC(RunAlpsApplication):
    """Runs the spinmc classical Monte Carlo application """
    appname = 'spinmc'

class RunLoop(RunAlpsApplication):
    """Runs the loop quantum Monte Carlo application """
    def getoptions(self):
        options = ['--auto-evaluate']
        if self.hasInputFromPort('tmin'):
            options += ['--report-interval', str(self.getInputFromPort('tmin'))]
        return options
    appname = 'loop'

    
class RunDirLoopSSE(RunAlpsApplication):
    """Runs the dirloop_sse quantum Monte Carlo application """
    appname = 'dirloop_sse'

class RunWorm(RunAlpsApplication):
    """Runs the worm quantum Monte Carlo application """
    appname = 'worm'

class RunDWA(RunAlpsApplication):
    """Runs dwa quantum Monte Carlo application """
    appname = 'dwa'

class RunFullDiag(RunAlpsApplication):
    """Runs the fulldiag exact diagonalization application """
    appname = 'fulldiag'
    options = ['--Nmax', '1']

class RunSparseDiag(RunAlpsApplication):
    """Runs the sparsediag exact diagonalization application """
    appname = 'sparsediag'
    options = ['--Nmax', '1']

class RunDMRG(RunAlpsApplication):
    """Runs the DMRG application """
    appname = 'dmrg'
    options = ['--Nmax', '1']

class RunMPSOptim(RunAlpsApplication):
    """Runs the MPS optimization application """
    appname = 'mps_optim'

class RunMPSEvolve(RunAlpsApplication):
    """Runs the MPS time evolution application """
    appname = 'mps_evolve'

class RunQWL(RunAlpsApplication):
    """Runs the qwl quantum Monte Carlo application """
    appname = 'qwl'
            
class RunDMFT(alpscore.SystemCommandLogged,tools.GetSimName):
    """Runs the DMFT quantum Monte Carlo application """
    def compute(self):
        tmp = self.interpreter.filePool.create_file()
        os.unlink(tmp.name)
        os.mkdir(tmp.name)
        resultdir = basic.Directory()
        resultdir.name = tmp.name
        id = self.getInputFromPort('fileID')
        paraminput = self.getInputFromPort('dmftparams')
        c=0
        for parms in paraminput:
            f = file(os.path.join(resultdir.name,id+str(c)),'w')
            for key in parms:
                value = parms[key]
                if type(value) == str:
                    f.write(str(key)+' = "' + value + '"\n')
                else:
                    f.write(str(key)+' = ' + str(value) + '\n')
            f.close()
            self.execute([alpscore._get_path('dmft'),f.name])
            c=c+1
        self.setResult('dir',resultdir)
    _input_ports = [('dmftparams',[alpsparameters.Parameters]),
                    ('fileID', [basic.String])]
    _output_ports = [('dir', [basic.Directory])]


class RunTEBD(RunAlpsApplication):
    """Runs the TEBD application """
    appname = 'tebd'

    def compute(self):
        input_files = self.getInputFromPort('input_files')
        result = basic.File()
        result.name = input_files[0].replace('.nml', '.h5')
        resultdir = basic.Directory()
        resultdir.name = os.path.dirname(result.name)
        for input_file in input_files:
            cmdline=[self.get_app_name()]
            cmdline += [input_file]
            self.execute(cmdline)
        self.setResult('output_file', result)
        self.setResult('output_dir', resultdir)

    _input_ports = [('input_files', [basic.File])]
    _output_ports = [('output_dir', [basic.Directory])]
    
class AlpsEvaluate(alpscore.SystemCommandLogged):
    def get_appname(self):
        if self.hasInputFromPort('application'):
          return alpscore._get_path(self.getInputFromPort('application'))
        else:
          if self.appname != '':
            return alpscore._get_path(self.appname)
          else: 
             raise ModuleError(self, 'No application specified')
          
    def compute(self):
        an = self.get_appname()
        if not os.path.isfile(an):
            raise ModuleError(self, "Application '%s' not existent" % an)
        cmdlist = [an]
        cmdlist += self.options
        for port_name in self.inputPorts:
           if port_name != 'files' and port_name != 'file' and port_name != 'application' and self.hasInputFromPort(port_name):
             cmdlist += ['--'+str(port_name),str(self.getInputFromPort(port_name))]
        rf = self.getInputFromPort('files')
        infiles = [x.props['filename'] for x in rf]
        cmdlist += infiles
        self.execute(cmdlist)
        datasetmap = {}
        datasets = []
        for infile in infiles:
          ofname = infile.replace('.out.xml', '.plot.*.xml')
          l = glob.glob(ofname)
          for fn in l:
            dataset = read_xml(fn)
            datasets.append(dataset)
            ylabel = dataset.props['ylabel']
            if ylabel in datasetmap:
              datasetmap[ylabel].append(dataset)
            else:
              datasetmap[ylabel] = [dataset]
              
        for (port_name,ylabel) in self.plots:
          if ylabel in datasetmap:
            self.setResult(port_name,datasetmap[ylabel])
          else:
            self.setResult(port_name,[])
          
    _input_ports = [('file',[basic.File],True),
                    ('files',[ResultFiles]),
                    ('application',[basic.File])]
    _output_ports = [('all',[DataSets])]
    appname = ''
    options = []

class EvaluateFullDiagVersusT(AlpsEvaluate):
    """ 
    Runs the evaluation application to produce plots from the spectra calculated by fulldiag as a function of temperature. The input parameters are:
    
    T_MIN the lower end of the temperature range
    T_MAX the upper end of the temperature range
    DELTA_T the spacing between temperature points
    
    The code produces datasets for a number of different quantities as a function of temperature: energy, free energy, entropy, specific heat. 
    For spin models (models with an Sz quantum number) is also calculates uniform susceptibility and magnetization.
    For particle models (models with an N quantum number) is also calculates compressibility and particle number.
    """
    appname = 'fulldiag_evaluate'
    _input_ports = [('T_MIN',[basic.Float]),
                    ('T_MAX',[basic.Float]),
                    ('DELTA_T',[basic.Float]),
                    ('application',[basic.File],True)]
    plots = [('energy','Energy Density'), 
             ('free_energy','Free Energy Density'),
             ('entropy','Entropy Density'),
             ('specific_heat','Specific Heat per Site'),
             ('uniform_susceptibility','Uniform Susceptibility per Site'),
             ('magnetization','Magnetization per Site'),
             ('compressibility','Compressibility per Site'),
             ('particle_number','Particle number per Site')]


class EvaluateFullDiagVersusH(AlpsEvaluate):
    """ 
    Runs the evaluation application to produce plots from the spectra calculated by fulldiag as a function of magnetic field. The input parameters are:
    
    H_MIN the lower end of the field range
    H_MAX the upper end of the field range
    DELTA_H the spacing between field points
    
    The code produces datasets for a number of different quantities as a function of temperature: energy, free energy, entropy, specific heat. 
    For spin models (models with an Sz quantum number) is also calculates uniform susceptibility and magnetization.
    """
    appname = 'fulldiag_evaluate'
    options = ['--versus', 'h']
    _input_ports = [('H_MIN',[basic.Float]),
                    ('H_MAX',[basic.Float]),
                    ('DELTA_H',[basic.Float]),
                    ('application',[basic.File],True)]
    plots = [('energy','Energy Density'), 
             ('free_energy','Free Energy Density'),
             ('entropy','Entropy Density'),
             ('specific_heat','Specific Heat per Site'),
             ('uniform_susceptibility','Uniform Susceptibility per Site'),
             ('magnetization','Magnetization per Site')]


class EvaluateLoop(alpscore.SystemCommandLogged,tools.GetSimName):
    """ 
    Runs the evaluation tool of the loop application to evaluate all measurements. This is only needed if the application was not run using the --auto-evaluate option. 
    Note that --auto-evaluate that is automatically used if run by the RunLoop module and this module is thus not needed for pure VisTrails workflows.
    """
    def compute(self):
        name = self.get_sim_name(self.getInputFromPort('dir').name)
        self.execute([alpscore._get_path('loop'),'--evaluate',name])
        self.setResult('dir',self.getInputFromPort('dir'))
    _input_ports = [('dir', [basic.Directory])]
    _output_ports = [('dir', [basic.Directory])]
    
class EvaluateSpinMC(alpscore.SystemCommandLogged,tools.GetSimName):
    def compute(self):
        name = self.get_sim_name(self.getInputFromPort('dir').name)
        taskname = name.replace('.out.xml', '.task*.out.xml')
        tasklist = glob.glob(taskname)
        self.execute([alpscore._get_path('spinmc_evaluate')]+tasklist)
        self.setResult('dir',self.getInputFromPort('dir'))
    _input_ports = [('dir', [basic.Directory])]
    _output_ports = [('dir', [basic.Directory])]

class EvaluateQWL(AlpsEvaluate):
    """ 
    Runs the evaluation application to produce plots from the density of states calculated by qwl as a function of temperature. The input parameters are:
    
    T_MIN the lower end of the temperature range
    T_MAX the upper end of the temperature range
    DELTA_T the spacing between temperature points
    
    The code produces datasets for a number of different quantities as a function of temperature: energy, free energy, entropy, specific heat, uniform susceptibility, and uniform and staggered structure factor.
    """
    appname = 'qwl_evaluate'
    _input_ports = [('T_MIN',[basic.Float]),
                    ('T_MAX',[basic.Float]),
                    ('DELTA_T',[basic.Float]),
                    ('application',[basic.File],True)]
    plots = [('energy','Energy Density'), 
             ('free_energy','Free Energy Density'),
             ('entropy','Entropy Density'),
             ('specific_heat','Specific Heat per Site'),
             ('uniform_susceptibility','Uniform Susceptibility per Site'),
             ('staggered_structure_factor','Staggered Structure Factor per Site'),
             ('uniform_structure_factor','Uniform Structure Factor per Site')]



  
def initialize(): pass

def register_parameters(type, ns="Applications"):
  reg = vistrails.core.modules.module_registry.get_module_registry()
  reg.add_module(type,namespace=ns)
  reg.add_output_port(type, "value", type)


def register_application(type):
  reg = vistrails.core.modules.module_registry.get_module_registry()
  reg.add_module(type,namespace="Applications")
  reg.add_input_port(type,'application',[basic.File],False)

def register_evaluation(type):
  reg = vistrails.core.modules.module_registry.get_module_registry()
  reg.add_module(type,namespace="Applications")
  reg.add_output_port(type,'all',[DataSets])
  for (port_name,ylabel) in type.plots:
    reg.add_output_port(type,port_name,[DataSets])
  reg.add_output_port(type,'log_file',[basic.File])
  

def selfRegister():

  reg = vistrails.core.modules.module_registry.get_module_registry()
  
#  register_parameters(system.SimulationID)
  
  reg.add_module(RunAlpsApplication,namespace="Applications")
  
  register_application(RunSpinMC)
  register_application(RunLoop)
  register_application(RunWorm)
  register_application(RunDWA)
  register_application(RunDirLoopSSE)
  register_application(RunFullDiag)
  register_application(RunSparseDiag)
  register_application(RunDMRG)
  register_application(RunMPSOptim)
  register_application(RunMPSEvolve)
  register_application(RunQWL)
  register_application(RunDMFT)
  register_application(RunTEBD)
  
  reg.add_module(AlpsEvaluate,namespace="Applications",abstract=True)
  
  register_evaluation(EvaluateFullDiagVersusT)
  register_evaluation(EvaluateFullDiagVersusH)
  register_application(EvaluateLoop)
  register_application(EvaluateSpinMC)
  register_evaluation(EvaluateQWL)
  
  register_parameters(system.SimulationName)

  reg.add_module(system.LatticeModel,namespace="Applications")
  reg.add_module(system.PrepareMonteCarlo,namespace="Applications")
  reg.add_module(system.PrepareDiagonalization,namespace="Applications")
  reg.add_module(system.PrepareDMRG,namespace="Applications")
  reg.add_module(system.PrepareDMFT,namespace="Applications")
  reg.add_module(system.PrepareTEBD,namespace="Applications")
  reg.add_module(system.PrepareMPS,namespace="Applications")
