import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import numpy
import scipy
import scipy.ndimage
from Array import *
from Matrix import *

class ArrayImaging(object):
    my_namespace = 'numpy|imaging'

class ExtractRGBAChannel(ArrayImaging, Module):
    """ Extract a single color channel from an array representing an
    RGBA type image.  This will return a 2D array with the single channel
    specified as the scalar elements """
    def compute(self):
        im = self.get_input("Image").get_array()
        chan = self.get_input("Channel")
        ar = im[:,:,chan]
        out = NDArray()
        out.set_array(ar)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Image", (NDArray, 'Image Array'))
        reg.add_input_port(cls, "Channel", (basic.Integer, 'Channel'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class GaussianGradientMagnitude(ArrayImaging, Module):
    """ Calculate the Gradient Magnitude of an input NDArray using gaussian derivatives.
    The standard-deviation of the Gaussian filter are given for each axis as a sequence
    or as a single number, in which case the filter will be isotropic. """
    def compute(self):
        im = self.get_input("Image")
        sigma = self.getInputListFromPort("Sigmas")
        if len(sigma) <= 1:
            sigma = sigma[0]
        der = scipy.ndimage.gaussian_gradient_magnitude(im.get_array(), sigma)
        out = NDArray()
        out.set_array(der)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Image", (NDArray, 'Image Array'))
        reg.add_input_port(cls, "Sigmas", (basic.Float, 'Standard Deviations'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class JointHistogram(ArrayImaging, Module):
    """ Calculate the Joint Histogram of 2 inputs.  The inputs can be of arbitrary dimension,
    but must be equivalently sized. """
    def compute(self):
        in_x = self.get_input("Array One").get_array()
        in_y = self.get_input("Array Two").get_array()
        size_x = self.get_input("Bins X")
        size_y = self.get_input("Bins Y")

        take_log = True
        if self.has_input("Log10"):
            take_log = self.get_input("Log10")

        out_ar = numpy.zeros((size_x, size_y))
        min_x = in_x.min()
        max_x = in_x.max() - min_x
        min_y = in_y.min()
        max_y = in_y.max() - min_y

        in_x = in_x.flatten()
        in_y = in_y.flatten()

        for i in xrange(in_x.size):
            x_cor = int(((in_x[i] - min_x)/max_x) * (size_x - 1))
            y_cor = int(((in_y[i] - min_y)/max_y) * (size_y - 1))

            out_ar[x_cor,y_cor] += 1.0

        if take_log:
            out_ar = out_ar + 1.0
            out_ar = scipy.log(out_ar)
        out = NDArray()
        out_ar = out_ar.transpose()
        out_ar = out_ar[::-1]
        out.set_array(out_ar)
        self.setResult("Joint Histogram", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array One", (NDArray, 'X Axis Input'))
        reg.add_input_port(cls, "Array Two", (NDArray, 'Y Axis Input'))
        reg.add_input_port(cls, "Log10", (basic.Boolean, 'Use Log of Histogram'), True)
        reg.add_input_port(cls, "Bins X", (basic.Integer, 'Number of X Bins'))
        reg.add_input_port(cls, "Bins Y", (basic.Integer, 'Number of Y Bins'))
        reg.add_output_port(cls, "Joint Histogram", (NDArray, 'Joint Histogram'))

class GaussianSmooth(ArrayImaging, Module):
    """ Smooth the Input array with a multi-dimensional gaussian kernel.
    The standard-deviation of the Gaussian filter are given for each axis as a sequence
    or as a single number, in which case the filter will be isotropic. """
    def compute(self):
        im = self.get_input("Input Array")
        sigma = self.getInputListFromPort("Sigmas")
        if len(sigma) <= 1:
            sigma = sigma[0]
        der = scipy.ndimage.gaussian_filter(im.get_array(), sigma)
        out = NDArray()
        out.set_array(der)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Image Array'))
        reg.add_input_port(cls, "Sigmas", (basic.Float, 'Standard Deviations'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))
        
class MedianFilter(ArrayImaging, Module):
    """ Smooth the Input array with a multi-dimensional median filter.  """
    def compute(self):
        im = self.get_input("Input Array")
        k_size = self.get_input("Size")
        der = scipy.ndimage.median_filter(im.get_array(), size=k_size)
        out = NDArray()
        out.set_array(der)
        self.setResult("Output Array", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Image Array'))
        reg.add_input_port(cls, "Size", (basic.Integer, 'Kernel Size'))
        reg.add_output_port(cls, "Output Array", (NDArray, 'Output Array'))

class ImageDifference(ArrayImaging, Module):
    """ Calculate the difference between two input images. """
    def compute(self):
        im = self.get_input("Input 1")
        im2 = self.get_input("Input 2")

        da_ar = im.get_array() - im2.get_array()
        da_ar = numpy.abs(da_ar)

        out = NDArray()
        out.set_array(da_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input 1", (NDArray, 'Image Array'))
        reg.add_input_port(cls, "Input 2", (NDArray, 'Image Array'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Array'))

class ImageNormalize(ArrayImaging, Module):
    """ Move the range of the image to [0,1] """
    def compute(self):
        im = self.get_input("Input")
        im_max = im.get_array().max()
        im_ar = im.get_array() / im_max

        out = NDArray()
        out.set_array(im_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Image Array'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Array'))

class SobelGradientMagnitude(ArrayImaging, Module):
    """ Use n-dimensional sobel kernels to compute the gradient magnitude
    of an image """
    def compute(self):
        im = self.get_input("Input").get_array()
        mag = numpy.zeros(im.shape)
        for i in xrange(im.ndim):
            kern = scipy.ndimage.sobel(im, axis=i)
            mag += kern*kern

        out = NDArray()
        out.set_array(numpy.sqrt(mag))
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input", (NDArray, 'Image Array'))
        reg.add_output_port(cls, "Output", (NDArray, 'Output Array'))
