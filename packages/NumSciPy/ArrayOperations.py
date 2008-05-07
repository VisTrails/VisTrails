from core.modules.vistrails_module import Module, ModuleError
from Array import *

class ArrayOperationModule(object):
    my_namespace = 'numpy|array|operations'


class ArrayReshape(ArrayOperationModule, Module):
    """ Reshape the input array.  The dimension sizes are presented
    and used to reshape the array.  Please note that the total number
    of elements in the array must remain the same before and after
    reshaping. """
    def compute(self):
	a = self.getInputFromPort("Array")
        dims = self.getInputFromPort("Dims")
        newdims = []
	
	for i in xrange(dims):
	    pname = "dim" + str(i)
	    newdims.append(self.getInputFromPort(pname))

        try:
            a.reshape(tuple(newdims))
        except:
            raise ModuleError("Could not assign new shape.  Be sure the number of elements remains constant")
        
        self.setResult("Array Output", a)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="ReshapeArray", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Dims", (basic.Integer, 'New Dimensionality'))
        reg.add_input_port(cls, "dim0", (basic.Integer, 'Dimension Size'))
        reg.add_input_port(cls, "dim1", (basic.Integer, 'Dimension Size'))
        reg.add_input_port(cls, "dim2", (basic.Integer, 'Dimension Size'))
        reg.add_input_port(cls, "dim3", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim4", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim5", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim6", (basic.Integer, 'Dimension Size'), True)
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))
    
class ArrayCumulativeSum(ArrayOperationModule, Module):
    """ Get the cumulative sum of a given array.  This is returned as a
    flattened array of the same size as the input where each element
    of the array serves as the cumulative sum up until that point."""
    def compute(self):
        a = self.getInputFromPort("Array")
        b = a.cumulative_sum()
        out = NDArray()
        out.set_array(b)
        self.setResult("Array Output", out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))

class ArrayScalarMultiply(ArrayOperationModule, Module):
    """ Multiply the input array with a given scalar """
    def compute(self):
        a = self.getInputFromPort("Array")
        b = self.getInputFromPort("Scalar")
        out = NDArray()
        out.set_array(a.get_array() * b)
        self.setResult("Array Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Scalar", (basic.Float, 'Input Scalar'))
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))

class ArraySort(ArrayOperationModule, Module):
    def __init__(self):
        Module.__init__(self)
        self.axis = -1
        self.kind = 'quicksort'
        self.order = None
        
    """ Sort the input array.  By default, a flattened representation
    of the input array is used as input to a quicksort.  Optional
    inputs are the axis in which to sort on and the type of sort to
    use.

    Sorting algorithms supported:
         quicksort - best average speed, unstable
         mergesort - needs additional working memory, stable
         heapsort  - good worst-case performance, unstable
    """
    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Axis"):
            self.axis = self.getInputFromPort("Axis")
        if self.hasInputFromPort("Sort"):
            self.kind = self.getInputFromPort("Sort")
        if self.hasInputFromPort("Order"):
            self.order = self.getInputFromPort("Order")

        b = a.sort_array(axis=self.axis, kind=self.kind, order=self.order)
        out = NDArray()
        out.set_array(b)
        self.setResult("Sorted Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Axis", (basic.Integer, 'Axis to sort'), True)
        reg.add_input_port(cls, "Sort", (basic.String, 'Sort Algorithm'), True)
        reg.add_input_port(cls, "Order", (basic.Integer, 'Order'),True)
        reg.add_output_port(cls, "Sorted Array", (NDArray, 'Sorted Array'))

class ArrayCumulativeProduct(ArrayOperationModule, Module):
    """ Get the cumulative product of a given array.  This is returned as
    a flattened array of the same size as the input where each element of
    the array serves as the cumulative product up until that point"""
    def compute(self):
        a = self.getInputFromPort("Array")
        b = a.cumulative_product()
        out = NDArray()
        out.set_array(b)
        self.setResult("Array Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))

class ArrayFill(ArrayOperationModule, Module):
    """ Fill the input array with the given value. If no value is given
    it is filled with 0.0"""
    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Value"):
            val = self.getInputFromPort("Value")
        else:
            val = 0.
            
        a.fill_array(val)
        self.setResult("Array Output", a)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Fill Array", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Value", (basic.Float, 'Value'))
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))
        
class ArrayResize(ArrayOperationModule, Module):
    """ Resize the input array.  Unlike the ArrayReshape module,
    the number of elements of the array need not be conserved.
    If the shape is larger than the input array size, repeated
    copies of the input array will be copied to the resized version.
    If the shape is smaller, the input array will be cropped appropriately.
    """
    def compute(self):
	a = self.getInputFromPort("Array")
        dims = self.getInputFromPort("Dims")
        newdims = []
	
	for i in xrange(dims):
	    pname = "dim" + str(i)
	    newdims.append(self.getInputFromPort(pname))

        try:
            t = tuple(newdims)
            b = a.resize(t)
            out = NDArray()
            out.set_array(b)
        except:
            raise ModuleError("Could not assign new shape.")
        
        self.setResult("Array Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Dims", (basic.Integer, 'Output Dimensionality'))
        reg.add_input_port(cls, "dim0", (basic.Integer, 'Dimension Size'))
        reg.add_input_port(cls, "dim1", (basic.Integer, 'Dimension Size'))
        reg.add_input_port(cls, "dim2", (basic.Integer, 'Dimension Size'))
        reg.add_input_port(cls, "dim3", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim4", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim5", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim6", (basic.Integer, 'Dimension Size'), True)
        reg.add_input_port(cls, "dim7", (basic.Integer, 'Dimension Size'), True)
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))

class ArrayExtractRegion(ArrayOperationModule, Module):
    """ Extract a region from array as specified by the
    dimension and starting and ending indices """
    def compute(self):
        import operator
        a = self.getInputFromPort("Array")
        dims = self.getInputFromPort("Dims")
        a_dims = len(a.get_shape())
        if dims > a_dims:
            raise ModuleError("Output Dimensionality larger than Input Dimensionality")

        slices = []
        for i in xrange(dims):
            (start, stop) = self.getInputFromPort("dim"+str(i))
            slices.append(slice(start, stop))

        ar = operator.__getitem__(a.get_array(), tuple(slices))
        out = NDArray()
        out.set_array(ar)
        self.setResult("Array Output", out)
        
    @classmethod
    def register(cls, reg, basic):
        l = [basic.Integer, basic.Integer]
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Dims", (basic.Integer, 'Output Dimensionality'))
        reg.add_input_port(cls, "dim0", l, True)
        reg.add_input_port(cls, "dim1", l, True)
        reg.add_input_port(cls, "dim2", l, True)
        reg.add_input_port(cls, "dim3", l, True)
        reg.add_input_port(cls, "dim4", l, True)
        reg.add_input_port(cls, "dim5", l, True)
        reg.add_input_port(cls, "dim6", l, True)
        reg.add_input_port(cls, "dim7", l, True)
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))

class ArrayRavel(ArrayOperationModule, Module):
    """ Get a 1D array containing the elements of the input array"""
    def compute(self):
        a = self.getInputFromPort("Array")
        b = NDArray()
        b.set_array(a.ravel())
        self.setResult("Array Output", b)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))
        
class ArrayRound(ArrayOperationModule, Module):
    """ Round each element of the array to the given number of
    decimal places.  This defaults to 0 resulting in a rounding
    to integers """
    def __init__(self):
        Module.__init__(self)
        self.decimals = 0

    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Decimals"):
            self.decimals = self.getInputFromPort("Decimals")

        out = NDArray()
        out.set_array(a.round(precision=self.decimals))
        self.setResult("Array Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Decimals", (basic.Integer, 'Precision'))
        reg.add_output_port(cls, "Array Output", (NDArray, 'Output Array'))

class ArrayGetSigma(ArrayOperationModule, Module):
    """ Return the standard deviation of elements in the array """
    def __init__(self):
        Module.__init__(self)
        self.axis=None

    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Axis"):
            self.axis = self.getInputFromPort("Axis")

        out = NDArray()
        out.set_array(a.get_standard_deviation(self.axis))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="ArrayStandardDeviation", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Axis", (basic.Integer, 'Axis'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArraySum(ArrayOperationModule, Module):
    """ Get the sum of all elements in the input array """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Array Sum", float(a.get_sum()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Array Sum", (basic.Float, 'Sum'))

class ArrayElementMultiply(ArrayOperationModule, Module):
    """ Perform an element-wise multiply on the elements of two arrays """
    def compute(self):
        a1 = self.getInputFromPort("Array1")
        a2 = self.getInputFromPort("Array2")
        out = NDArray()
        out.set_array(a1.get_array() * a2.get_array())
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array1", (NDArray, 'Input Array 1'))
        reg.add_input_port(cls, "Array2", (NDArray, 'Input Array 2'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
class ArraySetElement(ArrayOperationModule, Module):
    """ Set a set of array elements given arrays of values and indices

        Please note that this module creates a copy of the input to operate
        on to preserve the original array data. """
    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Scalar Value"):
            self.v = self.getInputFromPort("Scalar Value")
        else:
            self.v = self.getInputFromPort("Value Array")

        if self.hasInputFromPort("Single Index"):
            self.ind = self.getInputFromPort("Single Index")
        else:
            self.ind = self.getInputFromPort("Index Array")

        out_a = a.copy()
        
        out_a.put(self.ind, self.v)
        out = NDArray()
        out.set_array(out_a)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Scalar Value", (basic.Float, 'Value to Set'))
        reg.add_input_port(cls, "Value Array", (NDArray, 'Values to Set'))
        reg.add_input_port(cls, "Single Index", (basic.Integer, 'Index to Set'))
        reg.add_input_port(cls, "Index Array", (NDArray, 'Indexes to Set'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
class ArrayVariance(ArrayOperationModule, Module):
    """ Calculate the variance of the elements of an array """
    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Axis"):
            self.setResult("Variance", float(a.get_variance(axis=self.getInputFromPort("Axis"))))
        else:
            self.setResult("Variance", float(a.get_variance()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Axis", (basic.Integer, 'Axis'))
        reg.add_output_port(cls, "Variance", (basic.Float, 'Variance'))
        
class ArrayTrace(ArrayOperationModule, Module):
    """ Calculate the trace of the input array.

        The input array must have at least rank 2.  The trace is taken
        on the diagonal given by the inputs Axis1 and Axis2 using the
        given Offset.  If these values are not supplied, they default to:

        Axis1 = 0
        Axis2 = 1
        Offset = 0
    """
    def compute(self):
        a = self.getInputFromPort("Array")
        if self.hasInputFromPort("Axis1"):
            self.axis1 = self.getInputFromPort("Axis1")
        else:
            self.axis1 = 0

        if self.hasInputFromPort("Axis2"):
            self.axis2 = self.getInputFromPort("Axis2")
        else:
            self.axis2 = 1

        if self.hasInputFromPort("Offset"):
            self.offset = self.getInputFromPort("Offset")
        else:
            self.offset = 0

        self.setResult("Trace", float(a.get_trace(self.offset, self.axis1, self.axis2)))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Axis1", (basic.Integer, 'Axis 1'))
        reg.add_input_port(cls, "Axis2", (basic.Integer, 'Axis 2'))
        reg.add_input_port(cls, "Offset", (basic.Integer, 'Offset'))
        reg.add_output_port(cls, "Trace", (basic.Float, 'Array Trace'))
        
class ArraySwapAxes(ArrayOperationModule, Module):
    """ Create a new view of the input array with the
    given axes swapped.
    """
    def compute(self):
        a = self.getInputFromPort("Array")
        a1 = self.getInputFromPort("Axis1")
        a2 = self.getInputFromPort("Axis2")
        out = NDArray()
        out.set_array(a.swap_axes(a1, a2))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Axis1", (basic.Integer, 'Axis 1'))
        reg.add_input_port(cls, "Axis2", (basic.Integer, 'Axis 2'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArraySqueeze(ArrayOperationModule, Module):
    """ Eliminate all length-1 dimensions in the input array. """
    def compute(self):
        a = self.getInputFromPort("Array")
        out = NDArray()
        out.set_array(a.squeeze())
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
