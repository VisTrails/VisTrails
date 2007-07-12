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

class RescaleIntensityImageFilter(IntensityFilter):
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

class SigmoidImageFilter(IntensityFilter):
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

class ThresholdImageFilter(IntensityFilter):
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
