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

from core.configuration import ConfigurationObject
from core.upgradeworkflow import UpgradeWorkflowHandler
from vistrails.core.modules.module_registry import get_module_registry

import alpscore
import parameters
import alpsparameters
import lattices
import models
import system
import applications
import plots
import tools
import platform

import dataset


##############################################################################

_subworkflows = [('MplXYPlotCell.xml', {'namespace': 'Tools'}),
                 ('ShowListOfPlots.xml', {'namespace': 'DataSet|Plot'}),
                 ('ShowMplPlot.xml', {'namespace': 'DataSet|Plot'}),
                 ('ShowListOfXMLFiles.xml', {'namespace': 'Tools'}),
                 ('ShowListOfHTMLFiles.xml', {'namespace': 'Tools'})
                 ]

def handle_module_upgrade_request(controller, module_id, pipeline):
   reg = get_module_registry()

   # format is {<old module name>: (<new_module_klass>, <remap_dictionary>}}
   # where remap_dictionary is {<remap_type>: <name_changes>}
   # and <name_changes> is a map from <old_name> to <new_name>
   module_remap = {'AlpsApplication': (applications.RunAlpsApplication,{}),
                   'AlpsEvaluate': (applications.AlpsEvaluate,{}),
                   'AppSpinMC': (applications.RunSpinMC,{}),
                   'AppLoop': (applications.RunLoop,{}),
                   'AppDirLoopSSE': (applications.RunDirLoopSSE,{}),
                   'AppWorm': (applications.RunWorm,{}),
                   'AppDWA' : (applications.RunDWA,{}),
                   'AppFullDiag': (applications.RunFullDiag,{}),
                   'AppSparseDiag': (applications.RunSparseDiag,{}),
                   'AppDMRG': (applications.RunDMRG,{}),
                   'AppTEBD': (applications.RunTEBD,{}),
                   'AppQWL': (applications.RunQWL,{}),
                   'EvaluateFullDiagT': (applications.EvaluateFullDiagVersusT,{}),
                   'EvaluateFullDiagH': (applications.EvaluateFullDiagVersusH,{}),
                   
                   'MonteCarloSimulation': (system.PrepareMonteCarlo,{}),
                   'DiagonalizationSimulation': (system.PrepareDiagonalization,{}),
                   'DMRGSimulation': (system.PrepareDMRG,{}),
                   'TEBDSimulation': (system.PrepareTEBD,{}),
                   'SimulationID': (system.SimulationName,{'dst_port_remap': {'value': 'value'}, 'src_port_remap': {'value': 'value'}}),
                   'Applications|SimulationName': (system.SimulationName,{'dst_port_remap': {'value': 'value'},'src_port_remap': {'value': 'value'}}),
                   'SimulationName': (system.SimulationName,{'dst_port_remap': {'value': 'value'}, 'dst_port_remap': {'value': 'value'}}),
                   'LatticeModel': (system.LatticeModel,{}),

                   'LatticeParameters': (lattices.Lattice,{}),
                   'square_lattice': (lattices.SquareLattice,{}),
                   'simple_cubic_lattice': (lattices.SimpleCubicLattice,{}),
                   'ladder': (lattices.LadderLattice,{}),
                   'open_ladder': (lattices.OpenLadderLattice,{}),
                   'chain_lattice': (lattices.ChainLattice,{}),
                   'open_chain_lattice': (lattices.OpenChainLattice,{}),
                   'ModelParameters': (models.Model,{}),
                   'ClassicalSpinModel': (models.ClassicalSpinModel,{}),
                   'SpinModel': (models.SpinModel,{}),
                   'BosonHubbardModel': (models.BosonHubbardModel,{}),
                   'HardcoreBosonModel': (models.HardcoreBosonModel,{}),
                   
                   'CombineParameters': (parameters.ConcatenateParameters,{}),
                   'Parameter': (parameters.Parameter,{}),
                   'ConservedQuantumnumbers': (alpsparameters.ConservedQuantumNumbers,{}),
                   'SystemParameters': (alpsparameters.SystemParameters,{}),

                   'MakeParameterFile': (tools.WriteParameterFile,{'dst_port_remap': {'simulationid': 'simulationid'}}),
                   'MakeParameterXMLFiles': (tools.WriteInputFiles,{'dst_port_remap': {'simulationid': 'simulationid'}}),
                   'WriteInputFiles': (tools.WriteInputFiles,{'dst_port_remap': {'simulationid': 'simulationid'}}),
                   'GetRunFiles': (tools.GetCloneFiles,{}),
                   'GetResultFiles': (tools.GetResultFiles,{}),
                   'GetCloneFiles': (tools.GetCloneFiles,{}),
                   'XML2HTML': (tools.ConvertXML2HTML,{}),
                   'ConvertXML2HTML': (tools.ConvertXML2HTML,{}),
                   'GetSimulationInDir': (tools.GetJobFile,{}),
                   'OpenHTML': (alpscore.DisplayInBrowser,{}),
                   'TextFile': (alpscore.WriteTextFile,{}),

                   'GenerateDataSet': (dataset.PrepareDataSets,{}),
                   'LoadDataSet': (dataset.LoadDataSetsFromTextFile,{}),
                   'CustomLoader': (dataset.LoadCustomFile,{}),
                   'CollectXY': (dataset.CollectDataSets,{'dst_port_remap': {'for-each': 'for-each'}}),
                   'Parameters|CollectDataSets': (dataset.CollectDataSets,{'dst_port_remap': {'for-each': 'for-each'}}),
                   'LoadProperties': (dataset.LoadAlpsProperties,{}),
                   'LoadAlpsHdf5': (dataset.LoadAlpsMeasurements,{}),
                   'LoadAlpsMeasurements': (dataset.LoadAlpsMeasurements,{}),
                   'LoadSpectrumHdf5': (dataset.LoadAlpsSpectra,{}),
                   'LoadBinningAnalysis': (dataset.LoadBinningAnalysis,{}),
                   'LoadAlpsDiagData': (dataset. LoadAlpsEigenstateMeasurements,{}),
                   'LoadAlpsEigenstateMeasurements': (dataset. LoadAlpsEigenstateMeasurements,{}),
                   'Transform': (dataset.TransformEachDataSet,{}),
                   'PlotDescriptor': (dataset.PreparePlot,{}),
                   'PreparePlot': (dataset.PreparePlot,{}),
                   'AxisDescriptor': (dataset.Axis,{}),
                   'Axis': (dataset.Axis,{}),
                   'LegendDescriptor': (dataset.Legend,{}),
                   'Legend': (dataset.Legend,{}),
                   'Convert2Text': (dataset.WriteTextFile,{}),
                   'Convert2Grace': (dataset.WriteGraceFile,{}),
                   'DisplayXMGRPlot': (plots.DisplayGracePlot,{}),
                   'GraceXYPlot': (dataset.WriteGraceFile,{}),
                   'MplXYPlot': (dataset.MplXYPlot,{'dst_port_remap': {'plot': 'plot'}, 'src_port_remap' :  {'unused': 'self'}}),
                   'DataSet|Plot|MplXYPlot': (dataset.MplXYPlot,{'dst_port_remap': {'plot': 'plot'}, 'src_port_remap' :  {'unused': 'self'}}),
                   'Select': (dataset.Select,{}),
                   'And': (dataset.And,{}),
                   'Or': (dataset.Or,{}),
                   
                   'PolyFit': (dataset.DoPolynomialFit,{}),
                   'NonlinearFit': (dataset.DoNonlinearFit,{}),
                   'DoNonlinearFit': (dataset.DoNonlinearFit,{}),
                   
                   'SortByX': (dataset.SortEachDataSet,{}),
                   'SelectXRange': (dataset.RestrictXRange,{}),
                   'SetLabels': (dataset.SetLabels,{}),
                   'MakeScatter': (dataset.SetPlotStyle,{}),
                   'Selector': (dataset.Predicate,{}),
                   'PropertySelector': (dataset.PropertyPredicate,{}),
                   'PropertyRangeSelector': (dataset.PropertyRangePredicate,{}),
                   'ObservableSelector': (dataset.ObservablePredicate,{}),
                   'GroupBy': (dataset.GroupDataSets,{'dst_port_remap': {'for-each': 'for-each'}}),
                   'GroupDataSets': (dataset.GroupDataSets,{'dst_port_remap': {'for-each': 'for-each'}}),
                   'GroupedTransform': (dataset.TransformGroupedDataSets,{}),
                   'GenerateDataSet': (dataset.PrepareDataSets,{}),
                   'GenerateDataSet': (dataset.PrepareDataSets,{}),
                   
                   'CycleColors': (dataset.CycleColors,{}),
                   'CycleMarkers': (dataset.CycleMarkers,{}),
                   'Convert2XML': (tools.Convert2XML,{}),
                   'IterateValue': (parameters.IterateValue,{'dst_port_remap': {'value_list': 'value_list'}}),
                   'IterateParameter': (parameters.IterateParameter,{'dst_port_remap': {'value_list': 'value_list'}})
                   }


# remaps for move of List in VT
   new_remap = {'DataSet|Fit|DoNonlinearFit': [(None, '2.2.0', None, {'dst_port_remap': {'parameters': 'parameters'}})], 'Tools|GetResultFiles': [(None, '2.2.0', None, {'src_port_remap': {'value': 'value'}})], 'Plots|ExtractText': [(None, '2.2.0', None, {'dst_port_remap': {'data': 'data'}})], 'DataSet|Hierarchy|GroupDataSets': [(None, '2.2.0', None, {'dst_port_remap': {'for-each': 'for-each'}})], 'DataSet|Plot|SetLabels': [(None, '2.2.0', None, {'dst_port_remap': {'label_props': 'label_props'}})], 'DataSet|Load|LoadTimeEvolution': [(None, '2.2.0', None, {'dst_port_remap': {'Measurements': 'Measurements'}})], 'DataSet|Load|LoadDataSetsFromTextFile': [(None, '2.2.0', None, {'dst_port_remap': {'y-columns': 'y-columns'}})], 'Tools|ShowListOfXMLFiles': [(None, '2.2.0', None, {'dst_port_remap': {'InputList': 'InputList'}})], 'Plots|ExtractAnything': [(None, '2.2.0', None, {'dst_port_remap': {'data': 'data'}})], 'Tools|GetCloneFiles': [(None, '2.2.0', None, {'src_port_remap': {'value': 'value'}})], 'Plots|ExtractMpl': [(None, '2.2.0', None, {'dst_port_remap': {'data': 'data'}})], 'Tools|Convert2XML': [(None, '2.2.0', None, {'src_port_remap': {'value': 'value'}, 'dst_port_remap': {'input_file': 'input_file'}})], 'Tools|ConcatenatePathList': [(None, '2.2.0', None, {'src_port_remap': {'files': 'files', 'paths': 'paths', 'directories': 'directories'}, 'dst_port_remap': {'leafs': 'leafs'}})], 'Parameters|IterateValue': [(None, '2.2.0', None, {'dst_port_remap': {'value_list': 'value_list'}})], 'DataSet|Load|LoadAlpsEigenstateMeasurements': [(None, '2.2.0', None, {'dst_port_remap': {'Measurements': 'Measurements'}})], 'DataSet|DataSets': [(None, '2.2.0', None, {'src_port_remap': {'value': 'value'}, 'dst_port_remap': {'tail': 'tail', 'value': 'value'}})], 'Tools|DisplayInBrowser': [(None, '2.2.0', None, {'dst_port_remap': {'files': 'files'}})], 'DataSet|Plot|CycleMarkers': [(None, '2.2.0', None, {'dst_port_remap': {'for-each': 'for-each', 'markers': 'markers'}})], 'DataSet|Load|LoadAlpsMeasurements': [(None, '2.2.0', None, {'dst_port_remap': {'Measurements': 'Measurements'}})], 'Plots|ExtractXMGR': [(None, '2.2.0', None, {'dst_port_remap': {'data': 'data'}})], 'DataSet|Plot|CycleColors': [(None, '2.2.0', None, {'dst_port_remap': {'for-each': 'for-each', 'colors': 'colors'}})], 'Tools|Glob': [(None, '2.2.0', None, {'src_port_remap': {'value': 'value'}})], 'Tools|ConvertXML2HTML': [(None, '2.2.0', None, {'src_port_remap': {'output_files': 'output_files'}, 'dst_port_remap': {'input_files': 'input_files'}})], 'Parameters|IterateParameter': [(None, '2.2.0', None, {'dst_port_remap': {'value_list': 'value_list'}})], 'DataSet|Load|CollectDataSets': [(None, '2.2.0', None, {'dst_port_remap': {'for-each': 'for-each'}})], 'DataSet|ResultFiles': [(None, '2.2.0', None, {'src_port_remap': {'value': 'value', 'filenames': 'filenames'}, 'dst_port_remap': {'tail': 'tail', 'value': 'value', 'filenames': 'filenames'}})], 'Dataset|Plot|ShowListOfPlots': [(None, '2.2.0', None, {'dst_port_remap': {'InputList': 'InputList'}})], 'DataSet|Load|LoadBinningAnalysis': [(None, '2.2.0', None, {'dst_port_remap': {'Measurements': 'Measurements'}})], 'Tools|PickFileFromList': [(None, '2.2.0', None, {'dst_port_remap': {'files': 'files'}})], 'Tools|ShowListOfHTMLFiles': [(None, '2.2.0', None, {'dst_port_remap': {'InputList': 'InputList'}})]}

   for name, (new_module, d) in module_remap.iteritems():
      new_remap[name] = [(None, '2.2.0', new_module, d)]

   # [(<start_version>, <end_version>, <new_module (None=same module, new version)>, <remap_dict>)]
   new_remap['ShowListOfHTMLFiles'] = [(None, '2.2.0', None, {})]
   new_remap['Tools|ShowListOfXMLFiles'] = [(None, '2.2.0', None, {})]
   new_remap['ShowListOfPlots'] = [(None, '2.2.0', None, {})]
   new_remap['DataSet|Plot|ShowListOfPlots'] = [(None, '2.2.0', None, {})]
   new_remap['Dataset|Plot|ShowListOfPlots'] = [(None, '2.2.0', 'DataSet|Plot|ShowListOfPlots', {})]
   new_remap['DataSet|Plot|ShowMplPlot'] = [(None, '2.2.0', None, {})]
   new_remap['Dataset|Plot|ShowMplPlot'] = [(None, '2.2.0', 'DataSet|Plot|ShowMplPlot', {})]
   new_remap['MplXYPlotCell'] = [(None, '2.2.0', None, {})]
   new_remap['Tools|MplXYPlotCell'] = [(None, '2.2.0', None, {})]
   new_remap['DataSet|Plot|MplXYPlot'] = [(None, '2.2.0', None, {})]
   new_remap['Tools|WriteInputFiles'] = [(None, '2.2.0', None, {'dst_port_remap': {'simulationid': 'simulationid'}})]
   new_remap['SimulationName'] = [(None, '2.2.0', None, {'dst_port_remap': {'value': 'value'},'src_port_remap': {'value': 'value'}})]
   new_remap['Applications|SimulationName'] = [(None, '2.2.0', None, {'dst_port_remap': {'value': 'value'},'src_port_remap': {'value': 'value'}})]
   new_remap['MplXYPlot'] = [(None,'2.2.0',dataset.MplXYPlot,{'dst_port_remap': {'plot': 'plot'}, 'src_port_remap' :  {'unused': 'self'}})]
   new_remap['DataSet|Plot|MplXYPlot'] = [(None,'2.2.0',dataset.MplXYPlot,{'dst_port_remap': {'plot': 'plot'}, 'src_port_remap' :  {'unused': 'self'}})]




   return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                             new_remap)


def initialize():
  dataset.selfRegister()
  alpscore.selfRegister()  
  parameters.selfRegister()
  alpsparameters.selfRegister()
  lattices.selfRegister()
  models.selfRegister()
  applications.selfRegister()
  plots.selfRegister()
  tools.selfRegister()
  
  alpscore.config = configuration
  
  dataset.initialize()


