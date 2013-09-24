import core.modules
from core.modules.vistrails_module import Module, ModuleError

import numpy
from Array import *

class ArrayAccess(object):
    my_namespace = "numpy|array|access"

class GetShape(Module, ArrayAccess):
    """ Get the size of each dimension of an N-dimensional array"""
    def compute(self):
        a = self.get_input("Array")
        sh = a.get_shape()
        dims = len(sh)
        for i in xrange(dims):
            pname = "dim" + str(i)
            self.set_output(pname, sh[i])

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
        a = self.get_input("Array")
        b = a.get_reals()
        out = NDArray()
        out.set_array(b)
        self.set_output("Real Component", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Reals", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Real Component", (NDArray, 'Real Components'))
    

class GetImaginaries(Module, ArrayAccess):
    """ Get the imaginary component of a complex array """
    def compute(self):
        a = self.get_input("Array")
        b = a.get_imaginary()
        out = NDArray()
        out.set_array(b)
        self.set_output("Im Component", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Imaginaries", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Im Component", (NDArray, 'Imaginary Components'))

class GetMax(Module, ArrayAccess):
    """ Get the maximal value from an array """
    def compute(self):
        a = self.get_input("Array")
        self.set_output("Max", float(a.get_max()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Max", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Max", (basic.Float, 'Max Value'))

class GetMean(Module, ArrayAccess):
    """ Get the mean value of an array """
    def compute(self):
        a = self.get_input("Array")
        axis = self.force_get_input("Axis")
        out = NDArray()
        out.set_array(numpy.array(a.get_mean(axis)))
        self.set_output("Mean", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Mean", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Axis", (basic.Integer, 'Axis'), True)
        reg.add_output_port(cls, "Mean", (NDArray, 'Mean Value'))

class GetMin(Module, ArrayAccess):
    """ Get the smallest value in an array """
    def compute(self):
        a = self.get_input("Array")
        self.set_output("Min", float(a.get_min()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Min", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Min", (basic.Float, 'Min Value'))

class GetDiagonal(Module, ArrayAccess):
    """ Get an array representing the values on the diagonal of the input array """
    def compute(self):
        a = self.get_input("Array")
        out = NDArray()
        out.set_array(a.get_diagonal())
        self.set_output("Diagonal", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Diagonal", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Diagonal", (NDArray, 'Diagonal Elements'))

class GetArrayAsType(Module, ArrayAccess):
    """ Cast the array to the given type """
    def compute(self):
        a = self.get_input("Array")
        t = self.get_input("Type")
        t.setValue("0")
        out = NDArray()
        out.set_array(a.get_array_as_type(type(t.value)))
        self.set_output("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Cast Array", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Type", (basic.Constant, 'Cast To Type'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Array'))

class GetConjugate(Module, ArrayAccess):
    """ Get the complex conjugate of the input array """
    def compute(self):
        a = self.get_input("Array")
        out = NDArray()
        out.set_array(a.get_conjugate())
        self.set_output("Conjugate", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Conjugate", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Conjugate", (NDArray, 'Complex Conjugate'))

class GetFlattenedArray(Module, ArrayAccess):
    """ Get a flattened representation of the input array"""
    def compute(self):
        a = self.get_input("Array")
        out = NDArray()
        out.set_array(a.get_flattened())
        self.set_output("Flat Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Flattened Array", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Flat Array", (NDArray, 'Output Vector'))

class GetField(Module, ArrayAccess):
    """ Get a field from an array given the output datatype and offset into the array"""
    def compute(self):
        a = self.get_input("Array")
        dt = self.get_input("DType")
        dt.setValue("0")
        o = self.get_input("Offset")
        out = NDArray()
        out.set_array(a.get_field(type(dt.value), o))
        self.set_output("Field", out)

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
        a = self.get_input("Array")
        self.set_output("Item", float(a.get_item()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="To Scalar", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Item", (basic.Float, 'Item'))

class GetMemoryFootprint(Module, ArrayAccess):
    """ Return the amount of system memory consumed by the array """
    def compute(self):
        a = self.get_input("Array")
        self.set_output("Size", int(a.get_mem_size()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Memory Size", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'InputArray'))
        reg.add_output_port(cls, "Size", (basic.Integer, 'Memory Size'))

class GetArrayRank(Module, ArrayAccess):
    """ Get the rank of the array """
    def compute(self):
        a = self.get_input("Array")
        self.set_output("Rank", int(a.get_num_dims()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Array Rank", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Rank", (basic.Integer, 'Array Rank'))

class GetNonZeroEntries(Module, ArrayAccess):
    """ Get an array consisting of the indices to all non-zero entries of the input array."""
    def compute(self):
        a = self.get_input("Array")
        out = NDArray()
        out.set_array(a.get_nonzero_indices())
        self.set_output("Entries", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Non-Zero Entries", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Entreis", (NDArray, 'Output Array'))

class GetArraySize(Module, ArrayAccess):
    """ Get the number of entries in an array """
    def compute(self):
        a = self.get_input("Array")
        self.set_output("Size", a.get_num_elements())

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Array Size", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Size", (basic.Integer, 'Number of Elements'))

class GetTranspose(Module, ArrayAccess):
    """ Get the transpose of the array """
    def compute(self):
        a = self.get_input("Array")
        out = NDArray()
        out.set_array(a.get_transpose())
        self.set_output("Transpose", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Get Transpose", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Transpose", (NDArray, 'Transposed Array'))

class GetRowRange(Module, ArrayAccess):
    """ Get a set of rows from the input array """
    def compute(self):
        a = self.get_input("Array")
        s = self.get_input("Start")
        e = self.get_input("End")
        out = NDArray()
        if self.force_get_input("One Indexed"):
            s = s-1
            e = e-1

        out.set_array(a.get_row_range(s, e))
        new_index = 0
        for i in range(s,e+1):
            out.set_row_name(a.get_name(i), new_index)
            new_index += 1

        out.set_domain_name(a.get_domain_name())
        out.set_range_name(a.get_range_name())
        self.set_output("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Start", (basic.Integer, 'Start Index'))
        reg.add_input_port(cls, "End", (basic.Integer, 'End Index'))
        reg.add_input_port(cls, "One Indexed", (basic.Boolean, 'One Indexed'), True)
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))


class GetRows(Module, ArrayAccess):
    """ Get a set of rows from the input array defined by a list of indexes """
    def compute(self):
        l = self.force_get_input("Index List")
        if l == None:
            l = self.forceGetInputListFromPort("Indexes")

        if l == None or len(l) == 0:
            raise ModuleError("No indexes provided")

        l.sort()
        inp = self.get_input("Array")
        in_ar = inp.get_array()
        out_ar = in_ar[l[0],::]
        for i in range(1,len(l)):
            out_ar = numpy.vstack((out_ar,in_ar[i,::]))

        out = NDArray()
        for i in range(out_ar.shape[0]):
            out.set_row_name(inp.get_row_name(l[i]), i)
            
        out.set_array(out_ar)
        out_order = NDArray()
        out_order.set_array(numpy.array(l))
        self.set_output("Output Array", out)
        self.set_output("Output Order", out_order)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Indexes", (basic.Integer, 'Index'))
        reg.add_input_port(cls, "Index List", (basic.List, 'Index List'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        reg.add_output_port(cls, "Output Order", (NDArray, 'Output Ordering'))

class GetColumnRange(Module, ArrayAccess):
    """ Get a set of columns from the input array """
    def compute(self):
        a = self.get_input("Array")
        s = self.get_input("Start")
        e = self.get_input("End")
        out = NDArray()
        out.set_array(a.get_col_range(s, e-1))
        self.set_output("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Start", (basic.Integer, 'Start Index'))
        reg.add_input_port(cls, "End", (basic.Integer, 'End Index'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

