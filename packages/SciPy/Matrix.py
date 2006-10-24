import modules
import modules.module_registry
from modules.vistrails_module import Module, ModuleError
from SciPy import SciPy

from numpy import allclose, arange, eye, linalg, ones
from scipy import linsolve, sparse

#######################################################################
class Matrix(SciPy):

    def __init__(self, mat):
        self.matrix=mat

    def __str__(self):
        return self.matrix.__str__()

    def setSize(self, size):
        pass

    def setMatrix(self, m):
        self.matrix = m

    def numElements(self):
        return self.matrix.getnnz()

    def maxNumElements(self):
        return self.matrix.nzmax

    def rows(self):
        return self.matrix.shape[0]

    def cols(self):
        return self.matrix.shape[1]

    def Reals(self):
        return SparseMatrix(self.matrix.real)

    def Imaginaries(self):
        return SparseMatrix(self.matrix.imag)
 
    def Conjugate(self):
        return SparseMatrix(self.matrix.conjugate())

    def GetRow(self, i):
        return self.matrix.getrow(i)

    def GetCol(self, i):
        return self.matrix.getcol(i)

class SparseMatrix(Matrix):

    def __init__(self, mat):
        self.matrix=mat

    def setSize(self, size):
        self.matrix = sparse.csc_matrix((size, size))
        self.matrix.setdiag(ones(size))

class DenseMatrix(Matrix):
    def __init__(self, mat):
        self.matrix = mat

    def setSize(self, size):
        self.matrix = sparse.csc_matrix((size, size))
        self.matrix.setdiag(ones(size))
        self.matrix.todense()
    

class DOKMatrix(Matrix):
    
    def __init__(self, mat):
        self.matrix=mat

    def setSize(self, size):
        self.matrix = sparse.dok_matrix((size, size))
        self.matrix.setdiag(ones(size))

class COOMatrix(Matrix):
    
    def __init__(self, mat):
        self.matrix=mat

    def setSize(self, size):
        self.matrix = sparse.coo_matrix((size, size))
        self.matrix.setdiag(ones(size))

class CSRMatrix(Matrix):
    
    def __init__(self, mat):
        self.matrix=mat

    def setSize(self, size):
        self.matrix = sparse.csr_matrix((size, size))
        self.matrix.setdiag(ones(size))

class LILMatrix(Matrix):
    
    def __init__(self, mat):
        self.matrix=mat

    def setSize(self, size):
        self.matrix = sparse.lil_matrix((size, size))
        self.matrix.setdiag(ones(size))

#######################################################################
