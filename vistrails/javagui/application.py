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

""" This is the main application of the Java version of VisTrail.

It will call initialize everything, check requirements and create the builder
frame.
"""

import sys
from core.application import VistrailsApplicationInterface, \
    get_vistrails_application, set_vistrails_application
from core import debug
import core.requirements
from core import system
from javagui.java_requirements import check_java_requirement
from javagui.utils import run_on_edt
from javagui.splashscreen import JSplashScreen

################################################################################

class VistrailsJavaApplicationSingleton(VistrailsApplicationInterface):
    """
    VistrailsJavaApplicationSingleton is the singleton of the application,
    there will be only one instance of the application during VisTrails

    """

    def __call__(self):
        """ __call__() -> VistrailsJavaApplicationSingleton
        Return self for calling method

        """
        if not self._initialized and not self._is_running:
            self.init()
        return self

    def __init__(self):
        super(VistrailsJavaApplicationSingleton, self).__init__()

        self.builderWindow = None
        self._splash_screen = None

        # Check for non-python requirements, locate additional JARs if needed

        # VLDocking
        check_java_requirement(
                ('com.vlsolutions.swing.docking',
                 ['DockKey', 'Dockable']))

        # Piccolo-core
        check_java_requirement(
                ('edu.umd.cs.piccolo',
                 ['PCanvas', 'PNode']))

        # Piccolo-extras
        # Not necessary as of now
        #check_java_requirement(
        #        ['piccolo', 'piccolox'],
        #        'piccolo2d-extras-{version}.jar', {'version': '1.3.1'},
        #        ('edu.umd.cs.piccolox',
        #         ['PApplet', 'PFrame']))

    def init(self, optionsDict=None):
        """ VistrailsJavaApplicationSingleton(optionDict: dict)
                                          -> VistrailsJavaApplicationSingleton
        Create the application with a dict of settings

        """
        VistrailsApplicationInterface.init(self,optionsDict)
        
        interactive = self.temp_configuration.check('interactiveMode')

        if not interactive:
            self.vistrailsStartup.init()
            self._initialized = True
            return self.noninteractiveMode()
        else:
            self.setupSplashScreen()
            self.createWindows()
            self.vistrailsStartup.init() # Will hang...
            self._initialized = True
            self.interactiveMode() # Will hang...
            self.finishSplashScreen()
            return True

    def is_running_gui(self):
        # Who asks? This is probably not the GUI you are looking for...
        sys.stderr.write("-----\n")
        import traceback
        traceback.print_stack()
        sys.stderr.write("javagui.application:VistrailsJavaApplicationSingleton#is_running_gui()\n- - -\n")
        return False

    def setupSplashScreen(self):
        """ setupSplashScreen() -> None
        Create the splash-screen at startup

        """
        if self.temp_configuration.check('showSplash'):
            splashPath = (system.vistrails_root_directory() +
                          "/gui/resources/images/vistrails_splash.png")
            def run():
                self._splash_screen = JSplashScreen(splashPath, "Starting up...")

                # debug.splashMessage will call splashMessage() back
                debug.DebugPrint.getInstance().register_splash(self)

                # Blocks until setVisible(False) is called...
                # Documentation states that running this on the EDT won't stop
                # event processing
                self._splash_screen.setVisible(True)
            run_on_edt(run, async=True)

    def finishSplashScreen(self):
        if self._splash_screen is not None:
            def run():
                self._splash_screen.finish(self.builderWindow)
                self._splash_screen = None
            run_on_edt(run)

    def splashMessage(self, msg):
        if self._splash_screen is not None:
            def run():
                self._splash_screen.message = msg
            run_on_edt(run, async=True)
            
        
    def noninteractiveMode(self):
        # TODO : application#noninteractiveMode()
        sys.stderr.write("Error: non-interactive mode is not implemented!")
        
    def interactiveMode(self):
        def run():
            self.builderWindow.link_registry()
            self.builderWindow.create_first_vistrail()
        run_on_edt(run)

    def createWindows(self):
        """ createWindows() -> None
        Create and configure all GUI widgets including the builder

        """
        # This is so that we don't import too many things before we
        # have to. Otherwise, requirements are checked too late.
        from javagui.builder_frame import BuilderFrame

        def run():
            self.builderWindow = BuilderFrame()
            self.builderWindow.showFrame()
        run_on_edt(run)

    def wait_finish(self):
        """Wait for the user to close the window.
        """
        if self.builderWindow:
            self.builderWindow.waitClose()

    def finishSession(self):
        if self.builderWindow:
            self.builderWindow.setVisible(False)
        VistrailsApplicationInterface.finishSession(self)

# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_application(optionsDict=None):
    """Initializes the application singleton."""
    VistrailsApplication = get_vistrails_application()
    if VistrailsApplication:
        debug.critical("Application already started.")
        return
    VistrailsApplication = VistrailsJavaApplicationSingleton()
    set_vistrails_application(VistrailsApplication)
    try:
        core.requirements.check_all_vistrails_requirements()
    except core.requirements.MissingRequirement, e:
        msg = ("VisTrails requires %s to properly run.\n" %
               e.requirement)
        debug.critical("Missing requirement", msg)
        sys.exit(1)
    x = VistrailsApplication.init(optionsDict)
    if x == True:
        return 0
    else:
        return 1

def stop_application():
    """Stop and finalize the application singleton."""
    VistrailsApplication = get_vistrails_application()
    VistrailsApplication.finishSession()
    VistrailsApplication.save_configuration()
