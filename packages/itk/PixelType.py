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

from ITK import PixelType
  
class PixelTypeFloat(Module):
    my_namespace = "pixeltype"
    def compute(self):
        self._type = itk.F
        self.setResult("Pixel Type", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Pixel Type Float", namespace=cls.my_namespace)
        reg.add_output_port(cls, "Pixel Type", (PixelType, 'Pixel Type'))

class PixelTypeUnsignedChar(Module):
    my_namespace = "pixeltype"
    def compute(self):
        self._type = itk.UC
        self.setResult("Pixel Type", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Pixel Type Unsigned Char", namespace=cls.my_namespace)
        reg.add_output_port(cls, "Pixel Type", (PixelType, 'Pixel Type'))

class PixelTypeUnsignedShort(Module):
    my_namespace = "pixeltype"
    def compute(self):
        self._type = itk.US
        self.setResult("Pixel Type", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Pixel Type Unsigned Short", namespace=cls.my_namespace)
        reg.add_output_port(cls, "Pixel Type", (PixelType, 'Pixel Type'))

class PixelTypeRGB(Module):
    my_namespace = "pixeltype"
    def compute(self):
        self._type = itk.RGBPixel[itk.US]
        self.setResult("Pixel Type", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Pixel Type RGB", namespace=cls.my_namespace)
        reg.add_output_port(cls, "Pixel Type", (PixelType, 'Pixel Type'))
