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

import importlib

from itertools import izip

from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.config import CIPort, COPort, ModuleSettings

from .common import convert_port, get_input_spec, get_output_spec


class BaseClassModule(Module):
    """ Wraps a python class as a vistrails Module using a ClassSpec
        setter methods are used as inputs and getter methods as outputs

    """
    _settings = ModuleSettings(abstract=True)

    _get_input_spec = classmethod(get_input_spec)
    _get_output_spec = classmethod(get_output_spec)

    def call_set_method(self, instance, port, params, method_results):
        # convert params
        # convert values to vistrail types
        params = convert_port(port, params, self._translations['input'])
        if len(self.input_specs[port.name].signature) > 1:
            params = list(params)
        else:
            params = [params]
        method_name = port.arg
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
        method = getattr(instance, method_name)
        try:
            result = method(*(prepend_params + params))
            # store result for output methods
            method_results[port.arg] = result
        except Exception, e:
            raise

    def call_get_method(self, instance, port):
        method = getattr(instance, port.arg)
        try:
            value = method(*(port.get_prepend_params()))
            # convert params
            return convert_port(port, value, self._translations['output'])
        except Exception, e:
            raise

    def call_inputs(self, instance, method_results):
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
            # skip non-methods
            if port.method_type in ['Instance', 'argument', 'attribute']:
                continue
            # Call method once for each item in depth1 lists
            if port.depth == 0:
                params = [params]
            for ps in params:
                self.call_set_method(instance, port, ps, method_results)

    def call_outputs(self, instance, method_results):
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
            if port.method_type == 'method':
                if port.arg in method_results:
                    result = method_results[port.arg]
                else:
                    result = self.call_get_method(instance, port)
                self.set_output(port_name, result)

    def get_parameters(self):
        """
        Compute constructor/function arguments
        """
        args = []
        kwargs = {}
        ops = []
        for port_name in self.inputPorts:
            port = self._get_input_spec(port_name)
            if port and port.method_type == 'argument':
                params = self.get_input(port_name)
                params = convert_port(port, params,
                                      self._translations['input'])

                if -1 == port.arg_pos:
                    kwargs[port.arg] = params
                elif -2 == port.arg_pos:
                    args = params
                elif -3 == port.arg_pos:
                    kwargs.update(params)
                elif -5 == port.arg_pos:
                    if params:
                        ops.extend(params)
                else:
                    # make room for arg
                    while len(args) <= port.arg_pos:
                        args.append(None)
                    args[port.arg_pos] = params
        return args, kwargs, ops

    def set_attributes(self, instance):
        """
        set class attributes
        """
        for port_name in self.inputPorts:
            port = self._get_input_spec(port_name)
            if port and port.method_type == 'attribute':
                params = self.get_input(port_name)
                params = convert_port(port, params,
                                      self._translations['input'])
                setattr(instance, port.arg, params)

    def get_attributes(self, instance):
        """
        set class attributes
        """
        for port_name in self.outputPorts:
            port = self._get_output_spec(port_name)
            if port and port.method_type == 'attribute':
                value = getattr(instance, port.arg)
                value = convert_port(port, value, self._translations['output'])
                self.set_output(port_name, value)

    def compute(self):
        spec = self._module_spec
        if self.has_input('Instance'):
            instance = self.get_input('Instance')
        else:
            # Handle parameters to instance
            args, kwargs, ops = self.get_parameters()
            # create the instance
            if not kwargs:
                # some constructors fail if passed empty kwarg
                if not args:
                    instance = self._class[0]()
                else:
                    instance = self._class[0](*args)
            else:
               instance = self._class[0](*args, **kwargs)

        # Optional callback used for progress reporting
        if spec.callback:
            def callback(c):
                self.logging.update_progress(self, c)
            getattr(instance, spec.callback)(callback)
        # Optional function for creating temporary files
        if spec.tempfile:
            getattr(instance, spec.tempfile)(self.interpreter.filePool.create_file)

        # set input attributes on instance
        self.set_attributes(instance)

        # input methods can transfer results to outputs
        method_results = {}
        # call input methods on instance
        self.call_inputs(instance, method_results)

        # optional compute method
        if spec.compute:
            getattr(instance, spec.compute)()

        # apply operations
        for op, op_args, op_kwargs in ops:
            if '.' in op:
                # Run as a function with obj as first argument
                # TODO: Support obj on other position and as kwarg
                m, c, n = op.rsplit('.', 2)
                function = getattr(getattr(importlib.import_module(m), c), n)
                op_args[0] = instance
            else:
                # it is a class method
                function = getattr(instance, op)
            try:
                print op, op_args, op_kwargs
                result = function(*op_args, **op_kwargs)
            except Exception, e:
                raise ModuleError(self, e.message)


        # get output attributes from instance
        self.get_attributes(instance)

        # convert outputs to dict
        outputs_list = self.output_specs_order
        outputs_list.remove('self') # self is automatically set by base Module

        # Get outputs
        self.call_outputs(instance, method_results)

        self.set_output('Instance', instance)

        # optional cleanup method
        if spec.cleanup:
            getattr(instance, spec.cleanup)()


def gen_class_module(spec, lib=None, modules=None, translations={},
                     operations={}, **module_settings):
    """Create a module from a python class specification

    Parameters
    ----------
    spec : ClassSpec
        A class to module specification
    module : pythonmodule
        The module to load classes from
    modules : dict of name:module
    operations : supported operation dict of {name: type}
    """
    if modules is None:
        modules = {}
    module_settings.update(spec.get_module_settings())
    _settings = ModuleSettings(**module_settings)

    # convert input/output specs into VT port objects
    input_ports = []
    for ispec in spec.all_input_port_specs():
        input_ports.append(CIPort(ispec.name, ispec.get_port_type(),
                                  **ispec.get_port_attrs()))
    output_ports = [COPort(ospec.name, ospec.get_port_type(),
                           **ospec.get_port_attrs())
                    for ospec in spec.output_port_specs]
    # Instance input is used to access an already existing Instance
    i_name = (spec.namespace + '|' if spec.namespace else '') + spec.module_name
    if 'Instance' not in [o.name for o in output_ports]:
        output_ports.insert(0, COPort('Instance', i_name,
            docstring='The class instance'))

    _input_spec_table = {}
    for ps in spec.all_input_port_specs():
        _input_spec_table[ps.name] = ps
    _output_spec_table = {}
    for ps in spec.output_port_specs:
        _output_spec_table[ps.name] = ps

    if '.' in spec.code_ref:
        # full paths are imported directly
        m, c = spec.code_ref.rsplit('.', 1)
        _class = getattr(importlib.import_module(m), c)
    else:
        _class = getattr(lib, spec.code_ref)

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
         '_translations': translations,
         '_class': [_class]} # Avoid attaching it to the class

    superklass = modules.get(spec.superklass, BaseClassModule)
    new_klass = type(str(spec.module_name), (superklass,), d)
    modules[spec.module_name] = new_klass
    return new_klass

_modules = [BaseClassModule]
