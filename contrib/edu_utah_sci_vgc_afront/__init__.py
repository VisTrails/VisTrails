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
"""The package afront defines three modules, Afront, AfrontIso and
MeshQualityHistogram. These run the meshing code described in

Schreiner et al, Vis 2006
Schreiner et al, Eurographics 2006
Scheidegger et al, SGP 2005

"""

from core.configuration import ConfigurationObject
from core.modules.vistrails_module import Module, ModuleError
from core.system import list2cmdline
import core.bundles
import core.modules.basic_modules
import core.modules.module_registry
import core.requirements
import os

configuration = ConfigurationObject(path=(None, str),
                                    debug=False)
version = '0.1.0'
identifier = 'edu.utah.sci.vgc.afront'
name = 'Afront'

################################################################################

class AfrontRun(object):

    def run(self, args):
        cmd = ['afront', '-nogui'] + args
        cmdline = list2cmdline(cmd)
        print cmdline
        os.system(cmdline)
#         if result != 0:
#             raise ModuleError(self, "Execution failed")


class Afront(Module, AfrontRun):
        
    def compute(self):
        o = self.interpreter.filePool.create_file(suffix='.m')
        args = []
        if not self.hasInputFromPort("file"):
            raise ModuleError(self, "Needs input file")
        args.append(self.getInputFromPort("file").name)
        if self.hasInputFromPort("rho"):
            args.append("-rho")
            args.append(str(self.getInputFromPort("rho")))
        if self.hasInputFromPort("eta"):
            args.append("-reduction")
            args.append(str(self.getInputFromPort("eta")))
        args.append("-outname")
        args.append(o.name)
        args.append("-tri")
        self.run(args)
        self.setResult("output", o)


class MeshQualityHistogram(Module, AfrontRun):

    def compute(self):
        o = self.interpreter.filePool.create_file(suffix='.csv')
        args = []
        self.checkInputPort("file")
        args.append(self.getInputFromPort("file").name)
        args.append('-histname')
        args.append(o.name)
        args.append('-histogram')
        self.run(args)
        self.setResult("output", o)

class AfrontIso(Afront):

    def compute(self):
        o = self.interpreter.filePool.create_file(suffix='.m')
        args = []
        if not self.hasInputFromPort("file"):
            raise ModuleError(self, "Needs input file")
        args.append(self.getInputFromPort("file").name)
        if self.hasInputFromPort("rho"):
            args.append("-rho")
            args.append(str(self.getInputFromPort("rho")))
        if self.hasInputFromPort("eta"):
            args.append("-eta")
            args.append(str(self.getInputFromPort("eta")))
        self.checkInputPort("iso")
        args.append("-outname")
        args.append(o.name)
        args.append("-tri")
        args.append(str(self.getInputFromPort("iso")))
        self.run(args)
        self.setResult("output", o)
        

################################################################################

def initialize():

    print "Afront VisTrails package"
    print "------------------------"
    print "Testing afront presence..."

#     if (not core.requirements.executable_file_exists('afront') and
#         not core.bundles.install({'linux-ubuntu': 'afront'})):
#         raise core.requirements.MissingRequirement("Afront")

    print "Ok, found afront"
    __version__ = 0.1
    
    reg = core.modules.module_registry
    reg.add_module(Afront)
    reg.add_input_port(Afront, "rho", (core.modules.basic_modules.Float, 'rho'))
    reg.add_input_port(Afront, "eta", (core.modules.basic_modules.Float, 'eta'))
    reg.add_input_port(Afront, "file", (core.modules.basic_modules.File, 'the file to process'))
    reg.add_output_port(Afront, "output", (core.modules.basic_modules.File, 'the result'))

    reg.add_module(MeshQualityHistogram)
    reg.add_input_port(MeshQualityHistogram, "file", core.modules.basic_modules.File)
    reg.add_output_port(MeshQualityHistogram, "output", core.modules.basic_modules.File)
    
    reg.add_module(AfrontIso)
    reg.add_input_port(AfrontIso, "iso", (core.modules.basic_modules.Float, 'iso'))
