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
	inType = self.getInputFromPort("Input PixelType")._type
	outType = self.getInputFromPort("Output PixelType")._type
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

	self.setResult("Output Image", self.filter_.GetOutput())
	self.setResult("Filter", self)
