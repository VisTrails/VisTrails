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
from PixelTypes import *

class Image(ITK):
    def setDimension(self, dim):
        self.dim = dim

    def setPixelType(self, pixeltype):
        self._type = pixeltype

    def getDimension(self):
        return self.dim

    def getPixelType(self):
        # Note:  This is still a PixelType object. 
        return self._type

    def compute(self):
        inIm = self.getInputFromPort("Image")
        if inIm:
            self.setDimension(inIm.getDimension())
            self.setPixelType(inIm.getPixelType())
        else:    
            self.setDimension(self.getInputFromPort("Dimension"))
            self.setPixelType(self.getInputFromPort("Pixel Type"))

        self._image = itk.Image[_type._type, dim]
        self._image.New()

        self.setResult("Image Pixel Type", self._type)
        self.setResult("Image Dimension", self.dim)
        self.setResult("Output Image", self)
