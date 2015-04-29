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

from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable
import vistrails.core.modules.basic_modules as basic
import vistrails.core.modules.module_registry
import copy

import parameters
from parameters import Parameters, ParametersData

##############################################################################

class SystemParameters(Parameters):
   """ A dictionary of parameters defining a model and lattice and all their parameters 
   """

class MonteCarloMeasurements(Parameters):
    """ a module to specify measurements for Monte Carlo simulations. One can turn on certain measurements. This is supported at the moment by the dirloop_sse and worm application. """
    def setFromPort(self,port_name,res):
        if self.hasInputFromPort(port_name):
          val  = self.getInputFromPort(port_name)
          if type(val) == bool:
            res.set('MEASURE['+port_name+']',val)
          else:
            res.set(port_name,val)
        return res
            
    _input_ports = [('Correlations',[(basic.Boolean, 'the spin or density correlations')]),
                   ('Structure Factor',[(basic.Boolean, 'the spin or density structure factor')]),
                   ('Green Function',[(basic.Boolean, 'the Green function')]),
                   ('Site Type Density',[(basic.Boolean, 'the density at each type of site')]),
                   ('Bond Type Stiffness',[(basic.Boolean, 'the stiffness for each type of bond function')])
                   ]

class MonteCarloParameters(Parameters): 
    """ A module to set the parameters for a Monte Carlo simulation: 
      SWEEPS: the number of sweeps for measurements 
      THERMALIZATION: the number of sweeps for thermailzation  
    """
    _input_ports = [('SWEEPS',[(basic.String, 'the number of sweeps for measurements')]),
                    ('THERMALIZATION',[(basic.String, 'the number of sweeps for thermalization')]),
                    ('SKIP',[(basic.String, 'the number of sweeps per measurement performed')])
                    ]

class LoopMonteCarloParameters(MonteCarloParameters): 
    """ A module to set the parameters for a loop quantum Monte Carlo simulation: 
      SWEEPS: the number of sweeps for measurements 
      THERMALIZATION: the number of sweeps for thermailzation 
      ALGORITHM:  the specific representation and loop algorithm used. Default is sse. See the loop documentation for more options
    """
    def compute(self):
        res = self.readInputs(ParametersData({}))
        res.updateIfMissing(self.defaults)
        self.setResult('value',res.toBasic())
    _input_ports = [('ALGORITHM',[(basic.String, 'the algorithm to be used, default sse')])]
    defaults = { 'ALGORITHM':'sse' }

class QWLMonteCarloParameters(MonteCarloParameters): 
    """ A module to set the parameters for a qwl simulation. Please see the ALPS documentation for qwl for an explanation of these parameters """
    _input_ports = [('T_MIN',[basic.String]),
                    ('T_MAX',[basic.String]),
                    ('DELTA_T',[basic.String]),
                    ('CUTOFF',[basic.String]),
                    ('MEASURE_MAGNETIC_PROPERTIES',[basic.String]),
                    ('NUMBER_OF_WANG_LANDAU_STEPS',[basic.String],True),
                    ('USE_ZHOU_BHATT_METHOD',[basic.String],True),
                    ('FLATNESS_TRESHOLD',[basic.String],True),
                    ('BLOCK_SWEEPS',[basic.String],True),
                    ('INITIAL_MODIFICATION_FACTOR',[basic.String],True),
                    ('EXPANSION_ORDER_MINIMUM',[basic.String],True),
                    ('EXPANSION_ORDER_MAXIMUM',[basic.String],True),
                    ('START_STORING',[basic.String],True)
                    ]
class DMFTMonteCarloParameters(MonteCarloParameters): 
    """ A module to set the temperature """
    _input_ports = [('SEED',[basic.String]),
                    ('MAX_TIME',[basic.String]),
                    ('MAX_IT',[basic.String]),
                    ('BETA',[basic.String]),
                    ('SITES',[basic.String]),
                    ('N',[basic.String],True),
                    ('NMATSUBARA',[basic.String]),
                    ('U',[basic.String]),
                    ('t' ,[basic.String]),
                    ('MU',[basic.String]),
                    ('H',[basic.String]),
                    ('H_INIT',[basic.String]),
                    ('TOLERANCE',[basic.String]),
                    ('CONVERGED',[basic.String]),
                    ('SYMMETRIZATION',[basic.String]),
                    ('ANTIFERROMAGNET',[basic.String]),
                    ('SOLVER',[basic.String]),
                    ('FLAVORS',[basic.String]),
                    ('OMEGA_LOOP',[basic.String]),
                    ('CHECKPOINT',[basic.String]),
                    ('F',[basic.String]),
                    ('N_ORDER' ,[basic.String]),
                    ('N_MEAS',[basic.String]),
                    ('N_SHIFT',[basic.String]),
                    ('N_FLIP',[basic.String]),
                    ('N_MOVE',[basic.String]),
                    ('OVERLAP',[basic.String]),
                    ('OVERLAP',[basic.String]),
                    ('CONVERGENCE_CHECK_PERIOD',[basic.String]),
                    ('MEASUREMENT_PERIOD' ,[basic.String]),
                    ('NRUNS',[basic.String]),
                    ('RECALC_PERIOD',[basic.String]),
                    ('HISTOGRAM_MEASUREMENT',[basic.String]),
                    ('NSELF',[basic.String]),
                    ('ALPHA',[basic.String]),
                    ('J',[basic.String]),
                    ('NMATSUBARA_MEASUREMENTS',[basic.String]),
                    ('t0',[basic.String]),
                    ('t1',[basic.String])
                    ]

class DMFTMonteCarloSolverParameters(MonteCarloParameters):
    """ Collect parameters to the DMFT MC solvers. """
    _input_ports = [
        ('SEED',[basic.String]),
        ('BETA',[basic.String]),
        ('CHECKPOINT',[basic.String]),

        ('SOLVER',[basic.String]),
        ('N',[basic.String],True),
        ('N_ORDER' ,[basic.String]),
        ('N_MEAS',[basic.String]),
        ('MAX_TIME',[basic.String]),
        ('MAX_IT',[basic.String])
    ]

class DMFTModelParameters(Parameters):
    """ Define the model for a DMFT simulation. """
    _input_ports = [
        ('U',[basic.String]),
        ('t' ,[basic.String]),
        ('t0',[basic.String]),
        ('t1',[basic.String]),
        ('MU',[basic.String]),
        ('H',[basic.String]),
        ('H_INIT',[basic.String]),
        ('J',[basic.String]),
        ('SITES',[basic.String]),
        ('FLAVORS',[basic.String])
    ]

class DMFTSelfConsistencyParameters(Parameters):
    """ Parameters for the DMFT self-consistency loop """
    _input_ports = [
        ('NMATSUBARA',[basic.String]),
        ('SC_WRITE_DELTA',[basic.String]),
        ('TOLERANCE',[basic.String]),
        ('CONVERGED',[basic.String]),
        ('OMEGA_LOOP',[basic.String]),
        ('HISTOGRAM_MEASUREMENT',[basic.String]),
        ('SYMMETRIZATION',[basic.String]),
        ('ANTIFERROMAGNET',[basic.String])
    ]

class ClassicalMonteCarloParameters(MonteCarloParameters): 
    """ A module to set the parameters for a loop quantum Monte Carlo simulation: 
      SWEEPS: the number of sweeps for measurements 
      THERMALIZATION: the number of sweeps for thermailzation 
      UPDATE: the update type (local or cluster)
    """
    _input_ports = [('UPDATE',[(basic.String, 'the update method (local or cluster)')])]


class DMRGParameters(Parameters): 
    """ 
    A module to set the parameters for a DMRG simulation:
      SWEEPS: the number of sweeps
      STATES: a comma-separated list of states used in each of the sweeps
      MAXSTATES: an alternatiove to SWEEPS< the maximum number of states used in the last sweep. The number of states is ramped up linearly.
      NUMBER_EIGENVALUES: the number of eigenstates to target for
    """
    _input_ports = [('SWEEPS',[(basic.String, 'the number of sweeps')]),
                    ('STATES',[(basic.String, 'the number of states in each sweep')]),
                    ('MAXSTATES',[(basic.String, 'the maximum number of states')]),
                    ('NUMBER_EIGENVALUES',[(basic.String, 'the number of eigenvalues to compute')])
                    ]


class TEBDParameters(Parameters): 
    """ 
    A module to set the parameters for a TEBD simulation:
    """
    _input_ports = [('ITP_CHIS',[basic.String]),
                   ('ITP_DTS',[basic.String]),
                   ('ITP_CONVS',[basic.String]),
                   ('CHI_LIMIT',[basic.String]),
                   ('TRUNC_LIMIT',[basic.String]),
                   ('NUM_THREADS',[basic.String]),
                   ('TAUS',[basic.String]),
                   ('POWS',[basic.String]),
                   ('GS',[basic.String]),
                   ('GIS',[basic.String]),
                   ('GFS',[basic.String]),
                   ('NUMSTEPS',[basic.String]),
                   ('VERBOSE',[basic.String]),
                   ('STEPSFORSTORE',[basic.String]),
                   ('SIMID',[basic.String]),
                    ('INITIAL_STATE',[basic.String])
                    ]

class MPSParameters(Parameters): 
    """ parameters for MPS simulations """

class MPSOptimParameters(MPSParameters): 
    """ 
    A module to set the parameters for a MPS optimization simulation
    """
    _input_ports = [('SWEEPS',[(basic.String, 'the number of sweeps')]),
                    ('STATES',[(basic.String, 'the number of states in each sweep')]),
                    ('MAXSTATES',[(basic.String, 'the maximum number of states')]),
                    ('NUMBER_EIGENVALUES',[(basic.String, 'the number of eigenvalues to compute')])
                    ]

class MPSEvolveParameters(MPSParameters): 
    """ 
    A module to set the parameters for a MPS time evolution simulation:
      DT : the length of a timesteps
      TIMESTEPS : the number of timesteps
      IMG_TIMESTEPS : the number of initial imaginary time steps
      MAXSTATES : the maximum bond dimension
      always_measure : comma-separeted list of measurement to compute during time evolution
      measure_each : number of timesteps to skip between measurements
      chkp_each : number of timesteps to skip between checkpoints
      update_each : number of timesteps to skip between changes in the parameters
      COMPLEX : use complex numbers
    """
    def compute(self):
        self.setOutput(self.readInputs(ParametersData({'COMPLEX':'1'})))
    _input_ports = [('DT',[basic.String]),
                    ('TIMESTEPS',[basic.String]),
                    ('IMG_TIMESTEPS',[basic.String]),
                    ('MAXSTATES',[basic.String]),
                    ('always_measure',[basic.String]),
                    ('measure_each',[basic.String]),
                    ('chkp_each',[basic.String]),
                    ('update_each',[basic.String]),
                    # ('COMPLEX', [basic.String], {'defaults': str(['1'])}),
                    ]


class Temperature(Parameters):
    """ A module to set the temperature. Either T or beta=1/T can be defined but not both. """
    def compute(self):
        if self.hasInputFromPort('T') and self.hasInputFromPort('beta'):
            raise ModuleError(self, "cannot define both T and beta")
        self.setOutput(self.readInputs(ParametersData({})))
    _input_ports = [('T',[(basic.String, 'the temperature')]),
                   ('beta',[(basic.String, 'the inverse temperature')])]


class ConservedQuantumNumbers(Parameters):
    """ defines conserved quantum numbers for exact diagonalization. This is  string of comma-separated names """
    _input_ports = [('CONSERVED_QUANTUMNUMBERS', [basic.String])]


class CustomMeasurements(Parameters): 
    """ A collection of custom measurements for diagonalization and DMRG """


class CustomMeasurement(basic.Module):
    def compute(self):
        key = 'MEASURE_'+ self.prefix+'['+str(self.getInputFromPort('name'))+']'
        self.setResult('value',{key : self.getInputFromPort('definition')})
    _input_ports = [('name',[(basic.String, 'the name of the measurement')]),
                    ('definition',[(basic.String, 'the operator to be measured')])]
    _output_ports=[('value', [CustomMeasurements])]


class AverageMeasurement(CustomMeasurement): 
    """
    The defintion of an average measurements, averaged over all bonds or sites. The operator name used in the defintiion needs to be defined as a site or bond operator in the model.
    """
    prefix = 'AVERAGE'

class LocalMeasurement(CustomMeasurement): 
    """
    The defintion of a local measurement on each bond or site. The operator name used in the defintiion needs to be defined as a site or bond operator in the model.
    """
    prefix = 'LOCAL'

class CorrelationsMeasurement(CustomMeasurement): 
    """
    The defintion of a correlation measurement. If the correlation is symmetric, e.g. density-density, then just one operator name ahs to be given as in "n". On the other hand, for non-summetric measurements like S^+_i S^-_j the two operators need to be separated by a colon as in "Splus:Sminus". The operator names used in the defintiion needs to be defined as a site or bond operator in the model.
    """
    prefix = 'CORRELATIONS'
                   
class StructureFactorMeasurement(CustomMeasurement): 
    """
    The defintion of a structure factor measurement. If the correlation is symmetric, e.g. density-density, then just one operator name ahs to be given as in "n". On the other hand, for non-summetric measurements like S^+_i S^-_j the two operators need to be separated by a colon as in "Splus:Sminus". The operator names used in the defintiion needs to be defined as a site or bond operator in the model.
    """
    prefix = 'STRUCTURE_FACTOR'

class OverlapMeasurement(basic.Module):
    """
    The defintion of an overlap measurement <bra | ket>, where |ket> is the current state in the simulation, and |bra> is a reference state.
      name: the name of the measurement.
      chkpfile: the checkpoint file containing the |bra> state.
    """
    def compute(self):
        key = 'MEASURE_OVERLAP['+str(self.getInputFromPort('name'))+']'
        self.setResult('value',{key : self.getInputFromPort('chkpfile').name})
    _input_ports = [('name',[basic.String]),
                    ('chkpfile',[basic.File])]
    _output_ports=[('value', [CustomMeasurements])]


class MPSInitialState(parameters.FixedAndDefaultParameters): 
   """ Initial state for MPS simulations """

class RandomInitialState(MPSInitialState):
    """ fill all quantum number sectors with random numbers """
    fixed = {'init_state': 'default'}

class InitialStateFromFile(MPSInitialState):
    """ fill all quantum number sectors with random numbers """
    _input_ports = [('initfile',[(basic.File, 'the initial state')])]
    fixed = {'init_state': 'default'}
    
class InitialProductState(MPSInitialState):
    """ use a product state as initial state
        Define parameters initial_local_QN='a1,a2,a3,...' for each
        quantum number QN needed for the definition of the model.
    """
    fixed = {'init_state': 'local_quantumnumbers'}


def register_parameters(type, ns="Parameters"):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    reg.add_module(type,namespace=ns)
    reg.add_output_port(type, "value", type)

def register_abstract_parameters(type, ns="Parameters"):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    reg.add_module(type,namespace=ns,abstract=True)
    reg.add_output_port(type, "value", type)
  
def initialize(): pass

def selfRegister():

  reg = vistrails.core.modules.module_registry.get_module_registry()

  register_parameters(SystemParameters,"Parameters")

  register_parameters(MonteCarloMeasurements)
  register_parameters(MonteCarloParameters)
  register_parameters(DMRGParameters)
  register_parameters(TEBDParameters)
  register_abstract_parameters(MPSParameters)
  reg.add_module(MPSOptimParameters,namespace="Parameters")
  reg.add_module(MPSEvolveParameters,namespace="Parameters")
  reg.add_module(LoopMonteCarloParameters,namespace="Parameters")
  reg.add_module(ClassicalMonteCarloParameters,namespace="Parameters")
  reg.add_module(QWLMonteCarloParameters,namespace="Parameters")
  reg.add_module(DMFTMonteCarloParameters,namespace="Parameters")

  register_parameters(Temperature)
  
  register_parameters(ConservedQuantumNumbers)
  register_abstract_parameters(CustomMeasurements)
  reg.add_module(CustomMeasurement,namespace="Parameters",abstract=True)
  reg.add_module(LocalMeasurement,namespace="Parameters")
  reg.add_module(AverageMeasurement,namespace="Parameters")
  reg.add_module(CorrelationsMeasurement,namespace="Parameters")
  reg.add_module(StructureFactorMeasurement,namespace="Parameters")
  reg.add_module(OverlapMeasurement,namespace="Parameters")
  
  register_abstract_parameters(MPSInitialState)
  reg.add_module(RandomInitialState,namespace="Parameters")
  reg.add_module(InitialStateFromFile,namespace="Parameters")
  reg.add_module(InitialProductState,namespace="Parameters")
  
  register_parameters(DMFTMonteCarloSolverParameters)
  register_parameters(DMFTModelParameters)
  register_parameters(DMFTSelfConsistencyParameters)
  
