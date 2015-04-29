
# VisTrails package for ALPS, Algorithms and Libraries for Physics Simulations
#
# Copyright (C) 2009 - 2010 by Bela Bauer <bauerb@itp.phys.ethz.ch>G
#
# Distributed under the Boost Software License, Version 1.0. (See accompany-
# ing file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
#
##############################################################################

import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry

import parameters

basic = vistrails.core.modules.basic_modules

##############################################################################

class Lattice(parameters.FixedAndDefaultParameters):
   """ a general lattice. Specify the lattice file in the LATTICE_LIBRARY input and the lattice name in LATTICE. LATTICE_LIBRARY defaults to the default ALPS lattices.xml file. """
   _input_ports = [('LATTICE',[basic.String]),
                   ('LATTICE_LIBRARY',[basic.File])]

class SimpleCubicLattice(Lattice):
  """ automatically generated lattice: simple cubic lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')]),
    ('H',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'simple cubic lattice'}
  defaults = {'H': 'W', 'W': 'L'}

class InhomogeneousSimpleCubicLattice(Lattice):
  """ automatically generated lattice: inhomogeneous simple cubic lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')]),
    ('H',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'inhomogeneous simple cubic lattice'}
  defaults = {'H': 'W', 'W': 'L'}

class AnisotropicSimpleCubicLattice(Lattice):
  """ automatically generated lattice: anisotropic simple cubic lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')]),
    ('H',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'anisotropic simple cubic lattice'}
  defaults = {'H': 'W', 'W': 'L'}

class InhomogeneousAnisotropicSimpleCubicLattice(Lattice):
  """ automatically generated lattice: inhomogeneous anisotropic simple cubic lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')]),
    ('H',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'inhomogeneous anisotropic simple cubic lattice'}
  defaults = {'H': 'W', 'W': 'L'}

class SquareLattice(Lattice):
  """ automatically generated lattice: square lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'square lattice'}
  defaults = {'W': 'L'}

class OpenSquareLattice(Lattice):
  """ automatically generated lattice: open square lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'open square lattice'}
  defaults = {'W': 'L'}

class CoupledLaddersLattice(Lattice):
  """ automatically generated lattice: coupled ladders """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'coupled ladders'}
  defaults = {'W': 'L'}

class TriangularLattice(Lattice):
  """ automatically generated lattice: triangular lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'triangular lattice'}
  defaults = {'W': 'L'}

class FrustratedSquareLattice(Lattice):
  """ automatically generated lattice: frustrated square lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'frustrated square lattice'}
  defaults = {'W': 'L'}

class ChainLattice(Lattice):
  """ automatically generated lattice: chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'chain lattice'}

class OpenChainLattice(Lattice):
  """ automatically generated lattice: open chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'open chain lattice'}

class InhomogeneousChainLattice(Lattice):
  """ automatically generated lattice: inhomogeneous chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'inhomogeneous chain lattice'}


class NNNChainLattice(Lattice):
  """ automatically generated lattice: nnn chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'nnn chain lattice'}

class NNNOpenChainLattice(Lattice):
  """ automatically generated lattice: nnn open chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'nnn open chain lattice'}

class _2BandChainLattice(Lattice):
  """ automatically generated lattice: 2 band chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': '2 band chain lattice'}

class _2BandOpenChainLattice(Lattice):
  """ automatically generated lattice: 2 band open chain lattice """
  _input_ports = [
    ('L',[(basic.String, '')])
  ]
  fixed = {'LATTICE': '2 band open chain lattice'}

class AnisotropicSquareLattice(Lattice):
  """ automatically generated lattice: anisotropic square lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'anisotropic square lattice'}
  defaults = {'W': 'L'}

class InhomogeneousSquareLattice(Lattice):
  """ automatically generated lattice: inhomogeneous square lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'inhomogeneous square lattice'}
  defaults = {'W': 'L'}

class InhomogeneousAnisotropicSquareLattice(Lattice):
  """ automatically generated lattice: inhomogeneous anisotropic square lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'inhomogeneous anisotropic square lattice'}
  defaults = {'W': 'L'}

class LadderLattice(Lattice):
  """ automatically generated lattice: ladder """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'ladder'}
  defaults = {'W': '2'}

class OpenLadderLattice(Lattice):
  """ automatically generated lattice: open ladder """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'open ladder'}
  defaults = {'W': '2'}

class KagomeLattice(Lattice):
  """ automatically generated lattice: Kagome lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'Kagome lattice'}
  defaults = {'W': 'L'}

class HoneycombLattice(Lattice):
  """ automatically generated lattice: honeycomb lattice """
  _input_ports = [
    ('L',[(basic.String, '')]),
    ('W',[(basic.String, '')])
  ]
  fixed = {'LATTICE': 'honeycomb lattice'}
  defaults = {'W': 'L'}


def register_lattice(type):
  reg = vistrails.core.modules.module_registry.get_module_registry()
  reg.add_module(type,namespace="Lattices")
  reg.add_input_port(type,'LATTICE',[basic.String],True)

def initialize(): pass

def selfRegister():    

  reg = vistrails.core.modules.module_registry.get_module_registry()
  
  reg.add_module(Lattice,namespace="Lattices")
  reg.add_output_port(Lattice, "value", Lattice)
  
  register_lattice(SimpleCubicLattice)
  register_lattice(InhomogeneousSimpleCubicLattice)
  register_lattice(AnisotropicSimpleCubicLattice)
  register_lattice(InhomogeneousAnisotropicSimpleCubicLattice)
  
  register_lattice(SquareLattice)
  register_lattice(AnisotropicSquareLattice)
  register_lattice(InhomogeneousSquareLattice)
  register_lattice(InhomogeneousAnisotropicSquareLattice)
  register_lattice(OpenSquareLattice)
  register_lattice(CoupledLaddersLattice)
  register_lattice(TriangularLattice)
  register_lattice(FrustratedSquareLattice)
  
  register_lattice(ChainLattice)
  register_lattice(InhomogeneousChainLattice)
  register_lattice(OpenChainLattice)
  register_lattice(NNNChainLattice)
  register_lattice(NNNOpenChainLattice)
  register_lattice(_2BandChainLattice)
  register_lattice(_2BandOpenChainLattice)
  register_lattice(LadderLattice)
  register_lattice(OpenLadderLattice)
  register_lattice(KagomeLattice)
  register_lattice(HoneycombLattice)
