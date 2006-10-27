import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, newModule

import os
import os.path
import stat

################################################################################

global_airpath = ""
global_fslpath = ""
global_netpbmpath = ""

class ProvenanceChallenge(Module):

    __quiet = True
    __programsQuiet = True
    
    def air_cmd_line(self, cmd, *params):
        return (global_airpath + cmd + " %s" * len(params)) % params

    def fsl_cmd_line(self, cmd, *params):
        return ('FSLOUTPUTTYPE=NIFTI_GZ ' + global_fslpath + cmd + " %s" * len(params)) % params

    def run(self, cmd):
        if not self.__quiet:
            print cmd
        if self.__programsQuiet:
            cmd = '(' + cmd + ') 2>&1 >/dev/null' 
        r = os.system(cmd)
        if r != 0:
            raise ModuleError(self, "system call failed: '%s'" % cmd)


class AIRHeaderFile(core.modules.basic_modules.File):

    def get_header_annotations(self):
        try:
            x = self.interpreter.filePool.createFile()
            os.system(global_airpath + 'scanheader ' + self.name + '> ' +
                      x.name)
            f = file(x.name, 'r')
        except:
            raise ModuleError(self, "Could not open header file " + self.name)

        result = {}
        for l in f:
            l = l[:-1]
            if not l:
                continue
            entries = l.split('=')
            if len(entries) != 2:
                raise ModuleError(self,
                                  "Error parsing line '%s' of header %s" %
                                  (l[:-1], self.name))
            result[entries[0]] = entries[1]
        return result

    def compute(self):
        modules.basic_modules.File.compute(self)
        d = self.get_header_annotations()
        self.annotate(d)


class AlignWarp(ProvenanceChallenge):

    def compute(self):
        image = self.getInputFromPort("image")
        ref   = self.getInputFromPort("reference")
        model = self.getInputFromPort("model")
        o     = self.interpreter.filePool.createFile(suffix='.warp')
        cmd   = self.air_cmd_line('align_warp',
                                  image.name,
                                  ref.name,
                                  o.name,
                                  '-m',
                                  model,
                                  '-q')
        self.run(cmd)
        self.setResult("output", o)


class Reslice(ProvenanceChallenge):

    def compute(self):
        warp = self.getInputFromPort("warp")
        o    = self.interpreter.filePool.createFile()
        cmd  = self.air_cmd_line('reslice',
                                 warp.name,
                                 o.name)
        self.run(cmd)
        self.setResult("output", o)


class SoftMean(ProvenanceChallenge):

    def compute(self):
        imageList = self.getInputFromPort("imageList")
        o        = self.interpreter.filePool.createFile(suffix='.hdr')
        cmd = self.air_cmd_line('softmean',
                                o.name,
                                'y',
                                'null',
                                *[f.name for f in imageList])
        self.run(cmd)
        self.setResult('output', o)


class Slicer(ProvenanceChallenge):

    def compute(self):
        cmd = ['slicer']
        i = self.getInputFromPort("input")
        cmd.append(i.name)
        if self.hasInputFromPort("slice_x"):
            cmd.append('-x')
            cmd.append(str(self.getInputFromPort("slice_x")))
        elif self.hasInputFromPort("slice_y"):
            cmd.append('-y')
            cmd.append(str(self.getInputFromPort("slice_y")))
        elif self.hasInputFromPort("slice_z"):
            cmd.append('-z')
            cmd.append(str(self.getInputFromPort("slice_z")))
        o = self.interpreter.filePool.createFile(suffix='.pgm')
        cmd.append(o.name)
        self.run(self.fsl_cmd_line(*cmd))
        self.setResult('output', o)


class PGMToPPM(ProvenanceChallenge):

    def compute(self):
        cmd = ['pgmtoppm white']
        i = self.getInputFromPort("input")
        cmd.append(i.name)
        o = self.interpreter.filePool.createFile(suffix='.ppm')
        cmd.append(' >')
        cmd.append(o.name)
        self.run(" ".join(cmd))
        self.setResult('output', o)
        

class PNMToJpeg(ProvenanceChallenge):

    def compute(self):
        cmd = ['pnmtojpeg']
        i = self.getInputFromPort("input")
        cmd.append(i.name)
        o = self.interpreter.filePool.createFile(suffix='.jpg')
        cmd.append(' >')
        cmd.append(o.name)
        self.run(" ".join(cmd))
        self.setResult('output', o)

################################################################################

def checkProgram(fileName):
    return os.path.isfile(fileName) and os.stat(fileName) & 005

def initialize(airpath=None, fslpath=None, netpbmpath=None, *args, **kwargs):
    print "Initializing Provenance Challenge Package"

    if not airpath:
        print "airpath not specified or incorrect: Will assume AIR tools are on the path"
    else:
        print "Will use AIR tools from ", airpath
        global global_airpath
        global_airpath = airpath + '/'

    if not fslpath:
        print "fslpath not specified or incorrect: Will assume fsl tools are on the path"
    else:
        print "Will use FSL tools from ", fslpath
        global global_fslpath
        global_fslpath = fslpath + '/'

    if not netpbmpath:
        print "netpbmpath not specified or incorrect: Will assume netpbm tools are on the path"
    else:
        print "Will use netpbm tools from ", netpbmpath
        global global_netpbmpath
        global_netpbmpath = netpbmpath + '/'
        
    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    reg.addModule(ProvenanceChallenge)
    
    reg.addModule(AlignWarp)
    reg.addInputPort(AlignWarp, "image", (basic.File, 'the image file to be deformed'))
    reg.addInputPort(AlignWarp, "image_header", (basic.File, 'the header of the image to be deformed'))
    reg.addInputPort(AlignWarp, "reference", (basic.File, 'the reference image'))
    reg.addInputPort(AlignWarp, "reference_header", (basic.File, 'the header of the reference image'))
    reg.addInputPort(AlignWarp, "model", (basic.Integer, 'the deformation model'))
    reg.addOutputPort(AlignWarp, "output", (basic.File, 'the output deformation'))

    reg.addModule(Reslice)
    reg.addInputPort(Reslice, "warp", (basic.File, 'the warping to be resliced'))
    reg.addOutputPort(Reslice, "output", (basic.File, 'the new slice'))
    
    reg.addModule(SoftMean)
    reg.addInputPort(SoftMean, "imageList", (basic.List, 'image files'))
    reg.addOutputPort(SoftMean, "output", (basic.File, 'average image'))

    reg.addModule(Slicer)
    reg.addInputPort(Slicer, "input", (basic.File, 'the input file to be sliced'))
    reg.addInputPort(Slicer, "slice_x", (basic.Float, 'sagittal slice with given value'))
    reg.addInputPort(Slicer, "slice_y", (basic.Float, 'coronal slice with given value'))
    reg.addInputPort(Slicer, "slice_z", (basic.Float, 'axial slice with given value'))
    reg.addOutputPort(Slicer, "output", (basic.File, 'slice output'))

    reg.addModule(PGMToPPM)
    reg.addInputPort(PGMToPPM, "input", (basic.File, "input"))
    reg.addOutputPort(PGMToPPM, "output", (basic.File, "output"))

    reg.addModule(PNMToJpeg)
    reg.addInputPort(PNMToJpeg, "input", (basic.File, "input"))
    reg.addOutputPort(PNMToJpeg, "output", (basic.File, "output"))

    reg.addModule(AIRHeaderFile)
