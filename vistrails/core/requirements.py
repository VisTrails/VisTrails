###############################################################################
##
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

"""module that allows online inspection of environment to test presence of
runtime components such as binaries, libraries, other python modules, etc."""

import sys
import core.system

##############################################################################

def python_module_exists(module_name):
    """python_module_exists(module_name): Boolean.
Returns if python module of given name can be safely imported."""
    
    try:
        sys.modules[module_name]
        return True
    except KeyError:
        pass
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False
    

def executable_file_exists(filename):
    """executable_file_exists(filename): Boolean.
Returns if certain file is in current path and is executable."""
    result = core.system.executable_is_in_path(filename)
    if result == "":
        result = core.system.executable_is_in_pythonpath(filename)
    return result != ""

# FIXME: Add documentation.

def require_python_module(module_name):
    if not python_module_exists(module_name):
        raise MissingRequirement(module_name)

def require_executable(filename):
    if not executable_file_exists(filename):
        raise MissingRequirement(filename)

def check_all_vistrails_requirements():
    pass

    # check scipy
#     try:
#         require_python_module('scipy')
#     except MissingRequirement:
#         r = core.bundles.installbundle.install({'linux-ubuntu': 'python-scipy'})
#         if not r:
#             raise
        

##############################################################################

class MissingRequirement(Exception):
    """Raise this exception in packages when necessary items are missing."""
    def __init__(self, req):
        self.requirement = req
    def __str__(self):
        return "Missing Requirement: %s" % self.requirement

