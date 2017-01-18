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

import os
import traceback

from vistrails.core import debug
from vistrails.core.modules.config import InputPort
import vistrails.core.modules.module_registry
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    new_module
from vistrails.core.system import current_dot_vistrails

from . import identifiers
from .notebook import execute, read_metadata, render_output


TYPE_MAP = {
    'int': 'basic:Integer',
    'float': 'basic:Float',
    'number': 'basic:Float',
    'str': 'basic:String',
    'string': 'basic:String',
}


class Notebook(Module):
    """A notebook.
    """
    notebook = None
    inputs = None
    outputs = None

    def compute(self):
        inputs = {}
        for name, optional in self.inputs:
            if optional and not self.has_input(name):
                continue
            inputs[name] = self.get_input(name)

        nb = execute(self.notebook, inputs)
        html = render_output(nb, self.outputs)
        self.set_output('html_result', html)


def initialize():
    reload_notebooks(True)


notebooks = {}


def reload_notebooks(initial=False):
    reg = vistrails.core.modules.module_registry.get_module_registry()

    for notebook_name in notebooks.iterkeys():
        del notebooks[notebook_name]
        reg.delete_module(identifiers.identifier, notebook_name)

    directory = os.path.join(current_dot_vistrails(), 'notebooks')
    if not os.path.exists(directory):
        os.mkdir(directory)
        return

    if initial:
        reg.add_module(Notebook, abstract=True)

    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.ipynb'):
                continue
            filename = os.path.join(dirpath, filename)

            try:
                add_notebook(reg, filename)
            except Exception as exc:
                debug.unexpected_exception(exc)

                debug.critical("Package Notebooks failed to load %s: %s" % (
                    filename, exc),
                    traceback.format_exc())


def add_notebook(reg, filename):
    metadata = read_metadata(filename)

    inputs = metadata.get('__inputs__', [])
    vistrails_inputs = []
    for elem in inputs:
        signature = 'basic:Variant'
        kwargs = {}
        if isinstance(elem, (tuple, list)):
            name = elem[0]
            if len(elem) >= 2:
                for k, v in elem[1].iteritems():
                    if k == 'type':
                        signature = TYPE_MAP.get(v, v)
                    elif k == 'optional':
                        kwargs['optional'] = v
                    else:
                        debug.warning("Unknown input setting %s" % k)
        else:
            name = elem
        vistrails_inputs.append((name, signature, kwargs))

    outputs = metadata.get('__output_cells__', 1)

    module_class = new_module(
        Notebook, os.path.basename(filename)[:-6],
        {'inputs': [(e[0], e[2].get('optional', True))
                    for e in vistrails_inputs],
         'outputs': outputs,
         'notebook': filename},
        "Notebook %s" % filename)
    reg.add_module(module_class, package=identifiers.identifier,
                   package_version=identifiers.version)
    for name, signature, kwargs in vistrails_inputs:
        reg.add_input_port(module_class, name, signature, **kwargs)
    reg.add_output_port(module_class, 'html_result', 'basic:String')


def menu_items():
    return [("Reload Notebooks", reload_notebooks)]


def context_menu(name):
    if name is None:
        return [("Reload Notebooks", reload_notebooks)]
    else:
        return None
