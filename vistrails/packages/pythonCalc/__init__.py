import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

################################################################################

class PythonCalc(Module):
    
    def __init__(self):
        Module.__init__(self)
        
    def compute(self):
#         print "Inside PythonCalc.compute()"
#         print "Will get input value1"
        v1 = self.getInputFromPort("value1")
#         print "input value1 =",v1
#         print "Will get input value2"
        v2 = self.getInputFromPort("value2")
#         print "input value1 =",v2
        self.setResult("value", self.op(v1, v2))

    def op(self, v1, v2):
        op = self.getInputFromPort("op")
#         print "op:",op
#         print "v1:",v2
#         print "v2:",v2
        if op == '+':
            return v1 + v2
        elif op == '-':
            return v1 - v2
        elif op == '*':
            return v1 * v2
        elif op == '/':
            return v1 / v2
        raise ModuleError("unrecognized operation: '%s'" % op)

################################################################################

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    reg.addModule(PythonCalc)
    reg.addInputPort(PythonCalc, "value1", (core.modules.basic_modules.Float, 'the first argument'))
    reg.addInputPort(PythonCalc, "value2", (core.modules.basic_modules.Float, 'the second argument'))
    reg.addInputPort(PythonCalc, "op", (core.modules.basic_modules.String, 'the operation'))
    reg.addOutputPort(PythonCalc, "value", (core.modules.basic_modules.Float, 'the result'))

