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

"""The package manager takes care of everything that has got to do
with handling packages, from setting paths to adding new packages
to checking dependencies to initializing them."""

import copy
import os
import sys

from core import debug, get_vistrails_application
from core.configuration import ConfigurationObject
import core.data_structures.graph
import core.db.io
from core.modules.module_registry import ModuleRegistry, MissingPackage
from core.modules.package import Package
from core.utils import VistrailsInternalError, InstanceObject, \
    versions_increasing
##############################################################################


global _package_manager
_package_manager = None

class PackageManager(object):
    # # add_package_menu_signal is emitted with a tuple containing the package
    # # identifier, package name and the menu item
    # add_package_menu_signal = QtCore.SIGNAL("add_package_menu")
    # # remove_package_menu_signal is emitted with the package identifier
    # remove_package_menu_signal = QtCore.SIGNAL("remove_package_menu")
    # # package_error_message_signal is emitted with the package identifier,
    # # package name and the error message
    # package_error_message_signal = QtCore.SIGNAL("package_error_message_signal")
    # # reloading_package_signal is emitted when a package reload has disabled
    # # the packages, but has not yet enabled them
    # reloading_package_signal = QtCore.SIGNAL("reloading_package_signal")

    class DependencyCycle(Exception):
        def __init__(self, p1, p2):
            self._package_1 = p1
            self._package_2 = p2
        def __str__(self):
            return ("Packages '%s' and '%s' have cyclic dependencies" %
                    (self._package_1,
                     self._package_2))

    class MissingPackage(Exception):
        def __init__(self, n):
            self._package_name = n
        def __str__(self):
            return "Package '%s' is missing." % self._package_name

    class PackageInternalError(Exception):
        def __init__(self, n, d):
            self._package_name = n
            self._description = d
        def __str__(self):
            return "Package '%s' has a bug: %s" % (self._package_name,
                                                   self._description)

    def import_packages_module(self):
        """Imports the packages module using path trickery to find it
        in the right place.

        """
        if self._packages is not None:
            return self._packages
        # Imports standard packages directory
        conf = self._configuration
        old_sys_path = copy.copy(sys.path)
        if conf.check('packageDirectory'):
            sys.path.insert(0, conf.packageDirectory)
        try:
            import packages
        except ImportError:
            debug.critical('ImportError: "packages" sys.path: %s' % sys.path)
            raise
        finally:
            sys.path = old_sys_path
        self._packages = packages
        return packages

    def import_user_packages_module(self):
        """Imports the packages module using path trickery to find it
        in the right place.

        """
        if self._userpackages is not None:
            return self._userpackages
        # Imports user packages directory
        conf = self._configuration
        old_sys_path = copy.copy(sys.path)
        if conf.check('userPackageDirectory'):
            sys.path.insert(0, os.path.join(conf.userPackageDirectory,
                                            os.path.pardir))
        try:
            import userpackages
        except ImportError:
            debug.critical('ImportError: "userpackages" sys.path: %s' % sys.path)
            raise
        finally:
            sys.path = old_sys_path
        self._userpackages = userpackages
        return userpackages

    def __init__(self, configuration):
        """__init__(configuration: ConfigurationObject) -> PackageManager
        configuration is the persistent configuration object of the application.
        
        """
        global _package_manager
        if _package_manager:
            m = "Package manager can only be constructed once."
            raise VistrailsInternalError(m)
        _package_manager = self
        self._configuration = configuration
        self._package_list = {}
        self._package_versions = {}
        self._dependency_graph = core.data_structures.graph.Graph()
        self._registry = None
        self._userpackages = None
        self._packages = None
        self._abstraction_pkg = None

    def init_registry(self, registry_filename=None):
        if registry_filename is not None:
            self._registry = core.db.io.open_registry(registry_filename)
            self._registry.set_global()
        else:
            self._registry = ModuleRegistry()
            self._registry.set_global()

            def setup_basic_package():
                # setup basic package
                basic_package = self.add_package('basic_modules')
                self._registry._default_package = basic_package
                prefix_dictionary = {'basic_modules': 'core.modules.'}
                self.initialize_packages(prefix_dictionary)
            setup_basic_package()

            self._abstraction_pkg = self.add_package('abstraction', False)
            # FIXME need to get this info from the package, but cannot
            # do this since controller isn't imported yet
            self._abstraction_pkg.identifier = 'local.abstractions'
            self._abstraction_pkg.name = 'My SubWorkflows'
            self._abstraction_pkg.version = '1.6'
            self._registry.add_package(self._abstraction_pkg)

    def finalize_packages(self):
        """Finalizes all installed packages. Call this only prior to
exiting VisTrails."""
        for package in self._package_list.itervalues():
            package.finalize()
        self._package_list = {}
        self._package_versions = {}
        global _package_manager
        _package_manager = None

    def add_package(self, codepath, add_to_package_list=True):
        """Adds a new package to the manager. This does not initialize it.
To do so, call initialize_packages()"""
        package = self._registry.create_package(codepath)
        if add_to_package_list:
            self.add_to_package_list(codepath, package)
        app = get_vistrails_application()
        app.send_notification("package_added", codepath)
        return package

    def add_to_package_list(self, codepath, package):
        self._package_list[codepath] = package

    def initialize_abstraction_pkg(self, prefix_dictionary):
        if self._abstraction_pkg is None:
            raise Exception("Subworkflows packages is None")
        self.add_to_package_list(self._abstraction_pkg.codepath,
                                 self._abstraction_pkg)
        self.late_enable_package(self._abstraction_pkg.codepath, 
                                 prefix_dictionary, False)

    def remove_package(self, codepath):
        """remove_package(name): Removes a package from the system."""
        pkg = self._package_list[codepath]
        self._dependency_graph.delete_vertex(pkg.identifier)
        del self._package_versions[pkg.identifier][pkg.version]
        if len(self._package_versions[pkg.identifier]) == 0:
            del self._package_versions[pkg.identifier]
        self.remove_menu_items(pkg)
        pkg.finalize()
        del self._package_list[codepath]
        self._registry.remove_package(pkg)
        app = get_vistrails_application()
        app.send_notification("package_removed", codepath)

    def has_package(self, identifier, version=None):
        """has_package(identifer: string) -> Boolean.
Returns true if given package identifier is present."""
        if identifier in self._package_versions:
            return (version is None or 
                    version in self._package_versions[identifier])
        return False

    def look_at_available_package(self, codepath):
        """look_at_available_package(codepath: string) -> Package

        Returns a Package object for an uninstalled package. This does
        NOT install a package.
        """
        return self._registry.create_package(codepath, False)

    def get_package(self, identifier, version=None):
        package_versions = self._package_versions[identifier]
        if version is not None:
            return package_versions[version]

        max_version = '0'
        max_pkg = None
        for version, pkg in package_versions.iteritems():
            if versions_increasing(max_version, version):
                max_version = version
                max_pkg = pkg
        return max_pkg

    def get_package_by_codepath(self, codepath):
        """get_package_by_codepath(codepath: string) -> Package.
        Returns a package with given codepath if it is enabled,
        otherwise throws exception
        """
        if codepath not in self._package_list:
            raise self.MissingPackage(codepath)
        else:
            return self._package_list[codepath]

    def get_package_by_identifier(self, identifier):
        """get_package_by_identifier(identifier: string) -> Package.
        Returns a package with given identifier if it is enabled,
        otherwise throws exception
        """
        if identifier not in self._registry.packages:
            raise self.MissingPackage(identifier)
        return self._registry.packages[identifier]

    def get_package_configuration(self, codepath):
        """get_package_configuration(codepath: string) ->
        ConfigurationObject or None

        Returns the configuration object for the package, if existing,
        or None. Throws MissingPackage if package doesn't exist.
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
            if type(dep) == tuple:
                identifier = dep[0]
                if len(dep) > 1:
                    min_version = dep[1]
                    if len(dep) > 2:
                        max_version = dep[2]
            else:
                identifier = dep

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
        """add_dependencies(package) -> None.  Register all
        dependencies a package contains by calling the appropriate
        callback.

        Does not add multiple dependencies - if a dependency is already there,
        add_dependencies ignores it.
        """
        deps = package.dependencies()
        # FIXME don't hardcode this
        from core.modules.basic_modules import identifier as basic_pkg
        if package.identifier != basic_pkg:
            deps.append(basic_pkg)

        self.check_dependencies(package, deps)

        for dep in deps:
            if type(dep) == tuple:
                dep_name = dep[0]
            else:
                dep_name = dep

            if not self._dependency_graph.has_edge(package.identifier,
                                                   dep_name):
                self._dependency_graph.add_edge(package.identifier, dep_name)

    def late_enable_package(self, package_codepath, prefix_dictionary={}, 
                            needs_add=True):
        """late_enable_package enables a package 'late', that is,
        after VisTrails initialization. All dependencies need to be
        already enabled.
        """
        if needs_add:
            if package_codepath in self._package_list:
                msg = 'duplicate package identifier: %s' % package_codepath
                raise VistrailsInternalError(msg)
            self.add_package(package_codepath)
        pkg = self.get_package_by_codepath(package_codepath)
        try:
            pkg.load(prefix_dictionary.get(pkg.codepath, None))
        except Exception, e:
            # invert self.add_package
            del self._package_list[package_codepath]
            raise
        self._dependency_graph.add_vertex(pkg.identifier)
        if pkg.identifier not in self._package_versions:
            self._package_versions[pkg.identifier] = {}
        self._package_versions[pkg.identifier][pkg.version] = pkg
        try:
            self.add_dependencies(pkg)
            #check_requirements is now called in pkg.initialize()
            #pkg.check_requirements()
            self._registry.initialize_package(pkg)
            # FIXME Empty packages still need to be added, but currently they are not
            # because newPackage is typically only called for the first module inside
            # a package.
            from core.modules.abstraction import identifier as abstraction_identifier
            if pkg.identifier == abstraction_identifier:
                self._registry.signals.emit_new_package(abstraction_identifier, True)
        except Exception, e:
            del self._package_versions[pkg.identifier][pkg.version]
            if len(self._package_versions[pkg.identifier]) == 0:
                del self._package_versions[pkg.identifier]
            self._dependency_graph.delete_vertex(pkg.identifier)
            # invert self.add_package
            del self._package_list[package_codepath]
            # if we adding the package to the registry, make sure we
            # remove it if initialization fails
            try:
                self._registry.remove_package(pkg)
            except MissingPackage:
                pass
            raise e
        self.add_menu_items(pkg)

    def late_disable_package(self, package_codepath):
        """late_disable_package disables a package 'late', that is,
        after VisTrails initialization. All reverse dependencies need to be
        already disabled.
        """
        pkg = self.get_package_by_codepath(package_codepath)
        self.remove_package(package_codepath)
        pkg.remove_own_dom_element()

    def reload_package_disable(self, package_codepath):
        # for all reverse dependencies, disable them
        prefix_dictionary = {}
        pkg = self.get_package_by_codepath(package_codepath)
        reverse_deps = []
        for dep_id in self.all_reverse_dependencies(pkg.identifier):
            reverse_deps.append(self.get_package(dep_id))

        for dep_pkg in reverse_deps:
            prefix_dictionary[dep_pkg.codepath] = dep_pkg.prefix
            self.late_disable_package(dep_pkg.codepath)

        # Queue the re-enabling of the packages so event loop can free
        # any QObjects whose deleteLater() method is invoked
        app = get_vistrails_application()
        app.send_notification("pm_reloading_package", package_codepath,
                              reverse_deps, prefix_dictionary)
        # self.emit(self.reloading_package_signal,
        #           package_codepath,
        #           reverse_deps,
        #           prefix_dictionary)

    def reload_package_enable(self, reverse_deps, prefix_dictionary):
        # for all reverse dependencies, enable them
        for dep_pkg in reversed(reverse_deps):
            self.late_enable_package(dep_pkg.codepath, prefix_dictionary)

    def initialize_packages(self,prefix_dictionary={}):
        """initialize_packages(prefix_dictionary={}): None

        Initializes all installed packages. If prefix_dictionary is
        not {}, then it should be a dictionary from package names to
        the prefix such that prefix + package_name is a valid python
        import."""

        packages = self.import_packages_module()
        userpackages = self.import_user_packages_module()

        failed = []
        # import the modules
        existing_paths = set(sys.modules.iterkeys())
        for package in self._package_list.itervalues():
            # print '+ initializing', package.codepath, id(package)
            if package.initialized():
                # print '- already initialized'
                continue
            try:
                package.load(prefix_dictionary.get(package.codepath, None),
                             existing_paths)
            except Package.LoadFailed, e:
                debug.critical("Will disable package %s" % package.name)
                debug.critical(str(e))
                # print "FAILED TO LOAD, let's disable it"
                # We disable the package manually to skip over things
                # we know will not be necessary - the only thing needed is
                # the reference in the package list
                package.remove_own_dom_element()
                failed.append(package)
            except Package.InitializationFailed, e:
                debug.critical("Will disable package <codepath %s>" % package.codepath)
                debug.critical(str(e))
                # print "FAILED TO LOAD, let's disable it"
                # We disable the package manually to skip over things
                # we know will not be necessary - the only thing needed is
                # the reference in the package list
                package.remove_own_dom_element()
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
                                                      package_codepath))
                else:
                    debug.warning('Duplicate package identifier: %s' % \
                                      package.identifier)
                self._package_versions[package.identifier][package.version] = \
                    package

        for pkg in failed:
            del self._package_list[pkg.codepath]
        failed = []

        # determine dependencies
        for package in self._package_list.itervalues():
            try:
                self.add_dependencies(package)
            except Package.MissingDependency, e:
                debug.critical("Will disable package %s" % package.name)
                debug.critical(str(e))
                # print "DEPENDENCIES FAILED TO LOAD, let's disable this"
                package.remove_own_dom_element()
                self._dependency_graph.delete_vertex(package.identifier)
                del self._package_versions[package.identifier][package.version]
                if len(self._package_versions[package.identifier]) == 0:
                    del self._package_versions[package.identifier]
                failed.append(package)

        for pkg in failed:
            del self._package_list[pkg.codepath]

        # perform actual initialization
        try:
            g = self._dependency_graph.inverse_immutable()
            sorted_packages = g.vertices_topological_sort()
        except core.data_structures.graph.Graph.GraphContainsCycles, e:
            raise self.DependencyCycle(e.back_edge[0],
                                       e.back_edge[1])

        for name in sorted_packages:
            pkg = self.get_package(name)
            if not pkg.initialized():
                #check_requirements is now called in pkg.initialize()
                #pkg.check_requirements()
                try:
                    self._registry.initialize_package(pkg)
                except Package.InitializationFailed, e:
                    debug.critical("Package initialization failed <codepath %s>" % pkg.codepath)
                    debug.critical("Will disable package <codepath %s>" % pkg.codepath)
                    debug.critical(str(e))
                    # print "FAILED TO LOAD, let's disable it"
                    # We disable the package manually to skip over things
                    # we know will not be necessary - the only thing needed is
                    # the reference in the package list
                    self.late_disable_package(pkg.codepath)
#                     pkg.remove_own_dom_element()
#                     failed.append(package)
                else:
                    pkg.remove_py_deps(existing_paths)
                    existing_paths.update(pkg.get_py_deps())
                    self.add_menu_items(pkg)

    def add_menu_items(self, pkg):
        """add_menu_items(pkg: Package) -> None
        If the package implemented the function menu_items(),
        the package manager will emit a signal with the menu items to
        be added to the builder window """
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
        """remove_menu_items(pkg: Package) -> None
        Send a signal with the pkg identifier. The builder window should
        catch this signal and remove the package menu items"""
        if pkg.menu_items():
            app = get_vistrails_application()
            app.send_notification("pm_remove_package_menu",
                                   pkg.identifier)
            # self.emit(self.remove_package_menu_signal,
            #           pkg.identifier)

    def show_error_message(self, pkg, msg):
        """show_error_message(pkg: Package, msg: str) -> None
        Print a message to standard error output and emit a signal to the
        builder so if it is possible, a message box is also shown """

        debug.critical("Package %s (%s) says: %s"%(pkg.name,
                                                   pkg.identifier,
                                                   msg))
        app = get_vistrails_application()
        app.send_notification("pm_package_error_message", pkg.identifier,
                              pkg.name, msg)
        # self.emit(self.package_error_message_signal,
        #           pkg.identifier,
        #           pkg.name,
        #           msg)

    def enabled_package_list(self):
        """package_list() -> returns list of all enabled packages."""
        return self._package_list.values()

    def identifier_is_available(self, identifier):
        """identifier_is_available(identifier: str) -> Pkg

        returns true if there exists a package with the given
        identifier in the list of available (ie, disabled) packages.

        If true, returns succesfully loaded, uninitialized package."""
        for codepath in self.available_package_names_list():
            try:
                pkg = self.get_package_by_codepath(codepath)
            except self.MissingPackage:
                pkg = self.look_at_available_package(codepath)
            try:
                pkg.load()
                if pkg.identifier == identifier:
                    return pkg
            except pkg.LoadFailed:
                pass
            except pkg.InitializationFailed:
                pass
            except Exception, e:
                pass
        return None

    def available_package_names_list(self):
        """available_package_names_list() -> returns list with code-paths of all
        available packages, by looking at the appropriate directories.

        The distinction between package names, identifiers and
        code-paths is described in doc/package_system.txt
        """

        lst = []

        def is_vistrails_package(path):
            return ((path.endswith('.py') and
                     not path.endswith('__init__.py') and
                     os.path.isfile(path)) or
                    os.path.isdir(path) and \
                        os.path.isfile(os.path.join(path, '__init__.py')))

        def visit(_, dirname, names):
            for name in names:
                if is_vistrails_package(os.path.join(dirname, name)):
                    if name.endswith('.py'):
                        name = name[:-3]
                    lst.append(name)
            # We want a shallow walk, so we prune the names list
            del names[:]

        # Finds standard packages
        packages = self.import_packages_module()
        os.path.walk(os.path.dirname(packages.__file__), visit, None)
        userpackages = self.import_user_packages_module()
        os.path.walk(os.path.dirname(userpackages.__file__), visit, None)

        return lst

    def dependency_graph(self):
        """dependency_graph() -> Graph.  Returns a graph with package
        dependencies, where u -> v if u depends on v.  Vertices are
        strings representing package names."""
        return self._dependency_graph

    def can_be_disabled(self, identifier):
        """Returns whether has no reverse dependencies (other
        packages that depend on it."""
        return self._dependency_graph.in_degree(identifier) == 0

    def reverse_dependencies(self, identifier):
        lst = [x[0] for x in
               self._dependency_graph.inverse_adjacency_list[identifier]]
        return lst

    # use this call if we're not necessarily loading
    def build_dependency_graph(self, pkg_identifiers):
        dep_graph = core.data_structures.graph.Graph()

        def process_dependencies(identifier):
            dep_graph.add_vertex(identifier)
            pkg = self.identifier_is_available(identifier)
            if pkg:
                deps = pkg.dependencies()
                for dep in deps:
                    if type(dep) == tuple:
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
        except core.data_structures.graph.Graph.GraphContainsCycles, e:
            raise self.DependencyCycle(e.back_edge[0],
                                       e.back_edge[1])
        return sorted_packages
        
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
    global _package_manager
    if not _package_manager:
        raise VistrailsInternalError("package manager not constructed yet.")
    return _package_manager

##############################################################################
