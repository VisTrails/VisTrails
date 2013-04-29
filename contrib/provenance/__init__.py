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
"""This package defines a set of methods that perform the command-line
tools necesary for the task designed for the first Provenance Challenge:

http://twiki.ipaw.info

This VisTrails package requires three software packages to be installed:

AIR - Automated Image Registration: http://bishopw.loni.ucla.edu/AIR5/
FSL - http://www.fmrib.ox.ac.uk/fsl/
netpbm - http://netpbm.sourceforge.net/

"""

from core.modules.vistrails_module import Module, ModuleError, new_module
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.utils
from core.system import list2cmdline
import os
import os.path
import stat
import subprocess

version = '0.9.0'
name = 'Provenance Challenge'
identifier = 'edu.utah.sci.vistrails.provenance'
################################################################################

global_airpath = ""
global_fslpath = ""
global_netpbmpath = ""

class ProvenanceChallenge(Module):
    """ProvenanceChallenge is the base Module for all Modules in the provenance
package. It simply define helper methods for subclasses."""

    __quiet = True
    __programsQuiet = True
    
    def air_cmd_line(self, cmd, *params):
        """Runs a command-line command for the AIR tools."""
        return list2cmdline([global_airpath + cmd] + list(params))

    def fsl_cmd_line(self, cmd, *params):
        """Runs a command-line command for the FSL tools."""
        return ('FSLOUTPUTTYPE=NIFTI_GZ ' +
                list2cmdline([global_fslpath + cmd] + list(params)))

    def run(self, cmd):
        if not self.__quiet:
            print cmd
        if self.__programsQuiet:
            cmd = '(' + cmd + ') 2>&1 >/dev/null' 
        r = os.system(cmd)
        if r != 0:
            raise ModuleError(self, "system call failed: '%s'" % cmd)


class AIRHeaderFile(core.modules.basic_modules.File):
    """AIRHeaderFile subclasses File to annotate the execution with header
file information for later querying."""

    def get_header_annotations(self):
        """Returns the header information for the file using the AIR scanheader
tool."""
        process = subprocess.Popen(global_airpath + 'scanheader ' + self.name,
                                   shell=True,
                                   stdout=subprocess.PIPE)
        if process.wait() != 0:
            raise ModuleError(self, "Could not open header file " + self.name)

        result = {}
        lines = core.utils.no_interrupt(process.stdout.readlines)
        for l in lines:
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
        core.modules.basic_modules.File.compute(self)
        d = self.get_header_annotations()
        self.annotate(d)


class AlignWarp(ProvenanceChallenge):
    """AlignWarp executes the AIR warping tool on the input."""

    def compute(self):
        image = self.getInputFromPort("image")
        ref = self.getInputFromPort("reference")
        model = self.getInputFromPort("model")
        o = self.interpreter.filePool.create_file(suffix='.warp')
        cmd = self.air_cmd_line('align_warp',
                                image.name,
                                ref.name,
                                o.name,
                                '-m',
                                str(model),
                                '-q')
        self.run(cmd)
        self.setResult("output", o)


class Reslice(ProvenanceChallenge):
    """AlignWarp executes the AIR reslicing tool on the input."""

    def compute(self):
        warp = self.getInputFromPort("warp")
        o = self.interpreter.filePool.create_file()
        cmd = self.air_cmd_line('reslice',
                                 warp.name,
                                 o.name)
        self.run(cmd)
        self.setResult("output", o)


class SoftMean(ProvenanceChallenge):
    """SoftMean executes the AIR softmean averaging tool on the input."""

    def compute(self):
        imageList = self.getInputFromPort("imageList")
        o = self.interpreter.filePool.create_file(suffix='.hdr')
        cmd = self.air_cmd_line('softmean',
                                o.name,
                                'y',
                                'null',
                                *[f.name for f in imageList])
        self.run(cmd)
        self.setResult('output', o)


class Slicer(ProvenanceChallenge):
    """Slicer executes the FSL slicer tool on the input."""

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
        o = self.interpreter.filePool.create_file(suffix='.pgm')
        cmd.append(o.name)
        self.run(self.fsl_cmd_line(*cmd))
        self.setResult('output', o)


class PGMToPPM(ProvenanceChallenge):
    """PGMToPPM executes the netpbm pgmtoppm tool on the input."""

    def compute(self):
        cmd = ['pgmtoppm', 'white']
        i = self.getInputFromPort("input")
        cmd.append(i.name)
        o = self.interpreter.filePool.create_file(suffix='.ppm')
        cmd.append(' >')
        cmd.append(o.name)
        self.run(list2cmdline(cmd))
        self.setResult('output', o)
        

class PNMToJpeg(ProvenanceChallenge):
    """PGMToPPM executes the netpbm pnmtojpeg tool on the input."""

    def compute(self):
        cmd = ['pnmtojpeg']
        i = self.getInputFromPort("input")
        cmd.append(i.name)
        o = self.interpreter.filePool.create_file(suffix='.jpg')
        cmd.append(' >')
        cmd.append(o.name)
        self.run(list2cmdline(cmd))
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
    reg.add_module(ProvenanceChallenge)
    
    reg.add_module(AlignWarp)
    reg.add_input_port(AlignWarp, "image", (basic.File, 'the image file to be deformed'))
    reg.add_input_port(AlignWarp, "image_header", (basic.File, 'the header of the image to be deformed'))
    reg.add_input_port(AlignWarp, "reference", (basic.File, 'the reference image'))
    reg.add_input_port(AlignWarp, "reference_header", (basic.File, 'the header of the reference image'))
    reg.add_input_port(AlignWarp, "model", (basic.Integer, 'the deformation model'))
    reg.add_output_port(AlignWarp, "output", (basic.File, 'the output deformation'))

    reg.add_module(Reslice)
    reg.add_input_port(Reslice, "warp", (basic.File, 'the warping to be resliced'))
    reg.add_output_port(Reslice, "output", (basic.File, 'the new slice'))
    
    reg.add_module(SoftMean)
    reg.add_input_port(SoftMean, "imageList", (basic.List, 'image files'))
    reg.add_output_port(SoftMean, "output", (basic.File, 'average image'))

    reg.add_module(Slicer)
    reg.add_input_port(Slicer, "input", (basic.File, 'the input file to be sliced'))
    reg.add_input_port(Slicer, "slice_x", (basic.Float, 'sagittal slice with given value'))
    reg.add_input_port(Slicer, "slice_y", (basic.Float, 'coronal slice with given value'))
    reg.add_input_port(Slicer, "slice_z", (basic.Float, 'axial slice with given value'))
    reg.add_output_port(Slicer, "output", (basic.File, 'slice output'))

    reg.add_module(PGMToPPM)
    reg.add_input_port(PGMToPPM, "input", (basic.File, "input"))
    reg.add_output_port(PGMToPPM, "output", (basic.File, "output"))

    reg.add_module(PNMToJpeg)
    reg.add_input_port(PNMToJpeg, "input", (basic.File, "input"))
    reg.add_output_port(PNMToJpeg, "output", (basic.File, "output"))

    reg.add_module(AIRHeaderFile)
