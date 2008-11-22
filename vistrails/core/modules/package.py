###########################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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

from core.utils.uxml import (named_elements, enter_named_element)
from core import debug
from core.configuration import ConfigurationObject
from db.domain import DBPackage
import copy
import traceback
from PyQt4 import QtCore

##############################################################################

class Package(DBPackage):
    Base, User, Other = 0, 1, 2

    class InitializationFailed(Exception):
        def __init__(self, package, exception, traceback):
            self.package = package
            self.exception = exception
            self.traceback = traceback
        def __str__(self):
            try:
                name = self.package.name
            except AttributeError:
                name = 'codepath <%s>' % self.package.codepath
            return ("Package '%s' failed to initialize, raising '%s: %s'. Traceback:\n%s" %
                    (name,
                     self.exception.__class__.__name__,
                     self.exception,
                     self.traceback))

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
            return ("Package '%s' has unmet dependencies: %s" %
                    (self.package.name,
                     self.dependencies))

    def __init__(self, *args, **kwargs):
        if 'load_configuration' in kwargs:
            arg = kwargs['load_configuration']
            if type(arg) == type(1):
                if type(arg) == type(True):
                    kwargs['load_configuration'] = 1 if arg else 0
                else:
                    raise VistrailsInternalError("Cannot convert "
                                                 "load_configuration")

        DBPackage.__init__(self, *args, **kwargs)
        self.descriptors = self.db_module_descriptors_name_index
        self.descriptors_by_id = self.db_module_descriptors_id_index

        self._module = None
        self._initialized = False
    
    def __copy__(self):
        Package.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPackage.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Package
        cp.descriptors = cp.db_module_descriptors_name_index
        cp.descriptors_by_id = cp.db_module_descriptors_id_index

        cp._module = self._module
        cp._initialized = self._initialized

    @staticmethod
    def convert(_package):
        if _package.__class__ == Package:
            return
        _package.__class__ = Package

        _package.descriptors = _package.db_module_descriptors_name_index
        _package.descriptors_by_id = _package.db_module_descriptors_id_index

        _package._module = None
        _package._initialized = False

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
    def delete_descriptor(self, desc):
        self.db_delete_module_descriptor(desc)

    def _get_module(self):
        return self._module
    module = property(_get_module)

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
    # Methods
    
    def load(self, module=None):
        """load(module=None). Loads package's module. If module is not None,
        then uses that as the module instead of 'import'ing it.

        If package is already initialized, this is a NOP.

        """

        errors = []
        def module_import(name):
            return

        if self._initialized:
            return
        if module is not None:
            self._module = module
            self._package_type = self.Other
            self.set_properties()
            return
        def import_from(prefix):
            try:
                self._module = getattr(__import__(prefix+self.codepath,
                                                  globals(),
                                                  locals(), []),
                                       self.codepath)
                self._package_type = self.Base
            except ImportError, e:
                errors.append((e, traceback.format_exc()))
                return False
            return True

        try:
            r = (not import_from('packages.') and
                 not import_from('userpackages.'))
        except Exception, e:
            raise self.LoadFailed(self, e, traceback.format_exc())
            
        if r:
            dbg = debug.DebugPrint
            dbg.critical("Could not enable package %s" % self.codepath)
            for e in errors:
                dbg.critical("Exceptions/tracebacks raised:")
                dbg.critical(str(e[0]))
                dbg.critical(str(e[1]))
            raise self.InitializationFailed(self,
                                            e[-1][0], e[-1][1])

        # Sometimes we don't want to change startup.xml, for example
        # when peeking at a package that's on the available package list
        # on edit -> preferences. That's what the load_configuration field
        # is for
        if self.load_configuration:
            if hasattr(self._module, 'configuration'):
                # hold a copy of the initial configuration so it can be reset
                self._initial_configuration = \
                    copy.copy(self._module.configuration)
            self.load_persistent_configuration()
            self.create_startup_package_node()

        self.set_properties()

    def set_properties(self):
        # Set properties
        try:
            self.name = self._module.name
            self.identifier = self._module.identifier
            self.version = self._module.version
        except AttributeError, e:
            try:
                v = self._module.__file__
            except AttributeError:
                v = self._module
            debug.DebugPrint.critical("Package %s is missing necessary "
                                      "attribute" % v)
            raise e
        if hasattr(self._module, '__doc__') and self._module.__doc__:
            self.description = self._module.__doc__
        else:
            self.description = "No description available"
            
    def report_missing_module(self, module_name, module_namespace):
        """report_missing_module(name, namespace):

        Calls the package's module handle_missing_module function, if
        present, to allow the package to dynamically add a missing
        module.
        """
        try:
            handle = self._module.handle_missing_module
        except AttributeError:
            return False
        try:
            return handle(module_name, module_namespace)
        except Exception, e:
            debug.DebugPrint.critical("Call to handle_missing_module in package '%s'"
                                      " raised exception '%s'. Assuming package could not"
                                      " handle call" % (self.name,
                                                        str(e)))
        return False

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
            return callable_()

    def finalize(self):
        if not self._initialized:
            return
        print "Finalizing",self.name
        try:
            callable_ = self._module.finalize
        except AttributeError:
            pass
        else:
            callable_()
        # Save configuration
        if self.configuration:
            self.set_persistent_configuration()
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

    ##########################################################################
    # Configuration

    def find_disabledpackage_element(self, doc):
        """find_disabledpackage_element(documentElement) -> Node or None

        Returns the package's disabledpackage element, if
        present. Returns None otherwise.

        """
        packages = enter_named_element(doc, 'disabledpackages')
        assert packages
        for package_node in named_elements(packages, 'package'):
            if str(package_node.attributes['name'].value) == self.codepath:
                return package_node
        return None

    def remove_own_dom_element(self):
        """remove_own_dom_element() -> None

        Opens the startup DOM, looks for the element that belongs to the package.
        If it is there and there's a configuration, moves it to disabledpackages
        node. This is done as part of package disable.

        """
        from PyQt4 import QtCore
        startup = QtCore.QCoreApplication.instance().vistrailsStartup
        dom = startup.startup_dom()
        doc = dom.documentElement

        def find_it():
            packages = enter_named_element(doc, 'packages')
            for package_node in named_elements(packages, 'package'):
                if str(package_node.attributes['name'].value) == self.codepath:
                    return package_node

        package_node = find_it()
        oldpackage_element = self.find_disabledpackage_element(doc)

        assert oldpackage_element is None
        packages = enter_named_element(doc, 'packages')
        disabledpackages = enter_named_element(doc, 'disabledpackages')
        packages.removeChild(package_node)
        disabledpackages.appendChild(package_node)
        startup.write_startup_dom(dom)

    def reset_configuration(self):
        """Reset_configuration() -> Resets configuration to original
        package settings."""

        (dom, element) = self.find_own_dom_element()
        doc = dom.documentElement
        configuration = enter_named_element(element, 'configuration')
        if configuration:
            element.removeChild(configuration)
        self.configuration = copy.copy(self._initial_configuration)

        from PyQt4 import QtCore
        startup = QtCore.QCoreApplication.instance().vistrailsStartup
        startup.write_startup_dom(dom)

    def find_own_dom_element(self):
        """find_own_dom_element() -> (DOM, Node)

        Opens the startup DOM, looks for the element that belongs to the package,
        and returns DOM and node. Creates a new one if element is not there.

        """
        from PyQt4 import QtCore
        dom = QtCore.QCoreApplication.instance().vistrailsStartup.startup_dom()
        doc = dom.documentElement
        packages = enter_named_element(doc, 'packages')
        for package_node in named_elements(packages, 'package'):
            if str(package_node.attributes['name'].value) == self.codepath:
                return (dom, package_node)

        # didn't find anything, create a new node

        package_node = dom.createElement("package")
        package_node.setAttribute('name', self.codepath)
        packages.appendChild(package_node)

        from PyQt4 import QtCore
        QtCore.QCoreApplication.instance().vistrailsStartup.write_startup_dom(dom)
        return (dom, package_node)

    def load_persistent_configuration(self):
        (dom, element) = self.find_own_dom_element()

        configuration = enter_named_element(element, 'configuration')
        if configuration:
            self.configuration.set_from_dom_node(configuration)
        dom.unlink()

    def set_persistent_configuration(self):
        (dom, element) = self.find_own_dom_element()
        child = enter_named_element(element, 'configuration')
        if child:
            element.removeChild(child)
        self.configuration.write_to_dom(dom, element)
        from PyQt4 import QtCore
        QtCore.QCoreApplication.instance().vistrailsStartup.write_startup_dom(dom)
        dom.unlink()

    def create_startup_package_node(self):
        (dom, element) = self.find_own_dom_element()
        doc = dom.documentElement
        disabledpackages = enter_named_element(doc, 'disabledpackages')
        packages = enter_named_element(doc, 'packages')

        oldpackage = self.find_disabledpackage_element(doc)

        if oldpackage is not None:
            # Must remove element from oldpackages,
            # _and_ the element that was just created in find_own_dom_element()
            disabledpackages.removeChild(oldpackage)
            packages.removeChild(element)
            packages.appendChild(oldpackage)
            configuration = enter_named_element(oldpackage, 'configuration')
            if configuration:
                self.configuration.set_from_dom_node(configuration)
            from PyQt4 import QtCore
            QtCore.QCoreApplication.instance().vistrailsStartup.write_startup_dom(dom)
        dom.unlink()

