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

class IsolatedWatershedImageFilter(Module):
    my_namespace="Filter|Segmentation"

    def compute(self):
        im = self.getInputFromPort("Input Image")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        dim = self.getInputFromPort("Dimension")
        inType = itk.Image[inType,dim]
        outType = itk.Image[outType,dim]

        self.filter_ = itk.IsolatedWatershedImageFilter[inType,outType].New(im)

        if self.hasInputFromPort("Seed1"):
            self.filter_.SetSeed1(self.getInputFromPort("Seed1").ind_)

        if self.hasInputFromPort("Seed2"):
            self.filter_.SetSeed2(self.getInputFromPort("Seed2").ind_)

        if self.hasInputFromPort("ReplaceValue1"):
            self.filter_.SetReplaceValue1(self.getInputFromPort("ReplaceValue1"))

        if self.hasInputFromPort("ReplaceValue2"):
            self.filter_.SetReplaceValue2(self.getInputFromPort("ReplaceValue2"))

        if self.hasInputFromPort("Threshold"):
            self.filter_.SetThreshold(self.getInputFromPort("Threshold"))

        self.filter_.Update()

        self.setResult("Output PixelType", out)
        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Isolated Watershed Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Seed1", (Index2D, 'Seed 1 Location'))

        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'), True)
        reg.add_input_port(cls, "Threshold", (basic.Float, 'Threshold'), True)
        reg.add_input_port(cls, "Seed2", (Index2D, 'Seed 2 Location'))
        reg.add_input_port(cls, "ReplaceValue1", (basic.Float, 'Replacement Value 1'), True);
        reg.add_input_port(cls, "ReplaceValue2", (basic.Float, 'Replacement Value 2'), True);

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))

class ConnectedThresholdImageFilter(Module):
    my_namespace="Filter|Segmentation"

    def compute(self):
        im = self.getInputFromPort("Input Image")
        if self.hasInputFromPort("Seed2D"):
            seed = self.getInputFromPort("Seed2D")
        else:
            seed = self.getInputFromPort("Seed3D")
        replace = self.getInputFromPort("Replace Value")
        t_lower = self.getInputFromPort("Lower Value")
        t_upper = self.getInputFromPort("Upper Value")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        dim = self.getInputFromPort("Dimension")
        inType = itk.Image[inType,dim]
        outType = itk.Image[outType,dim]

        self.filter_ = itk.ConnectedThresholdImageFilter[inType,outType].New(im)

        self.filter_.SetSeed(seed.ind_)
        self.filter_.SetReplaceValue(replace)
        self.filter_.SetLower(t_lower)
        self.filter_.SetUpper(t_upper)

        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", out)
        self.setResult("Output Dimension", dim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Connected Threshold Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Seed2D", (Index2D, 'Seed Point'))
        reg.add_input_port(cls, "Seed3D", (Index3D, 'Seed Point'))
        reg.add_input_port(cls, "Replace Value", (basic.Float, 'Replacement Value'))
        reg.add_input_port(cls, "Upper Value", (basic.Float, 'Upper Threshold Value'))
        reg.add_input_port(cls, "Lower Value", (basic.Float, 'Lower Threshold Value'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))

class ConfidenceConnectedImageFilter(Module):
    my_namespace="Filter|Segmentation"

    def compute(self):
        im = self.getInputFromPort("Input Image")
        if self.hasInputFromPort("Seed2D"):
            seed = self.getInputFromPort("Seed2D")
        else:
            seed = self.getInputFromPort("Seed3D")

        replace = self.getInputFromPort("Replace Value")
        multiplier = self.getInputFromPort("Multiplier")
        iterations = self.getInputFromPort("Iterations")
        radius = self.getInputFromPort("Neighborhood Radius")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        dim = self.getInputFromPort("Dimension")
        inType = itk.Image[inType,dim]
        outType = itk.Image[outType,dim]

        self.filter_ = itk.ConfidenceConnectedImageFilter[inType,outType].New(im)

        self.filter_.SetReplaceValue(replace)
        self.filter_.SetMultiplier(multiplier)
        self.filter_.SetNumberOfIterations(iterations)
        self.filter_.SetInitialNeighborhoodRadius(radius)

        self.filter_.SetSeed(seed.ind_)

        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", out)
        self.setResult("Output Dimension", dim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Confidence Connected Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Seed2D", (Index2D, 'Seed Point'))
        reg.add_input_port(cls, "Seed3D", (Index3D, 'Seed Point'))
        reg.add_input_port(cls, "Replace Value", (basic.Float, 'Replacement Value'))
        reg.add_input_port(cls, "Multiplier", (basic.Float, 'Multiplier'))
        reg.add_input_port(cls, "Iterations", (basic.Float, 'Iterations'))
        reg.add_input_port(cls, "Neighborhood Radius", (basic.Float, 'Neighborhood Radius'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))

class IsolatedConnectedImageFilter(Module):
    my_namespace="Filter|Segmentation"

    def compute(self):
        im = self.getInputFromPort("Input Image")
#only 2D for now, needs fix
        seed1 = self.getInputFromPort("Seed1")
        seed2 = self.getInputFromPort("Seed2")

        replace = self.getInputFromPort("Replace Value")
        t_lower = self.getInputFromPort("Lower Value")
        t_upper = self.getInputFromPort("Upper Value")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        dim = self.getInputFromPort("Dimension")
        inType = itk.Image[inType,dim]
        outType = itk.Image[outType,dim]

        self.filter_ = itk.IsolatedConnectedImageFilter[inType,outType].New(im)

        self.filter_.SetReplaceValue(replace)
        self.filter_.SetLower(t_lower)
        self.filter_.SetUpperValueLimit(t_upper)
        self.filter_.SetSeed1(seed1.ind_)
        self.filter_.SetSeed2(seed2.ind_)

        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", out)
        self.setResult("Output Dimension", dim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Isolated Connected Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Seed1", (Index2D, 'Seed Point'))
        reg.add_input_port(cls, "Seed2", (Index2D, 'Seed Point'))
        reg.add_input_port(cls, "Replace Value", (basic.Integer, 'Replacement Value'))
        reg.add_input_port(cls, "Upper Value", (basic.Integer, 'Upper Threshold Value'))
        reg.add_input_port(cls, "Lower Value", (basic.Integer, 'Lower Threshold Value'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
