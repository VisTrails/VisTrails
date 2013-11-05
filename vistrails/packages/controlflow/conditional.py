###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
##  - Neither the name of the University of Utah nor the names of its 
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
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.basic_modules import NotCacheable

#################################################################################
## If Operator

class If(Module, NotCacheable):
    """
    Return one of two values depending on a boolean condition.

    Note that the modules upstream of the port that is not chosen won't get
    executed (short-circuit).
    """

    def update(self):
        self.logging.begin_update(self)
        self.updateUpstream(
                self.condition_ready,
                [self.getInputConnector('Condition')])

    def condition_ready(self, connectors):
        if self.suspended:
            self.done()
            return

        if self.getInputFromPort('Condition'):
            mod_port_name = 'TruePort'
            self.__ports_port_name = 'TrueOutputPorts'
        else:
            mod_port_name = 'FalsePort'
            self.__ports_port_name = 'FalseOutputPorts'
        self.updateUpstream(
                self.input_ready,
                [self.getInputConnector(mod_port_name)],
                priority=50)
        # This module does nothing, it just forwards the value we get from
        # upstream, so we might as well give it a higher priority

    def input_ready(self, connectors):
        self.done()
        self.logging.begin_compute(self)
        module, = connectors
        module = module.obj
        if self.hasInputFromPort(self.__ports_port_name):
            output_ports = self.getInputFromPort(self.__ports_port_name)
            result = []
            for output_port in output_ports:
                result.append(module.get_output(output_port))
            if len(output_ports) == 1:
                self.setResult('Result', result[0])
            else:
                self.setResult('Result', result)
        self.upToDate = True
        self.logging.end_update(self)
        self.logging.signalSuccess(self)

#################################################################################
## Default module

class Default(Module, NotCacheable):
    """
    The Default module allows the user to provide a default value.

    This module can be put in the middle of a connection to provide a default
    value from the Default port in case nothing is set on the Input port. This
    is particularly useful when using subworkflows, with InputPort modules with
    optional set to True.

    Note that if a value is set on the Input port, the modules upstream of the
    Default port won't be executed (short-circuit).
    """

    def updateUpstream(self, callback=None, priority=None):
        try:
            self.__connector = self.getInputConnector('Input')
        except ModuleError:
            self.__connector = self.getInputConnector('Default')

        super(Default, self).updateUpstream(
                callback,
                [self.__connector],
                priority)

    def compute(self):
        self.setResult('Result', self.__connector())


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
