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
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import *
from scipy import sparse, fftpack
import numpy

#################################################################

class DSP(SciPy):
    def compute(self):
        pass

class FFT(DSP):
    def compute(self):
        mat = self.getInputFromPort("Signals")
        pts = self.getInputFromPort("FFT Samples")

        phasors = fftpack.fft(mat.matrix.data, pts)
        outmat = sparse.csc_matrix(phasors)
        out = SparseMatrix()
        out.matrix = outmat
        self.setResult("FFT Output", out)

class FFT2(DSP):
    def compute(self):
        mat = self.getInputFromPort("Signals")

        phasors = fftpack.fftn(mat.matrix.data)
        outmat = sparse.csc_matrix(phasors)
        out = SparseMatrix()
        out.matrix = outmat
        self.setResult("FFT Output", out)

class WindowedFourierTransform(DSP):
    def compute(self):
        mat = self.getInputFromPort("Signal")
        
        sr = self.getInputFromPort("Sampling Rate")
        if self.hasInputFromPort("Window Size"):
            window = self.getInputFromPort("Window Size")
        else:
            window = sr

        if self.hasInputFromPort("Stride"):
            stride = self.getInputFromPort("Stride")
        else:
            stride = int(sr / 2)

        
        signal_array = mat.matrix.toarray().ravel()

        # We now have a 1-D array that we can have good indexing into
        pad = signal_array[0:int(window/2)]
        signal_array = numpy.concatenate((pad,signal_array))
        win_low = 0
        win_hi = window - 1
        phasors = fftpack.fft(signal_array[win_low:win_hi])
        out_array = phasors.ravel()

        win_low += stride
        win_hi += stride

        while win_hi < signal_array.shape[0]:
            phasors = fftpack.fft(signal_array[win_low:win_hi])
            win_low += stride
            win_hi += stride
            out_array = numpy.vstack([out_array, phasors.ravel()])

        out = SparseMatrix()
        out.matrix = sparse.csc_matrix(out_array)
        self.setResult("FFT Output", out)
