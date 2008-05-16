import core.modules
from core.modules.vistrails_module import Module, ModuleError

import numpy
from Array import *

class ArrayAccess(object):
    my_namespace = "numpy|array|access"

class GetShape(Module, ArrayAccess):
    """ Get the size of each dimension of an N-dimensional array"""
    def compute(self):
        a = self.getInputFromPort("Array")
        sh = a.get_shape()
        dims = len(sh)
        for i in xrange(dims):
            pname = "dim" + str(i)
            self.setResult(pname, sh[i])

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Array Shape", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "dim0", (basic.Integer, 'Dim 0 Size'))
        reg.add_output_port(cls, "dim1", (basic.Integer, 'Dim 1 Size'))
        reg.add_output_port(cls, "dim2", (basic.Integer, 'Dim 2 Size'))
        reg.add_output_port(cls, "dim3", (basic.Integer, 'Dim 3 Size'), True)
        reg.add_output_port(cls, "dim4", (basic.Integer, 'Dim 4 Size'), True)
        reg.add_output_port(cls, "dim5", (basic.Integer, 'Dim 5 Size'), True)
        reg.add_output_port(cls, "dim6", (basic.Integer, 'Dim 6 Size'), True)
        reg.add_output_port(cls, "dim7", (basic.Integer, 'Dim 7 Size'), True)

class GetReals(Module, ArrayAccess):
    """ Get the real component of a complex array """
    def compute(self):
        a = self.getInputFromPort("Array")
        b = a.get_reals()
        out = NDArray()
        out.set_array(b)
        self.setResult("Real Component", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Reals", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Real Component", (NDArray, 'Real Components'))
    

class GetImaginaries(Module, ArrayAccess):
    """ Get the imaginary component of a complex array """
    def compute(self):
        a = self.getInputFromPort("Array")
        b = a.get_imaginary()
        out = NDArray()
        out.set_array(b)
        self.setResult("Im Component", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Imaginaries", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Im Component", (NDArray, 'Imaginary Components'))

class GetMax(Module, ArrayAccess):
    """ Get the maximal value from an array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Max", float(a.get_max()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Max", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Max", (basic.Float, 'Max Value'))

class GetMean(Module, ArrayAccess):
    """ Get the mean value of an array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Mean", float(a.get_mean()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Mean", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Mean", (basic.Float, 'Mean Value'))

class GetMin(Module, ArrayAccess):
    """ Get the smallest value in an array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Min", float(a.get_min()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Min", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Min", (basic.Float, 'Min Value'))

class GetDiagonal(Module, ArrayAccess):
    """ Get an array representing the values on the diagonal of the input array """
    def compute(self):
        a = self.getInputFromPort("Array")
        out = NDArray()
        out.set_array(a.get_diagonal())
        self.setResult("Diagonal", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Diagonal", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Diagonal", (NDArray, 'Diagonal Elements'))

class GetArrayAsType(Module, ArrayAccess):
    """ Cast the array to the given type """
    def compute(self):
        a = self.getInputFromPort("Array")
        t = self.getInputFromPort("Type")
        t.setValue("0")
        out = NDArray()
        out.set_array(a.get_array_as_type(type(t.value)))
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Cast Array", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Type", (basic.Constant, 'Cast To Type'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Array'))

class GetConjugate(Module, ArrayAccess):
    """ Get the complex conjugate of the input array """
    def compute(self):
        a = self.getInputFromPort("Array")
        out = NDArray()
        out.set_array(a.get_conjugate())
        self.setResult("Conjugate", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Conjugate", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Conjugate", (NDArray, 'Complex Conjugate'))

class GetFlattenedArray(Module, ArrayAccess):
    """ Get a flattened representation of the input array"""
    def compute(self):
        a = self.getInputFromPort("Array")
        out = NDArray()
        out.set_array(a.get_flattened())
        self.setResult("Flat Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Flattened Array", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Flat Array", (NDArray, 'Output Vector'))

class GetField(Module, ArrayAccess):
    """ Get a field from an array given the output datatype and offset into the array"""
    def compute(self):
        a = self.getInputFromPort("Array")
        dt = self.getInputFromPort("DType")
        dt.setValue("0")
        o = self.getInputFromPort("Offset")
        out = NDArray()
        out.set_array(a.get_field(type(dt.value), o))
        self.setResult("Field", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Field", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "DType", (basic.Constant, 'Output Type'))
        reg.add_input_port(cls, "Offset", (basic.Integer, 'Offset'))
        reg.add_output_port(cls, "Field", (NDArray, 'Output Field'))

class ToScalar(Module, ArrayAccess):
    """ Return an array of size 1 to a scalar """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Item", float(a.get_item()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="To Scalar", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Item", (basic.Float, 'Item'))

class GetMemoryFootprint(Module, ArrayAccess):
    """ Return the amount of system memory consumed by the array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Size", int(a.get_mem_size()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Memory Size", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'InputArray'))
        reg.add_output_port(cls, "Size", (basic.Integer, 'Memory Size'))

class GetArrayRank(Module, ArrayAccess):
    """ Get the rank of the array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Rank", int(a.get_num_dims()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Array Rank", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Rank", (basic.Integer, 'Array Rank'))

class GetNonZeroEntries(Module, ArrayAccess):
    """ Get an array consisting of the indices to all non-zero entries of the input array."""
    def compute(self):
        a = self.getInputFromPort("Array")
        out = NDArray()
        out.set_array(a.get_nonzero_indices())
        self.setResult("Entries", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Non-Zero Entries", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Entreis", (NDArray, 'Output Array'))

class GetArraySize(Module, ArrayAccess):
    """ Get the number of entries in an array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Size", a.get_num_elements())

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Array Size", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Size", (basic.Integer, 'Number of Elements'))

class GetTranspose(Module, ArrayAccess):
    """ Get the transpose of the array """
    def compute(self):
        a = self.getInputFromPort("Array")
        out = NDArray()
        out.set_array(a.get_transpose())
        self.setResult("Transpose", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Transpose", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Transpose", (NDArray, 'Transposed Array'))

class GetRowRange(Module, ArrayAccess):
    """ Get a set of rows from the input array """
    def compute(self):
        a = self.getInputFromPort("Array")
        s = self.getInputFromPort("Start")
        e = self.getInputFromPort("End")
        out = NDArray()
        out.set_array(a.get_row_range(s, e))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Start", (basic.Integer, 'Start Index'))
        reg.add_input_port(cls, "End", (basic.Integer, 'End Index'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class GetColumnRange(Module, ArrayAccess):
    """ Get a set of columns from the input array """
    def compute(self):
        a = self.getInputFromPort("Array")
        s = self.getInputFromPort("Start")
        e = self.getInputFromPort("End")
        out = NDArray()
        out.set_array(a.get_col_range(s, e-1))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Start", (basic.Integer, 'Start Index'))
        reg.add_input_port(cls, "End", (basic.Integer, 'End Index'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
