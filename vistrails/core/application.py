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
import copy
import os.path
import sys
import weakref

from vistrails.core import command_line
from vistrails.core import debug
from vistrails.core import keychain
from vistrails.core import system
from vistrails.core.collection import Collection
import vistrails.core.configuration
from vistrails.core.db.locator import BaseLocator, FileLocator, DBLocator, \
    UntitledLocator
import vistrails.core.db.io
import vistrails.core.interpreter.cached
import vistrails.core.interpreter.default
import vistrails.core.startup
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core.utils import InstanceObject
from vistrails.core.utils.uxml import enter_named_element
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.core.vistrail.controller import VistrailController
from vistrails.db import VistrailsDBException

VistrailsApplication = None

def finalize_vistrails(app):
    vistrails.core.interpreter.cached.CachedInterpreter.cleanup()

def get_vistrails_application():
    global VistrailsApplication
    if VistrailsApplication is not None:
        return VistrailsApplication()
    return None

def set_vistrails_application(app):
    global VistrailsApplication
    VistrailsApplication = weakref.ref(app, finalize_vistrails)

def is_running_gui():
    app = get_vistrails_application()
    return app.is_running_gui()

def init(options_dict={}, args=None):
    app = VistrailsCoreApplication()
    set_vistrails_application(app)
    app.init(optionsDict=options_dict, args=args)
    return app

class VistrailsApplicationInterface(object):
    def __init__(self):
        self._initialized = False
        self.notifications = {}

    def setupOptions(self, args=None):
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
            help="dump files in pdf format (non-interactive mode only)")
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
        add("-F", "--fixedcells", action="store_true",
            default = None,
            help="Use a fixed spreadsheet cell size of 200*180")
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
        add("-P", "--parameterExploration", action="store_true",
            help="Execute Parameter Exploration")
        add("-G", "--workflowgraph", action="store",
            default = None,
            help=("Save workflow graph in specified directory without running "
                  "the workflow (only valid in console mode)."))
        add("-U", "--evolutiongraph", action="store",
            default = None,
            help=("Save evolution graph in specified directory without running "
                  "any workflow (only valid in console mode)."))
        add ("-g", "--noSingleInstance", action="store_true",
             help=("Run VisTrails without the single instance restriction."))
        
        if args != None:
            command_line.CommandLineParser.parse_options(args=args)
        else:
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
        if get('fixedcells') != None:
            self.temp_configuration.fixedSpreadsheetCells = str(get('fixedcells'))
        if get('noninteractive')!=None:
            self.temp_configuration.interactiveMode = \
                                                  not bool(get('noninteractive'))
            if get('workflowinfo') != None:
                self.temp_configuration.workflowInfo = str(get('workflowinfo'))
            if get('dumpcells') != None:
                self.temp_configuration.spreadsheetDumpCells = get('dumpcells')
            if get('pdf') != None:
                self.temp_configuration.spreadsheetDumpPDF = get('pdf')
            if get('workflowgraph') != None:
                self.temp_configuration.workflowGraph = str(get('workflowgraph'))
            if get('evolutiongraph') != None:
                self.temp_configuration.evolutionGraph = str(get('evolutiongraph'))
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
        if get('parameterExploration')!= None:
            self.temp_configuration.parameterExploration = \
                str(get('parameterExploration'))
        if get('detachHistoryView')!= None:
            self.temp_configuration.detachHistoryView = bool(get('detachHistoryView'))
        if get('noSingleInstance')!=None:
            self.temp_configuration.singleInstance = not bool(get('noSingleInstance'))
        self.input = command_line.CommandLineParser().positional_arguments()
    def init(self, optionsDict=None, args=None):
        """ VistrailsApplicationSingleton(optionDict: dict)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        # gui.theme.initializeCurrentTheme()
        # self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self.finishSession)
        
        # This is the persistent configuration
        # Setup configuration to default
        self.configuration = vistrails.core.configuration.default()
        
        self.keyChain = keychain.KeyChain()
        self.setupOptions(args)
        
        # self.temp_configuration is the configuration that will be updated 
        # with the command line and custom options dictionary. 
        # We have to do this because we don't want to make these settings 
        # persistent. This is the actual VisTrails current configuration
        self.temp_configuration = copy.copy(self.configuration)
        
        vistrails.core.interpreter.default.connect_to_configuration(self.temp_configuration)
        
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

        # the problem here is that if the user pointed to a new .vistrails
        # folder, the persistent configuration will always point to the 
        # default ~/.vistrails. So we will copy whatever it's on 
        # temp_configuration to the persistent one. In case the configuration
        # that is on disk is different, it will overwrite this one
        self.configuration.dotVistrails = self.temp_configuration.dotVistrails
        
        # During this initialization, VistrailsStartup will load the
        # configuration from disk and update both configurations
        self.vistrailsStartup = \
            vistrails.core.startup.VistrailsStartup(self.configuration,
                                          self.temp_configuration)

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
        pe = None
        usedb = False
        if self.temp_db_options.host:
            usedb = True
        if self.input:
            locator = None
            #check if versions are embedded in the filename
            for filename in self.input:
                f_name, version = self._parse_vtinfo(filename, not usedb)
                if f_name is None:
                    msg = "Could not find file %s" % filename
                    debug.critical(msg)
                elif not usedb:
                    locator = FileLocator(os.path.abspath(f_name))
                    #_vnode and _vtag will be set when a .vtl file is open and
                    # it can be either a FileLocator or a DBLocator
                    
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
                    if self.temp_configuration.check('parameterExploration'):
                        pe = version
                        version = None
                    else:
                        if hasattr(locator, '_vnode') and \
                                locator._vnode is not None:
                            version = locator._vnode
                        if hasattr(locator,'_vtag'):
                            # if a tag is set, it should be used instead of the
                            # version number
                            if locator._vtag != '':
                                version = locator._vtag
                    execute = self.temp_configuration.executeWorkflows
                    mashuptrail = None
                    mashupversion = None
                    if hasattr(locator, '_mshptrail'):
                        mashuptrail = locator._mshptrail
                    if hasattr(locator, '_mshpversion'):
                        mashupversion = locator._mshpversion
                    if not self.temp_configuration.showSpreadsheetOnly:
                        self.showBuilderWindow()
                    self.builderWindow.open_vistrail_without_prompt(locator,
                                                                    version, execute,
                                                                    mashuptrail=mashuptrail, 
                                                                    mashupVersion=mashupversion)

                    if self.temp_configuration.check('parameterExploration'):
                        self.builderWindow.executeParameterExploration(pe)
                
                if self.temp_configuration.reviewMode:
                    self.builderWindow.interactiveExportCurrentPipeline()


                
    def finishSession(self):
        vistrails.core.interpreter.cached.CachedInterpreter.cleanup()
        
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

    def create_notification(self, notification_id, *args, **kwargs):
        notifications = self.notifications
        if notification_id not in notifications:
            notifications[notification_id] = set()
        else:
            print "already added notification", notification_id

    def register_notification(self, notification_id, method, *args, **kwargs):
        notifications = self.notifications     
        #print '>>> GLOBAL adding notification', notification_id, method  
        #print id(notifications), notifications
        if notification_id not in notifications:
            self.create_notification(notification_id)
        notifications[notification_id].add(method)

    def unregister_notification(self, notification_id, method, *args, **kwargs):
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
       
    def showBuilderWindow(self):
        pass
 
    def add_vistrail(self, *objs):
        """add_vistrail creates and returns a new controller based on the
        information contained in objs.

        """
        raise NotImplementedError("Subclass must implement add_vistrail!")

    def ensure_vistrail(self, locator):
        """ensure_vistrail returns the controller matching the locator if the
        vistrail is already open, otherwise it returns None.

        """
        raise NotImplementedError("Subclass must implement ensure_vistrail")

    def select_version(self, version=None):
        """select_version changes the version of the currently open vistrail
        to the specified version.

        """
        raise NotImplementedError("Subclass must implement select_version")

    def get_current_controller(self):
        """get_current_controller returns the currently active controller, if
        one exists, otherwise None.

        """
        raise NotImplementedError("Subclass must implement "
                                  "get_current_controller")

    def update_locator(self, old_locator, new_locator):
        """update_locator updates the application state to ensure that any
        vistrails referenced by old_locator are now referenced by
        new_locator.

        """
        raise NotImplementedError("Subclass must implement update_locator")

    def convert_version(self, version):
        if isinstance(version, basestring):
            try:
                version = \
                    self.get_controller().vistrail.get_version_number(version)
            except:
                version = None
        return version

    def new_vistrail(self):
        return self.open_vistrail(None)

    def open_vistrail(self, locator=None, version=None, is_abstraction=False):
        if isinstance(locator, basestring):
            locator = BaseLocator.from_url(locator)
        elif locator is None:
            locator = UntitledLocator()

        controller = self.ensure_vistrail(locator)
        if controller is None:
            # vistrail is not already open
            try:
                loaded_objs = vistrails.core.db.io.load_vistrail(locator, False)
                controller = self.add_vistrail(loaded_objs[0], locator, 
                                               *loaded_objs[1:])
                if locator.is_untitled():
                    return True
                controller.is_abstraction = is_abstraction
                thumb_cache = ThumbnailCache.getInstance()
                controller.vistrail.thumbnails = controller.find_thumbnails(
                    tags_only=thumb_cache.conf.tagsOnly)
                controller.vistrail.abstractions = controller.find_abstractions(
                    controller.vistrail, True)
                controller.vistrail.mashups = controller._mashups
                collection = Collection.getInstance()
                url = locator.to_url()
                entity = collection.updateVistrail(url, controller.vistrail)
                # add to relevant workspace categories
                if not controller.is_abstraction:
                    collection.add_to_workspace(entity)
                collection.commit()
            except VistrailsDBException, e:
                import traceback
                debug.critical(str(e), traceback.format_exc())
                return None
            except Exception, e:
                # debug.critical('An error has occurred', str(e))
                #print "An error has occurred", str(e)
                raise

        version = self.convert_version(version)
        if version is None:
            controller.select_latest_version()
            version = controller.current_version
        self.select_version(version)
        return True
        
    def open_workflow(self, locator):
        if isinstance(locator, basestring):
            locator = BaseLocator.from_url(locator)

        vistrail = Vistrail()
        try:
            if locator is None:
                return False
            if locator is not None:
                workflow = locator.load(Pipeline)
                action_list = []
                for module in workflow.module_list:
                    action_list.append(('add', module))
                for connection in workflow.connection_list:
                    action_list.append(('add', connection))
                action = vistrails.core.db.action.create_action(action_list)
                vistrail.add_action(action, 0L)
                vistrail.update_id_scope()
                vistrail.addTag("Imported workflow", action.id)

                # FIXME might need different locator?                
                controller = self.add_vistrail(vistrail, locator)
        except VistrailsDBException, e:
            import traceback
            debug.critical(str(e), traceback.format_exc())
            return None
        except Exception, e:
            # debug.critical('An error has occurred', str(e))
            raise

        controller.select_latest_version()
        controller.set_changed(True)
        return True

    def save_vistrail(self, locator=None, controller=None, export=False):
        if controller is None:
            controller = self.get_current_controller()
            if controller is None:
                return False
        if locator is None and controller is not None:
            locator = controller.locator
        elif isinstance(locator, basestring):
            locator = BaseLocator.from_url(locator)

        if not locator:
            return False
        old_locator = controller.locator

        try:
            controller.write_vistrail(locator, export=export)
        except Exception, e:
            import traceback
            debug.critical('Failed to save vistrail: %s' % str(e),
                           traceback.format_exc())
            raise
        if export:
            return controller.locator

        self.update_locator(old_locator, controller.locator)
        # update collection
        try:
            thumb_cache = ThumbnailCache.getInstance()
            controller.vistrail.thumbnails = controller.find_thumbnails(
                tags_only=thumb_cache.conf.tagsOnly)
            controller.vistrail.abstractions = controller.find_abstractions(
                controller.vistrail, True)
            controller.vistrail.mashups = controller._mashups

            collection = Collection.getInstance()
            url = locator.to_url()
            entity = collection.updateVistrail(url, controller.vistrail)
            # add to relevant workspace categories
            collection.add_to_workspace(entity)
            collection.commit()
        except Exception, e:
            import traceback
            debug.critical('Failed to index vistrail', traceback.format_exc())
        return controller.locator

    def close_vistrail(self, locator=None, controller=None):
        if controller is None:
            controller = self.get_current_controller()
            if controller is None:
                return False
        if locator is None and controller is not None:
            locator = controller.locator
        elif isinstance(locator, basestring):
            locator = BaseLocator.from_url(locator)
        
        self.send_notification('controller_closed', controller)
        controller.close_vistrail(locator)
        controller.cleanup()
        self.remove_vistrail(locator)

class VistrailsCoreApplication(VistrailsApplicationInterface):
    def __init__(self):
        VistrailsApplicationInterface.__init__(self)
        self._controllers = {}
        self._cur_controller = None

    def init(self, optionsDict=None, args=None):
        VistrailsApplicationInterface.init(self, optionsDict=optionsDict, args=args)
        self.vistrailsStartup.init()

    def is_running_gui(self):
        return False

    def get_current_controller(self):
        return self._cur_controller
    get_controller = get_current_controller

    def add_vistrail(self, *objs):
        (vistrail, locator, abstraction_files, thumbnail_files, mashups) = objs
        controller = VistrailController(*objs)
        self._controllers[locator] = controller
        self._cur_controller = controller
        return self._cur_controller
        
    def remove_vistrail(self, locator=None):
        if locator is None and self._cur_controller is not None:
            locator = self._cur_controller.locator
        del self._controllers[locator]
        if len(self._controllers) > 0:
            self._cur_controller = self._controllers.itervalues().next()

    def ensure_vistrail(self, locator):
        if locator in self._controllers:
            self._cur_controller = self._controllers[locator]
            return self._cur_controller
        return None

    def update_locator(self, old_locator, new_locator):
        self._controllers[new_locator] = self._controllers[old_locator]
        del self._controllers[old_locator]

    def select_version(self, version):
        if self._cur_controller is not None:
            self._cur_controller.change_selected_version(version)
            return True
        return False
        
