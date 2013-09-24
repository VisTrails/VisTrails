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
	a = self.get_input("Array")
        dims = self.get_input("Dims")
        newdims = []
	
	for i in xrange(dims):
	    pname = "dim" + str(i)
	    newdims.append(self.get_input(pname))

        try:
            a.reshape(tuple(newdims))
        except:
            raise ModuleError("Could not assign new shape.  Be sure the number of elements remains constant")
        
        self.setResult("Array Output", a.copy())

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
        a = self.get_input("Array")
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
        a = self.get_input("Array")
        b = self.get_input("Scalar")
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
        a = self.get_input("Array")
        if self.hasInputFromPort("Axis"):
            self.axis = self.get_input("Axis")
        if self.hasInputFromPort("Sort"):
            self.kind = self.get_input("Sort")
        if self.hasInputFromPort("Order"):
            self.order = self.get_input("Order")

        b = a.sort_array(axis=self.axis, kind=self.kind, order=self.order)
        out = NDArray()
        out.set_array(b.copy())
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
        a = self.get_input("Array")
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
        a = self.get_input("Array")
        if self.hasInputFromPort("Value"):
            val = self.get_input("Value")
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
	a = self.get_input("Array")
        dims = self.get_input("Dims")
        newdims = []
	
	for i in xrange(dims):
	    pname = "dim" + str(i)
	    newdims.append(self.get_input(pname))

        try:
            t = tuple(newdims)
            b = a.resize(t)
            out = NDArray()
            out.set_array(b.copy())
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
        a = self.get_input("Array")
        dims = self.get_input("Dims")
        a_dims = len(a.get_shape())
        if dims > a_dims:
            raise ModuleError("Output Dimensionality larger than Input Dimensionality")

        slices = []
        for i in xrange(dims):
            (start, stop) = self.get_input("dim"+str(i))
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
        a = self.get_input("Array")
        b = NDArray()
        b.set_array(a.ravel().copy())
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
        a = self.get_input("Array")
        if self.hasInputFromPort("Decimals"):
            self.decimals = self.get_input("Decimals")

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
        a = self.get_input("Array")
        if self.hasInputFromPort("Axis"):
            self.axis = self.get_input("Axis")

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
        a = self.get_input("Array")
        self.setResult("Array Sum", float(a.get_sum()))

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Array Sum", (basic.Float, 'Sum'))

class ArrayElementMultiply(ArrayOperationModule, Module):
    """ Perform an element-wise multiply on the elements of two arrays """
    def compute(self):
        a1 = self.get_input("Array1")
        a2 = self.get_input("Array2")
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
        a = self.get_input("Array")
        if self.hasInputFromPort("Scalar Value"):
            self.v = self.get_input("Scalar Value")
        else:
            self.v = self.get_input("Value Array")

        if self.hasInputFromPort("Single Index"):
            self.ind = self.get_input("Single Index")
        else:
            self.ind = self.get_input("Index Array")

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
        a = self.get_input("Array")
        if self.hasInputFromPort("Axis"):
            self.setResult("Variance", float(a.get_variance(axis=self.get_input("Axis"))))
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
        a = self.get_input("Array")
        if self.hasInputFromPort("Axis1"):
            self.axis1 = self.get_input("Axis1")
        else:
            self.axis1 = 0

        if self.hasInputFromPort("Axis2"):
            self.axis2 = self.get_input("Axis2")
        else:
            self.axis2 = 1

        if self.hasInputFromPort("Offset"):
            self.offset = self.get_input("Offset")
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
        a = self.get_input("Array")
        a1 = self.get_input("Axis1")
        a2 = self.get_input("Axis2")
        out = NDArray()
        out.set_array(a.swap_axes(a1, a2).copy())
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
        a = self.get_input("Array")
        out = NDArray()
        out.set_array(a.get_array().squeeze().copy())
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArrayAdd(ArrayOperationModule, Module):
    """ Add two arrays of the same size and shape """
    def compute(self):
        a1 = self.get_input("Array One").get_array()
        a2 = self.get_input("Array Two").get_array()

        if a1.shape != a2.shape:
            raise ModuleError("Cannot add arrays with different shapes")

        out = NDArray()
        out.set_array(a1 + a2)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array One", (NDArray, 'Input Array 1'))
        reg.add_input_port(cls, "Array Two", (NDArray, 'Input Array 2'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArrayScalarAdd(ArrayOperationModule, Module):
    """ Add two arrays of the same size and shape """
    def compute(self):
        a1 = self.get_input("Array One").get_array()
        s = self.get_input("Scalar")

        out = NDArray()
        out.set_array(a1 + s)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array One", (NDArray, 'Input Array 1'))
        reg.add_input_port(cls, "Scalar", (basic.Float, 'Scalar'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArrayLog10(ArrayOperationModule, Module):
    """ Take the base-10 log of each element in the input array """
    def compute(self):
        a = self.get_input("Array").get_array()
        out = NDArray()
        out.set_array(numpy.log10(a))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
    
class ArrayAtan2(ArrayOperationModule,  Module):
    """ Calculate the oriented arc-tangent of a vector stored as two arrays.
    Reals:  Real components of complex vectors
    Imaginaries:  Imaginary components of complex vectors
    """
    def compute(self):
        r = self.get_input("Reals").get_array()
        i = self.get_input("Imaginaries").get_array()
        out = NDArray()
        out.set_array(numpy.arctan2(r,i))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Reals", (NDArray, 'Real Components'))
        reg.add_input_port(cls, "Imaginaries", (NDArray, 'Imaginary Components'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArraySqrt(ArrayOperationModule, Module):
    """ Calculate the element-wise square root of the input array """
    def compute(self):
        a = self.get_input("Input Array").get_array()
        out = NDArray()
        out.set_array(numpy.sqrt(a))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
           
class ArrayThreshold(ArrayOperationModule, Module):
    """ Threshold the array keeping only the values above the scalar value, v. """
    def compute(self):
        in_ar = self.get_input("Input Array").get_array()
        v = self.get_input("Value")
        r = self.forceGetInputFromPort("Replacement")
        if r == None:
            r = 0.
        out = NDArray()
        out.set_array(numpy.where(in_ar > v, in_ar, r))
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Value", (basic.Float, 'Threshold Value'))
        reg.add_input_port(cls, "Replacement", (basic.Float, 'Replacement Value'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
class ArrayWindow(ArrayOperationModule, Module):
    """ Threshold the array from both above and below, keeping only
    the values within the window. """
    def compute(self):
        in_ar = self.get_input("Input Array").get_array()
        lo = self.forceGetInputFromPort("Lower Bound")
        hi = self.forceGetInputFromPort("Upper Bound")
        r = self.forceGetInputFromPort("Replacement")
        if r == None:
            r = 0.
        if lo == None:
            lo = in_ar.min()
        if hi == None:
            hi = in_ar.max()

        out = NDArray()
        o = numpy.where(in_ar >= lo, in_ar, r)
        o = numpy.where(o <= hi, o, r)
        out.set_array(o)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Lower Bound", (basic.Float, 'Lower Threshold Value'))
        reg.add_input_port(cls, "Upper Bound", (basic.Float, 'Upper Threshold Value'))
        reg.add_input_port(cls, "Replacement", (basic.Float, 'Replacement Value'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ArrayNormalize(ArrayOperationModule, Module):
    """ Normalize the input array """
    def compute(self):
        in_ar = self.get_input("Input Array").get_array()
        ar = numpy.zeros(in_ar.shape)
        if self.forceGetInputFromPort("Planes"):
            for i in range(in_ar.shape[0]):
                p = in_ar[i] - in_ar[i].min()
                ar[i] = p / p.max()
        else:
            ar = in_ar - in_ar.min()
            ar = ar/ar.max()
            
        out = NDArray()
        out.set_array(ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Planes", (basic.Boolean, 'Plane-wise normalization'), True)
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
class ArrayName(ArrayOperationModule, Module):
    """ Assign a name or label to the entries of an array """
    def compute(self):
        in_ar = self.get_input("Input Array")
        gen_name = self.forceGetInputFromPort("Name")
        one_index = self.forceGetInputFromPort("One Indexed")
        if gen_name:
            in_ar.set_name(gen_name, index=one_index)

        name_list = self.forceGetInputListFromPort("Row Name")
        if name_list != None:
            for (i,n) in name_list:
                in_ar.set_row_name(n, i)

        dname = self.forceGetInputFromPort("Domain Name")
        if dname:
            in_ar.set_domain_name(dname)

        rname = self.forceGetInputFromPort("Range Name")
        if rname:
            in_ar.set_range_name(rname)

        self.setResult("Output Array", in_ar)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "One Indexed", (basic.Boolean, 'One Indexed'))
        reg.add_input_port(cls, "Name", (basic.String, 'Array Name'))
        reg.add_input_port(cls, "Row Name", [basic.Integer, basic.String], True)
        reg.add_input_port(cls, "Domain Name", (basic.String, 'Domain Label'))
        reg.add_input_port(cls, "Range Name", (basic.String, 'Range Label'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
