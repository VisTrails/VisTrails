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
import core.modules
from core.modules.vistrails_module import Module, ModuleError

import itk

class ITK(object):
    my_namespace="itk"

class PixelType(Module, ITK):
    my_namespace = "disregard"

    def compute(self):
        pass

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Pixel Type", namespace=cls.my_namespace)

class Filter(Module, ITK):
    my_namespace="disregard"

    def compute(self):
        pass

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Filter", namespace=cls.my_namespace)


class Index2D(Module, ITK):
    my_namespace = "index"

    def compute(self):
        self.ind_ = itk.Index[2]()
        self.x_ = self.getInputFromPort("X Index")
        self.y_ = self.getInputFromPort("Y Index")

        self.ind_.SetElement(0,self.x_)
        self.ind_.SetElement(1,self.y_)

        self.setResult("Index", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Index2D", namespace=cls.my_namespace)

        reg.add_input_port(cls, "X Index", (basic.Integer, 'X Index'))
        reg.add_input_port(cls, "Y Index", (basic.Integer, 'Y Index'))

        reg.add_output_port(cls, "Index", (Index2D, 'Index'))

class Index3D(Module, ITK):
    my_namespace = "index"
    def compute(self):
        self.ind_ = itk.Index[3]()
        self.x_ = self.getInputFromPort("X Index")
        self.y_ = self.getInputFromPort("Y Index")
        self.z_ = self.getInputFromPort("Z Index")

        self.ind_.SetElement(0,self.x_)
        self.ind_.SetElement(1,self.y_)
        self.ind_.SetElement(2,self.z_)

        self.setResult("Index", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Index3D", namespace=cls.my_namespace)

        reg.add_input_port(cls, "X Index", (basic.Integer, 'X Index'))
        reg.add_input_port(cls, "Y Index", (basic.Integer, 'Y Index'))
        reg.add_input_port(cls, "Z Index", (basic.Integer, 'Z Index'))

        reg.add_output_port(cls, "Index", (Index3D, 'Index'))

class Size(Module, ITK):
    my_namespace = "size"
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        self.size_ = itk.Size[dim]()
        self.x = self.getInputFromPort("Element 1")
        self.y = self.getInputFromPort("Element 2")
        if dim > 2:
            self.z = self.getInputFromPort("Element 3")

        self.size_.SetElement(0,self.x)
        self.size_.SetElement(1,self.y)

        if dim > 2:
            self.size_.SetElement(2,self.z)

        self.setResult("Size",self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Size", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Element 1", (basic.Integer, 'Element 1'))
        reg.add_input_port(cls, "Element 2", (basic.Integer, 'Element 2'))
        reg.add_input_port(cls, "Element 3", (basic.Integer, 'Element 3'))

        reg.add_output_port(cls, "Size", (Size, 'Size'))

class Region(Module, ITK):
    my_namespace = "region"
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        self.region_ = itk.ImageRegion[dim]()
        self.region_.SetSize(self.getInputFromPort("Size").size_)
        if dim > 2:
            self.region_.SetIndex(self.getInputFromPort("Input 3D Index").ind_)
        else:
            self.region_.SetIndex(self.getInputFromPort("Input 2D Index").ind_)

        self.setResult("Region", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Region", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Size", (Size, 'Size'))
        reg.add_input_port(cls, "Input 2D Index", (Index2D, 'Input 2D Index'))
        reg.add_input_port(cls, "Input 3D Index", (Index3D, 'Input 3D Index'), True)

        reg.add_output_port(cls, "Region", (Region, 'Region'))

class Kernel(Module, ITK):
    my_namespace = "kernel"
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        radius = self.getInputFromPort("Radius")
        self.kernel = itk.strel(dim,radius)

        self.setResult("Kernel", self.kernel)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="Kernel", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_input_port(cls, "Radius", (basic.Integer, 'Radius'))

        reg.add_output_port(cls, "Kernel", (Kernel, 'Kernel'))
