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

class GradientMagnitudeRecursiveGaussianImageFilter(Module):
    my_namespace = "Filter|Feature"

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

        sigma_ = self.getInputFromPort("Sigma")

        self.filter_ = itk.GradientMagnitudeRecursiveGaussianImageFilter[inImgType, outImgType].New(im.getImg())
        self.filter_.SetSigma(sigma_)
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
        reg.add_module(cls, name="Gradient Magnitude Recursive Gaussian Image Filter", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)
        reg.add_input_port(cls, "Sigma", (basic.Float, 'Sigma'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

#TODO this filter doesn't produce any results
class DanielssonDistanceMapImageFilter(Module):
    my_namespace = 'Filter|Feature'

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

        squared_distance = self.getInputFromPort("Squared Distance")

        image_spaceing = self.getInputFromPort("Image Spaceing")

        self.filter_ = itk.DanielssonDistanceMapImageFilter[inImgType, outImgType].New(im.getImg())
        self.filter_.SetSquaredDistance(squared_distance)
        self.filter_.SetUseImageSpacing(image_spaceing)
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
        reg.add_module(cls, name="DanielssonDistance Map Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Squared Distance", (basic.Float, 'Squared Distance'))
        reg.add_input_port(cls, "Image Spaceing", (basic.Float, 'Image Spaceing'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

class SobelEdgeDetectionImageFilter(Module):
    my_namespace = 'Filter|Feature'

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

        self.filter_ = itk.SobelEdgeDetectionImageFilter[inImgType, outImgType].New(im.getImg())
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
        reg.add_module(cls, name="Sobel Edge Detection Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)


        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
