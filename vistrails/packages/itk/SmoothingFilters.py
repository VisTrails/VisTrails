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
from ITK import *
from Filters import *

class CurvatureAnisotropicDiffusionFilter(SmoothingFilter):
    def compute(self):
	im = self.getInputFromPort("Input Image")

	if self.hasInputFromPort("Output PixelType"):
	    out = self.getInputFromPort("Output PixelType")
	else:
	    out = self.getInputFromPort("Input PixelType")

	inType = self.getInputFromPort("Input PixelType")._type
	outType = out._type
	indim = self.getInputFromPort("Input Dimension")
	outdim = indim
	self.inIm = itk.Image[inType,indim]
	self.outIm = itk.Image[outType,outdim]

	self.filter_ = itk.CurvatureAnisotropicDiffusionImageFilter[self.inIm,self.outIm].New(im)

	if self.hasInputFromPort("Iterations"):
	    iterations = self.getInputFromPort("Iterations")
        else:
	    iterations = 5

	if self.hasInputFromPort("TimeStep"):
	    timestep = self.getInputFromPort("TimeStep")
	else:
	    if indim == 2:
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

	self.setResult("Output Image", self.filter_.GetOutput())
	self.setResult("Output PixelType", out)
	self.setResult("Filter", self)
	self.setResult("Output Dimension", outdim)


class RecursiveGaussianImageFilter(SmoothingFilter):
    def compute(self):
	im = self.getInputFromPort("Input Image")

	if self.hasInputFromPort("Output PixelType"):
	    out = self.getInputFromPort("Output PixelType")
	else:
	    out = self.getInputFromPort("Input PixelType")

	inType = self.getInputFromPort("Input PixelType")._type
	outType = out._type
	indim = self.getInputFromPort("Input Dimension")
	outdim = indim
	self.inIm = itk.Image[inType,indim]
	self.outIm = itk.Image[outType,outdim]

	self.filter_ = itk.RecursiveGaussianImageFilter[self.inIm,self.outIm].New(im)

	sigma = self.getInputFromPort("Sigma")
	self.filter_.SetSigma(sigma)

	self.filter_.Update()

	self.setResult("Output Image", self.filter_.GetOutput())
	self.setResult("Output PixelType", out)
	self.setResult("Output Dimension", outdim)