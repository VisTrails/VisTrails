import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

import scipy
import numpy
from scipy import sparse

from Array import *

class MatrixModule(object):
    my_namespace = 'scipy|matrix'

class MatrixOp(object):
    my_namespace = 'scipy|matrix|operation'

class Matrix(MatrixModule, Module):
    """ Container class for the scipy.sparse.csc_matrix class """
    def __init__(self):
        Module.__init__(self)
        self.matrix = None

    def get_shape(self):
        return self.matrix.shape

    def get_conjugate(self):
        return self.matrix.conjugate()

    def get_column(self, colId):
        return self.matrix.getcol(colId)

    def get_row(self, rowId):
        return self.matrix.getrow(rowId)

    def set_diagonal(self, vals):
        self.matrix.setdiag(vals)

    def toarray(self):
        return self.matrix.toarray()

    def transpose(self):
        return self.matrix.transpose()

    def get_num_elements(self):
        return self.matrix.getnnz()

    def get_max_elements(self):
        return self.matrix.nzmax

    def get_reals(self):
        return self.matrix._real()

    def get_imaginaries(self):
        return self.matrix._imag()

    def get_matrix(self):
        return self.matrix

    def set_matrix(self, mat):
        self.matrix = mat

class MatrixMultiply(MatrixOp, Module):
    """ Multiply two matrices together """
    def compute(self):
        a = self.get_input("Matrix1")
        b = self.get_input("Matrix2")
        out = Matrix()
        out.set_matrix(a.get_matrix() * b.get_matrix())

        self.setResult("Matrix Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Matrix1", (Matrix, 'Input Matrix 1'))
        reg.add_input_port(cls, "Matrix2", (Matrix, 'Input Matrix 2'))
        reg.add_output_port(cls, "Matrix Output", (Matrix, 'Output Matrix'))

class MatrixConjugate(MatrixOp, Module):
    """ Get the complex conjugate of the input matrix. """
    def compute(self):
        a = self.get_input("Matrix")
        b = a.get_conjugate().copy()
        out = Matrix()
        out.set_matrix(b)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Matrix", (Matrix, 'Input Matrix'))
        reg.add_output_port(cls, "Output", (Matrix, 'Output Matrix'))

class MatrixToArray(MatrixOp, Module):
    """ Convert a SciPy matrix to a Numpy Array """
    def compute(self):
        m = self.get_input("Matrix")
        a = m.toarray()
        out = NDArray()
        out.set_array(a)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Matrix", (Matrix, 'Input Matrix'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
