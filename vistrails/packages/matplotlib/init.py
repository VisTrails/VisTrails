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

from __future__ import absolute_import # 'import .numpy' is not ambiguous

import copy
import time
import urllib

import vistrails.core.modules
import vistrails.core.modules.module_registry
from vistrails.core import debug
import vistrails.core.db.action
from vistrails.core.modules.basic_modules import Boolean, Color, File, List, \
    String, Integer, Float
from vistrails.core.modules.vistrails_module import Module, NotCacheable, InvalidOutput
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.operation import AddOp

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

from .bases import _modules as _base_modules
from .plots import _modules as _plot_modules
from .artists import _modules as _artist_modules
from .numpy import _modules as _numpy_modules
from .identifiers import identifier

################################################################################

#list of modules to be displaced on matplotlib.new package
_modules = _base_modules + _plot_modules + _artist_modules + _numpy_modules

def initialize(*args, **kwargs):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    if reg.has_module('edu.utah.sci.vistrails.spreadsheet',
                      'SpreadsheetCell'):
        from .figure_cell import MplFigureCell
        _modules.append(MplFigureCell)


###############################################################################

# Define DAT plots
try:
    from dat.packages import Plot, DataPort, ConstantPort, Variable, \
        FileVariableLoader, VariableOperation, OperationArgument, \
        translate, derive_varname
except ImportError:
    pass # We are not running DAT; skip plot/variable/operation definition
else:
    from PyQt4 import QtGui

    from .numpy import NumPyArray

    _ = translate('packages.matplotlib')

    # Builds a DAT variable from a data file
    def build_variable(filename, dtype, shape=None):
        var = Variable(type=List)
        # We use the high-level interface to build the variable pipeline
        mod = var.add_module(NumPyArray)
        mod.add_function('file', File, filename)
        mod.add_function('datatype', String, dtype)
        if shape is not None:
            mod.add_function('shape', List, repr(shape))
        # We select the 'value' output port of the NumPyArray module as the
        # port that will be connected to plots when this variable is used
        var.select_output_port(mod, 'value')
        return var

    ########################################
    # Defines plots from subworkflow files
    #
    _plots = [
        Plot(name="Matplotlib bar diagram",
             subworkflow='{package_dir}/dat-plots/bar.xml',
             description=_("Build a bar diagram out of two lists"),
             ports=[
                 DataPort(name='left', type=List, optional=True),
                 DataPort(name='height', type=List),
                 ConstantPort(name='title', type=String, optional=True),
                 ConstantPort(name='alpha', type=Float, optional=True),
                 ConstantPort(name='facecolor', type=Color, optional=True),
                 ConstantPort(name='edgecolor', type=Color, optional=True)]),
        Plot(name="Matplotlib box plot",
             subworkflow='{package_dir}/dat-plots/boxplot.xml',
             description=_("Build a box diagram out of a list of values"),
             ports=[
                 DataPort(name='values', type=List),
                 ConstantPort(name='title', type=String, optional=True),
                 ConstantPort(name='edgecolor', type=Color, optional=True)]),
        Plot(name="Matplotlib histogram",
             subworkflow='{package_dir}/dat-plots/hist.xml',
             description=_("Build a histogram out of a list"),
             ports=[
                 DataPort(name='x', type=List),
                 ConstantPort(name='title', type=String, optional=True),
                 ConstantPort(name='bins', type=Integer, optional=True),
                 ConstantPort(name='alpha', type=Float, optional=True),
                 ConstantPort(name='facecolor', type=Color, optional=True),
                 ConstantPort(name='edgecolor', type=Color, optional=True)]),
        Plot(name="Matplotlib image",
             subworkflow='{package_dir}/dat-plots/imshow.xml',
             description=_("Shows a 2D MxN or MxNx3 matrix as an image"),
             ports=[
                 DataPort(name='matrix', type=List),
                 ConstantPort(name='title', type=String, optional=True)]),
        Plot(name="Matplotlib line plot",
             subworkflow='{package_dir}/dat-plots/line.xml',
             description=_("Build a plot out of two lists"),
             ports=[
                 DataPort(name='x', type=List, optional=True),
                 DataPort(name='y', type=List),
                 ConstantPort(name='title', type=String, optional=True),
                 ConstantPort(name='marker', type=String, optional=True),
                 ConstantPort(name='markercolor', type=Color, optional=True),
                 ConstantPort(name='edgecolor', type=Color, optional=True)]),
        Plot(name="Matplotlib pie diagram",
             subworkflow='{package_dir}/dat-plots/pie.xml',
             description=_("Build a pie diagram out of a list of values"),
             ports=[
                 DataPort(name='x', type=List),
                 ConstantPort(name='title', type=String, optional=True)]),
        Plot(name="Matplotlib polar plot",
             subworkflow='{package_dir}/dat-plots/polar.xml',
             description=_("Build a plot out of two lists"),
             ports=[
                 DataPort(name='r', type=List),
                 DataPort(name='theta', type=List),
                 ConstantPort(name='title', type=String, optional=True),
                 ConstantPort(name='marker', type=String, optional=True),
                 ConstantPort(name='markercolor', type=Color, optional=True),
                 ConstantPort(name='edgecolor', type=Color, optional=True)]),
    ]

    ########################################
    # Defines a variable loader
    #
    class BinaryArrayLoader(FileVariableLoader):
        """Loads a NumPy array using numpy:fromfile().
        """
        FORMATS = [
                ("%s (%s)" % (_("byte"), 'numpy.int8'),
                 'int8'),
                ("%s (%s)" % (_("unsigned byte"), 'numpy.uint8'),
                 'uint8'),
                ("%s (%s)" % (_("short"), 'numpy.int16'),
                 'int16'),
                ("%s (%s)" % (_("unsigned short"), 'numpy.uint16'),
                 'uint16'),
                ("%s (%s)" % (_("32-bit integer"), 'numpy.int32'),
                 'int32'),
                ("%s (%s)" % (_("32-bit unsigned integer"), 'numpy.uint32'),
                 'uint32'),
                ("%s (%s)" % (_("64-bit integer"), 'numpy.int64'),
                 'int64'),
                ("%s (%s)" % (_("64-bit unsigned integer"), 'numpy.uint64'),
                 'uint64'),

                ("%s (%s)" % (_("32-bit floating number"), 'numpy.float32'),
                 'float32'),
                ("%s (%s)" % (_("64-bit floating number"), 'numpy.float64'),
                 'float64'),
                ("%s (%s)" % (_("128-bit floating number"), 'numpy.float128'),
                 'float128'),

                ("%s (%s)" % (_("64-bit complex number"), 'numpy.complex64'),
                 'complex64'),
                ("%s (%s)" % (_("128-bit complex number"), 'numpy.complex128'),
                 'complex128'),
                ("%s (%s)" % (_("256-bit complex number"), 'numpy.complex256'),
                 'complex128'),
        ]

        @classmethod
        def can_load(cls, filename):
            return (filename.lower().endswith('.dat') or
                    filename.lower().endswith('.ima'))

        def __init__(self, filename):
            FileVariableLoader.__init__(self)
            self.filename = filename
            self._varname = derive_varname(filename, remove_ext=True,
                                          remove_path=True, prefix="nparray_")

            layout = QtGui.QFormLayout()

            self._format_field = QtGui.QComboBox()
            for label, dtype in BinaryArrayLoader.FORMATS:
                self._format_field.addItem(label)
            layout.addRow(_("Data &format:"), self._format_field)

            self._shape = QtGui.QLineEdit()
            layout.addRow(_("&Shape:"), self._shape)
            shape_label = QtGui.QLabel(_("Comma-separated list of dimensions"))
            label_font = shape_label.font()
            label_font.setItalic(True)
            shape_label.setFont(label_font)
            layout.addRow('', shape_label)

            self.setLayout(layout)

        def load(self):
            shape = str(self._shape.text())
            if not shape:
                shape = None
            else:
                shape = [int(d.strip()) for d in shape.split(',')]
            return build_variable(
                    self.filename,
                    BinaryArrayLoader.FORMATS[
                            self._format_field.currentIndex()][1],
                    shape)

        def get_default_variable_name(self):
            return self._varname

    def npy_load(self, filename):
        return build_variable(filename, 'npy')
    def npy_get_varname(filename):
        return derive_varname(filename, remove_ext=True,
                              remove_path=True, prefix="nparray_")
    NPYArrayLoader = FileVariableLoader.simple(
            extension='.npy',
            load=npy_load,
            get_varname=npy_get_varname)

    _variable_loaders = {
            BinaryArrayLoader: _("Numpy plain binary array"),
            NPYArrayLoader: _("Numpy .NPY format"),
    }

    ########################################
    # Defines variable operations
    #
    _variable_operations = [
        VariableOperation(
            '*',
            subworkflow='{package_dir}/dat-operations/scale_array.xml',
            args=[
                OperationArgument('array', List),
                OperationArgument('num', Float),
            ],
            return_type=List,
            symmetric=True),
    ]


def handle_module_upgrade_request(controller, module_id, pipeline):
    from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
    create_new_connection = UpgradeWorkflowHandler.create_new_connection
    reg = vistrails.core.modules.module_registry.get_module_registry()

    def find_module_in_upgrade_action(action):
        for op in action.operations:
            if isinstance(op, AddOp):
                if op.what == Module.vtType:
                    return op.data
        return None

    def find_inputs(m):
        functions = {}
        for f in m.functions:
            if f.name not in functions:
                functions[f.name] = [f]
            else:
                functions[f.name].append(f)
        connections = {}
        for edge in pipeline.graph.iter_edges_to(m.id):
            c = pipeline.connections[edge[2]]
            if c.destination.name not in connections:
                connections[c.destination.name] = [c]
            else:
                connections[c.destination.name].append(c)
        return (functions, connections)

    def find_figure(m):
        has_new_module = False
        for edge in pipeline.graph.iter_edges_from(m.id):
            to_m = pipeline.modules[edge[1]]
            if to_m.name == 'MplFigure':
                # !!! assume only a single down-stream MplFigure !!!
                # may have old or new module...
                if pipeline.connections[edge[2]].destination.name == 'addPlot':
                    return (to_m, None)
                else:
                    return (to_m, edge)
        return (None, None)

    def attach_inputs(new_module, inputs, selected_inputs):
        conns = []
        for port_name in selected_inputs:
            if port_name in inputs[0]:
                for f in inputs[0][port_name]:
                    if len(f.parameters) > 0:
                        new_param_vals, aliases = zip(*[(p.strValue, p.alias) 
                                                        for p in f.parameters])
                    else:
                        new_param_vals = []
                        aliases = []
                    new_f = controller.create_function(new_module, 
                                                       port_name,
                                                       new_param_vals,
                                                       aliases)
                    new_module.add_function(new_f)
            if port_name in inputs[1]:
                for c in inputs[1][port_name]:
                    source_module = pipeline.modules[c.source.id]
                    new_conn = create_new_connection(controller,
                                                     source_module,
                                                     c.source,
                                                     new_module,
                                                     port_name)
                    conns.append(new_conn)
        return conns

    module = pipeline.modules[module_id]
    to_properties = []
    to_axes = []
    old_figure = (None, None)
    if module.name == 'MplScatterplot':
        props_name = 'MplPathCollectionProperties'
        props_input = 'pathCollectionProperties'
        to_properties = ['facecolor']
        to_axes = ['title', 'xlabel', 'ylabel']
        inputs = find_inputs(module)
        old_loc = module.location
        old_figure = find_figure(module)
    elif module.name == 'MplHistogram':
        props_name = 'MplRectangleProperties'
        props_input = 'rectangleProperties'
        to_properties = ['facecolor']
        to_axes = ['title', 'xlabel', 'ylabel']
        inputs = find_inputs(module)
        old_loc = module.location
        old_figure = find_figure(module)

    module_remap = {'MplPlot': 
                    [(None, '1.0.0', 'MplSource',
                      {'dst_port_remap': {'source': 'source',
                                          'Hide Toolbar': None},
                       'src_port_remap': {'source': 'self'}})],
                    'MplFigure': 
                    [(None, '1.0.0', None,
                      {'dst_port_remap': {'Script': 'addPlot'},
                       'src_port_remap': {'FigureManager': 'self',
                                          'File': 'file'}})],
                    'MplFigureCell':
                    [(None, '1.0.0', None,
                      {'dst_port_remap': {'FigureManager': 'figure'}})],
                    # we will delete parts of this but add back later
                    'MplScatterplot':
                    [(None, '1.0.0', 'MplScatter',
                      {'dst_port_remap': {'xData': 'x',
                                          'yData': 'y',
                                          'facecolor': None,
                                          'title': None,
                                          'xlabel': None,
                                          'ylabel': None},
                       'src_port_remap': {'source': 'self'}})],
                    'MplHistogram':
                    [(None, '1.0.0', 'MplHist',
                      {'dst_port_remap': {'columnData': 'x',
                                          'bins': 'bins',
                                          'facecolor': None,
                                          'title': None,
                                          'xlabel': None,
                                          'ylabel': None},
                       'src_port_remap': {'source': 'self'}})],
                }

    action_list = []
    if old_figure[1] is not None and \
       any(p in inputs[0] or p in inputs[1] for p in to_axes):
        # need to remove the edge between plot and figure
        pipeline.graph.delete_edge(*old_figure[1])
        conn = pipeline.connections[old_figure[1][2]]
        action = vistrails.core.db.action.create_action([('delete', conn)])
        action_list.append(action)

    normal_actions = UpgradeWorkflowHandler.remap_module(controller, module_id, 
                                                        pipeline, module_remap)
    action_list.extend(normal_actions)

    more_ops = []
    if any(p in inputs[0] or p in inputs[1] for p in to_properties):
        # create props module
        desc = reg.get_descriptor_by_name(identifier, props_name)
        props_module = \
            controller.create_module_from_descriptor(desc,
                                                     old_loc.x + 100,
                                                     old_loc.y + 100)
        more_ops.append(('add', props_module))

        # attach functions/connections
        conns = attach_inputs(props_module, inputs, to_properties)
        more_ops.extend([('add', c) for c in conns])
        
        # attach into pipeline
        new_plot_module = find_module_in_upgrade_action(normal_actions[0])
        assert new_plot_module is not None
        new_conn = create_new_connection(controller,
                                         props_module,
                                         'self',
                                         new_plot_module,
                                         props_input)
        more_ops.append(('add', new_conn))

    if any(p in inputs[0] or p in inputs[1] for p in to_axes):
        # create axes module
        desc = reg.get_descriptor_by_name(identifier, "MplAxesProperties")
        if old_figure[0] is not None:
            old_loc = old_figure[0].location
        axes_module = \
            controller.create_module_from_descriptor(desc,
                                                     old_loc.x + 100,
                                                     old_loc.y + 100)
        more_ops.append(('add', axes_module))

        # attach functions/connections
        conns = attach_inputs(axes_module, inputs, to_axes)
        more_ops.extend([('add', c) for c in conns])
        
        # attach axes properties to new figure
        if old_figure[0] is not None and old_figure[1] is not None:
            # remap figure
            fig_action = UpgradeWorkflowHandler.remap_module(controller,
                                                             old_figure[0].id,
                                                             pipeline,
                                                             module_remap)
            fig_module = find_module_in_upgrade_action(fig_action[0])
            assert fig_module is not None
            # add the removed edge back in
            pipeline.graph.add_edge(*old_figure[1])
            action_list.extend(fig_action)

            new_plot_module = find_module_in_upgrade_action(normal_actions[0])
            assert new_plot_module is not None
            conn = create_new_connection(controller,
                                         new_plot_module,
                                         'self',
                                         fig_module,
                                         'addPlot')
            action = vistrails.core.db.action.create_action([('add', conn)])
            action_list.append(action)
        else:
            fig_module = old_figure[0]
        new_conn = create_new_connection(controller,
                                         axes_module,
                                         'self',
                                         fig_module,
                                         'axesProperties')
        more_ops.append(('add', new_conn))
    
    # for action in action_list:
    #     for op in action.operations:
    #         print "@+>:", op
    return action_list
