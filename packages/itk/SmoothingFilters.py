############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import itk
import core.modules
from core.modules.vistrails_module import Module, ModuleError
from ITK import *
from Image import Image

class CurvatureAnisotropicDiffusionFilter(Module):
    my_namespace="Filter|Smoothing"
    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]

        try:
            self.filter_ = itk.CurvatureAnisotropicDiffusionImageFilter[inImgType, inImgType].New(im.getImg())
        except:
            raise ModuleError(self, "Filter requires a decimal PixelType")

        #default values are recommended
        if self.hasInputFromPort("Iterations"):
            iterations = self.getInputFromPort("Iterations")
        else:
            iterations = 5

        if self.hasInputFromPort("TimeStep"):
            timestep = self.getInputFromPort("TimeStep")
        else:
            if dim == 2:
                timestep = 0.125
            else:
                timestep = 0.0625

        if self.hasInputFromPort("Conductance"):
            conductance = self.getInputFromPort("Conductance")
        else:
            conductance = 3.0

        self.filter_.SetNumberOfIterations(iterations)
        self.filter_.SetTimeStep(timestep)
        self.filter_.SetConductanceParameter(conductance)

        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(inPixelType)
        outIm.setDim(dim)
        
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Curvature Anisotropic Diffusion Filter", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input Dimension", (basic.Integer, 'Input Dimension'),True)
        reg.add_input_port(cls, "Input PixelType Float", (PixelType, 'Input PixelType Float'),True)
        reg.add_input_port(cls, "Iterations", (basic.Integer, 'Iterations'), True)
        reg.add_input_port(cls, "TimeStep", (basic.Float, 'TimeStep'), True)
        reg.add_input_port(cls, "Conductance", (basic.Float, 'Conductance'), True)

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)


class RecursiveGaussianImageFilter(Module):
    my_namespace="Filter|Smoothing"
    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.hasInputFromPort("Output PixelType"):
            outPixelType = self.getInputFromPort("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        outdim = dim

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]

        self.filter_ = itk.RecursiveGaussianImageFilter[inImgType, outImgType].New(im.getImg())

        sigma = self.getInputFromPort("Sigma")
        self.filter_.SetSigma(sigma)

        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)
        
        self.setResult("Output Image", outIm)
        self.setResult("Output PixelType", outPixelType)
        self.setResult("Output Dimension", outdim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Recursive Gaussian Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input Dimension", (basic.Integer, 'Input Dimension'),True)
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Sigma", (basic.Float, 'Sigma'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'),True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

class CurvatureFlowImageFilter(Module):
    my_namespace="Filter|Smoothing"
    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]

        try:
            self.filter_ = itk.CurvatureFlowImageFilter[inImgType, inImgType].New(im.getImg())
        except:
            raise ModuleError(self, "Filter requires a decimal PixelType")

        #default values recommended
        if self.hasInputFromPort("TimeStep"):
            self.ts = self.getInputFromPort("TimeStep")
        else:
            self.ts = 0.125

        if self.hasInputFromPort("Iterations"):
            self.iterations = self.getInputFromPort("Iterations")
        else:
            self.iterations = 5

        self.filter_.SetTimeStep(self.ts)
        self.filter_.SetNumberOfIterations(self.iterations)

        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(inPixelType)
        outIm.setDim(dim)
        
        self.setResult("Output Image", outIm)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Curvature Flow Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input Dimension", (basic.Integer, 'Input Dimension'),True)
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "TimeStep", (basic.Float, 'TimeStep'), True)
        reg.add_input_port(cls, "Iterations", (basic.Integer, 'Iterations'), True)

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))

class DiscreteGaussianImageFilter(Module):
    my_namespace = 'Filter|Smoothing'

    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.hasInputFromPort("Output PixelType"):
            outPixelType = self.getInputFromPort("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]

        gaussian_variance = self.getInputFromPort("Gaussian Variance")

        max_kernel_width = self.getInputFromPort("Max Kernel Width")

        try:
            self.filter_ = itk.DiscreteGaussianImageFilter[inImgType, outImgType].New(im.getImg())
        except:
            raise ModuleError(self, "Requires Signed PixelType")

        self.filter_.SetVariance(gaussian_variance)
        self.filter_.SetMaximumKernelWidth(max_kernel_width)
        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        #set results
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)
        self.setResult("Output PixelType", outPixelType)


    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Discrete Gaussian Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Gaussian Variance", (basic.Float, 'Gaussian Variance'))
        reg.add_input_port(cls, "Max Kernel Width", (basic.Integer, 'Max Kernel Width'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

class BinomialBlurImageFilter(Module):
    my_namespace = 'Filter|Smoothing'

    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.hasInputFromPort("Output PixelType"):
            outPixelType = self.getInputFromPort("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]

        repetitions = self.getInputFromPort("Repetitions")

        self.filter_ = itk.BinomialBlurImageFilter[inImgType, outImgType].New(im.getImg())
        self.filter_.SetRepetitions(repetitions)
        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        #set results
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)
        self.setResult("Output PixelType", outPixelType)


    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="BinomialBlur Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Repetitions", (basic.Integer, 'Repetitions'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

class GradientAnisotropicDiffusionImageFilter(Module):
    my_namespace = 'Filter|Smoothing'

    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.hasInputFromPort("Output PixelType"):
            outPixelType = self.getInputFromPort("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]

        timestep = self.getInputFromPort("Timestep")

        conductance = self.getInputFromPort("Conductance")

        iterations = self.getInputFromPort("Iterations")

        try:
            self.filter_ = itk.GradientAnisotropicDiffusionImageFilter[inImgType, outImgType].New(im.getImg())
        except:
            raise ModuleError(self, "Requires Decimal PixelType")

        self.filter_.SetTimeStep(timestep)
        self.filter_.SetConductanceParameter(conductance)
        self.filter_.SetNumberOfIterations(iterations)
        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        #set results
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)
        self.setResult("Output PixelType", outPixelType)


    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Gradient Anisotropic Diffusion Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Timestep", (basic.Float, 'Timestep'))
        reg.add_input_port(cls, "Conductance", (basic.Float, 'Conductance'))
        reg.add_input_port(cls, "Iterations", (basic.Integer, 'Iterations'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)


class MinMaxCurvatureFlowImageFilter(Module):
    my_namespace = 'Filter|Smoothing'

    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.hasInputFromPort("Output PixelType"):
            outPixelType = self.getInputFromPort("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]

        timestep = self.getInputFromPort("Timestep")

        radius = self.getInputFromPort("Radius")

        iterations = self.getInputFromPort("Iterations")

        self.filter_ = itk.MinMaxCurvatureFlowImageFilter[inImgType, outImgType].New(im.getImg())
        self.filter_.SetTimeStep(timestep)
        self.filter_.SetStencilRadius(radius)
        self.filter_.SetNumberOfIterations(iterations)
        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        #set results
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)
        self.setResult("Output PixelType", outPixelType)


    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="MinMax Curvature Flow Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Timestep", (basic.Float, 'Timestep'))
        reg.add_input_port(cls, "Radius", (basic.Float, 'Radius'))
        reg.add_input_port(cls, "Iterations", (basic.Integer, 'Iterations'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

class BilateralImageFilter(Module):
    my_namespace = 'Filter|Smoothing'

    def compute(self):
        im = self.getInputFromPort("Input Image")

        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.hasInputFromPort("Output PixelType"):
            outPixelType = self.getInputFromPort("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]

        range_sigma = self.getInputFromPort("Range Sigma")

        domain_sigma = self.getInputFromPort("Domain Sigma")

        self.filter_ = itk.BilateralImageFilter[inImgType, outImgType].New(im.getImg())
        self.filter_.SetRangeSigma(range_sigma)
        self.filter_.SetDomainSigma(domain_sigma)
        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        #set results
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)
        self.setResult("Output PixelType", outPixelType)


    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Bilateral Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Range Sigma", (basic.Float, 'Range Sigma'))
        reg.add_input_port(cls, "Domain Sigma", (basic.Float, 'Domain Sigma'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

