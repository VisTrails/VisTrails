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
from Matrix import *
import math
import scipy

class MatrixOperation(SciPy):
    def compute(self):
        pass

class GetReals(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        self.setResult("OutputMatrix", m.Reals())

class GetImaginaries(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        self.setResult("OutputMatrix", m.Imaginaries())

class Conjugate(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        self.setResult("OutputMatrix", m.Conjugate())

class GetRow(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        c = self.get_input("RowIndex")
        row = m.GetRow(c)
        mat = SparseMatrix()
        mat.matrix = row
        self.setResult("OutputMatrix", mat)

class GetCol(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        c = self.get_input("ColIndex")
        col = m.GetCol(c)
        mat = SparseMatrix()
        mat.matrix = col
        self.setResult("OutputMatrix", mat)

class MatrixMultiply(MatrixOperation):
    def compute(self):
        a = self.get_input("InputMatrix1")
        b = self.get_input("InputMatrix2")
        c = a.matrix * b.matrix
        out = SparseMatrix()
        out.matrix = c
        return out

class ScalarMultiply(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        s = self.get_input("Scalar")
        m.matrix = m.matrix * s
        self.setResult("OutputMatrix", m)

class ElementMultiply(MatrixOperation):
    def compute(self):
        from numpy import array
        a = self.get_input("InputMatrix1")
        b = self.get_input("InputMatrix2")
        if a.matrix.shape != b.matrix.shape:
            raise ModuleError(self, 'Mismatching input dimensions!')
        c = SparseMatrix()
        c.matrix = sparse.csc_matrix(array(a.matrix.toarray())*array(b.matrix.toarray()))
        self.setResult("OutputMatrix", c)

class Transpose(MatrixOperation):
    def compute(self):
        m = self.get_input("InputMatrix")
        m.matrix = m.matrix.transpose()
        self.setResult("OutputMatrix", m)
 
class PrintMatrix(Matrix):
    def compute(self):
        m = self.get_input("InputMatrix")
        s = m.matrix.__str__()
        self.setResult("Output", s)

class GetColumnRange(Matrix):
    def compute(self):
        m = self.get_input("InputMatrix")
        start = self.get_input("StartIndex")
        end = self.get_input("EndIndex")
        size = end - start
        out = SparseMatrix()
        out.matrix = sparse.csc_matrix((m.matrix.shape[0], size))

        i = 0
        j = 0
        while j < m.matrix.shape[0]:
            while i < size:
                val = m.matrix[j,start+i]
                out.matrix[j,i] = val
                i = i + 1
            j = j + 1
        
        self.setResult("Output", out)
        
class ATan2(MatrixOperation):
    def compute(self):
        if self.has_input("InputMatrix"):
            m = self.get_input("InputMatrix")
            r = m.Reals().matrix
            im = m.Imaginaries().matrix
        else:
            r = self.get_input("RealMatrix").matrix
            im = self.get_input("ImaginaryMatrix").matrix

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(scipy.arctan2(im.toarray(),r.toarray()))
        self.setResult("Output", out)
