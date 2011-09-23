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
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from SciPy import SciPy

from numpy import allclose, arange, eye, linalg, ones
from scipy import linsolve, sparse

#######################################################################
class Matrix(SciPy):

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
        out = SparseMatrix()
        tmp = self.matrix.copy()
        out.matrix = tmp._real()
        return out

    def Imaginaries(self):
        out = SparseMatrix()
        tmp = self.matrix.copy()
        out.matrix = tmp._imag()
        return out
 
    def Conjugate(self):
        out = SparseMatrix()
        out.matrix = self.matrix.conjugate().copy()
        return out

    def GetRow(self, i):
        return self.matrix.getrow(i)

    def GetCol(self, i):
        return self.matrix.getcol(i)

class SparseMatrix(Matrix):

    def setSize(self, size):
        self.matrix = sparse.csc_matrix((size, size))
        self.matrix.setdiag(ones(size))

class DenseMatrix(Matrix):

    def setSize(self, size):
        self.matrix = sparse.csc_matrix((size, size))
        self.matrix.setdiag(ones(size))
        self.matrix.todense()
    

class DOKMatrix(Matrix):

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
