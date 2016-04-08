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

from base64 import b16encode, b16decode
import copy
from itertools import izip
import time

from vistrails.core.modules.basic_modules import create_constant
from vistrails.core.modules.vistrails_module import Module, InvalidOutput, \
    ModuleError, ModuleConnector, ModuleSuspended, ModuleWasSuspended
from vistrails.core.utils import xor, long2bytes

try:
    import hashlib
    sha1_hash = hashlib.sha1
except ImportError:
    import sha
    sha1_hash = sha.new


class While(Module):
    """
    The While Module runs a module over and over until the condition port
    is false. Then, it returns the result.
    """

    def update_upstream(self):
        """A modified version of the update_upstream method."""

        # everything is the same except that we don't update the module on
        # FunctionPort
        suspended = []
        was_suspended = None
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name == 'FunctionPort':
                for connector in connector_list:
                    try:
                        connector.obj.update_upstream()
                    except ModuleWasSuspended, e:
                        was_suspended = e
                    except ModuleSuspended, e:
                        suspended.append(e)
            else:
                for connector in connector_list:
                    try:
                        connector.obj.update()
                    except ModuleWasSuspended, e:
                        was_suspended = e
                    except ModuleSuspended, e:
                        suspended.append(e)
        if len(suspended) == 1:
            raise suspended[0]
        elif suspended:
            raise ModuleSuspended(
                    self,
                    "multiple suspended upstream modules",
                    children=suspended)
        elif was_suspended is not None:
            raise was_suspended
        for port_name, connectorList in list(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput: # pragma: no cover
                        self.remove_input_connector(port_name, connector)

    def compute(self):
        name_output = self.get_input('OutputPort')
        name_condition = self.force_get_input('ConditionPort')
        name_state_input = self.force_get_input('StateInputPorts')
        name_state_output = self.force_get_input('StateOutputPorts')
        max_iterations = self.get_input('MaxIterations')
        delay = self.force_get_input('Delay')

        if (name_condition is None and
                not self.has_input('MaxIterations')):
            raise ModuleError(self,
                              "Please set MaxIterations or use ConditionPort")

        if name_state_input or name_state_output:
            if not name_state_input or not name_state_output:
                raise ModuleError(self,
                                  "Passing state between iterations requires "
                                  "BOTH StateInputPorts and StateOutputPorts "
                                  "to be set")
            if len(name_state_input) != len(name_state_output):
                raise ModuleError(self,
                                  "StateInputPorts and StateOutputPorts need "
                                  "to have the same number of ports "
                                  "(got %d and %d)" % (len(name_state_input),
                                                       len(name_state_output)))

        connectors = self.inputPorts.get('FunctionPort')
        if len(connectors) != 1:
            raise ModuleError(self,
                              "Multiple modules connected on FunctionPort")
        module = copy.copy(connectors[0].obj)

        state = None

        loop = self.logging.begin_loop_execution(self, max_iterations)
        for i in xrange(max_iterations):
            if not self.upToDate:
                module.upToDate = False
                module.computed = False

                # Set state on input ports
                if i > 0 and name_state_input:
                    for value, input_port, output_port \
                    in izip(state, name_state_input, name_state_output):
                        if input_port in module.inputPorts:
                            del module.inputPorts[input_port]
                        new_connector = ModuleConnector(
                                           create_constant(value), 'value',
                                           module.output_specs.get(output_port, None))
                        module.set_input_port(input_port, new_connector)
                        # Affix a fake signature on the module
                        inputPort_hash = sha1_hash()
                        inputPort_hash.update(input_port)
                        module.signature = b16encode(xor(
                                b16decode(self.signature.upper()),
                                inputPort_hash.digest()))

            loop.begin_iteration(module, i)

            module.update() # might raise ModuleError, ModuleSuspended,
                            # ModuleHadError, ModuleWasSuspended

            loop.end_iteration(module)

            if name_condition is not None:
                if name_condition not in module.outputPorts:
                    raise ModuleError(
                            module,
                            "Invalid output port: %s" % name_condition)
                if not module.get_output(name_condition):
                    break

            if delay and i+1 != max_iterations:
                time.sleep(delay)

            # Get state on output ports
            if name_state_output:
                state = [module.get_output(port) for port in name_state_output]

            self.logging.update_progress(self, i * 1.0 / max_iterations)

        loop.end_loop_execution()

        if name_output not in module.outputPorts:
            raise ModuleError(module,
                              "Invalid output port: %s" % name_output)
        result = module.get_output(name_output)
        self.set_output('Result', result)

class For(Module):
    """
    The For Module runs a module with input from a range.
    """

    def update_upstream(self):
        """A modified version of the update_upstream method."""

        # everything is the same except that we don't update the module on
        # FunctionPort
        suspended = []
        was_suspended = None
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name == 'FunctionPort':
                for connector in connector_list:
                    try:
                        connector.obj.update_upstream()
                    except ModuleWasSuspended, e:
                        was_suspended = e
                    except ModuleSuspended, e:
                        suspended.append(e)
            else:
                for connector in connector_list:
                    try:
                        connector.obj.update()
                    except ModuleWasSuspended, e:
                        was_suspended = e
                    except ModuleSuspended, e:
                        suspended.append(e)
        if len(suspended) == 1:
            raise suspended[0]
        elif suspended:
            raise ModuleSuspended(
                    self,
                    "multiple suspended upstream modules",
                    children=suspended)
        elif was_suspended is not None:
            raise was_suspended
        for port_name, connectorList in list(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput: # pragma: no cover
                        self.removeInputConnector(port_name, connector)

    def compute(self):
        name_output = self.get_input('OutputPort') # or 'self'
        name_input = self.force_get_input('InputPort') # or None
        lower_bound = self.get_input('LowerBound') # or 0
        higher_bound = self.get_input('HigherBound') # required

        connectors = self.inputPorts.get('FunctionPort')
        if len(connectors) != 1:
            raise ModuleError(self,
                              "Multiple modules connected on FunctionPort")

        outputs = []
        suspended = []
        loop = self.logging.begin_loop_execution(self,
                                                 higher_bound - lower_bound)
        for i in xrange(lower_bound, higher_bound):
            module = copy.copy(connectors[0].obj)

            if not self.upToDate:
                module.upToDate = False
                module.computed = False

                # Pass iteration number on input port
                if name_input is not None:
                    if name_input in module.inputPorts:
                        del module.inputPorts[name_input]
                    new_connector = ModuleConnector(create_constant(i),
                                                    'value')
                    module.set_input_port(name_input, new_connector)
                    # Affix a fake signature on the module
                    inputPort_hash = sha1_hash()
                    inputPort_hash.update(name_input)
                    module.signature = b16encode(xor(
                            b16decode(self.signature.upper()),
                            long2bytes(i, 20),
                            inputPort_hash.digest()))

            loop.begin_iteration(module, i)

            try:
                module.update()
            except ModuleSuspended, e:
                suspended.append(e)
                loop.end_iteration(module)
                continue

            loop.end_iteration(module)

            if name_output not in module.outputPorts:
                raise ModuleError(module,
                                  "Invalid output port: %s" % name_output)
            outputs.append(module.get_output(name_output))

        if suspended:
            raise ModuleSuspended(
                    self,
                    "function module suspended in %d/%d iterations" % (
                            len(suspended), higher_bound - lower_bound),
                        children=suspended)
        loop.end_loop_execution()

        self.set_output('Result', outputs)

###############################################################################

import unittest

class TestWhile(unittest.TestCase):
    def test_pythonsource(self):
        import urllib2
        source = ('o = i * 2\n'
                  "r = \"it's %d!!!\" % o\n"
                  'go_on = o < 100')
        source = urllib2.quote(source)
        from vistrails.tests.utils import execute, intercept_result
        with intercept_result(While, 'Result') as results:
            self.assertFalse(execute([
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', source)]),
                        ('i', [('Integer', '5')]),
                    ]),
                    ('While', 'org.vistrails.vistrails.control_flow', [
                        ('ConditionPort', [('String', 'go_on')]),
                        ('OutputPort', [('String', 'r')]),
                        ('StateInputPorts', [('List', "['i']")]),
                        ('StateOutputPorts', [('List', "['o']")]),
                    ]),
                ],
                [
                    (0, 'self', 1, 'FunctionPort'),
                ],
                add_port_specs=[
                    (0, 'input', 'i',
                     'org.vistrails.vistrails.basic:Integer'),
                    (0, 'output', 'o',
                     'org.vistrails.vistrails.basic:Integer'),
                    (0, 'output', 'r',
                     'org.vistrails.vistrails.basic:String'),
                    (0, 'output', 'go_on',
                     'org.vistrails.vistrails.basic:Boolean'),
                ]))
        self.assertEqual(results, ["it's 160!!!"])
