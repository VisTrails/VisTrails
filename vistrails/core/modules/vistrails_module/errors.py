###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
##  - Neither the name of the University of Utah nor the names of its 
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


class NeedsInputPort(Exception):
    def __init__(self, obj, port):
        self.obj = obj
        self.port = port
    def __str__(self):
        return "Module %s needs port %s" % (self.obj, self.port)


class IncompleteImplementation(Exception):
    def __str__(self):
        return "Module has incomplete implementation"


class ModuleBreakpoint(Exception):
    def __init__(self, module):
        self.module = module
        self.msg = "Hit breakpoint"
        self.errorTrace = ''

    def __str__(self):
        retstr = "Encoutered breakpoint at Module %s:\n" % (self.module)
        for k in self.module.__dict__.keys():
            retstr += "\t%s = %s\n" % (k, self.module.__dict__[k])

        inputs = self.examine_inputs()
        retstr += "\nModule has inputs:\n"

        for i in inputs.keys():
            retstr += "\t%s = %s\n" % (i, inputs[i])

        return retstr

    def examine_inputs(self):
        in_ports = self.module.__dict__["inputPorts"]
        inputs = {}
        for p in in_ports:
            inputs[p] = self.module.getInputListFromPort(p)

        return inputs

class ModuleError(Exception):

    """Exception representing a VisTrails module runtime error. This
exception is recognized by the interpreter and allows meaningful error
reporting to the user and to the logging mechanism."""

    def __init__(self, module, errormsg, abort=False):
        """ModuleError should be passed the module instance that signaled the
error and the error message as a string."""
        Exception.__init__(self, errormsg)
        self.abort = abort # force abort even if stopOnError is False
        self.module = module
        self.msg = errormsg
        import traceback
        self.errorTrace = traceback.format_exc()

class ModuleSuspended(ModuleError):
    """Exception representing a VisTrails module being suspended. Raising
    ModuleSuspended flags that the module is not ready to finish yet and
    that the workflow should be executed later.  A suspended module does
    not execute the modules downstream but all other branches will be
    executed. This is useful when executing external jobs where you do not
    want to block vistrails while waiting for the execution to finish.

    'queue' is a class instance that should provide a finished() method for
    checking if the job has finished

    'children' is a list of ModuleSuspended instances that is used for nested
    modules

    """

    def __init__(self, module, errormsg, queue=None, children=None):
        self.queue = queue
        self.children = children
        ModuleError.__init__(self, module, errormsg)

class ModuleErrors(Exception):
    """Exception representing a list of VisTrails module runtime errors.
    This exception is recognized by the interpreter and allows meaningful
    error reporting to the user and to the logging mechanism."""
    def __init__(self, module_errors):
        """ModuleErrors should be passed a list of ModuleError objects"""
        Exception.__init__(self, str(tuple(me.msg for me in module_errors)))
        self.module_errors = module_errors

class InvalidOutput(object):
    """ Specify an invalid result
    """
    pass
