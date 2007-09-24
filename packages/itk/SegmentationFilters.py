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
from ITK import *
from Filters import *

class IsolatedWatershedImageFilter(SegmentationFilter):
    def setSeed1(self, ind):
        self.filter_.SetSeed1(ind.ind_)

    def setSeed2(self, ind):
        self.filter_.SetSeed2(ind.ind_)

    def setReplace1(self, v):
        self.filter_.SetReplaceValue1(v)

    def setReplace2(self, v):
        self.filter_.SetReplaceValue2(v)

    def setThreshold(self, val):
        self.filter_.SetThreshold(val)

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

        if self.hasInputFromPort("Seed2"):
            self.setSeed2(self.getInputFromPort("Seed2"))
        if self.hasInputFromPort("ReplaceValue1"):
            self.setReplace1(self.getInputFromPort("ReplaceValue1"))
        if self.hasInputFromPort("ReplaceValue2"):
            self.setReplace2(self.getInputFromPort("ReplaceValue2"))
        if self.hasInputFromPort("Threshold"):
            self.setThreshold(self.getInputFromPort("Threshold"))
        
        self.setSeed1(self.getInputFromPort("Seed1"))

        self.filter_.Update()

        self.setResult("Output PixelType", out)
        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)

class ConnectedThresholdImageFilter(SegmentationFilter):
    def set_seed(self, ind):
        self.filter_.SetSeed(ind.ind_)

    def set_replace(self, v):
        self.filter_.SetReplaceValue(v)

    def set_lower(self, v):
        self.filter_.SetLower(v)

    def set_upper(self, v):
        self.filter_.SetUpper(v)

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

        self.set_seed(seed)
        self.set_replace(replace)
        self.set_upper(t_upper)
        self.set_lower(t_lower)

        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", out)
        self.setResult("Output Dimension", dim)

class ConfidenceConnectedImageFilter(SegmentationFilter):
    def compute(self):
        im = self.getInputFromPort("Input Image")
        if self.hasInputFromPort("Seed2D"):
            seed = self.getInputFromPort("Seed2D")
        else:
            seed = self.getInputFromPort("Seed3D")

        replace = self.getInputFromPort("Replace Value")
        multiplier = self.getInputFromPort("Multiplier")

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

        self.filter_.SetSeed(seed.ind_)

        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Output PixelType", out)
        self.setResult("Output Dimension", dim)
