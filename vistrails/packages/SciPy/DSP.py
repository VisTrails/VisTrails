import modules
import modules.module_registry
from modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import *
from scipy import sparse, fft

#################################################################

class DSP(SciPy):
    def compute(self):
        pass

class FFT(DSP):
    def compute(self):
        mat = self.getInputFromPort("Signals")
        pts = self.getInputFromPort("FFT Samples")
        phasors = fft.fft(mat.matrix.data, pts)
        outmat = sparse.csc_matrix(phasors)
        out = SparseMatrix(outmat)
        self.setResult("FFT Output", out)
