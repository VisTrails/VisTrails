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

import copy

from vistrails.core.modules.vistrails_module import Module, InvalidOutput, \
    ModuleError

#################################################################################
## If Operator

class If(Module):
    """
    The If Module alows the user to choose the part of the workflow to be
    executed through the use of a condition.
    """

    def update_upstream(self):
        """A modified version of the update_upstream method."""

        # everything is the same except that we don't update anything
        # upstream of TruePort or FalsePort
        excluded_ports = set(['TruePort', 'FalsePort', 'TrueOutputPorts',
                              'FalseOutputPorts'])
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name not in excluded_ports:
                for connector in connector_list:
                    connector.obj.update()
        for port_name, connectorList in copy.copy(self.inputPorts.items()):
            if port_name not in excluded_ports:
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput:
                        self.remove_input_connector(port_name, connector)

    def compute(self):
        """ The compute method for the If module."""

        if not self.has_input('Condition'):
            raise ModuleError(self, 'Must set condition')
        cond = self.get_input('Condition')

        if cond:
            port_name = 'TruePort'
            output_ports_name = 'TrueOutputPorts'
        else:
            port_name = 'FalsePort'
            output_ports_name = 'FalseOutputPorts'

        if self.has_input(output_ports_name):
            for connector in self.inputPorts.get(output_ports_name):
                connector.obj.update()

        if not self.has_input(port_name):
            raise ModuleError(self, 'Must set ' + port_name)

        for connector in self.inputPorts.get(port_name):
            connector.obj.update()

            if self.has_input(output_ports_name):
                output_ports = self.get_input(output_ports_name)
                result = []
                for output_port in output_ports:
                    result.append(connector.obj.get_output(output_port))

                # FIXME can we just make this a list?
                if len(output_ports) == 1:
                    self.set_output('Result', result[0])
                else:
                    self.set_output('Result', result)

#################################################################################
## Default module

class Default(Module):
    """
    The Default module allows the user to provide a default value.

    This module can be put in the middle of a connection to provide a default
    value from the Default port in case nothing is set on the Input port. This
    is particularly useful when using subworkflows, with InputPort modules with
    optional set to True.
    """

    def compute(self):
        if self.has_input('Input'):
            self.set_output('Result', self.get_input('Input'))
        else:
            self.set_output('Result', self.get_input('Default'))


###############################################################################

import unittest
import urllib2

from vistrails.tests.utils import intercept_result, execute

class TestIf(unittest.TestCase):
    def do_if(self, val):
        with intercept_result(If, 'Result') as results:
            interp_dict = execute([
                    ('If', 'org.vistrails.vistrails.control_flow', [
                        ('FalseOutputPorts', [('List', "['value']")]),
                        ('TrueOutputPorts', [('List', "['value']")]),
                        ('Condition', [('Boolean', str(val))]),
                    ]),
                    ('Integer', 'org.vistrails.vistrails.basic', [
                        ('value', [('Integer', '42')]),
                    ]),
                    ('Integer', 'org.vistrails.vistrails.basic', [
                        ('value', [('Integer', '28')]),
                    ]),
                ],
                [
                    (1, 'self', 0, 'TruePort'),
                    (2, 'self', 0, 'FalsePort'),
                ],
                full_results=True)
            self.assertFalse(interp_dict.errors)
        if val:
            self.assertEqual(results, [42])
        else:
            self.assertEqual(results, [28])
        self.assertEqual(interp_dict.executed, {0: True, 1: val, 2: not val})

    def test_if_true(self):
        self.do_if(True)

    def test_if_false(self):
        self.do_if(False)


class TestDefault(unittest.TestCase):
    def do_default(self, val):
        if val:
            src = 'o = 42'
        else:
            src = ('from vistrails.core.modules.vistrails_module import '
                   'InvalidOutput\n'
                   'o = InvalidOutput')
        src = urllib2.quote(src)
        with intercept_result(Default, 'Result') as results:
            self.assertFalse(execute([
                    ('Default', 'org.vistrails.vistrails.control_flow', [
                        ('Default', [('Integer', '28')]),
                    ]),
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', src)]),
                    ]),
                ],
                [
                    (1, 'o', 0, 'Input'),
                ],
                add_port_specs=[
                    (1, 'output', 'o',
                     'org.vistrails.vistrails.basic:Integer'),
                ]))
        if val:
            self.assertEqual(results, [42])
        else:
            self.assertEqual(results, [28])

    def test_default_set(self):
        self.do_default(True)

    def test_default_unset(self):
        self.do_default(False)
