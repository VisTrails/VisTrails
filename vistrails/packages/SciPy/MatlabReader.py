import modules
import modules.module_registry
from modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import *
from scipy import io, sparse

#######################################################################

class MatlabReader(SciPy):

    def compute(self):
        fname = self.getInputFromPort("Filename")
        self.readFileAsCSC(fname)
   
    def readFileAsCSC(self, filename):
        m = io.loadmat(filename, None, 0)
        vals = m.values()
        mat = vals[2]
        cscmat = sparse.csr_matrix(mat)
        self.matrix = SparseMatrix(cscmat)
        self.setResult("sparseoutput", self.matrix)
