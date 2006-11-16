"""ImageMagick package for VisTrails.

This package defines a set of modules that perform some of the
operations exposed by the ImageMagick package.

"""

import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, newModule, IncompleteImplementation

import os
import subprocess

################################################################################

class ImageMagick(Module):
    """ImageMagick is the base Module for all Modules in the ImageMagick
package. It simply defines some helper methods for subclasses."""

    def compute(self):
        raise IncompleteImplementation

    def input_file_description(self):
        """Returns a fully described name in the ImageMagick format. For example,
a file stored in PNG format may be described by its extension

        - 'graphic.png' indicates the filename 'graphic.png', using the PNG
        file format.

        - 'graphic:png' indicates the filename 'graphic', still using the PNG
        file format."""
        i = self.getInputFromPort("input")
        if self.hasInputFromPort('inputFormat'):
            return self.getInputFromPort('inputFormat') + ':' + i.name
        else:
            return i.name


class Convert(ImageMagick):
    """Convert is the base Module for VisTrails Modules in the ImageMagick
package that deal with operations on images. Convert is a bit of a misnomer since
the 'convert' tool does more than simply file format conversion. Each subclass
has a descriptive name of the operation it implements."""

    __quiet = True

    def create_output_file(self):
        """Creates a File with the output format given by the
outputFormat port."""
        if self.hasInputFromPort('outputFormat'):
            s = '.' + self.getInputFromPort('outputFormat')
            return self.interpreter.filePool.createFile(suffix=s)

    def geometry_description(self):
        """returns a string with the description of the geometry as
indicated by the appropriate ports (geometry or width and height)"""
        # if complete geometry is available, ignore rest
        if self.hasInputFromPort("geometry"):
            return self.getInputFromPort("geometry")
        elif self.hasInputFromPort("width"):
            w = self.getInputFromPort("width")
            h = self.getInputFromPort("height")
            return "'%sx%s'" % (w, h)
        else:
            raise ModuleError(self, "Needs geometry or width/height")

    def run(self, *args):
        """run(*args), runs ImageMagick's 'convert' on a shell, passing all
arguments to the program."""        
        cmdline = ("convert" + (" %s" * len(args))) % args
        if not self.__quiet:
            print cmdline
        r = os.system(cmdline)
        if r != 0:
            raise ModuleError("system call failed: '%s'" % cmdline)

    def compute(self):
        o = self.create_output_file()
        i = self.input_file_description()
        self.run(i, o.name)
        self.setResult("output", o)
        

class Negate(Convert):
    """Negate performs the two's complement negation of the image."""

    def compute(self):
        o = self.create_output_file()
        i = self.input_file_description()
        self.run(i,
                 "-negate",
                 o.name)
        self.setResult("output", o)


class Scale(Convert):
    """Scale rescales the input image to the given geometry description."""

    def compute(self):
        o = self.create_output_file()
        self.run(self.input_file_description(),
                 "-scale",
                 self.geometry_description(),
                 o.name)
        self.setResult("output", o)


class GaussianBlur(Convert):
    """GaussianBlur convolves the image with a Gaussian filter of given radius
and standard deviation."""

    def compute(self):
        (radius, sigma) = self.getInputFromPort('radiusSigma')
        o = self.create_output_file()
        self.run(self.input_file_description(),
                 "-blur %sx%s" % (radius, sigma),
                 o.name)
        self.setResult("output", o)


no_param_options = [("Negate", "-negate"),
                    ("EqualizeHistogram", "-equalize"),
                    ("Enhance", "-enhance"),
                    ("VerticalFlip", "-flip"),
                    ("HorizontalFlip", "-flop"),
                    ("FloydSteinbergDither", "-dither"),
                    ("IncreaseContrast", "-contrast"),
                    ("Despeckle", "-despeckle"),
                    ("Normalize", "-normalize")]


def no_param_options_method_dict(optionName):
    """Creates a method dictionary for a module that takes no extra
parameters. This dictionary will be used to dynamically create a
VisTrails module."""
   
    def compute(self):
        o = self.create_output_file()
        i = self.input_file_description()
        self.run(i, optionName, o.name)
        self.setResult("output", o)

    return {'compute': compute}


float_param_options = [("DetectEdges", "-edge", "radius", "filter radius"),
                       ("Emboss", "-emboss", "radius", "filter radius"),
                       ("GammaCorrect", "-gamma", "gamma", "gamma correction factor"),
                       ("MedianFilter", "-median", "radius", "filter radius")]

def float_param_options_method_dict(optionName, portName):
    """Creates a method dictionary for a module that has one port
taking a floating-point value. This dictionary will be used to
dynamically create a VisTrails module."""

    def compute(self):
        o = self.create_output_file()
        optionValue = self.getInputFromPort(portName)
        i = self.input_file_description()
        self.run(i, optionName, optionValue, o.name)
        self.setResult("output", o)

    return {'compute': compute}



################################################################################

def initialize(*args, **keywords):
    
    def parse_error_if_not_equal(s, expected):
        if s != expected:
            err = "Parse error on version line. Was expecting '%s', got '%s'"
            raise Exception(err % (s, expected))
    
    print "ImageMagick VisTrails package"
    print "-----------------------------"
    print "Will test ImageMagick presence..."

    process = subprocess.Popen("convert -version",
                               shell=True,
                               stdout=subprocess.PIPE)
    result = process.wait()
    if result != 0:
        raise Exception("ImageMagick does not seem to be present.")
    print "Ok, found ImageMagick"
    version_line = process.stdout.readlines()[0][:-1].split(' ')
    parse_error_if_not_equal(version_line[0], 'Version:')
    parse_error_if_not_equal(version_line[1], 'ImageMagick')
    print "Detected version %s" % version_line[2]
    global __version__
    __version__ = version_line[2]

    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    reg.addModule(ImageMagick)
    reg.addInputPort(ImageMagick, "input", (basic.File, 'the input file'))
    reg.addInputPort(ImageMagick, "inputFormat", (basic.String, 'coerce interpretation of file to this format'))
    reg.addInputPort(ImageMagick, "outputFormat", (basic.String, 'Force output to be of this format'))

    reg.addModule(Convert)
    reg.addInputPort(Convert, "geometry", (basic.String, 'ImageMagick geometry'))
    reg.addInputPort(Convert, "width", (basic.String, 'width of the geometry for operation'))
    reg.addInputPort(Convert, "height", (basic.String, 'height of the geometry for operation'))
    reg.addOutputPort(Convert, "output", (basic.File, 'the output file'))

    for (name, opt) in no_param_options:
        m = newModule(Convert, name, no_param_options_method_dict(opt))
        reg.addModule(m)

    for (name, opt, paramName, paramComment) in float_param_options:
        m = newModule(Convert, name, float_param_options_method_dict(opt, paramName))
        reg.addModule(m)
        reg.addInputPort(m, paramName, (basic.Float, paramComment))

    reg.addModule(GaussianBlur)
    reg.addInputPort(GaussianBlur, "radiusSigma", [(basic.Float, 'radius'), (basic.Float, 'sigma')])

    reg.addModule(Scale)
