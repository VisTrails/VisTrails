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
from vistrails.core.scripting import Script, Prelude
from .common import convert_port, convert_port_script, python_name, unique_name

IN_KWARG = -1
ARGV = -2
KWARG = -3
SELF = -4
OPERATION = -5


def gen_function_module(spec, lib=None, klasses=None, patches={}, translations={},
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
                value = convert_port(port, value, self._patches, self._translations, 'input')
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
                                             self._patches,
                                             self._translations,
                                             'output')
        # set outputs
        for key, value in outputs.iteritems():
            self.set_output(key, value)

    def to_python_script(cls, module):
        """ Create a script from the module specification
        """
        code = []
        preludes = []

        def strip_preludes(script):
            no_preludes = []
            for s in script.split('\n'):
                if s.startswith('import ') or s.startswith('from '):
                    preludes.append(Prelude(s))
                else:
                    no_preludes.append(s)
            return '\n'.join(no_preludes)

        input_map = {}
        output_map = {}

        used_inputs = set(module.connected_input_ports)
        used_inputs.update(set([f.name for f in module.functions]))
        used_outputs = set(module.connected_output_ports)

        # read inputs, convert, and translate to args
        # list of arg variables or string
        args = []
        # dict of kwarg variables, or comma-separated string
        kwargs = {}
        # it may be necessary to create kwargs variable
        def kwargs_string():
            kwarg_string = ', '.join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])
            _, kwargs = unique_name('kwargs', input_map)
            code.append('%s = dict(%s)' % (kwargs, kwarg_string))
        def add_kwarg(key, value):
            if isinstance(kwargs, basestring):
                code.append('%s[%s] = %s' % (kwargs, key, value))
            else:
                kwargs[key] = value
        def add_kwargs(varname):
            if not isinstance(kwargs, basestring):
                kwargs_string()
            code.append('%s.update(%s)' % (kwargs, varname))

        instance = None
        ops = []
        print "all specs", [p.name for p in spec.all_input_port_specs()]
        for port in spec.all_input_port_specs():
            if port.name in used_inputs:
                input_map[port.name] = python_name(port.name, input_map)
                value = convert_port_script(code, port, input_map[port.name],
                                            cls._patches, cls._translations,
                                            'input')
                print "do input", port.name, value
                if IN_KWARG == port.arg_pos:
                    add_kwarg(port.arg, value)
                elif ARGV == port.arg_pos:
                    args = value
                elif KWARG == port.arg_pos:
                    add_kwargs(value)
                elif SELF == port.arg_pos:
                    instance = value
                elif OPERATION == port.arg_pos:
                    ops.append(value)
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

            if not args:
                args = '[]'
            elif not isinstance(args, basestring):
                args = '[' + ', '.join(args) + ']'
            if not kwargs:
                kwargs = '{}'
            elif not isinstance(kwargs, basestring):
                kwargs = 'dict(' + ', '.join(['%s=%s' % (key, value)
                                          for key, value in kwargs.iteritems()]) + ')'
            ops.append("[('%s', %s, %s)]" % (spec.code_ref, args, kwargs))

            for name in used_outputs:
                name = python_name(name, output_map)
                code.append('%s = %s' % (name, ' + '.join(ops)))
            code = '\n'.join(code)
            return Script(code, input_map, output_map), preludes

        # Optional function for creating temporary files
        if spec.tempfile:
            #getattr(instance, spec.tempfile)(self.interpreter.filePool.create_file)
            preludes.append(Prelude('import tempfile'))
            code.append(strip_preludes(cls.call_patched_script(instance,
                                                               spec.tempfile,
                                                               ['tempfile.mkstemp'])))
            add_kwarg(spec.tempfile, spec.tempfile)

        if 'method' == spec.method_type:
            function = '%s.%s' % (instance, spec.code_ref)
        elif 'function' == spec.method_type:
            # full paths are imported directly
            m, f = spec.code_ref.rsplit('.', 1)
            preludes.append(Prelude('import ' + m))
            function = spec.code_ref

        arg_list = []
        if args:
            if isinstance(args, basestring):
                arg_list.append('*' + args)
            else:
                arg_list.append(', '.join(args))
        if kwargs:
            if isinstance(kwargs, basestring):
                arg_list.append('*' + args)
            else:
                arg_list.append(', '.join(['%s=%s' % (key, value)
                                           for key, value in kwargs.iteritems()]))

        function_call = "%s(%s)" % (function, ', '.join(arg_list))

        outputs_list = [p.name for p in module.sourcePorts() if p.name in used_outputs]

        print "out_)type", spec.output_type
        result_var = unique_name('result', output_map)
        # compute shape of output
        if spec.output_type is None or spec.output_type == 'object':
            # single object
            print "outputs_list", outputs_list, used_outputs
            for name in outputs_list:
                instance = python_name(name, output_map)
                function_call = '%s = %s' % (instance, function_call)
        elif spec.output_type == 'list':
            for name in outputs_list:
                python_name(name, output_map)
            function_call = '%s = %s' % (', '.join([output_map[name] for name in outputs_list]),
                                         function_call)
        elif spec.output_type == 'dict':
            # translate from args to names
            function_call = '%s = %s' % (result_var, function_call)
            for name in outputs_list:
                python_name(name, output_map)
                for ispec in spec.all_input_port_specs():
                    if ispec.name == name:
                        arg = ispec.arg
                function_call += '\n%s = %s.%s' % (output_map[name], result_var, arg)
        elif spec.output_type == 'self':
            # return result as only output
            for name in outputs_list:
                instance = python_name(name, output_map)
                function_call = '%s = %s' % (instance, function_call)
        elif ops:
            instance = result_var
            function_call = '%s = %s' % (result_var, function_call)

        code.append(function_call)

        # apply operations
        # the function must return a class instance for this to work
        op_name = unique_name('op', output_map)
        op_args_name = unique_name('op_args', output_map)
        op_kwargs_name = unique_name('op_kwargs', output_map)
        m_name = unique_name('m', output_map)
        c_name = unique_name('c', output_map)
        n_name = unique_name('n', output_map)
        function_name = unique_name('function', output_map)
        for op in ops:
            preludes.append(Prelude('import importlib'))
            code.append('for %s, %s, %s in %s:' % (op_name, op_args_name, op_kwargs_name, op))
            code.append("    if '.' in %s:" % op_name)
            # Run as a function with obj as first argument
            code.append("        %s, %s, %s = %s.rsplit('.', 2)" % (m_name, c_name, n_name, op_name))
            code.append("        %s = getattr(getattr(importlib.import_module(%s), %s), %s)" % (function_name, m_name, c_name, n_name))
            code.append("        %s[0] = %s" % (op_args_name, instance))
            code.append("    else:")
            # it is a class method
            code.append("        %s = getattr(%s, %s)" % (function_name, instance, op_name))
            code.append("    %s(*%s, **%s)" % (function_name, op_args_name, op_kwargs_name))

        # convert values to vistrail types
        for port in spec.output_port_specs:
            name = port.name
            if name in used_outputs:
                print "outcon", spec.module_name, name, used_outputs
                output_map[name] = python_name(name, output_map)
                convert_port_script(code,
                                    port,
                                    output_map[name],
                                    cls._patches,
                                    cls._translations,
                                   'output')

        code = '\n'.join(code)
        return Script(code, input_map, output_map), preludes


    d = {'compute': compute,
         'to_python_script': classmethod(to_python_script),
         '__module__': __name__,
         '_settings': _settings,
         '__doc__': spec.docstring,
         '__name__': spec.name or spec.module_name,
         'is_cacheable': lambda self:spec.cacheable,
         '_input_ports': input_ports,
         '_output_ports': output_ports,
         '_patches': patches,
         '_translations': translations}

    superklass = klasses.get(spec.superklass, Module) if klasses else Module
    new_klass = type(str(spec.module_name), (superklass,), d)
    klasses[spec.module_name] = new_klass
    return new_klass