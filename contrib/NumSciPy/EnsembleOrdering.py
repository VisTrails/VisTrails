import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from Array import *
import copy
import scipy
import numpy
from scipy import fftpack
import time

class EnsembleModule(object):
    my_namespace = 'scipy|signals|ensembles'

class ComputeDistance(EnsembleModule, Module):
    def compute(self):
        vol = self.getInputFromPort("Signals").get_array()
        num_im = vol.shape[0]

        out_ar = numpy.zeros((num_im, num_im))
        for i in range(num_im):
            im_i = vol[i].squeeze().flatten()
            for j in range(i+1, num_im, 1):
                im_j = vol[j].squeeze().flatten()

                d = (im_i - im_j)
                d = d * d
                d = numpy.sqrt(d.sum())

                out_ar[i,j] = d
                out_ar[j,i] = d

        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Planes'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Distance Matrix'))

class OrderByIndexes(EnsembleModule, Module):
    """ Order the inputs using an array containing the
    indexes they should appear in """
    def compute(self):
        vol = self.getInputFromPort("Signals")
        inds = self.getInputFromPort("Indexes")

        sh = vol.get_shape()
        vol = vol.get_array()
        inds = inds.get_array()
        out_ar = [vol[inds[0]]]
        for i in xrange(sh[0] - 1):
            i += 1
            try:
                out_ar = numpy.vstack((out_ar, [vol[inds[i]]]))
            except:
                pass

        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Set'))
        reg.add_input_port(cls, "Indexes", (NDArray, 'Sorted Index Set'))
        reg.add_output_port(cls, "Output", (NDArray, 'Sorted Signal Set'))

class OrderByCorrelation(EnsembleModule, Module):
    """ Order the inputs using the correlations between a given
    input index and all other slices in the volume """
    def append_slice(self, vol, sl):
        vol = numpy.vstack((vol, [sl]))
        return vol

    def append_cor(self, cor, sl_cor):
        cor.append(sl_cor)
        return cor
    
    def prepend_slice(self, vol, sl):
        vol = numpy.vstack(([sl], vol))
        return vol

    def prepend_cor(self, cor, sl_cor):
        cor.insert(0, sl_cor)
        return cor
    
    def find_max(self, a):
        f = a.max()
        sh = a.shape
        b = a.flatten()
        ind = b.argmax()
        row = int(ind/sh[1])
        col = ind - row * sh[1]
        return (row, col, f)
        
    def compute(self):
        ts = time.time()
        vol = self.getInputFromPort("Signals")
        ind = self.getInputFromPort("Key Slice")
        if self.hasInputFromPort("Normalize"):
            self.normalize = self.getInputFromPort("Normalize")
        else:
            self.normalize = False

        vol_ar = vol.get_array()
        if self.normalize:
            for i in range(vol_ar.shape[0]):
                sl = vol_ar[i]
                sl = sl - sl.min()
                sl = sl / sl.max()
                vol_ar[i] = sl

        pos = self.forceGetInputFromPort("Key Position")
            
        key_slice = vol_ar[ind]
        (r,c) = key_slice.shape
        key_fft = fftpack.fftn(key_slice)
        key_sq = key_slice * key_slice
        norm = key_sq.sum()
        norm = numpy.sqrt(norm)

        num_slices = vol.get_shape()[0]
        num_elements = key_slice.size
        cor = []
        for i in xrange(num_slices):
            cur_slice = vol_ar[i]
            cur_sq = cur_slice * cur_slice
            cur_norm = cur_sq.sum()
            cur_norm = numpy.sqrt(cur_norm)
            
            cur_fft = fftpack.fftn(cur_slice)
            cur_fft = cur_fft.conjugate()

            cur_max = cur_slice.max()
            prod_slice = key_fft * cur_fft
            prod_slice = prod_slice / (norm * cur_norm)
            cor_slice = fftpack.ifftn(prod_slice)

            (row,col,val) = self.find_max(cor_slice.real)

            cor.append((val,i,row,col))

        cor.sort(lambda x,y:cmp(y[0],x[0]))
        vol = [key_slice]
        key_slice_out = key_slice
        out_cor_ar = []
        if pos == None:
            app = True
            for i in range(len(cor)):
                sl_cor = cor[i]
                if sl_cor[1] == ind:
                    continue
                sl = vol_ar[sl_cor[1]]
                if app:
                    vol = self.append_slice(vol, sl)
                    out_cor_ar = self.append_cor(out_cor_ar, cor[i][0])
                else:
                    vol = self.prepend_slice(vol, sl)
                    out_cor_ar = self.prepend_cor(out_cor_ar, cor[i][0])
                
                app = (app != True)
        else:
            for i in range(len(cor)):
                sl_cor = cor[i]
                sl = vol_ar[sl_cor[1]]
                vol = self.append_slice(vol, sl)
                out_cor_ar = self.append_cor(out_cor_ar, cor[i][0])

        elapsed = time.time() - ts
#        elapsed *= 1000000.
        print "took: ", elapsed
        out_vol = NDArray()

        out_vol.set_array(vol/vol.max())
        out_cor = NDArray()
        out_cor_ar = numpy.array(out_cor_ar)
        out_cor.set_array(out_cor_ar / out_cor_ar.max())

        out_key = NDArray()
        out_key.set_array(key_slice_out)
        self.setResult("Output Key Slice", out_key)
        self.setResult("Output Volume", out_vol)
        self.setResult("Output Correlation", out_cor)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Volume'))
        reg.add_input_port(cls, "Key Slice", (basic.Integer, 'Key Slice Index'))
        reg.add_input_port(cls, "Normalize", (basic.Boolean, 'Normalize Slice Power'))
        reg.add_input_port(cls, "Key Position", (basic.Integer, 'Key Slice Position'))
        reg.add_output_port(cls, "Output Volume", (NDArray, 'Sorted Signal Volume'))
        reg.add_output_port(cls, "Output Correlation", (NDArray, 'Sorted Correlation Array'))
        reg.add_output_port(cls, "Output Key Slice", (NDArray, 'Key Slice'))
        
class OrderByProgressiveCorrelation(EnsembleModule, Module):
    def find_max(self, a):
        f = a.max()
        sh = a.shape
        b = a.flatten()
        ind = b.argmax()
        row = int(ind/sh[1])
        col = ind - row * sh[1]
        return (row, col, f)
        
    def correlate(self, plane, ref_im):
        (r,c) = ref_im.shape
        key_fft = fftpack.fftn(ref_im)
        key_sq = ref_im * ref_im
        norm = key_sq.sum()
        norm = numpy.sqrt(norm)

        cur_slice = plane
        cur_sq = cur_slice * cur_slice
        cur_norm = cur_sq.sum()
        cur_norm = numpy.sqrt(cur_norm)
        
        cur_fft = fftpack.fftn(cur_slice)
        cur_fft = cur_fft.conjugate()

        cur_max = cur_slice.max()
        prod_slice = key_fft * cur_fft
        prod_slice = prod_slice / (norm * cur_norm)
        cor_slice = fftpack.ifftn(prod_slice)
        
        (row,col,val) = self.find_max(cor_slice.real)

        return val
    
    def compute(self):
        vol = self.getInputFromPort("Signals").get_array()
        ind = self.getInputFromPort("Key Slice")
        normalize = self.forceGetInputFromPort("Normalize")

        if normalize:
            for i in range(vol.shape[0]):
                sl = vol[i]
                sl = sl - sl.min()
                sl = sl / sl.max()
                vol[i] = sl
            
        tmp_vol = copy.copy(vol)

        key_slice = vol[ind]
        vol_ind = numpy.arange(vol.shape[0]).tolist()

        out_ar = numpy.zeros(vol.shape)
        out_ar[0,:,:] = key_slice
        tmp_vol[ind,:,:] = 0.0

        tmp_size = 1
        cors_out = [self.correlate(key_slice,key_slice)]
        print "key cor = ", cors_out[0]
        while tmp_size < tmp_vol.shape[0]:
            ts = time.time()
            cors = []
            print "output size is currently:  ", tmp_size, 
            for i in range(tmp_vol.shape[0]):
                plane = tmp_vol[i]
                if plane.min() == 0. and plane.max() == 0.:
                    continue

                cor = self.correlate(plane,out_ar[tmp_size-1,:,:])
                cors.append((cor,i))

            cors.sort(lambda x,y:cmp(y[0],x[0]))
            (max_cor,ind) = cors[0]
            print "\tcor = ", max_cor, ind
            cors_out.append(max_cor)
            out_ar[tmp_size,:,:] = vol[ind]
            tmp_vol[ind,:,:] = 0.
            tmp_size += 1
            elapsed = time.time() - ts
#            elapsed *= 1000000.
            print "\tCorrelation took: ", elapsed

        cor_ar = numpy.array(cors_out)
        cor_ar /= cor_ar.max()
        out = NDArray()
        out.set_array(out_ar)
        out_cor = NDArray()
        out_cor.set_array(cor_ar)

        self.setResult("Output Signals", out)
        self.setResult("Output Correlations", out_cor)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Time Frequency Planes'))
        reg.add_input_port(cls, "Key Slice", (basic.Integer, 'Key Slice'))
        reg.add_input_port(cls, "Normalize", (basic.Boolean, 'Normalize each plane'), True)
        reg.add_output_port(cls, "Output Signals", (NDArray, 'Output Time Frequency Planes'))
        reg.add_output_port(cls, "Output Correlations", (NDArray, 'Output Correlations'))
