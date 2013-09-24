import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import numpy
import scipy
import scipy.io
import pylab
from Array import *
from Matrix import *

class ArrayIOModule(object):
    my_namespace = 'numpy|io'

class NrrdHelper(object):
    def __init__(self):
        self.type = {}
        self.type['float32'] = 'f'
        self.type['float'] = 'f'
        self.type['float64'] = 'd'
        self.type['double'] = 'd'
        self.type['int'] = 'i'
        self.type['int16'] = 'i'
        self.type['long'] = 'l'
        self.type['int32'] = 'l'
        self.type['unsigned short'] = 's'
        self.type['unsigned char'] = 'c'

        self.nrrd_type = {}
        self.nrrd_type['float'] = 'float'
        self.nrrd_type['float32'] = 'float'
        self.nrrd_type['float64'] = 'double'
        self.nrrd_type['double'] = 'double'
        self.nrrd_type['int64'] = 'long'
        self.nrrd_type['long'] = 'long'
        self.nrrd_type['int32'] = 'int'
        self.nrrd_type['int16'] = 'short'
        self.nrrd_type['int8'] = 'uchar'
        self.nrrd_type['unsigned short'] = 'short'

        self.little_endian = True
        
    def num_bytes(self, dtype):
        if self.type.has_key(dtype):
            return self.type[dtype]
        else:
            print "Cannot find " + dtype + " in type library."
            print "Assuming float32 for dtype"
            return 'f'

    def get_nrrd_type(self, data):
        dt = data.dtype.name
        if self.nrrd_type.has_key(dt):
            return self.nrrd_type[dt]
        else:
            print "Cannot find " + dt + " in type library."
            print "Assuming float32 for dtype"
            return 'float'
        
    def read_raw(self, fn, sizes, dtype, little_end=True):
        try:
            fid = open(fn, 'rb')
            dt = self.num_bytes(dtype)
            ndim = len(sizes)
            num_el = 1
            for i in xrange(ndim):
                num_el *= sizes[i]

            if little_end:
                dt = '<'+dt
            else:
                dt = '>'+dt

            data = numpy.fromfile(fn, dt)
            fid.close()
            data.shape = sizes
            return data
        except:
            raise ModuleError("Could not read .raw file!")

    def write_raw(self, fn, data):
        try:
            fid = open(fn, 'wb')
            scipy.io.fwrite(fid, data.size, data)
            fid.close()
        except:
            raise ModuleError("Could not write .raw file!")

    def write_nhdr(self, fn, data):
        import os
        l = fn.split('/')
        name = l[len(l)-1]
        base = name.split('.')[0]
        rawname = base + '.raw'
        rawpath = fn.rstrip(name)
        rawpath += rawname
        self.write_raw(rawpath, data)
        cmd = 'unu make -h -t '
        cmd += self.get_nrrd_type(data) + ' '
        cmd += '-e raw -i ' + rawname + ' -s '
        sh = data.shape
        ndims = len(sh)
        for i in xrange(ndims):
            cmd += str(sh[i]) + ' '

        cmd += '-o ' + fn
        try:
            os.system(cmd)
        except:
            raise ModuleError("Could not write NHDR file.  Please make sure the Teem and UNU utilities are on your path.")
        
    def read_nhdr(self, fn):
        import os.path
        try:
            fid = open(fn, 'r')
            for line in fid:
                if line.split(':')[0] == 'type':
                    self.dtype = line.split(':')[1].strip()
                if line.split(':')[0] == 'dimension':
                    self.ndim = int(line.split(':')[1].strip())
                if line.split(':')[0] == 'sizes':
                    s = line.split(':')[1].strip().split(' ')
                    self.sizes = []
                    for l in s:
                        self.sizes.append(int(l))
                if line.split(':')[0] == 'endian':
                    if line.split(':')[1].strip() == 'little':
                        self.little_endian = True
                    else:
                        self.little_endian = False
                if line.split(':')[0] == 'data file':
                    self.fn = line.split(':')[1].strip()
                if line.split(':')[0] == 'encoding':
                    self.encoding = line.split(':')[1].strip()
            fid.close()
        except:
            raise ModuleError("Could not read .nhdr file!")

        if self.encoding == 'raw':
            curpath = os.getcwd()
            npath = os.path.dirname(fn)
            os.chdir(npath)
            data = self.read_raw(self.fn, self.sizes, self.dtype, little_end=self.little_endian)
            os.chdir(curpath)
            return data

        raise ModuleError(".nhdr file contains file not in .raw format!")

class ReadPNG(ArrayIOModule, Module):
    """ Load a .png type image into a Numpy Array. """
    def compute(self):
        fn = self.get_input("Filename")
        ar = pylab.imread(fn)
        out = NDArray()
        out.set_array(ar)
        self.set_output("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class WritePNG(ArrayIOModule, Module):
    """ Write a .png type image from a Numpy Array. """
    def compute(self):
        fn = self.get_input("Filename")
        ar = self.get_input("Image")
        minv = self.force_get_input("Min")
        maxv = self.force_get_input("Max")
        if minv == None:
            minv = 0
        if maxv == None:
            maxv = 255
        da_ar = ar.get_array().squeeze()
        im = scipy.misc.toimage(da_ar, cmin=minv, cmax=maxv).save(fn)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Min", (basic.Integer, 'Min Value'))
        reg.add_input_port(cls, "Max", (basic.Integer, 'Max Value'))
        reg.add_input_port(cls, "Image", (NDArray, 'Image To Write'))

class ReadRAW(ArrayIOModule, Module):    
    """ Load a .raw file into a Numpy Array.  The .raw files are
    assumed to be in the volvis format: http://www.volvis.org """
    def __init__(self):
        Module.__init__(self)
        self.helper = NrrdHelper()
        
    def compute(self):
        fn = self.get_input("Filename")
        sizes = self.getInputListFromPort("Sizes")
        dtype = self.get_input("DataType")
        ar = self.helper.read_raw(fn, sizes, dtype)
        out = NDArray()
        out.set_array(ar)
        self.set_output("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Sizes", (basic.Integer, 'Dimension Sizes'))
        reg.add_input_port(cls, "DataType", (basic.String, 'Datatype'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class WriteRAW(ArrayIOModule, Module):
    """ Write a .raw file from a Numpy Array. """
    def __init__(self):
        Module.__init__(self)
        self.helper = NrrdHeler()

    def compute(self):
        fn = self.get_input("Filename")
        ar = self.get_input("Array").get_array()
        self.helper.write_raw(fn,ar)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        
class ReadNHDR(ArrayIOModule, Module):
    """ Load a .nhdr/.raw pair into a Numpy Array. """
    def __init__(self):
        Module.__init__(self)
        self.helper = NrrdHelper()

    def compute(self):
        fn = ''
        if self.has_input("File"):
            fn = self.get_input("File").name
        else:
            fn = self.get_input("Filename")
        ar = self.helper.read_nhdr(fn)
        out = NDArray()
        out.set_array(ar)
        self.set_output("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "File", (basic.File, 'File'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
class WriteNHDR(ArrayIOModule, Module):
    """ Write a .nhdr/.raw pair from a Numpy Array """
    def __init__(self):
        Module.__init__(self)
        self.helper = NrrdHelper()

    def compute(self):
        fn = self.get_input("Filename")
        ar = self.get_input("Array").get_array()
        self.helper.write_nhdr(fn,ar)
        self.set_output("Filename Out", fn)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Filename Out", (basic.String, 'Output Filename'))

class ReadStatisticalSummary(ArrayIOModule, Module):
    """
    Documentation
    """
    def compute(self):
        fn = ''
        if self.has_input("File"):
            fn = self.get_input("File").name
        else:
            fn = self.get_input("Filename")

        if self.force_get_input("Allocate Aggregated Array"):
            alloc_array = True
        else:
            alloc_array = False

        fid = open(fn, 'r')
        dims = fid.readline().strip().split()
        n_pts = int(dims[0])
        n_bins = int(dims[1])

        min_ar = numpy.zeros(n_pts)
        lq_ar = numpy.zeros(n_pts)
        med_ar = numpy.zeros(n_pts)
        hq_ar = numpy.zeros(n_pts)
        max_ar = numpy.zeros(n_pts)
        mode_ar = numpy.zeros((n_pts, 4))
        hist_ar = numpy.zeros((n_pts, n_bins))
        if alloc_array:
            ag_ar = numpy.zeros((n_pts, 5+4+n_bins))
        for i in xrange(n_pts):
            l = fid.readline().strip().split()
            min_ar[i] = float(l[0])
            lq_ar[i] = float(l[1])
            med_ar[i] = float(l[2])
            hq_ar[i] = float(l[3])
            max_ar[i] = float(l[4])
            for j in xrange(4):
                mode_ar[i, j] = float(l[5+j])

            for b in xrange(n_bins):
                hist_ar[i, b] = float(l[9+b])

            if alloc_array:
                vals = numpy.array(l).astype('float')
                ag_ar[i,:] += vals

        fid.close()
        
        min_ar_out = NDArray()
        min_ar_out.set_array(min_ar)
        self.set_output("Min Array", min_ar_out)
        
        lq_ar_out = NDArray()
        lq_ar_out.set_array(lq_ar)
        self.set_output("Lower Quartile Array", lq_ar_out)
        
        med_ar_out = NDArray()
        med_ar_out.set_array(med_ar)
        self.set_output("Median Array", med_ar_out)
        
        hq_ar_out = NDArray()
        hq_ar_out.set_array(hq_ar)
        self.set_output("Upper Quartile Array", hq_ar_out)
        
        max_ar_out = NDArray()
        max_ar_out.set_array(max_ar)
        self.set_output("Max Array", max_ar_out)
        
        mode_ar_out = NDArray()
        mode_ar_out.set_array(mode_ar)
        self.set_output("Mode Array", mode_ar_out)
        
        hist_ar_out = NDArray()
        hist_ar_out.set_array(hist_ar)
        self.set_output("Histogram Array", hist_ar_out)

        if alloc_array:
            ag_ar_out = NDArray()
            ag_ar_out.set_array(ag_ar)
            self.set_output("Aggregated Array", ag_ar_out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "File", (basic.File, 'File'))
        reg.add_input_port(cls, "Allocate Aggregated Array", (basic.Boolean, 'Allocate Extra Space for Aggregated Array'), True)
        reg.add_output_port(cls, "Min Array", (NDArray, 'Minima Array'))
        reg.add_output_port(cls, "Lower Quartile Array", (NDArray, 'Lower Quartile Array'))
        reg.add_output_port(cls, "Median Array", (NDArray, 'Median Array'))
        reg.add_output_port(cls, "Upper Quartile Array", (NDArray, 'Upper Quartile Array'))
        reg.add_output_port(cls, "Max Array", (NDArray, 'Maxima Array'))
        reg.add_output_port(cls, "Mode Array", (NDArray, 'Mode Array'))
        reg.add_output_port(cls, "Histogram Array", (NDArray, 'Histogram Array'))
        reg.add_output_port(cls, "Aggregated Array", (NDArray, 'Aggregated Array'), True)
