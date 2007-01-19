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
"""The TetGenBridge package wraps the TetGen library, exposing the tetrahedralize function as well as the input/output classes."""

import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import TetGen
import CreateTestSurf


# The port that wraps a tetgenio class.
class tetgenio_wrapper(Module):
    def __init__(self) :
        self.data = TetGen.tetgenio()
    

class tetrahedralize(Module):
    """tetrahedralize corresponds to the TetGen function of the same name"""


    def __init__(self):
        Module.__init__(self)


    def compute(self):
        switches = None
        if self.hasInputFromPort("switches") :
            switches = self.getInputFromPort("switches")
            print switches
        if self.hasInputFromPort("tgio in") :
            tgio_in = self.getInputFromPort("tgio in").data

        print "input has %d nodes!" % tgio_in.numberofpoints
        tgio_in.save_nodes("/tmp/tgIN.vt")
        tgio_in.save_poly("/tmp/tgIN.vt")
        out  = tetgenio_wrapper()
        TetGen.tetrahedralize(switches, tgio_in, out.data)
        print "Done making tets"

        self.setResult("tgio out", out)

      


def initialize(*args, **keywords):
    reg = core.modules.module_registry

    #calls the lib with function of the same name.
    reg.addModule(tetrahedralize)

    # command line switches that tell tetrahedralize what to do.
    reg.addInputPort(tetrahedralize, "switches",
                     (core.modules.basic_modules.String, 'tetgen options'))
    # input mesh information.
    reg.addInputPort(tetrahedralize, "tgio in",
                     (tetgenio_wrapper, 'input data'))
    # output mesh information.
    reg.addOutputPort(tetrahedralize, "tgio out",
                      (tetgenio_wrapper, 'output data'))

    #holds the tetgenio class, and acts as a port.
    reg.addModule(tetgenio_wrapper)

    # get support and testing modules registered.
    CreateTestSurf.initialize(reg)

