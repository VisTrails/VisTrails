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

"""Describes the start-up process of VisTrails"""
from vistrails.core import debug
from vistrails.core import system
from vistrails.core.configuration import ConfigurationObject
from vistrails.db.domain import DBStartup, DBStartupPackage, \
    DBEnabledPackages, DBDisabledPackages
import vistrails.db.services.io
import vistrails.core.db.io
from vistrails.core.system import get_elementtree_library, \
    get_vistrails_directory, systemType
from vistrails.core.utils import version_string_to_list

import atexit
import copy
import os.path
import re
import shutil
import string
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

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.name == other.name and
                self.configuration == other.configuration)

    def __ne__(self, other):
        return not self.__eq__(other)

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
    DIRECTORIES = [('logDir', 'logs', False),
                   ('userPackageDir', 'userpackages', True),
                   ('subworkflowsDir', 'subworkflows', False),
                   ('thumbs.cacheDir', 'thumbs', False)]
    DOT_VISTRAILS_PREFIX = "$DOT_VISTRAILS"
    DOT_VISTRAILS_PREFIX_RE = re.compile("%s([%s/\\\\]|$)" % 
                                         (re.escape(DOT_VISTRAILS_PREFIX),
                                          os.path.sep))

    first_run = False

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

        if ((command_line_config is not None and
                 command_line_config.check('spawned')) or 
                (options_config is not None and 
                 options_config.check('spawned'))):
            # Here we are in 'spawned' mode, i.e. we are running
            # non-interactively as a slave
            # We are going to create a .vistrails directory as a temporary
            # directory and copy a specific configuration file
            # We don't want to load packages that the user might enabled in
            # this machine's configuration file as it would slow down the
            # startup time, but we'll load any needed package without
            # confirmation
            tmpdir = tempfile.mkdtemp(prefix='vt_spawned_')
            @atexit.register
            def clean_dotvistrails():
                shutil.rmtree(tmpdir, ignore_errors=True)
            command_line_config.dotVistrails = tmpdir
            shutil.copyfile(os.path.join(system.vistrails_root_directory(),
                                         'core', 'resources',
                                         'spawned_startup_xml'),
                            os.path.join(tmpdir, 'startup.xml'))
            command_line_config.enablePackagesSilently = True
            command_line_config.errorLog = False
            command_line_config.singleInstance = False

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

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        def check_packages(self_pkgs, other_pkgs):
            if len(self_pkgs.db_packages) != len(other_pkgs.db_packages):
                return False
            for (p_name, pkg1) in \
                    self_pkgs.db_packages_name_index.iteritems():
                if p_name not in other_pkgs.db_packages_name_index:
                    return False
                else:
                    pkg2 = other_pkgs.db_packages_name_index[p_name]
                    if pkg1 != pkg2:
                        return False
            return True
        return (self.configuration == other.configuration and
                check_packages(self.db_enabled_packages, 
                               other.db_enabled_packages) and
                check_packages(self.db_disabled_packages,
                               other.db_disabled_packages))

    def get_startup_xml_fname(self):
        return os.path.join(self._dot_vistrails, 'startup.xml')

    def setup_base_dot_vistrails(self):
        self.create_dot_vistrails_if_necessary()
        self.create_startupxml_if_needed()

    def load_and_update_configurations(self, options_config, 
                                       command_line_config):
        # load options from startup.xml
        self.load_persisted_startup()

        # set up temporary configuration with options and command-line
        self.temp_configuration = copy.copy(self.configuration)

        if options_config is not None:
            self.temp_configuration.update(options_config)
        if command_line_config is not None:
            self.temp_configuration.update(command_line_config)

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

    def create_directory(self, dir_name):
        if not os.path.isdir(dir_name):
            debug.warning('Will try to create directory "%s"' % dir_name)
            try:
                os.mkdir(dir_name)
                return True
            except Exception, e:
                msg = ("Failed to create directory: '%s'."
                       "This could be an indication of a permissions problem."
                       "Make sure directory '%s' in writable." %
                       (str(e), dir_name))
                debug.critical(msg)
                sys.exit(1)
        return False

    def setup_directory(self, config_key, default_dir, setup_init_file=False):
        abs_dir_name = get_vistrails_directory(config_key, 
                                               self.temp_configuration)        
        if abs_dir_name is not None:
            self.create_directory(abs_dir_name)
        if abs_dir_name is not None and setup_init_file:
            self.setup_init_file(abs_dir_name)
        return abs_dir_name

    def setup_log_file(self, abs_dir_name):
        import vistrails.core.system
        version = vistrails.core.system.vistrails_version()
        version = version.replace(".", "_")

        if self.temp_configuration.errorLog:
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
            levels = [dbg.WARNING, dbg.INFO, dbg.DEBUG]
            dbg.set_message_level(levels[verbose])
            debug.log("Set verboseness level to %s" % verbose)


    def setup_dot_vistrails(self):
        for i, args in enumerate(self.DIRECTORIES):
            abs_dir_name = self.setup_directory(*args)
            # Brittle, know that log directory is first
            if i == 0:
                self.setup_log_file(abs_dir_name)
        self.setup_debug()

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
                self.first_run = True
            except:
                debug.critical("""Failed to copy default configuration
                file to %s. This could be an indication of a
                permissions problem. Please make sure '%s' is writable."""
                               % (fname, self._dot_vistrails))
                raise

import unittest
import stat

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

    def close_logger(self):
        for handler in debug.DebugPrint._instance.logger.handlers[:]:
            handler.close()
            debug.DebugPrint._instance.logger.removeHandler(handler)

    def test_simple_create(self):
        dir_name = tempfile.mkdtemp()
        options_config = ConfigurationObject(dotVistrails=dir_name)
        try:
            startup = VistrailsStartup(options_config, None)
            self.check_structure(dir_name)
        finally:
            self.close_logger()
            shutil.rmtree(dir_name)

    def test_create_dir_create(self):
        outer_dir_name = tempfile.mkdtemp()
        dir_name = os.path.join(outer_dir_name, '.vistrails')
        cl_config = ConfigurationObject(dotVistrails=dir_name)
        try:
            startup = VistrailsStartup(None, cl_config)
            self.check_structure(dir_name)
        finally:
            self.close_logger()
            shutil.rmtree(outer_dir_name)
        
    def test_config_override(self):
        dir_name = tempfile.mkdtemp()
        user_pkg_dir = tempfile.mkdtemp()
        abstractions_dir = tempfile.mkdtemp()
        thumbs_dir = tempfile.mkdtemp()
        log_dir = tempfile.mkdtemp()
        config = vistrails.core.configuration.default()
        config.dotVistrails = dir_name
        config.userPackageDir = user_pkg_dir
        config.subworkflowsDir= abstractions_dir
        config.thumbs.cacheDir = thumbs_dir
        config.logDir = log_dir
        try:
            startup = VistrailsStartup(config, None)
            self.assertTrue(os.path.isfile(os.path.join(dir_name, 
                                                        'startup.xml')))
            for t in VistrailsStartup.DIRECTORIES:
                a_dir = os.path.join(dir_name, t[1])
                self.assertFalse(os.path.isdir(a_dir),
                                'Directory "%s" exists' % a_dir)
        finally:
            self.close_logger()
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
        config.userPackageDir = user_pkg_dir
        config.subworkflowsDir = abstractions_dir
        config.thumbs.cacheDir = thumbs_dir
        config.logDir = log_dir
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
            self.close_logger()
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
            self.close_logger()
            shutil.rmtree(dir_name)

    def test_cannot_create(self):
        (fd, fname) = tempfile.mkstemp()
        os.close(fd)
        config = ConfigurationObject(dotVistrails=fname)
        try:
            with self.assertRaises(ValueError):
                startup = VistrailsStartup(config, None)
        finally:
            os.unlink(fname)
        
    def test_permissions(self):
        if systemType in ['Windows', 'Microsoft']:
            self.skipTest("chmod on Windows is limited")
        dir_name = tempfile.mkdtemp()
        config = ConfigurationObject(dotVistrails=dir_name)
        try:
            os.chmod(dir_name, stat.S_IRUSR)
            with self.assertRaises(IOError):
                startup = VistrailsStartup(config, None)
        finally:
            os.chmod(dir_name, stat.S_IRWXU)
            shutil.rmtree(dir_name)

    def test_load_old_startup_xml(self):
        # has old nested shell settings that don't match current naming
        startup_tmpl = os.path.join(system.vistrails_root_directory(),
                                    'tests', 'resources',
                                    'startup-0.1.xml.tmpl')
        f = open(startup_tmpl, 'r')
        template = string.Template(f.read())
        
        startup_dir = tempfile.mkdtemp(prefix="vt_startup")
        old_startup_fname = os.path.join(startup_dir, "startup.xml")
        with open(old_startup_fname, 'w') as f:
            f.write(template.substitute({'startup_dir': startup_dir}))

        startup1 = vistrails.core.db.io.load_startup(old_startup_fname)

        (h, fname) = tempfile.mkstemp(suffix=".xml")
        os.close(h)
        try:
            vistrails.core.db.io.save_startup(startup1, fname)
            startup2 = vistrails.core.db.io.load_startup(fname)
            self.assertEqual(startup1, startup2)
        finally:
            os.remove(fname)
            shutil.rmtree(startup_dir)

    # def test_load_packages(self):
    #     from vistrails.core.system import default_dot_vistrails
    #     dir_name = default_dot_vistrails()
    #     config = ConfigurationObject(dotVistrails=dir_name)
    #     startup = VistrailsStartup(config, None)
        
        
if __name__ == '__main__':
    unittest.main()
