###############################################################################
##
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

"""Utility functions for core.bundles"""

from core import debug
import core.system
import os
import platform

##############################################################################

def guess_graphical_sudo():
    """Tries to guess what to call to run a shell with elevated
privileges."""
    if core.system.executable_is_in_path('kdesu'):
        return 'kdesu -c'
    elif core.system.executable_is_in_path('gksu'):
        return 'gksu'
    elif (core.system.executable_is_in_path('sudo') and
          core.system.executable_is_in_path('zenity')):
        # This is a reasonably convoluted hack to only prompt for the password
        # if user has not recently entered it
        return ('((echo "" | sudo -v -S -p "") || ' +
                '(zenity --entry --title "sudo password prompt" --text "Please enter your password '
                'to give the system install authorization." --hide-text="" | sudo -v -S -p "")); sudo -S -p ""')
    else:
        debug.warning("Could not find a graphical su-like command.")
        debug.warning("Will use regular su")
        return 'su -c'

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
#    return os.path.isfile('/etc/apt/apt.conf.d/01ubuntu')
     return platform.linux_distribution()[0]=='Ubuntu'
_system_guesser.add_test(_guess_ubuntu, 'linux-ubuntu')

def _guess_fedora():
    return os.path.isfile('/etc/fedora-release')
_system_guesser.add_test(_guess_fedora, 'linux-fedora')

##############################################################################

def guess_system():
    """guess_system will try to identify which system you're running. Result
will be a string describing the system. This is more discriminating than
Linux/OSX/Windows: We'll try to figure out whether you're running SuSE, Debian,
Ubuntu, RedHat, fink, darwinports, etc.

Currently, we only support SuSE, Ubuntu and Fedora. However, we only have
actual bundle installing for Ubuntu and Fedora."""
    return _system_guesser.guess_system()
