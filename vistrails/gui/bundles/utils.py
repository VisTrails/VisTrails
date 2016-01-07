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

"""Utility functions for core.bundles"""
from __future__ import division

from vistrails.core import debug
import vistrails.core.system
import os
import platform
import sys

##############################################################################

def guess_graphical_sudo():
    """Tries to guess what to call to run a shell with elevated privileges.

    Returns: (sudo, escape)
    Where:
      sudo is the command to be used to gain root privileges, it 
           should contain %s where the actual command will be inserted
      escape is True if the rest of the line needs to be escaped
    """
    if sys.platform == 'win32':
        return '%s', False
    # sudo needs -E so that the Xauthority file is found and root can connect
    # to the user's X server
    if vistrails.core.system.executable_is_in_path('kdesudo'):
        return 'kdesudo %s', True
    elif vistrails.core.system.executable_is_in_path('kdesu'):
        return 'kdesu %s', False
    elif vistrails.core.system.executable_is_in_path('gksu'):
        return 'gksu %s', False
    elif (vistrails.core.system.executable_is_in_path('sudo') and
          vistrails.core.system.executable_is_in_path('zenity')):
        # This is a reasonably convoluted hack to only prompt for the password
        # if user has not recently entered it
        return ('((echo "" | sudo -v -S -p "") || '
                '(zenity --entry --title "sudo password prompt" --text '
                '"Please enter your password to give the system install '
                'authorization." --hide-text="" | sudo -v -S -p "")); '
                'sudo -E -S -p "" %s',
               False)
        # graphical sudo for osx
    elif vistrails.core.system.executable_is_in_path('osascript'):
        return "osascript -e " \
               "'do shell script %s with administrator privileges'", True
    else:
        debug.warning("Could not find a graphical sudo-like command.")

        if vistrails.core.system.executable_is_in_path('sudo'):
            debug.warning("Will use regular sudo")
            return "sudo -E %s", False
        else:
            debug.warning("Will use regular su")
            return "su --preserve-environment -c %s", True

##############################################################################

class System_guesser(object):

    def __init__(self):
        self._callable_dict = {}

    def add_test(self, test, system_name):
        if self._callable_dict.has_key(system_name):
            raise ValueError("test for '%s' already present." % system_name)
        if system_name == 'UNKNOWN':
            raise ValueError("Invalid system name")
        assert isinstance(system_name, str)
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
        tokens = open('/etc/SuSE-release').readline()[-1].split()
        return tokens[0] == 'SUSE'
    except (IOError, IndexError):
        return False
_system_guesser.add_test(_guess_suse, 'linux-suse')

def _guess_ubuntu():
    return platform.linux_distribution()[0]=='Ubuntu' or \
           platform.linux_distribution()[0]=='LinuxMint'
_system_guesser.add_test(_guess_ubuntu, 'linux-ubuntu')

def _guess_debian():
    return platform.linux_distribution()[0].lower() == 'debian'
_system_guesser.add_test(_guess_debian, 'linux-debian')

def _guess_fedora():
    return os.path.isfile('/etc/fedora-release')
_system_guesser.add_test(_guess_fedora, 'linux-fedora')

def _guess_windows():
    return vistrails.core.system.systemType == 'Windows'
_system_guesser.add_test(_guess_windows, 'windows')

##############################################################################

def guess_system():
    """guess_system will try to identify which system you're
    running. Result will be a string describing the system. This is
    more discriminating than Linux/OSX/Windows: We'll try to figure
    out whether you're running SuSE, Debian, Ubuntu, RedHat, fink,
    darwinports, etc.

    Currently, we only support SuSE, Debian, Ubuntu and
    Fedora. However, we only have actual bundle installing for Debian,
    Ubuntu and Fedora.

    """
    return _system_guesser.guess_system()
