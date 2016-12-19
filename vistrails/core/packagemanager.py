###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

"""The package manager takes care of everything that has got to do
with handling packages, from setting paths to adding new packages
to checking dependencies to initializing them."""
from __future__ import division

import copy
from distutils.version import LooseVersion
import inspect
import itertools
import os
import sys
import warnings

from vistrails.core import debug, get_vistrails_application, system
from vistrails.core.configuration import ConfigurationObject, \
    get_vistrails_configuration
import vistrails.core.data_structures.graph
from vistrails.core.modules.module_registry import MissingPackage, \
    MissingPackageVersion
from vistrails.core.modules.package import Package
from vistrails.core.requirements import MissingRequirement
from vistrails.core.utils import VistrailsInternalError, \
    versions_increasing, VistrailsDeprecation
import vistrails.packages

##############################################################################


global _package_manager
_package_manager = None

class PackageManager(object):
    """Discovers and loads packages of VisTrails modules.

    Signals:
    * add_package_menu_signal is emitted with a tuple containing the package
      identifier, package name and the menu item
    * remove_package_menu_signal is emitted with the package identifier
    * package_error_message_signal is emitted with the package identifier,
      package name and the error message
    * reloading_package_signal is emitted when a package reload has disabled
      the packages, but has not yet enabled them
    """

    class DependencyCycle(Exception):
        """There is a cycle in the dependencies between packages.
        """
        def __init__(self, p1, p2):
            self._package_1 = p1
            self._package_2 = p2
        def __str__(self):
            return ("Packages '%s' and '%s' have cyclic dependencies" %
                    (self._package_1,
                     self._package_2))

    class PackageInternalError(Exception):
        """An error was raised by the package while it was loading.
        """
        def __init__(self, n, d):
            self._package_name = n
            self._description = d
        def __str__(self):
            return "Package '%s' has a bug: %s" % (self._package_name,
                                                   self._description)

    def import_packages_module(self):
        """Imports the 'vistrails.packages' package.

        This might need to manipulate the Python path to find it.
        """
        if self._packages is not None:
            return self._packages
        # Imports standard packages directory
        conf = self._startup.temp_configuration
        old_sys_path = copy.copy(sys.path)
        if conf.check('packageDirectory'):
            sys.path.insert(0, conf.packageDirectory)
        try:
            import vistrails.packages
        except ImportError:
            debug.critical('ImportError: "packages" sys.path: %s' % sys.path)
            raise
        finally:
            sys.path = old_sys_path
        self._packages = vistrails.packages
        return vistrails.packages

    def import_user_packages_module(self):
        """Imports the 'userspackages' package.

        This will need to manipulate the Python path to find it.
        """
        if self._userpackages is not None:
            return self._userpackages
        # Imports user packages directory
        old_sys_path = copy.copy(sys.path)
        userPackageDir = system.get_vistrails_directory('userPackageDir')
        if userPackageDir is not None:
            sys.path.insert(0, os.path.join(userPackageDir, os.path.pardir))
            try:
                import userpackages
            except ImportError:
                debug.critical('ImportError: "userpackages" sys.path: %s' %
                               sys.path)
                raise
            finally:
                sys.path = old_sys_path
            os.environ['VISTRAILS_USERPACKAGES_DIR'] = userPackageDir
            self._userpackages = userpackages
            return userpackages
        # possible that we don't have userPackageDir set!
        return None

    def __init__(self, registry, startup):
        global _package_manager
        if _package_manager:
            m = "Package manager can only be constructed once."
            raise VistrailsInternalError(m)
        _package_manager = self

        self._registry = registry
        self._startup = startup

        # Contains packages that have not yet been enabled, but exist on the
        # filesystem
        self._available_packages = {} # codepath: str -> Package
        # These other lists contain enabled packages
        self._package_list = {} # codepath: str -> Package
        self._package_versions = {} # identifier: str -> version -> Package
        self._old_identifier_map = {} # old_id: str -> new_id: str
        self._dependency_graph = vistrails.core.data_structures.graph.Graph()
        self._default_prefix_dict = \
                                {'basic_modules': 'vistrails.core.modules.',
                                 'abstraction': 'vistrails.core.modules.'}

        self._userpackages = None
        self._packages = None
        self._abstraction_pkg = None
        self._currently_importing_package = None

        # Setup a global __import__ hook that calls Package#import_override()
        # for all imports executed from that package
        import __builtin__
        self._orig_import = __builtin__.__import__
        __builtin__.__import__ = self._import_override

        # Compute the list of available packages, _available_packages
        self.build_available_package_names_list()

        if get_vistrails_configuration().loadPackages:
            for pkg in self._startup.enabled_packages.itervalues():
                self.add_package(pkg.name, prefix=pkg.prefix)
        else:
            try:
                basic_pkg = self._startup.enabled_packages['basic_modules']
            except KeyError:
                pass
            else:
                self.add_package(basic_pkg.name, prefix=basic_pkg.prefix)

            try:
                abs_pkg = self._startup.enabled_packages['abstraction']
            except KeyError:
                pass
            else:
                self.add_package(abs_pkg.name, prefix=abs_pkg.prefix)

    def _import_override(self,
                         name, globals={}, locals={}, fromlist=[], level=-1):
        """Overridden __import__ function.

        This replaces the builtin __import__ function globally so that we can
        track imports done from a package. This is recorded in the Package so
        that reloading the package actually reloads all dependent code.
        """
        # Get the caller module, using globals (like the original __import
        # does)
        try:
            if globals is None:
                raise KeyError
            module = globals['__name__']
        except KeyError:
            # Another method of getting the caller module, using the stack
            caller = inspect.currentframe().f_back
            module = inspect.getmodule(caller)
            # Some frames might not be associated to a module, because of the
            # use of exec for instance; we just skip these until we reach a
            # valid one
            while module is None:
                caller = caller.f_back
                if caller is None:
                    break
                module = inspect.getmodule(caller)
            if module:
                module = module.__name__

        # Get the Package from the module name
        if module:
            importing_pkg = None
            current = self._currently_importing_package
            if (current is not None and
                    current.prefix and
                    module.startswith(current.prefix + current.codepath)):
                importing_pkg = current
            else:
                for pkg in itertools.chain(
                        self._package_list.itervalues(),
                        self._available_packages.itervalues()):
                    if (pkg.prefix is not None and
                            module.startswith(pkg.prefix + pkg.codepath)):
                        importing_pkg = pkg
                        break

            # If we are importing directly from a package
            if importing_pkg is not None:
                old_current = self._currently_importing_package
                self._currently_importing_package = importing_pkg
                result = importing_pkg.import_override(
                        self._orig_import,
                        name, globals, locals, fromlist, level,
                        package_importing_directly=True)
                self._currently_importing_package = old_current
                return result
            # If we are doing it indirectly (from other stuff imported from a
            # package)
            elif self._currently_importing_package is not None:
                return self._currently_importing_package.import_override(
                        self._orig_import,
                        name, globals, locals, fromlist, level,
                        package_importing_directly=False)

        # Else, this is not from a package
        return self._orig_import(name, globals, locals, fromlist, level)

    def finalize_packages(self):
        """Finalizes all initialized packages.
        """
        for package in self._package_list.itervalues():
            package.finalize()
        self._package_list = {}
        self._package_versions = {}
        self._old_identifier_map = {}
        global _package_manager
        _package_manager = None

    def get_available_package(self, codepath, prefix=None):
        try:
            pkg = self._available_packages[codepath]
        except KeyError:
            pkg = self._registry.create_package(codepath, prefix=prefix)
            self._available_packages[codepath] = pkg
        pkg.persistent_configuration = \
                                self._startup.get_pkg_configuration(codepath)
        return pkg

    def add_package(self, codepath, add_to_package_list=True, prefix=None):
        """Adds a new package to the manager. This does not initialize it.

        You will have to call initialize_packages() to initialize loaded but
        uninitialized packages.
        """
        package = self.get_available_package(codepath)
        if add_to_package_list:
            self.add_to_package_list(codepath, package, prefix)
        return package

    def add_to_package_list(self, codepath, package, prefix=None):
        self._available_packages[codepath] = package
        self._package_list[codepath] = package
        if prefix is not None:
            self._default_prefix_dict[codepath] = prefix

    def remove_old_identifiers(self, identifier):
        # remove refs in old_identifier_map
        old_ids = []
        for old_id, cur_id in self._old_identifier_map.iteritems():
            if cur_id == identifier:
                old_ids.append(old_id)
        for old_id in old_ids:
            del self._old_identifier_map[old_id]

    def remove_package(self, codepath):
        """Removes a package from the system.

        Use late_disable_package() in application code so that the
        configuration is updated.
        """
        pkg = self._package_list[codepath]

        from vistrails.core.interpreter.cached import CachedInterpreter
        CachedInterpreter.clear_package(pkg.identifier)

        self._dependency_graph.delete_vertex(pkg.identifier)
        del self._package_versions[pkg.identifier][pkg.version]
        if len(self._package_versions[pkg.identifier]) == 0:
            del self._package_versions[pkg.identifier]
        self.remove_old_identifiers(pkg.identifier)
        self.remove_menu_items(pkg)
        pkg.finalize()
        del self._package_list[codepath]
        self._registry.remove_package(pkg)
        app = get_vistrails_application()
        app.send_notification("package_removed", codepath)

    def has_package(self, identifier, version=None):
        """Returns true if given package identifier is present.
        """

        # check if it's an old identifier
        identifier = self._old_identifier_map.get(identifier, identifier)
        if identifier in self._package_versions:
            return (version is None or
                    version in self._package_versions[identifier])
        return False

    def look_at_available_package(self, codepath):
        """Returns a Package object for an uninitialized package.

        This does NOT initialize it.
        """
        return self.get_available_package(codepath)

    def get_package(self, identifier, version=None):
        # check if it's an old identifier
        identifier = self._old_identifier_map.get(identifier, identifier)
        try:
            package_versions = self._package_versions[identifier]
            if version is not None:
                return package_versions[version]
        except KeyError:
            # dynamic packages are only registered in the registry
            try:
                return self._registry.get_package_by_name(identifier, version)
            except MissingPackageVersion:
                return self._registry.get_package_by_name(identifier)

        max_version = '0'
        max_pkg = None
        for version, pkg in package_versions.iteritems():
            if versions_increasing(max_version, version):
                max_version = version
                max_pkg = pkg
        return max_pkg

    def get_package_by_codepath(self, codepath):
        """Returns a package with given codepath if it is initialized.

        :raises MissingPackage: if the package is not loaded or initialized.
        """
        if codepath not in self._package_list:
            raise MissingPackage(codepath)
        else:
            return self._package_list[codepath]

    def get_package_by_identifier(self, identifier):
        """Deprecated, use get_package() instead.
        """
        warnings.warn(
                "You should use get_package instead of "
                "get_package_by_identifier",
                VistrailsDeprecation,
                stacklevel=2)
        return self.get_package(identifier)

    def get_package_configuration(self, codepath):
        """Returns the configuration object for the package, or None.

        This will only return None if the package exists but has no
        configuration object.
        :raises MissingPackage: if the package is not loaded or initialized.
        """
        pkg = self.get_package_by_codepath(codepath)

        if not hasattr(pkg.module, 'configuration'):
            return None
        else:
            c = pkg.module.configuration
            if not isinstance(c, ConfigurationObject):
                d = "'configuration' attribute should be a ConfigurationObject"
                raise self.PackageInternalError(codepath, d)
            return c

    def check_dependencies(self, package, deps):
        # want to check that necessary version also exists, if specified
        missing_deps = []
        for dep in deps:
            min_version = None
            max_version = None
            if isinstance(dep, tuple):
                identifier = dep[0]
                if len(dep) > 1:
                    min_version = dep[1]
                    if len(dep) > 2:
                        max_version = dep[2]
            else:
                identifier = dep

            # check if it's an old identifier
            identifier = self._old_identifier_map.get(identifier, identifier)
            if identifier not in self._package_versions:
                missing_deps.append((identifier, None, None))
            else:
                if min_version is None and max_version is None:
                    continue
                found_version = False
                for version, pkg in \
                        self._package_versions[identifier].iteritems():
                    if ((min_version is None or
                         versions_increasing(min_version, version)) and
                        (max_version is None or
                         versions_increasing(version, max_version))):
                        found_version = True
                if not found_version:
                    missing_deps.append((identifier, min_version, max_version))

        if len(missing_deps) > 0:
            raise Package.MissingDependency(package, missing_deps)
        return True

    def add_dependencies(self, package):
        """Register all the dependencies of a package contains.
        """
        deps = package.dependencies()
        # FIXME don't hardcode this
        from vistrails.core.modules.basic_modules import identifier as basic_pkg
        if package.identifier != basic_pkg:
            deps.append(basic_pkg)

        self.check_dependencies(package, deps)

        for dep in deps:
            if isinstance(dep, tuple):
                dep_name = dep[0]
            else:
                dep_name = dep
            dep_name = self.get_package(dep_name).identifier

            if not self._dependency_graph.has_edge(package.identifier,
                                                   dep_name):
                self._dependency_graph.add_edge(package.identifier, dep_name)

    def late_enable_package(self, codepath, prefix_dictionary={},
                            needs_add=True):
        """Enables a package 'late', i.e. after VisTrails initialization.

        Note that all the dependencies need to already be enabled.
        """
        if needs_add:
            if codepath in self._package_list:
                msg = 'duplicate package identifier: %s' % codepath
                raise VistrailsInternalError(msg)
            self.add_package(codepath)
        app = get_vistrails_application()
        pkg = self.get_package_by_codepath(codepath)
        try:
            pkg.load(prefix_dictionary.get(pkg.codepath, None))
            # pkg.create_startup_package_node()
        except Exception, e:
            # invert self.add_package
            del self._package_list[codepath]
            raise
        self._dependency_graph.add_vertex(pkg.identifier)
        if pkg.identifier not in self._package_versions:
            self._package_versions[pkg.identifier] = {}
        self._package_versions[pkg.identifier][pkg.version] = pkg
        for old_id in pkg.old_identifiers:
            self._old_identifier_map[old_id] = pkg.identifier
        try:
            self.add_dependencies(pkg)
            #check_requirements is now called in pkg.initialize()
            #pkg.check_requirements()
            self._registry.initialize_package(pkg)
            self._registry.signals.emit_new_package(pkg.identifier, True)
            app.send_notification("package_added", codepath)
            self.add_menu_items(pkg)
            self._startup.set_package_to_enabled(codepath)
        except Exception, e:
            del self._package_versions[pkg.identifier][pkg.version]
            if len(self._package_versions[pkg.identifier]) == 0:
                del self._package_versions[pkg.identifier]
            self.remove_old_identifiers(pkg.identifier)
            self._dependency_graph.delete_vertex(pkg.identifier)
            # invert self.add_package
            del self._package_list[codepath]
            # if we adding the package to the registry, make sure we
            # remove it if initialization fails
            try:
                self._registry.remove_package(pkg)
            except MissingPackage:
                pass
            raise e
        self._startup.save_persisted_startup()

    def late_disable_package(self, codepath):
        """Disables a package 'late', i.e. after VisTrails initialization.

        Note that all the reverse dependencies need to already be disabled.
        """
        pkg = self.get_package_by_codepath(codepath)
        self.remove_package(codepath)
        app = get_vistrails_application()
        self._startup.set_package_to_disabled(codepath)
        self._startup.save_persisted_startup()

    def reload_package_disable(self, codepath):
        # for all reverse dependencies, disable them
        prefix_dictionary = {}
        pkg = self.get_package_by_codepath(codepath)
        reverse_deps = []
        for dep_id in self.all_reverse_dependencies(pkg.identifier):
            reverse_deps.append(self.get_package(dep_id))

        for dep_pkg in reverse_deps:
            prefix_dictionary[dep_pkg.codepath] = dep_pkg.prefix
            self.late_disable_package(dep_pkg.codepath)

        # Queue the re-enabling of the packages so event loop can free
        # any QObjects whose deleteLater() method is invoked
        app = get_vistrails_application()
        app.send_notification("pm_reloading_package", codepath,
                              reverse_deps, prefix_dictionary)
        # self.emit(self.reloading_package_signal,
        #           codepath,
        #           reverse_deps,
        #           prefix_dictionary)

    def reload_package_enable(self, reverse_deps, prefix_dictionary):
        # for all reverse dependencies, enable them
        for dep_pkg in reversed(reverse_deps):
            self.late_enable_package(dep_pkg.codepath, prefix_dictionary)

    def initialize_packages(self, prefix_dictionary={},
                            report_missing_dependencies=True):
        """Initializes all installed packages.

        :param prefix_dictionary: dictionary from package names to the prefix
        such that prefix + package_name is a valid python import.
        :type prefix_dictionary: dict
        """
        failed = []
        # import the modules
        app = get_vistrails_application()
        for package in self._package_list.itervalues():
            # print '+ initializing', package.codepath, id(package)
            if package.initialized():
                # print '- already initialized'
                continue
            try:
                prefix = prefix_dictionary.get(package.codepath)
                if prefix is None:
                    prefix = self._default_prefix_dict.get(package.codepath)
                package.load(prefix)
            except Package.LoadFailed, e:
                debug.critical("Package %s failed to load and will be "
                               "disabled" % package.name, e)
                # We disable the package manually to skip over things
                # we know will not be necessary - the only thing needed is
                # the reference in the package list
                self._startup.set_package_to_disabled(package.codepath)
                failed.append(package)
            except MissingRequirement, e:
                debug.critical("Package <codepath %s> is missing a "
                               "requirement: %s" % (
                                   package.codepath, e.requirement),
                               e)
            except Package.InitializationFailed, e:
                debug.critical("Initialization of package <codepath %s> "
                               "failed and will be disabled" %
                               package.codepath,
                               e)
                # We disable the package manually to skip over things
                # we know will not be necessary - the only thing needed is
                # the reference in the package list
                self._startup.set_package_to_disabled(package.codepath)
                failed.append(package)
            else:
                if package.identifier not in self._package_versions:
                    self._package_versions[package.identifier] = {}
                    self._dependency_graph.add_vertex(package.identifier)
                elif package.version in \
                        self._package_versions[package.identifier]:
                    raise VistrailsInternalError("Duplicate package version: "
                                                 "'%s' (version %s) in %s" % \
                                                     (package.identifier,
                                                      package.version,
                                                      package.codepath))
                else:
                    debug.warning('Duplicate package identifier: %s' % \
                                      package.identifier)
                self._package_versions[package.identifier][package.version] = \
                    package
                for old_id in package.old_identifiers:
                    self._old_identifier_map[old_id] = package.identifier

        for pkg in failed:
            del self._package_list[pkg.codepath]
        failed = []

        # determine dependencies
        for package in self._package_list.itervalues():
            try:
                self.add_dependencies(package)
            except Package.MissingDependency, e:
                if report_missing_dependencies:
                    debug.critical("Dependencies of package %s are missing "
                                   "so it will be disabled" % package.name,
                                   e)
            except Exception, e:
                if report_missing_dependencies:
                    debug.critical("Got an exception while getting dependencies "
                                   "of %s so it will be disabled" % package.name,
                                   e)
            else:
                continue
            self._startup.set_package_to_disabled(package.codepath)
            self._dependency_graph.delete_vertex(package.identifier)
            del self._package_versions[package.identifier][package.version]
            if len(self._package_versions[package.identifier]) == 0:
                del self._package_versions[package.identifier]
            self.remove_old_identifiers(package.identifier)
            failed.append(package)

        for pkg in failed:
            del self._package_list[pkg.codepath]

        # perform actual initialization
        try:
            g = self._dependency_graph.inverse_immutable()
            sorted_packages = g.vertices_topological_sort()
        except vistrails.core.data_structures.graph.GraphContainsCycles, e:
            raise self.DependencyCycle(e.back_edge[0],
                                       e.back_edge[1])

        for name in sorted_packages:
            pkg = self.get_package(name)
            if not pkg.initialized():
                #check_requirements is now called in pkg.initialize()
                #pkg.check_requirements()
                try:
                    self._registry.initialize_package(pkg)
                except MissingRequirement, e:
                    if report_missing_dependencies:
                        debug.critical("Package <codepath %s> is missing a "
                                       "requirement: %s" % (
                                           pkg.codepath, e.requirement),
                                       e)
                    self.late_disable_package(pkg.codepath)
                except Package.InitializationFailed, e:
                    debug.critical("Initialization of package <codepath %s> "
                                   "failed and will be disabled" %
                                   pkg.codepath,
                                   e)
                    # We disable the package manually to skip over things
                    # we know will not be necessary - the only thing needed is
                    # the reference in the package list
                    self.late_disable_package(pkg.codepath)
                else:
                    self.add_menu_items(pkg)
                    app = get_vistrails_application()
                    app.send_notification("package_added", pkg.codepath)

        self._startup.save_persisted_startup()

    def add_menu_items(self, pkg):
        """Emit the appropriate signal if the package has menu items.

        :type pkg: Package
        """
        items = pkg.menu_items()
        if items:
            app = get_vistrails_application()
            app.send_notification("pm_add_package_menu", pkg.identifier,
                                  pkg.name, items)
            # self.emit(self.add_package_menu_signal,
            #           pkg.identifier,
            #           pkg.name,
            #           items)

    def remove_menu_items(self, pkg):
        """Emit the appropriate signal if the package has menu items.

        :type pkg: Package
        """
        if pkg.menu_items():
            app = get_vistrails_application()
            app.send_notification("pm_remove_package_menu",
                                   pkg.identifier)
            # self.emit(self.remove_package_menu_signal,
            #           pkg.identifier)

    def show_error_message(self, pkg, msg):
        """Print and emit a notification for an error message.
        """
        # TODO: isn't debug enough for the UI?
        debug.critical("Package %s (%s) says: %s"%(pkg.name,
                                                   pkg.identifier,
                                                   msg))
        app = get_vistrails_application()
        app.send_notification("pm_package_error_message", pkg.identifier,
                              pkg.name, msg)

    def enabled_package_list(self):
        """Returns list of all enabled packages."""
        return self._package_list.values()

    def identifier_is_available(self, identifier):
        """Searchs for an available (but disabled) package.

        If found, returns succesfully loaded, uninitialized package.

        There can be multiple package versions for a single identifier. If so,
        return the version that passes requirements, or the latest version.
        """
        matches = []
        for codepath in self.available_package_names_list():
            pkg = self.get_available_package(codepath)
            try:
                pkg.load()
                if pkg.identifier == identifier:
                    matches.append(pkg)
                elif identifier in pkg.old_identifiers:
                    matches.append(pkg)
                if (hasattr(pkg._module, "can_handle_identifier") and
                        pkg._module.can_handle_identifier(identifier)):
                    matches.append(pkg)
            except (pkg.LoadFailed, pkg.InitializationFailed,
                    MissingRequirement):
                pass
            except Exception, e:
                debug.warning(
                    "Error loading package <codepath %s>" % pkg.codepath,
                    e)
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        # return package version that passes requirements
        valids = []
        for pkg in matches:
            try:
                pkg.check_requirements()
                valids.append(pkg)
            except (pkg.LoadFailed, pkg.InitializationFailed,
                    MissingRequirement):
                pass
            except Exception, e:
                debug.warning(
                    "Package <codepath %s> raised an exception while "
                    "querying requirements" % pkg.codepath,
                    e)
        if len(valids) == 1:
            return valids[0]
        elif len(valids) == 0:
            # return latest invalid package
            valids = matches
        # return latest version
        return sorted(valids, key=lambda x: LooseVersion(x.version))[-1]

    def available_package_names_list(self):
        """Returns the list of all available packages' codepaths.
        """
        return self._available_packages.keys()

    def build_available_package_names_list(self):
        def is_vistrails_package(path):
            if os.path.isfile(path):
                return (path.endswith('.py') and
                        not path.endswith('__init__.py'))
            elif os.path.isdir(path):
                return os.path.isfile(os.path.join(path, '__init__.py'))
            return False

        def search(dirname, prefix):
            for name in os.listdir(dirname):
                if is_vistrails_package(os.path.join(dirname, name)):
                    if name.endswith('.py'):
                        name = name[:-3]
                    self.get_available_package(name, prefix=prefix)

        # Finds standard packages
        packages = self.import_packages_module()
        # This makes VisTrails not zip-safe
        search(os.path.dirname(packages.__file__),
               prefix='vistrails.packages.')

        # Finds user packages
        userpackages = self.import_user_packages_module()
        if userpackages is not None:
            search(os.path.dirname(userpackages.__file__),
                   prefix='userpackages.')

        # Finds plugin packages
        try:
            from pkg_resources import iter_entry_points
        except ImportError:
            pass
        else:
            for entry_point in iter_entry_points('vistrails.packages'):
                # Reads module name and turns it into prefix and codepath
                name = entry_point.module_name.rsplit('.', 1)
                if len(name) > 1:
                    prefix, name = name
                    prefix = '%s.' % prefix
                else:
                    prefix = ''
                    name, = name

                # Create the Package, with the right prefix
                self.get_available_package(name, prefix=prefix)

        return self._available_packages.keys()

    def dependency_graph(self):
        """Returns a graph with package dependencies.

        Vertices are the package identifiers (strings), and an edge u -> v
        means that u depends on v.

        :rtype: Graph
        """
        return self._dependency_graph

    def can_be_disabled(self, identifier):
        """Returns whether a package has no reverse dependencies.
        """
        return self._dependency_graph.in_degree(identifier) == 0

    def reverse_dependencies(self, identifier):
        lst = [x[0] for x in
               self._dependency_graph.inverse_adjacency_list[identifier]]
        return lst

    # use this call if we're not necessarily loading
    def build_dependency_graph(self, pkg_identifiers):
        dep_graph = vistrails.core.data_structures.graph.Graph()

        def process_dependencies(identifier):
            dep_graph.add_vertex(identifier)
            pkg = self.identifier_is_available(identifier)
            if pkg:
                deps = pkg.dependencies()
                for dep in deps:
                    if isinstance(dep, tuple):
                        dep_name = dep[0]
                    else:
                        dep_name = dep

                    if dep_name not in self._dependency_graph.vertices and \
                            not dep_graph.has_edge(identifier, dep_name):
                        dep_graph.add_edge(identifier, dep_name)
                        process_dependencies(dep_name)

        for pkg_identifier in pkg_identifiers:
            process_dependencies(pkg_identifier)

        return dep_graph

    def get_ordered_dependencies(self, dep_graph, identifiers=None):
        try:
            sorted_packages = dep_graph.vertices_topological_sort(identifiers)
        except vistrails.core.data_structures.graph.GraphContainsCycles, e:
            raise self.DependencyCycle(e.back_edge[0],
                                       e.back_edge[1])
        return list(reversed(sorted_packages))

    def get_all_dependencies(self, identifier, reverse=False, dep_graph=None):
        if dep_graph is None:
            dep_graph = self._dependency_graph

        if reverse:
            adj_list = dep_graph.inverse_adjacency_list
        else:
            adj_list = dep_graph.adjacency_list

        all = [identifier]
        last_adds = [identifier]
        while len(last_adds) != 0:
            adds = [x[0] for y in last_adds for x in adj_list[y]]
            all.extend(adds)
            last_adds = adds

        seen = set()
        order = []
        for pkg in reversed(all):
            if pkg not in seen:
                order.append(pkg)
                seen.add(pkg)
        return order

    def all_dependencies(self, identifier, dep_graph=None):
        return self.get_all_dependencies(identifier, False, dep_graph)

    def all_reverse_dependencies(self, identifier, dep_graph=None):
        return self.get_all_dependencies(identifier, True, dep_graph)

def get_package_manager():
    if not _package_manager:
        raise VistrailsInternalError("package manager not constructed yet.")
    return _package_manager

##############################################################################

import unittest


class TestImports(unittest.TestCase):
    def test_package(self):
        from vistrails.tests.utils import MockLogHandler

        pm = get_package_manager()
        pm.get_available_package(
                'test_import_pkg',
                prefix='vistrails.tests.resources.import_pkg.')

        # Check the package is in the list
        available_pkg_names = pm.available_package_names_list()
        self.assertIn('test_import_pkg', available_pkg_names)

        # Import __init__ and check metadata
        pkg = pm.look_at_available_package('test_import_pkg')
        with MockLogHandler(debug.DebugPrint.getInstance().logger) as log:
            pkg.load('vistrails.tests.resources.import_pkg.')
        self.assertEqual(len(log.messages['warning']), 1)
        self.assertEqual(pkg.identifier,
                         'org.vistrails.tests.test_import_pkg')
        self.assertEqual(pkg.version,
                         '0.42')
        for n in ['vistrails.tests.resources.import_targets.test1',
                  'vistrails.tests.resources.import_targets.test2']:
            self.assertIn(n, sys.modules, "%s not in sys.modules" % n)

        # Import init.py
        pm.late_enable_package(
                'test_import_pkg',
                {'test_import_pkg':
                 'vistrails.tests.resources.import_pkg.'})
        pkg = pm.get_package_by_codepath('test_import_pkg')
        for n in ['vistrails.tests.resources.import_targets.test3',
                  'vistrails.tests.resources.import_targets.test4',
                  'vistrails.tests.resources.import_targets.test5']:
            self.assertIn(n, sys.modules, "%s not in sys.modules" % n)

        # Check dependencies
        deps = pkg.get_py_deps()
        for dep in ['vistrails.tests.resources.import_pkg.test_import_pkg',
                    'vistrails.tests.resources.import_pkg.test_import_pkg.init',
                    'vistrails.tests.resources.import_pkg.test_import_pkg.module1',
                    'vistrails.tests.resources.import_pkg.test_import_pkg.module2',
                    'vistrails.tests.resources.import_targets',
                    'vistrails.tests.resources.import_targets.test1',
                    'vistrails.tests.resources.import_targets.test2',
                    'vistrails.tests.resources.import_targets.test3',
                    'vistrails.tests.resources.import_targets.test4',
                    'vistrails.tests.resources.import_targets.test5',
                    'vistrails.tests.resources.import_targets.test6']:
            self.assertIn(dep, deps)
