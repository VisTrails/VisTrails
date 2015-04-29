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
import core.bundles
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry
import copy
# import packages.controlflow
basic = vistrails.core.modules.basic_modules

import numpy as np

try:
  from gui.modules.constant_configuration import StandardConstantWidget
except:
  from vistrails.core.modules.constant_configuration import StandardConstantWidget

##############################################################################

class CommonParametersFunctions:
    def set_checked(self,p,key,value):
        if isinstance(value,basic.File):
          value = value.name
        if key in p and p[key] != value:
          raise ModuleError(self, "parameter " + key + " defined twice and the values differ")
        else:
          p[key] = value

    def update_checked(self,lhs,rhs):
        for k in rhs.keys():
          self.set_checked(lhs,k,rhs[k])
            

class ParametersData(CommonParametersFunctions):
    """ A dictionary of parameters """
    def __init__(self, d):
        self.parms = copy.deepcopy(d)
        
    def merge_one(self,p):
        self.update_checked(self.parms,p.parms)
      
    def copy(self):
        p = ParametersData(self.parms)
        return p
        
    def set(self,key_name,value):
        self.set_checked(self.parms,key_name,value)

    def updateIfMissing(self,defaults):
        for k in defaults.keys():
          if not k in self.parms:
            self.parms[k] = defaults[k]

    def write(self,out):
        out.write('{\n')
        for key in self.parms:
          out.write(key)
          out.write('=\"')
          out.write(str(self.parms[key]))
          out.write('\"\n')
        out.write('}\n')
        
    def update_unchecked(self,other):
        self.parms.update(other)

    def toBasic(self):
        return self.parms
        
    parms = {}

class ParameterListData(CommonParametersFunctions):
    """ a list of Parameters """
    def __init__(self, l):
        self.list = copy.deepcopy(l)

    def copy(self):
        p = ParameterListData(self.list)
        return p
        
    def merge_one(self,p):
        if isinstance(p,ParametersData):
          for q in self.list:
            self.update_checked(q,p.parms)
        else:
          newlist = []
          for p1 in self.list:
            for p2 in p.list:
              newlist.append(p1.copy())
              self.update_checked(newlist[-1],p2)
          self.list = newlist
        
    def set(self,key_name,value):
        for p in self.list:
          self.set_checked(p,key_name,value)
          
    def updateIfMissing(self,defaults):
        for k in defaults.keys():
          for p in self.list:
            if not k in p:
              p[k] = defaults[k]

    def write(self,out):
        for p in self.list:
          pd = ParametersData(p)
          pd.write(out)
       
    def toBasic(self):
        return self.list

    def update_unchecked(self,other):
        for p in self.list:
          p.update(other)
       
    list = []

def make_parameter_data(p):
    if isinstance(p,list):
      return ParameterListData(p)
    if isinstance(p,dict):
      return ParametersData(p)
    else:
      raise "unknown type passed to make_parameter_data"


class ParameterValueList(list):
    """ a class holding values for a parameter """


class Parameters(Module):
    """ Simulation parameters """
    def merge(self,p1,p2):
        if isinstance(p1,ParametersData):
          res = p2
          res.merge_one(p1)
        else:
          res = p1
          res.merge_one(p2)
        return res
          
    def updateFromPort(self,port_name,res):
        if self.hasInputFromPort(port_name):
          input_values = self.forceGetInputListFromPort(port_name)
          for p in input_values:
            res = self.merge(res,make_parameter_data(p))
        return res
        
    def setFromPort(self,port_name,res):
        if self.hasInputFromPort(port_name):
          val = self.getInputFromPort(port_name)
          if (isinstance(val,ParameterValueList)):
            l = []
            for v in val:
              l.append({port_name:v})
            res = self.merge(res,ParameterListData(l))
          else:
            res.set(port_name,val)
          return res
    
    def readInputs(self,res):
        for port_name in self.inputPorts:
          if port_name == 'parms':
            res = self.updateFromPort('parms',res)
          else: 
            res = self.setFromPort(port_name,res)
        return res

#   def update_parms(self,other):
#       update_checked(self.parms,other.parms)
       
    def setOutput(self,res):
        self.setResult('value',res.toBasic())
                      
    def compute(self):
        self.setOutput(self.readInputs(ParametersData({})))

class ConcatenateParameters(Module):
    """ merge several lists of parameters into one, by appending one to the other """
    def compute(self):
        l = []
        if self.hasInputFromPort('parms'):
          input_values = self.forceGetInputListFromPort('parms')
          for p in input_values:
            if isinstance(p,list):
              l.extend(p)
            else:
              l.append(p)
        if len(l)==1:
          self.setResult('value',l[0])
        else:
          self.setResult('value',l)
        
    _input_ports = [('parms',[Parameters])]
    _output_ports = [('value',[Parameters])]



class MergeParameters(Module,CommonParametersFunctions):
    """ join parameters from several lists, merging the parameters element-wise """
    def compute(self):
        if self.hasInputFromPort('parms'):
          input_values = self.forceGetInputListFromPort('parms')
          l = input_values[0]
          for p in input_values[1:]:
            if len(p) != len(l):
              raise ModuleError(self, "Cannot join lists of different length")
            for i in range(len(l)):
              self.update_checked(l[i],p[i])
        if len(l)==1:
          self.setResult('value',l[0])
        else:
          self.setResult('value',l)
        
    _input_ports = [('parms',[Parameters])]
    _output_ports = [('value',[Parameters])]



class FixedAndDefaultParameters(Parameters):
    def setOutput(self,res):
        res.updateIfMissing(self.defaults)
        self.setResult('value',res.toBasic())
    def compute(self):
        res = self.readInputs(ParametersData(self.fixed))
        self.setOutput(res)
    fixed    = {}
    defaults = {}



class IterateValue(Module):
    """ This module iterates a parameter value over a list of values. It can be connected to any input port for a paramater. """
    def compute(self):
        self.setResult('value',ParameterValueList(self.getInputFromPort('value_list')))
    _input_ports = [('value_list',[basic.List])]
    _output_ports = [('value', [basic.String])]


class Parameter(Module):
    """ A module to define a single parameter, given by a name and value """
    def compute(self):
        name = self.getInputFromPort('name')
        value = self.getInputFromPort('value')
        if (isinstance(value,ParameterValueList)):
          list = []
          for v in value:
            list.append({name:v})
          self.setResult('value',list)
        else:
          d = {name: value}
          self.setResult('value',d)
    _input_ports = [('name',[basic.String]),
                    ('value',[basic.String])]
    _output_ports=[('value', [Parameters])]


class IterateParameter(Module):
    """ This module iterates a parameter over a list of values. Both name and the list of values need to be given. """
    def compute(self):
        if self.hasInputFromPort('name') and self.hasInputFromPort('value_list'):
          name = self.getInputFromPort('name')
          value_list = self.getInputFromPort('value_list')
          list = []
          for val in value_list:
            list.append({ name : val })
          self.list = list 
        self.setResult('value',list)
    _input_ports = [('name',[basic.String]),
                    ('value_list',[basic.List])]
    _output_ports = [('value', [Parameters])]

class IterateParameterInRange(Module):
    """ This module iterates a parameter in a range with a given number of steps. """
    def compute(self):
        name = self.getInputFromPort('name')
        min_val = self.getInputFromPort('min')
        max_val = self.getInputFromPort('max')
        steps = self.getInputFromPort('num_steps')
        
        ll = []
        for val in np.linspace(min_val, max_val, steps):
            ll.append({ name: val })
        self.setResult('value',ll)
        
    _input_ports = [('name',[basic.String]),
                    ('min',[basic.Float]),
                    ('max',[basic.Float]),
                    ('num_steps',[basic.Integer])]
    _output_ports = [('value', [Parameters])]

class UpdateParameters(Parameters):
   """ 
   This module updates all parameters in the list parms by values from the parameters of the 'updated' list. if a parameter in updated does not exist in parms yet, it is created. If a parameter exists, it is replaced by the value in updated. 
   """
   def compute(self):
       res=self.updateFromPort('parms',ParametersData({}))
       if self.hasInputFromPort('updated'):
         input_values = self.forceGetInputListFromPort('updated')
         for p in input_values:
           res.update_unchecked(p)
       self.setOutput(res)
   _input_ports = [('parms',[Parameters]),
                   ('updated',[Parameters])]

class QuenchParameter(Module):
    """ A module to define a time evolution of a parameter, according to the quench:
        g(t) = g(t_i) + ((t-t_i) / t_f)^p * (g(t_f) - g(t_i))
        with t = t_i + n*dt, and t_f = t_i + num_steps*dt.
        The exponent p defaults to 1.
    """
    def quench(self, g_i, g_f, num_steps, p):
        num_value = g_i + ((np.arange(num_steps, dtype=float)+1)/num_steps)**p * (g_f - g_i)
        value = ','.join( [str(n) for n in num_value] )
        return value
    
    def loadParmList(self, port_name):
        value = self.getInputFromPort(port_name)
        if not isinstance(value,ParameterValueList):
            value = [value]
        return value
        
    def compute(self):
        name = self.getInputFromPort('name')
        initials  = self.loadParmList('initial')
        finals    = self.loadParmList('final')
        num_steps = self.loadParmList('num_steps')
        exponents = ['1']
        if self.hasInputFromPort('exponent'):
            exponents = self.loadParmList('exponent')
        
        params_list = []
        for g_i in initials:
            for g_f in finals:
                for ns in num_steps:
                    for p in exponents:
                        params_list.append( {name+'[Time]': self.quench(float(g_i), float(g_f), int(ns), float(p))} )
        
        if len(params_list) == 1:
            self.setResult('value', params_list[0])
        else:
            self.setResult('value', params_list)
    _input_ports = [('name',[basic.String]),
                    ('initial',[basic.String]),
                    ('final',[basic.String]),
                    ('num_steps',[basic.String]),
                    ('exponent',[basic.String])]
    _output_ports=[('value', [Parameters])]

class ConcatenateParameterQuenches(Module):
    """
      This module concatenates different segments of a parameter quench into a longer one.
    """
    def compute(self):
        quench_names = [ 'quench'+str(i) for i in [1,2,3,4] ]
        quenches = []
        for port_name in quench_names:
            if self.hasInputFromPort(port_name):
                tmp = self.getInputFromPort(port_name)
                if not isinstance(tmp, list):
                    tmp = [tmp]
                quenches.append(tmp)
        
        ## TODO: nice error in case len(quenches) == 0
        
        res = copy.deepcopy(quenches[0])
        for q in quenches[1:]:
            newlist = []
            for v1 in res:
                for v2 in q:
                    
                    d = copy.deepcopy(v1)
                    for k,v in d.items():
                        if '[Time]' in k:
                            d[k] = v+','+v2[k]
                    newlist.append(d)
            res = newlist
        self.setResult('value', res)
    _input_ports = [('quench1', [Parameters]),
                    ('quench2', [Parameters]),
                    ('quench3', [Parameters]),
                    ('quench4', [Parameters]),
                    ]
    _output_ports=[('value', [Parameters])]




def register_parameters(type, ns="Parameters"):
  reg = vistrails.core.modules.module_registry.get_module_registry()
  reg.add_module(type,namespace=ns)
  reg.add_output_port(type, "value", type)
  
def initialize(): pass

def selfRegister():

  reg = vistrails.core.modules.module_registry.get_module_registry()

  register_parameters(Parameters)
  reg.add_input_port(Parameters, "parms", Parameters)

  reg.add_module(Parameter,namespace="Parameters")
  reg.add_module(FixedAndDefaultParameters,namespace="Parameters",abstract=True)
  reg.add_module(MergeParameters,namespace="Parameters")
  reg.add_module(ConcatenateParameters,namespace="Parameters")
  reg.add_module(IterateParameter,namespace="Parameters")
  reg.add_module(IterateValue,namespace="Parameters")
  reg.add_module(UpdateParameters,namespace="Parameters")
  reg.add_module(IterateParameterInRange,namespace="Parameters")
  
  reg.add_module(QuenchParameter,namespace="Parameters")
  reg.add_module(ConcatenateParameterQuenches,namespace="Parameters")

