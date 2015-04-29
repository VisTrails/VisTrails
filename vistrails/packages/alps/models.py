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
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry

import parameters

basic = vistrails.core.modules.basic_modules

##############################################################################


class Model(parameters.FixedAndDefaultParameters): 
   """ A dictionary of parameters defining a general model. Specify the model file in the MODEL_LIBRARY input and the model name in MODEL. MODEL_LIBRARY defaults to the default ALPS models.xml file. """
   _input_ports = [('MODEL',[basic.String]),
                   ('MODEL_LIBRARY',[basic.File])]

class ClassicalSpinModel(Model):
    """ the classical spin models for ALPS spinmc """
    _input_ports = [('MODEL',[basic.String],True),
                    ('MODEL_LIBRARY',[basic.File],True)]

class ClassicalIsingModel(ClassicalSpinModel):
    """ the classical Ising model for ALPS spinmc """
    fixed = {'MODEL':'Ising'}

class ClassicalXYModel(ClassicalSpinModel):
    """ the classical XY model for ALPS spinmc """
    fixed = {'MODEL':'XY'}

class ClassicalHeisenbergModel(ClassicalSpinModel):
    """ the classical Heisenberg model for ALPS spinmc """
    fixed = {'MODEL':'Heisenberg'}

                    
class SpinModel(Model):
   """ 
   A quantum spin model. The coupling parameters are as follows. The suffix # should be replaced by the site or bond type number, where no number defaults to 0, thus J is the same as J0. A prime (') is the same as 1. Thus J' is the same as J1.
   
   Jxy#: the coupling between XY spin ompenents, defaults to J#
   Jz#: the coupling between Z spin ompenents, defaults to J#
   h#: a longitudinal field coupling to the Z spin component
   Gamma#: a transverse field coupling to the X spin component
   D#: a single-ion anisotropy coupling to the square of the Z spin component
   """
   fixed = {'MODEL'   : 'spin'}
   defaults =      {'J0'    : '0',
                    'J'     : 'J0',
                    'Jxy'   : 'J',
                    'Jz'    : 'J',
                    'Jxy0'  : 'Jxy',
                    'Jz0'   : 'Jz',
                    'J1'    : '0',
                    "J'"    : 'J1',
                    "Jz'"   : "J'",
                    "Jxy'"  : "J'",
                    'Jz1'   : "Jz'",
                    'Jxy1'  : "Jxy'",
                    'h'     : '0',
                    'Gamma' : '0',
                    'D'     : '0',
                    'h#'    : 'h',
                    'Gamma#': 'Gamma',
                    'D#'    : 'D',
                    'J#'    : '0',
                    'Jz#'   : 'J#',
                    'Jxy#'  : 'J#'
                 }

class BosonHubbardModel(Model):
   """ 
   A Bose Hubbard model. The coupling parameters are as follows. The suffix # should be replaced by the site or bond type number, where no number defaults to 0, thus t is the same as t0. A prime (') is the same as 1. Thus t' is the same as t1.
   
   t#: the hopping
   U#: the on-site repulsion
   mu#: the chemical potential
   V#: a nearest neighbor repulsion
   """
   fixed = {'MODEL'   : 'boson Hubbard'}
   defaults =      {'mu'    : '0',
                    't'     : '1',
                    'V'     : '0',
                    "t'"    : '0',
                    "V''"   : '0',
                    'U'     : '0',
                    't0'    : 't',
                    't1'    : "t'",
                    'V0'    : '0',
                    'V1'    : "V'",
                    'mu#'   : 'mu',
                    'U#'    : 'U',
                    't#'    : '0',
                    'V#'    : '0'
                 }

class HardcoreBosonModel(Model):
   """ 
   A hardcore boson model. The coupling parameters are as follows. The suffix # should be replaced by the site or bond type number, where no number defaults to 0, thus t is the same as t0. A prime (') is the same as 1. Thus t' is the same as t1.
   
   t#: the hopping
   mu#: the chemical potential
   V#: a nearest neighbor repulsion
   """
   fixed = {'MODEL'   : 'hardcore boson'}
   defaults =      {'mu'    : '0',
                    't'     : '1',
                    'V'     : '0',
                    "t'"    : '0',
                    "V''"   : '0',
                    't0'    : 't',
                    't1'    : "t'",
                    'V0'    : 'V',
                    'V1'    : "V'",
                    'mu#'   : 'mu',
                    't#'    : '0',
                    'V#'    : '0'
                 }

def register_model(type):
   reg = vistrails.core.modules.module_registry.get_module_registry()
   reg.add_module(type,namespace="Models")
   reg.add_input_port(type,'MODEL_LIBRARY',[basic.File])

def register_parameters(type, ns="Models"):
   reg = vistrails.core.modules.module_registry.get_module_registry()
   reg.add_module(type,namespace=ns)
   reg.add_output_port(type, "value", type)
  
def initialize(): pass

def selfRegister():

   reg = vistrails.core.modules.module_registry.get_module_registry()
  
   register_parameters(Model)
   
   reg.add_module(ClassicalSpinModel,namespace="Models",abstract=True)
   reg.add_module(ClassicalIsingModel,namespace="Models")
   reg.add_module(ClassicalXYModel,namespace="Models")
   reg.add_module(ClassicalHeisenbergModel,namespace="Models")
   
   register_model(SpinModel)
   register_model(BosonHubbardModel)
   register_model(HardcoreBosonModel)
  
