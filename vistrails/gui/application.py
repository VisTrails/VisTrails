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
""" This is the main application of vistrail, it will calls for
initializations to the theme, packages and the builder...

"""


from PyQt4 import QtGui, QtCore
from core import command_line
from core import debug
from core import system
from core.modules.module_registry import registry
from core.utils import InstanceObject
from gui import qt
from gui.builder_window import QBuilderWindow
from gui.theme import CurrentTheme
import core.interpreter.cached
import gui.bookmark_window
import gui.theme
import os.path
import sys
import core.startup

################################################################################

class VistrailsApplicationSingleton(QtGui.QApplication):
    """
    VistrailsApplicationSingleton is the singleton of the application,
    there will be only one instance of the application during VisTrails
    
    """
    
    def __call__(self):
        """ __call__() -> VistrailsApplicationSingleton
        Return self for calling method
        
        """
        return self

    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)
        qt.allowQObjects()

    def init(self, optionsDict=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        gui.theme.initializeCurrentTheme()
        self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
        
        self.configuration = core.startup.vistrailsDefaultConfiguration()
        self.setupOptions()
        self.readOptions()
        if optionsDict:
            for (k, v) in optionsDict.iteritems():
                setattr(self.configuration, k, v)
        self.vistrailsStartup = core.startup.VistrailsStartup()
        if self.configuration.interactiveMode:
            self.setIcon()
            self.createWindows()
            self.processEvents()
            
        self.vistrailsStartup.init(self.configuration)
        self.runInitialization()
        
        if self.configuration.interactiveMode:
            self.interactiveMode()
        else:
            self.noninteractiveMode()

    def destroy(self):
        """ destroy() -> None
        Finalize all packages to, such as, get rid of temp files
        
        """
        self.vistrailsStartup.destroy()

    def __del__(self):
        """ __del__() -> None
        Make sure to finalize in the destructor
        
        """
        self.destroy()

    def interactiveMode(self):
        """ interactiveMode() -> None
        Instantiate the GUI for interactive mode
        
        """
        self.builderWindow.modulePalette.treeWidget.updateFromModuleRegistry()
        registry.connect(registry, registry.newModuleSignal, 
                         self.builderWindow.modulePalette.newModule)
        if self.configuration.showSplash:
            self.splashScreen.finish(self.builderWindow)
        if self.input:
            for filename in self.input:
                self.builderWindow.viewManager.openVistrail(
                    os.path.abspath(filename))
        self.builderWindow.activateWindow()

    def noninteractiveMode(self):
        """ noninteractiveMode() -> None
        Run the console in non-interactive mode
        
        """
        if self.input:
            if not self.nonInteractiveOpts.workflow:
                debug.DebugPrint.critical('need workflow tag or id to \
run in batch mode.')
                sys.exit(1)
            if len(self.input) > 1:
                print "Only one vistrail can be specified for non-interactive mode"
            import core.console_mode
            core.console_mode.run(self.input[0],
                                  self.nonInteractiveOpts.workflow)
        else:
            debug.DebugPrint.critical("no input vistrails provided")

    def setIcon(self):
        """ setIcon() -> None
        Setup Vistrail Icon
        """
        iconPath = (system.visTrailsRootDirectory() +
                    "/gui/resources/images/vistrails_icon_small.png")
        icon = QtGui.QIcon(iconPath)
        self.setWindowIcon(icon)
        
    def setupSplashScreen(self):
        """ setupSplashScreen() -> None
        Create the splash-screen at startup
        
        """
        if self.configuration.showSplash:
            splashPath = (system.visTrailsRootDirectory() +
                          "/gui/resources/images/vistrails_splash.png")
            pixmap = QtGui.QPixmap(splashPath)
            self.splashScreen = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            self.splashScreen.show()

    def createWindows(self):
        """ createWindows() -> None
        Create and configure all GUI widgets including the builder
        
        """
        self.setupSplashScreen()
        self.builderWindow = QBuilderWindow()
        if self.configuration.maximizeWindows:
            self.builderWindow.showMaximized()
        else:
            self.builderWindow.show()
        self.visDiffParent = QtGui.QWidget(None, QtCore.Qt.ToolTip)
        self.visDiffParent.resize(0,0)
        
    def setupOptions(self):
        """ setupOptions() -> None
        Check and store all command-line arguments
        
        """
        add = command_line.CommandLineParser.addOption
        add("-S", "--startup", action="store", type="str", default="",
            dest="dotVistrails",
            help="Set startup file (default is ~/.vistrails)")
        add("-?", action="help",
            help="show this help message and exit")
        add("-p", "--prompt", action="store_true",
            default=False, dest="prompt",
            help="start a python prompt inside VisTrails")
        add("-v", "--version", action="callback",
            callback=lambda option, opt, value, parser: self.printVersion(),
            help="print version information and quit")
        add("-V", "--verbose", action="store", type="int", default=-1,
            dest="verbose", help="set verboseness level (0--2, "
            "default=0, higher means more verbose)")
        add("-n", "--nosplash", action="store_true",
            default = False,
            help="don't display splash on startup")
        add("-c", "--cache", action="store", type="int", default=1,
            dest="cache", help="enable/disable caching")
        add("-m", "--movies", action="store", type="int", default=1,
            dest="movies", help="""set automatic movie creation on spreadsheet "
            "(0 or 1, default=1. Set this to zero to work around vtk bug with "
            "offscreen renderer and opengl texture3d mappers)""")
        add("-s", "--multiheads", action="store_true",
            default = False,
            help="display the builder and spreadsheet on different screens "
            "(if available)")
        add("-x", "--maximized", action="store_true",
            default = False,
            help="Maximize VisTrails windows at startup")
        add("-w", "--workflow", action="store", dest="workflow",
            help="set the workflow to be run (non-interactive mode only)")
        add("-b", "--noninteractive", action="store_true",
            default = False,
            help="run in non-interactive mode")
        add("-l", "--nologger", action="store_true",
            default = False,
            help="disable the logging")
        add("-d", "--debugsignals", action="store_true",
            default = False,
            help="debug Qt Signals")
        command_line.CommandLineParser.parseOptions()

    def printVersion(self):
        """ printVersion() -> None
        Print version of Vistrail and exit
        
        """
        print system.aboutString()
        sys.exit(0)

    def readOptions(self):
        """ readOptions() -> None
        Read arguments from the command line
        
        """
        get = command_line.CommandLineParser().getOption
        if get('prompt'):
            self.configuration.pythonPrompt = True
        if get('nosplash'):
            self.configuration.showSplash = False
        self.configuration.debugSignals = get('debugsignals')
        self.configuration.dotVistrails = get('dotVistrails')
        if not self.configuration.dotVistrails:
            self.configuration.dotVistrails = system.defaultDotVistrails()
        self.configuration.multiHeads = get('multiheads')
        self.configuration.maximizeWindows = get('maximized')
        self.configuration.showMovies = get('movies')
        self.configuration.useCache = get('cache')
        self.configuration.verbosenessLevel = get('verbose')
        if get('noninteractive'):
            self.configuration.interactiveMode = False
            self.nonInteractiveOpts = InstanceObject(workflow=get('workflow'))
        self.configuration.nologger = get('nologger')
        self.input = command_line.CommandLineParser().positionalArguments()
        if get('workflow') and not get('noninteractive'):
            print "Workflow option only allowed in noninteractive mode."
            sys.exit(1)

    def runInitialization(self):
        """ runInitialization() -> None
        Run init script on the user folder
        
        """
        def initBookmarks():
            """loadBookmarkCollection() -> None
            Init BookmarksManager and creates .vistrails folder if it 
            does not exist 

            """
            if (not os.path.isdir(self.configuration.dotVistrails) and 
                not os.path.isfile(self.configuration.dotVistrails)):
                #create .vistrails dir
                os.mkdir(self.configuration.dotVistrails)
            gui.bookmark_window.initBookmarks(system.defaultBookmarksFile())    
            
        initBookmarks()
        if self.configuration.pythonPrompt:
            debug.startVisTrailsREPL(locals())
        self.showSplash = self.configuration.showSplash

    def finishSession(self):
        gui.bookmark_window.finalizeBookmarks()        
        if core.startup.logger:
            core.startup.logger.finishSession()
        core.interpreter.cached.CachedInterpreter.cleanup()

# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_application(optionsDict=None):
    """Initializes the application singleton."""
    global VistrailsApplication
    if VistrailsApplication:
        print "Application already started."""
        return
    VistrailsApplication = VistrailsApplicationSingleton()
    VistrailsApplication.init(optionsDict)

VistrailsApplication = None

def stop_application():
    """Stop and finalize the application singleton."""
    global VistrailsApplication
    VistrailsApplication.destroy()
    VistrailsApplication.deleteLater()
