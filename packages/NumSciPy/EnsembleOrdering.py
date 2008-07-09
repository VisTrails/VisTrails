import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from Array import *

class EnsembleModule(object):
    my_namespace = 'scipy|signals|ensembles'


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
        import scipy
        from scipy import fftpack
        
        vol = self.getInputFromPort("Signals")
        ind = self.getInputFromPort("Key Slice")
        if self.hasInputFromPort("Normalize"):
            self.normalize = self.getInputFromPort("Normalize")
        else:
            self.normalize = False
            
        vol_ar = vol.get_array()

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
        out_cor_ar = []
        app = True
        for i in xrange(len(cor)):
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

        out_vol = NDArray()

        out_vol.set_array(vol)
        out_cor = NDArray()
        out_cor.set_array(numpy.array(out_cor_ar))
        
        self.setResult("Output Volume", out_vol)
        self.setResult("Output Correlation", out_cor)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Volume'))
        reg.add_input_port(cls, "Key Slice", (basic.Integer, 'Key Slice Index'))
        reg.add_input_port(cls, "Normalize", (basic.Boolean, 'Normalize Slice Power'))
        reg.add_output_port(cls, "Output Volume", (NDArray, 'Sorted Signal Volume'))
        reg.add_output_port(cls, "Output Correlation", (NDArray, 'Sorted Correlation Array'))

class OrderByProgressiveCorrelation(EnsembleModule, Module):
    class Correlate(object):
        def __init__(self, v, i, x, y):
            self.cor = v
            self.ind = i
            self.x = x
            self.y = y
            
    def find_max(self, a):
        f = a.max()
        sh = a.shape
        b = a.flatten()
        ind = b.argmax()
        row = int(ind/sh[1])
        col = ind - row * sh[1]
        return (row, col, f)
        
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

    def correlate(self, ref_im, im_ind, im_vol):
        (r,c) = ref_im.shape
        key_fft = fftpack.fftn(ref_im)
        key_sq = ref_im * ref_im
        norm = key_sq.sum()
        norm = numpy.sqrt(norm)

        num_slices = len(im_ind)
        cor = []
        for i in xrange(num_slices):
            cur_slice = im_vol[im_ind[i]]
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

            c = Correlate(val, im_ind[i], row, col)
            cor.append(c)

        cor.sort(lambda x,y:cmp(y.cor,x.cor))
        return cor
    
    def compute(self):
        import scipy
        from scipy import fftpack
        
        vol = self.getInputFromPort("Signals")
        ind = self.getInputFromPort("Key Slice")

        key_slice = vol.get_array()[ind]
        vol_ind = numpy.arange(vol.get_shape()[0]).tolist()
        vol_im_ar = vol.get_array()
        # The correlates object is a list of indices and correlations
        # sorted.
        correlates = self.correlate(key_slice, vol_ind, vol_im_ar)
        out_vol = [vol_im_ar[ind]]
        
