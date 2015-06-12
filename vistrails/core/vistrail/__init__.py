###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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


def enable_package(identifier):
    """Enables a package.
    """
    from vistrails.core.modules.module_registry import MissingPackage
    from vistrails.core.packagemanager import get_package_manager

    pm = get_package_manager()

    try:
        pm.get_package(identifier)
    except MissingPackage:
        dep_graph = pm.build_dependency_graph([identifier])
        for pkg_id in pm.get_ordered_dependencies(dep_graph):
            pkg = pm.identifier_is_available(pkg_id)
            if pkg is None:
                raise
            pm.late_enable_package(pkg.codepath)


def build_pipeline(modules, connections=[], add_port_specs=[],
                   enable_pkg=True):
    """Build a pipeline.

    `modules` is a list of module tuples describing the modules to be created,
    with the following format:
        [('ModuleName', 'package.identifier', [
            # Functions
            ('port_name', [
                # Function parameters
                ('Signature', 'value-as-string'),
            ]),
        ])]

    `connections` is a list of tuples describing the connections to make, with
    the following format:
        [
            (source_module_index, 'source_port_name',
             dest_module_index, 'dest_module_name'),
         ]

    `add_port_specs` is a list of specs to add to modules, with the following
    format:
        [
            (mod_id, 'input'/'output', 'portname',
             '(port_sig)'),
        ]
    It is useful to create modules that can have custom ports through a
    configuration widget.
    """
    from vistrails.core.modules.module_registry import MissingPackage
    from vistrails.core.packagemanager import get_package_manager
    from vistrails.core.vistrail.connection import Connection
    from vistrails.core.vistrail.module import Module
    from vistrails.core.vistrail.module_function import ModuleFunction
    from vistrails.core.vistrail.module_param import ModuleParam
    from vistrails.core.vistrail.pipeline import Pipeline
    from vistrails.core.vistrail.port import Port
    from vistrails.core.vistrail.port_spec import PortSpec

    pm = get_package_manager()

    port_spec_per_module = {} # mod_id -> [portspec: PortSpec]
    j = 0
    for i, (mod_id, inout, name, sig) in enumerate(add_port_specs):
        mod_specs = port_spec_per_module.setdefault(mod_id, [])
        ps = PortSpec(id=i,
                      name=name,
                      type=inout,
                      sigstring=sig,
                      sort_key=-1)
        for psi in ps.port_spec_items:
            psi.id = j
            j += 1
        mod_specs.append(ps)

    pipeline = Pipeline()
    module_list = []
    for i, (name, identifier, functions) in enumerate(modules):
        function_list = []
        try:
            pkg = pm.get_package(identifier)
        except MissingPackage:
            if not enable_pkg:
                raise
            enable_package(identifier)
            pkg = pm.get_package(identifier)

        for func_name, params in functions:
            param_list = []
            for j, (param_type, param_val) in enumerate(params):
                param_list.append(ModuleParam(pos=j,
                                              type=param_type,
                                              val=param_val))
            function_list.append(ModuleFunction(name=func_name,
                                                parameters=param_list))
        name = name.rsplit('|', 1)
        if len(name) == 2:
            namespace, name = name
        else:
            namespace = None
            name, = name
        module = Module(name=name,
                        namespace=namespace,
                        package=identifier,
                        version=pkg.version,
                        id=i,
                        functions=function_list)
        for port_spec in port_spec_per_module.get(i, []):
            module.add_port_spec(port_spec)
        pipeline.add_module(module)
        module_list.append(module)

    for i, (sid, sport, did, dport) in enumerate(connections):
        s_sig = module_list[sid].get_port_spec(sport, 'output').sigstring
        d_sig = module_list[did].get_port_spec(dport, 'input').sigstring
        pipeline.add_connection(Connection(
                id=i,
                ports=[
                    Port(id=i*2,
                         type='source',
                         moduleId=sid,
                         name=sport,
                         signature=s_sig),
                    Port(id=i*2+1,
                         type='destination',
                         moduleId=did,
                         name=dport,
                         signature=d_sig),
                ]))

    return pipeline
