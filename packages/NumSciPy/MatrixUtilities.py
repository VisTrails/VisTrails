from core.modules.vistrails_module import Module, ModuleError
from Matrix import *

import scipy
from scipy import io, sparse


class ArrayUtilityModule(object):
    my_namespace = 'scipy|matrix|utilities|Matlab'

class MatlabReader(ArrayUtilityModule, Module):
    """ Read a Matlab .mat file into a SciPy matrix """
    def compute(self):
        if self.hasInputFromPort("Filename"):
            fname = self.getInputFromPort("Filename")
        else:
            fname = self.getInputFromPort("File").name

        m = io.loadmat(fname, None, 0)
        vals = m.values()
        for t in vals:
            if type(t) == numpy.ndarray:
                mat = t

        out = Matrix()
        out.set_matrix(sparse.csc_matrix(mat))

        self.setResult("Matrix Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "File", (basic.File, 'File'))
        reg.add_output_port(cls, "Matrix Output", (Matrix, 'Matrix Output'))
    
