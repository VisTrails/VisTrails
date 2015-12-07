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
""" extensible class that generates a vistrails module from a ModuleSpec
    extra attributes are appended to the module as an attribute by default
"""

from vistrails.core.modules.config import CIPort, COPort, ModuleSettings
from .common import get_input_spec, get_output_spec
from .specs import ModuleSpec

class ModuleSpecGenerator(object):
    def __init__(self, module_spec=ModuleSpec):
        """
        Parameters
        ----------
        module_spec : subclass of ModuleSpec, default ModuleSpec
            The module spec class
        """
        self.ModuleSpec = module_spec

    def generate(self, spec, base_classes, **module_settings):
        """Create a module from a python function specification

        Parameters
        ----------
        spec : ModuleSpec
            A module specification
        base_classes : dict([(name, Module)])
            dict of Module subclasses to use as base classes
        module_settings : kwarg with extra module setting attributes
        """
        module_settings.update(spec.get_module_settings())
        _settings = ModuleSettings(**module_settings)

        # convert input/output specs into VT port objects
        input_ports = [CIPort(ispec.name, ispec.get_port_type(), **ispec.get_port_attrs())
                       for ispec in spec.all_input_port_specs()]
        output_ports = [COPort(ospec.name, ospec.get_port_type(), **ospec.get_port_attrs())
                        for ospec in spec.output_port_specs]

        _input_spec_table = {}
        for ps in spec.input_port_specs:
            _input_spec_table[ps.name] = ps
        _output_spec_table = {}
        for ps in spec.output_port_specs:
            _output_spec_table[ps.name] = ps

        d = {'__module__': __name__,
             '_settings': _settings,
             '__doc__': spec.docstring,
             '__name__': spec.name or spec.module_name,
             '_input_ports': input_ports,
             '_output_ports': output_ports,
             '_input_spec_table': _input_spec_table,
             '_output_spec_table': _output_spec_table}

        superklass = base_classes.get(spec.superklass, None)
        # Put methods for accessing superclasses on top classes
        if superklass is None:
            d['_get_input_spec'] = classmethod(get_input_spec)
            d['_get_output_spec'] = classmethod(get_output_spec)

        new_class = type(str(spec.module_name), (superklass,), d)
        extra_args = set(self.ModuleSpec.attrs)-set(ModuleSpec.attrs)
        for arg in extra_args:
            self.handle_extra_arg(new_class, arg, getattr(spec, arg))

        base_classes[spec.module_name] = new_class
        return new_class

    def handle_extra_arg(self, module, arg, value):
        """ Handles extra arguments not in ModuleSpec.args

            Override this to handle extra args differently
        """
        setattr(module, arg, value)
