###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

from .gmap_cell import _modules as gmap_modules
from .vis import _modules as vis_modules
from .identifiers import identifier

from vistrails.core.modules.utils import create_port_spec_string
from vistrails.core.vistrail.port import Port
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.core.vistrail.port_spec_item import PortSpecItem

_modules = gmap_modules + vis_modules

def handle_module_upgrade_request(controller, module_id, pipeline):
    from vistrails.core.modules.module_descriptor import ModuleDescriptor
    from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler, \
        UpgradePackageRemap, UpgradeModuleRemap
    from vistrails.core.modules.basic_modules import identifier as basic_pkg

    def remap_functions(old_module, new_module, function_remap):
        # FIXME need use_registry flag passed through!
        use_registry = True
        function_ops = []
        for function in old_module.functions:
            if function.name in function_remap:
                remap = function_remap[function.name]
                if remap is None:
                    # don't add the function back in
                    continue
                elif not isinstance(remap, basestring):
                    function_ops.extend(remap(function, new_module))
                    continue
                else:
                    function_name = remap

                if len(function.parameters) > 0:
                    new_param_vals, aliases = zip(*[(p.strValue, p.alias)
                                                    for p in function.parameters])
                else:
                    new_param_vals = []
                    aliases = []
                if use_registry:
                    function_port_spec = function_name
                else:
                    def mk_psi(pos):
                        psi = PortSpecItem(module="Module", package=basic_pkg,
                                           namespace="", pos=pos)
                        return psi
                    n_items = len(new_param_vals)
                    function_port_spec = PortSpec(name=function_name,
                                                  items=[mk_psi(i)
                                                         for i in xrange(n_items)])
                new_function = controller.create_function(new_module,
                                                          function_port_spec,
                                                          new_param_vals,
                                                          aliases)
                new_module.add_function(new_function)

        if None in function_remap:
            # used to add new functions
            remap = function_remap[None]
            function_ops.extend(remap(None, new_module))
        return function_ops

    def remap_dst_connections(old_module, new_module, port_remap):
        # FIXME need use_registry flag passed through!
        use_registry = True
        create_new_connection = UpgradeWorkflowHandler.create_new_connection

        ops = []
        for _, conn_id in pipeline.graph.edges_to(old_module.id):
            old_conn = pipeline.connections[conn_id]
            if old_conn.destination.name in port_remap:
                remap = port_remap[old_conn.destination.name]
                if remap is None:
                    # don't add this connection back in
                    continue
                elif not isinstance(remap, basestring):
                    ops.extend(remap(old_conn, new_module))
                    continue
                else:
                    destination_name = remap

                old_src_module = pipeline.modules[old_conn.source.moduleId]
                if use_registry:
                    destination_port = destination_name
                else:
                    destination_port = Port(name=destination_name,
                                            type='destination',
                                            signature=create_port_spec_string(
                                                [(basic_pkg, 'Variant', '')]))

                new_conn = create_new_connection(controller,
                                                 old_src_module,
                                                 old_conn.source,
                                                 new_module,
                                                 destination_port)
                ops.append(('add', new_conn))
        return ops

    def insert_vis(vis_name, vis_port_remap):
        def remap_vis(old_conn, new_cell_module):
            ops = []
            old_src_module = pipeline.modules[old_conn.source.moduleId]
            old_cell_module = pipeline.modules[old_conn.destination.moduleId]

            new_x = (old_src_module.location.x + new_cell_module.location.x)/2.0
            new_y = (old_src_module.location.y + new_cell_module.location.y)/2.0

            new_vis_desc = ModuleDescriptor(package=identifier,
                                            name=vis_name,
                                            version='0.3.0')
            new_vis_module = \
                controller.create_module_from_descriptor(new_vis_desc,
                                                         new_x, new_y)

            function_ops = remap_functions(old_cell_module,
                                           new_vis_module,
                                           vis_port_remap)
            ops.append(('add', new_vis_module))
            ops.extend(function_ops)
            ops.extend(remap_dst_connections(old_cell_module,
                                             new_vis_module,
                                             vis_port_remap))

            create_new_connection = UpgradeWorkflowHandler.create_new_connection
            new_conn_1 = create_new_connection(controller,
                                               old_src_module,
                                               old_conn.source,
                                               new_vis_module,
                                               "table")
            ops.append(('add', new_conn_1))
            new_conn_2 = create_new_connection(controller,
                                               new_vis_module,
                                               "self",
                                               new_cell_module,
                                               "layers")
            ops.append(('add', new_conn_2))
            return ops

        # returns the actual remap function
        return remap_vis

    # zoom gets moved for free from old cell to new cell
    remap = UpgradePackageRemap()
    def add_legacy(fname, module):
        new_function = controller.create_function(module,
                                                  "allowLegacy",
                                                  ["True"])
        return [('add', new_function, 'module', module.id)]
    remap.add_module_remap(UpgradeModuleRemap('0.1.0', '0.3.0', '0.3.0',
                                              new_module="GMapCell",
                                              module_name="GMapCell",
                            dst_port_remap={'table': insert_vis("GMapSymbols",
                                            {None: add_legacy}),
                                            'colormapName': None}))
    remap.add_module_remap(UpgradeModuleRemap('0.1.0', '0.3.0', '0.3.0',
                                              new_module="GMapCell",
                                              module_name="GMapHeatmapCell",
                            dst_port_remap={'table': insert_vis("GMapHeatmap",
                                            {'dissipating': 'dissipating',
                                             'maxIntensity': 'maxIntensity',
                                             'opacity': 'opacity',
                                             'radius': 'radius'}),
                                            'dissipating': None,
                                            'maxIntensity': None,
                                            'opacity': None,
                                            'radius': None,
                                            }))
    remap.add_module_remap(UpgradeModuleRemap('0.1.0', '0.3.0', '0.3.0',
                                              new_module="GMapCell",
                                              module_name="GMapCircleCell",
                            dst_port_remap={'table': insert_vis("GMapCircles",
                                            {'strokeColor': 'strokeColor',
                                             'strokeWeight': 'strokeWeight',
                                             'strokeOpacity': 'strokeOpacity',
                                             'fillColor': 'fillColor',
                                             'fillOpacity': 'fillOpacity'}),
                                            'strokeColor': None,
                                            'strokeWeight': None,
                                            'strokeOpacity': None,
                                            'fillColor': None,
                                            'fillOpacity': None,
                                            }))
    remap.add_module_remap(UpgradeModuleRemap('0.1.0', '0.3.0', '0.3.0',
                                              new_module="GMapCell",
                                              module_name="GMapSymbolCell",
                            dst_port_remap={'table': insert_vis("GMapSymbols",
                                            {'strokeColor': 'strokeColor',
                                             'strokeWeight': 'strokeWeight',
                                             'strokeOpacity': 'strokeOpacity',
                                             'fillStartColor': 'fillStartColor',
                                             'fillEndColor': 'fillEndColor',
                                             'fillOpacity': 'fillOpacity',
                                             'scale': 'scale'}),
                                            'strokeColor': None,
                                            'strokeWeight': None,
                                            'strokeOpacity': None,
                                            'fillStartColor': None,
                                            'fillEndColor': None,
                                            'fillOpacity': None,
                                            'scale': None,
                                        }))

    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                               remap)
