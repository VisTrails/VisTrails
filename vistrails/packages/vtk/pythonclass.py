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

from itertools import izip

from vistrails.core.debug import format_exc
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.config import CIPort, COPort, ModuleSettings

from .common import convert_input, convert_output, get_input_spec, get_output_spec


class BaseClassModule(Module):
    """ Wraps a python class as a vistrails Module using a ClassSpec
        setter methods are used as inputs and getter methods as outputs

    """
    _settings = ModuleSettings(abstract=True)

    _get_input_spec = classmethod(get_input_spec)
    _get_output_spec = classmethod(get_output_spec)

    def call_set_method(self, instance, port, params):
        # convert params
        params = convert_input(params, self.input_specs[port.name].signature)
        if isinstance(params, tuple):
            params = list(params)
        elif not isinstance(params, list):
            params = [params]
        method_name = port.method_name
        if port.method_type == 'OnOff':
            # This converts OnOff ports to XOn(), XOff() calls
            method_name = method_name + ('On' if params[0] else 'Off')
            params = []
        elif port.method_type == 'nullary':
            # Call X() only if boolean is true
            if params[0]:
                params = []
            else:
                return
        elif port.method_type == 'SetXToY':
            # Append enum name to function name and delete params
            method_name += params[0]
            params = []
        prepend_params = port.get_prepend_params()
        # print "SETTING", method_name, prepend_params + params, instance.vtkInstance.__class__.__name__
        method = getattr(instance, method_name)
        try:
            method(*(prepend_params + params))
        except Exception, e:
            raise

    def call_get_method(self, instance, port):
        # print "GETTING", port.method_name, port.get_prepend_params(), instance.vtkInstance.__class__.__name__
        method = getattr(instance, port.method_name)
        try:
            value = method(*(port.get_prepend_params()))
            # convert params
            return convert_output(value, self.output_specs[port.name].signature)
        except Exception, e:
            raise

    def call_inputs(self, instance):
        # compute input methods and connections
        # We need to preserve the order of the inputs
        methods = self.is_method.values()
        methods.sort()
        methods_to_call = []
        for value in methods:
            (_, port) = value
            conn = self.is_method.inverse[value]
            p = conn()
            # Convert to correct port depth
            depth = conn.depth()
            while depth < self._get_input_spec(port).depth:
                p = [p]
                depth += 1
            methods_to_call.append([port, p])
        connections_to_call = []
        for (function, connector_list) in self.inputPorts.iteritems():
            paramList = self.force_get_input_list(function)
            for p,connector in izip(paramList, connector_list):
                # Don't call method
                if connector in self.is_method:
                    continue
                depth = connector.depth()
                while depth < connector.spec.depth:
                    p = [p]
                    depth += 1
                connections_to_call.append([function, p])
        # Compute methods from visible ports last
        #In the case of a vtkRenderer,
        # we need to call the methods after the
        #input ports are set.
        if self._module_spec.methods_last:
            to_call = connections_to_call + methods_to_call
        else:
            to_call = methods_to_call + connections_to_call
        for port_name, params in to_call:
            port = self._get_input_spec(port_name)
            # Call method once for each item in depth1 lists
            if port.depth == 0:
                params = [params]
            for ps in params:
                self.call_set_method(instance, port, ps)

    def call_outputs(self, instance):
        outputs_list = self.output_specs_order
        if 'self' in outputs_list:
            outputs_list.remove('self')
        if 'Instance' in outputs_list:
            outputs_list.remove('Instance')
        for port_name in outputs_list:
            if not port_name in self.outputPorts:
                # not connected
                continue
            port = self._get_output_spec(port_name)
            result = self.call_get_method(instance, port)
            self.set_output(port_name, result)

    def compute(self):
        spec = self._module_spec
        # First create the instance
        # TODO: How to handle parameters to instance
        instance = getattr(self._lib, spec.code_ref)()

        # Optional callback used for progress reporting
        if spec.callback:
            def callback(c):
                self.logging.update_progress(self, c)
            getattr(instance, spec.callback)(callback)
        # Optional function for creating temporary files
        if spec.tempfile:
            getattr(instance, spec.tempfile)(self.interpreter.filePool.create_file)

        # call input methods on instance
        self.call_inputs(instance)

        # optional compute method
        if spec.compute:
            getattr(instance, spec.compute)()

        # convert outputs to dict
        outputs = {}
        outputs_list = self.output_specs_order
        outputs_list.remove('self') # self is automatically set by base Module

        # Get outputs
        self.call_outputs(instance)

        self.set_output('Instance', instance)

        # optional cleanup method
        if spec.cleanup:
            getattr(instance, spec.cleanup)()


def gen_class_module(spec, lib, klasses, **module_settings):
    """Create a module from a python class specification

    Parameters
    ----------
    spec : ClassSpec
        A class to module specification
    """
    module_settings.update(spec.get_module_settings())
    _settings = ModuleSettings(**module_settings)

    # convert input/output specs into VT port objects
    input_ports = [CIPort(ispec.name, ispec.get_port_type(), **ispec.get_port_attrs())
                   for ispec in spec.input_port_specs]
    output_ports = [COPort(ospec.name, ospec.get_port_type(), **ospec.get_port_attrs())
                    for ospec in spec.output_port_specs]
    output_ports.insert(0, COPort('Instance', spec.module_name)) # Adds instance output port

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
         '_output_spec_table': _output_spec_table,
         '_module_spec': spec,
         'is_cacheable': lambda self:spec.cacheable,
         '_lib': lib}

    superklass = klasses.get(spec.superklass, BaseClassModule)
    new_klass = type(str(spec.module_name), (superklass,), d)
    klasses[spec.module_name] = new_klass
    return new_klass
