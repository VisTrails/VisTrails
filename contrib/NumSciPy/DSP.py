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

class SignalGenerator(DSPModule, Module):
    my_namespace = 'scipy|signals|generator'

    def compute(self):
        samples = self.get_input("Samples")
        periods = self.get_input("Periods")
        freqs = self.getInputListFromPort("Frequencies")

        ar = numpy.linspace(0., float(periods) * 2. * scipy.pi, periods * samples)
        out_ar = numpy.zeros(periods * samples)

        for f in freqs:
            out_ar += scipy.sin(f * ar)

        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Samples", (basic.Integer, "Sampling Rate"))
        reg.add_input_port(cls, "Periods", (basic.Integer, "Signal Length"))
        reg.add_input_port(cls, "Frequencies", (basic.Float, "Additive Frequency"))
        reg.add_output_port(cls, "Output", (NDArray, "Output Signal"))

class FFT(DSPModule, Module):
    __doc__ = """ Calculate the discrete Fourier transform of the arbitrary
    sequence presented on the Signal port.  This is done using
    SciPy's FFTPack module.\n\n"""
    __doc__ += """From fftpack.fft:\n\t"""
    __doc__ += fftpack.fft.__doc__

    my_namespace = 'scipy|signals|fourier'
    
    def compute(self):
        sig_array = self.get_input("Signals")

        # If there is no input on the samples port,
        # use the number of samples in an array row for
        # the number of fft points.
        if self.hasInputFromPort("Samples"):
            pts = self.get_input("Samples")
            
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
    
    my_namespace = 'scipy|signals|fourier'

    def compute(self):
        sig_array = self.get_input("Signals")
        # If there is no input on the samples port,
        # use the number of samples in an array row for
        # the number of fft points.
        if self.hasInputFromPort("Samples"):
            pts = self.get_input("Samples")
            
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
    my_namespace = 'scipy|signals|fourier'

    def get_signal(self, sigs, window, offset, size):
        win = scipy.zeros(sigs.shape[0])
        win[offset:offset+size] = window
        part = sigs * win
        return part

    def compute(self):
        sigs = self.get_input("Signals")
        sr = self.get_input("SamplingRate")

        out_vol = None

        if self.hasInputFromPort("Window"):
            window = self.get_input("Window").get_array()
            win_size = window.shape[0]
        else:
            win_size = self.get_input("Window Size")
            window = scipy.signal.hamming(win_size)

        if self.hasInputFromPort("Stride"):
            stride = self.get_input("Stride")
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

class SignalSmoothing(DSPModule, Module):
    """
    Documentation
    """
    def compute(self):
        window = self.get_input("Window").get_array()
        in_signal = self.get_input("Signal").get_array()

        to_conv = window/window.sum() # Make sure the window is normalized
        if in_signal.ndim > 1:
            out_ar = numpy.zeros(in_signal.shape)
        else:
            out_ar = numpy.zeros(1,in_signal.shape[0])
            in_signal.shape = (1, in_signal.shape[0])

        for row in xrange(in_signal.shape[0]):
            out_ar[row] = numpy.convolve(to_conv, in_signal[row], mode='same')

        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output Array", out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signal", (NDArray, "Input Signals"))
        reg.add_input_port(cls, "Window", (NDArray, "Smoothing Filter"))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Smoothed Signals'))
        
# class SingleTrialPhaseLocking(DSPModule, Module):
#     """
#     Documentation
#     """
#     def get_time_indexes(self, t0, time_window):
#         if time_window % 2:
#             # odd number of samples:  t0 +/- (window-1)/2
#             tw = (time_window - 1) / 2
#         else:
#             tw = time_window / 2
#         return (t0 - tw, t0 + tw)
    
#     def calc_pli(self, f_n_ar, f_m_ar):
#         phasors = numpy.concatenate((f_n_ar, f_m_ar))
#         norm_c = numpy.sqrt(phasors.real*phasors.real + phasors.imag*phasors.imag)
#         phasors /= norm_c
#         mean_phasor = phasors.mean()
#         pli = numpy.sqrt(mean_phasor.real*mean_phasor.real + mean_phasor.imag*mean_phasor.imag)
#         return pli
    
#     def compute(self):
#         phasors = self.get_input("Phasor Array").get_array()
#         time_window = self.get_input("Time Window")
#         time_step = self.force_get_input("Time Step")
#         if time_step == None:
#             time_step = 1
            
#         ndims = phasors.ndim
#         if ndims == 2:
#             phasors.shape = (1, phasors.shape[0], phasors.shape[1])
#         elif ndims == 1:
#             phasors.shape = (1, phasors.shape[0], 1)
#         else:
#             raise ModuleError("Cannot Process Phasor set of dimension " + str(ndims))
        
#         num_freqs = phasors[0].shape[0]
#         num_times = phasors[0].shape[1]
#         num_times /= time_step
#         out_ar = numpy.zeros((phasors.shape[0], num_freqs, num_freqs, num_times))
#         for channel in xrange(phasors.shape[0]):
#             tfr = phasors[channel,:,:].squeeze()
#             for f_m in xrange(tfr.shape[0]):
#                 f_m_row = tfr[f_m,:]
#                 for f_n in xrange(f_m+1, tfr.shape[0], 1):
#                     f_n_row = tfr[f_n,:]
#                     t0 = 0
#                     tn = 0
#                     (start_i, end_i) = self.get_time_indexes(t0, time_window)
#                     while t0 < f_m_row.shape[0]:
#                         f_m_range = f_m_row[max(0,start_i):min(end_i,f_m_row.shape[0]-1)]
#                         f_n_range = f_n_row[max(0,start_i):min(end_i,f_n_row.shape[0]-1)]
#                         pli = self.calc_pli(f_m_range, f_n_range)
#                         out_ar[channel, f_m, f_n, tn] = pli
#                         out_ar[channel, f_n, f_m, tn] = pli
#                         out_ar[channel, f_m, f_m, tn] = 1.0
#                         tn += 1
#                         t0 += time_step
#                         start_i += time_step
#                         end_i += time_step

#         out = NDArray()
#         out.set_array(out_ar)
#         self.setResult("Output Array", out)

#     @classmethod
#     def register(cls, reg, basic):
#         reg.add_module(cls, namespace=cls.my_namespace)
#         reg.add_input_port(cls, "Phasor Array", (NDArray, 'Phasor Array'))
#         reg.add_input_port(cls, "Time Step", (basic.Integer, 'Stride in the Time Domain'))
#         reg.add_input_port(cls, "Time Window", (basic.Integer, 'Samples per Timeslice'))
#         reg.add_output_port(cls, "Output Array", (NDArray, 'Result set'))

# class CalculatePhaseLocking(DSPModule, Module):
#     """
#     documentation
#     """
#     def Phi(self, p):
#         return scipy.arctan2(p.real, p.imag)
    
#     def compute(self):
#         phasors = self.get_input("Phasor Array").get_array()
#         if phasors.ndim != 3:
#             raise ModuleError("Cannot handle phasor array with less than 3 dimensions")

#         (trials, times, frequencies) = phasors.shape
#         lowestF = self.get_input("Lowest Freq")
# #        highestF = self.get_input("Highest Freq")
        
#         Phi = self.Phi(phasors)

#         gamma_ar = numpy.zeros((times, frequencies, frequencies))
        
#         for t in range(times):
#             n = lowestF
#             for fn_i in range(frequencies):
#                 n += fn_i
#                 fn = fn_i + lowestF
#                 m = lowestF
#                 for fm_i in range(fn_i, frequencies, 1):
#                     m += fm_i
#                     fm = fm_i + lowestF
#                     DeltaPhi = (float((n+m)/(2*m))Phi[:,t,fm_i] - float((n+m)/(2*n))Phi[:,t,fn_i]) % (2. * scipy.pi)
#                     Gamma = exp(complex(0.,DeltaPhi))
#                     Gamma = Gamma.sum()
#                     Gamma = numpy.sqrt(Gamma * Gamma.conjugate())
#                     gamma_ar[t, fn_i, fm_i] = Gamma
#                     gamma_ar[t, fm_i, fn_i] = Gamma
#                     m += 1
#                 n += 1

#         out = NDArray()
#         out.set_array(gamma_ar)
#         self.setResults("Gamma", out)

#     @classmethod
#     def register(cls, reg, basic):
#         reg.add_module(cls, namespace=cls.my_namespace)
#         reg.add_input_port(cls, "Phasor Array", (NDArray, 'Phasor Array'))
#         reg.add_input_port(cls, "Lowest Freq", (basic.Integer, 'Lowest Frequency Phasor'))
#         reg.add_output_port(cls, "Gamma", (NDArray, 'Phase Locking Volume'))
        

# class DifferentialPhaseLocking(DSPModule, Module):
#     """
#     documentation
#     """
#     def compute(self):
#         phasors = self.get_input("Phasor Array").get_array()
#         if phasors.ndim != 2:
#             raise ModuleError("Cannot handle phasor array with more than 2 dimensions")

#         mag = phasors.real*phasors.real + phasors.imag*phasors.imag
#         mag = numpy.sqrt(mag)
#         normalized = phasors / mag

        
