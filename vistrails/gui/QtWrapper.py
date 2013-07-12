"""Adapted from http://askubuntu.com/a/141641

This compatibility layer allows to use either PySide or PyQt4 as the Qt
binding. It will choose what's available, defaulting on PySide, unless the
QT_API environment variable is set.
"""


import os
import sys


default_binding = 'PySide'


def set_sip_api():
    import sip
    api2_classes = [
            'QData', 'QDateTime', 'QString', 'QTextStream',
            'QTime', 'QUrl', 'QVariant',
            ]
    for cl in api2_classes:
        sip.setapi(cl, 2)


def try_import(what):
    if what == 'PySide':
        try:
            from PySide import QtCore, QtGui
            return True
        except:
            return False
    else:
        try:
            set_sip_api()
            from PyQt4 import QtCore, QtGui
            return True
        except:
            return False


env_api = os.environ.get('QT_API', '').lower()
if env_api == 'pyside':
    sys.stderr.write("Using binding PySide from QT_API\n")
    binding = 'PySide'
elif env_api == 'pyqt' or env_api == 'pyqt4':
    sys.stderr.write("Using binding PyQt4 from QT_API\n")
    binding = 'PyQt4'
elif env_api:
    sys.stderr.write("QT_API set to '%s' -- failing\n" % env_api)
    raise ImportError("QT_API environment variable is set to '%s' -- please "
                      "use either 'pyside' or 'pyqt'" % env_api)
else:
    if not try_import(default_binding):
        other_binding = 'PyQt4' if default_binding == 'PySide' else 'PySide'
        if not try_import(other_binding):
            binding = default_binding
        else:
            binding = other_binding
            sys.stderr.write("Binding %s not available -- using %s\n" % (
                       default_binding, binding))
    else:
        binding = default_binding
    if binding == default_binding:
        sys.stderr.write("Using default binding %s\n" % binding)


if binding == 'PySide':
    from PySide import QtCore, QtGui, QtNetwork, QtSvg
    sys.modules[__name__ + '.QtCore'] = QtCore
    sys.modules[__name__ + '.QtGui'] = QtGui
    sys.modules[__name__ + '.QtNetwork'] = QtNetwork
    sys.modules[__name__ + '.QtSvg'] = QtSvg
    try:
        from PySide import QtOpenGL
        sys.modules[__name__ + '.QtOpenGL'] = QtOpenGL
    except ImportError:
        pass
    try:
        from PySide import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass
    # This will be passed on to new versions of matplotlib
    os.environ['QT_API'] = 'pyside'
    def QtLoadUI(uifile):
        from PySide import QtUiTools
        loader = QtUiTools.QUiLoader()
        uif = QtCore.QFile(uifile)
        uif.open(QtCore.QFile.ReadOnly)
        result = loader.load(uif)
        uif.close()
        return result
elif binding == 'PyQt4':
    set_sip_api()
    from PyQt4 import QtCore, QtGui, QtNetwork, QtSvg
    sys.modules[__name__ + '.QtCore'] = QtCore
    sys.modules[__name__ + '.QtGui'] = QtGui
    sys.modules[__name__ + '.QtNetwork'] = QtNetwork
    sys.modules[__name__ + '.QtSvg'] = QtSvg
    try:
        from PyQt4 import QtOpenGL
        sys.modules[__name__ + '.QtOpenGL'] = QtOpenGL
    except ImportError:
        pass
    try:
        from PyQt4 import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
    os.environ['QT_API'] = 'pyqt'
    def QtLoadUI(uifile):
        from PyQt4 import uic
        return uic.loadUi(uifile)
else:
    raise ImportError("Python binding not specified")


def get_qt_binding_name():
    return binding


__all__ = ['QtCore', 'QtGui', 'QtLoadUI', 'get_qt_binding_name']
