from core.common import unimplemented, VistrailsInternalError
import os
import os.path
import sys
import platform

systemType = platform.system()

if systemType in ['Windows', 'Microsoft']:
    from core.system.windows import *
elif systemType in ['Linux']:
    from core.system.linux import *
elif systemType in ['Darwin']:
    from core.system.osx import *
else:
    print "Critical error"
    print "VisTrails could not detect your operating system."
    sys.exit(1)

__rootDir = os.getcwd() + os.path.normcase('/')
__dataDir = __rootDir + 'data/'
def setVistrailsDataDirectory(d):
    global __dataDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __dataDir = d + '/'

def setVistrailsDirectory(d):
    global __rootDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __rootDir = d + '/'

def visTrailsRootDirectory():
    return __rootDir

def vistrailsDirectory():
    return visTrailsRootDirectory() + 'test_files'

def packagesDirectory():
    return visTrailsRootDirectory() + 'packages'

def blankVistrailFile():
    unimplemented()

def resourceDirectory():
    unimplemented()

def defaultOptionsFile():
    return homeDirectory() + "/.vistrailsrc"

def defaultDotVistrails():
    return homeDirectory() + "/.vistrails"

def pythonVersion():
   """pythonVersion() -> (major, minor, micro, release, serial)
Returns python version info."""
   return sys.version_info

def vistrailsVersion():
   """vistrailsVersion() -> string - Returns the current VisTrails version."""
   # 0.1 was the Vis2005 version
   # 0.2 will be the SIGMOD demo version
   return '0.3'

def aboutString():
   """aboutString() -> string - Returns the about string for VisTrails."""
   return """VisTrails -- version %s
Copyright 2005--2006, University of Utah.
Contact us at vistrails@sci.utah.edu

VisTrails is developed at the SCI Institute and the School of
Computing at the University of Utah.  THERE IS NO WARRANTY FOR THE
PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM AS IS WITHOUT WARRANTY OF ANY KIND, EITHER
EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE
PROGRAM IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME
THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION. IN NO EVENT
UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL ANY
COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR
DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL
DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM
(INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED
INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF
THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER
OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.""" % vistrailsVersion()
