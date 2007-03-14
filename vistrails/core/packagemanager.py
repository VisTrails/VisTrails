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

    def load_existing_module(self, module):
        """Loads an already imported module. Useful for getting a package
from places other than packages or userpackages."""
        self._module = module
        self._package_type = self.Other

    def load(self):
        def import_from_base():
            try:
                self._module = getattr(__import__('packages.'+self.name,
                                                  globals(),
                                                  locals(), []),
                                       self.name)
                self._package_type = self.Base
            except ImportError:
                return False
            return True
        def import_from_user():
            try:
                self._module = getattr(__import__('userpackages.'+self.name,
                                                  globals(),
                                                  locals(), []),
                                       self.name)
                self._package_type = self.User
            except ImportError:
                return False
            return True

        if (not import_from_base() and
            not import_from_user()):
            dbg = debug.DebugPrint
            dbg.critical("Could not install package %s" % self._name)
            raise ImportError("Package %s not present" % self._name)

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
        self._dependency_graph.addVertex(packageName)

    def has_package(self, name):
        """has_package(name: string) -> Boolean.
Returns true if given package is installed."""
        return self._package_list.has_key(name)

    def get_package(self, name):
        """get_package(name: string) -> Package.
Returns a package with given name if it exists, otherwise throws exception"""
        if not self.has_package(name):
            raise self.MissingPackage(name)
        else:
            return self._package_list[name]

    def add_dependencies(self, package):
        """add_dependencies(package) -> None.  Register all
dependencies a package contains by calling the appropriate callback."""
        deps = package.dependencies()
        missing_packages = [name
                            for name in deps
                            if name not in self._dependency_graph.vertices]
        if len(missing_packages):
            raise ImportError("Package '%s' has unmet dependencies: %s" %
                              (package.name,
                               missing_packages))
        for name in deps:
            self._dependency_graph.addEdge(package.name, name)

    def initialize_packages(self,package_dictionary={}):
        """initialize_packages(package_dictionary={}): None

        Initializes all installed packages. If module_dictionary is
not {}, then it should be a dictionary from package names to preloaded
package-like objects (in theory they have to be modules that respect
the correct interface, but nothing actually prevents anyone from
creating a class that behaves similarly)."""
        # Imports standard packages directory
        conf = self._configuration
        old_sys_path = sys.path
        if conf.packageDirectory:
            sys.path.append(conf.packageDirectory)
        import packages
        sys.path = old_sys_path

        try:
            old_sys_path = sys.path
            sys.path.append(conf.userPackageDirectory
                            + '/'
                            + os.path.pardir)
            import userpackages
        finally:
            sys.path = old_sys_path

        # import the modules
        for package in self._package_list.itervalues():
            if not package.initialized():
                if package.name in package_dictionary:
                    mod = package_dictionary[package.name]
                    package.load_existing_module(mod)
                else:
                    package.load()

        # determine dependencies
        for package in self._package_list.itervalues():
            if not package.initialized():
                self.add_dependencies(package)
            
        # perform actual initialization
        try:
            g = self._dependency_graph.inverse_immutable()
            sorted_packages = g.vertices_topological_sort()
        except core.data_structures.Graph.GraphContainsCycles, e:
            raise self.DependencyCycle(e.back_edge[0],
                                       e.back_edge[1])
        for name in sorted_packages:
            package = self._package_list[name]
            if not package.initialized():
                package.check_requirements()
                package.initialize()

def get_package_manager():
    global _package_manager
    if not _package_manager:
        raise VistrailsInternalError("package manager not constructed yet.")
    return _package_manager
        
##############################################################################
            
