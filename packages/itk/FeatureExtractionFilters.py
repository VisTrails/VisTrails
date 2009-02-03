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

class GradientMagnitudeRecursiveGaussianImageFilter(Module):
    my_namespace = "Filter|Feature"

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
        sigma_ = self.getInputFromPort("Sigma")
        inType = itk.Image[inType, dim]
        outType= itk.Image[outType, dim]

        self.filter_ = itk.GradientMagnitudeRecursiveGaussianImageFilter[inType, outType].New(im)
        self.filter_.SetSigma(sigma_)
        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)
        self.setResult("Output PixelType", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Gradient Magnitude Recursive Gaussian Image Filter", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Input Filter", (Filter, 'Input Filter'))
        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'))
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Sigma", (basic.Float, 'Sigma'))
        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'))
