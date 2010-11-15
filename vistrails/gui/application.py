############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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


from PyQt4 import QtGui, QtCore, QtNetwork
from core import command_line
from core import debug
from core import system
from core import keychain
from core.db.locator import FileLocator, DBLocator
from core.utils import InstanceObject
from core.utils.uxml import enter_named_element
from gui import qt
import core.configuration
import core.interpreter.default
import core.interpreter.cached
import core.requirements
import core.startup
import gui.theme
import os.path
import sys
import copy

################################################################################
class VistrailsApplicationInterface(object):
    def __init__(self):
        self._initialized = False
    
    def setupOptions(self):
        """ setupOptions() -> None
        Check and store all command-line arguments
        
        """
        add = command_line.CommandLineParser.add_option
        add("-S", "--startup", action="store", type="str", default=None,
            dest="dotVistrails",
            help="Set startup file (default is ~/.vistrails/startup.py)")
        add("-?", action="help",
            help="show this help message and exit")
        add("-v", "--version", action="callback",
            callback=lambda option, opt, value, parser: self.printVersion(),
            help="print version information and quit")
        add("-V", "--verbose", action="store", type="int", default=None,
            dest="verbose", help="set verboseness level (0--2, "
            "default=0, higher means more verbose)")
        add("-n", "--nosplash", action="store_false",
            default = None,
            help="don't display splash on startup")
        add("-c", "--cache", action="store", type="int", default=None,
            dest="cache", help="enable/disable caching")
        add("-m", "--movies", action="store", type="int", default=None,
            dest="movies", help="set automatic movie creation on spreadsheet "
            "(0 or 1, default=1. Set this to zero to work around vtk bug with "
            "offscreen renderer and opengl texture3d mappers)")
        add("-s", "--multiheads", action="store_true",
            default = None,
            help="display the builder and spreadsheet on different screens "
            "(if available)")
        add("-x", "--maximized", action="store_true",
            default = None,
            help="Maximize VisTrails windows at startup")
        add("-b", "--noninteractive", action="store_true",
            default = None,
            help="run in non-interactive mode")
        add("-e", "--dumpcells", action="store", dest="dumpcells",
            default = None,
            help="when running in non-interactive mode, directory to dump "
            "spreadsheet cells before exiting")
        add("-p", "--pdf", action="store_true",
            default = None,
            help="dump files in pdf format (only valid in console mode)")
        add("-l", "--nologger", action="store_true",
            default = None,
            help="disable the logging")
        add("-d", "--debugsignals", action="store_true",
            default = None,
            help="debug Qt Signals")
        add("-a", "--parameters", action="store", dest="parameters",
            help="workflow parameter settings (non-interactive mode only)")
        add("-t", "--host", action="store", dest="host",
            help="hostname or ip address of database server")
        add("-r", "--port", action="store", type="int", default=3306,
            dest="port", help="database port")
        add("-f", "--db", action="store", dest="db",
            help="database name")
        add("-u", "--user", action="store", dest="user",
            help="database username")
        add("-i", "--showspreadsheetonly", action="store_true",
            default = None,
            help="only the spreadsheet will be shown. This implies -w was given.\
The builder window can be accessed by a spreadsheet menu option.")
        add("-w", "--executeworkflows", action="store_true",
            default = None,
            help="The workflows will be executed")
        add("-I", "--workflowinfo", action="store",
            default = None,
            help=("Save workflow graph and spec in specified directory "
                  "(only valid in console mode)."))
        add("-E", "--reviewmode", action="store_true",
            default = None,
            help="Show the spreadsheet in the reviewing mode")
        add("-q", "--quickstart", action="store",
            help="Start VisTrails using the specified static registry")
        add("-D", "--detachHistoryView", action="store_true",
            help="Detach the history view from the builder windows")
        command_line.CommandLineParser.parse_options()

    def printVersion(self):
        """ printVersion() -> None
        Print version of Vistrail and exit
        
        """
        print system.about_string()
        sys.exit(0)
        
    def read_dotvistrails_option(self):
        """ read_dotvistrails_option() -> None
        Check if the user sets a new dotvistrails folder and updates 
        self.temp_configuration with the new value. 
        
        """
        get = command_line.CommandLineParser().get_option
        if get('dotVistrails')!=None:
            self.temp_configuration.dotVistrails = get('dotVistrails')
            
    def readOptions(self):
        """ readOptions() -> None
        Read arguments from the command line
        
        """
        get = command_line.CommandLineParser().get_option
        if get('nosplash')!=None:
            self.temp_configuration.showSplash = bool(get('nosplash'))
        if get('debugsignals')!=None:
            self.temp_configuration.debugSignals = bool(get('debugsignals'))
        if get('dotVistrails')!=None:
            self.temp_configuration.dotVistrails = get('dotVistrails')
        #in theory this should never happen because core.configuration.default()
        #should have done this already
        #if not self.configuration.check('dotVistrails'):
        #    self.configuration.dotVistrails = system.default_dot_vistrails()
        #    self.temp_configuration.dotVistrails = system.default_dot_vistrails()
        if get('multiheads')!=None:
            self.temp_configuration.multiHeads = bool(get('multiheads'))
        if get('maximized')!=None:
            self.temp_configuration.maximizeWindows = bool(get('maximized'))
        if get('movies')!=None:
            self.temp_configuration.showMovies = bool(get('movies'))
        if get('cache')!=None:
            self.temp_configuration.useCache = bool(get('cache'))
        if get('verbose')!=None:
            self.temp_configuration.verbosenessLevel = get('verbose')
        if get('noninteractive')!=None:
            self.temp_configuration.interactiveMode = \
                                                  not bool(get('noninteractive'))
            if get('workflowinfo') != None:
                self.temp_configuration.workflowInfo = str(get('workflowinfo'))
            if get('dumpcells') != None:
                self.temp_configuration.spreadsheetDumpCells = get('dumpcells')
            if get('pdf') != None:
                self.temp_configuration.spreadsheetDumpPDF = get('pdf')
        if get('executeworkflows') != None:
            self.temp_configuration.executeWorkflows = \
                                            bool(get('executeworkflows'))
        if get('showspreadsheetonly') != None:
            self.temp_configuration.showSpreadsheetOnly = \
                                            bool(get('showspreadsheetonly'))
            # asking to show only the spreadsheet will force the workflows to
            # be executed
            if get('reviewmode') != None:
                self.temp_configuration.reviewMode = bool(get('reviewmode'))

            if self.temp_configuration.showSpreadsheetOnly and not self.temp_configuration.reviewMode:
                self.temp_configuration.executeWorkflows = True
            
        self.temp_db_options = InstanceObject(host=get('host'),
                                                 port=get('port'),
                                                 db=get('db'),
                                                 user=get('user'),
                                                 parameters=get('parameters')
                                                 )
        if get('nologger')!=None:
            self.temp_configuration.nologger = bool(get('nologger'))
        if get('quickstart') != None:
            self.temp_configuration.staticRegistry = str(get('quickstart'))
        if get('detachHistoryView')!= None:
            self.temp_configuration.detachHistoryView = bool(get('detachHistoryView'))
        self.input = command_line.CommandLineParser().positional_arguments()
    
    def init(self, optionsDict=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        gui.theme.initializeCurrentTheme()
        self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
        
        # This is the persistent configuration
        # Setup configuration to default
        self.configuration = core.configuration.default()
        
        self.keyChain = keychain.KeyChain()
        self.setupOptions()
        
        # self.temp_configuration is the configuration that will be updated 
        # with the command line and custom options dictionary. 
        # We have to do this because we don't want to make these settings 
        # persistent. This is the actual VisTrails current configuration
        self.temp_configuration = copy.copy(self.configuration)
        
        core.interpreter.default.connect_to_configuration(self.temp_configuration)
        
        # now we want to open vistrails and point to a specific version
        # we will store the version in temp options as it doesn't
        # need to be persistent. We will do the same to database
        # information passed in the command line
        self.temp_db_options = InstanceObject(host=None,
                                           port=None,
                                           db=None,
                                           user=None,
                                           vt_id=None,
                                           parameters=None
                                           ) 
        
        # Read only new .vistrails folder option if passed in the command line
        # or in the optionsDict because this may affect the configuration file 
        # VistrailsStartup will load. This updates self.temp_configuration
        self.read_dotvistrails_option()
        
        if optionsDict and 'dotVistrails' in optionsDict.keys():
            self.temp_configuration.dotVistrails = optionsDict['dotVistrails']
                
        # During this initialization, VistrailsStartup will load the
        # configuration from disk and update both configurations
        self.vistrailsStartup = core.startup.VistrailsStartup(self.configuration,
                                                    self.temp_configuration)
        
        # the problem here is that if the user pointed to a new .vistrails
        # folder, the persistent configuration will always point to the 
        # default ~/.vistrails. So we will copy whatever it's on 
        # temp_configuration to the persistent one. In case the configuration
        # that is on disk is different, it will overwrite this one
        self.configuration.dotVistrails = self.temp_configuration.dotVistrails
        
        # Starting in version 1.2.1 logging is enabled by default.
        # Users have to explicitly disable it through the command-line
        self.configuration.nologger = False
        self.temp_configuration.nologger = False
        
        if optionsDict:
            for (k, v) in optionsDict.iteritems():
                setattr(self.temp_configuration, k, v)
                
        # Command line options override temp_configuration
        self.readOptions()
        
        if self.temp_configuration.check('staticRegistry'):
            reg = self.temp_configuration.staticRegistry
        else:
            reg = None
        self.vistrailsStartup.set_registry(reg)
        
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
    
    def _parse_vtinfo(self, info, use_filename=True):
        name = None
        version = None
        if use_filename and os.path.isfile(info):
            name = info
        else:
            data = info.split(":")
            if len(data) >= 2:
                if use_filename:
                    if os.path.isfile(str(data[0])):
                        name = str(data[0])
                    else:
                        # maybe we are running on Windows and a full path
                        # was passed as the filename so it has a : separating
                        # the driver letter
                        if system.systemType in ["Windows", "Microsoft"]:
                            if os.path.isfile(":".join(data[:2])):
                                name = ":".join(data[:2])
                                data.pop(0)
                                data[0] = name
                elif not use_filename:
                    name = str(data[0])
                # will try to convert version to int
                # if it fails, it's a tag name
                try:
                    #maybe a tag name contains ':' in its name
                    #so we need to bring it back together
                    rest = ":".join(data[1:])
                    version = int(rest)
                except ValueError:
                    version = str(rest)
            elif len(data) == 1:
                if use_filename and os.path.isfile(str(data[0])):
                    name = str(data[0])
                elif not use_filename:
                    name = str(data[0])
        return (name, version)
    
    def process_interactive_input(self):
        usedb = False
        if self.temp_db_options.host:
            usedb = True
        if self.input:
            locator = None
            #check if versions are embedded in the filename
            for filename in self.input:
                f_name, version = self._parse_vtinfo(filename, not usedb)
                if f_name is None:
                    msg = "VisTrails could not find file %s"%filename
                    QtGui.QMessageBox.critical(None, "File not found",
                                               msg)
                elif not usedb:
                    locator = FileLocator(os.path.abspath(f_name))
                    #_vnode and _vtag will be set when a .vtl file is open and
                    # it can be either a FileLocator or a DBLocator
                    if hasattr(locator, '_vnode'):
                        version = locator._vnode
                    if hasattr(locator,'_vtag'):
                        # if a tag is set, it should be used instead of the
                        # version number
                        if locator._vtag != '':
                            version = locator._vtag
                elif usedb:
                    locator = DBLocator(host=self.temp_db_options.host,
                                        port=self.temp_db_options.port,
                                        database=self.temp_db_options.db,
                                        user='',
                                        passwd='',
                                        obj_id=f_name,
                                        obj_type=None,
                                        connection_id=None)
                if locator:
                    execute = self.temp_configuration.executeWorkflows
                    self.builderWindow.open_vistrail_without_prompt(locator,
                                                                    version,
                                                                    execute)
                if self.temp_configuration.reviewMode:
                    self.builderWindow.interactiveExportCurrentPipeline()
                
    def finishSession(self):
        core.interpreter.cached.CachedInterpreter.cleanup()
        
    def save_configuration(self):
        """ save_configuration() -> None
        Save the current vistrail configuration to the startup.xml file.
        This is required to capture changes to the configuration that we 
        make programmatically during the session, ie., browsed directories or
        window sizes.

        """
        dom = self.vistrailsStartup.startup_dom()
        doc = dom.documentElement
        configuration_element = enter_named_element(doc, 'configuration')
        doc.removeChild(configuration_element)
        self.configuration.write_to_dom(dom, doc)
        self.vistrailsStartup.write_startup_dom(dom)
        dom.unlink()
        
class VistrailsApplicationSingleton(VistrailsApplicationInterface,
                                    QtGui.QApplication):
    """
    VistrailsApplicationSingleton is the singleton of the application,
    there will be only one instance of the application during VisTrails
    
    """
    
    def __call__(self):
        """ __call__() -> VistrailsApplicationSingleton
        Return self for calling method
        
        """
        if not self._initialized and not self._is_running:
            self.init()
        return self

    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)
        VistrailsApplicationInterface.__init__(self)
        if QtCore.QT_VERSION < 0x40200: # 0x40200 = 4.2.0
            raise core.requirements.MissingRequirement("Qt version >= 4.2")
        self._is_running = False
        # code for single instance of the application
        # based on the C++ solution availabe at
        # http://wiki.qtcentre.org/index.php?title=SingleApplication
        if QtCore.QT_VERSION >= 0x40400:
            self.timeout = 5000
            self._unique_key = "vistrails-single-instance-check"
            self.shared_memory = QtCore.QSharedMemory(self._unique_key)
            self.local_server = None
            if self.shared_memory.attach():
                self._is_running = True
            else:
                self._is_running = False
                if not self.shared_memory.create(1):
                    print "Unable to create single instance of vistrails application"
                    return
                self.local_server = QtNetwork.QLocalServer(self)
                self.connect(self.local_server, QtCore.SIGNAL("newConnection()"),
                             self.message_received)
                self.local_server.listen(self._unique_key)
                #print "Listening on ", self.local_server.serverName()
        qt.allowQObjects()

    def init(self, optionsDict=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        VistrailsApplicationInterface.init(self,optionsDict)

        interactive = self.temp_configuration.check('interactiveMode')
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
            if  self.temp_configuration.check('maximizeWindows'):
                self.builderWindow.showMaximized()
            if self.temp_configuration.check('dbDefault'):
                self.builderWindow.setDBDefault(True)
        self._python_environment = self.vistrailsStartup.get_python_environment()
        self._initialized = True
        
        if interactive:
            self.interactiveMode()
        else:
            r = self.noninteractiveMode()
            return r
        return True

    def interactiveMode(self):
        """ interactiveMode() -> None
        Instantiate the GUI for interactive mode
        
        """     
        if self.temp_configuration.check('showSplash'):
            self.splashScreen.finish(self.builderWindow)
        self.builderWindow.create_first_vistrail()
        self.builderWindow.modulePalette.updateFromModuleRegistry()
        self.builderWindow.modulePalette.connect_registry_signals()
        
        self.process_interactive_input()

        if not self.temp_configuration.showSpreadsheetOnly:
            # in some systems (Linux and Tiger) we need to make both calls
            # so builderWindow is activated
            self.setActiveWindow(self.builderWindow)
            self.builderWindow.activateWindow()
            self.builderWindow.show()
            self.builderWindow.raise_()
        else:
            self.builderWindow.hide()

    def noninteractiveMode(self):
        """ noninteractiveMode() -> None
        Run the console in non-interactive mode
        
        """
        usedb = False
        if self.temp_db_options.host:
            usedb = True
        if self.input:
            w_list = []
            for filename in self.input:
                f_name, version = self._parse_vtinfo(filename, not usedb)
                if f_name and version:
                    if not usedb:
                        locator = FileLocator(os.path.abspath(f_name))
                    else:
                        locator = DBLocator(host=self.temp_db_options.host,
                                            port=self.temp_db_options.port,
                                            database=self.temp_db_options.db,
                                            user=self.temp_db_options.user,
                                            passwd='',
                                            obj_id=f_name,
                                            obj_type=None,
                                            connection_id=None)
                    w_list.append((locator, version))
            import core.console_mode
            if self.temp_db_options.parameters == None:
                self.temp_db_options.parameters = ''
            
            if self.temp_configuration.check('workflowInfo'):
                workflow_info = self.temp_configuration.workflowInfo
            else:
                workflow_info = None
            extra_info = None
            if self.temp_configuration.check('spreadsheetDumpCells'):
                extra_info = \
                {'pathDumpCells': self.temp_configuration.spreadsheetDumpCells}
            if self.temp_configuration.check('spreadsheetDumpPDF'):
                if extra_info is None:
                    extra_info = {}
                extra_info['pdf'] = self.temp_configuration.spreadsheetDumpPDF
            errs = core.console_mode.run(w_list,
                                      self.temp_db_options.parameters,
                                      workflow_info, extra_info=extra_info)
            if len(errs) > 0:
                for err in errs:
                    print "*** Error in %s:%s:%s -- %s" % err
                return False
            return True
        else:
            debug.warning("no input vistrails provided")
            return True

    def setIcon(self):
        """ setIcon() -> None
        Setup Vistrail Icon
        """
        self.setWindowIcon(gui.theme.CurrentTheme.APPLICATION_ICON)
        
    def setupSplashScreen(self):
        """ setupSplashScreen() -> None
        Create the splash-screen at startup
        
        """
        if self.temp_configuration.check('showSplash'):
            splashPath = (system.vistrails_root_directory() +
                          "/gui/resources/images/vistrails_splash.png")
            pixmap = QtGui.QPixmap(splashPath)
            self.splashScreen = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            debug.DebugPrint.getInstance().register_splash(self)
            self.splashScreen.show()
            
    def splashMessage(self, msg):
        if hasattr(self, "splashScreen"):
            self.splashScreen.showMessage(msg,
                        QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft,
                        QtCore.Qt.white)

    def createWindows(self):
        """ createWindows() -> None
        Create and configure all GUI widgets including the builder
        
        """
        self.setupSplashScreen()
        if system.systemType in ['Darwin']:
            self.installEventFilter(self)

        # This is so that we don't import too many things before we
        # have to. Otherwise, requirements are checked too late.
        from gui.builder_window import QBuilderWindow

        self.builderWindow = QBuilderWindow()
        if not self.temp_configuration.showSpreadsheetOnly:
            # self.builderWindow.show()
            # self.setActiveWindow(self.builderWindow)
            pass

    def finishSession(self):
        if QtCore.QT_VERSION >= 0x40400:
            self.shared_memory.detach()
            if self.local_server:
                self.local_server.close()
        if system.systemType in ['Darwin']:
			self.removeEventFilter(self)
        VistrailsApplicationInterface.finishSession(self)
   
    def eventFilter(self, o, event):
        """eventFilter(obj,event)-> boolean
        This will filter all create events and will set on the WA_MacMetalStyle
        attribute of a QWidget. It will also filter the FileOpen events on a Mac
        
        """
        metalstyle = self.temp_configuration.check('useMacBrushedMetalStyle')
        if metalstyle:
            if QtCore.QT_VERSION < 0x40500:    
                create_event = QtCore.QEvent.Create
                mac_attribute = QtCore.Qt.WA_MacMetalStyle
            else:
                create_event = 15
                mac_attribute = QtCore.Qt.WA_MacBrushedMetal
            if(event.type() == create_event and 
               issubclass(type(o),QtGui.QWidget) and
               type(o) != QtGui.QSplashScreen):
                o.setAttribute(mac_attribute)
        if event.type() == QtCore.QEvent.FileOpen:
            self.input = [str(event.file())]
            self.process_interactive_input()
        return QtGui.QApplication.eventFilter(self,o,event)
    
    def is_running(self):
        return self._is_running

    def message_received(self):
        if QtCore.QT_VERSION >= 0x40400:
            local_socket = self.local_server.nextPendingConnection()
            if not local_socket.waitForReadyRead(self.timeout):
                print local_socket.errorString().toLatin1()
                return
            byte_array = local_socket.readAll()
            self.temp_db_options = None 
            self.parse_input_args_from_other_instance(str(byte_array))
            local_socket.disconnectFromServer()
    
    def send_message(self, message):
        if QtCore.QT_VERSION >= 0x40400:
            if not self._is_running:
                return False
            local_socket = QtNetwork.QLocalSocket(self)
            local_socket.connectToServer(self._unique_key)
            if not local_socket.waitForConnected(self.timeout):
                print "Failed: ", local_socket.errorString().toLatin1()
                return False
            self.shared_memory.lock()
            local_socket.write(message)
            self.shared_memory.unlock()
            if not local_socket.waitForBytesWritten(self.timeout):
                print "Writing failed: " 
                print local_socket.errorString().toLatin1()
                return False
            local_socket.disconnectFromServer()
            return True
    
    def parse_input_args_from_other_instance(self, msg):
        import re
        options_re = re.compile(r"(\[('([^'])*', ?)*'([^']*)'\])|(\[\s?\])")
        if options_re.match(msg):
            #it's safe to eval as a list
            args = eval(msg)
            if type(args) == type([]):
                command_line.CommandLineParser.init_options(args)
                self.readOptions()
                self.process_interactive_input()
                if not self.temp_configuration.showSpreadsheetOnly:
                    # in some systems (Linux and Tiger) we need to make both calls
                    # so builderWindow is activated
                    self.builderWindow.raise_()
                    self.builderWindow.activateWindow()
            else:
                print "Invalid string: %s"%msg
        else:
            print "Invalid input: %s"%msg
        
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
    if VistrailsApplication.is_running():
        print "Found another instance of VisTrails running"
        msg = str(sys.argv[1:])
        print "Sending parameters to main instance ", msg
        VistrailsApplication.send_message(msg)
        sys.exit(0)
    try:
        core.requirements.check_all_vistrails_requirements()
    except core.requirements.MissingRequirement, e:
        msg = ("VisTrails requires %s to properly run.\n" %
               e.requirement)
        QtGui.QMessageBox.critical(None, "Missing requirement",
                                   msg)
        sys.exit(1)
    x = VistrailsApplication.init(optionsDict)
    if x == True:
        return 0
    else:
        return 1

VistrailsApplication = None

def stop_application():
    """Stop and finalize the application singleton."""
    global VistrailsApplication
    VistrailsApplication.finishSession()
    VistrailsApplication.save_configuration()
    VistrailsApplication.destroy()
    VistrailsApplication.deleteLater()

