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


from PyQt4 import QtGui, QtCore, Qt
from core import command_line
from core import debug
from core import system
from core import keychain
from core.modules.module_registry import registry
from core.utils import InstanceObject
from core.utils.uxml import (named_elements,
                             elements_filter, enter_named_element)
from gui import qt
from db.services.io import XMLFileLocator
import core.configuration
import core.interpreter.cached
import core.requirements
import core.startup
import gui.theme
import os.path
import sys

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
        if not self._initialized:
            self.init()
        return self

    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)
        if Qt.QT_VERSION < 0x40200: # 0x40200 = 4.2.0
            raise core.requirements.MissingRequirement("Qt version >= 4.2")
        self._initialized = False
        qt.allowQObjects()

    def init(self, optionsDict=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        gui.theme.initializeCurrentTheme()
        self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
        self.configuration = core.configuration.default()
        self.keyChain = keychain.KeyChain()
        self.setupOptions()

        # Setup configuration to default or saved preferences
        self.vistrailsStartup = core.startup.VistrailsStartup(self.configuration)

        # Command line options override configuration
        self.readOptions()
        if optionsDict:
            for (k, v) in optionsDict.iteritems():
                setattr(self.configuration, k, v)

        interactive = self.configuration.check('interactiveMode')
        if interactive:
            self.setIcon()
            self.createWindows()
            self.processEvents()
            
        self.vistrailsStartup.init()
        # ugly workaround for configuration initialization order issue
        # If we go through the configuration too late,
        # The window does not get maximized. If we do it too early,
        # there are no created windows during spreadsheet initialization.
        if interactive:
            if self.configuration.check('maximizeWindows'):
                self.builderWindow.showMaximized()
            if self.configuration.check('dbDefault'):
                self.builderWindow.setDBDefault(True)
        self.runInitialization()
        self._python_environment = self.vistrailsStartup.get_python_environment()
        self._initialized = True
        
        if interactive:
            self.interactiveMode()
        else:
            return self.noninteractiveMode()
        return True

    def get_python_environment(self):
        """get_python_environment(): returns an environment that
includes local definitions from startup.py. Should only be called
after self.init()"""
        return self._python_environment

    def destroy(self):
        """ destroy() -> None
        Finalize all packages to, such as, get rid of temp files
        
        """
        if hasattr(self, 'vistrailsStartup'):
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
        registry.connect(registry, registry.deletedModuleSignal, 
                         self.builderWindow.modulePalette.deletedModule)
        registry.connect(registry, registry.deletedPackageSignal, 
                         self.builderWindow.modulePalette.deletedPackage)
        if self.configuration.check('showSplash'):
            self.splashScreen.finish(self.builderWindow)
        if self.input:
            for filename in self.input:
                locator = XMLFileLocator(os.path.abspath(filename))
                self.builderWindow.open_vistrail_without_prompt(locator)
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
            if self.nonInteractiveOpts.parameters == None:
                self.nonInteractiveOpts.parameters = ''
            locator = XMLFileLocator(self.input[0])
            r = core.console_mode.run(locator,
                                      self.nonInteractiveOpts.workflow,
                                      self.nonInteractiveOpts.parameters)
            return r
        else:
            debug.DebugPrint.critical("no input vistrails provided")
            return False

    def setIcon(self):
        """ setIcon() -> None
        Setup Vistrail Icon
        """
        self.setWindowIcon(gui.theme.CurrentTheme.APPLICATION_ICON)
        
    def setupSplashScreen(self):
        """ setupSplashScreen() -> None
        Create the splash-screen at startup
        
        """
        if self.configuration.check('showSplash'):
            splashPath = (system.vistrails_root_directory() +
                          "/gui/resources/images/vistrails_splash.png")
            pixmap = QtGui.QPixmap(splashPath)
            self.splashScreen = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            self.splashScreen.show()

    def createWindows(self):
        """ createWindows() -> None
        Create and configure all GUI widgets including the builder
        
        """
        self.setupSplashScreen()
        if system.systemType in ['Darwin']:
            #to make all widgets to have the mac's nice looking
            self.installEventFilter(self)

        # This is so that we don't import too many things before we
        # have to. Otherwise, requirements are checked too late.
        from gui.builder_window import QBuilderWindow

        self.builderWindow = QBuilderWindow()
        self.builderWindow.show()
        self.visDiffParent = QtGui.QWidget(None, QtCore.Qt.ToolTip)
        self.visDiffParent.resize(0,0)
        
    def setupOptions(self):
        """ setupOptions() -> None
        Check and store all command-line arguments
        
        """
        add = command_line.CommandLineParser.add_option
        add("-S", "--startup", action="store", type="str", default="",
            dest="dotVistrails",
            help="Set startup file (default is ~/.vistrails/startup.py)")
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
            default = True,
            help="disable the logging")
        add("-d", "--debugsignals", action="store_true",
            default = False,
            help="debug Qt Signals")
        add("-a", "--parameters", action="store", dest="parameters",
            help="workflow parameter settings (non-interactive mode only)")
        command_line.CommandLineParser.parse_options()

    def printVersion(self):
        """ printVersion() -> None
        Print version of Vistrail and exit
        
        """
        print system.about_string()
        sys.exit(0)

    def readOptions(self):
        """ readOptions() -> None
        Read arguments from the command line
        
        """
        get = command_line.CommandLineParser().get_option
        if get('prompt'):
            self.configuration.pythonPrompt = True
        if get('nosplash'):
            self.configuration.showSplash = False
        self.configuration.debugSignals = bool(get('debugsignals'))
        self.configuration.dotVistrails = get('dotVistrails')
        if not self.configuration.check('dotVistrails'):
            self.configuration.dotVistrails = system.default_dot_vistrails()
        self.configuration.multiHeads = bool(get('multiheads'))
        self.configuration.maximizeWindows = bool(get('maximized'))
        self.configuration.showMovies = bool(get('movies'))
        self.configuration.useCache = bool(get('cache'))
        self.configuration.verbosenessLevel = get('verbose')
        if get('noninteractive'):
            self.configuration.interactiveMode = False
            self.nonInteractiveOpts = InstanceObject(workflow=get('workflow'),
                                                     parameters=get('parameters'))
        self.configuration.nologger = bool(get('nologger'))
        self.input = command_line.CommandLineParser().positional_arguments()
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

            # This is so that we don't import too many things before we
            # have to. Otherwise, requirements are checked too late.
            import gui.bookmark_window
            gui.bookmark_window.initBookmarks(system.default_bookmarks_file())    
            
        initBookmarks()
        if self.configuration.check('pythonPrompt'):
            debug.startVisTrailsREPL(locals())
        self.showSplash = self.configuration.showSplash

    def finishSession(self):
        logger = core.logger.Logger.get() 
        if logger:
            logger.finish_session()
        core.interpreter.cached.CachedInterpreter.cleanup()
   
    def eventFilter(self, o, event):
        """eventFilter(obj,event)-> boolean
        This will filter all create events and will set on the WA_MacMetalStyle
        attribute of a QWidget.
        
        """
        if(event.type() == QtCore.QEvent.Create and 
           issubclass(type(o),QtGui.QWidget) and
           type(o) != QtGui.QSplashScreen):
            o.setAttribute(QtCore.Qt.WA_MacMetalStyle)
        return QtGui.QApplication.eventFilter(self,o,event)

    def save_configuration(self):
        """ save_configuration() -> None
        Save the current vistrail configuration to the startup.xml file.
        This is required to capture changes to the configuration that we 
        make the session, ie., browsed directories or window sizes.

        """
        dom = self.vistrailsStartup.startup_dom()
        doc = dom.documentElement
        configuration_element = enter_named_element(doc, 'configuration')
        doc.removeChild(configuration_element)
        self.configuration.write_to_dom(dom, doc)
        self.vistrailsStartup.write_startup_dom(dom)
        dom.unlink()


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
    core.requirements.check_all_vistrails_requirements()
    x = VistrailsApplication.init(optionsDict)
    if x == True:
        return 0
    else:
        return 1

VistrailsApplication = None

def stop_application():
    """Stop and finalize the application singleton."""
    global VistrailsApplication
    VistrailsApplication.save_configuration()
    VistrailsApplication.destroy()
    VistrailsApplication.deleteLater()
