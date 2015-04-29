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
import vistrails.core.bundles
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry
import tempfile

import alpscore
from vistrails.packages.matplotlib.bases import MplSource

basic = vistrails.core.modules.basic_modules

##############################################################################

class DisplayGracePlot(NotCacheable, alpscore.SystemCommand):
     """ opens a grace plotfile using  the xmgr command. The path to xmgrace and other tools can be set in the ALPS package preferences """
     def compute(self):
         cmd = ['nohup',alpscore._get_tool_path('xmgrace'), self.getInputFromPort('file').name,'&']
         if alpscore.config.check("xdisplay"):
           if alpscore.config.xdisplay != "":
             cmd = ['export','DISPLAY='+alpscore.config.xdisplay,';']+cmd
         self.execute(cmd)
     _input_ports = [('file', [basic.File])]

class DisplayGnuplot(NotCacheable, alpscore.SystemCommand):
    """ opens a gnuplot plotfile using  the gnuplot command. The path to gnuplot and other tools can be set in the ALPS package preferences """
    def compute(self):
        lines = [x.strip() for x in open(self.getInputFromPort('file').name).readlines()]
        lines = []
        if alpscore.config.check("gnuplot_term"):
          lines2 = ['set terminal '+alpscore.config.gnuplot_term]
        for line in lines:
            if not line.startswith('set terminal'):
                lines2.append(line)
        outf = open(self.getInputFromPort('file').name, 'w')
        for line in lines2:
            outf.write(line + '\n')
        outf.close()
        cmd=['nohup',alpscore._get_tool_path('gnuplot'), '-persist' , self.getInputFromPort('file').name,'&']
        if alpscore.config.check("xdisplay"):
           cmd = ['export','DISPLAY='+alpscore.config.xdisplay,';']+cmd
        self.execute(cmd)
    _input_ports = [('file', [basic.File])]
    
class PlotDescription(basic.File):
    """ a plot desription file """

class PlotScalarVersusParameter(PlotDescription):
    def compute(self):
        self.name = self.interpreter.filePool.create_file(suffix='.xsl').name
        f = file(self.name,'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        if (self.hasInputFromPort('title')):
          f.write('<plot name="'+str(self.getInputFromPort('title')) + '">\n')
        else:
          f.write('<plot>\n')
        if (self.hasInputFromPort('x-label')):
          xlabel = self.getInputFromPort('x-label')
        else:
          xlabel = self.getInputFromPort('parameter')
        if (self.hasInputFromPort('y-label')):
          ylabel = self.getInputFromPort('y-label')
        else:
          ylabel = self.getInputFromPort('observable')
        f.write('  <legend show="true"/>\n')
        f.write('  <xaxis label="' + str(xlabel) + '" type="PARAMETER" name="' + str(self.getInputFromPort('parameter')) + '"/>\n')
        f.write('  <yaxis label="' + str(ylabel) + '" type="SCALAR_AVERAGE" name="' + str(self.getInputFromPort('observable')) + '"/>\n')
        if (self.hasInputFromPort('for-each')):
          f.write('  <for-each name="' + str(self.getInputFromPort('for-each')) + '"/>\n')
        f.write('</plot>\n')
        f.close()
        self.setResult('value',self)
    _input_ports = [('parameter', [basic.String]),
                    ('observable', [basic.String]),
                    ('x-label', [basic.String]),
                    ('y-label', [basic.String]),
                    ('title',[basic.String]),
                    ('for-each',[basic.String])]
    _output_ports = [('value',PlotDescription)]

class PlotFile(basic.File):
   """ a plot in XML """

class ExtractAnything(alpscore.SystemCommand):
    def compute(self):
        outputfile = self.interpreter.filePool.create_file(suffix=self.suffix)
        cmdlist = [alpscore._get_path(self.extractapp), 
                   self.getInputFromPort('plotdescription').name ]
        cmdlist += self.getInputFromPort('data')
        cmdlist += [ '>', outputfile.name]
        self.execute(cmdlist)
        self.setResult('file',outputfile)
        f = file(outputfile.name,'r')
        self.setResult('source',f.read())
    _input_ports = [('data',[basic.List]),
                    ('plotdescription',[PlotDescription])]
    _output_ports = [('file',[basic.File]),
                     ('source',[basic.String])]

class Plot2Anything(alpscore.SystemCommand):
    def compute(self):
        outputfile = self.interpreter.filePool.create_file(suffix=self.suffix)
        cmdlist = [alpscore._get_path(self.extractapp), 
                   self.getInputFromPort('plot').name, '>', outputfile.name]
        self.execute(cmdlist)
        self.setResult('file',outputfile)
        f = file(outputfile.name,'r')
        self.setResult('source',f.read())
    _input_ports = [('plot',[PlotFile])]
    _output_ports = [('file',[basic.File]),
                     ('source',[basic.String])]
       
       
class ExtractXMGR(ExtractAnything):
    suffix='xmgr'
    extractapp='extractxmgr'

class ExtractText(ExtractAnything):
    suffix='txt'
    extractapp='extracttext'

class ExtractMpl(ExtractAnything):
    suffix='py'
    extractapp='extractmpl'
    
class Plot2XMGR(Plot2Anything):
    suffix='xmgr'
    extractapp='plot2xmgr'

class Plot2Text(Plot2Anything):
    suffix='txt'
    extractapp='plot2text'

class Plot2Mpl(Plot2Anything):
    suffix='py'
    extractapp='plot2mpl'

class AlpsMplPlot(MplSource):
    _input_ports=[('source', basic.String)]
  
def initialize(): pass

def selfRegister():

  reg = vistrails.core.modules.module_registry.get_module_registry()

  reg.add_module(PlotDescription,namespace="Plots",abstract=True)
  reg.add_output_port(PlotDescription, "value", PlotDescription)
  reg.add_output_port(PlotDescription, "self", PlotDescription, True)
  reg.add_module(PlotScalarVersusParameter,namespace="Plots",abstract=True)
  reg.add_module(PlotFile,namespace="Plots",abstract=True)

  reg.add_module(ExtractAnything,namespace="Plots",abstract=True)
  reg.add_module(ExtractXMGR,namespace="Plots",abstract=True)
  reg.add_module(ExtractText,namespace="Plots",abstract=True)
  reg.add_module(ExtractMpl,namespace="Plots",abstract=True)
  reg.add_module(Plot2Anything,namespace="Plots",abstract=True)
  reg.add_module(Plot2XMGR,namespace="Plots",abstract=True)
  reg.add_module(Plot2Text,namespace="Plots",abstract=True)
  reg.add_module(Plot2Mpl,namespace="Plots",abstract=True)
  
  reg.add_module(DisplayGracePlot,namespace="DataSet|Plot")
  reg.add_module(DisplayGnuplot,namespace="DataSet|Plot")
  reg.add_module(AlpsMplPlot,namespace="Plots",abstract=True)
  
 # reg.add_module(MakePlot)
