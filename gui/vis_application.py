import command_line
import debug
import sys
import copy
import time
import system
from PyQt4 import QtGui, QtCore
import qt
from common import InstanceObject
import os.path

class VistrailsApplication(QtGui.QApplication):
    def __init__(self, argv):
        QtGui.QApplication.__init__(self, argv)
        qt.allowQObjects()
        self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
        
        self.configuration = InstanceObject(
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
        self.startupHooks = []
        self.packageList = []
        self.setupOptions()
        self.readOptions()
        self.runInitialization()
        if not self.configuration.nologger:
            from logger import Logger
            self.logger = Logger()
        else:
            self.logger = None
        if self.configuration.interactiveMode:
            self.interactiveMode()
        else:
            self.noninteractiveMode()
        
    def interactiveMode(self):
        self.setIcon()
        self.createWindows()
        self.setupBaseModules()
        self.installPackages()
        self.runStartupHooks()

        if self.configuration.showSplash:
            self.splashScreen.finish(self.builderWindow)
	if self.input:
            self.builderWindow.openVistrail(os.path.abspath(self.input))
        QtGui.QApplication.setActiveWindow(self.builderWindow)

    def noninteractiveMode(self):
        self.setupBaseModules()
        self.installPackages()
        self.runStartupHooks()
        if self.input:
            if self.workflow == 0:
                print "invalid workflow"
                return
            import console_mode
            console_mode.run(self.input, self.workflow)
            return
        else:
            print "no input vistrails provided"
            return

    def setupBaseModules(self):
        import modules.vistrails_module
        import modules.basic_modules

    def setIcon(self):
        iconPath = system.visTrailsRootDirectory() + "/images/vistrails_icon_small.png"
        icon = QtGui.QIcon(iconPath)
        self.setWindowIcon(icon)
        
    def setupSplashScreen(self):
        if self.configuration.showSplash:
            splashPath = system.visTrailsRootDirectory() + "/images/vistrails_splash.png"
            pixmap = QtGui.QPixmap(splashPath)
            self.splashScreen = QtGui.QSplashScreen(pixmap)
            self.splashScreen.show()

    def createWindows(self):
        from qbuilder import QBuilder
        self.setupSplashScreen()
	self.builderWindow = QBuilder()
        if self.configuration.maximizeWindows:
            self.builderWindow.showMaximized()
        else:
            self.builderWindow.show()
        self.builderWindow.pipelineView.draw()
        self.setActiveWindow(self.builderWindow)
        self.visDiffParent = QtGui.QWidget(None, QtCore.Qt.ToolTip)
        self.visDiffParent.resize(0,0)
#        self.connect(self, QtCore.SIGNAL("aboutToQuit()"),self.builderWindow.closeAllVistrails)
        import modules.module_registry
        reg = modules.module_registry.registry
        reg.connect(reg, reg.newModuleSignal, 
                    self.builderWindow.modulePalette.treeManager.newModule)
        
    # Deal with command line here
    def setupOptions(self):
        add = command_line.CommandLineParser.addOption
        add("-S", "--startup", action="store", type="str", default="",
            dest="dotVistrails", help="Set startup file (default is ~/.vistrails)")
        add("-?", action="help",
            help="show this help message and exit")
        add("-p", "--prompt", action="store_true",
            default=False, dest="prompt",
            help="start a python prompt inside VisTrails")
        add("-v", "--version", action="callback",
            callback=lambda option, opt, value, parser: self.printVersion(),
            help="print version information and quit")
        add("-V", "--verbose", action="store", type="int", default=-1,
            dest="verbose", help="set verboseness level (0--2, default=0, higher means more verbose)")
        add("-n", "--nosplash", action="store_true",
            default = False,
            help="don't display splash on startup")
        add("-c", "--cache", action="store", type="int", default=1,
            dest="cache", help="enable/disable caching")
        add("-m", "--movies", action="store", type="int", default=1,
            dest="movies", help="""set automatic movie creation on spreadsheet (0 or 1, default=1. Set this
to zero to work around vtk bug with offscreen renderer and opengl texture3d mappers)""")
        add("-s", "--multiheads", action="store_true",
            default = False,
            help="display the builder and spreadsheet on different screens (if available)")
        add("-x", "--maximized", action="store_true",
            default = False,
            help="Maximize VisTrails windows at startup")
        add("-w", "--workflow", action="store", dest="workflow", help="set the workflow to be run")
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
        print system.aboutString()
        sys.exit(0)

    def readOptions(self):
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
        self.input = command_line.CommandLineParser().getArg(0)
        #self.output = command_line.CommandLineParser().getArg(1)
        self.workflow = get('workflow')

    def runInitialization(self):
        import system
        def addStartupHook(hook):
            self.startupHooks.append(hook)
        def addPackage(packageName, *args, **keywords):
            self.packageList.append([packageName,None, keywords])
        def execDotVistrails():
            try:
                dotVistrails = file(self.dotVistrails)
                code = compile("".join(dotVistrails.readlines()),
                               system.temporaryDirectory() + "dotVistrailsErrors.txt",
                               'exec')
                g = {}
                localsDir = {'configuration': self.configuration,
                             'addStartupHook': addStartupHook,
                             'addPackage': addPackage}
                eval(code, g, localsDir)
            except IOError:
                debug.DebugPrint.critical('%s not found' % self.dotVistrails)
                debug.DebugPrint.critical('Will not run an initialization file - there will only be the default modules')
        execDotVistrails()
        if self.configuration.pythonPrompt:
            debug.startVisTrailsREPL(locals())
        self.showSplash = self.configuration.showSplash
        if self.configuration.rootDirectory:
            system.setVistrailsDirectory(self.configuration.rootDirectory)
        if self.configuration.dataDirectory:
            system.setVistrailsDataDirectory(self.configuration.dataDirectory)
	if self.configuration.verbosenessLevel != -1:
            dbg = debug.DebugPrint
            if verbose < 0:
                msg = """Don't know how to set verboseness level to %s - setting to
the lowest one I know of: 0""" % verbose
                dbg.critical(msg)
                verbose = 0
            if verbose > 2:
                msg = """Don't know how to set verboseness level to %s - setting to
the highest one I know of: 2""" % verbose
                dbg.critical(msg)
                verbose = 2
            levels = [dbg.Critical, dbg.Warning, dbg.Log]
            dbg.setMessageLevel(levels[verbose])
            dbg.log("Set verboseness level to %s" % verbose)

    def installPackages(self):
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
        for hook in self.startupHooks:
            try:
                hook()
            except Exception, e:
                dbg = debug.DebugPrint
                dbg.critical("Exception raised during hook: %s - %s" % (e.__class__, e))

    def finishSession(self):
        if self.logger:
            self.logger.finishSession()
