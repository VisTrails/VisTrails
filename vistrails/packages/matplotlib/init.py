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

import core.modules
import core.modules.module_registry
from core import debug
from core.modules.basic_modules import File, String, Boolean
from core.modules.vistrails_module import Module, NotCacheable, InvalidOutput

from core.bundles import py_import
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

class MplPlot(Module):
    _input_ports = [("subfigRow", "(edu.utah.sci.vistrails.basic:Integer)",
                     {"defaults": ["1"]}),
                    ("subfigCol", "(edu.utah.sci.vistrails.basic:Integer)",
                     {"defaults": ["1"]})]
    _output_ports = [("self", "(MplPlot)")]

    def __init__(self):
        Module.__init__(self)
        self.figInstance = None

    def set_fig(self, fig):
        self.figInstance = fig

    def get_fig(self):
        if self.figInstance is None:
            self.figInstance = pylab.figure()
        return self.figInstance

class MplFigure(NotCacheable, Module):
    _input_ports = [("addPlot", "(MplPlot)"),
                    ("numSubfigRows", "(edu.utah.sci.vistrails.basic:Integer)",
                     {"defaults": ["1"]}),
                    ("numSubfigCols", "(edu.utah.sci.vistrails.basic:Integer)",
                     {"defaults": ["1"]}),
                    ]
    _output_ports = [("self", "(MplFigure)")]

    def __init__(self):
        Module.__init__(self)
        self.figInstance = None

    def compute(self):
        plots = self.getInputListFromPort("addPlot")
        num_rows = self.getInputFromPort("numSubfigRows")
        if num_rows < 1:
            raise ModuleError(self, "numSubfigRows must be at least 1.")
        num_cols = self.getInputFromPort("numSubfigCols")
        if num_cols < 1:
            raise ModuleError(self, "numSubfigCols must be at least 1.")
        if len(plots) < 1:
            raise ModuleError(self, "Must add at least one plot to figure.")

        if num_rows > 1 or num_cols > 1:
            # need to reconstruct plot...
            self.figInstance = pylab.figure()
        else:
            self.figInstance = plots[0].figInstance

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
        
# class MplHistogram(MplPlot):
#     _input_ports = [('columnData', '(edu.utah.sci.vistrails.basic:List)'),
#                     ('title', '(edu.utah.sci.vistrails.basic:String)'),
#                     ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
#                     ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
#                     ('bins', '(edu.utah.sci.vistrails.basic:Integer)'),
#                     ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
#     _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

#     def compute(self):
#         data = [float(x) for x in self.getInputFromPort('columnData')]
#         fig = self.get_fig()
#         pylab.setp(fig, facecolor='w')
#         if self.hasInputFromPort('title'):
#             pylab.title(self.getInputFromPort('title'))
#         if self.hasInputFromPort('xlabel'):
#             pylab.xlabel(self.getInputFromPort('xlabel'))
#         if self.hasInputFromPort('ylabel'):
#             pylab.ylabel(self.getInputFromPort('ylabel'))
#         if self.hasInputFromPort('bins'):
#             bins = self.getInputFromPort('bins')
#         else:
#             bins = 10
#         if self.hasInputFromPort('facecolor'):
#             color = self.getInputFromPort('facecolor').tuple
#         else:
#             color = 'b'
#         pylab.hist(data, bins, facecolor=color)
#         pylab.get_current_fig_manager().toolbar.hide()
#         self.setResult('self', self)

# class MplScatterplot(MplPlot):
#     _input_ports = [('xData', '(edu.utah.sci.vistrails.basic:List)'),
#                     ('yData', '(edu.utah.sci.vistrails.basic:List)'),
#                     ('title', '(edu.utah.sci.vistrails.basic:String)'),
#                     ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
#                     ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
#                     ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
#     _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

#     def compute(self):
#         x_data = [float(x) for x in self.getInputFromPort('xData')]
#         y_data = [float(x) for x in self.getInputFromPort('yData')]
#         fig = self.get_fig()
#         # pylab.setp(fig, facecolor='w')
#         if self.hasInputFromPort('title'):
#             pylab.title(self.getInputFromPort('title'))
#         if self.hasInputFromPort('xlabel'):
#             pylab.xlabel(self.getInputFromPort('xlabel'))
#         if self.hasInputFromPort('ylabel'):
#             pylab.ylabel(self.getInputFromPort('ylabel'))
#         if self.hasInputFromPort('facecolor'):
#             color = self.getInputFromPort('facecolor').tuple
#         else:
#             color = 'r'
#         pylab.scatter(x_data, y_data, marker='s', facecolor=color)
#         pylab.get_current_fig_manager().toolbar.hide()
#         self.setResult('self', self)

# class MplLegend(Module):
#     _input_ports = [('fontsize', '(edu.utah.sci.vistrails.basic:Integer)'),
#                     ('numpoints', '(edu.utah.sci.vistrails.basic:Integer)'),
#                     ('scatter

# class MplFigureManager(Module):
#     """
#     MplFigureManager is the figure viewer available from
#     Matplotlib. It supports pan/zoom, save and other plot
#     interactions. It can be embedded in different backend. We are
#     using Qt4Agg backend in this package.
    
#     """

#     def __init__(self):
#         """ MplFigureManager() -> MplFigureManager
#         Init the class as a storage structure
        
#         """
#         Module.__init__(self)
#         self.figManager = None

# class MplFigure(NotCacheable, Module):
#     """
#     MplFigure is a module representing a single figure (type Figure)
#     in Matplotlib. It receive multiple MplPlot inputs
    
#     """
#     def update(self):
#         """ update() -> None        
#         Interfere into the update process to set the appropriate
#         figure command before going upstream to the MplPlot
        
#         """
#         pylab.figure()
#         Module.update(self)

#     def compute(self):
#         """ compute() -> None        
#         Either passing the figure manager to a SpreadsheetCell or save
#         the image to file

#         """
#         noOutput = True
#         if self.outputPorts.has_key('FigureManager'):
#             mfm = MplFigureManager()
#             mfm.figManager = pylab.get_current_fig_manager()
#             self.setResult('FigureManager', mfm)
#             noOutput = False
#         self.setResult('File', InvalidOutput)
#         if 'File' in self.outputPorts:
#             f = self.interpreter.filePool.create_file(suffix='.png')
#             pylab.savefig(f.name)
#             self.setResult('File', f)
#             noOutput = False
#         if noOutput:
#             pylab.show()

from artists import MplArtistProperties, MplLine2DProperties, \
    MplPatchProperties, translate_color

class MplArtistPlot(MplPlot):
    _port_types = {'color': '(edu.utah.sci.vistrails.basic:Color)',
                   'marker': '(edu.utah.sci.vistrails.basic:String)',
                   'linestyle': '(edu.utah.sci.vistrails.basic:String)'}
    _translations = {'marker': {'square': 's', 
                                'point': '.', 
                                'tickdown': 3, 
                                'triangle_right': '>', 
                                'tickup': 2, 
                                'caretup': 6, 
                                'hline': '_', 
                                'vline': '|', 
                                'caretleft': 4, 
                                'pentagon': 'p', 
                                'tri_left': '3', 
                                'caretright': 5, 
                                'tickright': 1, 
                                'tickleft': 0, 
                                'tri_up': '2', 
                                'circle': 'o', 
                                'pixel': ',', 
                                'diamond': 'D', 
                                'star': '*', 
                                'hexagon1': 'h', 
                                'hexagon2': 'H', 
                                'tri_right': '4', 
                                'nothing': '', 
                                'thin_diamond': 'd', 
                                'tri_down': '1', 
                                'triangle_left': '<', 
                                'caretdown': 7, 
                                'plus': '+', 
                                'triangle_down': 'v', 
                                'triangle_up': '^', 
                                'x': 'x',
                                }, 
                     'linestyle': {'solid': '-', 
                                   'dashed': '--', 
                                   'dash_dot': '-.', 
                                   'dotted': ':', 
                                   'draw nothing': ''},
                     'color': translate_color,
                     }
    _port_dicts = {'marker': {'entry_types': ['enum'],
                              'values': [['caretdown', 'caretleft', 'caretright', 'caretup', 'circle', 'diamond', 'hexagon1', 'hexagon2', 'hline', 'nothing', 'pentagon', 'pixel', 'plus', 'point', 'square', 'star', 'thin_diamond', 'tickdown', 'tickleft', 'tickright', 'tickup', 'tri_down', 'tri_left', 'tri_right', 'tri_up', 'triangle_down', 'triangle_left', 'triangle_right', 'triangle_up', 'vline', 'x']]},
                   'linestyle': {'entry_types': ['enum'],
                                 'values': [['dash_dot', 'dashed', 'dotted', 'draw nothing', 'solid']]}
                   }
    # _input_ports = MplArtist._input_ports
    _input_ports = [('properties', '(MplArtistProperties)')]

    @staticmethod
    def update_ports(existing_ports, new_ports):
        ports = {}
        for port in existing_ports:
            ports[port[0]] = port
        for port in new_ports:
            ports[port[0]] = port
        port_list = ports.values()
        port_list.sort()
        return port_list

    @staticmethod
    def build_ports(ports):
        translations = {}
        port_tuples = []
        for port_opts in ports:
            port_name = port_opts[0]
            port_type = port_opts[1]
            if port_type in MplArtistPlot._port_types:
                port_spec = MplArtistPlot._port_types[port_type]
            else:
                port_spec = "(edu.utah.sci.vistrails.basic:%s)" % port_type
            if port_type in MplArtistPlot._translations:
                translations[port_name] = \
                    MplArtistPlot._translations[port_type]
            if port_type in MplArtistPlot._port_dicts:
                port_tuple = (port_name, port_spec, 
                              MplArtistPlot._port_dicts[port_type])
            else:
                port_tuple = (port_name, port_spec)
            port_tuples.append(port_tuple)
        return (port_tuples, translations)

def convert_to_numeric(data_list):
    if len(data_list) > 0 and isinstance(data_list[0], basestring):
        new_list = [float(d) for d in data_list]
        return new_list
    return data_list

class MplLinePlot(MplArtistPlot):
    _input_ports = [('xdata', '(edu.utah.sci.vistrails.basic:List)'),
                 ('ydata', '(edu.utah.sci.vistrails.basic:List)'),
                 ('properties', 
                  '(MplLine2DProperties)')]
    # _input_ports = MplArtistPlot.update_ports(MplLine2D._input_ports,
    #                                           _my_ports)
    
    def compute(self):
        # kwargs = self.get_kwargs()
        fig = self.get_fig()
        xdata = convert_to_numeric(self.getInputFromPort("xdata"))
        ydata = convert_to_numeric(self.getInputFromPort("ydata"))
        # for k,v in kwargs.iteritems():
        #     print "ARG", k, v
        lines = pylab.plot(xdata, ydata) #, **kwargs)
        if self.hasInputFromPort('properties'):
            properties = self.getInputFromPort('properties')
            for line in lines:
                for k, v in properties.kwargs.iteritems():
                    setter = 'set_%s' % k
                    if not hasattr(line, setter):
                        raise ModuleError(self, 
                                          "Cannot set property '%s' here" % k)
                    getattr(line, setter)(v)
        self.setResult('self', self)
                        
        # print "RETVAL:", retval
        # for r in retval:
        #     print r
        #     r.set_marker('*')
        # # pylab.xlabel("Time")
        # # pylab.ylabel("Temperature")
        # self.setResult('self', self)

class MplHistogram(MplArtistPlot): #, MplPatch):
    _my_ports = [('xdata', '(edu.utah.sci.vistrails.basic:List)'),
                 ('bins', '(edu.utah.sci.vistrails.basic:Integer)'),
                 ('range', '(edu.utah.sci.vistrails.basic:Float, ' \
                      'edu.utah.sci.vistrails.basic:Float)'),
                 ('normed', '(edu.utah.sci.vistrails.basic:Boolean)'),
                 ('weights', '(edu.utah.sci.vistrails.basic:List)'),
                 ('cumulative', '(edu.utah.sci.vistrails.basic:Boolean)'),
                 ('histtype', '(edu.utah.sci.vistrails.basic:String)',
                  {"entry_types": ["enum"],
                   "values": [['bar', 'barstacked', 'step', 'stepfilled']]}),
                 ('align', '(edu.utah.sci.vistrails.basic:String)',
                  {"entry_types": ["enum"],
                   "values": [['left', 'mid', 'right']]}),
                 ('orientation', '(edu.utah.sci.vistrails.basic:String)',
                  {"entry_types": ["enum"],
                   "values": [["horizontal", "vertical"]]}),
                 ('rwidth', '(edu.utah.sci.vistrails.basic:Float)'),
                 ('log', '(edu.utah.sci.vistrails.basic:Boolean)')]
    _input_ports = MplArtistPlot.update_ports(MplPatchProperties._input_ports,
                                              _my_ports)

    def compute(self):
        kwargs = self.get_kwargs()
        fig = self.get_fig()
        if "xdata" in kwargs:
            xdata = convert_to_numeric(kwargs["xdata"])
            del kwargs["xdata"]
        if "subfigRow" in kwargs:
            subfigRow
        pylab.hist(xdata, **kwargs)
        self.setResult('self', self)

class MplBoxPlot(MplArtistPlot):
    # _vt_ports = [('flier_color', 'color', 'fliers', 'markeredgecolor'),
    #              ('flier_marker', 'marker', 'fliers', 'marker'),
    #              ('whisker_linestyle', 'linestyle', 'whiskers', 'linestyle'),
    #              ('whisker_color', 'color', 'whiskers', 'color'),
    #              ('cap_color', 'color', 'caps', 'color'),
    #              ('cap_linestyle', 'linestyle', 'caps', 'linestyle'),
    #              ('median_color', 'color', 'medians', 'color'),
    #              ('median_linestyle', 'linestyle', 'medians', 'linestyle'),
    #              ('box_edgecolor', 'color', 'boxes', 'edgecolor'),
    #              ('box_facecolor', 'color', 'boxes', 'facecolor'),
    #              ('box_linestyle', 'linestyle', 'boxes', 'linestyle'),
    #              ('box_filled', 'Boolean')]
    # _vt_port_dict = dict((x[0], x[1:]) for x in _vt_ports)
    
    # extra_ports, _mpl_translations = MplArtistPlot.build_ports(_vt_ports)
    _input_ports = [('xdata', '(edu.utah.sci.vistrails.basic:List)'),
                    ('notch', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('vert', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('whis', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('bootstrap', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('width', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('patch_artist', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('flierProperties', '(MplLine2DProperties)'),
                    ('medianProperties', '(MplLine2DProperties)'),
                    ('whiskerProperties', '(MplLine2DProperties)'),
                    ('capProperties', '(MplLine2DProperties)'),
                    ('boxPatchProperties', '(MplPatchProperties)'),
                    ('boxLineProperties', '(MplLine2DProperties)'),
                    ]
    _property_mapping = {'fliers': 'flierProperties',
                         'medians': 'medianProperties',
                         'whiskers': 'whiskerProperties',
                         'caps': 'capProperties',
                         'boxes': 'boxLineProperties',
                         }

    # print "_INPUT_PORTS:", _input_ports

    def compute(self):
        # kwargs = self.get_kwargs()
        # other_args = []
        # for (k,v) in kwargs.iteritems():
        #     if k in self._vt_port_dict:
        #         other_args.append((k,v))
        # for (k,v) in other_args:
        #     del kwargs[k]
        # if "xdata" in kwargs:
        #     xdata = convert_to_numeric(kwargs["xdata"])
        #     del kwargs["xdata"]
        # else:
        #     # raise the input port missing error through a general method
        #     self.getInputFromPort("xdata")


        # kwargs['patch_artist'] = True
        xdata = self.getInputFromPort("xdata")
        fig = self.get_fig()
        patch_artist = self.forceGetInputFromPort('patch_artist', False)
        output_dict = pylab.boxplot(xdata, patch_artist=patch_artist)
        for output_type, objects in output_dict.iteritems():
            properties = None
            if output_type == 'boxes' and patch_artist:
                if self.hasInputFromPort('boxPatchProperties'):
                    properties = self.getInputFromPort('boxPatchProperties')
            else:
                properties_port = self._property_mapping[output_type]
                if self.hasInputFromPort(properties_port):
                    properties = self.getInputFromPort(properties_port)
            if properties is not None:
                # FIXME which iteration should be outer or inner?
                for obj in objects:
                    for (k,v) in properties.kwargs.iteritems():
                        setter = 'set_%s' % k
                        if not hasattr(obj, setter):
                            raise ModuleError(self, 
                                              "Cannot set property '%s' "
                                              "here" % k)
                    getattr(obj, setter)(v)
                    
        # for (k,v) in other_args:
        #     opts = self._vt_port_dict[k]
        #     output_type = opts[1]
        #     opt_setter = opts[2]
        #     if output_type in output_dict:
        #         for elt in output_dict[output_type]:
        #             setter_name = "set_%s" % opt_setter
        #             if hasattr(elt, setter_name):
        #                 getattr(elt, setter_name)(v)
        self.setResult('self', self)

class MplScatterplot(MplArtistPlot):
    _vt_ports = [('c', 'color'),
                 ('marker', 'marker')]
    _my_ports = [('xdata', '(edu.utah.sci.vistrails.basic:List)'),
                 ('ydata', '(edu.utah.sci.vistrails.basic:List)'),
                 ('s', '(edu.utah.sci.vistrails.basic:Float)'),
                 ('alpha', '(edu.utah.sci.vistrails.basic:Float)')]
    
    extra_ports, _mpl_translations = MplArtistPlot.build_ports(_vt_ports)
    _input_ports = MplArtistPlot.update_ports(MplArtistProperties._input_ports,
                                              _my_ports) + extra_ports
    def compute(self):
        kwargs = self.get_kwargs()
        fig = self.get_fig()
        if "xdata" in kwargs:
            xdata = convert_to_numeric(kwargs["xdata"])
            del kwargs["xdata"]
        if "ydata" in kwargs:
            ydata = convert_to_numeric(kwargs["ydata"])
            del kwargs["ydata"]
        # print "Marker:", kwargs['marker']
        print "xdata:", xdata
        print "ydata:", ydata
        retval = pylab.scatter(xdata, ydata, **kwargs)
        print "RETVAL:", retval
        self.setResult('self', self)

from mpl_toolkits.basemap import Basemap, cm

class MplBasemap(MplPlot):
    _resolutions = {"crude": "c",
                    "low": "l",
                    "intermediate": "i",
                    "high": "h",
                    "full": "f",
                    "None": None}
    _projections = {"McBryde-Thomas Flat-Polar Quartic": "mbtfpq",
                    "Azimuthal Equidistant": "aeqd",
                    "Sinusoidal": "sinu",
                    "Polyconic": "poly",
                    "Oblique Mercator": "omerc",
                    "Gnomonic": "gnom",
                    "Mollweide": "moll",
                    "Lambert Conformal": "lcc",
                    "Transverse Mercator": "tmerc",
                    "North-Polar Lambert Azimuthal": "nplaea",
                    "Gall Stereographic Cylindrical": "gall",
                    "North-Polar Azimuthal Equidistant": "npaeqd",
                    "Miller Cylindrical": "mill",
                    "Mercator": "merc",
                    "Stereographic": "stere",
                    "Equidistant Conic": "eqdc",
                    "Cylindrical Equidistant": "cyl",
                    "North-Polar Stereographic": "npstere",
                    "South-Polar Stereographic": "spstere",
                    "Hammer": "hammer",
                    "Geostationary": "geos",
                    "Near-Sided Perspective": "nsper",
                    "Eckert IV": "eck4",
                    "Albers Equal Area": "aea",
                    "Kavrayskiy VII": "kav7",
                    "South-Polar Azimuthal Equidistant": "spaeqd",
                    "Orthographic": "ortho",
                    "Cassini-Soldner": "cass",
                    "van der Grinten": "vandg",
                    "Lambert Azimuthal Equal Area": "laea",
                    "South-Polar Lambert Azimuthal": "splaea",
                    "Robinson": "robin"}

    _input_ports = [('showCoastlines', 
                     "(edu.utah.sci.vistrails.basic:Boolean)", True),
                    ('showStates',
                     "(edu.utah.sci.vistrails.basic:Boolean)", True),
                    ('showCountries',
                     "(edu.utah.sci.vistrails.basic:Boolean)", True),
                    ('showRivers',
                     "(edu.utah.sci.vistrails.basic:Boolean)", True),
                    ("projection", "(edu.utah.sci.vistrails.basic:String)",
                     {"optional": True,
                      "entry_types": ["enum"],
                      "values": [_projections.keys()],
                      "defaults": ["Cylindrical Equidistant"]}),
                    ("resolution", "(edu.utah.sci.vistrails.basic:String)",
                     {"optional": True,
                      "entry_types": ["enum"],
                      "values": [_resolutions.keys()],
                      "defaults": ["crude"]}),
                    ("llcrnrlon", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("llcrnrlat", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("urcrnrlon", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("urcrnrlat", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("width", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("height", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("lon_0", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("lat_0", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("lat_ts", "(edu.utah.sci.vistrails.basic:Float)", True),
                    ("area_thresh", "(edu.utah.sci.vistrails.basic:Float)", 
                     True),
                    ("rsphere", "(edu.utah.sci.vistrails.basic:Float)",
                     {"optional": True,
                      "defaults": ["6370997.0"]})]
    _output_ports = [('self', "(MplBasemap)")]
    _mpl_translations = {"resolution": _resolutions,
                         "projection": _projections}

    # FIXME merge these with other Mpl classes (duplicates artists:MplAritst)
    def get_translation(self, port, val):
        for klass in self.__class__.mro():
            if '_mpl_translations' in klass.__dict__ and \
                    port in klass._mpl_translations:
                obj = klass._mpl_translations[port]
                if isinstance(obj, dict):
                    if val in obj:
                        return obj[val]
                    else:
                        raise ArtistException(
                            "Value '%s' for input '%s' invalid." % (val, port))
                else:
                    print "trying to call"
                    return obj(val)
        return None

    # FIXME merge these with other Mpl classes (duplicates artists:MplAritst)
    def get_kwargs(self):
        kwargs = {}
        for port in self.inputPorts:
            val = self.getInputFromPort(port)
            translation = self.get_translation(port, val)
            if translation is not None:
                kwargs[port] = translation
            else:
                kwargs[port] = val
        return kwargs

    def __init__(self):
        MplPlot.__init__(self)
        self.map = None

    def compute(self):
        fig = self.get_fig()
        kwargs = self.get_kwargs()
        to_draw = []
        for k, v in kwargs.iteritems():
            if k.startswith("show"):
                if v:
                    to_draw.append(k)
        for elt in to_draw:
            del kwargs[elt]
        # kwargs["ax"] = fig.gca()
        kwargs["fix_aspect"] = False
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        self.map = Basemap(**kwargs)
        for elt in to_draw:
            getattr(self.map, "draw%s" % elt[4:].lower())()

        self.setResult('self', self)
        # m = Basemap(width=3000000,height=2250000,projection='lcc',
        #             resolution='h',lat_0=45,lon_0=-85.)
        # # m = Basemap(width=12000000,height=9000000,projection='lcc',
        # #             resolution='i',lat_0=50,lon_0=-107.)
        # # lat_1=45.,lat_2=55,

        # # draw coastlines.
        # m.drawcoastlines()
        # # draw a boundary around the map, fill the background.
        # # this background will end up being the ocean color, since
        # # the continents will be drawn on top.
        # m.drawmapboundary(fill_color='aqua')
        # # fill continents, set lake color same as ocean color.
        # m.fillcontinents(color='coral',lake_color='aqua')

        # self.setResult('self', self)

class MplMapProject(Module):
    _input_ports = [("latitudes", "(org.vistrails.dakoop.numpy:npArray)"),
                    ("longitudes", "(org.vistrails.dakoop.numpy:npArray)"),
                    ("map", "(MplBasemap)")]
    _output_ports = [("x", "(org.vistrails.dakoop.numpy:npArray)"),
                     ("y", "(org.vistrails.dakoop.numpy:npArray)")]
    
    def compute(self):
        wrapped_map = self.getInputFromPort("map")
        m = wrapped_map.map
        x, y = m(self.getInputFromPort("longitudes"),
                 self.getInputFromPort("latitudes"))
        self.setResult("x", x)
        self.setResult("y", y)
        self.setResult("map", wrapped_map)

class MplMapGrid(Module):
    _input_ports = [("x", "(edu.utah.sci.vistrails.basic:Integer)"),
                    ("y", "(edu.utah.sci.vistrails.basic:Integer)"),
                    ("map", "(MplBasemap)")]
    _output_ports = [("latitudes", "(org.vistrails.dakoop.numpy:npArray)"),
                     ("longitudes", "(org.vistrails.dakoop.numpy:npArray)")]

    def compute(self):
        m = self.getInputFromPort("map").map
        lons, lats = m.makegrid(self.getInputFromPort("x"),
                                self.getInputFromPort("y"))
        self.setResult("longitudes", lons)
        self.setResult("latitudes", lats)

class MplMapContourf(Module):
    _input_ports = [("map", "(MplBasemap)"),
                    ("x", "(org.vistrails.dakoop.numpy:npArray)"),
                    ("y", "(org.vistrails.dakoop.numpy:npArray)"),
                    ("data", "(org.vistrails.dakoop.numpy:npArray)"),
                    ("contourLevels", "(org.vistrails.dakoop.numpy:npArray)")]
    _output_ports = [("map", "(MplBasemap)")]
    
    def compute(self):
        wrapped_map = self.getInputFromPort("map")
        m = wrapped_map.map
        x = self.getInputFromPort("x")
        y = self.getInputFromPort("y")
        data = self.getInputFromPort("data")
        contourLevels = self.getInputFromPort("contourLevels")
        m.contourf(x,y,data,contourLevels, cmap=cm.s3pcpn)
        self.setResult("map", wrapped_map)

# want to be able to use normal plots

class MplBar(MplArtistPlot): # , MplPatch):
    _input_ports = [
        ("linewidth", "(edu.utah.sci.vistrails.basic:Float)",
         {"optional": True,
          "docstring": "width of bar edges; None means use default linewidth; 0 means don't draw edges."}),
        ("capsize", "(edu.utah.sci.vistrails.basic:Float)",
         {"optional": True,
          "docstring": "(default 3) determines the length in points of the error bar caps"}),
        ("log", "(edu.utah.sci.vistrails.basic:Boolean)",
         {"optional": True,
          "docstring": "orientation axis as-is; True sets it to log scale"}),
        ("bottom", "(edu.utah.sci.vistrails.basic:Float)",
         {"optional": True,
          "docstring": "None",
          "entry_types": ['None'],
          "values": [[]]}),
        ("color", "(edu.utah.sci.vistrails.basic:Color)",
         {"optional": True,
          "docstring": "the colors of the bars",
          "entry_types": ['None'],
          "values": [[]]}),
        ("align", "(edu.utah.sci.vistrails.basic:String)",
         {"optional": True,
          "docstring": "'edge' (default) | 'center'",
          "entry_types": ['enum'],
          "values": [['edge', 'center']],
          "defaults": ['edge']}),
        ("height", "(edu.utah.sci.vistrails.basic:List)",
         {"optional": False,
          "docstring": "None"}),
        ("width", "(edu.utah.sci.vistrails.basic:Float)",
         {"optional": True,
          "docstring": "the widths of the bars",
          "entry_types": ['None'],
          "values": [[]],
          "defaults": [0.8]}),
        ("yerr", "(edu.utah.sci.vistrails.basic:String)",
         {"optional": True,
          "docstring": "if not None, will be used to generate errorbars on the bar chart"}),
        ("left", "(edu.utah.sci.vistrails.basic:List)",
         {"optional": False,
          "docstring": "the x coordinates of the left sides of the bars"}),
        ("properties", "MplPatchProperties",
         {"optional": False}),
        ]
    # _input_ports = MplArtistPlot.update_ports(MplPatchProperties._input_ports,
    #                                           _my_ports)
    _mpl_translations = {'color': translate_color}

    
    def compute(self):
        # kwargs = self.get_kwargs()
        fig = self.get_fig()
        # if "left" in kwargs:
        #     left = convert_to_numeric(kwargs["left"])
        #     del kwargs["left"]
        # if "height" in kwargs:
        #     height = convert_to_numeric(kwargs["height"])
        #     del kwargs["height"]
        left = convert_to_numeric(self.getInputFromPort("left"))
        height = convert_to_numeric(self.getInputFromPort("height"))
        patches = pylab.bar(left, height) #, **kwargs)
        if self.hasInputFromPort('properties'):
            properties = self.getInputFromPort('properties')
            for patch in patches:
                for k, v in properties.kwargs.iteritems():
                    setter = 'set_%s' % k
                    if not hasattr(patch, setter):
                        raise ModuleError(self, 
                                          "Cannot set property '%s' here" % k)
                    getattr(patch, setter)(v)
        
        # pylab.xlabel("Time")
        # pylab.ylabel("Temperature")
        self.setResult('self', self)

# _modules = [(MplPlot, {'abstract': True}), MplFigure, 
#             (MplArtistPlot, {'abstract': True}), MplLinePlot, 
#             MplHistogram, MplBoxPlot, MplScatterplot, MplBasemap, MplMapGrid,
#             MplMapContourf, MplMapProject,
#             MplBar]

_modules = [(MplPlot, {'abstract': True}), MplFigure, 
            MplArtistProperties, MplLine2DProperties, MplPatchProperties,
            (MplArtistPlot, {'abstract': True}), 
            MplLinePlot, MplBoxPlot, MplBar]


def initialize(*args, **kwargs):
    reg = core.modules.module_registry.get_module_registry()
    if reg.has_module('edu.utah.sci.vistrails.spreadsheet',
                      'SpreadsheetCell'):
        from figure_cell import MplFigureCell
        _modules.append(MplFigureCell)

################################################################################

# def initialize(*args, **keywords):    

#     reg = core.modules.module_registry.get_module_registry()
    
#     reg.add_module(MplPlot, configureWidgetType=MplPlotConfigurationWidget)
# #    reg.add_input_port(MplPlot, 'source', String, True)
#     reg.add_input_port(MplPlot, 'Hide Toolbar', Boolean, True)
#     reg.add_output_port(MplPlot, 'source', String)
    
#     reg.add_module(MplFigureManager)

#     reg.add_module(MplFigure)
#     reg.add_input_port(MplFigure, 'Script', String)
#     reg.add_output_port(MplFigure, 'FigureManager', MplFigureManager)
#     reg.add_output_port(MplFigure, 'File', File)
    
#     # Register a figure cell type if the spreadsheet is up
#     if reg.has_module('edu.utah.sci.vistrails.spreadsheet',
#                                'SpreadsheetCell'):
#         from figure_cell import MplFigureCell
#         reg.add_module(MplFigureCell)
#         reg.add_input_port(MplFigureCell, 'FigureManager', MplFigureManager)

