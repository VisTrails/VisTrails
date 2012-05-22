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


from PyQt4 import QtGui, QtCore, QtNetwork
from core.application import VistrailsApplicationInterface, \
    get_vistrails_application, set_vistrails_application
from core import command_line
from core import debug
from core import system
from core.db.locator import FileLocator, DBLocator
import core.requirements
from db import VistrailsDBException
import db.services.io
from gui import qt
import gui.theme
import os.path
import getpass
import sys

################################################################################

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

        self.builderWindow = None
        # local notifications
        self.window_notifications = {}
        self.view_notifications = {}

        if QtCore.QT_VERSION < 0x40200: # 0x40200 = 4.2.0
            raise core.requirements.MissingRequirement("Qt version >= 4.2")
        self._is_running = False
        self.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus)
        # code for single instance of the application
        # based on the C++ solution availabe at
        # http://wiki.qtcentre.org/index.php?title=SingleApplication
        if QtCore.QT_VERSION >= 0x40400:
            self.timeout = 10000
            self._unique_key = os.path.join(system.home_directory(),
                                            "vistrails-single-instance-check-%s"%getpass.getuser())
            self.shared_memory = QtCore.QSharedMemory(self._unique_key)
            self.local_server = None
            if self.shared_memory.attach():
                self._is_running = True
            else:
                self._is_running = False
                if not self.shared_memory.create(1):
                    debug.critical("Unable to create single instance "
                                   "of vistrails application")
                    return
                self.local_server = QtNetwork.QLocalServer(self)
                self.connect(self.local_server, QtCore.SIGNAL("newConnection()"),
                             self.message_received)
                if self.local_server.listen(self._unique_key):
                    debug.log("Listening on %s"%self.local_server.fullServerName())
                else:
                    debug.warning("Server is not listening. This means it will not accept \
parameters from other instances")
                                  
        qt.allowQObjects()

    def init(self, optionsDict=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        gui.theme.initializeCurrentTheme()
        # DAK this is handled by finalize_vistrails in core.application now
        # self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
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

    def is_running_gui(self):
        return True

    def create_notification(self, notification_id, window=None, view=None):
        if view is not None:
            if view not in self.view_notifications:
                self.view_notifications[view] = {}
            notifications = self.view_notifications[view]
        elif window is not None:
            if window not in self.window_notifications:
                self.window_notifications[window] = {}
            notifications = self.window_notifications[window]
        else:
            notifications = self.notifications
        if notification_id not in notifications:
            notifications[notification_id] = set()
        # else:
        #     print "already added notification", notification_id

    def register_notification(self, notification_id, method, window=None,
                              view=None):
        if view is not None:
            if view not in self.view_notifications:
                self.view_notifications[view] = {}
            notifications = self.view_notifications[view]
            #print '>>> LOCAL adding notification', notification_id, view, method
            #print id(notifications), notifications
            #for n, o in notifications.iteritems():
            #    print "    ", n , "(%s)"%len(o)
            #    for m in o:
            #        print "        ", m
        elif window is not None:
            if window not in self.window_notifications:
                self.window_notifications[window] = {}
            notifications = self.window_notifications[window]
        else:
            notifications = self.notifications     
            #print '>>> GLOBAL adding notification', notification_id, method  
            #print id(notifications), notifications
        if notification_id not in notifications:
            self.create_notification(notification_id, window, view)
        notifications[notification_id].add(method)

    def unregister_notification(self, notification_id, method, window=None,
                                view=None):
        if view is not None:
            if view in self.view_notifications:
                notifications = self.view_notifications[view]
            else:
                notifications = {}
                #print '>>> LOCAL remove notification', notification_id, view
            
            #print id(notifications), notifications
#            for n, o in notifications.iteritems():
#                print "    ", n , "(%s)"%len(o)
#                for m in o:
#                    print "        ", m
        elif window is not None:
            if window in self.window_notifications:
                notifications = self.window_notifications[window]
            else:
                notifications = {}
        else:
            notifications = self.notifications    
            #print '>>> GLOBAL remove notification', notification_id, method   
            #print id(notifications), notifications           
        if notification_id in notifications:
            notifications[notification_id].remove(method)

    def send_notification(self, notification_id, *args):
        # do global notifications
        if notification_id in self.notifications:
            # print 'global notification ', notification_id
            for m in self.notifications[notification_id]:
                try:
                    #print "  m: ", m
                    m(*args)
                except Exception, e:
                    import traceback
                    traceback.print_exc()
        notifications = {}

        current_window = self.builderWindow

        # do window notifications
        if current_window in self.window_notifications:
            notifications = self.window_notifications[current_window]
            # print 'window notification', notification_id, current_window

        if notification_id in notifications:
            # print "found notification:", notification_id
            for m in notifications[notification_id]:
                try:
                    # print "  m: ", m
                    m(*args)
                except Exception, e:
                    import traceback
                    traceback.print_exc()
        # else:
        #     print "no notification...", notifications.keys()

        if current_window is not None:
            current_view = current_window.current_view
        else:
            current_view = None
        # do local notifications
        if current_view in self.view_notifications:
            notifications = self.view_notifications[current_view]
            # print 'local notification ', notification_id, current_view
                
        if notification_id in notifications:
            for m in notifications[notification_id]:
                try:
                    #print "  m: ", m
                    m(*args)
                except Exception, e:
                    import traceback
                    traceback.print_exc()

    def showBuilderWindow(self):
        # in some systems (Linux and Tiger) we need to make both calls
        # so builderWindow is activated
        self.setActiveWindow(self.builderWindow)
        self.builderWindow.activateWindow()
        self.builderWindow.show()
        self.builderWindow.raise_()
    
    def interactiveMode(self):
        """ interactiveMode() -> None
        Instantiate the GUI for interactive mode
        
        """     
        if self.temp_configuration.check('showSplash'):
            self.splashScreen.finish(self.builderWindow)
        # self.builderWindow.modulePalette.updateFromModuleRegistry()
        # self.builderWindow.modulePalette.connect_registry_signals()
        self.builderWindow.link_registry()
        
        self.process_interactive_input()
        if not self.temp_configuration.showSpreadsheetOnly:
            self.showBuilderWindow()
        else:
            self.builderWindow.hide()
        self.builderWindow.create_first_vistrail()

    def noninteractiveMode(self):
        """ noninteractiveMode() -> None
        Run the console in non-interactive mode
        
        """
        usedb = False
        if self.temp_db_options.host:
            usedb = True
            passwd = ''
        if usedb and self.temp_db_options.user:
            if self.temp_db_options.user:
                db_config = dict((x, self.temp_db_options.__dict__[x])
                                 for x in ['host', 'port', 
                                           'db', 'user'])
                try:
                    db.services.io.test_db_connection(db_config)
                except VistrailsDBException:
                    passwd = \
                        getpass.getpass("Connecting to %s:%s. Password for user '%s':" % (
                                        self.temp_db_options.host,
                                        self.temp_db_options.db,
                                        self.temp_db_options.user))
                    db_config['passwd'] = passwd
                    try:
                        db.services.io.test_db_connection(db_config)
                    except VistrailsDBException:
                        debug.critical("Cannot login to database")
                        return False
    
        if self.input:
            w_list = []
            vt_list = []
            for filename in self.input:
                f_name, version = self._parse_vtinfo(filename, not usedb)
                if not usedb:
                    locator = FileLocator(os.path.abspath(f_name))
                else:
                    locator = DBLocator(host=self.temp_db_options.host,
                                        port=self.temp_db_options.port,
                                        database=self.temp_db_options.db,
                                        user=self.temp_db_options.user,
                                        passwd=passwd,
                                        obj_id=f_name,
                                        obj_type=None,
                                        connection_id=None)
                    if not locator.is_valid():
                        #here there is a problem: as we allow execution from 
                        #command line with VisTrails already running, we need
                        #to update from the gui
                        if hasattr(self, 'builderWindow'):
                            ok = locator.update_from_gui(self.builderWindow)
                        else:
                            ok = locator.update_from_console()
                        if not ok:
                            debug.critical("Cannot login to database")
                if f_name and version:
                    w_list.append((locator, version))
                vt_list.append(locator)
            import core.console_mode
            if self.temp_db_options.parameters == None:
                self.temp_db_options.parameters = ''
            
            if self.temp_configuration.check('workflowGraph'):
                workflow_graph = self.temp_configuration.workflowGraph
                results = core.console_mode.get_wf_graph(w_list, workflow_graph,
                                     self.temp_configuration.spreadsheetDumpPDF)
                failed = True
                for r in results:
                    failed = False
                    if r[0] == False:
                        debug.critical("*** Error in get_wf_graph: %s" % r[1])
                        failed = True
                return not failed
            
            if self.temp_configuration.check('evolutionGraph'):
                evolution_graph = self.temp_configuration.evolutionGraph
                results = core.console_mode.get_vt_graph(vt_list, evolution_graph,
                                     self.temp_configuration.spreadsheetDumpPDF)
                
                failed = True
                for r in results:
                    failed = False
                    if r[0] == False:
                        debug.critical("*** Error in get_vt_graph: %s" % r[1])
                        failed = True
                return not failed
                
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
                                      workflow_info, update_vistrail=True,
                                      extra_info=extra_info)
            if len(errs) > 0:
                for err in errs:
                    debug.critical("*** Error in %s:%s:%s -- %s" % err)
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
            self.splashScreen.setFont(gui.theme.CurrentTheme.SPLASH_SCREEN_FONT)
            debug.DebugPrint.getInstance().register_splash(self)
            self.splashScreen.show()
            
    def splashMessage(self, msg):
        if hasattr(self, "splashScreen"):
            self.splashScreen.showMessage(msg,
                        QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft,
                        QtCore.Qt.white)
            self.processEvents()

    def createWindows(self):
        """ createWindows() -> None
        Create and configure all GUI widgets including the builder
        
        """
        self.setupSplashScreen()
        if system.systemType in ['Darwin']:
            self.installEventFilter(self)

        # This is so that we don't import too many things before we
        # have to. Otherwise, requirements are checked too late.
        # from gui.builder_window import QBuilderWindow
        from gui.vistrails_window import QVistrailsWindow

        # self.builderWindow = QBuilderWindow()
        self.builderWindow = QVistrailsWindow()
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
               type(o) != QtGui.QSplashScreen and 
               not (o.windowFlags() & QtCore.Qt.Popup)):
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
                debug.critical("Read error: %s" %
                               local_socket.errorString().toLatin1())
                return
            byte_array = local_socket.readAll()
            self.temp_db_options = None
            self.temp_configuration.workflowGraph = None
            self.temp_configuration.workflowInfo = None
            self.temp_configuration.evolutionGraph = None
            self.temp_configuration.spreadsheetDumpPDF = False
            self.temp_configuration.spreadsheetDumpCells = None
            self.temp_configuration.executeWorkflows = False
            self.temp_configuration.interactiveMode = True
            
            self.parse_input_args_from_other_instance(str(byte_array))
            self.shared_memory.lock()
            local_socket.write("1")
            self.shared_memory.unlock()
            if not local_socket.waitForBytesWritten(self.timeout):
                debug.debug("Writing failed: %s" %
                            local_socket.errorString().toLatin1())
                return
            local_socket.disconnectFromServer()
    
    def send_message(self, message):
        if QtCore.QT_VERSION >= 0x40400:
            if not self._is_running:
                return False
            local_socket = QtNetwork.QLocalSocket(self)
            local_socket.connectToServer(self._unique_key)
            if not local_socket.waitForConnected(self.timeout):
                debug.critical("Connection failed: %s" %
                               local_socket.errorString().toLatin1())
                return False
            self.shared_memory.lock()
            local_socket.write(message)
            self.shared_memory.unlock()
            if not local_socket.waitForBytesWritten(self.timeout):
                debug.critical("Writing failed: %s" %
                               local_socket.errorString().toLatin1())
                return False
            if not local_socket.waitForReadyRead(self.timeout):
                debug.critical("Read error: %s" %
                               local_socket.errorString().toLatin1())
                return
            byte_array = local_socket.readAll()
            debug.log("Other instance processed input (%s)"%str(byte_array))
            local_socket.disconnectFromServer()
            return True
    
    def parse_input_args_from_other_instance(self, msg):
        import re
        options_re = re.compile(r"(\[('([^'])*', ?)*'([^']*)'\])|(\[\s?\])")
        if options_re.match(msg):
            #it's safe to eval as a list
            args = eval(msg)
            if type(args) == type([]):
                #print "args from another instance %s"%args
                command_line.CommandLineParser.init_options(args)
                self.readOptions()
                interactive = self.temp_configuration.check('interactiveMode')
                if interactive:
                    self.process_interactive_input()
                    if not self.temp_configuration.showSpreadsheetOnly:
                        # in some systems (Linux and Tiger) we need to make both calls
                        # so builderWindow is activated
                        self.builderWindow.raise_()
                        self.builderWindow.activateWindow()
                else:
                    self.noninteractiveMode()
            else:
                debug.critical("Invalid string: %s" % msg)
        else:
            debug.critical("Invalid input: %s" % msg)
        
# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_application(optionsDict=None):
    """Initializes the application singleton."""
    VistrailsApplication = get_vistrails_application()
    if VistrailsApplication:
        debug.critical("Application already started.")
        return
    VistrailsApplication = VistrailsApplicationSingleton()
    set_vistrails_application(VistrailsApplication)
    if VistrailsApplication.is_running():
        debug.critical("Found another instance of VisTrails running")
        msg = str(sys.argv[1:])
        debug.critical("Will send parameters to main instance %s" % msg)
        res = VistrailsApplication.send_message(msg)
        if res:
            sys.exit(0)
        else:
            sys.exit(1)
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
    VistrailsApplication.destroy()
    VistrailsApplication.deleteLater()

