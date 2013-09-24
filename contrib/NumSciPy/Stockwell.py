import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from Matrix import *
from Array import *
from DSP import DSPModule
import scipy
import scipy.signal
import scipy.fftpack
import numpy
import smt
import st
import time

class StockwellModule(object):
    my_namespace = 'scipy|signals|stockwell'
#    my_namespace = 'scipy|signals'

class IsotropicScaleVolumes(StockwellModule, Module):
    def compute(self):
        vol = self.get_input("Input").get_array()
        lof = self.get_input("Low Freq")
        hif = self.get_input("Hi Freq")
        max_vol = numpy.zeros(vol.shape)
        grav_vol = numpy.zeros(vol.shape)

        (slices,rows,cols) = vol.shape
        for z in range(slices):
            tr = time.time()
            for y in range(rows):
                ray = vol[z,y,:].squeeze()
                t = st.st(ray, lof, hif)
                for x in range(cols):
                    scales = t[:,x].squeeze()
                    scales = scales * scales.conjugate()

                    max_vol[x,y,z] = float(scales.argmax())

                    grav = 0.
                    for i in range(scales.shape[0]):
                        v = scales[i]
                        f = lof + i
                        grav += float(v) * float(f)

                    grav_vol[x,y,z] = grav
            
            print "done z = ", z
            print "took: ", (time.time() - tr) * 1000.

        grav_vol = grav_vol - grav_vol.min()
        grav_vol = grav_vol / grav_vol.max()
        grav_vol = grav_vol * float(hif - lof)
        grav_vol = grav_vol + lof
        max_out = NDArray()
        max_out.set_array(max_vol)
        grav_out = NDArray()
        grav_out.set_array(grav_vol)
        self.setResult("Max Output", max_out)
        self.setResult("Grav Output", grav_out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, "Input Signals"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_output_port(cls, "Max Output", (NDArray, "Output Max TFR"))
        reg.add_output_port(cls, "Grav Output", (NDArray, "Output Grav TFR"))


class ScaleVolumes(StockwellModule, Module):
    def compute(self):
        vol = self.get_input("Input").get_array()
        lof = self.get_input("Low Freq")
        hif = self.get_input("Hi Freq")
        sigma = self.force_get_input("Sigma")
        max_vol = numpy.zeros(vol.shape)
        grav_vol = numpy.zeros(vol.shape)

        (slices,rows,cols) = vol.shape
        for z in range(slices):
            t = time.time()
            for y in range(rows):
                for x in range(cols):
                    # grab our 3 rays
                    xray = vol[z,y,:].squeeze()
                    yray = vol[z,:,x].squeeze()
                    zray = vol[:,y,x].squeeze()
                    
                    # Transform each ray
                    xt = st.st(xray,lof,hif)
                    yt = st.st(yray,lof,hif)
                    zt = st.st(zray,lof,hif)

                    # Grab the point at all valid scales
                    xpt = xt[:,x]
                    ypt = yt[:,y]
                    zpt = zt[:,z]

                    # Take the magnitude
                    xpt = xpt * xpt.conjugate()
                    ypt = ypt * ypt.conjugate()
                    zpt = zpt * zpt.conjugate()

                    scale_vec = xpt.real + ypt.real + zpt.real
                    if sigma:
                        scale_vec = scale_vec * scipy.signal.gaussian(scale_vec.shape[0], sigma)

                    scale = scale_vec.argmax()
                    max_vol[x,y,z] = scale

#                    scale_vec = 
#                    scale_vec = scale_vec / scale_vec.sum()


                    grav = 0
                    for s in range(scale_vec.shape[0]):
                        v = scale_vec[s]
                        f = lof + s
                        grav += float(f) * float(v)

#                    grav = grav / float(scale_vec.shape[0])
                    
                    grav_vol[x,y,z] = grav
                    
            print "done z = ", z
            print "took: ", (time.time() - t) * 1000.

        grav_vol = grav_vol - grav_vol.min()
        grav_vol = grav_vol / grav_vol.max()
        grav_vol = grav_vol * float(hif - lof)
        grav_vol = grav_vol + lof
        max_out = NDArray()
        max_out.set_array(max_vol)
        grav_out = NDArray()
        grav_out.set_array(grav_vol)
        self.setResult("Max Output", max_out)
        self.setResult("Grav Output", grav_out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, "Input Signals"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_input_port(cls, "Sigma", (basic.Float, "Sigma"))
        reg.add_output_port(cls, "Max Output", (NDArray, "Output Max TFR"))
        reg.add_output_port(cls, "Grav Output", (NDArray, "Output Grav TFR"))


class MaximalScaleVolume(StockwellModule, Module):
    def compute(self):
        vol = self.get_input("Input").get_array()
        lof = self.get_input("Low Freq")
        hif = self.get_input("Hi Freq")
        sigma = self.force_get_input("Sigma")
        out_vol = numpy.zeros(vol.shape)

        (slices,rows,cols) = vol.shape
        for z in range(slices):
            t = time.time()
            for y in range(rows):
                for x in range(cols):
                    # grab our 3 rays
                    xray = vol[z,y,:].squeeze()
                    yray = vol[z,:,x].squeeze()
                    zray = vol[:,y,x].squeeze()
                    
                    # Transform each ray
                    xt = st.st(xray,lof,hif)
                    yt = st.st(yray,lof,hif)
                    zt = st.st(zray,lof,hif)

                    # Grab the point at all valid scales
                    xpt = xt[:,x]
                    ypt = yt[:,y]
                    zpt = zt[:,z]

                    # Take the magnitude
                    xpt = xpt * xpt.conjugate()
                    ypt = ypt * ypt.conjugate()
                    zpt = zpt * zpt.conjugate()

                    scale_vec = xpt.real + ypt.real + zpt.real
                    if sigma:
                        scale_vec = scale_vec * scipy.signal.gaussian(scale_vec.shape[0], sigma)

                    scale = scale_vec.argmax()
                    out_vol[x,y,z] = scale
            print "done z = ", z
            print "took: ", (time.time() - t) * 1000.

        out = NDArray()
        out.set_array(out_vol)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, "Input Signals"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_input_port(cls, "Sigma", (basic.Float, "Sigma"))
        reg.add_output_port(cls, "Output", (NDArray, "Output TFR"))
        

class StockwellTransform(StockwellModule, Module):
    def compute(self):
        t = time.time()
        signals = self.get_input("Signals").get_array()
        lof = self.get_input("Low Freq")
        hif = self.get_input("Hi Freq")
        if len(signals.shape) == 1:
            signals.shape = (1, signals.shape[0])

        outl = []
        for i in xrange(signals.shape[0]):
            sig_ar = signals[i]
            x = st.st(sig_ar, lof, hif)
            outl.append(x)

        out_ar = numpy.array(outl).squeeze()
        print "c time = ", (time.time() - t) * 1000.
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, "Input Signals"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_output_port(cls, "Output", (NDArray, "Output TFR"))

class PyStockwellTransform(StockwellModule, Module):

    def get_gaussian(self, length, freq, factor=1.0):
        g = numpy.arange(float(length))
        g = g*g
        g = scipy.exp(-2. * scipy.pi * scipy.pi * g / (float(freq)*float(freq)))
        return g
#       return numpy.roll(g, length/2)#.astype(complex)
    
    def compute(self):
        t = time.time()
        signal = self.get_input("Signal").get_array().squeeze()
        print "signal.shape = ", signal.shape
        f = scipy.fftpack.fft(signal)
        print "got f made"
        f = scipy.fftpack.hilbert(f)
        print "got hilbert done"
#        f2 = numpy.concatenate((f,f))

        lof = self.get_input("Low Freq")
        hif = self.get_input("Hi Freq")

        out_ar = numpy.zeros((hif-lof+1, signal.shape[0]))

        start = 0
        if lof == 0:
            out_ar[0,:] = signal.mean()
            start = 1

        for k in range(start, hif-lof, 1):
            g = self.get_gaussian(signal.shape[0], lof+k)
            o = scipy.fftpack.ifft(numpy.roll(f,lof+k) * g) / float(signal.size)
            out_ar[k,:] = o

        print "time = ", (time.time() - t) * 1000.
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signal", (NDArray, "Input Signal"))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Integer, "High Frequency"))
        reg.add_output_port(cls, "Output", (NDArray, "Output TFR"))
        
class MultiTaperStockwellTransform(StockwellModule, Module):
    def compute(self):
        signals = self.get_input("Signals").get_array()
        sr = self.get_input("Sample Rate")
        lof = self.get_input("Low Freq")
        hif = self.get_input("Hi Freq")

        if len(signals.shape) == 1:
            signals.shape = (1, signals.shape[0])

        if self.has_input("Bandwidth"):
            self.k = smt.calcK(self.get_input("Bandwidth"),signals.shape[1], sr)
        else:
            self.k = self.get_input("K")

        outl = []
        for i in xrange(signals.shape[0]):
            sig_ar = signals[i]
            x = smt.mtst(self.k, smt.calc_tapers(self.k, signals.shape[1]), sig_ar, lof, hif)
            outl.append(x)

        out_ar = numpy.array(outl).squeeze()
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Array'))
        reg.add_input_port(cls, "Sample Rate", (basic.Integer, 'Sample Rate'))
        reg.add_input_port(cls, "K", (basic.Float, "K"))
        reg.add_input_port(cls, "Bandwidth", (basic.Float, "Bandwidth"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_output_port(cls, "Output", (NDArray, "Output TFR"))

class FastStockwell3D(StockwellModule, Module):
    """
    Compute an approximation to the 3D Stockwell Transform.
    The output is a 4D array with dimensions as follows:
    output.shape = (voices, slices, rows, columns)
    """
    def compute(self):
        in_ar = self.get_input("Input").get_array()
        lo_f  = self.get_input("Low Freq")
        hi_f  = self.get_input("High Freq")
        num_f = hi_f - lo_f + 1

        (slices, rows, cols) = in_ar.shape
        out_ar = numpy.zeros((num_f, slices, rows, cols))
        for s in range(slices):
            for r in range(rows):
                sig = in_ar[s,r,:]
                t = st.st(sig,lo_f,hi_f)
                t = t.conjugate() * t
                t = t.real
                for f in range(t.shape[0]):
                    out_ar[f,s,r,:] = t[f,:]

        print "done dim 1"
        for s in range(slices):
            for c in range(cols):
                sig = in_ar[s,:,c]
                t = st.st(sig,lo_f,hi_f)
                t = t.conjugate() * t
                t = t.real
                for f in range(t.shape[0]):
                    out_ar[f,s,:,c] += t[f,:]

        print "done dim 2"
        for r in range(rows):
            for c in range(cols):
                sig = in_ar[:,r,c]
                t = st.st(sig,lo_f,hi_f)
                t = t.conjugate() * t
                t = t.real
                for f in range(t.shape[0]):
                    out_ar[f,:,r,c] += t[f,:]

        print "done dim 3"
#        out_ar = out_ar * out_ar.conjugate()
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Input Volume'))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, 'Lowest Voice'))
        reg.add_input_port(cls, "High Freq", (basic.Integer, 'Highest Voice'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Voice Volume'))

class ScaleSpaceHistogram(StockwellModule, Module):
    def compute(self):
        signal = self.get_input("Input").get_array()
        lof = self.get_input("Low Freq")
        hif = self.get_input("High Freq")

        num_pts = signal.size
        min_s = signal.min()
        max_s = signal.max()
        d = max_s - min_s
        print "Accumulating over " + str(num_pts) + " points"
        histo = numpy.zeros((512,hif-lof+1))
        print "Histo: ",histo.shape
        dist = numpy.zeros(512)
        for z in range(signal.shape[2]):
            for y in range(signal.shape[1]):
                for x in range(signal.shape[0]):
                    sigx = signal[z,y,:]
                    sigy = signal[z,:,x]
                    tx = st.st(sigx, lof, hif)
                    ty = st.st(sigy, lof, hif)
                    sigz = signal[:,y,z]
                    tz = st.st(sigz, lof, hif)
                    tz = tz[:,x].squeeze()
                    tz = tz * tz.conjugate()
                    tx = tx[:,z].squeeze()
                    ty = ty[:,y].squeeze()
                    tx = tx * tx.conjugate()
                    ty = ty * ty.conjugate()

                    ar = tx.real + ty.real + tz.real
                    ar = ar / ar.sum()
#                    ar = ar.sum(axis=1)
#                    print "ar: ", ar.shape
#                    ar.shape = (ar.shape[0],1)
                    scalar = signal[z,y,x]
                    try:
                        bin = int((scalar - min_s) / d * 511.)
#                        dist[bin] += 1
#                        print bin, scalar, ar
                        sigma = self.force_get_input("Sigma")
                        if sigma:
                            ar = scipy.signal.gaussian(ar.size, sigma) * ar
                        histo[bin,:] += ar
                    except:
                        print "Cannot assign to bin: " + str(bin) +", scalar: " +str(scalar)
                        print "location = ", x, y, z
                        raise ModuleError("Cannot assign to bin: " + str(bin) +", scalar: " +str(scalar))
                    
#                print "done with y = ", y
            print "done with z = ", z

        out = NDArray()
        out.set_array(histo)# / dist)
        self.setResult("Output", out)
                    
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Input Volume'))
        reg.add_input_port(cls, "Sigma", (basic.Float, 'Sigma'))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, 'Lowest Voice'))
        reg.add_input_port(cls, "High Freq", (basic.Integer, 'Highest Voice'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Voice Volume'))

class PyScaleSpaceHistogram(StockwellModule, Module):
    def get_gaussian(self, length, freq, factor=1.0):
        g = numpy.arange(float(length))
        g = g*g
        g = scipy.exp(-2. * scipy.pi * scipy.pi * g / (float(freq)*float(freq)))
        return g

    def stockwell(self, ray, lof, hif):
        ret = numpy.zeros((hif-lof,ray.shape[0]))
#        ray = scipy.fftpack.hilbert(ray)
#        ray = numpy.concatenate((ray,ray[::-1]))
        start = 0
        if lof == 0:
            ret[0,:] = ray.mean()
            start = 1

        for k in range(start, hif-lof, 1):
            g = self.get_gaussian(ray.shape[0], lof+k)
            o = scipy.fftpack.ifft(numpy.roll(ray,lof+k) * g) / float(ray.size)
            ret[k,:] = o

        return ret
    
    def compute(self):
        signal = self.get_input("Input").get_array().squeeze()
        print "signal.shape = ", signal.shape
        lof = self.get_input("Low Freq")
        hif = self.get_input("High Freq")

        num_scalar_bins = self.get_input("Scalar Bins")

        num_pts = signal.size
        min_s = signal.min()
        max_s = signal.max()
        d = max_s - min_s
        print "Accumulating over " + str(num_pts) + " points"
        histo = numpy.zeros((num_scalar_bins,hif-lof))

        f_sig = scipy.fftpack.fftn(signal)

        for z in range(signal.shape[0]):
            for y in range(signal.shape[1]):
                for x in range(signal.shape[2]):
                    yray = f_sig[z,:,x].squeeze()
                    ty = self.stockwell(yray, lof, hif)
                    zray = f_sig[:,y,x].squeeze()
                    tz = self.stockwell(zray, lof, hif)
                    xray = f_sig[z,y,:].squeeze()
                    tx = self.stockwell(xray, lof, hif)

                    tx = tx[:,z].squeeze()
                    ty = ty[:,y].squeeze()
                    tz = tz[:,x].squeeze()

                    tx = tx * tx.conjugate()
                    ty = ty * ty.conjugate()
                    tz = tz * tz.conjugate()
                    
                    ar = tx.real + ty.real + tz.real
                    ar = ar / ar.sum()
                    
    
                    scalar = signal[z,y,x]
                    try:
                        bin = int((scalar - min_s) / d * float(num_scalar_bins-1.))
#                        dist[bin] += 1
#                        print bin, scalar, ar
                        sigma = self.force_get_input("Sigma")
                        if sigma:
                            ar = scipy.signal.gaussian(ar.size, sigma) * ar
                        histo[bin,:] += ar
                    except:
                        print "Cannot assign to bin: " + str(bin) +", scalar: " +str(scalar)
                        print "location = ", x, y, z
                        raise ModuleError("Cannot assign to bin: " + str(bin) +", scalar: " +str(scalar))
                    
#                print "done with y = ", y
            print "done with z = ", z

        out = NDArray()
        out.set_array(histo)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Input Volume'))
        reg.add_input_port(cls, "Scalar Bins", (basic.Integer, 'Scalar Bins'))
        reg.add_input_port(cls, "Sigma", (basic.Float, 'Sigma'))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, 'Lowest Voice'))
        reg.add_input_port(cls, "High Freq", (basic.Integer, 'Highest Voice'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Voice Volume'))

class PointBasedStockwell(StockwellModule, Module):
    def compute(self):
        signal = self.get_input("Input").get_array()
        ptx = self.get_input("X")
        pty = self.get_input("Y")
        ptz = self.get_input("Z")

        lof = self.get_input("Low Freq")
        hif = self.get_input("High Freq")

        sigx = signal[ptz,pty,:]
        sigy = signal[ptz,:,ptx]
        sigz = signal[:,pty,ptx]

        tx = st.st(sigx, lof, hif)
        ty = st.st(sigy, lof, hif)
        tz = st.st(sigz, lof, hif)

        tx = tx * tx.conjugate()
        ty = ty * ty.conjugate()
        tz = tz * tz.conjugate()

        out_ar = tx.real + ty.real + tz.real
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Input Volume'))
        reg.add_input_port(cls, "X", (basic.Integer, 'X'))
        reg.add_input_port(cls, "Y", (basic.Integer, 'Y'))
        reg.add_input_port(cls, "Z", (basic.Integer, 'Z'))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, 'Lowest Voice'))
        reg.add_input_port(cls, "High Freq", (basic.Integer, 'Highest Voice'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Voice Volume'))        

class Stockwell2D(StockwellModule, Module):
    ''' Calculate the 3D Stockwell Transform '''
    def g_window(self, l, w):
        if w != 0.0:   
            sigma = l / (2 * pi * w)
        else:   
            print 'w is zero!'
        g = numpy.zeros(l)
        iarr = numpy.arange(float(l))
        ex = (iarr - l / 2) ** 2 / (2 * sigma ** 2)
        wl = numpy.where(numpy.ravel(ex < 25))[0]
        g = numpy.where(ex < 25., numpy.exp(-1.*ex), ex)
#        g = roll(g, -l / 2)
        return g.astype(complex)
        
    def get_gaussian(self, sx, sy, kx, ky, factor=1.0):
        wrow = factor * (float(sx) / float(kx))
        wcol = factor * (float(sy) / float(ky))
        sig_row = 1. / (2. * scipy.pi * wrow)
        sig_col = 1. / (2. * scipy.pi * wcol)
        print "sigmas = ", sig_row, sig_col

        grow = scipy.signal.gaussian(sx, sig_row)
        gcol = scipy.signal.gaussian(sy, sig_col)

        print "gaussians good?"
        grow.shape = sx,1
        gcol.shape = 1,sy

        print "gaussians reshaped"
        gwin = grow*gcol
        print "2d formed..."
        gwin = gwin.astype(complex)
        print "gaussian formed"
        return gwin

    def compute(self):
        in_ar = self.get_input("Input").get_array()
        lof = self.get_input("Low Freq")
        hif = self.get_input("High Freq")
        (nx,ny) = in_ar.shape
        nf = hif-lof
        kx_len = nf
        nyquist_x = nx/2 + 1
        ky_len = nf
        h = scipy.fftpack.fftn(in_ar)
        h = scipy.fftpack.fftshift(h)
        or_spe = h

        print "allocating output", nf,kx_len,ky_len
        # allocate output
        try:
            l = numpy.zeros((nf, nx, ny))
        except:
            raise ModuleError("Cannot allocate output array")
        print "Output Allocated - ", l.shape

        vf = 0
        for ky in range(lof, hif, 1):
            print "ky = ", ky
            for kx in range(lof, hif, 1):
                print "kx = ", kx
                if kx >= nyquist_x:
                    kxwidth = nx - kx
                else:
                    kxwidth = kx

                print "kxwidth = ", kxwidth
                gw = self.get_gaussian(nx,ny,kxwidth,ky)
                
                b = h * gw
                h = numpy.roll(h,-1,axis=0)
                voice = scipy.fftpack.ifftn(scipy.fftpack.ifftshift(b))
                print "voice shape = ", voice
                t = voice * voice.conjugate()
                print "t.min() = ", t.min()
                print "t.max() = ", t.max()
                l[vf,:,:] += t.real
            h = or_spe
            h = numpy.roll(h, -1, axis=1)
            vf += 1

        print l.shape
        out = NDArray()
        out.set_array(l)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Input Volume'))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, 'Lowest Voice'))
        reg.add_input_port(cls, "High Freq", (basic.Integer, 'Highest Voice'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Voice Volume'))

class FrequencyPhaseLocking(StockwellModule, Module):
    """
    Compute the phase-locking index with respect to a single frequency.  The algorithm
    implemented is the realization of that outline in Sauseng et al. Cross-frequency phase
    synchronization: A brain mechanism of memory matching and attention:  NeuroImage - 2008

    To summarize, the instantaneous phase of a signal at a given frequency and time is denoted
    \Phi(f, t) = arctan(F_{Real}(x(t)), F_{Imaginary}(x(t)))

    The generalized phase differences between two signal components with an m:n frequency relationship
    is:

    \frac{m+n}{2n}f_n = \frac{n+m}{2m}f_m

    \Delta \Phi(f_n,f_m,t) = (\frac{n+m}{2m} \Phi(f_m, t) - \frac{m+n}{2n}f_n \Phi(f_n, t)) % 2 \pi

    And the Phase Synchronization Index is defined as:

    \hat{\Gamma}_\Phi(f_n,f_m,t) = \|\langle e^{j \Delta \Phi(f_n,f_m,t)} \rangle\|, j = \sqrt{-1}

    """
    def make_delta_phi(self, phase_ar):
        (freqs,times) = phase_ar.shape
        dphi_ar = numpy.zeros((times, freqs, freqs))
        for t in range(times):
            for fn in range(freqs):
                f_n = float(fn) + float(self.lof)
                for fm in range(fn+1,freqs,1):
                    f_m = float(fm) + float(self.lof)
                    n = 1.
                    m = f_n / f_m
                    phi_m = phase_ar[fm,t]
                    phi_n = phase_ar[fn,t]
                    dphi = (((n+m)/2.*m) * phi_m) - (((n+m)/2.*n) * phi_n)
                    dphi = dphi % (2. * numpy.pi)
                    dphi_ar[t,fn,fm] = dphi
                    dphi_ar[t,fm,fn] = dphi

        # dphi_ar.shape = (sig_len, freq_range, freq_range)
        return dphi_ar
    
    def compute(self):
        trial_ar = self.get_input("Single Trials").get_array()
        print "trial_ar.shape = ", trial_ar.shape
        self.lof = self.get_input("Low Freq")
        self.hif = self.get_input("High Freq")
        sensor_list = self.forceGetInputListFromPort("Sensors")
        
        if len(trial_ar.shape) != 3:
            raise ModuleError("Cannot process input with rank not 3")

        (trials, sensors, sig_len) = trial_ar.shape
        if sensor_list == None:
            sensor_list = numpy.arange(sensors)
        else:
            sensor_list = numpy.array(sensor_list)
            
        # Compute the TFR for a single sensor across all trials
        freq_range = self.hif - self.lof
        out_ar = numpy.zeros((sensor_list.shape[0], sig_len, freq_range+1, freq_range+1))
        print "sensor list = ", sensor_list
        
        # For each sensor to consider, extract the signal array
        for i in range(sensor_list.shape[0]):
            tmp_sig = trial_ar[:,sensor_list[i],:].squeeze()
            # For each trial, extract the signal
            for j in range(trials):
                sig = tmp_sig[j,:].squeeze()
                tfr = st.st(sig, self.lof, self.hif)

                # Compute the phase for the Time-freq plane
                p = numpy.arctan2(tfr.real, tfr.imag)
                
                # the ordering of p is:  (freqs,times) = p.shape
                dphi_ar = numpy.array(0.-1.j*self.make_delta_phi(p.real))
                dphi_ar = numpy.exp(dphi_ar)
                out_ar[i,:,:,:] += dphi_ar

                print "Trial " + str(j) + " done processing..."
            print "out_ar done with all trials"
            out_ar[i,:,:,:] /= float(trials)
            out_ar[i,:,:,:] = out_ar[i,:,:,:] * out_ar[i,:,:,:].conjugate()
            out_ar[i,:,:,:] = out_ar[i,:,:,:].real
            print "min,max,mean = ", out_ar[i].min(), out_ar[i].max(), out_ar[i].mean()
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Single Trials", (NDArray, "Input Single Trial Array"))
        reg.add_input_port(cls, "Low Freq", (basic.Integer, "Low Frequency"))
        reg.add_input_port(cls, "High Freq", (basic.Integer, "High Frequency"))
        reg.add_input_port(cls, "Sensors", (basic.Integer, "Sensors"))
        reg.add_output_port(cls, "Output", (NDArray, "Phase Locking Volume"))
