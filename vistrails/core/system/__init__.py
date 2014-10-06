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
from __future__ import with_statement

import datetime
import functools
import getpass
import locale
import os
import platform
import socket
import subprocess
import sys
import time
import urllib2

from vistrails.core import debug
from vistrails.core.utils import unimplemented, VistrailsInternalError, Chdir


###############################################################################

from common import *

def with_c_locale(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        previous_locale = locale.setlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, 'C')
        try:
            return func(*args, **kwargs)
        finally:
            locale.setlocale(locale.LC_TIME, previous_locale)
    return newfunc

@with_c_locale
def strptime(*args, **kwargs):
    """Version of datetime.strptime that always uses the C locale.

    This is because date strings are used internally in the database, and
    should not be localized.
    """
    return datetime.datetime.strptime(*args, **kwargs)

@with_c_locale
def time_strptime(*args, **kwargs):
    """Version of time.strptime that always uses the C locale.

    This is because date strings are used internally in the database, and
    should not be localized.
    """
    return time.strptime(*args, **kwargs)

@with_c_locale
def strftime(dt, *args, **kwargs):
    """Version of datetime.strftime that always uses the C locale.

    This is because date strings are used internally in the database, and
    should not be localized.
    """
    if hasattr(dt, 'strftime'):
        return dt.strftime(*args, **kwargs)
    else:
        return time.strftime(dt, *args, **kwargs)

##############################################################################

systemType = platform.system()

if systemType in ['Windows', 'Microsoft']:
    from vistrails.core.system.windows import *

elif systemType in ['Linux']:
    from vistrails.core.system.linux import *

elif systemType in ['Darwin']:
    from vistrails.core.system.osx import *
else:
    debug.critical("VisTrails could not detect your operating system.")
    sys.exit(1)

###############################################################################

# Makes sure root directory is sensible.
if __name__ == '__main__':
    _thisDir = sys.argv[0]
else:
    _thisDir = sys.modules[__name__].__file__
_thisDir = os.path.split(_thisDir)[0]
__rootDir = os.path.realpath(os.path.join(_thisDir,
                                          '..',
                                          '..'))

__dataDir = os.path.realpath(os.path.join(__rootDir,
                                          'data'))
__fileDir = os.path.realpath(os.path.join(__rootDir,
                                          '..','examples'))

if systemType in ['Darwin'] and not os.path.exists(__fileDir):
    # Assume we are running from py2app
    __fileDir = os.path.realpath(os.path.join(__rootDir,
                                              '/'.join(['..']*6),'examples'))

__examplesDir = __fileDir

__defaultFileType = '.vt'

__defaultPkgPrefix = 'org.vistrails.vistrails'

def get_vistrails_default_pkg_prefix():
    return __defaultPkgPrefix

def get_vistrails_basic_pkg_id():
    return "%s.basic" % get_vistrails_default_pkg_prefix()

def get_vistrails_directory(config_key, conf=None):
    if conf is None:
        from vistrails.core.configuration import get_vistrails_configuration
        conf = get_vistrails_configuration()
    if conf.has_deep_value(config_key):
        d = conf.get_deep_value(config_key)
        if os.path.isabs(d):
            return d
        else:
            return os.path.join(current_dot_vistrails(conf), d)
    return None

def set_vistrails_data_directory(d):
    """ set_vistrails_data_directory(d:str) -> None
    Sets vistrails data directory taking into account environment variables

    """
    global __dataDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __dataDir = os.path.realpath(d)

def set_vistrails_file_directory(d):
    """ set_vistrails_file_directory(d: str) -> None
    Sets vistrails file directory taking into accoun environment variables

    """
    global __fileDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __fileDir = os.path.realpath(d)

def set_vistrails_root_directory(d):
    """ set_vistrails_root_directory(d:str) -> None
    Sets vistrails root directory taking into account environment variables

    """

    global __rootDir
    new_d = os.path.expanduser(d)
    new_d = os.path.expandvars(new_d)
    while new_d != d:
        d = new_d
        new_d = os.path.expandvars(d)
    __rootDir = os.path.realpath(d)

def set_vistrails_default_file_type(t):
    """ set_vistrails_default_file_type(t:str) -> None
    Which file type to use when the user doesn't provide a file extension

    """
    global __defaultFileType
    if t in ['.vt', '.xml']:
        __defaultFileType = t
    else:
        __defaultFileType = '.vt'

def vistrails_root_directory():
    """ vistrails_root_directory() -> str
    Returns vistrails root directory

    """
    return __rootDir

def vistrails_file_directory():
    """ vistrails_file_directory() -> str 
    Returns current vistrails file directory

    """
    return __fileDir

def vistrails_examples_directory():
    """ vistrails_file_directory() -> str 
    Returns vistrails examples directory

    """
    return __examplesDir

def vistrails_data_directory():
    """ vistrails_data_directory() -> str
    Returns vistrails data directory

    """
    return __dataDir

def vistrails_default_file_type():
    """ vistrails_default_file_type() -> str
    Returns vistrails file type

    """
    return __defaultFileType

def packages_directory():
    """ packages_directory() -> str
    Returns vistrails packages directory

    """
    return os.path.join(vistrails_root_directory(),'packages')

def blank_vistrail_file():
    unimplemented()

def resource_directory():
    """ resource_directory() -> str
    Returns vistrails gui resource directory

    """
    return os.path.join(vistrails_root_directory(),
                        'gui', 'resources')

def default_options_file():
    """ default_options_file() -> str
    Returns vistrails default options file

    """
    return os.path.join(home_directory(), ".vistrailsrc")

def default_dot_vistrails():
    """ default_dot_vistrails() -> str
    Returns the default VisTrails per-user directory.

    """
    return os.path.join(home_directory(), '.vistrails')

def current_dot_vistrails(conf=None):
    """ current_dot_vistrails() -> str
    Returns the VisTrails per-user directory.

    """
    if conf is None:
        from vistrails.core.configuration import get_vistrails_configuration
        conf = get_vistrails_configuration()
    return conf.dotVistrails

def default_connections_file():
    """ default_connections_file() -> str
    Returns default Vistrails per-user connections file

    """
    return os.path.join(current_dot_vistrails(), 'connections.xml')

def vistrails_version():
    """vistrails_version() -> string - Returns the current VisTrails version."""
    # 0.1 was the Vis2005 version
    # 0.2 was the SIGMOD demo version
    # 0.3 was the plugin/vtk version
    # 0.4 is cleaned up version with new GUI
    # 1.0 is version with new schema
    return '2.1.4'

def get_latest_vistrails_version():
    """get_latest_vistrails_version() -> string - Returns latest vistrails
    release version as queried from vistrails.org"""

    version = ''
    version_url = \
            "http://www.vistrails.org/download/download.php?id=release_version.txt"
    try:
        request = urllib2.Request(version_url)
        get_latest_version = urllib2.urlopen(request)
        version = get_latest_version.read().strip()
    except urllib2.HTTPError, err:
        debug.warning("Unable to check for updates: %s" % str(err))
        return version

    return version

def new_vistrails_release_exists():
    """ new_vistrail_release_exists() -> (bool, str)
    Returns (True, new_version_str) if newer version exists

    """

    local_version = [int(x) for x in vistrails_version().split('.')]

    remote_str = get_latest_vistrails_version()
    if remote_str:
        remote_version = [int(x) for x in remote_str.split('.')]
    else:
        remote_version = [0]

    if cmp(local_version, remote_version) is -1:
        return (True, remote_str)

    return (False, None)

def vistrails_revision():
    """vistrails_revision() -> str
    When run on a working copy, shows the current svn revision else
    shows the latest release revision

    """
    git_dir = os.path.join(vistrails_root_directory(), '..')
    with Chdir(git_dir):
        release = "269e4808eca3"
        import vistrails.core.requirements
        if vistrails.core.requirements.executable_file_exists('git'):
            lines = []
            result = execute_cmdline(
                ['git', 'describe', '--always', '--abbrev=12'],
                lines)
            if len(lines) == 1:
                if result == 0:
                    release = lines[0].strip(" \n")
    return release


_registry = None
def get_module_registry():
    global _registry
    if _registry is None:
        from vistrails.core.modules.module_registry import get_module_registry
        _registry = get_module_registry()
    return _registry

def short_about_string():
    return """VisTrails version %s.%s -- contact@vistrails.org""" % \
            (vistrails_version(), vistrails_revision())

def about_string():
    """about_string() -> string - Returns the about string for VisTrails."""
    return """VisTrails version %s.%s -- contact@vistrails.org

Copyright (C) 2011-2014 NYU-Poly. Copyright (C) 2006-2011 University of Utah. 
All rights reserved.
http://www.vistrails.org

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of Utah nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" \
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE \
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE \
ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT, \
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, \
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, \
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY \
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING \
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, \
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.""" % (vistrails_version(),
                                                         vistrails_revision())

###############################################################################

import unittest

if __name__ == '__main__':
    unittest.main()

class TestSystem(unittest.TestCase):

    def test_vistrails_revision(self):
        r = vistrails_root_directory()
        with Chdir(r):
            v1 = vistrails_revision()
            try:
                with Chdir(os.path.join(r, '..')):
                    self.assertEquals(v1, vistrails_revision())
            except AssertionError:
                raise
            except Exception:
                pass
            try:
                with Chdir(os.path.join(r, '..', '..')):
                    self.assertEquals(v1, vistrails_revision())
            except AssertionError:
                raise
            except Exception:
                pass
