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

"""module responsible for smartly importing python modules, checking
for necessary installs."""

import traceback

import core.bundles.installbundle
from core import debug

##############################################################################

class PyImportException(Exception):
    def __init__(self, py_module_name, traceback_str):
        self.py_module_name = py_module_name
        self.traceback_str = traceback_str
    def __str__(self):
        return ("Installation of python package '%s' failed.\n%s" % \
                    (self.py_module_name, self.traceback_str))

class PyImportBug(PyImportException):
    def __str__(self):
        return ("Installation of package '%s' successful, "
                "but import still failed.\n%s" % \
                    (self.py_module_name, self.traceback_str))

def _vanilla_import(module_name):
    return __import__(module_name, globals(), locals(), [])

def unknown_py_import(module_name, package_name):
    return _vanilla_import(module_name)

def py_import(module_name, dependency_dictionary):
    """Tries to import a python module. If unsuccessful, tries to install
the appropriate bundle and then reimport. py_import tries to be smart
about which system it runs on."""
    try:
        result = _vanilla_import(module_name)
        return result
    except ImportError, e:
        pass
    debug.warning("Import of python module '%s' failed. "
                  "Will try to install bundle." % module_name)

    success = core.bundles.installbundle.install(dependency_dictionary)

    if not success:
        raise PyImportException(module_name, traceback.format_exc())
    try:
        result = _vanilla_import(module_name)
        return result
    except ImportError, e:
        raise PyImportBug(module_name, traceback.format_exc())

##############################################################################
