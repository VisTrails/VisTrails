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
import core.modules
from core.modules.vistrails_module import Module, ModuleError

import itk

class ITK(Module):
    def compute(self):
        pass

class PixelType(ITK):
    def compute(self):
        pass

class Filter(ITK):
    def compute(self):
        pass

class Index2D(ITK):
    def compute(self):
	self.ind_ = itk.Index[2]()
	self.x_ = self.getInputFromPort("X Index")
	self.y_ = self.getInputFromPort("Y Index")

	self.ind_.SetElement(0,self.x_)
	self.ind_.SetElement(1,self.y_)

	self.setResult("Index", self)

class Index3D(ITK):
    def compute(self):
	self.ind_ = itk.Index[3]()
	self.x_ = self.getInputFromPort("X Index")
	self.y_ = self.getInputFromPort("Y Index")
	self.z_ = self.getInputFromPort("Z Index")

	self.ind_.SetElement(0,self.x_)
	self.ind_.SetElement(1,self.y_)
	self.ind_.SetElement(2,self.z_)

	self.setResult("Index", self)