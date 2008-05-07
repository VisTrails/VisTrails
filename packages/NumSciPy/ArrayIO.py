import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import numpy
from Array import *
from Matrix import *

class ArrayIOModule(object):
    my_namespace = 'numpy|io'

class ReadPNG(ArrayIOModule, Module):
    """ Load a .png type image into a Numpy Array. """
    def compute(self):
        import pylab
        fn = self.getInputFromPort("Filename")
        ar = pylab.imread(fn)
        out = NDArray()
        out.set_array(ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

        
