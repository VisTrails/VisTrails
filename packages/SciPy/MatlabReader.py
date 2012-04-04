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
from scipy import io, sparse
import numpy

#######################################################################

class MatlabReader(SciPy):

    def compute(self):
        if self.hasInputFromPort("Filename"):
            fname = self.getInputFromPort("Filename")
        else:
            fname = self.getInputFromPort("File").name
        self.readFileAsCSC(fname)
   
    def readFileAsCSC(self, filename):
        m = io.loadmat(filename, None, 0)
        vals = m.values()
        for t in vals:
            if type(t) == numpy.ndarray:
                mat = t

        cscmat = sparse.csr_matrix(mat)
        self.matrix = SparseMatrix()
        self.matrix.matrix = cscmat
        self.setResult("sparseoutput", self.matrix)
