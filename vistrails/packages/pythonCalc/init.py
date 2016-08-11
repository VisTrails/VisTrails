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

from __future__ import division

from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.config import IPort, OPort

###############################################################################
# PythonCalc
#
# A VisTrails package is simply a Python class that subclasses from
# Module.  For this class to be executable, it must define a method
# compute(self) that will perform the appropriate computations and set
# the results.
#
# Extra helper methods can be defined, as usual. In this case, we're
# using a helper method op(self, v1, v2) that performs the right
# operations.

class PythonCalc(Module):
    """PythonCalc is a module that performs simple arithmetic operations
    on its inputs.

    """

    # You need to report the ports the module wants to make
    # available. This is done by creating _input_ports and
    # _output_ports lists composed of InputPort (IPort) and OutputPort
    # (OPort) objects. These are simple ports that take only one
    # value. We'll see in later tutorials how to create compound ports
    # which can take a tuple of values.  Each port must specify its
    # name and signature.  The signature specifies the package
    # (e.g. "basic" which is shorthand for
    # "org.vistrails.vistrails.basic") and module (e.g. "Float").
    # Note that the third input port (op) has two other arguments.
    # The "enum" entry_type specifies that there are a set of options
    # the user should choose from, and the values then specifies those
    # options.
    _input_ports = [IPort(name="value1", signature="basic:Float"),
                    IPort(name="value2", signature="basic:Float"),
                    IPort(name="op", signature="basic:String",
                          entry_type="enum", values=["+", "-", "*", "/"])]
    _output_ports = [OPort(name="value", signature="basic:Float")]

    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        Module.__init__(self)

    # This is the method you should implement in every module that
    # will be executed directly. VisTrails does not use the return
    # value of this method.
    def compute(self):
        # get_input is a method defined in Module that returns
        # the value stored at an input port. If there's no value
        # stored on the port, the method will return None.
        v1 = self.get_input("value1")
        v2 = self.get_input("value2")

        # You should call set_output to store the appropriate results
        # on the ports.  In this case, we are only storing a
        # floating-point result, so we can use the number types
        # directly. For more complicated data, you should
        # return an instance of a VisTrails Module. This will be made
        # clear in further examples that use these more complicated data.
        self.set_output("value", self.op(v1, v2))

    def op(self, v1, v2):
        op = self.get_input("op")
        if op == '+':
            return v1 + v2
        elif op == '-':
            return v1 - v2
        elif op == '*':
            return v1 * v2
        elif op == '/':
            return v1 / v2
        # If a module wants to report an error to VisTrails, it should raise
        # ModuleError with a descriptive error. This allows the interpreter
        # to capture the error and report it to the caller of the evaluation
        # function.
        raise ModuleError(self, "unrecognized operation: '%s'" % op)

# VisTrails will only load the modules specified in the _modules list.
# This list contains all of the modules a package defines.
_modules = [PythonCalc,]
