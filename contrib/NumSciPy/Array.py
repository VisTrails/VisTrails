import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

import numpy

class ArrayModule(object):
    my_namespace = 'numpy|array'

class NDArray(Module, ArrayModule):
    """ Container class for the numpy.ndarray class """
    def __init__(self):
        Module.__init__(self)
        self.array = None
        self.names = {}
        self.general_name = None
        self.domain = ''
        self.range = ''
        
    def get_shape(self):
	return self.array.shape

    # Array Operation 
    def reshape(self, shape):
	self.array.shape = shape
        
    # Array Access
    def get_reals(self):
	return self.array.real

    # Array Access
    def get_imaginary(self):
	return self.array.imag

    # Array Access
    def get_max(self):
	return self.array.max()

    # Array Access
    def get_mean(self, axis=None):
	return self.array.mean(axis=axis)

    # Array Access
    def get_min(self):
	return self.array.min()

    # Array Operation 
    def cumulative_sum(self):
	return self.array.cumsum()

    # Array Access
    def get_arg_min(self):
	return self.array.argmin()

    # Array Access
    def get_arg_max(self):
	return self.array.argmax()

    # Array Access
    def get_diagonal(self):
	return self.array.diagonal()

    # Array Naming
    def get_name(self, row):
        if self.names.has_key(row):
            return self.names[row]
        else:
            return None

    # Array Naming
    def get_general_name(self):
        return self.general_name
    
    # Array Naming
    def set_name(self, name, index=False):
        self.general_name = name
        for i in range(self.array.shape[0]):
            if index:
                self.names[i] = name + " " + str(i+1)
            else:
                self.names[i] = name + " " + str(i)

    # Array Naming
    def set_row_name(self, name, row):
        self.names[row] = name

    # Array Naming
    def clear_names(self):
        self.general_name = None
        self.names = {}

    # Array Naming
    def get_domain_name(self):
        return self.domain

    # Array Naming
    def get_range_name(self):
        return self.range
    
    # Array Naming
    def set_domain_name(self, name):
        self.domain = name

    # Array Naming
    def set_range_name(self, name):
        self.range = name

    # Array Naming
    def clear_domain_name(self):
        self.domain = ''

    # Array Naming
    def clear_range_name(self):
        self.range = ''
        
    # Array Operation 
    def sort_array(self, axis=-1, kind='quicksort', order=None):
	return self.array.argsort(axis, kind, order)

    # Array Access
    def get_array_as_type(self, t):
	return self.array.astype(t)

    # Array Operation 
    def swap_bytes(self, view=False):
	return self.array.byteswap(view)

    # Array Access
    def get_conjugate(self):
	return self.array.conjugate().copy()

    # Array Operation 
    def cumulative_product(self):
	return self.array.cumprod()

    # Array Convert
    def dump_to_file(self, fn):
	self.array.dump(fn)

    # Array Convert
    def dump_to_string(self):
	return self.array.dumps()

    # Array Operation 
    def fill_array(self, val=0.):
	self.array.fill(val)

    # Array Access
    def get_flattened(self):
	return self.array.flatten()

    # Array Access
    def get_field(self, dtype, offset):
	return self.array.getfield(dtype, offset)

    # Array Access
    def get_item(self):
	return self.array.item()

    # Array Access
    def get_mem_size(self):
	return self.array.nbytes

    # Array Access
    def get_num_dims(self):
	return self.array.ndim

    # Array Access
    def get_nonzero_indices(self):
	return self.array.nonzero()

    # Array Operation 
    def put(self, indices, values, mode):
	self.array.put(indices, values, mode)

    # Array Operation 
    def ravel(self):
	return self.array.ravel()

    # Array Operation 
    def resize(self, newshape, refcheck=True, order=False):
	return numpy.resize(self.array, newshape, refcheck=refcheck, order=order)

    # Array Operation 
    def round(self, precision=0, out=None):
	return self.array.round(precision, out)

    # Array Operation 
    def set_field(self, val, dtype, offset):
	self.array.set_field(val, dtype, offset)

    # Array Access
    def get_num_elements(self):
	return self.array.size

    # Array Operation 
    def squeeze(self):
	return self.array.squeeze()

    # Array Operation 
    def get_standard_deviation(self, axis=None, dtype=None, out=None):
	return self.array.std(axis, dtype, out)

    # Array Operation 
    def get_sum(self):
	return self.array.sum()

    # Array Operation 
    def swap_axes(self, axis1, axis2):
	return self.array.swapaxes(axis1, axis2)

    # Array Convert
    def tofile(self, file, sep, format="%s"):
	self.array.tofile(file, sep, format)

    # Array Convert 
    def tolist(self):
	return self.array.tolist()

    # Array Convert
    def tostring(self, order='C'):
	return self.array.tostring(order)

    # Array Operation 
    def get_trace(self, offset, axis1, axis2, dtype=None, out=None):
	return self.array.trace(offset, axis1, axis2, dtype, out)

    # Array Access
    def get_transpose(self):
	return self.array.transpose()

    # Array Operation 
    def get_variance(self, axis=None, dtype=None, out=None):
	return self.array.var(axis, dtype, out)

    # Helper function for assignment
    def get_array(self):
        return self.array

    # Helper function for assignment
    def set_array(self, a):
        self.array = a

    # Array Access
    def get_row_range(self, start, to):
        return self.array[start:to+1,:]

    # Array Access
    def get_col_range(self, start, to):
        return self.array[:, start:to+1]
