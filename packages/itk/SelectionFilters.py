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

class RegionOfInterestImageFilter(Module):
    my_namespace="Filter|Selection"

    def setStart(self, start):
        if start == 2:
            self.index = self.getInputFromPort("Input 2D Index").ind_
        else:
            self.index = self.getInputFromPort("Input 3D Index").ind_

        self.region_.SetIndex(self.index)

    def compute(self):
        im = self.getInputFromPort("Input Image")

        if self.hasInputFromPort("Output PixelType"):
            out = self.getInputFromPort("Output PixelType")
        else:
            out = self.getInputFromPort("Input PixelType")

        inType = self.getInputFromPort("Input PixelType")._type
        outType = out._type
        indim = self.getInputFromPort("Input Dimension")
        outdim = self.getInputFromPort("Output Dimension")
        self.inIm = itk.Image[inType,indim]
        self.outIm = itk.Image[outType,outdim]

        self.filter_ = itk.RegionOfInterestImageFilter[self.inIm,self.outIm].New()

        if self.hasInputFromPort("Input Region"):
            self.region_ = self.getInputFromPort("Input Region").region_
        else:
            self.region_ = itk.ImageRegion[indim]()
            self.setStart(indim)
            self.region_.SetSize(self.getInputFromPort("Region Size").size_)

        self.filter_.SetRegionOfInterest(self.region_)
        self.filter_.SetInput(im)
        self.filter_.Update()
        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", out)
        self.setResult("Filter", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Region of Interest Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
        reg.add_output_port(cls, "Dimension", (basic.Integer, 'Dimension'))

class CastImageFilter(Module):
    my_namespace="Filter|Selection"
    def compute(self):
        im = self.getInputFromPort("Input Image")
        dim = self.getInputFromPort("Dimension")
        inType = self.getInputFromPort("Input PixelType")
        outType = self.getInputFromPort("Output PixelType")

        self.filter_ = itk.CastImageFilter[itk.Image[inType._type, dim], itk.Image[outType._type,dim]].New()
        self.filter_.SetInput(im)
        self.filter_.Update()
        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", outType)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Cast Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Dimension", (basic.Integer, 'Input Dimension'))
        reg.add_input_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'), True)
        reg.add_input_port(cls, "Input 2D Index", (Index2D, 'Input 2D Index'))
        reg.add_input_port(cls, "Input 3D Index", (Index3D, 'Input 3D Index'), True)
        reg.add_input_port(cls, "Region Size", (Size, 'Region Size'))
        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input Region", (Region, 'Input Region'), True)

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'))
        reg.add_output_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))


class ExtractImageFilter(Module):
    my_namespace="Filter|Selection"
    def compute(self):
        imVol = self.getInputFromPort("Input Volume")
        inDim = self.getInputFromPort("Input Dimension")
        outDim = self.getInputFromPort("Output Dimension")
        pType = self.getInputFromPort("Input PixelType")

        inType = itk.Image[pType._type,inDim]
        outType = itk.Image[pType._type,outDim]
        self.filter_ = itk.ExtractImageFilter[inType,outType].New()
        self.filter_.SetInput(imVol)

        region = self.getInputFromPort("Extraction Region")
        self.filter_.SetExtractionRegion(region.region_)
        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", pType)
        self.setResult("Dimension", outDim)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Extract Image Filter", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Volume", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input Dimension", (basic.Integer, 'Input Dimension'))
        reg.add_input_port(cls, "Output Dimension", (basic.Integer, 'Output Dimension'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Extraction Region", (Region, 'Extraction Region'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
        reg.add_output_port(cls, "Dimension", (basic.Integer, 'Dimension'))
