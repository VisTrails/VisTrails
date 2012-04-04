#############################################################################
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

class BinaryThresholdImageFilter(Module):
    my_namespace = "Filter|Threshold"

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

        if self.hasInputFromPort("Upper Threshold"):
            upper_threshold = self.getInputFromPort("Upper Threshold")
        else:
            upper_threshold = 255

        lower_threshold = self.getInputFromPort("Lower Threshold")

        if self.hasInputFromPort("Outside Value"):
            outside_value = self.getInputFromPort("Outside Value")
        else:
            outside_value = 0

        if self.hasInputFromPort("Inside Value"):
            inside_value = self.getInputFromPort("Inside Value")
        else:
            inside_value = 255

        self.filter_ = itk.BinaryThresholdImageFilter[inImgType, outImgType].New(im.getImg())
        self.filter_.SetUpperThreshold(upper_threshold)
        self.filter_.SetLowerThreshold(lower_threshold)
        self.filter_.SetOutsideValue(outside_value)
        self.filter_.SetInsideValue(inside_value)
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
        reg.add_module(cls, name="BinaryThresholdImageFilter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)

        reg.add_input_port(cls, "Upper Threshold", (basic.Integer, 'Upper Threshold'),True)
        reg.add_input_port(cls, "Lower Threshold", (basic.Integer, 'Lower Threshold'))
        reg.add_input_port(cls, "Outside Value", (basic.Integer, 'Outside Value'),True)
        reg.add_input_port(cls, "Inside Value", (basic.Integer, 'Inside Value'),True)

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)

