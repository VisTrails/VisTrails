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
## of VisTrails), please contact us at vistrails@sci.utah.edu.
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

#TODO This filter only accepts decimal pixel types, and there is no warning about this
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

        self.filter_ = itk.CurvatureAnisotropicDiffusionImageFilter[inImgType, inImgType].New(im.getImg())

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

#TODO This filter only accepts decimal pixel types, and there is no warning about this
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

        self.filter_ = itk.CurvatureFlowImageFilter[inImgType, inImgType].New(im.getImg())

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
