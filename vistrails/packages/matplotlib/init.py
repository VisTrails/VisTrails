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

import matplotlib
matplotlib.use('Qt4Agg', warn=False)

import vistrails.core.modules.module_registry
import vistrails.core.db.action
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.operation import AddOp

from bases import _modules as _base_modules, MplFigureOutput
from plots import _modules as _plot_modules
from artists import _modules as _artist_modules
from identifiers import identifier

################################################################################

#list of modules to be displaced on matplotlib.new package
_modules = _base_modules + _plot_modules + _artist_modules

def initialize(*args, **kwargs):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    if reg.has_module('org.vistrails.vistrails.spreadsheet',
                      'SpreadsheetCell'):
        from figure_cell import MplFigureCell, MplFigureToSpreadsheet
        _modules.append(MplFigureCell)
        MplFigureOutput.register_output_mode(MplFigureToSpreadsheet)

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
                       'src_port_remap': {'source': 'value',
                                          'self': 'value'}})],
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
                                          'ylabel': None,
                                          'self': 'value'},
                       'src_port_remap': {'source': 'value'}})],
                    'MplHistogram':
                    [(None, '1.0.0', 'MplHist',
                      {'dst_port_remap': {'columnData': 'x',
                                          'bins': 'bins',
                                          'facecolor': None,
                                          'title': None,
                                          'xlabel': None,
                                          'ylabel': None,
                                          'self': 'value'},
                       'src_port_remap': {'source': 'value'}})],
                }

    # '1.0.2' -> '1.0.3' changes 'self' output port to 'value'
    module_remap.setdefault('MplSource', []).append(
                (None, '1.0.3', None, {
                 'src_port_remap': {'self': 'value'}}))
    if module.name in (m.__name__ for m in _plot_modules + _artist_modules):
        module_remap.setdefault(module.name, []).append(
                (None, '1.0.3', None, {
                 'src_port_remap': {'self': 'value'}}))

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

    return action_list
