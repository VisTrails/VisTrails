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
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""The package afront defines a single module, Afront, which runs the meshing code
described in

Schreiner et al, Vis 2006
Schreiner et al, Eurographics 2006
Scheidegger et al, SGP 2005

"""

import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, newModule

import os

################################################################################

class Afront(Module):

    def run(self, args):
        cmdline = ("afront -nogui " + (" %s" * len(args)))
        cmdline = cmdline % tuple(args)
        os.system(cmdline)
        
    def compute(self):
        o = self.interpreter.filePool.create_file()
        args = []
        if not self.hasInputFromPort("file"):
            raise ModuleError("Needs input file")
        args.append(self.getInputFromPort("file").name)
        if self.hasInputFromPort("rho"):
            args.append("-rho")
            args.append(self.getInputFromPort("rho"))
        if self.hasInputFromPort("eta"):
            args.append("-eta")
            args.append(self.getInputFromPort("eta"))
        args.append("-outname")
        args.append(o.name)
        args.append("-tri")
        self.run(args)
        self.setResult("output", o)

# class HHM_File_to_VTK(Module):

#     def compute(self):
        

################################################################################

def initialize(*args, **keywords):

    print "Afront VisTrails package"
    print "------------------------"
    print "Testing afront presence..."

    result = os.system("afront >/dev/null 2>&1")
    if result != 0:
        raise Exception("afront does not seem to be present.")
    print "Ok, found afront"
    __version__ = 0.9
    
    reg = core.modules.module_registry
    reg.addModule(Afront)
    reg.addInputPort(Afront, "rho", (core.modules.basic_modules.Float, 'rho'))
    reg.addInputPort(Afront, "eta", (core.modules.basic_modules.Float, 'eta'))
    reg.addInputPort(Afront, "file", (core.modules.basic_modules.File, 'the file to process'))
    reg.addOutputPort(Afront, "output", (core.modules.basic_modules.File, 'the result'))
    
