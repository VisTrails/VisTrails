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
import scipy
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

class ShortTimeFourierTransform(DSP):
    def get_signal(self, sigs, window, offset, size):
        win = scipy.zeros(sigs.shape[0]).ravel()
        win[offset:offset+size] = window.ravel()
        part = sigs * win
        return part
    
    def compute(self):
        mat = self.getInputFromPort("Signal")
        sr = self.getInputFromPort("Sampling Rate")

        if self.hasInputFromPort("Window"):
            window = self.getInputFromPort("Window").matrix.toarray()
            win_size = window.shape[1]
        else:
            win_size = self.getInputFromPort("WindowSize")
            window = scipy.signal.hamming(win_size)

        if self.hasInputFromPort("Stride"):
            stride = self.getInputFromPort("Stride")
        else:
            stride = int(win_size / 2)

        signal_array = mat.matrix.transpose().toarray().ravel()

        samples = signal_array.shape[0]

        offset = 0
        sig = self.get_signal(signal_array, window, offset, win_size)
        phasors = fftpack.fft(sig).ravel()
        out_array = phasors
        offset += stride

        i = 1
        while 1:
            try:
                sig = self.get_signal(signal_array, window, offset, win_size)
                phasors = fftpack.fft(sig)
                offset += stride
                out_array = numpy.vstack([out_array, phasors.ravel()])
                i += 1
            except:
                break

        (slices, freqs) = out_array.shape
        ar = out_array[0:,0:sr*2]
        ar = ar[0:,::-1]

        out = SparseMatrix()
        sigout = SparseMatrix()
        sigout.matrix = sparse.csc_matrix(signal_array)
        out.matrix = sparse.csc_matrix(ar)
        self.setResult("Signal Output", sigout)
        self.setResult("FFT Output", out)
