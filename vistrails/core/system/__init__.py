import os
import os.path
import sys
import platform
from core.utils import unimplemented, VistrailsInternalError

################################################################################

systemType = platform.system()

if systemType in ['Windows', 'Microsoft']:
    from core.system.windows import guessTotalMemory, temporaryDirectory, \
        homeDirectory, remoteCopyProgram, remoteShellProgram, \
        graphVizDotCommandLine, removeGraphvizTemporaries, link_or_copy, \
        getClipboard, TestWindows

elif systemType in ['Linux']:
    from core.system.linux import guessTotalMemory, temporaryDirectory, \
        homeDirectory, remoteCopyProgram, remoteShellProgram, \
        graphVizDotCommandLine, removeGraphvizTemporaries, link_or_copy, \
        getClipboard, TestLinux

elif systemType in ['Darwin']:
    from core.system.osx import guessTotalMemory, temporaryDirectory, \
        homeDirectory, remoteCopyProgram, remoteShellProgram, \
        graphVizDotCommandLine, removeGraphvizTemporaries, link_or_copy, \
        getClipboard, TestMacOSX 
else:
    print "Critical error"
    print "VisTrails could not detect your operating system."
    sys.exit(1)

# Makes sure root directory is sensible.
if __name__ == '__main__':
    _thisDir = sys.argv[0]
else:
    _thisDir = sys.modules[__name__].__file__
_thisDir = os.path.split(_thisDir)[0]
__rootDir = _thisDir + '/../../'

__dataDir = __rootDir + 'data/'

def setVistrailsDataDirectory(d):
    """ setVistrailsDataDirectory(d:str) -> None 
    Sets vistrails data directory taking into account environment variables

    """
    global __dataDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __dataDir = d + '/'

def setVistrailsDirectory(d):
    """ setVistrailsDirectory(d:str) -> None 
    Sets vistrails root directory taking into account environment variables

    """

    global __rootDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __rootDir = d + '/'

def visTrailsRootDirectory():
    """ visTrailsRootDirectory() -> str
    Returns vistrails root directory

    """
    return __rootDir

def vistrailsDirectory():
    """ vistrailsDirectory() -> str 
    Returns vistrails examples directory

    """
    return visTrailsRootDirectory() + '../examples/'

def packagesDirectory():
    """ packagesDirectory() -> str 
    Returns vistrails packages directory

    """
    return visTrailsRootDirectory() + 'packages/'

def blankVistrailFile():
    unimplemented()

def resourceDirectory():
    """ resourceDirectory() -> str 
    Returns vistrails gui resource directory

    """
    return visTrailsRootDirectory() + 'gui/resources/'

def defaultOptionsFile():
    """ defaultOptionsFile() -> str 
    Returns vistrails default options file

    """
    return homeDirectory() + "/.vistrailsrc"

def defaultDotVistrails():
    """ defaultDotVistrails() -> str 
    Returns VisTrails per-user directory.

    """
    return homeDirectory() + "/.vistrails"

def pythonVersion():
   """pythonVersion() -> (major, minor, micro, release, serial)
Returns python version info."""
   return sys.version_info

def vistrailsVersion():
   """vistrailsVersion() -> string - Returns the current VisTrails version."""
   # 0.1 was the Vis2005 version
   # 0.2 was the SIGMOD demo version
   # 0.3 is the plugin/vtk version
   # 0.4 is cleaned up version with new GUI
   return '0.4'

def aboutString():
   """aboutString() -> string - Returns the about string for VisTrails."""
   return """VisTrails version %s -- vistrails@sci.utah.edu

Copyright (c) 2006 University of Utah
All rights reserved.

This is PROPRIETARY software. If you or your organization has not
received this software directly by authorized personnel from the
University of Utah, you should delete it immediately.

This software is being provided solely for EVALUATION purposes. You
can use it for 30 days from the moment you get it from the University
of Utah personnel. Continued use requires renewal of the evaluation
period.

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM AS IS WITHOUT
WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE PROGRAM PROVE
DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
CORRECTION. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO
IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY
MODIFY AND/OR REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE
TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE
PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING
RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A
FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF
SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGES.""" % vistrailsVersion()

################################################################################

import unittest

if __name__ == '__main__':
    unittest.main()
