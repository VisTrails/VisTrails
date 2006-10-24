import modules
import modules.module_registry

from modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import *

class MatrixOperation(SciPy):
    def compute(self):
        pass

class GetReals(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        self.setResult("OutputMatrix", m.Reals())

class GetImaginaries(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        self.setResult("OutputMatrix", m.Imaginaries())

class Conjugate(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        self.setResult("OutputMatrix", m.Conjugate())

class GetRow(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        c = self.getInputFromPort("RowIndex")
        row = m.GetRow(c)
        mat = SparseMatrix(row)
        self.setResult("OutputMatrix", mat)

class GetCol(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        c = self.getInputFromPort("ColIndex")
        col = m.GetCol(c)
        mat = SparseMatrix(col)
        self.setResult("OutputMatrix", mat)

class MatrixMultiply(MatrixOperation):
    def compute(self):
        a = self.getInputFromPort("InputMatrix1")
        b = self.getInputFromPort("InputMatrix2")
        c = a.matrix * b.matrix
        out = SparseMatrix(c)
        return out

class ScalarMultiply(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        s = self.getInputFromPort("Scalar")
        m.matrix = m.matrix * s
        self.setResult("OutputMatrix", m)

class ElementMultiply(MatrixOperation):
    def compute(self):
        a = self.getInputFromPort("InputMatrix1")
        b = self.getInputFromPort("InputMatrix2")
        if a.matrix.shape != b.matrix.shape:
            raise ModuleError(self, 'Mismatching input dimensions!')

        i = 0
        j = 0
        while i < a.matrix.shape[0]:
            while j < a.matrix.shape[1]:
                a.matrix[i,j] = a.matrix[i,j] * b.matrix[i,j]
                j = j+1
            i = i+1

        self.setResult("OutputMatrix", a)

class Transpose(MatrixOperation):
    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        m.matrix = m.matrix.transpose()
        self.setResult("OutputMatrix", m)
 
