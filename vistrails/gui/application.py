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
import copy
import core.interpreter.cached
import core.system
import gui.bookmark_window
import gui.theme
import os.path
import shutil
import sys
import tempfile
import time

################################################################################

logger = None

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
        pass

    def init(self, optionsDict=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        global logger
        QtGui.QApplication.__init__(self, sys.argv)
        qt.allowQObjects()
        gui.theme.initializeCurrentTheme()
        self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
        
        self.configuration = InstanceObject(
            packageDirectory=None,
            pythonPrompt=False,
            debugSignals=False,
            showSplash=True,
            verbosenessLevel=-1,
            useCache=True,
            minMemory=-1,
            maxMemory=-1,
            pluginList=[],
            multiHeads=False,
            maximizeWindows=False,
            showMovies=True,
            interactiveMode=True,
            nologger=False,
            rootDirectory=None,
            dataDirectory=None,
            fileRepository=InstanceObject(dbHost='',
                                          dbPort=0,
                                          dbUser='',
                                          dbPasswd='',
                                          dbName='',
                                          sshHost='',
                                          sshPort=0,
                                          sshUser='',
                                          sshDir='',
                                          localDir=''),
            logger=InstanceObject(dbHost='',
                                  dbPort=0,
                                  dbUser='',
                                  dbPasswd='',
                                  dbName=''))
        if optionsDict:
            for (k, v) in optionsDict.iteritems():
                setattr(self.configuration, k, v)
        self.startupHooks = []
        self.packageList = []
        self.setupOptions()
        self.readOptions()
        self.runInitialization()
        if not self.configuration.nologger:
            from core.logger import Logger
            logger = Logger()
        else:
            logger = None
        if self.configuration.interactiveMode:
            self.interactiveMode()
        else:
            self.noninteractiveMode()

    def destroy(self):
        """ destroy() -> None
        Finalize all packages to, such as, get rid of temp files
        
        """
        if not hasattr(self, "__destroyed"):
            for (packageName, packageModule, _) in self.packageList:
                print "Finalizing",packageName
                try:
                    x = packageModule.finalize
                except AttributeError:
                    pass
                else:
                    x()
            self.__destroyed = True

    def __del__(self):
        """ __del__() -> None
        Make sure to finalize in the destructor
        
        """
        self.destroy()

    def interactiveMode(self):
        """ interactiveMode() -> None
        Instantiate the GUI for interactive mode
        
        """
        self.setIcon()
        self.createWindows()
        self.setupBaseModules()
        self.processEvents()
        self.installPackages()
        self.runStartupHooks()
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
        self.setupBaseModules()
        self.installPackages()
        self.runStartupHooks()
        if self.input:
            if self.workflow == 0:
                print "invalid workflow"
                return
            if len(self.input) > 1:
                print "Only one vistrail can be specified for non-interactive mode"
            import core.console_mode
            core.console_mode.run(self.input[0], self.workflow)
            return
        else:
            print "no input vistrails provided"
            return

    def setupBaseModules(self):
        """ setupBaseModules() -> None        
        Import basic modules for self-registration. The import here is
        on purpose, not a typo against the coding rule
        
        """
        import core.modules.vistrails_module
        import core.modules.basic_modules

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
        self.dotVistrails = get('dotVistrails')
        if not self.dotVistrails:
            self.dotVistrails = system.defaultDotVistrails()
        self.configuration.multiHeads = get('multiheads')
        self.configuration.maximizeWindows = get('maximized')
        self.configuration.showMovies = get('movies')
        self.configuration.useCache = get('cache')
        self.configuration.verbosenessLevel = get('verbose')
        if get('noninteractive'):
            self.configuration.interactiveMode = False
        self.configuration.nologger = get('nologger')
        self.input = command_line.CommandLineParser().positionalArguments()
        self.workflow = get('workflow')
        if get('workflow') and not get('noninteractive'):
            print "Workflow option only allowed in noninteractive mode."
            sys.exit(1)

    def runInitialization(self):
        """ runInitialization() -> None
        Run init script on the user folder
        
        """
        def addStartupHook(hook):
            """ addStartupHook(hook: function) -> None
            Add a hook for start-up after initialization
            
            """
            self.startupHooks.append(hook)

        def addPackage(packageName, *args, **keywords):
            """ addPackage(packageName: str, *args) -> None
            """
            self.packageList.append([packageName,None, keywords])

        def install_default_startup():
            debug.critical('Will try to create default startup script')
            try:
                shutil.copyfile((core.system.visTrailsRootDirectory() +
                                 'core/resources/default_vistrails_startup'),
                                self.dotVistrails + '/startup.py')
                debug.critical('Succeeded!')
            except:
                debug.critical("""Failed to copy default file to .vistrails.
This could be an indication of a permissions problem.
Make sure directory '%s' is writable""" % self.dotVistrails)
                sys.exit(1)

        def create_default_directory():
            debug.critical('Will try to create default directory')
            try:
                os.mkdir(self.dotVistrails)
                debug.critical('Succeeded!')
            except:
                debug.critical("""Failed to create initialization directory.
This could be an indication of a permissions problem. Make sure parent
directory of '%'s is writable.""" % self.dotVistrails)
                sys.exit(1)

        def execDotVistrails(tried_once=False):
            """ execDotVistrails() -> None
            Actually execute the Vistrail initialization
            
            """
            # if it is file, then must move old-style .vistrails to
            # directory.
            if os.path.isfile(self.dotVistrails):
                debug.warning("Old-style initialization hooks. Will try to set things correctly.")
                (fd, name) = tempfile.mkstemp()
                os.close(fd)
                shutil.copyfile(self.dotVistrails, name)
                try:
                    os.unlink(self.dotVistrails)
                except:
                    debug.critical("""Failed to remove old initialization file.
This could be an indication of a permissions problem.
Make sure file '%s' is writable.""" % self.dotVistrails)
                    sys.exit(1)
                create_default_directory()
                try:
                    shutil.copyfile(name, self.dotVistrails + '/startup.py')
                except:
                    debug.critical("""Failed to copy old initialization file to
newly-created initialization directory. This must have been a race condition.
Please remove '%s' and restart VisTrails.""" % self.dotVistrails)
                    sys.exit(1)
                debug.critical("Successful move!")
                try:
                    os.unlink(name)
                except:
                    debug.warning("Failed to erase temporary file.")

            if os.path.isdir(self.dotVistrails):
                try:
                    dotVistrails = file(self.dotVistrails + '/startup.py')
                    code = compile("".join(dotVistrails.readlines()),
                                   system.temporaryDirectory() +
                                   "dotVistrailsErrors.txt",
                                   'exec')
                    g = {}
                    localsDir = {'configuration': self.configuration,
                                 'addStartupHook': addStartupHook,
                                 'addPackage': addPackage}
                    eval(code, g, localsDir)
                except IOError:
                    if tried_once:
                        debug.critical("""Still cannot find default file.
Something has gone wrong. Please make sure ~/.vistrails exists, is writable,
and ~/.vistrails/startup.py does not exist.""")
                        sys.exit(1)
                    debug.critical('%s not found' %
                                   (self.dotVistrails +
                                    '/startup.py'))
                    debug.critical('Will try to install default' +
                                              'startup file')
                    install_default_startup()
                    execDotVistrails(True)
            elif not os.path.lexists(self.dotVistrails):
                debug.critical('%s not found' % self.dotVistrails)
                create_default_directory()
                install_default_startup()
                execDotVistrails(True)

        def initBookmarks():
            """loadBookmarkCollection() -> None
            Init BookmarksManager and creates .vistrails folder if it 
            does not exist 

            """
            if (not os.path.isdir(self.dotVistrails) and 
                not os.path.isfile(self.dotVistrails)):
                #create .vistrails dir
                os.mkdir(self.dotVistrails)
            gui.bookmark_window.initBookmarks(system.defaultBookmarksFile())    
            
        execDotVistrails()
        initBookmarks()
        if self.configuration.pythonPrompt:
            debug.startVisTrailsREPL(locals())
        self.showSplash = self.configuration.showSplash
        if self.configuration.rootDirectory:
            system.setVistrailsDirectory(self.configuration.rootDirectory)
        if self.configuration.dataDirectory:
            system.setVistrailsDataDirectory(self.configuration.dataDirectory)
        if self.configuration.verbosenessLevel != -1:
            dbg = debug.DebugPrint
            verbose = self.configuration.verbosenessLevel
            if verbose < 0:
                msg = ("""Don't know how to set verboseness level to %s - "
                       "setting tothe lowest one I know of: 0""" % verbose)
                dbg.critical(msg)
                verbose = 0
            if verbose > 2:
                msg = ("""Don't know how to set verboseness level to %s - "
                       "setting to the highest one I know of: 2""" % verbose)
                dbg.critical(msg)
                verbose = 2
            levels = [dbg.Critical, dbg.Warning, dbg.Log]
            dbg.setMessageLevel(levels[verbose])
            dbg.log("Set verboseness level to %s" % verbose)

    def installPackages(self):
        """ installPackages() -> None
        Scheme through packages directory and initialize them all
        """
        if self.configuration.packageDirectory:
            sys.path.append(self.configuration.packageDirectory)
        import packages

        # import all packages in list
        for package in self.packageList:
            try:
                __import__('packages.'+package[0], globals(), locals(), [])
                package[1] = getattr(packages, package[0])
            except ImportError, e:
                dbg = debug.DebugPrint
                dbg.critical("Could not install package %s" % package[0])
                raise

        # initialize all packages in list
        for (packageName, packageModule, packageParams) in self.packageList:
            print "Initializing ",packageName
            oldPath = copy.copy(sys.path)
            sys.path.append(system.visTrailsRootDirectory() +
                            '/packages/' +
                            packageName)
            packageModule.initialize(**packageParams)
            sys.path = oldPath

    def runStartupHooks(self):
        """ runStartupHooks() -> None
        After initialization, need to run all start up hooks registered
        
        """
        for hook in self.startupHooks:
            try:
                hook()
            except Exception, e:
                dbg = debug.DebugPrint
                dbg.critical("Exception raised during hook: %s - %s" %
                             (e.__class__, e))

    def finishSession(self):
        global logger
        gui.bookmark_window.finalizeBookmarks()
        if logger:
            logger.finishSession()
        core.interpreter.cached.CachedInterpreter.cleanup()

# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_application(optionsDict=None):
    """Initializes the application singleton."""
    global VistrailsApplication
    VistrailsApplication = VistrailsApplicationSingleton()
    VistrailsApplication.init(optionsDict)

VistrailsApplication = None

def stop_application():
    """Stop and finalize the application singleton."""
    global VistrailsApplication
    VistrailsApplication.destroy()
    VistrailsApplication.deleteLater()
