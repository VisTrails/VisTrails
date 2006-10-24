import modules
import modules.module_registry
import modules.basic_modules
from modules.vistrails_module import Module, ModuleError, newModule, IncompleteImplementation

import os

################################################################################

class ImageMagick(Module):

    def compute(self):
        raise IncompleteImplementation

    def inputFileDescription(self):
        i = self.getInputFromPort("input")
        if self.hasInputFromPort('inputFormat'):
            return self.getInputFromPort('inputFormat') + ':' + i.name
        else:
            return i.name


class Convert(ImageMagick):

    __quiet = True

    def createOutputFile(self):
        if self.hasInputFromPort('outputFormat'):
            s = '.' + self.getInputFromPort('outputFormat')
            return self.interpreter.filePool.createFile(suffix=s)

    def geometryDescription(self):
        # if complete geometry is available, ignore rest
        if self.hasInputFromPort("geometry"):
            print "hasInputFromPort geometry"
            return self.getInputFromPort("geometry")
        elif self.hasInputFromPort("width"):
            print "hasInputFromPort width and height"
            w = self.getInputFromPort("width")
            h = self.getInputFromPort("height")
            return "'%sx%s'" % (w, h)
        else:
            raise ModuleError(self, "Needs geometry or width/height")

    def run(self, *args):
        cmdline = ("convert" + (" %s" * len(args))) % args
        if not self.__quiet:
            print cmdline
        r = os.system(cmdline)
        if r != 0:
            raise ModuleError("system call failed: '%s'" % cmdline)

    def compute(self):
        o = self.createOutputFile()
        i = self.inputFileDescription()
        self.run(i, o.name)
        self.setResult("output", o)
        


class Negate(Convert):

    def compute(self):
#        print "entered Negate.compute"
        o = self.createOutputFile()
        i = self.inputFileDescription()
#        print "input description: %s" % i
#        print "output description: %s" % odesc
        self.run(i,
                 "-negate",
                 o.name)
        self.setResult("output", o)


class Scale(Convert):

    def compute(self):
#        print "entered Scale.compute"
        o = self.createOutputFile()
        self.run(self.inputFileDescription(),
                 "-scale",
                 self.geometryDescription(),
                 o.name)
        self.setResult("output", o)


class GaussianBlur(Convert):

    def compute(self):
        (radius, sigma) = self.getInputFromPort('radiusSigma')
        o = self.createOutputFile()
        self.run(self.inputFileDescription(),
                 "-blur %sx%s" % (radius, sigma),
                 o.name)
        self.setResult("output", o)


class DetectEdges(Convert):

    def compute(self):
        radius = self.getInputFromPort('radius')
        o = self.createOutputFile()
        self.run(self.inputFileDescription(),
                 "-edge %s" % radius,
                 o.name)
        self.setResult("output", o)
        

noParamOptions = [("Negate", "-negate"),
                  ("EqualizeHistogram", "-equalize"),
                  ("Enhance", "-enhance"),
                  ("VerticalFlip", "-flip"),
                  ("HorizontalFlip", "-flop"),
                  ("FloydSteinbergDither", "-dither"),
                  ("IncreaseContrast", "-contrast"),
                  ("Despeckle", "-despeckle"),
                  ("Normalize", "-normalize")]


def noParamOptionsMethodDict(optionName):
    def compute(self):
        o = self.createOutputFile()
        i = self.inputFileDescription()
        self.run(i, optionName, o.name)
        self.setResult("output", o)
    return {'compute': compute}


floatParamOptions = [("DetectEdges", "-edge", "radius", "filter radius"),
                     ("Emboss", "-emboss", "radius", "filter radius"),
                     ("GammaCorrect", "-gamma", "gamma", "gamma correction factor"),
                     ("MedianFilter", "-median", "radius", "filter radius")]

def floatParamOptionsMethodDict(optionName, portName):
    def compute(self):
        o = self.createOutputFile()
        optionValue = self.getInputFromPort(portName)
        i = self.inputFileDescription()
        self.run(i, optionName, optionValue, o.name)
        self.setResult("output", o)
    return {'compute': compute}



################################################################################

def initialize(*args, **keywords):
    
    def parseErrorIfNotEqual(s, expected):
        if s != expected:
            err = "Parse error on version line. Was expecting '%s', got '%s'"
            raise Exception(err % (s, expected))
    
    print "ImageMagick VisTrails package"
    print "-----------------------------"
    print "Will test ImageMagick presence..."
    import tempfile
    (fd, name) = tempfile.mkstemp()
    os.close(fd)

    try:
        result = os.system("convert -version > %s" % name)
        if result != 0:
            raise Exception("ImageMagick does not seem to be present.")
        print "Ok, found ImageMagick"
        version_line = file(name).readlines()[0][:-1].split(' ')
        parseErrorIfNotEqual(version_line[0], 'Version:')
        parseErrorIfNotEqual(version_line[1], 'ImageMagick')
        print "Detected version %s" % version_line[2]
        global __version__
        __version__ = version_line[2]
    finally:
        os.unlink(name)

    reg = modules.module_registry
    basic = modules.basic_modules
    reg.addModule(ImageMagick)
    reg.addInputPort(ImageMagick, "input", (basic.File, 'the input file'))
    reg.addInputPort(ImageMagick, "inputFormat", (basic.String, 'coerce interpretation of file to this format'))
    reg.addInputPort(ImageMagick, "outputFormat", (basic.String, 'Force output to be of this format'))

    reg.addModule(Convert)
    reg.addInputPort(Convert, "geometry", (basic.String, 'ImageMagick geometry'))
    reg.addInputPort(Convert, "width", (basic.String, 'width of the geometry for operation'))
    reg.addInputPort(Convert, "height", (basic.String, 'height of the geometry for operation'))
    reg.addOutputPort(Convert, "output", (basic.File, 'the output file'))

    for (name, opt) in noParamOptions:
        m = newModule(Convert, name, noParamOptionsMethodDict(opt))
        reg.addModule(m)

    for (name, opt, paramName, paramComment) in floatParamOptions:
        m = newModule(Convert, name, floatParamOptionsMethodDict(opt, paramName))
        reg.addModule(m)
        reg.addInputPort(m, paramName, (basic.Float, paramComment))

    reg.addModule(GaussianBlur)
    reg.addInputPort(GaussianBlur, "radiusSigma", [(basic.Float, 'radius'), (basic.Float, 'sigma')])

    reg.addModule(Scale)
