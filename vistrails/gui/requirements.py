###############################################################################
##
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

import os
import sys

from vistrails.core.requirements import MissingRequirement, require_python_module


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
