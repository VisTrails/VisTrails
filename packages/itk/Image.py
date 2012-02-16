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
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import itk
import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from ITK import *
from PixelType import *

class Image(Module, ITK):
    my_namespace="disregard"

    def getPixelType(self):
        return self._type

    def getDim(self):
        return self.dim

    def getImg(self):
        return self.inIm

    def setImg(self, img):
        self.inIm = img

    def setDim(self, dim):
        self.dim = dim

    def setPixelType(self, pt):
        self._type = pt
    
    def compute(self):
        self.inIm = self.getInputFromPort("Image")
        self.dim = self.getInputFromPort("Dimension")
        self._type = self.getInputFromPort("Pixel Type")

        self.setResult("Output Image", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Image", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Pixel Type", (PixelType, 'Pixel Type'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Image", (Image, 'Image'))

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
