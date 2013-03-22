###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

import copy
import time
import urllib

import vistrails.core.modules
from vistrails.core.modules.basic_modules import PythonSource
import vistrails.core.modules.module_registry
from vistrails.core import debug
from vistrails.core.modules.basic_modules import File, String, Boolean
from vistrails.core.modules.vistrails_module import Module, NotCacheable, InvalidOutput

from vistrails.core.bundles import py_import
try:
    mpl_dict = {'linux-ubuntu': 'python-matplotlib',
                'linux-fedora': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg', warn=False)
    pylab = py_import('pylab', mpl_dict)
    import matplotlib.transforms as mtransforms
except Exception, e:
    debug.critical("Exception: %s" % e)

################################################################################

class MplProperties(Module):
    _output_ports = [("self", "(MplProperties)")]
    
    def update_props(self, objs):
        # must implement in subclass
        pass
        

#base class for 2D plots
class MplPlot(NotCacheable, Module):
    # _input_ports = [("subfigRow", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]}),
    #                 ("subfigCol", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]})]
    _output_ports = [("self", "(MplPlot)")]

    def __init__(self):
        Module.__init__(self)
        # self.figInstance = None

    # def set_fig(self, fig):
    #     self.figInstance = fig

    # def get_fig(self):
    #     if self.figInstance is None:
    #         self.figInstance = pylab.figure()
    #     return self.figInstance

    # def get_translation(self, port, val):
    #     '''doing translation for enum type of the input ports'''
        
    #     for klass in self.__class__.mro():
    #         if '_mpl_translations' in klass.__dict__ and \
    #                 port in klass._mpl_translations:
    #             obj = klass._mpl_translations[port]
    #             if isinstance(obj, dict):
    #                 if val in obj:
    #                     return obj[val]
    #                 else:
    #                     raise ArtistException(
    #                         "Value '%s' for input '%s' invalid." % (val, port))
    #             else:
    #                 print "trying to call"
    #                 return obj(val)
    #     return None
    
    # def get_kwargs_except(self, listExcepts):
    #     ''' getting all the input ports except those ports listed inside listExcepts
    #         return format: {port_name:value,...}'''
    #     kwargs = {}
    #     for port in self.inputPorts:
    #         if port not in listExcepts:
    #             val = self.getInputFromPort(port)
    #             translation = self.get_translation(port, val)
    #             if translation is not None:
    #                 kwargs[port] = translation
    #             else:
    #                 kwargs[port] = val
    #     return kwargs
            
class MplSource(MplPlot):
    """
    MplSource is a module similar to PythonSource. The user can enter
    Matplotlib code into this module. This will then get connected to
    MplFigure to draw the figure. Please note that, codes entered in
    this module should limit to subplot() scope only. Using
    Figure-level commands, e.g. figure() or show(), the result will be
    unknown
    
    """
    _input_ports = [('source', '(basic:String)')]

    run_code = PythonSource.run_code
    def compute(self):
        """ compute() -> None        
        
        """
        source = self.getInputFromPort('source')
        s = ('from pylab import *\n' +
             'from numpy import *\n' +
             urllib.unquote(source))

        # FIXME there is probably a better way of doing this but
        # cannot use multiple inheritance because of the single parent
        # descriptor issue in the registry (InvalidModuleClass exc)
        old_class = self.__class__
        self.__class__ = PythonSource
        PythonSource.run_code(self, s, use_input=True, use_output=True)
        self.__class__ = old_class

class MplFigure(Module):
    # _input_ports = [("addPlot", "(MplPlot)"),
    #                 ("numSubfigRows", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]}),
    #                 ("numSubfigCols", "(edu.utah.sci.vistrails.basic:Integer)",
    #                  {"defaults": ["1"]}),
    #                 ]
    _input_ports = [("addPlot", "(MplPlot)"),
                    ("axesProperties", "(MplAxesProperties)"),
                    ("figureProperties", "(MplFigureProperties)"),
                    ("setLegend", "(MplLegend)")]

    _output_ports = [("self", "(MplFigure)")]

    def __init__(self):
        Module.__init__(self)
        self.figInstance = None

    def updateUpstream(self):
        if self.figInstance is None:
            self.figInstance = pylab.figure()
        pylab.hold(True)
        Module.updateUpstream(self)

    def compute(self):
        plots = self.getInputListFromPort("addPlot")
        # num_rows = self.getInputFromPort("numSubfigRows")
        # if num_rows < 1:
        #     raise ModuleError(self, "numSubfigRows must be at least 1.")
        # num_cols = self.getInputFromPort("numSubfigCols")
        # if num_cols < 1:
        #     raise ModuleError(self, "numSubfigCols must be at least 1.")
        # if len(plots) < 1:
        #     raise ModuleError(self, "Must add at least one plot to figure.")

        # FIXME just take the fig instance from the first plot
        # self.figInstance = plots[0].figInstance

        if self.hasInputFromPort("figureProperties"):
            figure_props = self.getInputFromPort("figureProperties")
            figure_props.update_props(self.figInstance)
        if self.hasInputFromPort("axesProperties"):
            axes_props = self.getInputFromPort("axesProperties")
            axes_props.update_props(self.figInstance.gca())
        if self.hasInputFromPort("setLegend"):
            legend = self.getInputFromPort("setLegend")
            self.figInstance.gca().legend()

        # if num_rows > 1 or num_cols > 1:
        #     # need to reconstruct plot...
        #     self.figInstance = pylab.figure()
        # else:
        #     self.figInstance = plots[0].figInstance

        # for plot in plots:
        #     p_axes = plot.get_fig().gca()
        #     print "DPI:", plot.get_fig().dpi
        #     for c in p_axes.collections:
        #         print "TRANSFORM:", c._transform
        #         print "DATALIM:", c.get_datalim(p_axes.transData)
        #         print "PREPARE POINTS:", c._prepare_points()

        # self.figInstance = pylab.figure()
        # axes = self.figInstance.gca()
        # x0 = None
        # x1 = None
        # y0 = None
        # y1 = None
        # dataLim = None
        # for plot in plots:
        #     p_axes = plot.get_fig().gca()
        #     dataLim = p_axes.dataLim.frozen()
        #     p_x0, p_x1 = p_axes.get_xlim()
        #     if x0 is None or p_x0 < x0:
        #         x0 = p_x0
        #     if x1 is None or p_x1 > x1:
        #         x1 = p_x1
        #     p_y0, p_y1 = p_axes.get_ylim()
        #     if y0 is None or p_y0 < y0:
        #         y0 = p_y0
        #     if y1 is None or p_y1 > y1:
        #         y1 = p_y1

        # print x0, x1, y0, y1
        # axes.set_xlim(x0, x1, emit=False, auto=None)
        # axes.set_ylim(y0, y1, emit=False, auto=None)

        # # axes.dataLim = dataLim
        # # axes.ignore_existing_data_limits = False
        # # axes.autoscale_view()

        # for plot in plots:
        #     p_axes = plot.get_fig().gca()
        #     # axes.lines.extend(p_axes.lines)
        #     for line in p_axes.lines:
        #         print "adding line!"
        #         line = copy.copy(line)
        #         line._transformSet = False
        #         axes.add_line(line)
        #     # axes.patches.extend(p_axes.patches)
        #     for patch in p_axes.patches:
        #         print "adding patch!"
        #         patch = copy.copy(patch)
        #         patch._transformSet = False
        #         axes.add_patch(patch)
        #     axes.texts.extend(p_axes.texts)
        #     # axes.tables.extend(p_axes.tables)
        #     for table in p_axes.tables:
        #         table = copy.copy(table)
        #         table._transformSet = False
        #         axes.add_table(table)
        #     # axes.artists.extend(p_axes.artists)
        #     for artist in p_axes.artists:
        #         artist = copy.copy(artist)
        #         artist._transformSet = False
        #         axes.add_artist(artist)
        #     axes.images.extend(p_axes.images)
        #     # axes.collections.extend(p_axes.collections)
        #     for collection in p_axes.collections:
        #         print "adding collection!"
        #         # print "collection:", collection.__class__.__name__
        #         # print "datalim:", p_axes.dataLim
        #         # transOffset = axes.transData
        #         collection = copy.copy(collection)
        #         # collection._transformSet = False
        #         # print dir(mtransforms)
        #         collection.set_transform(mtransforms.IdentityTransform())
        #         collection._transOffset = axes.transData
        #         # collection._transformSet = False
        #         collection._label = None
        #         collection._clippath = None
        #         axes.add_collection(collection)
        #         # collection.set_transform(mtransforms.IdentityTransform())
        #         # axes.collections.append(collection)
        #     # axes.containers.extend(p_axes.containers)
        # print "transFigure start:", self.figInstance.transFigure
        # # axes.dataLim = dataLim
        # # axes.ignore_existing_data_limits = False
        # # print "datalim after:", axes.dataLim


        # # print "DPI:", self.figInstance.dpi
        # # for c in axes.collections:
        # #     print "TRANSFORM:", c._transform
        # #     print "DATALIM:", c.get_datalim(p_axes.transData)
        # #     print "PREPARE POINTS:", c._prepare_points()


        self.setResult("self", self)

class MplContourSet(Module):
    pass

class MplQuadContourSet(MplContourSet):
    pass
        
_modules = [(MplProperties, {'abstract': True}),
            (MplPlot, {'abstract': True}), 
            (MplSource, {'configureWidgetType': \
                             ('vistrails.packages.matplotlib.widgets',
                              'MplSourceConfigurationWidget')}),
            MplFigure,
            MplContourSet,
            MplQuadContourSet]
