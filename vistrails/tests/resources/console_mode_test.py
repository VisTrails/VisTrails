###############################################################################
##
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

"""Testing package for console_mode"""

##############################################################################

import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.modules.basic_modules import Float, Integer

identifier = 'edu.utah.sci.vistrails.console_mode_test'
version = '0.9.0'
name = 'Console Mode Tests'

class TestTupleExecution(Module):

    def compute(self):
        v1, v2 = self.getInputFromPort('input')
        self.setResult('output', v1 + v2)


class TestDynamicModuleError(Module):

    def compute(self):
        c = TestDynamicModuleError()
        c.die()

    def die(self):
        raise ModuleError(self, "I died!")

class TestChangeVistrail(NotCacheable, Module):

    def compute(self):
        if self.hasInputFromPort('foo'):
            v1 = self.getInputFromPort('foo')
        else:
            v1 = 0
        if v1 != 12:
            self.change_parameter('foo', v1 + 1)

class TestCustomNamed(Module):

    pass


class TestOptionalPorts(Module):

    pass

##############################################################################

def initialize():
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(TestTupleExecution)
    reg.add_input_port(TestTupleExecution, 'input', [Float, Float])
    reg.add_output_port(TestTupleExecution, 'output', (Float, 'output'))
    reg.add_module(TestDynamicModuleError)
    reg.add_module(TestChangeVistrail)
    reg.add_input_port(TestChangeVistrail, 'foo', Integer)

    reg.add_module(TestCustomNamed, name='different name')
    reg.add_input_port(TestCustomNamed, 'input', Float)

    reg.add_module(TestOptionalPorts)
    reg.add_input_port(TestOptionalPorts, 'foo', Float, optional=True)
    reg.add_output_port(TestOptionalPorts, 'foo', Float, optional=True)

