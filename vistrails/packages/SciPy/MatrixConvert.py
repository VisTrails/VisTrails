import modules
from modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import Matrix, COOMatrix, SparseMatrix, CSRMatrix
from scipy import sparse

class MatrixConvert(SciPy):

    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        to = self.getInputFromPort("OutputType")

        to = to.upper()
        if to == 'Dense':
            self.matrix = DenseMatrix(m.matrix.todense())
            self.setResult("SparseOutput", self.matrix)
        else:
            self.matrix = SparseMatrix(m.matrix.tocsc())
            self.setResult("SparseOutput", self.matrix)

