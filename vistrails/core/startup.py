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

"""Describes the start-up process of VisTrails"""
from vistrails.core import debug
from vistrails.core import system
from vistrails.core.configuration import ConfigurationObject
from vistrails.core.utils.uxml import named_elements, elements_filter, \
     eval_xml_value, enter_named_element
from vistrails.db.domain import DBStartup, DBStartupPackage
import copy
import vistrails.core.packagemanager
import vistrails.core.utils
import os.path
import shutil
import sys
import tempfile
import vistrails.core.configuration
import xml.dom.minidom

################################################################################

class StartupPackage(DBStartupPackage):
    @staticmethod
    def convert(_pkg):
        _pkg.__class__ = StartupPackage
        if _pkg.configuration is not None:
            ConfigurationObject.convert(_pkg.configuration)

    configuration = DBStartupPackage.db_configuration
    name = DBStartupPackage.db_name

class PersistedStartup(DBStartup):
    @staticmethod
    def convert(_startup):
        _startup.__class__ = PersistedStartup
        ConfigurationObject.convert(_startup.configuration)
        # FIXME need to translate package settings
        for _pkg in _startup.enabled_packages:
            StartupPackage.convert(_pkg)
        for _pkg in _startup.disabled_packages:
            StartupPackage.convert(_pkg)
        
    configuration = DBStartup.db_configuration
    def _get_enabled_packages(self):
        return self.db_enabled_packages.db_packages
    enabled_packages = property(_get_enabled_packages)
    def _get_disabled_packages(self):
        return self.db_disabled_packages.db_packages
    disabled_packages = property(_get_disabled_packages)
    version = DBStartup.db_version

class VistrailsStartup(object):
    """
    VistrailsStartup is the class that initializes VisTrails based on
    a configuration. Both application mode (interactive and
    non-interactive) and import mode of VisTrails use this start up
    process to install packages and run .vistrails file. The purpose
    of this class is to separate the initialization process with Qt
    Application
    
    """

    DIRECTORIES = [('userPackageDirectory', 'userpackages', True),
                   ('abstractionsDirectory', 'subworkflows', False),
                   ('thumbs.cacheDirectory', 'thumbs', False)]

    def __init__(self, config=None, tempconfig=None, dot_vistrails=None):
        """VistrailsStartup(config, tempconfig: ConfigurationObject,
                            dot_vistrails: str) -> None

        Setup the configuration. config is the persistent
        configuration and tempconfig is the current
        configuration. dot_vistrals indicates the file we will use to
        load and save configuration options; if it is None, options
        will not be loaded or saved for the session.

        """
        assert (config is None or
                isinstance(config, vistrails.core.configuration.ConfigurationObject))
        assert (tempconfig is None or
                isinstance(tempconfig, vistrails.core.configuration.ConfigurationObject))
        if config:
            self.configuration = config
        else:
            self.configuration = vistrails.core.configuration.default()
        if tempconfig:
            self.temp_configuration = tempconfig
        else:
            self.temp_configuration = copy.copy(self.configuration)
        
        # self.startupHooks = []

        self._dot_vistrails = dot_vistrails
        self._persisted_startup = None
        if self._dot_vistrails is not None:
            self.setup_base_dot_vistrails()
            self.load_configuration()
            self.configuration.dotVistrails = self._dot_vistrails
            self.temp_configuration.dotVistrails = self._dot_vistrails
            self.setup_dot_vistrails()
            self.load_packages()

        #     # This needs to be here because we want to log all initialization
        #     # steps
        #     self.setupLogFile()
        #     self._python_environment = self.runDotVistrails()
        #     self.load_configuration()

        #     #the problem is that maybe the logFile now points to a different place
        #     self.setupLogFile()

        #     self.setupDefaultFolders()
        #     self._do_load_packages = True

        # else:
        #     self._do_load_packages = False
        # #package_manager needs the persistent configuration
        # self._package_manager = vistrails.core.packagemanager.PackageManager(
        #     self.configuration)
            
        # self._package_dictionary = {}
        # # stores all packages that must be enabled on startup
        # self._needed_packages = []
        
    def get_startup_xml_fname(self):
        return os.path.join(self._dot_vistrails, 'startup.xml')

    def setup_base_dot_vistrails(self):
        self.create_dot_vistrails_if_necessary()
        self.create_startupxml_if_needed()

    def load_configuration(self):
        startup = self.get_persisted_startup()
        self.configuration.update(startup.configuration)
        self.temp_configuration.update(startup.configuration)

    def update_deep_configs(self, keys_str, value):
        self.configuration.set_deep_value(keys_str, value)
        self.temp_configuration.set_deep_value(keys_str, value)

    def setup_init_file(self, dir_name):
        name = os.path.join(dir_name, '__init__.py')
        try:
            f = open(name, 'w')
            f.write('pass\n')
            f.close()
        except:
            msg = ("""Failed to create file '%s'. This could indicate a
            rare combination of a race condition and a permissions problem.
            Please make sure it is writable.""" % name)
            debug.critical(msg)
            sys.exit(1)

    def resolve_dir_name(self, config_key, default_dir):
        dir_name = None
        is_default = False
        if self.temp_configuration.has_deep_value(config_key):
            dir_name = self.temp_configuration.get_deep_value(config_key)
        if dir_name is None:
            dir_name = os.path.join(self._dot_vistrails, default_dir)
            is_default = True
        return dir_name, is_default

    def create_directory(self, dir_name):
        if not os.path.isdir(dir_name):
            debug.warning('Will try to create directory "%s"' % dir_name)
            try:
                os.mkdir(dir_name)
                return True
            except e:
                msg = ("Failed to create directory: '%s'."
                       "This could be an indication of a permissions problem."
                       "Make sure directory '%s' in writable." %
                       (str(e), dir_name))
                debug.critical(msg)
                sys.exit(1)
        return False

    def setup_directory(self, config_key, default_dir, setup_init_file=False):
        dir_name, is_default = self.resolve_dir_name(config_key, default_dir)
        self.create_directory(dir_name)
        if is_default:
            self.update_deep_configs(config_key, dir_name)
        if setup_init_file:
            self.setup_init_file(dir_name)

    def setup_log_file(self):
        import vistrails.core.system
        version = vistrails.core.system.vistrails_version()
        version = version.replace(".", "_")
        
        # FIXME this is really log dir, not log file
        # we should really create a logs subdir in .vistrails
        is_default = False
        if not self.temp_configuration.check('logFile'):
            dir_name = self._dot_vistrails
            is_default = True
        else:
            dir_name = os.path.dirname(self.temp_configuration.logFile)
        self.create_directory(dir_name)
        log_fname = os.path.join(dir_name, 'vistrails_%s.log' % version)
        if is_default:
            self.configuration.logFile = log_fname
            self.temp_configuration.logFile = log_fname
        debug.DebugPrint.getInstance().set_logfile(log_fname)
            
    def load_packages(self):
        startup = self.get_persisted_startup()
        for pkg in startup.enabled_packages:
            print "Loading package:", pkg.name

            

        # def get_version():
        #     import vistrails.core.system
        #     version = vistrails.core.system.vistrails_version()
        #     return version.replace(".","_")
        # #To make sure we always save a log file name according to the
        # #current version, we will only consider the directory stored in
        # # logFile and append a name with the correct version encoded. 
        # if not self.temp_configuration.check('logFile'):
        #     s = os.path.join(self.temp_configuration.dotVistrails,
        #                      'vistrails_%s.log'%(get_version()))
        #     self.temp_configuration.logFile = s
        # else:
        #     dirname = os.path.dirname(self.temp_configuration.logFile)
        #     self.temp_configuration.logFile = os.path.join(dirname,
        #                                 'vistrails_%s.log'%(get_version()))
        # if not self.configuration.check('logFile'):
        #     # if this was not set before, it should point to the
        #     # value in temp_configuration
        #     s = os.path.join(self.temp_configuration.dotVistrails,
        #                      'vistrails_%s.log'%(get_version()))
        #     self.configuration.logFile = s
        # else:
        #     dirname = os.path.dirname(self.configuration.logFile)
        #     self.configuration.logFile = os.path.join(dirname,
        #                                 'vistrails_%s.log'%(get_version()))
        # if not os.path.lexists(self.temp_configuration.dotVistrails):
        #     self.create_default_directory()
        # debug.DebugPrint.getInstance().set_logfile(self.temp_configuration.logFile)
        
    def setup_dot_vistrails(self):
        self.setup_log_file()
        for args in self.DIRECTORIES:
            self.setup_directory(*args)

    def init(self):
        """ init() -> None        
        Initialize VisTrails with optionsDict. optionsDict can be
        another VisTrails Configuration object, e.g. ConfigurationObject
        
        """
        if self._do_load_packages:
            self.load_packages()
        if self._do_load_packages:
            # don't call this anymore since we do an add_package for it now
            # self.setupBaseModules()
            self.installPackages()
        self.runStartupHooks()

    def set_needed_packages(self, package_list):
        self._needed_packages = package_list

    ##########################################################################
    # startup.xml related

    def startup_dom(self):
        filename = os.path.join(self.temp_configuration.dotVistrails,'startup.xml')
        return xml.dom.minidom.parse(filename)

    def write_startup_dom(self, dom):
        filename = os.path.join(self.temp_configuration.dotVistrails,'startup.xml')
        f = open(filename, 'w')
        f.write(dom.toxml())
                
    # def load_configuration(self):
    #     """load_configuration() -> None
    #     Loads the appropriate configuration from .vistrails/startup.xml.
    #     This will overwrite both configuration and temp_configuration
        
    #     """
    #     dom = self.startup_dom()
    #     conf = enter_named_element(dom.documentElement, 'configuration')
    #     self.configuration.set_from_dom_node(conf)
    #     self.temp_configuration.set_from_dom_node(conf)
        
    # def load_packages(self):
    #     """load_packages() -> None

    #     Loads the appropriate packages from .vistrails/startup.xml.
    #     """
        
    #     for package_name in self._needed_packages:
    #         self._package_manager.add_package(package_name)

    #     def parse_package(node):
    #         is_value = (lambda node: node.nodeName in
    #                     set(['bool', 'str', 'int', 'float']))
    #         package_name = str(node.attributes['name'].value)
    #         # FIXME use more robust checks here!
    #         if package_name != 'basic_modules' and \
    #                 package_name != 'abstraction':
    #             self._package_manager.add_package(package_name)
    #     dom = self.startup_dom()
    #     doc = dom.documentElement
    #     packages_node = enter_named_element(doc, 'packages')
    #     for package_node in named_elements(packages_node, 'package'):
    #         parse_package(package_node)

    ##########################################################################

    def get_python_environment(self):
        """get_python_environment(): returns the python environment generated
by startup.py. This should only be called after init()."""
        return self._python_environment

    def create_dot_vistrails_if_necessary(self):
        if os.path.exists(self._dot_vistrails):
            if not os.path.isdir(self._dot_vistrails):
                raise ValueError('The .vistrails directory cannot be used or '
                                 'created because the specified path "%s" is '
                                 'a file not a directory.' % 
                                 self._dot_vistrails)
            else:
                return

        debug.log('Will try to create default directory')
        try:
            os.mkdir(self._dot_vistrails)
            debug.log('Succeeded!')
        except:
            debug.critical("""Failed to create initialization directory.
                    This could be an indication of a permissions problem.
                    Make sure parent directory of '%s' is writable."""
                    % self._dot_vistrails)
            raise

    def get_persisted_startup(self):
        if self._persisted_startup is None:
            fname = self.get_startup_xml_fname()
            self._persisted_startup = vistrails.core.db.io.load_startup(fname)
        return self._persisted_startup

    def create_startupxml_if_needed(self):
        needs_create = True
        fname = self.get_startup_xml_fname()
        if os.path.isfile(fname):
            try:
                startup = self.get_persisted_startup()
                print "GOT STARTUP!!"
                version_string_to_list = \
                                vistrails.core.utils.version_string_to_list
                version_list = version_string_to_list(startup.version)
                print "version_list:", version_list
                if version_list >= [0,1]:
                    needs_create = False
            except:
                print "GOT EXCEPTION!!"
                import traceback
                traceback.print_exc()
                # pass

        if needs_create:
            root_dir = system.vistrails_root_directory()
            origin = os.path.join(root_dir, 'core','resources',
                                  'default_vistrails_startup_xml')
            try:
                shutil.copyfile(origin, fname)
                debug.log('Succeeded!')
            except:
                debug.critical("""Failed to copy default configuration
                file to %s. This could be an indication of a
                permissions problem. Please make sure '%s' is writable."""
                               % (fname, self._dot_vistrails))
                raise

    def create_default_directory(self):
        if os.path.lexists(self.temp_configuration.dotVistrails):
            return

        debug.log('Will try to create default directory')
        try:
            os.mkdir(self.temp_configuration.dotVistrails)
            debug.log('Succeeded!')
        except:
            debug.critical("""Failed to create initialization directory.
                    This could be an indication of a permissions problem.
                    Make sure parent directory of '%s' is writable."""
                    % self.temp_configuration.dotVistrails)
            sys.exit(1)
                
    def runDotVistrails(self):
        """ runDotVistrails() -> None
        Setup to run user .vistrails file

        """        
        def addStartupHook(hook):
            """ addStartupHook(hook: function) -> None
            Add a hook for start-up after initialization
            
            """
            self.startupHooks.append(hook)

        def addPackage(packageName, *args, **keywords):
            """ addPackage(packageName: str, *args) -> None
            """
            self._package_manager.add_package(packageName)

        def create_user_packages_init(userpackagesname):
            try:
                name = os.path.join(userpackagesname, '__init__.py')
                f = open(name, 'w')
                f.write('pass\n')
                f.close()
            except:
                msg = ("""Failed to create file '%s'. This could indicate a
                rare combination of a race condition and a permissions problem.
                Please make sure it is writable.""" % name)
                debug.critical(msg)
                sys.exit(1)

        def create_user_packages_dir(userpackagesname=None):
            debug.warning('Will try to create userpackages directory')
            if userpackagesname is None:
                userpackagesname = os.path.join(self.temp_configuration.dotVistrails,
                                            'userpackages')
            if not os.path.isdir(userpackagesname):
                try:
                    os.mkdir(userpackagesname)
                    self.configuration.userPackageDirectory = userpackagesname
                    self.temp_configuration.userPackageDirectory = \
                        userpackagesname
                except:
                    msg = ("""Failed to create userpackages directory: '%s'.
                    This could be an indication of a permissions problem.
                    Make sure directory '%s' in writable.""" %
                           (userpackagesname,
                            self.configuration.dotVistrails))
                    debug.critical(msg)
                    sys.exit(1)
            create_user_packages_init(userpackagesname)
                
        def create_thumbnails_dir(thumbnails_dir=None):
            debug.log('Will try to create thumbnails directory')
            if thumbnails_dir is None:
                thumbnails_dir = os.path.join(self.temp_configuration.dotVistrails,
                                            'thumbs')

            if not os.path.isdir(thumbnails_dir):
                try:
                    os.mkdir(thumbnails_dir)
                    self.configuration.thumbs.cacheDirectory = thumbnails_dir
                    self.temp_configuration.thumbs.cacheDirectory = \
                        thumbnails_dir
                except:
                    msg = ("Failed to create thumbnails cache directory: '%s'.  "
                           "This could be an indication of a permissions "
                           "problem.  Make sure directory '%s' is writable." % \
                               (thumbnails_dir, 
                                self.configuration.dotVistrails))
                    debug.critical(msg)
                    sys.exit(1)   
                                
        def create_abstractions_dir(abstractions_dir=None):
            debug.log('Will try to create subworkflows directory')
            abstractions_dir = os.path.join(self.temp_configuration.dotVistrails,
                                            'subworkflows')

            if not os.path.isdir(abstractions_dir):
                try:
                    os.mkdir(abstractions_dir)
                    self.configuration.abstractionsDirectory = abstractions_dir
                    self.temp_configuration.abstractionsDirectory = \
                        abstractions_dir
                except:
                    msg = ("Failed to create subworkflows directory: '%s'.  "
                           "This could be an indication of a permissions "
                           "problem.  Make sure directory '%s' is writable." % \
                               (abstractions_dir, 
                                self.configuration.dotVistrails))
                    debug.critical(msg)
                    sys.exit(1)
#             try:
#                 root_dir = core.system.vistrails_root_directory()
#                 default_file = os.path.join(root_dir,'core','resources',
#                                             'abstractions_init')
#                 user_file = os.path.join(abstractions_dir, '__init__.py')
#                 print 'copying', default_file, '->', abstractions_dir
#                 shutil.copyfile(default_file, user_file)
#                 debug.log('Succeeded!')
#             except Exception, e:
#                 print e
#                 debug.critical("Failed to copy default file to abstractions "
#                                "package.  This could be an indication of a "
#                                "permissions problem. Make sure directory "
#                                "'%s' is writable" % abstractions_dir)
#                 sys.exit(1)

        def install_default_startup():
            debug.log('Will try to create default startup script')
            try:
                root_dir = system.vistrails_root_directory()
                default_file = os.path.join(root_dir,'core','resources',
                                            'default_vistrails_startup')
                user_file = os.path.join(self.temp_configuration.dotVistrails,
                                         'startup.py')
                shutil.copyfile(default_file,user_file)
                debug.log('Succeeded!')
            except:
                debug.critical("""Failed to copy default file %s.
                This could be an indication of a permissions problem.
                Make sure directory '%s' is writable"""
                % (user_file,self.temp_configuration.dotVistrails))
                sys.exit(1)

        def install_default_startupxml_if_needed():
            fname = self.get_startup_xml_fname()
            root_dir = system.vistrails_root_directory()
            origin = os.path.join(root_dir, 'core','resources',
                                  'default_vistrails_startup_xml')
            def skip():
                if os.path.isfile(fname):
                    try:
                        d = self.startup_dom()
                        v = str(d.getElementsByTagName('startup')[0].attributes['version'].value)
                        r = vistrails.core.utils.version_string_to_list(v)
                        return r >= [0, 1]
                    except:
                        return False
                else:
                    return False
            if skip():
                return
            try:
                shutil.copyfile(origin, fname)
                debug.log('Succeeded!')
            except:
                debug.critical("""Failed to copy default configuration
                file to %s. This could be an indication of a
                permissions problem. Please make sure '%s' is writable."""
                               % (fname,
                                  self.temp_configuration.dotVistrails))

        def execDotVistrails(tried_once=False):
            """ execDotVistrails() -> None
            Actually execute the Vistrail initialization
            
            """
            # if it is file, then must move old-style .vistrails to
            # directory.
            if os.path.isfile(self.temp_configuration.dotVistrails):
                debug.warning("Old-style initialization hooks. Will try to set things correctly.")
                (fd, name) = tempfile.mkstemp()
                os.close(fd)
                try:
                    shutil.copyfile(self.temp_configuration.dotVistrails, name)
                    try:
                        os.unlink(self.temp_configuration.dotVistrails)
                    except:
                        debug.critical("""Failed to remove old initialization file.
                        This could be an indication of a permissions problem.
                        Make sure file '%s' is writable."""
                        % self.temp_configuration.dotVistrails)
                        sys.exit(1)
                    self.create_default_directory()
                    try:
                        destiny = os.path.join(self.temp_configuration.dotVistrails,
                                               'startup.py')
                        shutil.copyfile(name, destiny)
                    except:
                        debug.critical("""Failed to copy old initialization file to
                        newly-created initialization directory. This must have been
                        a race condition. Please remove '%s' and
                        restart VisTrails."""
                        % self.temp_configuration.dotVistrails)
                        sys.exit(1)
                    debug.critical("Successful move!")
                finally:
                    try:
                        os.unlink(name)
                    except:
                        debug.warning("Failed to erase temporary file.")

            if os.path.isdir(self.temp_configuration.dotVistrails):
                if self.temp_configuration.check('userPackageDirectory'):
                    userpackages = self.temp_configuration.userPackageDirectory
                else:
                    userpackages = os.path.join(self.temp_configuration.dotVistrails,
                                            'userpackages')
                startup = os.path.join(self.temp_configuration.dotVistrails,
                                       'startup.py')
                if self.temp_configuration.check('abstractionsDirectory'):
                    abstractions = self.temp_configuration.abstractionsDirectory
                else:
                    abstractions = os.path.join(self.temp_configuration.dotVistrails,
                                            'subworkflows')
                if (self.temp_configuration.has('thumbs') and
                    self.temp_configuration.thumbs.check('cacheDirectory')):
                    thumbnails = self.temp_configuration.thumbs.cacheDirectory
                else:
                    thumbnails = os.path.join(self.temp_configuration.dotVistrails,
                                          'thumbs')
                if not os.path.isdir(userpackages):
                    create_user_packages_dir(userpackages)
                if not os.path.isfile(os.path.join(userpackages, 
                                                   '__init__.py')):
                    create_user_packages_init(userpackages)
                if not os.path.isdir(abstractions):
                    create_abstractions_dir(abstractions)
                if not os.path.isdir(thumbnails):
                    create_thumbnails_dir(thumbnails)
                try:
                    
                    dotVistrails = open(startup)
                    g = {}
                    localsDir = {'configuration': self.temp_configuration,
                                 'addStartupHook': addStartupHook,
                                 'addPackage': addPackage}
                    old_path = copy.copy(sys.path)
                    sys.path.append(self.temp_configuration.dotVistrails)
                    exec dotVistrails in localsDir
                    sys.path = old_path
                    del localsDir['addPackage']
                    del localsDir['addStartupHook']
                    return localsDir
                except IOError:
                    if tried_once:
                        debug.critical("""Still cannot find default file.
                        Something has gone wrong. Please make sure ~/.vistrails
                        exists, is writable, and ~/.vistrails/startup.py does
                        not exist.""")
                        sys.exit(1)
                    debug.critical('%s not found' % startup)
                    debug.critical('Will try to install default '
                                              'startup file')
                    install_default_startup()
                    install_default_startupxml_if_needed()
                    return execDotVistrails(True)
            elif not os.path.lexists(self.temp_configuration.dotVistrails):
                debug.log('%s not found' % self.temp_configuration.dotVistrails)
                self.create_default_directory()
                create_user_packages_dir()
                create_abstractions_dir()
                create_thumbnails_dir()
                install_default_startup()
                install_default_startupxml_if_needed()
                return execDotVistrails(True)

        #install_default_startupxml_if_needed()
        # Now execute the dot vistrails
        return execDotVistrails()

    def setupDefaultFolders(self):
        """ setupDefaultFolders() -> None        
        Give default values to folders when there are no values specified
        
        """
        if self.temp_configuration.has('rootDirectory'):
            system.set_vistrails_root_directory(self.temp_configuration.rootDirectory)
        if self.temp_configuration.has('dataDirectory'):
            system.set_vistrails_data_directory( \
                self.temp_configuration.dataDirectory)
        if self.temp_configuration.has('fileDirectory'):
            system.set_vistrails_file_directory( \
                self.temp_configuration.fileDirectory)
        if (self.temp_configuration.has('verbosenessLevel') and
            self.temp_configuration.verbosenessLevel != -1):
            verbose = self.temp_configuration.verbosenessLevel
            if verbose < 0:
                msg = ("""Don't know how to set verboseness level to %s - "
                       "setting to the lowest one I know of: 0""" % verbose)
                debug.critical(msg)
                verbose = 0
            if verbose > 2:
                msg = ("""Don't know how to set verboseness level to %s - "
                       "setting to the highest one I know of: 2""" % verbose)
                debug.critical(msg)
                verbose = 2
            dbg = debug.DebugPrint.getInstance()
            levels = [dbg.Critical, dbg.Warning, dbg.Log]
            dbg.set_message_level(levels[verbose])
            debug.log("Set verboseness level to %s" % verbose)
        
        #these checks may need to update the persistent configuration, so
        # we have to change both objects
        #userpackages directory
        if not self.temp_configuration.check('userPackageDirectory'):
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'userpackages')
            self.temp_configuration.userPackageDirectory = s
        if not self.configuration.check('userPackageDirectory'):
            s = os.path.join(self.configuration.dotVistrails,
                             'userpackages')
            self.configuration.userPackageDirectory = s
        #abstractions directory    
        if not self.temp_configuration.check('abstractionsDirectory') or \
                self.temp_configuration.abstractionsDirectory == \
                os.path.join(self.temp_configuration.userPackageDirectory, 
                             'abstractions'):
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'subworkflows')
            self.temp_configuration.abstractionsDirectory = s
        if not self.configuration.check('abstractionsDirectory') or \
                self.configuration.abstractionsDirectory == \
                os.path.join(self.configuration.userPackageDirectory, 
                             'abstractions'):
            s = os.path.join(self.configuration.dotVistrails,
                             'subworkflows')
            self.configuration.abstractionsDirectory = s
        #thumbnails directory    
        if self.temp_configuration.has('thumbs'):
            if not self.temp_configuration.thumbs.check('cacheDirectory'):
                s = os.path.join(self.temp_configuration.dotVistrails,'thumbs')
                self.temp_configuration.thumbs.cacheDirectory = s
        if self.configuration.has('thumbs'):
            if not self.configuration.thumbs.check('cacheDirectory'):
                s = os.path.join(self.configuration.dotVistrails, 'thumbs')
                self.configuration.thumbs.cacheDirectory = s
        
    def setupLogFile(self):
        def get_version():
            import vistrails.core.system
            version = vistrails.core.system.vistrails_version()
            return version.replace(".","_")
        #To make sure we always save a log file name according to the
        #current version, we will only consider the directory stored in
        # logFile and append a name with the correct version encoded. 
        if not self.temp_configuration.check('logFile'):
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'vistrails_%s.log'%(get_version()))
            self.temp_configuration.logFile = s
        else:
            dirname = os.path.dirname(self.temp_configuration.logFile)
            self.temp_configuration.logFile = os.path.join(dirname,
                                        'vistrails_%s.log'%(get_version()))
        if not self.configuration.check('logFile'):
            # if this was not set before, it should point to the
            # value in temp_configuration
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'vistrails_%s.log'%(get_version()))
            self.configuration.logFile = s
        else:
            dirname = os.path.dirname(self.configuration.logFile)
            self.configuration.logFile = os.path.join(dirname,
                                        'vistrails_%s.log'%(get_version()))
        if not os.path.lexists(self.temp_configuration.dotVistrails):
            self.create_default_directory()
        debug.DebugPrint.getInstance().set_logfile(self.temp_configuration.logFile)
        
    def setupBaseModules(self):
        """ setupBaseModules() -> None        
        Import basic modules for self-registration. The import here is
        on purpose, not a typo against the coding rule
        
        """
        import vistrails.core.modules.vistrails_module
        import vistrails.core.modules.basic_modules
        import vistrails.core.modules.sub_module

    def installPackages(self):
        """ installPackages() -> None
        Scheme through packages directory and initialize them all
        """
        # Imports standard packages directory
        self._package_manager.initialize_packages(self._package_dictionary)

        # Enable abstractions
        import vistrails.core.modules.abstraction
        abstraction_pkg = "abstraction"
        abstraction_dict = {abstraction_pkg: 'vistrails.core.modules.'}
        self._package_manager.initialize_abstraction_pkg(abstraction_dict)

    def runStartupHooks(self):
        """ runStartupHooks() -> None
        After initialization, need to run all start up hooks registered
        
        """
        for hook in self.startupHooks:
            try:
                hook()
            except Exception, e:
                debug.critical("Exception raised during hook: %s - %s" %
                             (e.__class__, e))

    def destroy(self):
        """ destroy() -> None
        Finalize all packages to, such as, get rid of temp files
        
        """
        self._package_manager.finalize_packages()

    def set_registry(self, registry_filename=None):
        if registry_filename is not None:
            self._do_load_packages = False
        self._package_manager.init_registry(registry_filename)
            

import unittest
import shutil
import stat
import tempfile

class TestStartup(unittest.TestCase):
    def check_structure(self, dir_name):
        self.assertTrue(os.path.isdir(dir_name))
        self.assertTrue(os.path.isfile(os.path.join(dir_name, 
                                                    'startup.xml')))
        for t in VistrailsStartup.DIRECTORIES:
            a_dir = os.path.join(dir_name, t[1])
            self.assertTrue(os.path.isdir(a_dir),
                            'Directory "%s" does not exist' % a_dir)
            if t[2]:
                self.assertTrue(os.path.isfile(os.path.join(a_dir, 
                                                            '__init__.py')))

        import vistrails.core.system
        version = vistrails.core.system.vistrails_version()
        version = version.replace(".", "_")
        self.assertTrue(os.path.isfile(os.path.join(dir_name, 
                                                "vistrails_%s.log" % version)))

    def test_simple_create(self):
        dir_name = tempfile.mkdtemp()
        try:
            startup = VistrailsStartup(None, None, dir_name)
            self.check_structure(dir_name)
        finally:
            shutil.rmtree(dir_name)

    def test_create_dir_create(self):
        outer_dir_name = tempfile.mkdtemp()
        dir_name = os.path.join(outer_dir_name, '.vistrails')
        try:
            startup = VistrailsStartup(None, None, dir_name)
            self.check_structure(dir_name)
        finally:
            shutil.rmtree(outer_dir_name)
        
    def test_config_override(self):
        dir_name = tempfile.mkdtemp()
        user_pkg_dir = tempfile.mkdtemp()
        abstractions_dir = tempfile.mkdtemp()
        thumbs_dir = tempfile.mkdtemp()
        config = vistrails.core.configuration.default()
        config.userPackageDirectory = user_pkg_dir
        config.abstractionsDirectory = abstractions_dir
        config.thumbs.cacheDirectory = thumbs_dir
        try:
            startup = VistrailsStartup(config, None, dir_name)
            self.assertTrue(os.path.isfile(os.path.join(dir_name, 
                                                        'startup.xml')))
            for t in VistrailsStartup.DIRECTORIES:
                a_dir = os.path.join(dir_name, t[1])
                self.assertFalse(os.path.isdir(a_dir),
                                'Directory "%s" exists' % a_dir)
        finally:
            shutil.rmtree(dir_name)
            shutil.rmtree(user_pkg_dir)
            shutil.rmtree(abstractions_dir)
            shutil.rmtree(thumbs_dir)
            
    def test_config_override_create(self):
        dir_name = tempfile.mkdtemp()
        outer_user_pkg_dir = tempfile.mkdtemp()
        user_pkg_dir = os.path.join(outer_user_pkg_dir, 'userpackages')
        outer_abstractions_dir = tempfile.mkdtemp()
        abstractions_dir = os.path.join(outer_abstractions_dir, 'subworkflows')
        outer_thumbs_dir = tempfile.mkdtemp()
        thumbs_dir = os.path.join(outer_thumbs_dir, 'thumbs')
        config = vistrails.core.configuration.default()
        config.userPackageDirectory = user_pkg_dir
        config.abstractionsDirectory = abstractions_dir
        config.thumbs.cacheDirectory = thumbs_dir
        try:
            startup = VistrailsStartup(config, None, dir_name)
            self.assertTrue(os.path.isfile(os.path.join(dir_name, 
                                                        'startup.xml')))
            for t in VistrailsStartup.DIRECTORIES:
                a_dir = os.path.join(dir_name, t[1])
                self.assertFalse(os.path.isdir(a_dir),
                                'Directory "%s" exists' % a_dir)
            self.assertTrue(os.path.isdir(user_pkg_dir))
            self.assertTrue(os.path.isdir(abstractions_dir))
            self.assertTrue(os.path.isdir(thumbs_dir))
        finally:
            shutil.rmtree(dir_name)
            shutil.rmtree(outer_user_pkg_dir)
            shutil.rmtree(outer_abstractions_dir)
            shutil.rmtree(outer_thumbs_dir)
    
    def test_default_startup_xml(self):
        dir_name = tempfile.mkdtemp()
        try:
            startup = VistrailsStartup(None, None, dir_name)
            p = startup.get_persisted_startup()
            self.assertTrue(p.configuration.nologger)
            self.assertTrue(startup.configuration.autosave)
            self.assertTrue(startup.temp_configuration.autosave)
        finally:
            shutil.rmtree(dir_name)

    def test_cannot_create(self):
        (fd, fname) = tempfile.mkstemp()
        try:
            with self.assertRaises(ValueError):
                startup = VistrailsStartup(None, None, fname)
        finally:
            os.unlink(fname)
        
    def test_permissions(self):
        dir_name = tempfile.mkdtemp()
        try:
            os.chmod(dir_name, stat.S_IRUSR)
            with self.assertRaises(IOError):
                startup = VistrailsStartup(None, None, dir_name)
        finally:
            os.chmod(dir_name, stat.S_IRWXU)
            shutil.rmtree(dir_name)
            
    def test_load_packages(self):
        from vistrails.core.system import default_dot_vistrails
        dir_name = default_dot_vistrails()
        print "== TESTING LOAD PACKAGES =="
        startup = VistrailsStartup(None, None, dir_name)
        
        
if __name__ == '__main__':
    unittest.main()
