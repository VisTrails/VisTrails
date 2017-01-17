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

"""Online checking for required runtime components.
"""

from __future__ import division

import os
import sys

import vistrails.core.bundles.installbundle
from vistrails.core.configuration import get_vistrails_configuration
import vistrails.core.system


def python_module_exists(module_name):
    """Checks that a Python module is importable, and return True or False.
    """
    if module_name in sys.modules:
        return True
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def executable_file_exists(filename):
    """Checks whether the given executable file name is in the PATH.
    """
    result = vistrails.core.system.executable_is_in_path(filename)
    if not result:
        result = vistrails.core.system.executable_is_in_path(filename)
    return result


def require_python_module(module_name, dep_dict=None):
    """Fail if the given Python module isn't importable and can't be installed.

    This raises `MissingRequirements` and is thus suitable for use in a
    package's `package_requirements()` function. If `dep_dict` is provided, it
    will try to install the requirement before failing, using
    :func:`~vistrails.core.bundles.installbundle.install`.

    :raises MissingRequirement: on error
    """
    exists = python_module_exists(module_name)
    if (not exists and
            dep_dict and
            getattr(get_vistrails_configuration(), 'installBundles')):
        vistrails.core.bundles.installbundle.install(dep_dict)
        exists = python_module_exists(module_name)
    if not exists:
        raise MissingRequirement(module_name)


def require_executable(filename):
    """Fail if the given executable file name is not in PATH.

    This raises `MissingRequirements` and is thus suitable for use in a
    package's `package_requirements()` function.

    :raises MissingRequirement: on error
    """
    if not executable_file_exists(filename):
        raise MissingRequirement(filename)


class MissingRequirement(Exception):
    """Indicates that a package won't run because it's missing dependencies.
    """
    def __init__(self, req):
        self.requirement = req

    def __str__(self):
        return "Missing Requirement: %s" % self.requirement


##############################################################################

def setNewPyQtAPI():
    import sip
    # We now use the new PyQt API - IPython needs it
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)


def qt_available():
    try:
        require_python_module('sip')
        setNewPyQtAPI()
        require_python_module('PyQt4.QtGui')
        require_python_module('PyQt4.QtOpenGL')
    except MissingRequirement:
        return False
    else:
        return True


def require_pyqt4_api2():
    # Forces the use of PyQt4 (avoid PySide even if installed)
    # This is necessary at least for IPython
    if os.environ.get('QT_API', None) not in (None, 'pyqt'):
        sys.stderr.write("Warning: QT_API was set to %r, changing to 'pyqt'\n" %
                         os.environ['QT_API'])
    os.environ['QT_API'] = 'pyqt'

    if not qt_available():
        from vistrails.gui.bundles.installbundle import install
        r = install({
            'linux-debian': ['python-qt4', 'python-qt4-gl', 'python-qt4-sql'],
            'linux-ubuntu': ['python-qt4', 'python-qt4-gl', 'python-qt4-sql'],
            'linux-fedora': ['PyQt4'],
            'pip': ['PyQt<5.0']})
        if not r:
            raise MissingRequirement('PyQt4')
        setNewPyQtAPI()
