###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

"""Module with utilities to try and install a bundle if possible."""
from vistrails.core import get_vistrails_application
from vistrails.core import debug
from vistrails.core.system import get_executable_path, vistrails_root_directory
from vistrails.gui.bundles.utils import guess_system, guess_graphical_sudo
import vistrails.gui.bundles.installbundle # this is on purpose
import os


##############################################################################

def has_qt():
    try:
        import PyQt4.QtGui
        # Must import this on Ubuntu linux, because PyQt4 doesn't come with
        # PyQt4.QtOpenGL by default
        import PyQt4.QtOpenGL
        return True
    except ImportError:
        return False


def hide_splash_if_necessary():
    qt = has_qt()
    # HACK, otherwise splashscreen stays in front of windows
    if qt:
        try:
            get_vistrails_application().splashScreen.hide()
        except:
            pass


def run_install_command_as_root(graphical, cmd, args):
    if type(args) == str:
        cmd += ' ' + args
    elif type(args) == list:
        for package in args:
            if type(package) != str:
                raise TypeError("Expected string or list of strings")
            cmd += ' ' + package
    else:
        raise TypeError("Expected string or list of strings")

    if graphical:
        sucmd, escape = guess_graphical_sudo()
    else:
        debug.warning("VisTrails wants to install package(s) %r" %
                      args)
        if get_executable_path('sudo'):
            sucmd, escape = "sudo", False
        else:
            sucmd, escape = "su -c", True

    if escape:
        sucmd = '%s "%s"' % (sucmd, cmd.replace('\\', '\\\\').replace('"', '\\"'))
    else:
        sucmd = '%s %s' % (sucmd, cmd)

    print "about to run: %s" % sucmd
    result = os.system(sucmd)

    return result == 0 # 0 indicates success


def linux_debian_install(package_name):
    qt = has_qt()
    try:
        import apt
        import apt_pkg
    except ImportError:
        qt = False
    hide_splash_if_necessary()

    if qt:
        cmd = vistrails_root_directory()
        cmd += '/gui/bundles/linux_debian_install.py'
    else:
        cmd = '%s install -y' % ('aptitude' if get_executable_path('aptitude') else 'apt-get')

    return run_install_command_as_root(qt, cmd, package_name)

linux_ubuntu_install = linux_debian_install


def linux_fedora_install(package_name):
    qt = has_qt()
    hide_splash_if_necessary()

    if qt:
        cmd = vistrails_root_directory()
        cmd += '/gui/bundles/linux_fedora_install.py'
    else:
        cmd = 'yum -y install'

    return run_install_command_as_root(qt, cmd, package_name)


def show_question(which_files):
    qt = has_qt()
    if qt:
        import vistrails.gui.utils
        if type(which_files) == str:
            which_files = [which_files]
        v = vistrails.gui.utils.show_question("Required packages missing",
                                    "One or more required packages are missing: " +
                                    " ".join(which_files) +
                                    ". VisTrails can " +
                                    "automaticallly install them. " +
                                    "If you click OK, VisTrails will need "+
                                    "administrator privileges, and you " +
                                    "might be asked for the administrator password.",
                                    buttons=[vistrails.gui.utils.OK_BUTTON,
                                             vistrails.gui.utils.CANCEL_BUTTON],
                                    default=vistrails.gui.utils.OK_BUTTON)
        return v == vistrails.gui.utils.OK_BUTTON
    else:
        print "Required package missing"
        print ("A required package is missing, but VisTrails can " +
               "automatically install it. " +
               "If you say Yes, VisTrails will need "+
               "administrator privileges, and you" +
               "might be asked for the administrator password.")
        print "Give VisTrails permission to try to install package? (y/N)"
        v = raw_input().upper()
        return v == 'Y' or v == 'YES'


def install(dependency_dictionary):
    """Tries to install a bundle after a py_import() failed.."""

    distro = guess_system()
    if distro not in dependency_dictionary:
        return False
    else:
        files = dependency_dictionary[distro]
        if show_question(files):
            callable_ = getattr(vistrails.gui.bundles.installbundle,
                                distro.replace('-', '_') + '_install')
            return callable_(files)
        else:
            return False
