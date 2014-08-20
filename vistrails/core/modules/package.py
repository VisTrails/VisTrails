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
import copy
import inspect
import os
import re
import sys
import traceback

import vistrails
from vistrails.core import debug
from vistrails.core import get_vistrails_application
from vistrails.core.configuration import ConfigurationObject
from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.utils import versions_increasing, VistrailsInternalError
from vistrails.core.utils.uxml import (named_elements, enter_named_element)
from vistrails.db.domain import DBPackage


vistrails_dir = os.path.dirname(os.path.realpath(vistrails.__file__))

##############################################################################

class Package(DBPackage):
    Base, User, Other = 0, 1, 2

    FIX_PACKAGE_NAMES = ["api", "core", "db", "gui", "packages", "tests"]

    class InitializationFailed(Exception):
        def __init__(self, package, tracebacks):
            self.package = package
            self.tracebacks = tracebacks
        def __str__(self):
            try:
                name = self.package.name
                if name is None:
                    name = 'codepath <%s>' % self.package.codepath
            except AttributeError:
                name = 'codepath <%s>' % self.package.codepath
            return ("Package '%s' failed to initialize because of the "
                    "following exceptions:\n%s" % \
                        (name, "\n".join(self.tracebacks)))

    class LoadFailed(Exception):
        def __init__(self, package, exception, traceback):
            self.package = package
            self.exception = exception
            self.traceback = traceback
        def __str__(self):
            return ("Package '%s' failed to load, raising '%s: %s'. Traceback:\n%s" %
                    (self.package.codepath,
                     self.exception.__class__.__name__,
                     self.exception,
                     self.traceback))

    class MissingDependency(Exception):
        def __init__(self, package, dependencies):
            self.package = package
            self.dependencies = dependencies
        def __str__(self):
            def dep_string(dep):
                retval = dep[0]
                if dep[1] is not None:
                    retval += ': requires version >= %s' % dep[1]
                    if dep[2] is not None:
                        retval += ' and <= %s' % dep[2]
                elif dep[2] is not None:
                    retval += ': requires version <= %s' % dep[2]
                return retval

            return ("Package '%s' has unmet dependencies:\n  %s" %
                    (self.package.name,
                     '\n  '.join([dep_string(d) for d in self.dependencies])))

    def __init__(self, *args, **kwargs):
        if 'load_configuration' in kwargs:
            arg = kwargs['load_configuration']
            if not isinstance(arg, (int, long)):
                if isinstance(arg, bool):
                    if arg:
                        kwargs['load_configuration'] = 1
                    else:
                        kwargs['load_configuration'] = 0
                    # kwargs['load_configuration'] = 1 if arg else 0
                else:
                    raise VistrailsInternalError("Cannot convert "
                                                 "load_configuration")

        DBPackage.__init__(self, *args, **kwargs)
        self.set_defaults()
        self._force_no_unload = None
        self._force_unload = None
        self._force_sys_unload = None
        self._imports_are_good = True
    
    def __copy__(self):
        Package.do_copy(self)

    def set_defaults(self, other=None):
        self.setup_indices()
        if other is None:
            self._module = None
            self._init_module = None
            self._loaded = False
            self._initialized = False
            self._abs_pkg_upgrades = {}
            self.package_dir = None
            self.prefix = None
            self.py_dependencies = set()
            self.old_identifiers = []
            self._default_configuration = None
            self._persistent_configuration = None
        else:
            self._module = other._module
            self._init_module = other._init_module
            self._loaded = other._loaded
            self._initialized = other._initialized
            self._abs_pkg_upgrades = copy.copy(other._abs_pkg_upgrades)
            self.package_dir = other.package_dir
            self.prefix = other.prefix
            self.py_dependencies = copy.copy(other.py_dependencies)
            self.old_identifiers = [i for i in self.old_identifiers]
            self._default_configuration = \
                                        copy.copy(other._default_configuration)
            self._persistent_configuration = \
                                    copy.copy(other._persistent_configuration)

        # FIXME decide whether we want None or ''
        if self.version is None:
            self.version = ''

    def setup_indices(self):
        self.descriptor_versions = self.db_module_descriptors_name_index
        self.descriptors_by_id = self.db_module_descriptors_id_index
        self.descriptors = {}
        for key, desc in self.descriptor_versions.iteritems():
            key = key[:2]
            if key in self.descriptors:
                old_desc = self.descriptors[key]
                if versions_increasing(old_desc.version, desc.version):
                    self.descriptors[key] = desc
            else:
                self.descriptors[key] = desc

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPackage.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Package
        cp.set_defaults(self)
        
    @staticmethod
    def convert(_package):
        if _package.__class__ == Package:
            return
        _package.__class__ = Package

        for descriptor in _package.db_module_descriptors:
            ModuleDescriptor.convert(descriptor)
        _package.set_defaults()

    ##########################################################################
    # Properties
    
    id = DBPackage.db_id
    name = DBPackage.db_name
    identifier = DBPackage.db_identifier
    description = DBPackage.db_description
    version = DBPackage.db_version
    codepath = DBPackage.db_codepath
    load_configuration = DBPackage.db_load_configuration
    descriptor_list = DBPackage.db_module_descriptors

    def add_descriptor(self, desc):
        self.db_add_module_descriptor(desc)
        key = (desc.name, desc.namespace)
        if key in self.descriptors:
            old_desc = self.descriptors[key]
            if versions_increasing(old_desc.version, desc.version):
                self.descriptors[key] = desc
        else:
            self.descriptors[key] = desc
        
    def delete_descriptor(self, desc):
        self.db_delete_module_descriptor(desc)
        # FIXME hard to incremental updates here so we'll just recreate
        # this can be slow
        self.setup_indices()

    def _get_module(self):
        return self._module
    module = property(_get_module)

    def _get_init_module(self):
        return self._init_module
    init_module = property(_get_init_module)

    def _get_configuration(self):
        if hasattr(self._module, 'configuration'):
            return self._module.configuration
        else:
            return None
    def _set_configuration(self, configuration):
        if hasattr(self._module, 'configuration'):
            self._module.configuration = configuration
        else:
            raise AttributeError("Can't set configuration on a module "
                                 "without one")
    configuration = property(_get_configuration, _set_configuration)

    ##########################################################################
    # Operators

    def __hash__(self):
        if self.identifier and self.version:
            return (type(self), self.identifier, self.version).__hash__()
        return (type(self), self.codepath).__hash__()

    def __eq__(self, other):
        return (type(self) == type(other) and 
                self.identifier == other.identifier and
                self.version == other.version)

    def __str__(self):
        return ("Package(id=%s, identifier=%s, version=%s, name=%s, "
                "codepath=%s") % (self.id, self.identifier,
                                  self.version, self.name,
                                  self.codepath)

    ##########################################################################
    # Methods

    _python_lib_regex = re.compile(r'python[0-9.]+[a-z]?/lib/(?!vistrails)',
                                   re.IGNORECASE)
    _lib_python_regex = re.compile(r'lib/python[0-9.]+[a-z]?/(?!vistrails)',
                                   re.IGNORECASE)
    def import_override(self, orig_import,
                        name, globals, locals, fromlist, level,
                        package_importing_directly):
        def in_package_list(pkg_name, pkg_list):
            if pkg_list is None:
                return False
            for pkg in pkg_list:
                if pkg_name == pkg or pkg_name.startswith(pkg + '.'):
                    return True
            return False

        def is_sys_pkg(pkg):
            try:
                pkg_fname = pkg.__file__
            except AttributeError:
                return True
            if os.path.realpath(pkg_fname).startswith(vistrails_dir):
                return False
            if "site-packages" in pkg_fname:
                return True
            if os.sep != '/':
                pkg_fname = pkg_fname.replace(os.sep, '/')
            return (self._python_lib_regex.search(pkg_fname) or
                    self._lib_python_regex.search(pkg_fname))

        sys_modules = sys.modules.keys()

        def checked_add_package(qual_name, pkg):
            if qual_name in sys_modules:
                return
            if (not in_package_list(qual_name, self._force_no_unload) and
                    (self._force_sys_unload or not is_sys_pkg(pkg)
                     or in_package_list(qual_name, self._force_unload)) and
                     not qual_name.endswith('_rc')):
                self.py_dependencies.add(qual_name)

        fixed = False
        try:
            res = orig_import(name, globals, locals, fromlist, level)
        except ImportError:
            if not package_importing_directly:
                # We only fix stuff imported directly from a package, i.e. we
                # only tolerate misspellings in the package's code
                raise

            # backward compatibility for packages that import without
            # "vistrails." prefix
            for pkg in Package.FIX_PACKAGE_NAMES:
                if name == pkg or name.startswith(pkg + '.'):
                    if self._imports_are_good: # only warn first time
                        self._imports_are_good = False
                        debug.warning(
                            "In package '%s', Please use the 'vistrails.' "
                            "prefix when importing vistrails packages." %
                            (self.identifier or self.codepath))
                    fixed = pkg
                    name = "vistrails." + name
                    break
            if fixed:
                res = orig_import(name, globals, locals, fromlist, level)
            else:
                raise
        mod = res

        if not fromlist:
            checked_add_package(mod.__name__, mod)
            for comp in name.split('.')[1:]:
                try:
                    mod = getattr(mod, comp)
                    checked_add_package(mod.__name__, mod)
                except AttributeError:
                    break
        else:
            res_name = mod.__name__
            checked_add_package(mod.__name__, mod)
            for from_name in fromlist:
                qual_name = res_name + '.' + from_name
                checked_add_package(qual_name, mod)

        if fixed and not fromlist:
            return getattr(res, fixed)
        else:
            return res

    def get_py_deps(self):
        return self.py_dependencies

    def load(self, prefix=None):
        """load(module=None). Loads package's module.

        If package is already loaded, this is a NOP.

        """

        errors = []
        if self._loaded:
            return

        def import_from(p_path):
            # print 'running import_from'
            try:
                # print p_path + self.codepath
                self.prefix = p_path
                __import__(p_path + self.codepath,
                           globals(),
                           locals(),
                           [])
                self._module = module = sys.modules[p_path + self.codepath]
                self.py_dependencies.add(p_path + self.codepath)
                self._package_type = self.Base

                if hasattr(module, "_force_no_unload_pkg_list"):
                    self._force_no_unload = module._force_no_unload_pkg_list
                else:
                    self._force_no_unload = []
                if hasattr(module, "_force_unload_pkg_list"):
                    self._force_unload = module._force_unload_pkg_list
                else:
                    self._force_unload = []
                if hasattr(module, "_force_sys_unload"):
                    self._force_sys_unload = module._force_sys_unload
                else:
                    self._force_sys_unload = False
            except ImportError, e:
                errors.append(traceback.format_exc())
                self.prefix = None
                return False
            return True

        try:
            if self.prefix is not None:
                r = not import_from(self.prefix)
            elif prefix is not None:
                r = not import_from(prefix)
            else:
                r = (not import_from('vistrails.packages.') and
                     not import_from('userpackages.'))
        except Exception, e:
            raise self.LoadFailed(self, e, traceback.format_exc())

        if r:
            raise self.InitializationFailed(self, errors)

        self.set_properties()
        self.do_load_configuration()

    def initialize(self):
        if not self._loaded:
            raise VistrailsInternalError("Called initialize() on non-loaded "
                                         "Package %s" % self.codepath)

        self.check_requirements()

        try:
            name = self.prefix + self.codepath + '.init'
            try:
                __import__(name, globals(), locals(), [])
            except ImportError, e:
                # FIXME !!! Want to differentiate between .init not
                # existing and an error with an import in the .init
                # file !!!
                if str(e) != 'No module named init':
                    raise
                else:
                    self._init_module = self._module
            else:
                self._init_module = sys.modules[name]
                self.py_dependencies.add(name)
                # Copy attributes (shallow) from _module into _init_module's namespace and point _module to _init_module
                module_attributes = ['identifier', 'name', 'version',
                                     'configuration', 'package_dependencies',
                                     'package_requirements',
                                     'can_handle_identifier',
                                     'can_handle_vt_file']
                for attr in module_attributes:
                    if (hasattr(self._module, attr) and
                            not hasattr(self._init_module, attr)):
                        setattr(self._init_module, attr, getattr(self._module, attr))
                self._module = self._init_module

            if hasattr(self._init_module, 'initialize'):
                self._init_module.initialize()
        except Exception, e:
            debug.unexpected_exception(e)
            self.unload()
            raise

    def unload(self):
        for path in self.py_dependencies:
            if path not in sys.modules:
                # print "skipping %s" % path
                pass
            else:
                # print 'deleting path:', path, path in sys.modules
                del sys.modules[path]
        self.py_dependencies.clear()
        self._loaded = False

    def set_properties(self):
        # Set properties
        try:
            self._loaded = True
            self.name = self._module.name
            self.identifier = self._module.identifier
            self.version = self._module.version
            if hasattr(self._module, "old_identifiers"):
                self.old_identifiers = self._module.old_identifiers
            self.package_dir = os.path.dirname(self._module.__file__)
        except AttributeError, e:
            try:
                v = self._module.__file__
            except AttributeError:
                v = self._module
            raise e
        descr = inspect.getdoc(self._module)
        if descr:
            self.description = re.sub('^ *\n', '', descr.rstrip())
        else:
            self.description = "(No description available)"

    def can_handle_all_errors(self):
        return hasattr(self._init_module, 'handle_all_errors')

    def can_handle_upgrades(self):
        return hasattr(self._init_module, 'handle_module_upgrade_request')

    def can_handle_identifier(self, identifier):
        """ Asks package if it can handle this package
        """
        try:
            return (hasattr(self.init_module, 'can_handle_identifier') and
                    self.init_module.can_handle_identifier(identifier))
        except Exception, e:
            debug.critical("Got exception calling %s's can_handle_identifier: "
                           "%s: %s" % (self.name,
                                       type(e).__name__, ', '.join(e.args)))
            return False

    def can_handle_vt_file(self, name):
        """ Asks package if it can handle a file inside a zipped vt file
        """
        try:
            return (hasattr(self.init_module, 'can_handle_vt_file') and
                    self.init_module.can_handle_vt_file(name))
        except Exception, e:
            debug.critical("Got exception calling %s's can_handle_vt_file: "
                           "%s: %s" % (self.name,
                                       type(e).__name__, ', '.join(e.args)))
            return False

    def can_handle_missing_modules(self):
        return hasattr(self._init_module, 'handle_missing_module')

    def handle_all_errors(self, *args, **kwargs):
        return self._init_module.handle_all_errors(*args, **kwargs)

    def handle_module_upgrade_request(self, *args, **kwargs):
        return self._init_module.handle_module_upgrade_request(*args, **kwargs)
        
    def handle_missing_module(self, *args, **kwargs):
        """report_missing_module(name, namespace):

        Calls the package's module handle_missing_module function, if
        present, to allow the package to dynamically add a missing
        module.
        """
        return self._init_module.handle_missing_module(*args, **kwargs)

    def add_abs_upgrade(self, new_desc, name, namespace, module_version):
        key = (name, namespace)
        if key not in self._abs_pkg_upgrades:
            self._abs_pkg_upgrades[key] = {}
        self._abs_pkg_upgrades[key][module_version] = new_desc

    def has_abs_upgrade(self, name, namespace='', module_version=''):
        key = (name, namespace)
        if key not in self._abs_pkg_upgrades:
            return False
        if module_version and module_version not in self._abs_pkg_upgrades[key]:
            return False
        return True
        
    def get_abs_upgrade(self, name, namespace='', module_version=''):
        key = (name, namespace)
        if key in self._abs_pkg_upgrades:
            if module_version:
                if module_version in self._abs_pkg_upgrades[key]:
                    return self._abs_pkg_upgrades[key][module_version]
            else:
                latest_version = max(self._abs_pkg_upgrades[key].iterkeys())
                return self._abs_pkg_upgrades[key][latest_version]
        return None

    def has_contextMenuName(self):
        return hasattr(self._init_module, 'contextMenuName')

    def contextMenuName(self, signature):
        return self._init_module.contextMenuName(signature)
    
    def has_callContextMenu(self):
        return hasattr(self._init_module, 'callContextMenu')

    def callContextMenu(self, signature):
        return self._init_module.callContextMenu(signature)

    def loadVistrailFileHook(self, vistrail, tmp_dir):
        if hasattr(self._init_module, 'loadVistrailFileHook'):
            try:
                self._init_module.loadVistrailFileHook(vistrail, tmp_dir)
            except Exception, e:
                debug.critical("Got exception in %s's loadVistrailFileHook(): "
                               "%s: %s" % (self.name, type(e).__name__,
                                           ', '.join(e.args)))

    def saveVistrailFileHook(self, vistrail, tmp_dir):
        if hasattr(self._init_module, 'saveVistrailFileHook'):
            try:
                self._init_module.saveVistrailFileHook(vistrail, tmp_dir)
            except Exception, e:
                debug.critical("Got exception in %s's saveVistrailFileHook(): "
                               "%s: %s" % (self.name, type(e).__name__,
                                           ', '.join(e.args)))

    def check_requirements(self):
        try:
            callable_ = self._module.package_requirements
        except AttributeError:
            return
        else:
            callable_()

    def menu_items(self):
        try:
            callable_ = self._module.menu_items
        except AttributeError:
            return None
        else:
            try:
                return callable_()
            except Exception, e:
                debug.critical("Couldn't load menu items for %s: %s: %s" % (
                               self.name, type(e).__name__, ', '.join(e.args)))

    def finalize(self):
        if not self._initialized:
            return
        debug.log("Finalizing %s" % self.name)
        try:
            callable_ = self._module.finalize
        except AttributeError:
            pass
        else:
            try:
                callable_()
            except Exception, e:
                debug.critical("Couldn't finalize %s: %s: %s" % (
                               self.name, type(e).__name__, ', '.join(e.args)))
        # Save configuration
        if self.load_configuration and self.configuration is not None:
            self.persist_configuration()
        self.unload()
        self._module = None
        self._init_module = None
        self._initialized = False

    def dependencies(self):
        deps = []
        try:
            callable_ = self._module.package_dependencies
        except AttributeError:
            pass
        else:
            try:
                deps = callable_()
            except Exception, e:
                debug.critical("Couldn't get dependencies of %s: %s: %s" % (
                               self.name, type(e).__name__, ', '.join(e.args)))

        if self._module is not None and \
                hasattr(self._module, '_dependencies'):
            deps.extend(self._module._dependencies)
        return deps

    def initialized(self):
        return self._initialized

    ##########################################################################
    # Configuration

    def _get_persistent_configuration(self):
        return self._persistent_configuration
    def _set_persistent_configuration(self, config):
        self._persistent_configuration = config
    persistent_configuration = property(_get_persistent_configuration,
                                        _set_persistent_configuration)

    def do_load_configuration(self):
        # Sometimes we don't want to change startup.xml, for example
        # when peeking at a package that's on the available package list
        # on edit -> preferences. That's what the load_configuration field
        # is for
        if self.load_configuration:
            if self.configuration is not None:
                # hold a copy of the initial configuration so it can be reset
                self._default_configuration = copy.copy(self.configuration)

                # now we update the actual configuration in place so it is
                # available to the package itself
                if self.persistent_configuration is not None:
                    self.configuration.update(self.persistent_configuration)
                else:
                    # we don't have a persisted configuration so we
                    # should create one
                    self.persistent_configuration = \
                                                copy.copy(self.configuration)
                    self.persist_configuration(True)

        
    def persist_configuration(self, no_update=False):
        if self.load_configuration:
            if not no_update:
                self.persistent_configuration.update(self.configuration)
            # make sure startup is updated to reflect changes
            get_vistrails_application().startup.persist_pkg_configuration(
                self.codepath, self.persistent_configuration)

    def reset_configuration(self):
        """Reset package configuration to original package settings.

        """
        self.configuration = copy.copy(self._default_configuration)
        if self.load_configuration:
            self.persisted_configuration = copy.copy(self.configuration)
            self.persist_configuration(True)
