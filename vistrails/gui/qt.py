############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""The only reason this module exists is to try to prevent QObjects
from being created before a QApplication gets constructed. The problem
with a QObject being constructed before a QApplication is that signals
and slots do not get connected, leading to hard-to-spot bugs.

Notice that there is no hard enforcement - if the client code does not
ask for permission, nothing stops it from creating QObjects (which
won't work correctly). Even worse, nothing stops a malicious object
from setting okToCreateQObjects directly.

As the python saying goes, 'we are all consenting adults here'."""

import inspect
from PyQt4 import QtGui, QtCore

################################################################################

class DisallowedCaller(Exception):
    """This expection is raised whenever a caller that's not privileged to
allow QObject construction tries to do so."""
    def __str__(self):
        return "Caller is not allowed to call this function"

class QApplicationNotYetCreated(Exception):
    """This expection is raised whenever a function asks for permission to
create a QObject but the QApplication has not granted it yet."""
    def __str__(self):
        return "QApplication has not been created yet"

def allowQObjects():
    """Allows subsequent QObject creation. The constructor for the
QApplication-derived class must call this so that we know it's alright
to start creating other QtCore.QObjects."""
    
    # tries to check if caller is allowed to call this
    caller = inspect.currentframe().f_back
    d = caller.f_locals
    if (not d.has_key('self') or
        not isinstance(d['self'], QtCore.QCoreApplication)):
        raise DisallowedCaller
    global okToCreateQObjects
    okToCreateQObjects = True

def askForQObjectCreation():
    """This function simply throws an exception if it is not yet ok
to create QObjects."""
    global okToCreateQObjects
    if not okToCreateQObjects:
        raise QApplicationNotYetCreated()

global _appHolder

def createBogusQtApp():
    """createBogusQtApp creates a bogus Qt App so that we can use QObjects."""
    class BogusApplication(QtCore.QCoreApplication):
        def __init__(self):
            QtCore.QCoreApplication.__init__(self, ["bogus"])
            allowQObjects()
    global _appHolder
    _appHolder = BogusApplication()
    return _appHolder

def createBogusQtGuiApp(argv=["bogus"]):    
    """createBogusQtGuiApp is similar to createBogusQtApp but return a
    GUI application instead"""    
    class BogusApplication(QtGui.QApplication):
        def __init__(self):
            QtGui.QApplication.__init__(self, argv)
            allowQObjects()
    global _appHolder
    _appHolder = BogusApplication()
    return _appHolder

def destroyBogusQtApp():
    global _appHolder
    del _appHolder

def qt_version():
    return [int(i)
            for i in
            QtCore.qVersion().split('.')]

################################################################################

okToCreateQObjects = False

class SignalSet(object):
    
    """SignalSet stores a list of (object, signal, method) that can be
    all connected and disconnected simultaneously. This way, it's
    harder to forget to disconnect one of many signals. Also, if the
    SignalSet has already been plugged, it will signal an exception,
    to avoid multiple connections."""
    
    def __init__(self, owner, signalTripleList):
        self.owner = owner
        self.signalTripleList = signalTripleList
        self.plugged = False

    def plug(self):
        if self.plugged:
            raise Exception("SignalSet %s is already plugged" % self)
        for tupl in self.signalTripleList:
            self.owner.connect(*tupl)
        self.plugged = True

    def unplug(self):
        if not self.plugged:
            return
        for tupl in self.signalTripleList:
            self.owner.disconnect(*tupl)
        self.plugged = False

        
################################################################################

_oldConnect = QtCore.QObject.connect
_oldDisconnect = QtCore.QObject.disconnect

def _wrapConnect(callableObject):
    """Returns a wrapped call to the old version of QtCore.QObject.connect"""
    @staticmethod
    def call(*args):
        callableObject(*args)
        _oldConnect(*args)
    return call

def _wrapDisconnect(callableObject):
    """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""
    @staticmethod
    def call(*args):
        callableObject(*args)
        _oldDisconnect(*args)
    return call

def enableSignalDebugging(connectCall = None, disconnectCall = None):
    """Call this to enable Qt Signal debugging. This will trap all
    connect, and disconnect calls."""
    def printIt(msg):
        def call(*args):
            print msg, args
        return call
    QtCore.QObject.connect = _wrapConnect(connectCall or (lambda *args: None))
    QtCore.QObject.disconnect = _wrapDisconnect(disconnectCall or (lambda *args: None))
