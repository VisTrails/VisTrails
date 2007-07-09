############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

"""The package manager takes care of everything that has got to do
with handling packages, from setting paths to adding new packages
to checking dependencies to initializing them."""

from core import debug
from core.modules.module_registry import registry
from core.utils import VistrailsInternalError
from core.configuration import ConfigurationObject
import copy
import core.data_structures.graph
import os
import sys

##############################################################################

class Package(object):

    Base, User, Other = 0, 1, 2

    class InitializationFailed(Exception):
        def __init__(self, package, exception):
            self.package = package
            self.exception = exception
        def __str__(self):
            return ("Package '%s' failed to initialize, raising '%s'" %
                    (self.package.name,
                     self.exception))

    def __init__(self, packageName, args, keywords):
        self._name = packageName
        self._args = args
        self._kwargs = keywords
        self._module = None
        self._initialized = False

    def load(self, module=None):
        """load(module=None). Loads package's module. If module is not None,
        then uses that as the module instead of 'import'ing it.

        If package is already initialized, this is a NOP.

        """
        
        class InternalImportError(ImportError):
            def __init__(self, import_error):
                self.import_error = import_error
        
        def module_import(name):
            return 
            
        if self._initialized:
            return
        if module is not None:
            self._module = module
            self._package_type = self.Other
            return
        def import_from(prefix):
            try:
                self._module = getattr(__import__(prefix+self.name,
                                                  globals(),
                                                  locals(), []),
                                       self.name)
                self._package_type = self.Base
            except InternalImportError, e:
                raise e.import_error
            except ImportError:
                return False
            return True

        if (not import_from('packages.') and
            not import_from('userpackages.')):
            dbg = debug.DebugPrint
            dbg.critical("Could not enable package %s" % self._name)
            raise ImportError("Package %s not present "
                              "(or one of its imports failed)" % self._name)

    def initialize(self):
        if self._initialized:
            return
        print "Initializing", self._name
        registry.setCurrentPackageName(self._name)
        try:
            self._module.initialize(*self._args, **self._kwargs)
        except Exception, e:
            raise self.InitializationFailed(self, e)
        registry.setCurrentPackageName(None)
        self._initialized = True

    def check_requirements(self):
        try:
            callable_ = self._module.package_requirements
        except AttributeError:
            return
        else:
            callable_()
    
    def finalize(self):
        if not self._initialized:
            return
        try:
            callable_ = self._module.finalize
        except AttributeError:
            pass
        else:
            callable_()
            self._initialized = False
            
    def dependencies(self):
        try:
            callable_ = self._module.package_dependencies
        except AttributeError:
            return []
        else:
            return callable_()

    def initialized(self):
        return self._initialized

    def _get_name(self):
        return self._name
    name = property(_get_name)

    def _get_module(self):
        return self._module

    module = property(_get_module)

    def _get_configuration(self):
        if hasattr(self._module, 'configuration'):
            return self._module.configuration
        else:
            return None
    configuration = property(_get_configuration)

    def _get_description(self):
        if hasattr(self._module, '__doc__'):
            return self._module.__doc__ or "No description available"
        else:
            return "No description available"
    description = property(_get_description)

##############################################################################

global _package_manager
_package_manager = None

class PackageManager(object):

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
        # Imports standard packages directory
        conf = self._configuration
        old_sys_path = sys.path
        if conf.check('packageDirectory'):
            sys.path.append(conf.packageDirectory)
        try:
            import packages
        finally:
            sys.path = old_sys_path
        return packages


    def import_user_packages_module(self):
        """Imports the packages module using path trickery to find it
        in the right place.

        """
        # Imports user packages directory
        conf = self._configuration
        old_sys_path = sys.path
        if conf.check('userPackageDirectory'):
            sys.path.append(conf.userPackageDirectory + '/' + os.path.pardir)
        try:
            import userpackages
        finally:
            sys.path = old_sys_path
        return userpackages
        

    def __init__(self, configuration):
        global _package_manager
        if _package_manager:
            m = "Package manager can only be constructed once."
            raise VistrailsInternalError(m)
        _package_manager = self
        self._configuration = configuration
        self._package_list = {}
        self._dependency_graph = core.data_structures.graph.Graph()

    def finalize_packages(self):
        """Finalizes all installed packages. Call this only prior to
exiting VisTrails."""
        for package in self._package_list.itervalues():
            print "Finalizing",package.name
            package.finalize()
        self._package_list = {}

    def add_package(self, packageName, args=[], keywords={}):
        """Adds a new package to the manager. This does not initialize it.
To do so, call initialize_packages()"""
        self._package_list[packageName] = Package(packageName, args, keywords)
        if self._dependency_graph.vertices.has_key('packageName'):
            raise VistrailsInternalError('duplicate package name')
        self._dependency_graph.add_vertex(packageName)

    def remove_package(self, name):
        """remove_package(name): Removes a package from the system."""
        pkg = self._package_list[name]
        self._dependency_graph.remove_vertex(name)
        pkg.finalize()
        del self._package_list[name]

    def has_package(self, name):
        """has_package(name: string) -> Boolean.
Returns true if given package is installed."""
        return self._package_list.has_key(name)

    def look_at_available_package(self, name):
        """look_at_available_package(name: string) -> Package

        Returns a Package object for an uninstalled package. This does
        NOT install a package.
        """
        return Package(name, [], {})

    def get_package(self, name):
        """get_package(name: string) -> Package.
Returns a package with given name if it is enabled, otherwise throws exception
        """
        if not self.has_package(name):
            raise self.MissingPackage(name)
        else:
            return self._package_list[name]

    def get_package_configuration(self, name):
        """get_package_configuration(name: string) ->
        ConfigurationObject or None
        
        Returns the configuration object for the package, if existing,
        or None. Throws MissingPackage if package doesn't exist.
        """

        pkg = self.get_package(name)

        if not hasattr(pkg.module, 'configuration'):
            return None
        else:
            c = pkg.module.configuration
            if not isinstance(c, ConfigurationObject):
                d = "'configuration' attribute should be a ConfigurationObject"
                raise self.PackageInternalError(name, d)
            return c

    def add_dependencies(self, package):
        """add_dependencies(package) -> None.  Register all
dependencies a package contains by calling the appropriate callback.

        Does not add multiple dependencies.
        """
        deps = package.dependencies()
        missing_packages = [name
                            for name in deps
                            if name not in self._dependency_graph.vertices]
        if len(missing_packages):
            raise ImportError("Package '%s' has unmet dependencies: %s" %
                              (package.name,
                               missing_packages))
        
        for name in deps:
            if name not in self._dependency_graph.adjacency_list:
                self._dependency_graph.add_edge(package.name, name)

    def late_enable_package(self, package_name):
        """late_enable_package enables a package 'late', that is,
        after VisTrails initialization. All dependencies need to be
        already enabled.
        """

        self.add_package(package_name)
        pkg = self.get_package(package_name)
        pkg.load()
        pkg.check_requirements()
        pkg.initialize()

    def initialize_packages(self,package_dictionary={}):
        """initialize_packages(package_dictionary={}): None

        Initializes all installed packages. If module_dictionary is
not {}, then it should be a dictionary from package names to preloaded
package-like objects (in theory they have to be modules that respect
the correct interface, but nothing actually prevents anyone from
creating a class that behaves similarly)."""
        packages = self.import_packages_module()
        userpackages = self.import_user_packages_module()

        # import the modules
        for package in self._package_list.itervalues():
            package.load(package_dictionary.get(package.name, None))

        # determine dependencies
        for package in self._package_list.itervalues():
            self.add_dependencies(package)
            
        # perform actual initialization
        try:
            g = self._dependency_graph.inverse_immutable()
            sorted_packages = g.vertices_topological_sort()
        except core.data_structures.Graph.GraphContainsCycles, e:
            raise self.DependencyCycle(e.back_edge[0],
                                       e.back_edge[1])
        
        for name in sorted_packages:
            pkg = self._package_list[name]
            if not pkg.initialized():
                pkg.check_requirements()
                pkg.initialize()

    def enabled_package_list(self):
        """package_list() -> returns list of all enabled packages."""
        return self._package_list.values()

    def available_package_names_list(self):
        """available_package_names_list() -> returns list of all
        available packages, by looking at the appropriate directories."""
        
        lst = []

        def is_vistrails_package(path):
            return ((path.endswith('.py') and
                     not path.endswith('__init__.py') and
                     os.path.isfile(path)) or
                    os.path.isdir(path) and os.path.isfile(path + '/__init__.py'))

        def visit(_, dirname, names):
            for name in names:
                if is_vistrails_package(dirname + '/' + name):
                    if name.endswith('.py'):
                        name = name[:-3]
                    lst.append(name)
            # We want a shallow walk, so we prune the names list
            del names[:]

        # Finds standard packages
        import packages
        os.path.walk(os.path.dirname(packages.__file__), visit, None)
        import userpackages
        os.path.walk(os.path.dirname(userpackages.__file__), visit, None)

        return lst

    def dependency_graph(self):
        """dependency_graph() -> Graph.  Returns a graph with package
        dependencies, where u -> v if u depends on v.  Vertices are
        strings representing package names."""
        return self._dependency_graph

def get_package_manager():
    global _package_manager
    if not _package_manager:
        raise VistrailsInternalError("package manager not constructed yet.")
    return _package_manager
        
##############################################################################
            
