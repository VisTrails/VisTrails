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

"""Package for bundle management. "Bundle" refers to system-level
packages managed by specialized systems such as RedHat's RPM, Debian
and Ubuntu's APT, OSX's fink, etc."""

import core.requirements
import core.system
import os.path

import core.bundles # This is on purpose

##############################################################################

class System_guesser(object):

    def __init__(self):
        self._callable_dict = {}

    def add_test(self, test, system_name):
        if self._callable_dict.has_key(system_name):
            raise Exception("test for '%s' already present." % system_name)
        if system_name == 'UNKNOWN':
            raise Exception("Invalid system name")
        assert type(system_name) == str
        self._callable_dict[system_name] = test

    def guess_system(self):
        for (name, callable_) in self._callable_dict.iteritems():
            if callable_():
                return name
        else:
            return 'UNKNOWN'

_system_guesser = System_guesser()

##############################################################################
# System tests

def _guess_suse():
    try:
        tokens = file('/etc/SuSE-release').readline()[-1].split()
        return tokens[0] == 'SUSE'
    except:
        return False
_system_guesser.add_test(_guess_suse, 'linux-suse')

def _guess_ubuntu():
    return os.path.isfile('/etc/apt/apt.conf.d/01ubuntu')
_system_guesser.add_test(_guess_ubuntu, 'linux-ubuntu')

##############################################################################

def guess_system():
    """guess_system will try to identify which system you're running. Result
will be a string describing the system. This is more discriminating than
Linux/OSX/Windows: We'll try to figure out whether you're running SuSE, Debian,
Ubuntu, RedHat, fink, darwinports, etc.

Currently, we only support SuSE and Ubuntu"""
    return _system_guesser.guess_system()


##############################################################################

def _vanilla_import(module_name):
    return __import__(module_name, globals(), locals(), [])

def _guess_graphical_sudo():
    """Tries to guess what to call to run a shell with elevated
privileges."""
    if core.system.executable_is_in_path('kdesu'):
        return 'kdesu -c'
    elif core.system.executable_is_in_path('gksu'):
        return 'gksu'
    else:
        print "Could not find a graphical su-like command."
        print "Will use regular su"
        return 'su -c'

def unknown_py_import(module_name, package_name):
    return _vanilla_import(module_name)

def linux_ubuntu_py_import(module_name, package_name):
    try:
        result = _vanilla_import(module_name)
        return result
    except ImportError, e:
        pass
    print "Import failed. Will try to install package"

    cmd = core.system.visTrailsRootDirectory()
    cmd += '/core/bundles/linux_ubuntu_install.py '
    cmd += package_name

    sucmd = _guess_graphical_sudo() + " '" + cmd + "'"

    # HACK
    import PyQt4.QtCore
    PyQt4.QtCore.QCoreApplication.instance().splashScreen.hide()
    result = os.system(sucmd)
    
    if result == 0:
        print "Install succeeded."
    else:
        print "Package installation failed."
        print "Package might not be available in the provided repositories."
        raise e
    try:
        result = _vanilla_import(module_name)
        return result
    except ImportError, e:
        print "Package installation successful, but import still failed."
        print "This means py_import was called with bad arguments."
        print "Please report this bug to the package developer."
        raise e
    
def py_import(module_name, dependency_dictionary):
    """Tries to import a python module. If unsuccessful, tries to install
the appropriate bundle and then reimport. py_import tries to be smart
about which system it runs on."""
    distro = guess_system()
    if not dependency_dictionary.has_key(distro):
        return _vanilla_import(module_name)
    else:
        callable_ = getattr(core.bundles,
                            distro.replace('-', '_') + '_py_import')
        return callable_(module_name, dependency_dictionary[distro])

##############################################################################
