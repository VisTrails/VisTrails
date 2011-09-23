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
import os
import os.path
import stat
import subprocess
import glob

version = '0.9.0'
name = 'Provenance Challenge'
identifier = 'edu.utah.sci.vistrails.provenance2'

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

    def netpbm_cmd_line(self, cmd, *params):
	"""Runs a command-line command for the netpbm tools."""
        return list2cmdline([global_netpbmpath + cmd] + list(params))

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
	
	waitCode = 0
	try:
	    waitCode = process.wait()
	except OSError:
	    pass
        if waitCode != 0:
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
                                  image.baseName,
                                  ref.baseName,
                                  o.name,
                                  '-m',
                                  model,
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
        ofs = FileSet()
        ofs.baseName = o.name
        self.setResult("output", ofs)


class SoftMean(ProvenanceChallenge):
    """SoftMean executes the AIR softmean averaging tool on the input."""

    def compute(self):
        imageList = self.getInputFromPort("imageList")
        o = self.interpreter.filePool.create_file()
        cmd = self.air_cmd_line('softmean',
                                o.name,
                                'y',
                                'null',
                                *[f.baseName for f in imageList])
        self.run(cmd)
        ofs = FileSet()
        ofs.baseName = o.name
        self.setResult('output', ofs)

class Slicer(ProvenanceChallenge):
    """Slicer executes the FSL slicer tool on the input."""

    def compute(self):
        cmd = ['slicer']
        i = self.getInputFromPort("input")
        cmd.append(i.baseName)
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
        cmd = ['pgmtoppm white']
        i = self.getInputFromPort("input")
        cmd.append(i.name)
        o = self.interpreter.filePool.create_file(suffix='.ppm')
        cmd.append(' >')
        cmd.append(o.name)
        self.run(self.netpbm_cmd_line(*cmd))
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
        self.run(self.netpbm_cmd_line(*cmd))
        self.setResult('output', o)

class FileSet(ProvenanceChallenge):
    """FileSet stores a set of files related by a common filename base."""

    def compute(self):
        self.checkInputPort("baseName")
        n = self.getInputFromPort("baseName")
	if self.hasInputFromPort("file_hdr") and \
		self.hasInputFromPort("file_img"):
	    n1 = self.getInputFromPort("file_hdr").name
	    n2 = self.getInputFromPort("file_img").name
	    if n1.endswith('.hdr'):
		n1base = n1.rsplit('.hdr',1)[0]
	    else:
		n1base = n1
	    if n2.endswith('.img'):
		n2base = n2.rsplit('.img',1)[0]
	    else:
		n2base = n2
	    if n1base != n2base:
		o = self.interpreter.filePool.create_file()
		o1 = o.name + '.hdr'
		o2 = o.name + '.img'
		try:
		    core.system.link_or_copy(n1, o1)
		except OSError, e:
		    msg = "error creating tmp file '%s'" % o1
		    raise ModuleError(self, msg)
		try:
		    core.system.link_or_copy(n2, o2)
		except OSError, e:
		    msg = "error creating tmp file '%s'" % o2
		    raise ModuleError(self, msg)
	    else:
		self.baseName = n1base
	else:
	    self.baseName = n
        self.setResult("local_basename", self.baseName)

class FileSetSink(ProvenanceChallenge):
    """FileSetSink is a module that takes a file set and writes them
    in a user-specified location in the file system."""

    def compute(self):
        self.checkInputPort("fileSet")
        self.checkInputPort("outputBaseName")
        v1 = self.getInputFromPort("fileSet")
        v2 = self.getInputFromPort("outputBaseName")
        filenames = glob.glob('%s.*' % v1.baseName)
        for filename in filenames:
            try:
                outFilename = filename.replace(v1.baseName, v2, 1)
                core.system.link_or_copy(filename, outFilename)
            except OSError, e:
                if (self.hasInputFromPort("overrideFile") and
                    self.getInputFromPort("overrideFile")):
                    try:
                        os.unlink(outFilename)
                        core.system.link_or_copy(filename, outFilename)
                    except OSError, e:
                        msg = "(override true) Could not create file '%s'" % \
                            outFilename
                        raise ModuleError(self, msg)
                else:
                    msg = "Could not create file '%s': %s" % (outFilename, e)
                    raise ModuleError(self, msg)

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
    reg.add_input_port(AlignWarp, "image", (FileSet, 'the image file to be deformed'))
#    reg.add_input_port(AlignWarp, "image_header", (basic.File, 'the header of the image to be deformed'))
    reg.add_input_port(AlignWarp, "reference", (FileSet, 'the reference image'))
#    reg.add_input_port(AlignWarp, "reference_header", (basic.File, 'the header of the reference image'))
    reg.add_input_port(AlignWarp, "model", (basic.Integer, 'the deformation model'))
    reg.add_output_port(AlignWarp, "output", (basic.File, 'the output deformation'))

    reg.add_module(Reslice)
    reg.add_input_port(Reslice, "warp", (basic.File, 'the warping to be resliced'))
    reg.add_output_port(Reslice, "output", (FileSet, 'the new slice'))
    
    reg.add_module(SoftMean)
    reg.add_input_port(SoftMean, "imageList", (basic.List, 'image files'))
    reg.add_output_port(SoftMean, "output", (FileSet, 'average image'))

    reg.add_module(Slicer)
    reg.add_input_port(Slicer, "input", (FileSet, 'the input file to be sliced'))
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

    reg.add_module(FileSet)
    reg.add_input_port(FileSet, "file_hdr", basic.File)
    reg.add_input_port(FileSet, "file_img", basic.File)
    reg.add_input_port(FileSet, "baseName", basic.String)
    reg.add_output_port(FileSet, "self", FileSet)
    reg.add_output_port(FileSet, "local_basename", basic.String)

    reg.add_module(FileSetSink)
    reg.add_input_port(FileSetSink,  "fileSet", FileSet)
    reg.add_input_port(FileSetSink,  "outputBaseName", basic.String)
    reg.add_input_port(FileSetSink,  "overrideFile", basic.Boolean)
