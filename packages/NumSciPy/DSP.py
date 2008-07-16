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
            try:
                pts = sig_array.get_shape()[1]
            except:
                pts = sig_array.get_shape()[0]

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
        win = scipy.zeros(sigs.shape[0])
        win[offset:offset+size] = window
        part = sigs * win
        return part

    def compute(self):
        sigs = self.getInputFromPort("Signals")
        sr = self.getInputFromPort("SamplingRate")

        out_vol = None

        if self.hasInputFromPort("Window"):
            window = self.getInputFromPort("Window").get_array()
            win_size = window.shape[0]
        else:
            win_size = self.getInputFromPort("Window Size")
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
            signal = sigs.get_array()[i]
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

class StockwellTransform(DSPModule, Module):

    def __init__(self):
        Module.__init__(self)

    def compute_basis(self, N, order, tau):
        al2 = scipy.log(2.)
        imag = 0-1j
        if order == 0:
            s = numpy.ones(N)
            s = s + 0j
            return s
        elif order == 1:
            t = numpy.arange(float(N))
            cosar = scipy.cos(2.*scipy.pi*t/float(N))
            sinar = scipy.sin(2.*scipy.pi*t/N)
            s = numpy.cast['complex64'](cosar)
            s.imag = -1.*sinar
            return s
        elif order >= 2:
            aln = scipy.log(float(N))
            if order <= (aln/al2 - 1):
                v = float(pow(2,order-1) + pow(2,order-2))
                b = float(pow(2,order-1))
                k = numpy.arange(float(N))
                s = numpy.zeros(N)
                s = s + 0j
                factor = numpy.exp(imag * scipy.pi * tau) / numpy.sqrt(b)
                firstterm = numpy.exp(imag * 2. * scipy.pi * ((k / N) - (tau / b)) * (v - (b/2.) - 0.5))
                termtwo = numpy.exp(imag * 2. * scipy.pi * ((k / N) - (tau / b)) * (v + (b/2.) - 0.5))
                den = 2. * scipy.sin(scipy.pi * ((k / N) - (tau / b)))
                cond = numpy.where(den != 0.)
                wcond = numpy.where(den == 0.)
                s[cond] = factor * imag * (firstterm[cond] - termtwo[cond]) / den[cond]
                if len(wcond[0]) > 0:
                    s[wcond] = numpy.sqrt(b) * numpy.exp(imag * scipy.pi * tau)

                return s
        else:
            raise ModuleError("Order less than 0")

    def get_partitions(self, n):
        n_freqs = n/2
        a = self.partition(n_freqs)
        s = a.sum()
        if s < n_freqs:
            diff = numpy.ones((n_freqs - s))
            a = numpy.concatenate((a,diff))
            print "s < freqs:  diff = ", diff
        if n % 2 == 0:
            b = a[1:]
            a = numpy.concatenate((a[::-1],b))
        else:
            b = a[0:]
            a = numpy.concatenate((a[::-1],b))

        a = numpy.concatenate(([1.],a))
        return a

    def partition(self, n, partsizes=None):
        if n == 1:
            if partsizes == None:
                return numpy.array([1])
            else:
                return partsizes
#                return numpy.concatenate((partsizes,[1]))
        
        if partsizes == None:
            if n%2 == 0:
                partsizes = numpy.array([1])

        half = long(float((n+1) / 2.))
        if partsizes == None:
            partsizes = numpy.array([half])
        else:
            partsizes = numpy.concatenate((partsizes,[half]))

        rem = n - half
        return self.partition(rem, partsizes=partsizes)
#         if rem > 0.:

#         print "output partsizes = ", partsizes
#         return partsizes

    def do_dost(self, signal):
        sig = signal.squeeze()
        length = sig.shape[0]
        partitions = self.get_partitions(length)
        num_parts = partitions.shape[0]
        big_part = partitions.max()
        np = num_parts / 2
        sp = numpy.zeros((np,big_part))

        for i in xrange(np):
            p_len = partitions[i]
            voice = numpy.zeros(p_len) + 0j
            for j in xrange(p_len):
                b_func = self.compute_basis(length, i, j) / numpy.sqrt(float(pow(2.,float(i-1.))))
                dprod = sig * b_func
                voice[j] = dprod.sum()
            # Not sure if this resample is necessary...
            print "voice shape = ", voice.shape
            sp[i] = scipy.signal.resample(voice, big_part, window=('ksr', 3.))
            
        return sp
        
    def compute(self):
        signal = self.getInputFromPort("Signals")
        sig_ar = signal.get_array()
        if len(sig_ar.shape) == 1:
            sig_ar.shape = (1,sig_ar.shape[0])
        try:
            (num_sigs, sig_len) = sig_ar.shape
        except:
            raise ModuleError("Signal Array shape is invalid.")

        out_list = []
        for i in xrange(num_sigs):
            sig = sig_ar[i]
            out_list.append(self.do_dost(sig))

        out_ar = numpy.array(out_list)
        out = self.create_instance_of_type('edu.utah.sci.vistrails.numpyscipy','Numpy Array','numpy|array')
        out.set_array(out_ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Signal Array'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output TFR Collection'))
