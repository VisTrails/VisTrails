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
import copy

import parameters
import alpsparameters
import lattices 
import models

from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
import packages.spreadsheet

from alpsparameters import SystemParameters
from parameters import Parameters
basic = vistrails.core.modules.basic_modules

##############################################################################

class SimulationName(basic.String):
    """ the name given to a simulation, which can then be used in file names or spreadsheet names """

class LatticeModel(parameters.Parameters): 
    """ the simulation parameters, conistsing of model, lattice, and other parameters """
    def compute(self):
        res=self.updateFromPort('parms',parameters.ParametersData({}))
        res=self.updateFromPort('lattice',res)
        res=self.updateFromPort('model',res)
        self.setOutput(res)
    _input_ports = [('lattice', [lattices.Lattice]),
                     ('model', [models.Model])]
    _output_ports=[('value', [SystemParameters])]

class PrepareDiagonalization(parameters.Parameters):
    """ a module collecting the typical input parameters for exact diagonalization """
    def compute(self):
        res = parameters.ParametersData({})
        for port_name in self.inputPorts:
           res=self.updateFromPort(port_name,res)
        self.setOutput(res)
    _input_ports = [('system', [SystemParameters]),
                     ('conserved', [alpsparameters.ConservedQuantumNumbers]),
                     ('measurements',[alpsparameters.CustomMeasurements])]
    _output_ports=[('value', [SystemParameters])]


class PrepareMonteCarlo(parameters.Parameters):
    """ a module collecting the typical input parameters for a Monte Carlo simulation """
    def compute(self):
        res = parameters.ParametersData({})
        for port_name in self.inputPorts:
           res=self.updateFromPort(port_name,res)
        self.setOutput(res)
    _input_ports = [('system', [SystemParameters]),
                     ('mcparms', [alpsparameters.MonteCarloParameters]),
                     ('temperature',[alpsparameters.Temperature]),
                     ('measurements',[alpsparameters.MonteCarloMeasurements])]
    _output_ports=[('value', [SystemParameters])]

class PrepareDMRG(parameters.Parameters):
    """ a module collecting the typical input parameters for a DMRG simulation """
    def compute(self):
        res = parameters.ParametersData({})
        for port_name in self.inputPorts:
           res=self.updateFromPort(port_name,res)
        self.setOutput(res)
    _input_ports = [('system', [SystemParameters]),
                     ('dmrgparms', [alpsparameters.DMRGParameters]),
                     ('conserved', [alpsparameters.ConservedQuantumNumbers]),
                     ('measurements',[alpsparameters.CustomMeasurements])]
    _output_ports=[('value', [SystemParameters])]

class PrepareDMFT(parameters.Parameters):
    """ A module collecting the typical input parameters for a DMFT simulation """
    def compute(self):
        res = parameters.ParametersData({})
        for port_name in self.inputPorts:
           res=self.updateFromPort(port_name,res)
        self.setOutput(res)
    _input_ports = [
            ("MCSolverParameters",[alpsparameters.DMFTMonteCarloSolverParameters]),
            ("ModelParameters",[alpsparameters.DMFTModelParameters]),
            ("SelfConsistencyParameters",[alpsparameters.DMFTSelfConsistencyParameters])]
    _output_ports=[('value', [Parameters])]

class PrepareTEBD(parameters.Parameters):
    """ a module collecting the typical input parameters for a TEBD simulation """
    def compute(self):
        res = parameters.ParametersData({})
        for port_name in self.inputPorts:
           res=self.updateFromPort(port_name,res)
        self.setOutput(res)
    _input_ports = [('system', [SystemParameters]),
                     ('tebdparms', [alpsparameters.TEBDParameters]),
                     ('conserved', [alpsparameters.ConservedQuantumNumbers])]
    _output_ports=[('value', [SystemParameters])]

class PrepareMPS(parameters.Parameters):
    """ a module collecting the typical input parameters for a MPS simulation """
    def compute(self):
        res = parameters.ParametersData({})
        for port_name in self.inputPorts:
           res=self.updateFromPort(port_name,res)
        self.setOutput(res)
    _input_ports = [('system', [alpsparameters.SystemParameters]),
                     ('mpsparms', [alpsparameters.MPSParameters]),
                     ('conserved', [alpsparameters.ConservedQuantumNumbers]),
                     ('measurements',[alpsparameters.CustomMeasurements]),
                     ('initialstate',[alpsparameters.MPSInitialState])]
    _output_ports=[('value', [Parameters])]

def initialize(): pass



