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
from core.modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import Matrix

class MatrixInfo(SciPy):

    def getString(self, m):
        numrows = m.rows()
        numcols = m.cols()
        numel = m.numElements()
        maxel = m.maxNumElements()

        out = "Matrix Info:\n\tNumber of Rows:  " + str(numrows) + \
              "\n\tNumber of Columns:  " + str(numcols) + \
              "\n\tNumber of Elements:  " + str(numel) + \
              "\n\tMaximum Number of Elements for compressed matrix:  " + \
              str(maxel)

        return out

    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        self.setResult("output", self.getString(m))
