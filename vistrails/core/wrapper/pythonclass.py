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
from __future__ import division, absolute_import

import ast
import importlib
import re

from itertools import izip
from string import Template

from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.config import CIPort, COPort, ModuleSettings
from vistrails.core.scripting import Script, Prelude

METHOD_TYPES = ['method', 'nullary', 'OnOff', 'SetXToY']

from .common import convert_port, convert_port_script, get_input_spec, get_output_spec, get_patches


class BaseClassModule(Module):
    """ Wraps a python class as a vistrails Module using a ClassSpec
        setter methods are used as inputs and getter methods as outputs

    """
    _settings = ModuleSettings(abstract=True)

    _get_input_spec = classmethod(get_input_spec)
    _get_output_spec = classmethod(get_output_spec)

    def call_patched(self, instance, method_name, params, patches=None):
        """ call method using existing patches

            it builds a patched script recursively and execute it at top level

            supported patch tempalte variables
            $self - instance
            $original - original call or inner patch
            $input - first input
            $inputs - all inputs as list
            $output - sets the output
        """
        if patches is None:
            # top level
            # FIXME: CHECK superclasses!
            patches = get_patches(type(self), method_name)
            script = self.call_patched(instance, method_name, params, patches)
            output = None
            locals_ = locals()
            exec script + '\n' in locals_, locals_
            if locals_.get('output') is not None:
                output = locals_['output']
            return output
        if len(patches) == 0:
            # original call
            return 'output = instance.%s(*params)' % method_name
        patch_name = patches.pop()
        patch = self._patches[patch_name].strip()
        template = Template(patch)
        # get attributes in patch
        vars = set([i[1] for i in Template.pattern.findall(patch)])
        d = {}
        if 'original' in vars:
            # get inner patches
            rest = self.call_patched(instance, method_name, params, patches)
            d['original'] = rest
            vars.remove('original')
        # add attributes to patch
        if 'self' in vars:
            d['self'] = 'instance'
            vars.remove('self')
        if 'input' in vars:
            d['input'] = 'params[0]'
            vars.remove('input')
        if 'inputs' in vars:
            d['inputs'] = 'params'
            vars.remove('inputs')
        if 'output' in vars:
            d['output'] = 'output'
            vars.remove('output')
        if vars:
            raise Exception('Unknown variables in patch: %s' % vars)
        # return final patch
        return template.safe_substitute(d)

    def call_set_method(self, instance, port, params, method_results):
        # convert params
        # convert values to vistrail types
        params = convert_port(port, params, self._translations['input'])
        if ',' in port.port_type:
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
        try:
            result = self.call_patched(instance, method_name, prepend_params + params)
            # store result for output methods
            method_results[port.arg] = result
        except Exception, e:
            raise

    def call_get_method(self, instance, port):
        try:
            value = self.call_patched(instance, port.arg, port.get_prepend_params())
            # convert params
            return convert_port(port, value, self._patches, 'output')
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
                                      self._patches, 'input')

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
                                      self._patches, 'input')
                setattr(instance, port.arg, params)

    def get_attributes(self, instance):
        """
        set class attributes
        """
        for port_name in self.outputPorts:
            port = self._get_output_spec(port_name)
            if port and port.method_type == 'attribute':
                value = getattr(instance, port.arg)
                value = convert_port(port, value, self._patches, 'output')
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

        # optional initialize method
        if spec.initialize:
            self.call_patched(instance, spec.initialize, [])
        # Optional callback used for progress reporting
        if spec.callback:
            def callback(c):
                self.logging.update_progress(self, c)
            self.call_patched(instance, spec.callback, [callback])
        # Optional function for creating temporary files
        if spec.tempfile:
            self.call_patched(instance, spec.tempfile, [self.interpreter.filePool.create_file])

        # set input attributes on instance
        self.set_attributes(instance)

        # input methods can transfer results to outputs
        method_results = {}
        # call input methods on instance
        self.call_inputs(instance, method_results)

        # optional compute method
        if spec.compute:
            self.call_patched(instance, spec.compute, [])

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
                result = function(*op_args, **op_kwargs)
            except Exception, e:
                raise ModuleError(self, e.message)


        # get output attributes from instance
        self.get_attributes(instance)

        # convert outputs to dict
        outputs_list = self.output_specs_order
        if 'self' in outputs_list:
            outputs_list.remove('self') # self is automatically set by base Module

        # Get outputs
        self.call_outputs(instance, method_results)

        self.set_output('Instance', instance)

        # optional cleanup method
        if spec.cleanup:
#            getattr(instance, spec.cleanup)()
            self.call_patched(instance, spec.cleanup, [])


    ################ SCRIPT METHODS ############################

    @classmethod
    def convert_value_or_translate_script(cls, module, code, port, value):
        """ convert value and return it. If the translated value is not
            serializable the translation code will be written out instead.

        """
        # First try to get the translated value directly
        was_simplified = False
        value0 = value
        try:
            final_value = convert_port(port, value0, cls._translations['input'])
            # Test: If it can be reversed, it is serializable.
            reversed_value = ast.literal_eval(repr(final_value))
            if reversed_value == final_value:
                value = final_value
                was_simplified = True
        except Exception, e:
            pass
        if not was_simplified:
            # Add translation code
            port_name = port.name
            # Make sure port.name is not aready used as an input port
            if port_name in module.connected_input_ports:
                i = 0
                new_name = port_name + '_0'
                while new_name in module.connected_input_ports:
                    i += 1
                    new_name = '%s_%s' % (port_name, i)
                port_name = new_name
            code.append('%s = %s' % (port_name, repr(value0)))
            convert_port_script(code, port, port.name, cls._translations, 'input')
            value = port_name
        return value


    @classmethod
    def call_set_connection_methods_script(cls, module, code, instance,
                                           method_results):
        """ Write code for methods on input connections

            Connections are already joined and available as {port.name}

        """
        for port_name in module.connected_input_ports:
            port = cls._get_input_spec(port_name)
            if port.method_type not in METHOD_TYPES:
                continue
            if port.depth == 1:
                # Need to loop the list of functions on each port
                # There is no way to know how many functions are on a port
                # FIXME: "{port.name}Item" may not be unique
                loop_name = port.name + 'Item'
                code.append('for %s in %s:' % (loop_name, port.name))
            else: # depth == 0
                loop_name = port.name
            loop_code = []
            if (len(module.input_specs[port_name].signature) == 1 and
                port.get_port_type() in cls._translations['input']):
                # convert all values to vistrail types
                convert_port_script(loop_code, port, loop_name,
                                    cls._translations, 'input')

            if port.method_type == 'OnOff':
                # This converts OnOff ports to XOn(), XOff() calls
                #method_name = method_name + ('On' if params[0] else 'Off')
                #params = []
                loop_code.append('if %s:' % loop_name)
                loop_code.append('    %s.%sOn()' % (instance, port.arg))
                loop_code.append('else:')
                loop_code.append('    %s.%sOff()' % (instance, port.arg))

            elif port.method_type == 'nullary':
                # Call X() only if boolean is true
                #if params[0]:
                #    params = []
                #else:
                #    return
                loop_code.append('if %s:' % port.name)
                loop_code.append('    %s.%s()' % (instance, port.arg))
            elif port.method_type == 'SetXToY':
                # Append enum name to function name and delete params
                #method_name += params[0]
                #params = []
                # We could also check all enums, but that is equally ugly
                loop_code.append("getattr(%s, '%s' + %s)()" % (instance,
                                                               port.arg,
                                                               port.name))
            else:

                star = '*' if len(module.input_specs[port.name].signature) != 1 else ''
                prepend_params = [repr(p) for p in port.get_prepend_params()]
                if prepend_params:
                    prepend_params = ', '.join(prepend_params) + ', '
                else:
                    prepend_params = ''
                parameters = prepend_params + star + loop_name

                set_output = ''
                if (port.name in module.connected_output_ports and
                    cls._get_output_spec(port_name).method_type == 'method'):
                    set_output = '%s =' % port.name
                    method_results[port.arg] = port.name

                loop_code.append("%s%s.%s(%s)" % (set_output, instance,
                                                  port.arg, parameters))
            if port.depth == 1:
                # indent loop_code
                code.extend(['    ' + line for line in loop_code])
            else:
                code.extend(loop_code)

    @classmethod
    def call_set_function_methods_script(cls, module, code, instance, method_results):
        """ Functions can be directly translated into method calls
        """
        for function in module.functions:
            port_name = function.name
            port = cls._get_input_spec(port_name)
            if port.method_type not in METHOD_TYPES:
                continue
            value = [p.value() for p in function.params]

            if (len(module.input_specs[port_name].signature) == 1 and
                port.get_port_type() in cls._translations['input']):
                # convert values to vistrail types
                value = [cls.convert_value_or_translate_script(module, code,
                                                             port, value[0])]

            if port.method_type == 'OnOff':
                # This converts OnOff ports to XOn(), XOff() calls
                #method_name = method_name + ('On' if params[0] else 'Off')
                #params = []
                if value[0]:
                    code.append('%s.%sOn()' % (instance, port.arg))
                else:
                    code.append('%s.%sOff()' % (instance, port.arg))

            elif port.method_type == 'nullary':
                # Call X() only if boolean is true
                #if params[0]:
                #    params = []
                #else:
                #    return
                if value[0]:
                    code.append('%s.%s()' % (instance, port.arg))
            elif port.method_type == 'SetXToY':
                # Append enum name to function name and delete params
                #method_name += params[0]
                #params = []
                code.append("%s.%s%s()" % (instance, port.arg, value[0]))
            else:
                params = ', '.join([repr(v) for v in value])
                prepend_params = [repr(p) for p in port.get_prepend_params()]
                if prepend_params:
                    params =  ', '.join(prepend_params) + ', ' + params

                set_output = ''
                if (port.name in module.connected_output_ports and
                    cls._get_output_spec(port_name).method_type == 'method'):
                    set_output = '%s =' % port.name
                    method_results[port.arg] = port.name

                code.append("%s%s.%s(%s)" % (set_output, instance, port.arg,
                                              params))

    @classmethod
    def call_get_method_script(cls, module, code, instance, port):
        prepend_params = [repr(p) for p in port.get_prepend_params()]
        if prepend_params:
            prepend_params += ', '.join(prepend_params)
        else:
            prepend_params = ''
        code.append("%s = %s.%s(%s)" % (port.name, instance, port.arg,
                                      prepend_params))
        convert_port_script(code, port, port.name, cls._translations,
                            'output')

    @classmethod
    def call_inputs_script(cls, module, code, instance, method_results):
        # Compute methods from visible ports last.
        # In the case of a vtkRenderer, we need to call the
        # methods after the input ports are set.
        if cls._module_spec.methods_last:
            cls.call_set_connection_methods_script(module, code, instance,
                                                   method_results)
            cls.call_set_function_methods_script(module, code, instance,
                                                 method_results)
        else:
            cls.call_set_function_methods_script(module, code, instance,
                                                 method_results)
            cls.call_set_connection_methods_script(module, code, instance,
                                                   method_results)

    @classmethod
    def call_outputs_script(cls, module, code, instance, method_results):
        outputs_list = set(module.connected_output_ports)
        if 'self' in outputs_list:
            outputs_list.remove('self')
        if 'Instance' in outputs_list:
            outputs_list.remove('Instance')
        for port_name in outputs_list:
            if not port_name in module.connected_output_ports:
                # not connected
                continue
            port = cls._get_output_spec(port_name)
            if port.method_type == 'method':
                if port.arg in method_results:
                    # port variable already set
                    pass
                else:
                    cls.call_get_method_script(module, code, instance, port)

    @classmethod
    def get_parameters_script(cls, module, code):
        """
        Compute constructor/function arguments
        """

        # Set functions manually (to correct depth)
        arg_dict = {}

        # translate connections
        for port in module.connected_input_ports:
            pspec = cls._get_input_spec(port)
            if pspec.method_type != 'argument':
                continue
            convert_port_script(code, pspec, port, cls._translations, 'input')
            arg_dict[port] = port

        # Set functions manually (to correct depth)
        for function in module.functions:
            port = function.name
            pspec = cls._get_input_spec(port)
            if pspec.method_type == 'argument':
                if len(module.input_specs[port.name].signature) == 1:
                    value = repr(function.params[0].value())
                else:
                    # a tuple
                    value = repr(tuple([p.value() for p in function.params]))

                if (len(module.input_specs[port].signature) == 1 and
                    pspec.get_port_type() in cls._translations):
                    # convert values to vistrail types
                    value = cls.convert_value_or_translate_script(module,
                                                                  code,
                                                                  pspec,
                                                                  value)
                depth = - pspec.depth
                while depth:
                    depth += 1
                    value = '[%s]' % value
                arg_dict[port] = value

        args = []
        star_args = None
        kwargs = {}
        star_kwargs = []
        ops = []
        for port_name, arg_value in arg_dict.iteritems():
            port = cls._get_input_spec(port_name)
            #params = self.get_input(port_name)
            if -1 == port.arg_pos:
                kwargs[port.arg] = arg_value
            elif -2 == port.arg_pos:
                star_args = arg_value
            elif -3 == port.arg_pos:
                star_kwargs.append(arg_value)
            elif -5 == port.arg_pos:
                ops.extend(arg_value)
            else:
                # make room for arg
                while len(args) <= port.arg_pos:
                    args.append('None')
                args[port.arg_pos] = arg_value

        args = ', '.join(args)
        if star_args:
            if args:
                args += ', '
            args += '*' + star_args

        if kwargs:
            if star_kwargs:
                # need to explicitly create kwargs variable
                code.append('_kwargs = %s' % kwargs)
                for sk in star_kwargs:
                    code.append('_kwargs.update(%s)' % sk)
                kwargs = '_kwargs'
            else:
                kwargs = '%s' % kwargs
            args += ', **' + kwargs

        return args, ops

    @classmethod
    def set_attributes_script(cls, module, code, instance):
        """
        set class attributes
        """

        # Handle functions
        # Set functions manually (to correct depth)
        for function in module.functions:
            port = function.name
            pspec = cls._get_input_spec(port)
            if pspec.method_type == 'argument':
                if len(module.input_specs[port.name].signature) == 1:
                    value = repr(function.params[0].value())
                else:
                    # a tuple
                    value = repr(tuple([p.value() for p in function.params]))

                if (len(module.input_specs[port].signature) == 1 and
                    pspec.get_port_type() in cls._translations):
                    # convert values to vistrail types
                    value = cls.convert_value_or_translate_script(module,
                                                                  code,
                                                                  pspec,
                                                                  value)
                # FIXME: If depth > 1 we should merge all functions on each port
                depth = - pspec.depth
                while depth:
                    depth += 1
                    value = '[%s]' % value
                code.append('%s.%s = %s' % (instance, port.arg, value))

        # Handle connections
        for port_name in module.connected_input_ports:
            port = cls._get_input_spec(port_name)
            if port and port.method_type == 'attribute':
                convert_port_script(code, port, port.name,
                                    cls._translations, 'input')
                code.append('%s.%s = %s' % (instance, port.arg, port.name))

    @classmethod
    def get_attributes_script(cls, module, code, instance):
        """
        set class attributes
        """
        for port_name in module.connected_output_ports:
            port = cls._get_output_spec(port_name)
            if port and port.method_type == 'attribute':
                code.append('%s = %s.' % (port.name, instance, port.arg))
                convert_port_script(code, port, port.name, cls._translations,
                                    'output')

    @classmethod
    def to_python_script(cls, module):
        """ Create a script from the module specification
        """

        # functions are treated separately from connections because:
        # * functions are ordered by age
        #   - irrespective of port
        #   - Required by VTK
        #   - Used by iterating all function (lists) and using them in order
        # * connections are ordered by age on each port
        #   - Lists are joined into a single port item
        #   - Used by iterating the connected value (list) on each port
        #     and using them in order.
        #     * Functions have been removed from input


        #used_input_functions = [f.name for f in module.functions]
        code = []
        preludes = []
        spec = cls._module_spec
        module.input_specs = dict((p.name, p) for p in module.destinationPorts())

        # Set up the class instance
        if ('Instance' in module.connected_input_ports and
            cls._get_input_spec('Instance').method_type == 'Instance'):
            instance = 'Instance'
        else:
            # Handle parameters to instance
            # args will be used as {portname}
            # kwargs will be used as {arg}={portname}
            # ops are (methodname, args, kwargs)
            # And needs to be codified as getattr({nstance}, ops[0])(ops[1], ops[2])
            # FIXME: ops are ugly by default
            # It is tricky to write them as methods in the code
            args, ops = cls.get_parameters_script(module, code)
            # create the instance
            # Use code_ref:
            #   "vistrails.packages.vtk.vtk_wrapper.vtk.vtkActor"
            # Import as package name: (can easily change to "import vtk")
            #   "from vistrails.packages.vtk.vtk_wrapper import vtk"
            # Then create instance:
            #   "instance = vtk.vtkActor(my_param)"
            # What to do if code_ref is just module name?

            # We want the code_ref to be

            # for now just require full-path code_ref for exporting


            m, c = spec.code_ref.rsplit('.', 1)
            if '.' in m:
                path, m = m.rsplit('.', 1)
                preludes.append(Prelude("from %s import %s" % (path, m)))
            else:
                preludes.append(Prelude("import %s" % m))
            class_name = '%s.%s' % (m, c)

            # create a nice instance name
            instance = re.sub('(?!^)([A-Z]+)', r'_\1',c).lower()
            code.append("%s = %s(%s)" % (instance, class_name, args))
            #instance = module._class[0](*args, **kwargs)

        # Optional callback used for progress reporting
        if spec.callback:
            # no callback for scripts right now
            pass
        # Optional function for creating temporary files
        if spec.tempfile:
            # TODO: need to call mktmp directly from scripts
            #getattr(instance, spec.tempfile)(self.interpreter.filePool.create_file)
            pass
        # set input attributes on instance
        cls.set_attributes_script(module, code, instance)

        # input methods can transfer results to outputs
        method_results = {}
        # call input methods on instance
        cls.call_inputs_script(module, code, instance, method_results)

        # optional compute method
        if spec.compute:
            code.append("%s.%s()" % (instance, spec.compute))
            #getattr(instance, spec.compute)()

        # apply operations
        # need to add the whole calling code
        for op in ops:
            code.append('for op, op_args, op_kwargs in %s:' % op)
            code.append("    if '.' in op:")
            # Run as a function with obj as first argument
            # TODO: Support obj on other position and as kwarg
            code.append("        m, c, n = op.rsplit('.', 2)")
            code.append("        function = getattr(getattr(importlib.import_module(m), c), n)")
            code.append("        op_args[0] = %s" % instance)
            code.append("    else:")
            # it is a class method
            code.append("        function = getattr(%s, op)" % instance)
            code.append("    function(*op_args, **op_kwargs)")

        # get output attributes from instance
        cls.get_attributes_script(module, code, instance)

        # Get outputs
        cls.call_outputs_script(module, code, instance, method_results)

        # optional cleanup method
        if spec.cleanup:
            code.append("%s.%s()" % (instance, spec.cleanup))
            #getattr(instance, spec.cleanup)()

        inputs = dict((n, n) for n in module.connected_input_ports)
        outputs = dict((n, n) for n in module.connected_output_ports)
        if 'Instance' in inputs:
            inputs['Instance'] = instance
        if 'Instance' in outputs:
            outputs['Instance'] = instance

        # Set skip_functions, as we have used them directly
        # We cannot use "inputs" for this, since there may exist connections
        # for the same ports.
        code = '\n'.join(code)
        return (Script(code, inputs, outputs, skip_functions=True), preludes)


def gen_class_module(spec, lib=None, modules=None, patches={},
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
         '_patches': patches,
         '_class': [_class]} # Avoid attaching it to the class

    superklass = modules.get(spec.superklass, BaseClassModule)
    new_klass = type(str(spec.module_name), (superklass,), d)
    modules[spec.module_name] = new_klass
    return new_klass

_modules = [BaseClassModule]
