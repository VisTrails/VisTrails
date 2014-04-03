import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import scipy
import scipy.interpolate
import scipy.ndimage
import vtk
from Array import *
from Matrix import *

class ArrayInterpModule(object):
    my_namespace = 'scipy|interpolation'
    
class RBFInterpolate(ArrayInterpModule, Module):
    """ Use radial basis function interpolation to project scalars from
    one mesh to another.  The input, Source, describes the x,y,z coordinates and
    values of the points in the form:  [[x,y,z,v]]  The input, Destination,
    describes the x,y,z coordinates of the points to project onto in the form
    [[x,y,z]].  Additional (optional) inputs controll the basis function (basis),
    the smoothing factor (smoothing) and the tuning parameter (epsilon).  Not
    all parameters are valid for all bases.  The following defaults are applied:

    basis = inverse multiquadric
    smoothing = 0.0
    epsilon = 1.0
    """

    def compute(self):
        src = self.get_input("Source").get_array()
        if src.shape[1] != 4:
            raise ModuleError("Source array must be in the form [[x,y,z,v]]")
        
        dest = self.get_input("Destination").get_array()
        if dest.shape[1] != 3:
            raise ModuleError("Destination array must be in the form [[x,y,z]]")
        
        if self.has_input("Basis"):
            self.basis = self.get_input("Basis")
        else:
            self.basis = 'inverse multiquadric'

        if self.has_input("Smoothing"):
            self.smooth = self.get_input("Smoothing")
        else:
            self.smooth = 0.0

        if self.has_input("Epsilon"):
            self.eps = self.get_input("Epsilon")
        else:
            self.eps = 1.0

        rbfi = scipy.interpolate.Rbf(src[:,0], src[:,1], src[:,2], src[:,3], function=self.basis, smooth=self.smooth, epsilon=self.eps)

        val_ar = rbfi(dest[:,0], dest[:,1], dest[:,2])

        out = NDArray()
        out.set_array(val_ar)
        self.set_output("Output", out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Source", (NDArray, 'Source Array'))
        reg.add_input_port(cls, "Destination", (NDArray, 'Destination Array'))
        reg.add_input_port(cls, "Basis", (basic.String, 'Basis Function'), True)
        reg.add_input_port(cls, "Smoothing", (basic.Float, 'Smoothing Factor'), True)
        reg.add_input_port(cls, "Epsilon", (basic.Float, 'Basis Epsilon'), True)
        reg.add_output_port(cls, "Output", (NDArray, 'Output Scalars'))

class BSplineInterpolate(ArrayInterpModule, Module):
    """
    Find the B-Spline representation of an N-dimensional curve.
    """

    def compute(self):
        in_ar = self.get_input("Input").get_array()
        num_samp = self.force_get_input("Interpolant Support")
        if not num_samp:
            num_samp = in_ar.shape[0]

        smoothing = self.force_get_input("Smoothing")
        if not smoothing:
            smoothing = 0.0

        degree = self.force_get_input("Degree")
        if not degree:
            degree = 3

        (tckvec, u) = scipy.interpolate.splprep(in_ar, s=smoothing, k=degree, nest=-1)
        (x,y,z) = splev(numpy.linspace(0.,1.,num_samp), tckvec)
        out_ar = numpy.zeros((x.shape[0], 3))
        out_ar[:,0] = x
        out_ar[:,1] = y
        out_ar[:,2] = z

        out = NDArray()
        out.set_array(out_ar)

        self.set_output("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Source Array'))
        reg.add_input_port(cls, "Smoothing", (basic.Float, 'Smoothing Factor'), True)
        reg.add_input_port(cls, "Interpolant Support", (basic.Integer, 'Output Samples'), True)
        reg.add_input_port(cls, "Degree", (basic.Integer, 'Polynomial Degree'), True)
        reg.add_output_port(cls, "Output", (NDArray, 'Output Scalars'))

class BSplineResample(ArrayInterpModule, Module):
    """
    Resample the input array using an order-n bspline
    """
    def compute(self):
        in_ar = self.get_input("Input").get_array()
        order = self.force_get_input("Order")
        if order == None:
            order = 3
        planes = self.force_get_input("Planes")
        ndim = in_ar.ndim
        gridshape = self.get_input("New Shape").values

        out_ar = None
        if planes:
            out_ar = []
            for i in range(in_ar.shape[0]):
                pl = in_ar[i].squeeze()
                arshape = pl.shape
                g = scipy.mgrid[tuple([slice(0, v1-1, complex(0,v2)) for (v1,v2) in zip(arshape, gridshape)])]
                coords = numpy.array(list(g))
                out_ar.append(scipy.ndimage.map_coordinates(pl, coords))

            out_ar = numpy.array(out_ar)
            
        else:
            arshape = in_ar.shape
            g = scipy.mgrid[tuple([slice(0, v1-1, complex(0,v2)) for (v1,v2) in zip(arshape, gridshape)])]
            coords = numpy.array(list(g))
            out_ar = scipy.ndimage.map_coordinates(in_ar, coords)
            
        out = NDArray()
        out.set_array(out_ar)
        self.set_output("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Source Array'))
        reg.add_input_port(cls, "Order", (basic.Integer, 'Bspline Order'), True)
        reg.add_input_port(cls, "New Shape", (basic.Tuple, 'New Array Shape'))
        reg.add_input_port(cls, "Planes", (basic.Boolean, 'Apply to each plane'), True)
        reg.add_output_port(cls, "Output", (NDArray, 'Output Scalars'))
