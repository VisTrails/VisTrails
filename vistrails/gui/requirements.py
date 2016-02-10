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



import os
import sys

from vistrails.core.requirements import MissingRequirement, require_python_module


# This needs updating


def qt_available():
    try:
        require_python_module('sip')
        require_python_module('PyQt5.QtGui')
        require_python_module('PyQt5.QtOpenGL')
        require_python_module('PyQt5.QtSvg')
    except MissingRequirement:
        return False
    else:
        return True


def require_pyqt5():
    # Forces the use of PyQt5 (avoid PySide even if installed)
    # This is necessary at least for IPython
    if os.environ.get('QT_API', None) not in (None, 'pyqt'):
        sys.stderr.write("Warning: QT_API was set to %r, changing to 'pyqt'\n" %
                         os.environ['QT_API'])
    os.environ['QT_API'] = 'pyqt'

    if not qt_available():
        from vistrails.gui.bundles.installbundle import install
        r = install({
            'linux-debian': ['python3-pyqt5', 'python3-pyqt5.qtopengl',
                             'python3-pyqt5.qtsql', 'python3-pyqt5.qtsvg'],
            'linux-ubuntu': ['python3-pyqt5', 'python3-pyqt5.qtopengl',
                             'python3-pyqt5.qtsql', 'python3-pyqt5.qtsvg'],
            'linux-fedora': ['PyQt5'],
            'pip': ['PyQt>=5.0']})
        if not r:
            raise MissingRequirement('PyQt5')
