#!/usr/bin/env python

##############################################################################
# Basic information

import sys
import platform

print "Python:"
print "  Basic version: %s.%s.%s" % (sys.version_info[0],
                                     sys.version_info[1],
                                     sys.version_info[2], )
print "  Full version: " + sys.version.replace('\n', ' ')
print

def c(s):
    return s or "<COULD NOT DETERMINE>"

print "System:"
print "  Type: " + c(platform.system())
print "  Architecture: " + c(platform.architecture()[0])
print "  Machine: " + c(platform.machine())
print "  Platform: " + c(platform.platform())
print "  Processor: " + c(platform.processor())
print

##############################################################################

print "Libraries:"

try:
    import sip
    print "  sip installed."
    print "    version: " + sip.SIP_VERSION_STR
except ImportError:
    print "  sip NOT installed."
print

try:
    import PyQt4.Qt
    print "  PyQt installed."
    print "    Qt version: " + PyQt4.Qt.QT_VERSION_STR
    print "    PyQt version: " + PyQt4.Qt.PYQT_VERSION_STR
except ImportError:
    print "  PyQt NOT installed."
print

try:
    import vtk
    print "  VTK installed."
    print "    VTK short version: " + vtk.vtkVersion().GetVTKVersion()
    print "    VTK full version: " + vtk.vtkVersion().GetVTKSourceVersion()
except ImportError:
    print "  VTK NOT installed."
