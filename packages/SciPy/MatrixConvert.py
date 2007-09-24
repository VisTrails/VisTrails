############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import core.modules
from core.modules.vistrails_module import Module, ModuleError
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

class vtkDataSetToMatrix(SciPy):
    ''' In some cases, particularly in terms of user-defined VTK Filters, the
        output of the filter is a vtk datatype representing '''
    
    def from_unstructured_grid(self, vtkalgout):
        import vtk
        prod = vtkalgout.vtkInstance.GetProducer()
        prod.Update()
        grid = prod.GetOutput()
        pt_set = grid.GetPoints()
        scalars = grid.GetPointData().GetScalars()

        ''' Points in vtk are always 3D... so we must assume this. '''
        self.matrix_ = SparseMatrix()
        self.matrix_.matrix = sparse.csc_matrix((grid.GetNumberOfPoints(), 3))

        i = 0
        while i < grid.GetNumberOfPoints():
            (x,y,z) = pt_set.GetPoint(i)
            self.matrix_.matrix[i,0] = x
            self.matrix_.matrix[i,1] = y
            self.matrix_.matrix[i,2] = z
            print x, y, z
            i += 1
            
        
    def compute(self):
        if self.hasInputFromPort("vtkUnstructuredGrid"):
            self.from_unstructured_grid(self.getInputFromPort("vtkUnstructuredGrid"))
        else:
            pass

        self.setResult("Output Matrix", self.matrix_)
