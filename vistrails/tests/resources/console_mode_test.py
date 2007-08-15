############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

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
    reg = core.modules.module_registry
    reg.addModule(TestTupleExecution)
    reg.addInputPort(TestTupleExecution, 'input', [Float, Float])
    reg.addOutputPort(TestTupleExecution, 'output', (Float, 'output'))
    reg.addModule(TestDynamicModuleError)
    reg.addModule(TestChangeVistrail)
    reg.addInputPort(TestChangeVistrail, 'foo', Integer)

    reg.addModule(TestCustomNamed, name='different name')
    reg.addInputPort(TestCustomNamed, 'input', Float)

    reg.addModule(TestOptionalPorts)
    reg.addInputPort(TestOptionalPorts, 'foo', Float, optional=True)
    reg.addOutputPort(TestOptionalPorts, 'foo', Float, optional=True)

