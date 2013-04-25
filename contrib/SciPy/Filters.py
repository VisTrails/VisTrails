import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import *
import scipy
import scipy.signal
from scipy import sparse, fftpack
import numpy

class DSPFilters(SciPy):
    def compute(self):
        pass

class HanningWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.hanning(size))
        self.setResult("Window", out)

class TriangularWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.triang(size))
        self.setResult("Window", out)

class BlackmanWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.blackman(size))
        self.setResult("Window", out)

class BlackmanHarrisWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.blackmanharris(size))
        self.setResult("Window", out)

class ParzenWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.parzen(size))
        self.setResult("Window", out)

class HammingWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.hamming(size))
        self.setResult("Window", out)

class KaiserWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")
        beta = self.getInputFromPort("Beta")
        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.kaiser(size, beta))
        self.setResult("Window", out)

class BartlettHannWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.barthann(size))
        self.setResult("Window", out)

class GaussianWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")
        sigma = self.getInputFromPort("Sigma")
        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.gaussian(size, sigma))
        self.setResult("Window", out)

class BoxcarWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.boxcar(size))
        self.setResult("Window", out)

class BohmanWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.bohman(size))
        self.setResult("Window", out)

class BartlettWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.bartlett(size))
        self.setResult("Window", out)

class NuttallBlackmanHarrisWindow(DSPFilters):
    def compute(self):
        size = self.getInputFromPort("Window Size")

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.signal.nuttall(size))
        self.setResult("Window", out)

