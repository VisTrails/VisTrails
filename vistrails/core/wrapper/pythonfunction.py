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

import importlib

from vistrails.core.modules.config import CIPort, COPort, ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError
from .common import convert_port

IN_KWARG = -1
ARGV = -2
KWARG = -3
SELF = -4
OPERATION = -5


def gen_function_module(spec, lib=None, klasses=None, translations={},
                        **module_settings):
    """Create a module from a python function specification

    Parameters
    ----------
    spec : FunctionSpec
        A function specification
    lib : python module
         optional library module
    klasses : dict
         superclasses
    translations : dict
         port translations {signature: function}
    module_settings : InstanceObject
         module settings
    """
    if klasses is None:
        klasses = {}

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

    def compute(self):
        # read inputs, convert, and translate to args
        args = []
        kwargs = {}
        instance = None
        ops = []
        for port in spec.all_input_port_specs():
            if self.has_input(port.name):
                value = self.get_input(port.name)
                value = convert_port(port, value, self._translations['input'])
                if IN_KWARG == port.arg_pos:
                    kwargs[port.arg] = value
                elif ARGV == port.arg_pos:
                    args = value
                elif KWARG == port.arg_pos:
                    kwargs.update(value)
                elif SELF == port.arg_pos:
                    instance = value
                elif OPERATION == port.arg_pos:
                    ops.extend(value)
                else:
                    # make room for arg
                    while len(args) <= port.arg_pos:
                        args.append(None)
                    args[port.arg_pos] = value

        if 'operation' == spec.method_type:
            # Set module info on self output and quit
            # FIXME: using spec.name assumes same package
            # FIXME: serialize kwargs?
            # NOTE: tempfile/callback not supported on operations
            info = (spec.code_ref, args, kwargs)
            ops.append(info)
            for name in self.output_specs_order: # there is only one
                self.set_output(name, ops)
            return

        # Optional temp file
        if spec.tempfile:
            kwargs[spec.tempfile] = self.file_pool.create_file

        # Optional callback used for progress reporting
        if spec.callback:
            def callback(c):
                self.logging.update_progress(self, c)
            kwargs[spec.callback] = callback

        if 'method' == spec.method_type:
            if instance:
                function = getattr(instance, spec.code_ref)
            elif '.' in spec.code_ref:
                # DEPRECATED: Set SELF as arg_pos and use instance
                # full paths are imported directly
                m, c, n = spec.code_ref.rsplit('.', 2)
                function = getattr(getattr(importlib.import_module(m), c), n)
        elif 'function' == spec.method_type:
            if '.' in spec.code_ref:
                # full paths are imported directly
                m, f = spec.code_ref.rsplit('.', 1)
                function = getattr(importlib.import_module(m), f)
            else:
                function = getattr(lib, spec.code_ref)


        try:
            print args, kwargs
            result = function(*args, **kwargs)
        except Exception, e:
            raise ModuleError(self, e.message)

        # convert outputs to dict
        outputs = {}
        outputs_list = self.output_specs_order
        outputs_list.remove('self') # self is automatically set by base Module

        if spec.output_type is None or spec.output_type == 'object':
            # single object
            if 'operation' != spec.method_type:
                # apply operations
                # the function must return a class instance for this to work
                for op, op_args, op_kwargs in ops:
                    if '.' in op:
                        # Run as a function with obj as first argument
                        # TODO: Support result on other position and as kwarg
                        m, c, n = op.rsplit('.', 2)
                        function = getattr(getattr(importlib.import_module(m), c), n)
                        op_args[0] = result
                    else:
                        # it is a class method
                        function = getattr(result, op)
                    try:
                        print op, op_args, op_kwargs
                        function(*op_args, **op_kwargs)
                    except Exception, e:
                        raise ModuleError(self, e.message)
            for name in self.output_specs_order:
                outputs[name] = result
        elif spec.output_type == 'list':
            for name, value in zip(self.output_specs_order, result):
                outputs[name] = value
        elif spec.output_type == 'dict':
            # translate from args to names
            t = dict([(self._get_output_spec(s.name).arg, s.name)
                      for s in spec.output_port_specs])
            outputs = dict([(t[arg], value)
                            for arg, value in result.iteritems()])
        elif spec.output_type == 'self':
            # return instance
            for name in self.output_specs_order:
                outputs[name] = instance
        # convert values to vistrail types
        for port in spec.output_port_specs:
            name = port.name
            if name in outputs and outputs[name] is not None:
                outputs[name] = convert_port(port,
                                             outputs[name],
                                             self._translations['output'])
        # set outputs
        for key, value in outputs.iteritems():
            self.set_output(key, value)

    d = {'compute': compute,
         '__module__': __name__,
         '_settings': _settings,
         '__doc__': spec.docstring,
         '__name__': spec.name or spec.module_name,
         'is_cacheable': lambda self:spec.cacheable,
         '_input_ports': input_ports,
         '_output_ports': output_ports,
         '_translations': translations}

    superklass = klasses.get(spec.superklass, Module) if klasses else Module
    new_klass = type(str(spec.module_name), (superklass,), d)
    klasses[spec.module_name] = new_klass
    return new_klass