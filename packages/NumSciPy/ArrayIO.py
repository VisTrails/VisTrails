import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import numpy
import scipy
import scipy.io
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

    def num_bytes(self, dtype):
        if self.type.has_key(dtype):
            return self.type[dtype]
        else:
            print "Cannot find " + dtype + " in type library."
            print "Assuming float32 for dtype"
            return 'f'
        
    def read_raw(self, fn, sizes, dtype, little_end=True):
        try:
#            fn = "/scratch/eranders/data/joao/foot/" + fn
            fid = open(fn, 'rb')
            print 'fid open'
            dt = self.num_bytes(dtype)
            ndim = len(sizes)
            num_el = 1
            for i in xrange(ndim):
                num_el *= sizes[i]

            if little_end:
                data = scipy.io.fread(fid, num_el, dt, 'd')
            else:
                data = scipy.io.fread(fid, num_el, dt, 'd', byteswap=1)
            fid.close()
            print 'fid closed'
            data.shape = sizes
            return data
        except:
            raise ModuleError("Could not read .raw file!")
            
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
        import pylab
        fn = self.getInputFromPort("Filename")
        ar = pylab.imread(fn)
        out = NDArray()
        out.set_array(ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ReadRAW(ArrayIOModule, Module):    
    """ Load a .raw file into a Numpy Array.  The .raw files are
    assumed to be in the volvis format: http://www.volvis.org """
    def __init__(self):
        Module.__init__(self)
        self.helper = NrrdHelper()
        
    def compute(self):
        fn = self.getInputFromPort("Filename")
        sizes = self.getInputListFromPort("Sizes")
        dtype = self.getInputFromPort("DataType")
        ar = self.helper.read_raw(fn, sizes, dtype)
        out = NDArray()
        out.set_array(ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Sizes", (basic.Integer, 'Dimension Sizes'))
        reg.add_input_port(cls, "DataType", (basic.String, 'Datatype'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ReadNHDR(ArrayIOModule, Module):
    """ Load a .nhdr/.raw pair into a Numpy Array. """
    def __init__(self):
        Module.__init__(self)
        self.helper = NrrdHelper()

    def compute(self):
        fn = self.getInputFromPort("Filename")
        ar = self.helper.read_nhdr(fn)
        out = NDArray()
        out.set_array(ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
