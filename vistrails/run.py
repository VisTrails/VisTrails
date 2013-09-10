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
"""Main file for the VisTrails distribution."""

import os
import sys

# Allows the userpackages directory to be overridden through an environment
# variable
# As this variable is set by the package manager, this also allows
# multiprocessing to work correctly on Windows, where fork is not used and thus
# 'userpackages' needs to be available in processes spawned from a
# userpackage's code
try:
    userpackages_dir = os.environ['VISTRAILS_USERPACKAGES_DIR']
except KeyError:
    pass
else:
    old_sys_path = list(sys.path)
    sys.path.insert(0, os.path.join(userpackages_dir, os.path.pardir))
    try:
        import userpackages
    except ImportError:
        sys.stderr.write("Couldn't import VISTRAILS_USERPACKAGES_DIR (%s), "
                         "continuing\n" % userpackages_dir)

def disable_lion_restore():
    """ Prevent Mac OS 10.7 to restore windows state since it would
    make Qt 4.7.3 unstable due to its lack of handling Cocoa's Main
    Window. """
    import platform
    if platform.system()!='Darwin': return
    release = platform.mac_ver()[0].split('.')
    if len(release)<2: return
    major = int(release[0])
    minor = int(release[1])
    if major*100+minor<107: return
    ssPath = os.path.expanduser('~/Library/Saved Application State/org.vistrails.savedState')
    if os.path.exists(ssPath):
        os.system('rm -rf "%s"' % ssPath)
    os.system('defaults write org.vistrails NSQuitAlwaysKeepsWindows -bool false')

def setNewPyQtAPI():
    try:
        import sip
        # We now use the new PyQt API - IPython needs it
        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
    except:
        print "Could not set PyQt API, is PyQt4 installed?"


def enable_user_base():
    # USER_BASE and USER_SITE in site.py is not set when running from py2app,
    # this is neded by at least scipy.weave
    import platform
    if platform.system()!='Darwin': return
    import site
    if hasattr(site, "USER_BASE"): return
    from vistrails.core.system import mac_site
    site.USER_BASE = mac_site.getuserbase()
    site.USER_SITE = mac_site.getusersitepackages()


def fix_paths():
    import site
    if not hasattr(site, "USER_BASE"): return # We are running py2app

    # Fix import path: add parent directory(so that we can
    # import vistrails.[gui|...] and remove other paths below it (we might have
    # been started from a subdir)
    # A better solution is probably to move run.py up a
    # directory in the repo
    old_dir = os.path.realpath(os.path.dirname(__file__))
    vistrails_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    i = 0
    while i < len(sys.path):
        rpath = os.path.realpath(sys.path[i])
        if rpath.startswith(old_dir):
            del sys.path[i]
        else:
            i += 1
    if vistrails_dir not in sys.path:
        sys.path.insert(0, vistrails_dir)

if __name__ == '__main__':
    fix_paths()
    disable_lion_restore()
    enable_user_base()

    import vistrails.core.requirements
    import vistrails.gui.bundles.installbundle

    setNewPyQtAPI()
    try:
        vistrails.core.requirements.require_python_module('PyQt4.QtGui')
        vistrails.core.requirements.require_python_module('PyQt4.QtOpenGL')
    except vistrails.core.requirements.MissingRequirement, req:
        r = vistrails.gui.bundles.installbundle.install({
            'linux-debian': ['python-qt4', 'python-qt4-gl', 'python-qt4-sql'],
            'linux-ubuntu': ['python-qt4', 'python-qt4-gl', 'python-qt4-sql'],
            'linux-fedora': ['PyQt4'],
            'pip': ['PyQt<5.0']})
        if not r:
            raise req
        setNewPyQtAPI()

    from PyQt4 import QtGui
    import vistrails.gui.application
    from vistrails.core.application import APP_SUCCESS, APP_FAIL, APP_DONE
    try:
        v = vistrails.gui.application.start_application()
        if v != APP_SUCCESS:
            app = vistrails.gui.application.get_vistrails_application()
            if app:
                app.finishSession()
            sys.exit(APP_SUCCESS if v == APP_DONE else APP_FAIL)
        app = vistrails.gui.application.get_vistrails_application()()
    except SystemExit, e:
        app = vistrails.gui.application.get_vistrails_application()
        if app:
            app.finishSession()
        sys.exit(e)
    except Exception, e:
        app = vistrails.gui.application.get_vistrails_application()
        if app:
            app.finishSession()
        print "Uncaught exception on initialization: %s" % e
        import traceback
        traceback.print_exc()
        sys.exit(255)
    if (app.temp_configuration.interactiveMode and
        not app.temp_configuration.check('spreadsheetDumpCells')): 
        v = app.exec_()
        
    vistrails.gui.application.stop_application()
    sys.exit(v)
