###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
import os
import sys
import traceback
import weakref
import warnings

from vistrails.core import debug
from vistrails.core import keychain
from vistrails.core import system
from vistrails.core.collection import Collection
import vistrails.core.configuration
from vistrails.core.configuration import ConfigurationObject
from vistrails.core.db.locator import BaseLocator, FileLocator, DBLocator, \
    UntitledLocator
import vistrails.core.db.io
import vistrails.core.interpreter.cached
import vistrails.core.interpreter.default
from vistrails.core.modules.module_registry import ModuleRegistry
from vistrails.core.packagemanager import PackageManager
from vistrails.core.startup import VistrailsStartup
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core.utils import InstanceObject, VistrailsWarning
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.core.vistrail.controller import VistrailController
from vistrails.db import VistrailsDBException

VistrailsApplication = None
APP_SUCCESS = 0 # Success exit code
APP_FAIL = 1 # fialed exit code
APP_DONE = 2 # Success but shut down prematurely (other instance called)

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

def init(options_dict={}, args=[]):
    app = VistrailsCoreApplication()
    set_vistrails_application(app)
    app.init(options_dict=options_dict, args=args)
    return app

class VistrailsApplicationInterface(object):
    def __init__(self):
        self._initialized = False
        self.notifications = {}

    def printVersion(self):
        """ printVersion() -> None
        Print version of Vistrail and exit
        
        """
        print system.about_string()
        sys.exit(0)

    def read_options(self, args=None):
        """ read_options() -> None
        Read arguments from the command line
        
        """
        if args is None:
            args = sys.argv[1:]

        parser = vistrails.core.configuration.build_default_parser()
        command_line_config = vistrails.core.configuration.ConfigurationObject()
        try:
            parser.parse_args(args, namespace=command_line_config)
        except SystemError:
            print "GOT SYSTEM ERROR!"
            traceback.print_exc()

        self.input = command_line_config.vistrails
        if len(self.input) == 0:
            self.input = None

        return command_line_config

    # startup is going to manage configurations
    def _get_configuration(self):
        return self.startup.configuration
    configuration = property(_get_configuration)

    def _get_temp_configuration(self):
        return self.startup.temp_configuration
    temp_configuration = property(_get_temp_configuration)

    def create_registry(self, registry_filename=None):
        if registry_filename is not None:
            registry = vistrails.core.db.io.open_registry(registry_filename)
            registry.set_global()
        else:
            registry = ModuleRegistry()
            registry.set_global()
        return registry

    def init(self, options_dict=None, args=[]):
        """ VistrailsApplicationSingleton(options_dict: dict, args: list)
                                          -> VistrailsApplicationSingleton
        Create the application with a dict of settings
        
        """
        warnings.simplefilter('once', VistrailsWarning, append=True)

        # options_dict overrides startup configuration
        if options_dict is not None:
            options_config = ConfigurationObject(**options_dict)
        else:
            options_config = None

        # command line options override both
        command_line_config = self.read_options(args)

        # startup takes care of all configurations
        self.startup = VistrailsStartup(options_config, command_line_config)

        self.keyChain = keychain.KeyChain()
        vistrails.core.interpreter.default.connect_to_configuration(
            self.temp_configuration)

        # now we want to open vistrails and point to a specific version

        self.check_all_requirements()

        if self.temp_configuration.check('staticRegistry'):
            self.registry = \
                self.create_registry(self.temp_configuration.staticRegistry)
        else:
            self.registry = self.create_registry(None)

        self.package_manager = PackageManager(self.registry,
                                              self.startup)

    def check_all_requirements(self):
        # check scipy
        vistrails.core.requirements.require_python_module('scipy', {
                'linux-debian': 'python-scipy',
                'linux-ubuntu': 'python-scipy',
                'linux-fedora': 'scipy',
                'pip': 'scipy'})

    def destroy(self):
        """ destroy() -> None
        Finalize all packages to, such as, get rid of temp files
        
        """
        if hasattr(self, 'package_manager'):
            self.package_manager.finalize_packages()
        Collection.clearInstance()
        ThumbnailCache.clearInstance()

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
        if self.temp_configuration.check('host'):
            usedb = True
        if self.input:
            #check if versions are embedded in the filename
            for filename in self.input:
                f_name, version = self._parse_vtinfo(filename, not usedb)
                locator = None
                if f_name is None:
                    debug.critical("Could not find file %s" % filename)
                    return False
                elif not usedb:
                    locator = FileLocator(os.path.abspath(f_name))
                    #_vnode and _vtag will be set when a .vtl file is open and
                    # it can be either a FileLocator or a DBLocator
                    
                elif usedb:
                    locator = DBLocator(
                           host=self.temp_configuration.check('host'),
                           port=self.temp_configuration.check('port') or 3306,
                           database=self.temp_configuration.check('db'),
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
                    execute = self.temp_configuration.execute
                    mashuptrail = None
                    mashupversion = None
                    if hasattr(locator, '_mshptrail'):
                        mashuptrail = locator._mshptrail
                    if hasattr(locator, '_mshpversion'):
                        mashupversion = locator._mshpversion
                        if mashupversion:
                            execute = True
                    if self.temp_configuration.showWindow:
                        self.showBuilderWindow()
                    self.builderWindow.open_vistrail_without_prompt(locator,
                                                                    version, execute,
                                                                    mashuptrail=mashuptrail, 
                                                                    mashupVersion=mashupversion)

                    if self.temp_configuration.check('parameterExploration'):
                        self.builderWindow.executeParameterExploration(pe)
                
        return True

    def finishSession(self):
        vistrails.core.interpreter.cached.CachedInterpreter.cleanup()
        
    def save_configuration(self):
        """ save_configuration() -> None
        Save the current vistrail configuration to the startup.xml file.
        This is required to capture changes to the configuration that we 
        make programmatically during the session, ie., browsed directories or
        window sizes.

        """
        self.startup.save_persisted_startup()

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
                except Exception:
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
            except Exception, e:
                debug.unexpected_exception(e)
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
                    return controller
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
            except VistrailsDBException:
                debug.critical("Exception from the database",
                               traceback.format_exc())
                return None

        version = self.convert_version(version)
        if version is None:
            controller.select_latest_version()
            version = controller.current_version
        self.select_version(version)
        return controller

    def open_workflow(self, locator):
        if isinstance(locator, basestring):
            locator = BaseLocator.from_url(locator)

        new_locator = UntitledLocator()
        controller = self.open_vistrail(new_locator)
        try:
            if locator is None:
                return False
            workflow = locator.load(Pipeline)
            action_list = []
            for module in workflow.module_list:
                action_list.append(('add', module))
            for connection in workflow.connection_list:
                action_list.append(('add', connection))
            action = vistrails.core.db.action.create_action(action_list)
            controller.add_new_action(action)
            controller.perform_action(action)
            controller.vistrail.set_tag(action.id, "Imported workflow")
            controller.change_selected_version(action.id)
        except VistrailsDBException:
            debug.critical("Exception from the database",
                           traceback.format_exc())
            return None

        controller.select_latest_version()
        controller.set_changed(True)
        return controller

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

        controller.flush_delayed_actions()
        try:
            controller.write_vistrail(locator, export=export)
        except Exception, e:
            debug.unexpected_exception(e)
            debug.critical("Failed to save vistrail", traceback.format_exc())
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
        
        controller.close_vistrail(locator)
        controller.cleanup()
        self.remove_vistrail(locator)

class VistrailsCoreApplication(VistrailsApplicationInterface):
    def __init__(self):
        VistrailsApplicationInterface.__init__(self)
        self._controllers = {}
        self._cur_controller = None

    def init(self, options_dict=None, args=[]):
        VistrailsApplicationInterface.init(self, options_dict=options_dict, 
                                           args=args)
        self.package_manager.initialize_packages(
                report_missing_dependencies=not self.startup.first_run)

    def is_running_gui(self):
        return False

    def get_current_controller(self):
        return self._cur_controller
    get_controller = get_current_controller

    def add_vistrail(self, vistrail, locator,
            abstraction_files=None,  thumbnail_files=None, mashups=None):
        objs = vistrail, locator, abstraction_files, thumbnail_files, mashups
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
