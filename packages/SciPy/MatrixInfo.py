import modules
from modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import Matrix

class MatrixInfo(SciPy):

    def getString(self, m):
        numrows = m.rows()
        numcols = m.cols()
        numel = m.numElements()
        maxel = m.maxNumElements()

        out = "Matrix Info:\n\tNumber of Rows:  " + str(numrows) + "\n\tNumber of Columns:  " + str(numcols) + "\n\tNumber of Elements:  " + str(numel) + "\n\tMaximum Number of Elements for compressed matrix:  " + str(maxel)

        return out

    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        self.setResult("output", self.getString(m))
