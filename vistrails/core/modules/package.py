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

import __builtin__
import copy
import os
import sys
import traceback
import xml.dom

from core import debug
from core import get_vistrails_application
from core.configuration import ConfigurationObject, get_vistrails_configuration
from core.modules.module_descriptor import ModuleDescriptor
from core.utils import versions_increasing
from core.utils.uxml import (named_elements, enter_named_element)

from db.domain import DBPackage

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
                if name is None:
                    name = 'codepath <%s>' % self.package.codepath
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
            if type(arg) != type(1):
                if type(arg) == type(True):
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
    
    def __copy__(self):
        Package.do_copy(self)

    def set_defaults(self, other=None):
        self.setup_indices()
        if other is None:
            self._module = None
            self._init_module = None
            self._initialized = False
            self._abs_pkg_upgrades = {}
            self.package_dir = None
            self.prefix = None
            self.py_dependencies = set()
        else:
            self._module = other._module
            self._init_module = other._init_module
            self._initialized = other._initialized
            self._abs_pkg_upgrades = copy.copy(other._abs_pkg_upgrades)
            self.package_dir = other.package_dir
            self.prefix = other.prefix
            self.py_dependencies = copy.copy(other.py_dependencies)
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
    
    def _override_import(self, existing_paths=None):
        self._real_import = __builtin__.__import__
        self._imported_paths = set()
        if existing_paths is not None:
            self._existing_paths = existing_paths
        else:
            self._existing_paths = set(sys.modules.iterkeys())
        __builtin__.__import__ = self._import
        
    def _reset_import(self):
        __builtin__.__import__ = self._real_import
        return self._imported_paths

    def _import(self, name, globals=None, locals=None, fromlist=None, level=-1):
        # if name != 'core.modules.module_registry':
        #     print 'running import', name, fromlist
        res = apply(self._real_import, 
                    (name, globals, locals, fromlist, level))
        if len(name) > len(res.__name__):
            res_name = name
        else:
            res_name = res.__name__
        qual_name = ''
        for m in res_name.split('.'):
            qual_name += m
            if qual_name not in self._existing_paths and \
                    not qual_name.endswith('_rc'):
                # print '  adding', name, qual_name
                self._imported_paths.add(qual_name)
            # else:
            #     if name != 'core.modules.module_registry':
            #         print '  already exists', name, res.__name__
	    qual_name += '.'
        if fromlist is not None:
            for from_module in fromlist:
                qual_name = res_name + '.' + from_module
                if qual_name not in self._existing_paths and \
                        not qual_name.endswith('_rc'):
                    # print '  adding222', name, qual_name
                    self._imported_paths.add(qual_name)

        return res

    def get_py_deps(self):
        return self.py_dependencies

    def remove_py_deps(self, deps):
        self.py_dependencies.difference_update(deps)

    def load(self, prefix=None, existing_paths=None):
        """load(module=None). Loads package's module. If module is not None,
        then uses that as the module instead of 'import'ing it.

        If package is already initialized, this is a NOP.

        """

        errors = []
        if self._initialized:
            # print 'initialized'
            return

        def import_from(p_path):
            # print 'running import_from'
            try:
                # print p_path + self.codepath
                module = __import__(p_path+self.codepath,
                                    globals(),
                                    locals(), []),
                self._module = sys.modules[p_path + self.codepath]
                self._imported_paths.add(p_path + self.codepath)
                self._package_type = self.Base
                self.prefix = p_path
            except ImportError, e:
                errors.append((e, traceback.format_exc()))
                return False
            return True

        try:
            # override __import__ so that we can track what needs to
            # be unloaded, try imports, and then stop overriding,
            # updating the set of python dependencies
            self._override_import(existing_paths)
            if self.prefix is not None:
                r = not import_from(self.prefix)
            elif prefix is not None:
                r = not import_from(prefix)
            else:
                r = (not import_from('packages.') and
                     not import_from('userpackages.'))
        except Exception, e:
            raise self.LoadFailed(self, e, traceback.format_exc())
        finally:
            self.py_dependencies.update(self._reset_import())
            
        if r:
            debug.critical("Could not enable package %s" % self.codepath)
            for e in errors:
                debug.critical("Exceptions/tracebacks raised:")
                debug.critical(str(e[0]))
                debug.critical(str(e[1]))
            raise self.InitializationFailed(self,
                                            errors[-1][0], errors[-1][1])

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

    def initialize(self, existing_paths=None):
        self._override_import(existing_paths)
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
                self._imported_paths.add(name)
                # Copy attributes (shallow) from _module into _init_module's namespace and point _module to _init_module
                module_attributes = ['identifier', 'name', 'version',
                                     'configuration', 'package_dependencies',
                                     'package_requirements',
                                     'can_handle_identifier',
                                     'can_handle_vt_file']
                for attr in module_attributes:
                    if hasattr(self._module, attr):
                        setattr(self._init_module, attr, getattr(self._module, attr))
                self._module = self._init_module
            
            self.check_requirements()
            if hasattr(self._init_module, 'initialize'):
                # override __import__ so that we can track what needs to
                # be unloaded, try imports, and then stop overriding,
                # updating the set of python dependencies
                self._init_module.initialize()
        except Exception:
            self.py_dependencies.update(self._reset_import())            
            self.unload()
            raise
        else:
            self.py_dependencies.update(self._reset_import())
        
    def unload(self):
        for path in self.py_dependencies:
            if path not in sys.modules:
                # print "skipping %s"%path
                pass
            else:
                # print 'deleting path:', path, path in sys.modules
                del sys.modules[path]
        self.py_dependencies.clear()

    def set_properties(self):
        # Set properties
        try:
            self.name = self._module.name
            self.identifier = self._module.identifier
            self.version = self._module.version
            self.package_dir = os.path.dirname(self._module.__file__)
        except AttributeError, e:
            try:
                v = self._module.__file__
            except AttributeError:
                v = self._module
            debug.critical("Package %s is missing necessary attribute" % v)
            raise e
        if hasattr(self._module, '__doc__') and self._module.__doc__:
            self.description = self._module.__doc__
        else:
            self.description = "No description available"
            
    def can_handle_all_errors(self):
        return hasattr(self._init_module, 'handle_all_errors')

    def can_handle_upgrades(self):
        # redirect webservices to SUDSWebServices
        if self.package.startswith("SUDS#"):
            return True
        return hasattr(self._init_module, 'handle_module_upgrade_request')

    def can_handle_identifier(self, identifier):
        """ Asks package if it can handle this package
        """
        return hasattr(self.init_module, 'can_handle_identifier') and \
            self.init_module.can_handle_identifier(identifier)

    def can_handle_vt_file(self, name):
        """ Asks package if it can handle a file inside a zipped vt file
        """
        return hasattr(self.init_module, 'can_handle_vt_file') and \
            self.init_module.can_handle_vt_file(name)
    
    def can_handle_missing_modules(self):
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            return True
        return hasattr(self._init_module, 'handle_missing_module')

    def handle_all_errors(self, *args, **kwargs):
        return self._init_module.handle_all_errors(*args, **kwargs)

    def handle_module_upgrade_request(self, *args, **kwargs):
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            from core.packagemanager import get_package_manager
            pm = get_package_manager()
            package = pm.get_package_by_identifier('edu.utah.sci.vistrails.sudswebservices')
            return package._init_module.handle_module_upgrade_request(*args, **kwargs)
        return self._init_module.handle_module_upgrade_request(*args, **kwargs)
        
    def handle_missing_module(self, *args, **kwargs):
        """report_missing_module(name, namespace):

        Calls the package's module handle_missing_module function, if
        present, to allow the package to dynamically add a missing
        module.
        """
        
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            from core.packagemanager import get_package_manager
            pm = get_package_manager()
            package = pm.get_package_by_identifier('edu.utah.sci.vistrails.sudswebservices')
            return package._init_module.handle_missing_module(*args, **kwargs)
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
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            return True
        return hasattr(self._init_module, 'contextMenuName')

    def contextMenuName(self, signature):
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            from core.packagemanager import get_package_manager
            pm = get_package_manager()
            package = pm.get_package_by_identifier('edu.utah.sci.vistrails.sudswebservices')
            return package._init_module.contextMenuName(signature)
        return self._init_module.contextMenuName(signature)
    
    def has_callContextMenu(self):
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            return True
        return hasattr(self._init_module, 'callContextMenu')

    def callContextMenu(self, signature):
        # redirect webservices to SUDSWebServices
        if self.identifier.startswith("SUDS#"):
            from core.packagemanager import get_package_manager
            pm = get_package_manager()
            package = pm.get_package_by_identifier('edu.utah.sci.vistrails.sudswebservices')
            return package._init_module.callContextMenu(signature)
        return self._init_module.callContextMenu(signature)

    def loadVistrailFileHook(self, vistrail, tmp_dir):
        if hasattr(self._init_module, 'loadVistrailFileHook'):
            self._init_module.loadVistrailFileHook(vistrail, tmp_dir)

    def saveVistrailFileHook(self, vistrail, tmp_dir):
        if hasattr(self._init_module, 'saveVistrailFileHook'):
            self._init_module.saveVistrailFileHook(vistrail, tmp_dir)

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
        debug.log("Finalizing %s" % self.name)
        try:
            callable_ = self._module.finalize
        except AttributeError:
            pass
        else:
            callable_()
        # Save configuration
        if self.configuration:
            self.set_persistent_configuration()
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
            deps = callable_()

        if self._module is not None and \
                hasattr(self._module, '_dependencies'):
            deps.extend(self._module._dependencies)
        return deps

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
        startup = get_vistrails_application().vistrailsStartup
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
        try:
            packages.removeChild(package_node)
            disabledpackages.appendChild(package_node)
        except xml.dom.NotFoundErr:
            pass
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

        startup = get_vistrails_application().vistrailsStartup
        startup.write_startup_dom(dom)

    def find_own_dom_element(self):
        """find_own_dom_element() -> (DOM, Node)

        Opens the startup DOM, looks for the element that belongs to the package,
        and returns DOM and node. Creates a new one if element is not there.

        """
        dom = get_vistrails_application().vistrailsStartup.startup_dom()
        doc = dom.documentElement
        packages = enter_named_element(doc, 'packages')
        for package_node in named_elements(packages, 'package'):
            if str(package_node.attributes['name'].value) == self.codepath:
                return (dom, package_node)

        # didn't find anything, create a new node

        package_node = dom.createElement("package")
        package_node.setAttribute('name', self.codepath)
        packages.appendChild(package_node)

        get_vistrails_application().vistrailsStartup.write_startup_dom(dom)
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
        get_vistrails_application().vistrailsStartup.write_startup_dom(dom)
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
            get_vistrails_application().vistrailsStartup.write_startup_dom(dom)
        dom.unlink()

