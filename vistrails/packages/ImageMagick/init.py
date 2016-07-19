###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

##############################################################################
# Changes
#
# 20130827 (by Remi)
#    CombineRGBA can now also accept RGB
#    Factored code common between Convert and CombineRGBA
#    Removes 'geometry' and related ports from most modules, as they were
#    *already ignored* except by the Scale module
#
# 20090521 (by Emanuele)
#    Added path configuration option so imagemagick does not to be in the path
#    Removed ImageMagick presence check
#
# 20081002:
#    Added CombineRGBA to create image from channels.
#    Moved quiet to configuration
#    Fixed bug with GaussianBlur

from __future__ import division

from vistrails.core import debug
import vistrails.core.modules.basic_modules as basic
import vistrails.core.modules.module_registry
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    new_module, IncompleteImplementation
from vistrails.core.system import list2cmdline

import os

################################################################################

class ImageMagick(Module):
    """ImageMagick is the base Module for all Modules in the ImageMagick
    package. It simply defines some helper methods for subclasses.

    """

    def compute(self):
        raise IncompleteImplementation

    def input_file_description(self):
        """Returns a fully described name in the ImageMagick format.

        For example, a file stored in PNG format may be described by:
        - 'graphic.png' indicates the filename 'graphic.png', using
        the PNG file format.
        - 'png:graphic' indicates the filename 'graphic', still using
        the PNG file format.

        """
        i = self.get_input("input")
        if self.has_input('inputFormat'):
            return self.get_input('inputFormat') + ':' + i.name
        else:
            return i.name

    def create_output_file(self):
        """Creates a File with the output format given by the outputFormat
        port.

        """
        if self.has_input('outputFormat'):
            s = '.' + self.get_input('outputFormat')
            return self.interpreter.filePool.create_file(suffix=s)
        else:
            return self.interpreter.filePool.create_file(suffix='.png')

    def run(self, *args):
        """run(*args), runs ImageMagick's 'convert' on a shell, passing all
        arguments to the program.

        """
        path = None
        if configuration.check('path'):
            path = configuration.path
        if path:
            cmd = os.path.join(path,'convert')
        else:
            cmd = 'convert'    
        cmd = [cmd] + list(args)
        cmdline = list2cmdline(cmd)
        if not configuration.quiet:
            debug.log(cmdline)
        r = os.system(cmdline)
        if r != 0:
            raise ModuleError(self, "system call failed: %r" % cmdline)


class Convert(ImageMagick):
    """Convert is the base Module for VisTrails Modules in the ImageMagick
package that transform a single input into a single output. Each subclass has
a descriptive name of the operation it implements."""

    def compute(self):
        o = self.create_output_file()
        i = self.input_file_description()
        self.run(i, o.name)
        self.set_output("output", o)


class CombineRGBA(ImageMagick):
    """Combines channels as separate images into a single RGBA file."""

    def compute(self):
        o = self.create_output_file()
        r = self.get_input("r")
        g = self.get_input("g")
        b = self.get_input("b")
        a = self.force_get_input("a")

        if a is not None:
            self.run(r.name, g.name, b.name, a.name,
                     '-channel', 'RGBA',
                     '-combine', o.name)
        else:
            self.run(r.name, g.name, b.name,
                     '-channel', 'RGB',
                     '-combine', o.name)

        self.set_output("output", o)


class Scale(Convert):
    """Scale rescales the input image to the given geometry
    description.

    """

    def geometry_description(self):
        """returns a string with the description of the geometry as
indicated by the appropriate ports (geometry or width and height)"""
        # if complete geometry is available, ignore rest
        if self.has_input("geometry"):
            return self.get_input("geometry")
        elif self.has_input("width"):
            w = self.get_input("width")
            h = self.get_input("height")
            return "'%sx%s'" % (w, h)
        else:
            raise ModuleError(self, "Needs geometry or width/height")

    def compute(self):
        o = self.create_output_file()
        self.run(self.input_file_description(),
                 "-scale",
                 self.geometry_description(),
                 o.name)
        self.set_output("output", o)


class GaussianBlur(Convert):
    """GaussianBlur convolves the image with a Gaussian filter of given
    radius and standard deviation.

    """

    def compute(self):
        (radius, sigma) = self.get_input('radiusSigma')
        o = self.create_output_file()
        self.run(self.input_file_description(),
                 "-blur",
                 "%sx%s" % (radius, sigma),
                 o.name)
        self.set_output("output", o)


no_param_options = [("Negate", "-negate",
                     """Negate performs the two's complement negation of the image."""
                     ),
                    ("EqualizeHistogram", "-equalize", None),
                    ("Enhance", "-enhance", None),
                    ("VerticalFlip", "-flip", None),
                    ("HorizontalFlip", "-flop", None),
                    ("FloydSteinbergDither", "-dither", None),
                    ("IncreaseContrast", "-contrast", None),
                    ("Despeckle", "-despeckle", None),
                    ("Normalize", "-normalize", None)]


def no_param_options_method_dict(optionName):
    """Creates a method dictionary for a module that takes no extra
    parameters. This dictionary will be used to dynamically create a
    VisTrails module.

    """
   
    def compute(self):
        o = self.create_output_file()
        i = self.input_file_description()
        self.run(i, optionName, o.name)
        self.set_output("output", o)

    return {'compute': compute}


float_param_options = [("DetectEdges", "-edge", "radius", "filter radius"),
                       ("Emboss", "-emboss", "radius", "filter radius"),
                       ("GammaCorrect", "-gamma", "gamma", "gamma correction factor"),
                       ("MedianFilter", "-median", "radius", "filter radius")]

def float_param_options_method_dict(optionName, portName):
    """Creates a method dictionary for a module that has one port taking a
    floating-point value. This dictionary will be used to dynamically
    create a VisTrails module.

    """

    def compute(self):
        o = self.create_output_file()
        optionValue = self.get_input(portName)
        i = self.input_file_description()
        self.run(i, optionName, str(optionValue), o.name)
        self.set_output("output", o)

    return {'compute': compute}



################################################################################

def initialize():
    def parse_error_if_not_equal(s, expected):
        if s != expected:
            err = "Parse error on version line. Was expecting '%s', got '%s'"
            raise RuntimeError(err % (s, expected))

    reg = vistrails.core.modules.module_registry.get_module_registry()

    reg.add_module(ImageMagick, abstract=True)

    reg.add_module(Convert)
    reg.add_input_port(Convert, "input", (basic.File, 'the input file'))
    reg.add_input_port(Convert, "inputFormat", (basic.String, 'coerce interpretation of file to this format'))
    reg.add_output_port(Convert, "output", (basic.File, 'the output file'))
    reg.add_input_port(Convert, "outputFormat", (basic.String, 'Force output to be of this format'))

    for (name, opt, doc_string) in no_param_options:
        m = new_module(Convert, name, no_param_options_method_dict(opt),
                      docstring=doc_string)
        reg.add_module(m)

    for (name, opt, paramName, paramComment) in float_param_options:
        m = new_module(Convert, name, float_param_options_method_dict(opt, paramName))
        reg.add_module(m)
        reg.add_input_port(m, paramName, (basic.Float, paramComment))

    reg.add_module(GaussianBlur)
    reg.add_input_port(GaussianBlur, "radiusSigma", [(basic.Float, 'radius'), (basic.Float, 'sigma')])

    reg.add_module(Scale)
    reg.add_input_port(Scale, "geometry", (basic.String, 'ImageMagick geometry'))
    reg.add_input_port(Scale, "width", (basic.String, 'width of the geometry for operation'))
    reg.add_input_port(Scale, "height", (basic.String, 'height of the geometry for operation'))

    reg.add_module(CombineRGBA)
    reg.add_input_port(CombineRGBA, "r", basic.File)
    reg.add_input_port(CombineRGBA, "g", basic.File)
    reg.add_input_port(CombineRGBA, "b", basic.File)
    reg.add_input_port(CombineRGBA, "a", basic.File, optional=True)
    reg.add_input_port(CombineRGBA, "outputFormat", basic.String)
    reg.add_output_port(CombineRGBA, "output", basic.File)

################################################################################

