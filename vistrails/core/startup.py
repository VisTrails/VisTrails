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
from vistrails.db.domain import DBStartup, DBStartupPackage, \
    DBEnabledPackages, DBDisabledPackages
import vistrails.db.services.io
import vistrails.core.packagemanager
from vistrails.core.system import get_elementtree_library
import vistrails.core.utils
from vistrails.core.utils import version_string_to_list

import copy
import os.path
import re
import shutil
import sys
import tempfile
import vistrails.core.configuration

ElementTree = get_elementtree_library()

################################################################################

class StartupPackage(DBStartupPackage):
    def __init__(self, *args, **kwargs):
        if 'prefix' in kwargs:
            self.prefix = kwargs['prefix']
            del kwargs['prefix']
        else:
            self.prefix = None
        DBStartupPackage.__init__(self, *args, **kwargs)

    @staticmethod
    def convert(_pkg):
        _pkg.__class__ = StartupPackage
        if _pkg.configuration is not None:
            ConfigurationObject.convert(_pkg.configuration)
        _pkg.prefix = None

    def __copy__(self):
        """ __copy__() -> StartupPackage - Returns a clone of itself """ 
        return StartupPackage.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBStartupPackage.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = StartupPackage
        cp.prefix = self.prefix
        return cp

    configuration = DBStartupPackage.db_configuration
    name = DBStartupPackage.db_name

class VistrailsStartup(DBStartup):
    """
    VistrailsStartup is the class that initializes VisTrails based on
    a configuration. Both application mode (interactive and
    non-interactive) and import mode of VisTrails use this start up
    process to install packages and run .vistrails file. The purpose
    of this class is to separate the initialization process with Qt
    Application
    
    """

    # !!! IMPORTANT: keep logDirectory first!
    DIRECTORIES = [('logDirectory', 'logs', False),
                   ('userPackageDirectory', 'userpackages', True),
                   ('subworkflowsDirectory', 'subworkflows', False),
                   ('thumbs.cacheDirectory', 'thumbs', False)]
    DOT_VISTRAILS_PREFIX = "$DOT_VISTRAILS"
    DOT_VISTRAILS_PREFIX_RE = re.compile("%s([%s/\\\\]|$)" % 
                                         (re.escape(DOT_VISTRAILS_PREFIX),
                                          os.path.sep))

    def __init__(self, options_config, command_line_config, 
                 use_dot_vistrails=True):
        """VistrailsStartup(dot_vistrails: str) -> None

        Setup VisTrails configuration and options. dot_vistrals
        indicates the file we will use to load and save configuration
        options; if it is None, options will not be loaded or saved
        for the session.

        """

        DBStartup.__init__(self)
        self.db_enabled_packages = DBEnabledPackages()
        self.db_disabled_packages = DBDisabledPackages()

        self._dot_vistrails = None

        # self._enabled_packages = {}
        # self._disabled_packages = {}

        self.configuration = vistrails.core.configuration.default()

        if use_dot_vistrails:
            if command_line_config is not None and \
               command_line_config.check('dotVistrails'):
                self._dot_vistrails = command_line_config.get('dotVistrails')
            elif options_config is not None and \
                 options_config.check('dotVistrails'):
                self._dot_vistrails = options_config.get('dotVistrails')
            else:
                self._dot_vistrails = self.configuration.get('dotVistrails')
            self.setup_base_dot_vistrails()

        self.load_and_update_configurations(options_config, 
                                            command_line_config)
        self.update_packages()
        self.setup_dot_vistrails()

    @staticmethod
    def convert(_startup):
        _startup.__class__ = VistrailsStartup
        ConfigurationObject.convert(_startup.configuration)
        for _pkg in _startup.db_enabled_packages.db_packages:
            StartupPackage.convert(_pkg)
        for _pkg in _startup.db_disabled_packages.db_packages:
            StartupPackage.convert(_pkg)

    ########################################################################
    # Properties

    configuration = DBStartup.db_configuration
    def _get_enabled_packages(self):
        return self.db_enabled_packages.db_packages_name_index
    enabled_packages = property(_get_enabled_packages)
    def _get_disabled_packages(self):
        return self.db_disabled_packages.db_packages_name_index
    disabled_packages = property(_get_disabled_packages)
    version = DBStartup.db_version

    def get_startup_xml_fname(self):
        return os.path.join(self._dot_vistrails, 'startup.xml')

    def setup_base_dot_vistrails(self):
        self.create_dot_vistrails_if_necessary()
        self.create_startupxml_if_needed()

    def load_and_update_configurations(self, options_config, 
                                       command_line_config):
        # load options from startup.xml
        self.load_persisted_startup()

        # check the dot_vistrails paths
        if self._dot_vistrails is not None:
            self.update_dir_paths()

        # set up temporary configuration with options and command-line
        self.temp_configuration = copy.copy(self.configuration)        
        if options_config is not None:
            self.temp_configuration.update(options_config)
        if command_line_config is not None:
            self.temp_configuration.update(command_line_config)

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

    def remove_prefix(self, dir_name, prefix):
        suffix = dir_name[len(prefix):]
        if suffix.startswith('/') or suffix.startswith(os.path.sep) or \
           suffix.startswith('\\'):
            return suffix[1:]
        return suffix
            
    def expand_vt_path(self, dir_name):
        m = self.DOT_VISTRAILS_PREFIX_RE.match(dir_name)
        if m:
            if self._dot_vistrails is None:
                return None
            else:
                # could be "$DOT_VISTRAILS" or "$DOT_VISTRAILS/userpackages"
                prefix_len = len(self.DOT_VISTRAILS_PREFIX) + len(m.groups()[0])
                if prefix_len < len(dir_name):
                    return os.path.join(self._dot_vistrails, 
                                        dir_name[prefix_len:])
                else:
                    return self._dot_vistrails
        return dir_name

    # this should be more generally available (e.g. core.utils)
    def resolve_dir_name(self, config_key, default_dir):
        dir_name = None
        is_default = False
        if self.temp_configuration.has_deep_value(config_key):
            dir_name = self.temp_configuration.get_deep_value(config_key)
        if dir_name is None:
            dir_name = os.path.join("$DOT_VISTRAILS", default_dir)
            is_default = True
        abs_dir_name = self.expand_vt_path(dir_name)
        return dir_name, abs_dir_name, is_default

    def update_dir_paths(self):
        persistent_dot_vistrails = self.configuration.dotVistrails
        for (config_key, _, _) in self.DIRECTORIES:
            if self.configuration.has_deep_value(config_key):
                dir_name = self.configuration.get_deep_value(config_key)
                self.remove_prefix
                if (dir_name is not None and 
                    dir_name.startswith(persistent_dot_vistrails)):
                    suffix = self.remove_prefix(dir_name, 
                                                persistent_dot_vistrails)
                    print "suffix:", suffix
                    if suffix:
                        new_dir = os.path.join(self.DOT_VISTRAILS_PREFIX, 
                                               suffix)
                    else:
                        new_dir = self.DOT_VISTRAILS_PREFIX
                    print "SETTING new configuration", config_key, new_dir
                    self.configuration.set_deep_value(config_key, new_dir)
        self.save_persisted_startup()

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
        # FIXME need to deal with case where config value is
        # $DOT_VISTRAILS and that doesn't exist
        dir_name, abs_dir_name, is_default = \
                                self.resolve_dir_name(config_key, default_dir)
        if abs_dir_name is not None:
            self.create_directory(abs_dir_name)
        if is_default:
            self.update_deep_configs(config_key, dir_name)
        self.temp_configuration.set_deep_value(config_key, abs_dir_name)
        if abs_dir_name is not None and setup_init_file:
            self.setup_init_file(abs_dir_name)
        return abs_dir_name

    def setup_log_file(self, abs_dir_name):
        import vistrails.core.system
        version = vistrails.core.system.vistrails_version()
        version = version.replace(".", "_")
        
        # # FIXME this is really log dir, not log file
        # # we should really create a logs subdir in .vistrails
        # is_default = False
        # if not self.temp_configuration.check('logFile'):
        #     dir_name = self._dot_vistrails
        #     is_default = True
        # else:
        #     dir_name = os.path.dirname(self.temp_configuration.logFile)
        # abs_dir_name = self.expand_vt_path(dir_name)
        # if abs_dir_name is not None:
        #     self.create_directory(abs_dir_name)
        #     log_fname = os.path.join(abs_dir_name, 'vistrails_%s.log' % version)
        # else:
        #     log_fname = None
        # if is_default:
        #     self.update_deep_configs("logFile", 
        #                              os.path.join(dir_name,
        #                                           'vistrails_%s.log' % version))
        log_fname = os.path.join(abs_dir_name, 'vistrails_%s.log' % version)
        if log_fname is not None:
            debug.DebugPrint.getInstance().set_logfile(log_fname)
            
    def setup_debug(self):
        if (self.temp_configuration.has('debugLevel') and
            self.temp_configuration.debugLevel != -1):
            verbose = self.temp_configuration.debugLevel
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


    def setup_dot_vistrails(self):
        for i, args in enumerate(self.DIRECTORIES):
            abs_dir_name = self.setup_directory(*args)
            # Brittle, know that log directory is first
            if i == 0:
                self.setup_log_file(abs_dir_name)
        self.setup_debug()


    def setup_non_dot_vistrails(self):
        self.temp_configuration.set_deep_value('logFile', None)
        for (config_key, _, _) in self.DIRECTORIES:
            self.temp_configuration.set_deep_value(config_key, None)

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

    def update_packages(self):
        # make sure basic_modules and abstraction are enabled
        self.set_package_to_enabled('basic_modules')
        self.set_package_to_enabled('abstraction')
        self.enabled_packages['basic_modules'].prefix = \
                                            "vistrails.core.modules."
        self.enabled_packages['abstraction'].prefix = \
                                            "vistrails.core.modules."

    def load_persisted_startup(self):
        if self._dot_vistrails is not None:
            fname = self.get_startup_xml_fname()
            other = vistrails.core.db.io.load_startup(fname)
            self.configuration.update(other.configuration)
            self.db_enabled_packages = copy.copy(other.db_enabled_packages)
            self.db_disabled_packages = copy.copy(other.db_disabled_packages)

    def save_persisted_startup(self):
        if self._dot_vistrails is not None:
            fname = self.get_startup_xml_fname()
            vistrails.core.db.io.save_startup(self, fname)

    def get_pkg_startup_info(self, codepath):
        if codepath in self.enabled_packages:
            return self.enabled_packages[codepath]
        elif codepath in self.disabled_packages:
            return self.disabled_packages[codepath]
        return None

    def get_pkg_configuration(self, codepath):
        startup_info = self.get_pkg_startup_info(codepath)
        if startup_info is not None:
            return startup_info.configuration
        return None

    def persist_pkg_configuration(self, codepath, config):
        startup_info = self.get_pkg_startup_info(codepath)
        if startup_info is not None:
            startup_info.configuration = config
        else:
            startup_info = StartupPackage(name=codepath,
                                          configuration=config)
            self.db_disabled_packages.db_add_package(startup_info)
        self.save_persisted_startup()

    def set_package_enabled(self, codepath, enabled=True):
        package = None
        was_enabled = False
        was_disabled = False
        if codepath in self.enabled_packages:
            package = self.enabled_packages[codepath]
            was_enabled = True
        if codepath in self.disabled_packages:
            if package is None:
                package = self.disabled_packages[codepath]
            was_disabled = True
        if package is None:
            package = StartupPackage(name=codepath)

        def update_package_list(update_obj):
            # this is a kludge since the db code doesn't support non-keyed
            # deletion and name isn't a key right now
            # FIXME may cause issues with relational storage
            old_packages = update_obj.db_packages
            update_obj.db_packages = []
            update_obj.db_packages_name_index = {}
            for p in old_packages:
                if p.name != codepath:
                    update_obj.db_add_package(p)
            
        if was_enabled:
            update_package_list(self.db_enabled_packages)
        if was_disabled:
            update_package_list(self.db_disabled_packages)

        if enabled:
            self.db_enabled_packages.db_add_package(package)
        else:
            self.db_disabled_packages.db_add_package(package)

    def set_package_to_enabled(self, codepath):
        self.set_package_enabled(codepath, True)

    def set_package_to_disabled(self, codepath):
        self.set_package_enabled(codepath, False)

    def create_startupxml_if_needed(self):
        needs_create = True
        fname = self.get_startup_xml_fname()
        if os.path.isfile(fname):
            try:
                tree = ElementTree.parse(fname)
                startup_version = \
                    vistrails.db.services.io.get_version_for_xml(tree.getroot())
                version_list = version_string_to_list(startup_version)
                if version_list >= [0,1]:
                    needs_create = False
            except:
                debug.warning("Unable to read startup.xml file, "
                              "creating a new one")

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
                    self.configuration.subworkflowsDirectory = abstractions_dir
                    self.temp_configuration.subworkflowsDirectory = \
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
                if self.temp_configuration.check('subworkflowsDirectory'):
                    abstractions = self.temp_configuration.subworkflowsDirectory
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
        if (self.temp_configuration.has('debugLevel') and
            self.temp_configuration.debugLevel != -1):
            verbose = self.temp_configuration.debugLevel
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
        self.assertTrue(os.path.isfile(
            os.path.join(dir_name, 'logs', "vistrails_%s.log" % version)))

    def test_simple_create(self):
        dir_name = tempfile.mkdtemp()
        options_config = ConfigurationObject(dotVistrails=dir_name)
        try:
            startup = VistrailsStartup(options_config, None)
            self.check_structure(dir_name)
        finally:
            shutil.rmtree(dir_name)

    def test_create_dir_create(self):
        outer_dir_name = tempfile.mkdtemp()
        dir_name = os.path.join(outer_dir_name, '.vistrails')
        cl_config = ConfigurationObject(dotVistrails=dir_name)
        try:
            startup = VistrailsStartup(None, cl_config)
            self.check_structure(dir_name)
        finally:
            shutil.rmtree(outer_dir_name)
        
    def test_config_override(self):
        dir_name = tempfile.mkdtemp()
        user_pkg_dir = tempfile.mkdtemp()
        abstractions_dir = tempfile.mkdtemp()
        thumbs_dir = tempfile.mkdtemp()
        log_dir = tempfile.mkdtemp()
        config = vistrails.core.configuration.default()
        config.dotVistrails = dir_name
        config.userPackageDirectory = user_pkg_dir
        config.subworkflowsDirectory = abstractions_dir
        config.thumbs.cacheDirectory = thumbs_dir
        config.logDirectory = log_dir
        try:
            startup = VistrailsStartup(config, None)
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
            shutil.rmtree(log_dir)

    def test_config_override_create(self):
        dir_name = tempfile.mkdtemp()
        outer_user_pkg_dir = tempfile.mkdtemp()
        user_pkg_dir = os.path.join(outer_user_pkg_dir, 'userpackages')
        outer_abstractions_dir = tempfile.mkdtemp()
        abstractions_dir = os.path.join(outer_abstractions_dir, 'subworkflows')
        outer_thumbs_dir = tempfile.mkdtemp()
        thumbs_dir = os.path.join(outer_thumbs_dir, 'thumbs')
        outer_log_dir = tempfile.mkdtemp()
        log_dir = os.path.join(outer_log_dir, 'logs')
        config = vistrails.core.configuration.default()
        config.dotVistrails = dir_name
        config.userPackageDirectory = user_pkg_dir
        config.subworkflowsDirectory = abstractions_dir
        config.thumbs.cacheDirectory = thumbs_dir
        config.logDirectory = log_dir
        try:
            startup = VistrailsStartup(config, None)
            self.assertTrue(os.path.isfile(os.path.join(dir_name, 
                                                        'startup.xml')))
            for t in VistrailsStartup.DIRECTORIES:
                a_dir = os.path.join(dir_name, t[1])
                self.assertFalse(os.path.isdir(a_dir),
                                'Directory "%s" exists' % a_dir)
            self.assertTrue(os.path.isdir(user_pkg_dir))
            self.assertTrue(os.path.isdir(abstractions_dir))
            self.assertTrue(os.path.isdir(thumbs_dir))
            self.assertTrue(os.path.isdir(log_dir))
        finally:
            shutil.rmtree(dir_name)
            shutil.rmtree(outer_user_pkg_dir)
            shutil.rmtree(outer_abstractions_dir)
            shutil.rmtree(outer_thumbs_dir)
            shutil.rmtree(outer_log_dir)
    
    def test_default_startup_xml(self):
        dir_name = tempfile.mkdtemp()
        config = ConfigurationObject(dotVistrails=dir_name)
        try:
            startup = VistrailsStartup(config, None)
            self.assertTrue(startup.configuration.executionLog)
            self.assertTrue(startup.configuration.autoSave)
            self.assertTrue(startup.temp_configuration.autoSave)
        finally:
            shutil.rmtree(dir_name)

    def test_cannot_create(self):
        (fd, fname) = tempfile.mkstemp()
        config = ConfigurationObject(dotVistrails=fname)
        try:
            with self.assertRaises(ValueError):
                startup = VistrailsStartup(config, None)
        finally:
            os.unlink(fname)
        
    def test_permissions(self):
        dir_name = tempfile.mkdtemp()
        config = ConfigurationObject(dotVistrails=dir_name)
        try:
            os.chmod(dir_name, stat.S_IRUSR)
            with self.assertRaises(IOError):
                startup = VistrailsStartup(config, None)
        finally:
            os.chmod(dir_name, stat.S_IRWXU)
            shutil.rmtree(dir_name)
            
    # def test_load_packages(self):
    #     from vistrails.core.system import default_dot_vistrails
    #     dir_name = default_dot_vistrails()
    #     config = ConfigurationObject(dotVistrails=dir_name)
    #     startup = VistrailsStartup(config, None)
        
        
if __name__ == '__main__':
    unittest.main()
