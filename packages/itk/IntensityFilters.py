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

class RescaleIntensityImageFilter(Module):
    my_namespace = "Filter|Intensity"
    def compute(self):
        inFilter = self.forceGetInputFromPort("Input Filter")
        im = self.getInputFromPort("Input Image")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        dim = self.getInputFromPort("Dimension")
        minimum = self.getInputFromPort("Minimum")
        maximum = self.getInputFromPort("Maximum")
        inType = itk.Image[inType, dim]
        outType= itk.Image[outType, dim]

        self.filter_ = itk.RescaleIntensityImageFilter[inType, outType].New(im)
        self.filter_.SetOutputMaximum(maximum)
        self.filter_.SetOutputMinimum(minimum)

        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)
        self.setResult("Output PixelType", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Rescale Intensity Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Filter", (Filter, 'Input Filter'), True)
        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Minimum", (basic.Integer, 'Minimum'))
        reg.add_input_port(cls, "Maximum", (basic.Integer, 'Maximum'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))

class SigmoidImageFilter(Module):
    my_namespace = "Filter|Intensity"
    def compute(self):
        inFilter = self.forceGetInputFromPort("Input Filter")
        im = self.getInputFromPort("Input Image")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        dim = self.getInputFromPort("Dimension")
        inType = itk.Image[inType, dim]
        outType= itk.Image[outType, dim]

        if self.hasInputFromPort("Minimum"):
            min = self.getInputFromPort("Minimum")
        else:
            min = 10

        if self.hasInputFromPort("Maximum"):
            max = self.getInputFromPort("Maximum")
        else:
            max = 240

        if self.hasInputFromPort("Alpha"):
            alpha = self.getInputFromPort("Alpha")
        else:
            alpha = 10

        if self.hasInputFromPort("Beta"):
            beta = self.getInputFromPort("Beta")
        else:
            beta = 170

        self.filter_ = itk.SigmoidImageFilter[inType,outType].New(im)
        self.filter_.SetOutputMinimum(min)
        self.filter_.SetOutputMaximum(max)
        self.filter_.SetAlpha(alpha)
        self.filter_.SetBeta(beta)
        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)
        self.setResult("Output PixelType", out)
        self.setResult("Output Dimension", dim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Sigmoid Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Filter", (Filter, 'Input Filter'), True)
        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'), True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Minimum", (basic.Integer, 'Minimum'), True)
        reg.add_input_port(cls, "Maximum", (basic.Integer, 'Maximum'), True)
        reg.add_input_port(cls, "Alpha", (basic.Float, 'Alpha'), True)
        reg.add_input_port(cls, "Beta", (basic.Float, 'Beta'), True)

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Output Filter'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))

class ThresholdImageFilter(Module):
    my_namespace = "Filter|Intensity"
    def compute(self):
        im = self.getInputFromPort("Input Image")
        up = self.getInputFromPort("Upper Value")
        lo = self.getInputFromPort("Lower Value")

        inty = self.getInputFromPort("Input PixelType")._type
        dim = self.getInputFromPort("Dimension")
        inType = itk.Image[inty, dim]

        self.filter_ = itk.ThresholdImageFilter[inType].New(im)

        self.filter_.SetUpper(up)
        self.filter_.SetLower(lo)
#       self.filter_.ThresholdAbove(up)
        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", self.getInputFromPort("Input PixelType"))
        self.setResult("Output Dimension", dim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Threshold Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Upper Value", (basic.Integer, 'Upper Value'))
        reg.add_input_port(cls, "Lower Value", (basic.Integer, 'Lower Value'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
