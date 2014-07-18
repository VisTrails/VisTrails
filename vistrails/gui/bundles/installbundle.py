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

"""Module with utilities to try and install a bundle if possible."""
from vistrails.core import get_vistrails_application
from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core import debug
from vistrails.core.system import executable_is_in_path, get_executable_path
from vistrails.core.system import vistrails_root_directory, systemType
from vistrails.gui.bundles.utils import guess_system, guess_graphical_sudo
import vistrails.gui.bundles.installbundle # this is on purpose
from vistrails.gui.requirements import qt_available
import imp
import os
import subprocess
import sys

##############################################################################

pip_installed = True
try:
    imp.find_module('pip')
    # Here we do not actually import pip, to avoid pip issue #1314
    # https://github.com/pypa/pip/issues/1314
except ImportError:
    pip_installed = False

def hide_splash_if_necessary():
    """Disables the splashscreen, otherwise it sits in front of windows.
    """
    app = get_vistrails_application()
    if hasattr(app, 'splashScreen') and app.splashScreen:
        app.splashScreen.hide()


def shell_escape(arg):
    return '"%s"' % arg.replace('\\', '\\\\').replace('"', '\\"')


def run_install_command(graphical, cmd, args, as_root=True):
    if isinstance(args, str):
        cmd += ' %s' % shell_escape(args)
    elif isinstance(args, list):
        for package in args:
            if not isinstance(package, str):
                raise TypeError("Expected string or list of strings")
            cmd += ' %s' % shell_escape(package)
    else:
        raise TypeError("Expected string or list of strings")

    debug.warning("VisTrails wants to install package(s) %r" %
                  args)

    if as_root and systemType != 'Windows':
        if graphical:
            sucmd, escape = guess_graphical_sudo()
        else:
            if get_executable_path('sudo'):
                sucmd, escape = "sudo %s", False
            elif systemType != 'Darwin':
                sucmd, escape = "su -c %s", True
            else:
                sucmd, escape = '%s', False

        if escape:
            cmd = sucmd % shell_escape(cmd)
        else:
            cmd = sucmd % cmd

    print "about to run: %s" % cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True)
    lines = []
    try:
        for line in iter(p.stdout.readline, ''):
            print line,
            lines.append(line)
    except IOError, e:
        print "Ignoring IOError:", str(e)
    result = p.wait()

    if result != 0:
        debug.critical("Error running: %s" % cmd, ''.join(lines))

    return result == 0 # 0 indicates success


def linux_debian_install(package_name):
    qt = qt_available()
    try:
        import apt
        import apt_pkg
    except ImportError:
        qt = False
    hide_splash_if_necessary()

    if qt:
        cmd = shell_escape(vistrails_root_directory() +
                           '/gui/bundles/linux_debian_install.py')
    else:
        cmd = '%s install -y' % ('aptitude'
                                 if executable_is_in_path('aptitude')
                                 else 'apt-get')

    return run_install_command(qt, cmd, package_name)

linux_ubuntu_install = linux_debian_install


def linux_fedora_install(package_name):
    qt = qt_available()
    hide_splash_if_necessary()

    if qt:
        cmd = shell_escape(vistrails_root_directory() +
                           '/gui/bundles/linux_fedora_install.py')
    else:
        cmd = 'yum -y install'

    return run_install_command(qt, cmd, package_name)


def pip_install(package_name):
    hide_splash_if_necessary()

    if executable_is_in_path('pip'):
        cmd = '%s install' % shell_escape(get_executable_path('pip'))
    else:
        cmd = shell_escape(sys.executable) + ' -m pip install'

    if systemType != 'Windows':
        use_root = True
        try:
            from distutils.sysconfig import get_python_lib
            f = get_python_lib()
        except Exception:
            f = sys.executable
        use_root = os.stat(f).st_uid == 0
    else:
        use_root = False

    return run_install_command(qt_available(), cmd, package_name, use_root)

def show_question(which_files, has_distro_pkg, has_pip):
    if isinstance(which_files, str):
        which_files = [which_files]
    if qt_available():
        from PyQt4 import QtCore, QtGui
        dialog = QtGui.QDialog()
        dialog.setWindowTitle("Required packages missing")
        layout = QtGui.QVBoxLayout()

        label = QtGui.QLabel(
                "One or more required packages are missing: %s. VisTrails can "
                "automatically install them. If you click OK, VisTrails will "
                "need administrator privileges, and you might be asked for "
                "the administrator password." % (" ".join(which_files)))
        label.setWordWrap(True)
        layout.addWidget(label)

        if pip_installed and has_pip:
            use_pip = QtGui.QCheckBox("Use pip")
            use_pip.setChecked(
                not has_distro_pkg or (
                    has_pip and
                    getattr(get_vistrails_configuration(),
                            'installBundlesWithPip')))
            use_pip.setEnabled(has_distro_pkg and has_pip)
            layout.addWidget(use_pip)

            remember_align = QtGui.QHBoxLayout()
            remember_align.addSpacing(20)
            remember_pip = QtGui.QCheckBox("Remember my choice")
            remember_pip.setChecked(False)
            remember_pip.setEnabled(use_pip.isEnabled())
            remember_align.addWidget(remember_pip)
            layout.addLayout(remember_align)
        elif has_pip:
            label = QtGui.QLabel("pip package is available but pip is not installed")
            layout.addWidget(label)
        buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        QtCore.QObject.connect(buttons, QtCore.SIGNAL('accepted()'),
                               dialog, QtCore.SLOT('accept()'))
        QtCore.QObject.connect(buttons, QtCore.SIGNAL('rejected()'),
                               dialog, QtCore.SLOT('reject()'))
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        hide_splash_if_necessary()
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return False
        else:
            if pip_installed and has_pip:
                if remember_pip.isChecked():
                    setattr(get_vistrails_persistent_configuration(),
                            'installBundlesWithPip',
                            use_pip.isChecked())

                if use_pip.isChecked():
                    return 'pip'
            return 'distro'
    else:
        print "\nRequired package(s) missing: %s" % (" ".join(which_files))
        print ("A required package is missing, but VisTrails can "
               "automatically install it. "
               "If you say Yes, VisTrails will need "
               "administrator privileges, and you "
               "might be asked for the administrator password.")
        if has_distro_pkg:
            print "(VisTrails will use your distribution's package manager)"
        else:
            print "(VisTrails will use the 'pip' installer)"
        print "Give VisTrails permission to try to install package? (y/N)"
        v = raw_input().upper()
        if v == 'Y' or v == 'YES':
            if has_distro_pkg:
                return 'distro'
            else:
                return 'pip'


def install(dependency_dictionary):
    """Tries to install a bundle after a py_import() failed.."""

    distro = guess_system()
    files = (dependency_dictionary.get(distro) or
             dependency_dictionary.get('pip'))
    if not files:
        return None
    can_install = (('pip' in dependency_dictionary and pip_installed) or
                   distro in dependency_dictionary)
    if can_install:
        action = show_question(
                files,
                distro in dependency_dictionary,
                'pip' in dependency_dictionary)
        if action == 'distro':
            callable_ = getattr(vistrails.gui.bundles.installbundle,
                                distro.replace('-', '_') + '_install')
            return callable_(files)
        elif action == 'pip':
            if not pip_installed:
                debug.warning("Attempted to use pip, but it is not installed.")
                return False
            return pip_install(dependency_dictionary.get('pip'))
        else:
            return False
