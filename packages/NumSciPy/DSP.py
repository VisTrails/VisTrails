import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from Matrix import *
from Array import *
import scipy
import scipy.signal
from scipy import fftpack
import numpy

class DSPModule(object):
    my_namespace = 'scipy|signals'

class FFT(DSPModule, Module):
    __doc__ = """ Calculate the discrete Fourier transform of the arbitrary
    sequence presented on the Signal port.  This is done using
    SciPy's FFTPack module.\n\n"""
    __doc__ += """From fftpack.fft:\n\t"""
    __doc__ += fftpack.fft.__doc__
    
    def compute(self):
        sig_array = self.getInputFromPort("Signals")

        # If there is no input on the samples port,
        # use the number of samples in an array row for
        # the number of fft points.
        if self.hasInputFromPort("Samples"):
            pts = self.getInputFromPort("Samples")
            
        else:
            pts = sig_array.get_shape()[1]

        sh = sig_array.get_shape()
        if len(sh) < 2:
            shp = (1, sh[0])
            sig_array.reshape(shp)

        (num_sigs, num_samps) = sig_array.get_shape()
        phasors = fftpack.fft(sig_array.get_row_range(0,0), pts)
        out_ar = phasors

        for i in xrange(1,num_sigs):
            phasors = fftpack.fft(sig_array.get_row_range(i,i), pts)
            out_ar = numpy.vstack([out_ar, phasors])
        
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("FFT Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Array'))
        reg.add_input_port(cls, "Samples", (basic.Integer, 'FFT Samples'))
        reg.add_output_port(cls, "FFT Output", (NDArray, 'FFT Output'))

class FFTN(DSPModule, Module):
    __doc__ = """ Calculate the discrete Fourier transform of the arbitrary
    sequence presented on the Signal port.  This is done using
    SciPy's FFTPack module.\n\n"""
    __doc__ += """From fftpack.fftn:\n\t"""
    __doc__ += fftpack.fftn.__doc__
    
    def compute(self):
        sig_array = self.getInputFromPort("Signals")
        # If there is no input on the samples port,
        # use the number of samples in an array row for
        # the number of fft points.
        if self.hasInputFromPort("Samples"):
            pts = self.getInputFromPort("Samples")
            
        else:
            pts = sig_array.get_shape()[1]

        sh = (sig_array.get_shape()[0], pts)

        phasors = fftpack.fftn(sig_array.get_array(), shape=sh)
        out = NDArray()
        out.set_array(phasors)
        self.setResult("FFT Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Array'))
        reg.add_input_port(cls, "Samples", (basic.Integer, 'FFT Samples'))
        reg.add_output_port(cls, "FFT Output", (NDArray, 'FFT Output'))

class ShortTimeFourierTransform(DSPModule, Module):
    """ Calculate the short time Fourier transform of the
    sequence presented on the Signal port.  This is done using
    SciPy's FFTPack fft module in conjuction with an input window.
    If a window is not specified, a Hamming window of the specified
    size is used. """
    def get_signal(self, sigs, window, offset, size):
        win = scipy.zeros(sigs.shape[0]).ravel()
        win[offset:offset+size] = window.ravel()
        part = sigs * win
        return part

    def compute(self):
        sigs = self.getInputFromPort("Signals")
        sr = self.getInputFromPort("SamplingRate")

        out_vol = None

        if self.hasInputFromPort("Window"):
            window = self.getInputFromPort("Window")
            win_size = window.get_shape()[0]
        else:
            win_size = self.getInputFromPort("WindowSize")
            window = scipy.signal.hamming(win_size)

        if self.hasInputFromPort("Stride"):
            stride = self.getInputFromPort("Stride")
        else:
            stride = int(win_size / 2)

        sh = sigs.get_shape()
        if len(sh) < 2:
            shp = (1, sh[0])
            sigs.reshape(shp)
        (num_sigs, num_samps) = sigs.get_shape()

        for i in xrange(num_sigs):
            offset = 0
            signal = sigs.get_row_range(i,i).ravel()

            #  We need to do the first window here so that we
            #  can have something to call vstack on.
            sig = self.get_signal(signal, window, offset, win_size)
            im_array = fftpack.fft(sig)
            offset += stride
            
            while 1:
                try:
                    sig = self.get_signal(signal, window, offset, win_size)
                    phasors = fftpack.fft(sig)
                    offset += stride
                    im_array = numpy.vstack([im_array, phasors.ravel()])
                except:
                    break

            #  STFT of one signal is done.  Clean up the output
            (slices, freqs) = im_array.shape
            ar = im_array[0:,0:sr*2]
            ar = ar[0:,::-1]

            if out_vol == None:
                out_vol = ar
                ovshape = out_vol.shape
                out_vol.shape = 1, ovshape[0], ovshape[1]
            else:
                arshape = ar.shape
                ar.shape = 1, arshape[0], arshape[1]
                out_vol = numpy.vstack([out_vol, ar])

        # All signals have been processed and are in the volume.
        out = NDArray()
        out.set_array(out_vol)
        self.setResult("FFT Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Signal Array'))
        reg.add_input_port(cls, "SamplingRate", (basic.Integer, 'Sampling Rate'))
        reg.add_input_port(cls, "Window", (NDArray, 'Windowing Function'))
        reg.add_input_port(cls, "Window Size", (basic.Integer, 'Window Size'))
        reg.add_input_port(cls, "Stride", (basic.Integer, 'Stride'))
        reg.add_output_port(cls, "FFT Output", (NDArray, 'FFT Output'))
