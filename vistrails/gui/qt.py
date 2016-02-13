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

import importlib.util
import os
import types


################################################################################

qtapi = None
qtapi_env = os.environ.get('QT_API')

import pdb; pdb.set_trace()

# Try PyQt5
if qtapi is None and qtapi_env in (None, 'pyqt5'):
    if (importlib.util.find_spec('QtCore', 'PyQt5') is not None and
            importlib.util.find_spec('QtGui', 'PyQt5') is not None):
        from PyQt5 import QtCore
        from PyQt5 import QtGui
        from PyQt5 import QtWidgets
        from PyQt5 import QAxContainer
        from PyQt5 import QtPrintSupport
        from PyQt5 import QtXmlPatterns
        from PyQt5 import QtSvg
        from PyQt5 import QtWebKitWidgets
        from PyQt5 import QtOpenGL
        qtapi = os.environ['QT_API'] = 'pyqt5'
# Try PyQt4
if qtapi is None and qtapi_env in (None, 'pyqt', 'pyqt4'):
    try:
        if (importlib.util.find_spec('QtCore', 'PyQt4') is None or
                importlib.util.find_spec('QtGui', 'PyQt4') is None):
            raise ImportError
        import sip
    except ImportError:
        pass
    else:
        api2_classes = [
            'QData', 'QDateTime', 'QString', 'QTextStream',
            'QTime', 'QUrl', 'QVariant'
        ]
        for cl in api2_classes:
            try:
                sip.setapi(cl, 2)
            except ValueError:
                pass
        from PyQt4 import QtCore
        from PyQt4 import QtGui
        QtWidgets = QtGui
        from PyQt4 import QAxContainer
        from PyQt4 import QtPrintSupport
        from PyQt4 import QtXmlPatterns
        from PyQt4 import QtSvg
        from PyQt4 import QtWebKitWidgets
        from PyQt4 import QtOpenGL
        qtapi = os.environ['QT_API'] = 'pyqt'
# Oh no
if qtapi is None:
    if qtapi_env is not None:
        if qtapi_env in ('pyqt', 'pyqt4', 'pyqt5'):
            raise ImportError("QT_API is currently set to '%s', which is not "
                              "available" % qtapi_env)
        else:
            raise ImportError("QT_API is currently set to '%s', which is not "
                              "supported" % qtapi_env)
    else:
        raise ImportError("No suitable version of PyQt was found; PyQt4 or "
                          "PyQt5 is required")

################################################################################

class qt_super(object):

    def __init__(self, class_, obj):
        self._class = class_
        self._obj = obj

    def __getattr__(self, attr):
        s = super(self._class, self._obj)
        try:
            return getattr(s, attr)
        except AttributeError as e:
            mro = type(self._obj).mro()
            try:
                ix = mro.index(self._class)
            except ValueError:
                raise TypeError("qt_super: obj must be an instance of class")

            for class_ in mro[ix+1:]:
                try:
                    unbound_meth = getattr(class_, attr)
                    return types.MethodType(unbound_meth, self._obj, class_)
                except AttributeError:
                    pass
            raise e

################################################################################

_appHolder = None

def createBogusQtGuiApp(argv=["bogus"]):
    """createBogusQtGuiApp creates a bogus QtApplication so we can create
    qobjects during test runs.

    """
    class BogusApplication(QtWidgets.QApplication):
        def __init__(self):
            QtWidgets.QApplication.__init__(self, argv)
    global _appHolder
    if QtWidgets.QApplication.instance():
        _appHolder = QtWidgets.QApplication.instance()
    if not _appHolder:
        _appHolder = BogusApplication()
    return _appHolder

def destroyBogusQtApp():
    global _appHolder
    _appHolder = None

def qt_version():
    return [int(i)
            for i in
            QtCore.qVersion().split('.')]

################################################################################

okToCreateQObjects = False
