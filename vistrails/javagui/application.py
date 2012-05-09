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
""" This is the main application of vistrail, it will calls for
initializations to the theme, packages and the builder...

"""


from core.application import VistrailsApplicationInterface, \
    get_vistrails_application, set_vistrails_application
from core import debug
from core import system
import core.requirements
import sys

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
        VistrailsApplicationInterface.__init__(self)

        self.builderWindow = None

    def init(self, optionsDict=None):
        """ VistrailsJavaApplicationSingleton(optionDict: dict)
                                          -> VistrailsJavaApplicationSingleton
        Create the application with a dict of settings

        """
        VistrailsApplicationInterface.init(self,optionsDict)

        self.vistrailsStartup.init()
        
        interactive = self.temp_configuration.check('interactiveMode')
        if interactive:
            self.createWindows()

        self._initialized = True

        if interactive:
            self.interactiveMode()
        else:
            r = self.noninteractiveMode()
            return r
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
            # TODO : display splash screen

    def splashMessage(self, msg):
        if hasattr(self, "splashScreen"):
            # TODO : display splash message
            pass
        
    def noninteractiveMode(self):
        # TODO : application#noninteractiveMode()
        sys.stderr.write("Error: non-interactive mode is not implemented!")
        
    def interactiveMode(self):
        if self.temp_configuration.check('showSplash'):
            pass #self.splashScreen.finish(self.builderWindow) FIXME
        self.builderWindow.link_registry()
        
        #self.builderWindow.create_first_vistrail()
        
        # Debug code -- load some modules and a test vistrail
        
        def load_module_if_req(codepath):
            package_manager = core.packagemanager.get_package_manager()
            try:
                package_manager.get_package_by_codepath(codepath)
            except core.packagemanager.PackageManager.MissingPackage:
                print "Loading package '%s'..." % codepath
                try:
                    package_manager.late_enable_package(codepath)
                    print "Loading complete"
                except core.packagemanager.PackageManager.MissingPackage, e:
                    sys.stderr.write("Unable to load package '%s':" % codepath, str(e), "\n")
            else:
                print "Package '%s' had already been loaded automatically" % codepath

        load_module_if_req('javaspreadsheet')
        load_module_if_req('obvioustest')

        self.builderWindow.open_vistrail("C:/Users/User_2/Documents/obvioustest.vt")

    def createWindows(self):
        """ createWindows() -> None
        Create and configure all GUI widgets including the builder

        """
        print "createWindows"
        
        self.setupSplashScreen()

        # This is so that we don't import too many things before we
        # have to. Otherwise, requirements are checked too late.
        from javagui.builder_frame import BuilderFrame

        self.builderWindow = BuilderFrame()
        
        if not self.temp_configuration.showSpreadsheetOnly:
            self.builderWindow.showFrame()

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
