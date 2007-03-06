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

class RegionOfInterestImageFilter(SelectionFilter):
    def setSize(self, size):
	self.region_.SetSize(size)

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
	    self.setSize(self.getInputFromPort("Region Size").size_)

	self.filter_.SetRegionOfInterest(self.region_)
	self.filter_.SetInput(im)
	self.filter_.Update()
	self.setResult("Output Image", self.filter_.GetOutput())
	self.setResult("Output PixelType", out)
	self.setResult("Filter", self)
	self.setResult("Output Dimension", outdim)

class CastImageFilter(SelectionFilter):
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
	self.setResult("Dimension", dim)