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
from itertools import izip, chain
from ast import literal_eval
import collections
import copy
import os
import tempfile
import traceback
import uuid
import warnings

from vistrails.core import debug, get_vistrails_application
from vistrails.core.data_structures.graph import Graph
import vistrails.core.modules
from vistrails.core.modules.config import ConstantWidgetConfig, \
    ModuleSettings, InputPort, OutputPort, CompoundInputPort, \
    CompoundOutputPort, DeprecatedInputPort
import vistrails.core.modules.vistrails_module
from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.modules.package import Package
from vistrails.core.requirements import MissingRequirement
import vistrails.core.modules.utils
from vistrails.core.utils import VistrailsInternalError, memo_method, \
    InvalidModuleClass, ModuleAlreadyExists, append_to_dict_of_lists, \
    all, profile, versions_increasing, InvalidPipeline, VistrailsDeprecation
from vistrails.core.system import vistrails_root_directory, vistrails_version, \
    get_vistrails_basic_pkg_id
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.core.vistrail.port_spec_item import PortSpecItem
import vistrails.core.cache.hasher
from vistrails.db.domain import DBRegistry

import unittest

##############################################################################

# This is used by add_module to make sure the fringe specifications
# make sense
def _check_fringe(fringe):
    assert isinstance(fringe, list)
    assert len(fringe) >= 1
    for v in fringe:
        assert isinstance(v, tuple)
        assert len(v) == 2
        assert isinstance(v[0], float)
        assert isinstance(v[1], float)

def _toposort_modules(module_list):
    """_toposort_modules([class]) -> [class]

    _toposort_modules takes a list of modules and returns them
    sorted topologically wrt to the subclass relation, such that
    if a and b are both in the list and issubclass(a,b), then a
    will appear before b in the resulting order.
    """

    g = Graph()
    for m in module_list:
        if isinstance(m, tuple):
            g.add_vertex(m[0], m)
        else:
            g.add_vertex(m, m)
    for m in module_list:
        if isinstance(m, tuple):
            m = m[0]
        for subclass in m.mro()[1:]: # skip self
            if subclass in g.vertices:
                g.add_edge(subclass, m)
    return [g.vertices[v] for v in g.vertices_topological_sort()]

def _parse_abstraction_name(filename):
    # assume only 1 possible prefix or suffix
    prefixes = ["abstraction_"]
    suffixes = [".vt", ".xml"]
    name = os.path.basename(filename)
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    return name

def _toposort_abstractions(package, abstraction_list):
    from vistrails.core.modules.sub_module import find_internal_abstraction_refs
    g = Graph()
    for a in abstraction_list:
        if isinstance(a, tuple):
            if isinstance(a[1], dict) and 'name' in a[1]:
                name = (a[1]['name'], a[1].get('namespace', ''))
            else:
                name = (_parse_abstraction_name(a[0]), '')
            g.add_vertex(name, a)
        else:
            g.add_vertex((_parse_abstraction_name(a), ''), a)
    for a in abstraction_list:
        if isinstance(a, tuple):
            a = a[0]
        for ref in find_internal_abstraction_refs(package, a):
            if ref in g.vertices:
                g.add_edge(ref, a)
    return [g.vertices[v] for v in g.vertices_topological_sort()]

###############################################################################
# ModuleRegistrySignals

class ModuleRegistrySignals(object):

    # # new_module_signal is emitted with descriptor of new module
    # new_module_signal = QtCore.SIGNAL("new_module")
    # # new_abstraction_signal is emitted with descriptor of new abstraction
    # new_abstraction_signal = QtCore.SIGNAL("new_abstraction")
    # # new_package_signal is emitted with identifier of new package (only for abstractions)
    # new_package_signal = QtCore.SIGNAL("new_package")
    # # deleted_module_signal is emitted with descriptor of deleted module
    # deleted_module_signal = QtCore.SIGNAL("deleted_module")
    # # deleted_abstraction_signal is emitted with descriptor of deleted abstraction
    # deleted_abstraction_signal = QtCore.SIGNAL("deleted_abstraction")
    # # deleted_package_signal is emitted with package identifier
    # deleted_package_signal = QtCore.SIGNAL("deleted_package")
    # # new_input_port_signal is emitted with identifier and name of module, 
    # # new port and spec
    # new_input_port_signal = QtCore.SIGNAL("new_input_port_signal")
    # # new_output_port_signal is emitted with identifier and name of module,
    # # new port and spec
    # new_output_port_signal = QtCore.SIGNAL("new_output_port_signal")

    # show_module_signal = QtCore.SIGNAL("show_module")
    # hide_module_signal = QtCore.SIGNAL("hide_module")
    # module_updated_signal = QtCore.SIGNAL("module_updated")

    def __init__(self):
        app = get_vistrails_application()
        notifications = ["reg_new_module",
                         "reg_new_abstraction",
                         "reg_new_package",
                         "reg_deleted_module",
                         "reg_deleted_abstraction",
                         "reg_deleted_package",
                         "reg_new_input_port",
                         "reg_new_output_port",
                         "reg_show_module",
                         "reg_hide_module",
                         "reg_module_updated"]

        for notification in notifications:
            app.create_notification(notification)
        
    def emit_new_module(self, descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_new_module", descriptor)
        # self.emit(self.new_module_signal, descriptor)

    def emit_new_abstraction(self, descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_new_abstraction", descriptor)
        # self.emit(self.new_abstraction_signal, descriptor)

    def emit_new_package(self, identifier, prepend=False):
        app = get_vistrails_application()
        app.send_notification("reg_new_package", identifier, prepend)
        # self.emit(self.new_package_signal, identifier, prepend)        
        
    def emit_deleted_module(self, descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_deleted_module", descriptor)
        # self.emit(self.deleted_module_signal, descriptor)

    def emit_deleted_abstraction(self, descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_deleted_abstraction", descriptor)
        # self.emit(self.deleted_abstraction_signal, descriptor)
    
    def emit_deleted_package(self, package):
        app = get_vistrails_application()
        app.send_notification("reg_deleted_package", package)
        # self.emit(self.deleted_package_signal, package)

    def emit_new_input_port(self, identifier, name, port_name, spec):
        app = get_vistrails_application()
        app.send_notification("reg_new_input_port", identifier, name, 
                              port_name, spec)
        # self.emit(self.new_input_port_signal, identifier, name, port_name,
        #           spec)

    def emit_new_output_port(self, identifier, name, port_name, spec):
        app = get_vistrails_application()
        app.send_notification("reg_new_output_port", identifier, name, 
                              port_name, spec)
        # self.emit(self.new_output_port_signal, identifier, name, port_name, 
        #           spec)

    def emit_show_module(self, descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_show_module", descriptor)
        # self.emit(self.show_module_signal, descriptor)

    def emit_hide_module(self, descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_hide_module", descriptor)
        # self.emit(self.hide_module_signal, descriptor)

    def emit_module_updated(self, old_descriptor, new_descriptor):
        app = get_vistrails_application()
        app.send_notification("reg_module_updated", old_descriptor, 
                              new_descriptor)
        # self.emit(self.module_updated_signal, old_descriptor, new_descriptor)

###############################################################################
# ModuleRegistry

# !!!!!! DEPRECATED !!!!!!
# Use get_module_registry()
global registry, add_module, add_input_port, has_input_port, add_output_port, \
    set_current_package, get_descriptor_by_name, get_module_by_name, \
    get_descriptor
registry                 = None
add_module               = None
add_input_port           = None
has_input_port           = None
add_output_port          = None
set_current_package      = None
get_descriptor_by_name   = None
get_module_by_name       = None
get_descriptor           = None


class ModuleRegistryException(Exception):
    def __init__(self, identifier, name=None, namespace=None,
                 package_version=None, module_version=None, module_id=None):
        Exception.__init__(self)
        self._identifier = identifier
        self._name = name
        self._namespace = namespace
        self._package_version = package_version
        self._module_version = module_version
        self._module_id = module_id

    def __str__(self):
        p_version_str = ""
        m_str = ""
        if self._package_version:
            p_version_str = " (version '%s')" % self._package_version
        if self._name:
            if self._namespace:
                m_str = " : %s|%s" % (self._namespace, self._name)
            else:
                m_str = " : %s" % self._name
            if self._module_version:
                m_str += " (version '%s')" % self._module_version

        return "RegistryException: %s%s%s" % (self._identifier,
                                              p_version_str, m_str)

    def __eq__(self, other):
        return type(self) == type(other) and \
            self._identifier == other._identifier and \
            self._name == other._name and \
            self._namespace == other._namespace and \
            self._package_version == other._package_version and \
            self._module_version == other._module_version and \
            self._module_id == other._module_id

    def __hash__(self):
        return (type(self), self._identifier, self._name, self._namespace,
                self._package_version, self._module_version, 
                self._module_id).__hash__()

    def _get_module_name(self):
        if self._namespace:
            return "%s|%s" % (self._namespace, self._name)
        return self._name
    _module_name = property(_get_module_name)

    def _get_package_name(self):
        if self._package_version:
            return "%s (version %s)" % (self._identifier, 
                                        self._package_version)
        return self._identifier
    _package_name = property(_get_package_name)

class MissingPackage(ModuleRegistryException):
    def __init__(self, identifier):
        ModuleRegistryException.__init__(self, identifier)

    def __str__(self):
        return "Missing package: %s" % self._identifier

    def _get_module_id(self):
        return None
    def _set_module_id(self, m_id):
        # do not set
        pass
    _module_id = property(_get_module_id, _set_module_id)

class MissingModule(ModuleRegistryException):
    def __init__(self, identifier, name, namespace, package_version=None,
                 module_id=None):
        ModuleRegistryException.__init__(self, identifier, name, namespace,
                                         package_version, None, module_id)

    def __str__(self):
        return "Missing module %s in package %s" % (self._module_name,
                                                    self._package_name)

class MissingPackageVersion(ModuleRegistryException):
    def __init__(self, identifier, version):
        ModuleRegistryException.__init__(self, identifier, None, None, 
                                         version)

    def __str__(self):
        return "Missing version %s of package %s" % \
            (self._package_version, self._identifier)

class MissingModuleVersion(ModuleRegistryException):
    def __init__(self, identifier, name, namespace, module_version, 
                 package_version=None, module_id=None):
        ModuleRegistryException.__init__(self, identifier, name, namespace,
                                         package_version, module_version, module_id)

    def __str__(self):
        return "Missing version %s of module %s from package %s" % \
            (self._module_version, self._module_name, self._package_name)

class AmbiguousResolution(ModuleRegistryException):
    def __init__(self, name, namespace, matches):
        ModuleRegistryException.__init__(self, "<unkown package>", 
                                         name, namespace)
        self.matches = matches

    def __str__(self):
        return ("Ambiguous resolution of module %s.  Could resolve to:\n%s" % \
                    (self._module_name, 
                     ',\n'.join(str(m) for m in self.matches)))

class MissingPort(ModuleRegistryException):
    def __init__(self, descriptor, port_name, port_type):
        ModuleRegistryException.__init__(self,
                                         descriptor.identifier,
                                         descriptor.name,
                                         descriptor.namespace)
        self._port_name = port_name
        self._port_type = port_type

    def __str__(self):
        return "Missing %s port %s from module %s in package %s" % \
            (self._port_type, self._port_name, self._module_name, 
             self._package_name)

class PortMismatch(MissingPort):
    def __init__(self, identifier, name, namespace, port_name, port_type, port_sigstring):
        ModuleRegistryException.__init__(self,
                                         identifier,
                                         name,
                                         namespace)

        self._port_name = port_name
        self._port_type = port_type
        self._port_sigstring = port_sigstring

    def __str__(self):
        return ("%s port '%s' of signature '%s' has bad specification"
                " in module %s of package %s") % \
                (self._port_type.capitalize(), self._port_name,
                 self._port_sigstring, self._module_name, self._package_name)

class PortsIncompatible(ModuleRegistryException):

    def __init__(self, output_identifier, output_name, output_namespace,
                 output_port, input_identifier, input_name, input_namespace,
                 input_port):
        ModuleRegistryException.__init__(self, output_identifier, output_name,
                                         output_namespace)
        self._output_port = output_port
        self._input_identifier = input_identifier
        self._input_name = input_name
        self._input_namespace = input_namespace
        self._input_port = input_port

    def __str__(self):
        if self._namespace:
            out_name = "%s:%s|%s" % (self._identifier, self._namespace,
                                     self._name)
        else:
            out_name = "%s:%s" % (self._identifier, self._name)
        if self._input_namespace:
            in_name = "%s:%s|%s" % (self._input_identifier,
                                    self._input_namespace,
                                    self._input_name)
        else:
            in_name = "%s:%s" % (self._input_identifier, self._input_name)
        return ('Output port "%s" from module "%s" cannot connect to '
                'input port "%s" from module "%s".' % (self._output_port,
                                                       out_name,
                                                       self._input_port,
                                                       in_name))

class DuplicateModule(ModuleRegistryException):
    def __init__(self, old_descriptor, new_identifier, new_name, 
                 new_namespace):
        ModuleRegistryException.__init__(self,
                                         new_identifier,
                                         new_name,
                                         new_namespace)
        self.old_descriptor = old_descriptor

    def __str__(self):
        if self.old_descriptor.namespace:
            old_name = "%s|%s" % (self.old_descriptor.namespace,
                                  self.old_descriptor.name)
        else:
            old_name = self.old_descriptor.name
        return ("Module %s in package %s already exists as "
                "%s in package %s") % \
                (self._module_name, self._package_name, old_name, 
                 self.old_descriptor.identifier)

class DuplicateIdentifier(ModuleRegistryException):
    def __init__(self, identifier, name, namespace=None,
                 package_version=None, module_version=None):
        ModuleRegistryException.__init__(self, identifier, name, namespace,
                                         package_version, module_version)

    def __str__(self):
        return "There is already a module %s in package %s" % \
            (self._module_name, self._package_name)

class InvalidPortSpec(ModuleRegistryException):
    def __init__(self, descriptor, port_name, port_type, exc):
        ModuleRegistryException.__init__(self,
                                         descriptor.identifier,
                                         descriptor.name,
                                         descriptor.namespace)
        self._port_name = port_name
        self._port_type = port_type[0].capitalize() + port_type[1:]
        self._exc = exc
        
    def __str__(self):
        return ('%s port "%s" from module %s in package %s '
                'has bad specification\n  %s' % \
            (self._port_type, self._port_name, self._module_name,
             self._package_name, str(self._exc)))

class MissingBaseClass(Exception):
    def __init__(self, base):
        Exception.__init__(self)
        self._base = base

    def __str__(self):
        return "Base class has not been registered : %s" % (self._base.__name__)

class ModuleRegistry(DBRegistry):
    """ModuleRegistry serves as a registry of VisTrails modules.
    """

    ##########################################################################
    # Constructor and copy

    def __init__(self, *args, **kwargs):
        """ModuleRegistry is the base class for objects that store a hierarchy
        of registered VisTrails Modules. There is one global registry for the
        system, and some modules have local registries (in the case of
        dynamically configurable modules, like PythonSource).

        """
        
        if 'root_descriptor_id' not in kwargs:
            kwargs['root_descriptor_id'] = -1
        DBRegistry.__init__(self, *args, **kwargs)

        self._conversions = dict()
        self._converters = set()

        self.set_defaults()

    def __copy__(self):
        ModuleRegistry.do_copy(self)

    def set_defaults(self, other=None):
        self._root_descriptor = None
        self.signals = ModuleRegistrySignals()
        self.setup_indices()
        if other is None:
            # _constant_hasher_map stores callables for custom parameter
            # hashers
            self._constant_hasher_map = {}
            basic_pkg = get_vistrails_basic_pkg_id()
            if basic_pkg in self.packages:
                self._default_package = self.packages[basic_pkg]
                self._current_package = self._default_package
            else:
                self._default_package = None
                self._current_package = None
        else:
            self._constant_hasher_map = copy.copy(other._constant_hasher_map)
            self._current_package = \
                self.packages[other._current_package.identifier]
            self._default_package = \
                self.packages[other._default_package.identifier]

    def setup_indices(self):
        self.descriptors_by_id = {}
        self.package_versions = self.db_packages_identifier_index
        self.packages = {}
        self._module_key_map = {}
        for pkg in self.package_versions.itervalues():
            for key in chain(pkg.old_identifiers, [pkg.identifier]):
                if key in self.packages:
                    old_pkg = self.packages[key]
                    if versions_increasing(old_pkg.version, pkg.version):
                        self.packages[key] = pkg
                else:
                    self.packages[key] = pkg
            for descriptor in pkg.descriptor_list:
                self.descriptors_by_id[descriptor.id] = descriptor
                k = (descriptor.identifier, descriptor.name, 
                     descriptor.namespace, pkg.version, descriptor.version)
                if descriptor.module is not None:
                    self._module_key_map[descriptor.module] = k
        for descriptor in self.descriptors_by_id.itervalues():
            if descriptor.base_descriptor_id in self.descriptors_by_id:
                base_descriptor = \
                    self.descriptors_by_id[descriptor.base_descriptor_id]
                if descriptor not in base_descriptor.children:
                    base_descriptor.children.append(descriptor)
        
    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRegistry.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleRegistry
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_reg):
        if _reg.__class__ == ModuleRegistry:
            return
        _reg.__class__ = ModuleRegistry
        for package in _reg.package_list:
            Package.convert(package)
        _reg.set_defaults()

    def set_global(self):
        global registry, add_module, add_input_port, has_input_port, \
            add_output_port, set_current_package, get_descriptor_by_name, \
            get_module_by_name, get_descriptor

        if registry is not None:
            raise VistrailsInternalError("Global registry already set.")

        registry                 = self
        add_module               = self.add_module
        add_input_port           = self.add_input_port
        has_input_port           = self.has_input_port
        add_output_port          = self.add_output_port
        set_current_package      = self.set_current_package
        get_descriptor_by_name   = self.get_descriptor_by_name
        get_module_by_name       = self.get_module_by_name
        get_descriptor           = self.get_descriptor

    ##########################################################################
    # Properties

    package_list = DBRegistry.db_packages
    root_descriptor_id = DBRegistry.db_root_descriptor_id

    def _get_root_descriptor(self):
        if self._root_descriptor is None:
            if self.root_descriptor_id >= 0:
                self._root_descriptor = \
                    self.descriptors_by_id[self.root_descriptor_id]
        return self._root_descriptor
    def _set_root_descriptor(self, descriptor):
        self._root_descriptor = descriptor
        self.root_descriptor_id = descriptor.id
    root_descriptor = property(_get_root_descriptor, _set_root_descriptor)

    def add_descriptor(self, desc, package=None):
        if package is None:
            package = self._default_package
        # self.descriptors[(desc.package, desc.name, desc.namespace)] = desc
        self.descriptors_by_id[desc.id] = desc
        package.add_descriptor(desc)
    def delete_descriptor(self, desc, package=None):
        if package is None:
            try:
                package = self.packages[desc.identifier]
            except KeyError:
                package = self._default_package
        if desc.base_descriptor_id != -1 and desc.base_descriptor:
            desc.base_descriptor.children.remove(desc)
        # del self.descriptors[(desc.package, desc.name, desc.namespace)]
        del self.descriptors_by_id[desc.id]
        package.delete_descriptor(desc)
    def add_package(self, package):
        DBRegistry.db_add_package(self, package)
        for key in chain(package.old_identifiers, [package.identifier]):
            if key in self.packages:
                old_pkg = self.packages[key]
                if versions_increasing(old_pkg.version, package.version):
                    self.packages[key] = package
            else:
                self.packages[key] = package

    def delete_package(self, package):
        DBRegistry.db_delete_package(self, package)
        # FIXME hard to incremental updates here so we'll just recreate
        # this can be slow
        self.setup_indices()

    def has_abs_upgrade(self, identifier, name, namespace='',
                        package_version='', module_version=''):

        # if this fails, we want to raise the exception
        try:
            package = self.get_package_by_name(identifier, package_version)
        except MissingPackageVersion:
            package = self.get_package_by_name(identifier)
        return package.has_abs_upgrade(name, namespace, module_version)

    def get_abs_upgrade(self, identifier, name, namespace='',
                        package_version='', module_version=''):
        try:
            package = self.get_package_by_name(identifier, package_version)
        except MissingPackageVersion:
            package = self.get_package_by_name(identifier)
        return package.get_abs_upgrade(name, namespace, module_version)

    # def has_abs_upgrade(self, descriptor_info):
    #     return descriptor_info in self._abs_pkg_upgrades

    # def get_abs_upgrade(self, descriptor_info):
    #     if self.has_abs_upgrade(descriptor_info):
    #         return self._abs_pkg_upgrades[descriptor_info]
    #     return None

    ##########################################################################
    # Per-module registry functions

    def get_package_by_name(self, identifier, package_version=''):
        package_version = package_version or ''
        package_version_key = (identifier, package_version)
#         if package_version is not None and package_version.strip() == "":
#             package_version = None
        try:
            if not package_version:
                return self.packages[identifier]
            else:
                return self.package_versions[package_version_key]
        except KeyError:
            if identifier not in self.packages:
                raise MissingPackage(identifier)
            elif package_version and \
                    package_version_key not in self.package_versions:
                raise MissingPackageVersion(identifier, package_version)

    def get_module_by_name(self, identifier, name, namespace=None):
        """get_module_by_name(name: string): class

        Returns the VisTrails module (the class) registered under the
        given name.

        """
        return self.get_descriptor_by_name(identifier, name, namespace).module

    def has_descriptor_with_name(self, identifier, name, namespace='',
                                 package_version='', module_version=''):
        namespace = namespace or ''
        package_version = package_version or ''
        module_version = module_version or ''

        try:
            if not package_version:
                package = self.packages[identifier]
            else:
                package_version_key = (identifier, package_version)
                package = self.package_versions[package_version_key]
            if not module_version:
                descriptor = package.descriptors[(name, namespace)]
            else:
                descriptor_version_key = (name, namespace, module_version)
                descriptor = \
                    package.descriptor_versions[descriptor_version_key]
        except KeyError:
            return False
        return True
    has_module = has_descriptor_with_name

    def get_descriptor_by_name(self, identifier, name, namespace='', 
                               package_version='', module_version=''):
        """get_descriptor_by_name(package_identifier : str,
                                  module_name : str,
                                  namespace : str,
                                  package_version : str,
                                  module_version : str) -> ModuleDescriptor
        Gets the specified descriptor from the registry.  If you do not
        specify package_version, you will get the currently loaded version.
        If you do not specify the module_version, you will get the most recent
        version.  Note that module_version is currently only used for
        abstractions.

        Raises a ModuleRegistryException if lookup fails.
        """
        namespace = namespace or ''
        package_version = package_version or ''
        module_version = module_version or ''

        try:
            package = self.packages[identifier]
            if package_version:
                package_version_key = (identifier, package_version)
                package = self.package_versions[package_version_key]
            if not module_version:
                descriptor = package.descriptors[(name, namespace)]
            else:
                descriptor_version_key = (name, namespace, module_version)
                descriptor = \
                    package.descriptor_versions[descriptor_version_key]
            return descriptor
        except KeyError:
            if identifier not in self.packages:
                raise MissingPackage(identifier)
            elif (name, namespace) not in package.descriptors:
                raise MissingModule(identifier, name, namespace, 
                                    package_version)
            elif package_version and \
                    package_version_key not in self.package_versions:
                raise MissingPackageVersion(identifier, package_version)
            elif module_version and descriptor_version_key not in \
                    package.descriptor_versions:
                raise MissingModuleVersion(identifier, name, namespace,
                                           module_version, package_version)
            else:
                raise ModuleRegistryException(identifier, name, namespace,
                                              package_version, module_version)

    def get_similar_descriptor(self, identifier, name, namespace=None,
                               package_version=None, module_version=None):
        try:
            return self.get_descriptor_by_name(identifier, name, namespace,
                                               package_version, module_version)
        except MissingPackageVersion:
            return self.get_similar_descriptor(identifier, name, namespace,
                                               None, module_version)
        except MissingModuleVersion:
            return self.get_similar_descriptor(identifier, name, namespace,
                                               package_version, None)
#         except Exception:
#             raise

        return None
            
    def get_descriptor(self, module):
        """get_descriptor(module: class) -> ModuleDescriptor

        Returns the ModuleDescriptor of a given vistrails module (a
        class that subclasses from modules.vistrails_module.Module)

        """
        # assert isinstance(module, type)
        # assert issubclass(module, core.modules.vistrails_module.Module)
        # assert self._module_key_map.has_key(module)
        k = self._module_key_map[module]
        return self.get_descriptor_by_name(*k)

    # get_descriptor_from_module is a synonym for get_descriptor
    get_descriptor_from_module = get_descriptor

    def module_ports(self, p_type, descriptor):
        return [(p.name, p)
                for p in descriptor.port_specs_list
                if p.type == p_type]
        
    def module_source_ports_from_descriptor(self, do_sort, descriptor):
        ports = {}
        for desc in reversed(self.get_module_hierarchy(descriptor)):
            ports.update(self.module_ports('output', desc))
        all_ports = ports.values()
        if do_sort:
            all_ports.sort(key=lambda x: (x.sort_key, x.id))
        return all_ports        

    def module_source_ports(self, do_sort, identifier, module_name, 
                            namespace=None, version=None):
        descriptor = self.get_descriptor_by_name(identifier, module_name, 
                                                 namespace, version)
        return self.module_source_ports_from_descriptor(do_sort, descriptor)

    def module_destination_ports_from_descriptor(self, do_sort, descriptor):
        ports = {}
        for desc in reversed(self.get_module_hierarchy(descriptor)):
            ports.update(self.module_ports('input', desc))
        all_ports = ports.values()
        if do_sort:
            all_ports.sort(key=lambda x: (x.sort_key, x.id))
        return all_ports
        
    def module_destination_ports(self, do_sort, identifier, module_name,
                                 namespace=None, version=None):
        descriptor = self.get_descriptor_by_name(identifier, module_name, 
                                                 namespace, version)
        return self.module_destination_ports_from_descriptor(do_sort,
                                                             descriptor)

    ##########################################################################
    # Legacy

    def get_descriptor_from_name_only(self, name):
        """get_descriptor_from_name_only(name) -> descriptor

        This tries to return a descriptor from a name without a
        package. The call should only be used for converting from
        legacy vistrails to new ones. For one, it is slow on misses. 

        """
        matches = []
        for pkg in self.package_list:
            matches.extend((pkg, key) for key in pkg.descriptors.iterkeys()
                           if key[0] == name)
#         matches = [[(pkg, desc) for desc in pkg.descriptors.iterkeys()
#                     if desc[0] == name] for pkg in self.package_list]

#         matches = [x for x in
#                    self.descriptors.iterkeys()
#                    if x[1] == name]
        if len(matches) == 0:
            raise MissingModule("<unknown package>", name, None)
        if len(matches) > 1:
            matches_str = [(m[0].identifier, m[1][0], m[1][1],
                            m[0].version) for m in matches]
            raise AmbiguousResolution(name, None, matches_str)
        (pkg, key) = matches[0]
        desc = pkg.descriptors[key]
        result = self.get_descriptor_by_name(pkg.identifier, desc.name, 
                                             desc.namespace, pkg.version, 
                                             desc.version)
        return result

    ##########################################################################

    def module_signature(self, pipeline, module):
        """Returns signature of a given core.vistrail.Module in the
        given core.vistrail.Pipeline, possibly using user-defined
        hasher.
        """
        chm = self._constant_hasher_map
        descriptor = self.get_descriptor_by_name(module.package,
                                                 module.name,
                                                 module.namespace)
        if not descriptor:
            return vistrails.core.cache.hasher.Hasher.module_signature(module, chm)
        c = descriptor.hasher_callable()
        if c:
            return c(pipeline, module, chm)
        else:
            return vistrails.core.cache.hasher.Hasher.module_signature(module, chm)

    def get_module_color(self, identifier, name, namespace=None):
        return self.get_descriptor_by_name(identifier, name, namespace).module_color()

    def get_module_fringe(self, identifier, name, namespace=None):
        return self.get_descriptor_by_name(identifier, name, namespace).module_fringe()

    def update_registry(self, base_descriptor, module, identifier, name, 
                        namespace, package_version=None, version=None):
        if namespace is not None and not namespace.strip():
            namespace = None

        # add to package list, creating new package if necessary
        if identifier not in self.packages:
            if self._current_package.identifier == identifier:
                package = self._current_package
            else:
                package_id = self.idScope.getNewId(Package.vtType)
                package = Package(id=package_id,
                                  codepath="",
                                  load_configuration=False,
                                  name="",
                                  identifier=identifier,
                                  version=package_version,
                                  )
            self.add_package(package)
        else:
            package = self.package_versions[(identifier, package_version)]

        # create descriptor
        descriptor_id = self.idScope.getNewId(ModuleDescriptor.vtType)
        descriptor = ModuleDescriptor(id=descriptor_id,
                                      module=module,
                                      package=identifier,
                                      base_descriptor=base_descriptor,
                                      name=name,
                                      namespace=namespace,
                                      package_version=package_version,
                                      version=version
                                      )
        self.add_descriptor(descriptor, package)

        # invalidate the map of converters
        if issubclass(module,
                vistrails.core.modules.vistrails_module.Converter):
            self._conversions = dict()
            self._converters.add(descriptor)

        if module is not None:
            self._module_key_map[module] = (identifier, name, namespace,
                                            package_version, version)
        return descriptor

    def convert_port_val(self, val, sig=None, cls=None):
        basic_pkg = get_vistrails_basic_pkg_id()
        if sig is None and cls is None:
            raise ValueError("One of sig or cls must be set")
        try:
            if sig is not None:
                desc = self.get_descriptor_by_name(*sig)
            else:
                desc = self.get_descriptor(cls)
        except Exception, e:
            debug.unexpected_exception(e)
            raise VistrailsInternalError("Cannot convert value %r due to "
                                         "missing descriptor for port" % val)
        constant_desc = self.get_descriptor_by_name(basic_pkg, 'Constant')
        if not self.is_descriptor_subclass(desc, constant_desc):
            raise TypeError("Cannot convert value for non-constant type")
        if desc.module is None:
            return None
        
        if not isinstance(val, basestring):
            retval = desc.module.translate_to_string(val)
        else:
            checkval = desc.module.translate_to_python(val)
            retval = desc.module.translate_to_string(checkval)
            if isinstance(checkval, basestring) and retval != val:
                # we have a string -> string conversion that doesn't
                # match
                retval = desc.module.translate_to_string(val)
        return retval
            
    def auto_add_ports(self, module):
        """auto_add_ports(module or (module, kwargs)): add
        input/output ports to registry. Don't call this directly - it is
        meant to be used by the packagemanager, when inspecting the package
        contents."""
        create_psi_string = \
                    vistrails.core.modules.utils.create_port_spec_item_string
        for (port_key, adder_f, simple_t, compound_t, deprecated_t, is_input) \
            in [('_input_ports', self.add_input_port, InputPort, 
                 CompoundInputPort, DeprecatedInputPort, True),
                ('_output_ports', self.add_output_port, OutputPort, 
                 CompoundOutputPort, OutputPort, False)]:
            if port_key in module.__dict__:
                for port_info in module.__dict__[port_key]:
                    added = False
                    port_name = None
                    port_sig = None
                    try:
                        if not isinstance(port_info, simple_t) and \
                           not isinstance(port_info, compound_t):
                            port_name = port_info[0]
                            port_sig = port_info[1]
                            if len(port_info) > 2:
                                if isinstance(port_info[2], dict):
                                    port_info = compound_t(port_info[0],
                                                                port_info[1],
                                                                **port_info[2])

                                else:
                                    dep_port_info = deprecated_t(*port_info)
                                    port_info = \
                                        compound_t(**dep_port_info._asdict())
                            else:
                                port_info = compound_t(*port_info)

                        # convert simple ports to compound ones
                        kwargs = port_info._asdict()
                        port_name = kwargs.pop('name')
                        port_sig = kwargs.pop('signature')
                        if is_input and isinstance(port_info, simple_t):
                            kwargs['labels'] = [kwargs.pop('label')]
                            kwargs['defaults'] = [kwargs.pop('default')]
                            kwargs['values'] = [kwargs.pop('values')]
                            kwargs['entry_types'] = [kwargs.pop('entry_type')]
                        elif isinstance(port_info, compound_t):
                            # have compound port
                            port_items = kwargs.pop('items')
                            if port_items is not None:
                                sig_items = []
                                labels = []
                                defaults = []
                                values = []
                                entry_types = []
                                for item in port_info.items:
                                    if not isinstance(item.signature, 
                                                      basestring):
                                        d = self.get_descriptor(item.signature)
                                        sig_items.append(create_psi_string(
                                            d.package, d.name, d.namespace))
                                    else:
                                        sig_items.append(item.signature)
                                    labels.append(item.label)
                                    defaults.append(item.default)
                                    values.append(item.values)
                                    entry_types.append(item.entry_type)
                                kwargs['signature'] = ','.join(sig_items)
                                if is_input:
                                    kwargs['labels'] = labels
                                    kwargs['defaults'] = defaults
                                    kwargs['values'] = values
                                    kwargs['entry_types'] = entry_types

                        # add the port
                        adder_f(module, port_name, port_sig, **kwargs)
                        added = True
                    except Exception, e:
                        debug.critical('Failed to add port "%s" to '
                                       'module "%s"' % (port_name, 
                                                        module.__name__),
                                       e)
                        raise
                        
    def auto_add_module(self, module):
        """auto_add_module(module or (module, kwargs)): add module
        to registry. Don't call this directly - it is
        meant to be used by the packagemanager, when inspecting the package
        contents."""
        if isinstance(module, type):
            return self.add_module(module)
        elif (isinstance(module, tuple) and
              len(module) == 2 and
              isinstance(module[0], type) and
              isinstance(module[1], dict)):
            descriptor = self.add_module(module[0], **module[1])
            return descriptor
        else:
            raise TypeError("Expected module or (module, kwargs)")

    def add_module(self, module, **kwargs):
        """add_module(module: class, **kwargs) -> ModuleDescriptor

        See :py:class:`vistrails.core.modules.config.ModuleSettings`.
        All of its attributes may also be used as kwargs to
        add_module.

        """
        def remap_dict(d):
            remap = {'configureWidgetType': 'configure_widget',
                     'constantWidget': 'constant_widget',
                     'constantWidgets': 'constant_widgets',
                     'signatureCallable': 'signature',
                     'constantSignatureCallable': 'constant_signature',
                     'moduleColor': 'color',
                     'moduleFringe': 'fringe',
                     'moduleLeftFringe': 'left_fringe',
                     'moduleRightFringe': 'right_fringe',
                     'is_abstract': 'abstract'}
            remapped_d = {}
            for k, v in d.iteritems():
                if k in remap:
                    remapped_d[remap[k]] = v
                else:
                    remapped_d[k] = v
            return remapped_d

        module_settings = None
        if '_settings' in module.__dict__:
            settings = module.__dict__['_settings']
            if isinstance(settings, ModuleSettings):
                module_settings = settings
            elif isinstance(settings, dict):
                module_settings = ModuleSettings(**remap_dict(settings))
            else:
                raise TypeError("Expected module._settings to be "
                                "ModuleSettings or dict")
                
        remapped_kwargs = remap_dict(kwargs)
        if module_settings is not None:
            module_settings = module_settings._replace(**remapped_kwargs)
        else:
            module_settings = ModuleSettings(**remapped_kwargs)
        return self.add_module_from_settings(module, module_settings)

    def add_module_from_settings(self, module, settings):
        """add_module(module: class, settings) -> ModuleDescriptor

        See :py:class:`vistrails.core.modules.config.ModuleSettings`.
        All of its attributes may also be used as kwargs to
        add_module.

        """

        def get_setting(attr, default_val):
            val = getattr(settings, attr)
            if val is None:
                return default_val
            return val

        name = get_setting('name', module.__name__)

        default_identifier = None
        default_version = ""
        if self._current_package is not None:
            default_identifier = self._current_package.identifier
            default_version = self._current_package.version
        identifier = get_setting('package', default_identifier)
        package_version = get_setting('package_version', default_version)
        namespace = settings.namespace
        version = settings.version

        if identifier is None:
            raise VistrailsInternalError("No package is currently being "
                                         "loaded and arugment 'package' is "
                                         "not specified.")

        package = self.package_versions[(identifier, package_version)]
        desc_key = (name, namespace, version)
        if desc_key in package.descriptor_versions:
            raise ModuleAlreadyExists(identifier, name)

        # We allow multiple inheritance as long as only one of the superclasses
        # is a subclass of Module.
        if settings.is_root:
            base_descriptor = None
        else:
            candidates = self.get_subclass_candidates(module)
            if len(candidates) != 1:
                raise InvalidModuleClass(module)
            base_class = candidates[0]
            if base_class not in self._module_key_map:
                raise MissingBaseClass(base_class)
            base_descriptor = self.get_descriptor(base_class)

        if module in self._module_key_map:
            # This is really obsolete as having two descriptors
            # pointing to the same module isn't a big deal except to
            # get_descriptor which shouldn't be used often
            if identifier != 'local.abstractions':
                raise DuplicateModule(self.get_descriptor(module), identifier,
                                      name, namespace)
        elif self.has_descriptor_with_name(identifier, name, namespace,
                                           package_version, version):
            raise DuplicateIdentifier(identifier, name, namespace,
                                      package_version, version)
        descriptor = self.update_registry(base_descriptor, module, identifier, 
                                          name, namespace, package_version,
                                          version)
        if settings.is_root:
            self.root_descriptor = descriptor

        descriptor.set_module_abstract(settings.abstract)
        descriptor.set_configuration_widget(settings.configure_widget)
        # descriptor.set_configuration_widget(configureWidget)
        descriptor.is_hidden = settings.hide_descriptor
        descriptor.namespace_hidden = settings.hide_namespace

        if settings.signature:
            descriptor.set_hasher_callable(settings.signature)

        if settings.constant_signature:
            if not self.is_constant_module(module):
                raise TypeError("To set constant_signature, module "
                                "must be a subclass of Constant")
                
            # FIXME, currently only allow one per hash, no versioning
            hash_key = (identifier, name, namespace)
            self._constant_hasher_map[hash_key] = settings.constant_signature
        
        constant_widgets = []
        if settings.constant_widget:
            constant_widgets += [settings.constant_widget]
        if settings.constant_widgets is not None:
            constant_widgets += settings.constant_widgets
        if len(constant_widgets) > 0:
            if not self.is_constant_module(module):
                raise TypeError("To set constant widgets, module " +
                                "must be a subclass of Constant")
            for widget_t in constant_widgets:
                if isinstance(widget_t, tuple):
                    widget_t = ConstantWidgetConfig(*widget_t)
                else:
                    widget_t = ConstantWidgetConfig(widget_t)
                if widget_t.widget is not None:
                    self.set_constant_config_widget(descriptor, 
                                                    widget_t.widget,
                                                    widget_t.widget_type, 
                                                    widget_t.widget_use)

        descriptor.set_module_color(settings.color)

        if settings.fringe:
            _check_fringe(settings.fringe)
            left_fringe = list(reversed([(-x, 1.0-y) for (x, y) in \
                                    settings.fringe]))
            descriptor.set_module_fringe(left_fringe, settings.fringe)
        elif settings.left_fringe and settings.right_fringe:
            _check_fringe(settings.left_fringe)
            _check_fringe(settings.right_fringe)
            descriptor.set_module_fringe(settings.left_fringe, 
                                         settings.right_fringe)
        
        if settings.ghost_package:
            descriptor.ghost_identifier = settings.ghost_package
        if settings.ghost_package_version:
            descriptor.ghost_package_version = settings.ghost_package_version
        if settings.ghost_namespace:
            descriptor.ghost_namespace = settings.ghost_namespace
                 
        self.signals.emit_new_module(descriptor)
        if self.is_abstraction(descriptor):
            self.signals.emit_new_abstraction(descriptor)
        return descriptor

    def auto_add_subworkflow(self, subworkflow):
        if isinstance(subworkflow, str):
            return self.add_subworkflow(subworkflow)
        elif (isinstance(subworkflow, tuple) and
              len(subworkflow) == 2 and
              isinstance(subworkflow[0], str) and
              isinstance(subworkflow[1], dict)):
            descriptor = self.add_subworkflow(subworkflow[0], **subworkflow[1])
            return descriptor
        else:
            raise TypeError("Expected filename or (filename, kwargs)")

    def add_subworkflow(self, vt_fname, **kwargs):
        from vistrails.core.modules.sub_module import new_abstraction, read_vistrail, \
            get_next_abs_annotation_key

        # vt_fname is relative to the package path
        if 'package' in kwargs:
            identifier = kwargs['package']
        else:
            identifier = self._current_package.identifier
        if 'package_version' in kwargs:
            package_version = kwargs['package_version']
        else:
            package_version = self._current_package.version
        if 'version' in kwargs:
            version = kwargs['version']
        else:
            version = -1L
        if 'name' in kwargs:
            name = kwargs['name']
        else:
            name = _parse_abstraction_name(vt_fname)
            kwargs['name'] = name

        package = self.package_versions[(identifier, package_version)]
        if not os.path.isabs(vt_fname):
            vt_fname = os.path.join(package.package_dir, vt_fname)
        else:
            debug.warning("Using absolute path for subworkflow: '%s'" % \
                vt_fname)
        
        vistrail = read_vistrail(vt_fname)
        namespace = kwargs.get('namespace', '')
        
        # create module from workflow
        module = None
        is_upgraded_abstraction = False
        try:
            module = new_abstraction(name, vistrail, vt_fname, version)
        except InvalidPipeline, e:
            # This import MUST be delayed until this point or it will fail
            import vistrails.core.vistrail.controller 
            from vistrails.core.db.io import save_vistrail_to_xml
            from vistrails.core.modules.abstraction import identifier as \
                abstraction_pkg, version as abstraction_ver
            # Use a "dummy" controller to handle the upgrade
            controller = vistrails.core.vistrail.controller.VistrailController(vistrail)
            if version == -1L:
                version = vistrail.get_latest_version()
            (new_version, new_pipeline) = \
                controller.handle_invalid_pipeline(e, long(version), vistrail, 
                                                   False, True)
            del controller
            vistrail.set_annotation('__abstraction_descriptor_info__', 
                                    (identifier, name, namespace, 
                                     package_version, str(version)))
            vt_save_dir = tempfile.mkdtemp(prefix='vt_upgrade_abs')
            vt_fname = os.path.join(vt_save_dir, os.path.basename(vt_fname))
            
            
            # need to create new namespace for upgraded version
            new_namespace = str(uuid.uuid1())
            annotation_key = get_next_abs_annotation_key(vistrail)
            vistrail.set_annotation(annotation_key, new_namespace)

            # FIXME: Should delete this upgrade file when vistrails is exited
            save_vistrail_to_xml(vistrail, vt_fname) 
            module = new_abstraction(name, vistrail, vt_fname, new_version, 
                                     new_pipeline)
            # need to set identifier to local.abstractions and its version
            kwargs['package'] = abstraction_pkg
            kwargs['package_version'] = abstraction_ver
            # only want to change the namespace on the new version
            # (the one being added to local.abstractions)
            kwargs['namespace'] = new_namespace

            # Set ghost attributes so module palette shows it in
            # package instead of 'My Subworkflows'
            kwargs['ghost_package'] = identifier
            kwargs['ghost_package_version'] = package_version
            kwargs['ghost_namespace'] = namespace
            is_upgraded_abstraction = True
                                    
        module.internal_version = str(module.internal_version)
        kwargs['version'] = module.internal_version
        descriptor = None
        if kwargs:
            descriptor = self.add_module(module, **kwargs)
        else:
            descriptor = self.add_module(module)
        if is_upgraded_abstraction:
            descriptor_info = (identifier, name, namespace,  
                               package_version, str(version))
            # print 'adding to upgrades:', descriptor_info
            # print '  ', descriptor.package, descriptor.name, descriptor.namespace, descriptor.version, descriptor.package_version
            if identifier != abstraction_pkg:
                info_exc = ModuleRegistryException(*descriptor_info)
                debug.critical("Module %s in package %s is out-of-date.  "
                               "Please check with the package developer for "
                               "a new version." % (info_exc._module_name,
                                                   info_exc._package_name))
            package.add_abs_upgrade(descriptor, name, namespace, str(version))
            self.auto_add_ports(descriptor.module)
        return descriptor

    def has_input_port(self, module, portName):
        descriptor = self.get_descriptor(module)
        # return descriptor.input_ports.has_key(portName)
        return (portName, 'input') in descriptor.port_specs

    def has_output_port(self, module, portName):
        descriptor = self.get_descriptor(module)
        # return descriptor.output_ports.has_key(portName)
        return (portName, 'output') in descriptor.port_specs

    def create_port_spec(self, name, type, signature=None, sigstring=None,
                         optional=False, sort_key=-1, labels=None, 
                         defaults=None, values=None, entry_types=None,
                         docstring=None, shape=None, 
                         min_conns=0, max_conns=-1, depth=0):
        if signature is None and sigstring is None:
            raise VistrailsInternalError("create_port_spec: one of signature "
                                         "and sigstring must be specified")
        spec_id = self.idScope.getNewId(PortSpec.vtType)

        # convert values of defaults and values if necessary
        if defaults is not None or values is not None:
            parse_port_spec_string = \
                            vistrails.core.modules.utils.parse_port_spec_string
            # parse port specs as necessary
            if sigstring is not None:
                sigstrings = parse_port_spec_string(sigstring)
                sig_cls_list = [None,] * len(sigstrings)
            else:
                if isinstance(signature, collections.Sequence):
                    sig_cls_list = signature
                    sigstrings = [None,] * len(sig_cls_list)
                else:
                    sig_cls_list = [signature]
                    sigstrings = [None,]
            if defaults is not None:
                new_defaults = []
                if isinstance(defaults, basestring):
                    defaults = literal_eval(defaults)
                if not isinstance(defaults, list):
                    raise ValueError('Defaults for port "%s" must be a list' %
                                     name)
                for i, default_val in enumerate(defaults):
                    if default_val is not None:
                        default_conv = self.convert_port_val(default_val,
                                                             sigstrings[i], 
                                                             sig_cls_list[i])
                        if default_conv is not None:
                            new_defaults.append(default_conv)
                        else:
                            new_defaults.append(None)
                    else:
                        new_defaults.append(None)
                defaults = new_defaults
            if values is not None:
                new_values = []
                if isinstance(values, basestring):
                    values = literal_eval(values)
                if not isinstance(values, list):
                    raise ValueError('Values for port "%s" must be a list '
                                     'of lists' % name)
                for i, values_list in enumerate(values):
                    if isinstance(values_list, basestring):
                        values_list = literal_eval(values_list)
                    if values_list is not None:
                        if not isinstance(values_list, list):
                            raise ValueError('Values for port "%s" must be '
                                             'a list of lists' % name)
                        new_values_list = []
                        for val in values_list:
                            if val is not None:
                                val_conv = self.convert_port_val(val, 
                                                                 sigstrings[i],
                                                                 sig_cls_list[i])
                                if val_conv is not None:
                                    new_values_list.append(val_conv)
                        new_values.append(new_values_list)
                    else:
                        new_values.append(None)
                values = new_values        
        
        spec = PortSpec(id=spec_id,
                        name=name,
                        type=type,
                        signature=signature,
                        sigstring=sigstring,
                        optional=optional,
                        sort_key=sort_key,
                        labels=labels,
                        defaults=defaults,
                        values=values,
                        entry_types=entry_types,
                        docstring=docstring,
                        shape=shape,
                        min_conns=min_conns,
                        max_conns=max_conns,
                        depth=depth)

        # don't know how many port spec items are created until after...
        for psi in spec.port_spec_items:
            psi.id = self.idScope.getNewId(PortSpecItem.vtType)
        return spec

    def add_port_spec(self, descriptor, spec):
        # check if the spec is valid
        try:
            spec.descriptors()
        except ModuleRegistryException, e:
            raise InvalidPortSpec(descriptor, spec.name, spec.type, e)

        descriptor.add_port_spec(spec)
        if spec.type == 'input':
            self.signals.emit_new_input_port(descriptor.identifier,
                                             descriptor.name, spec.name, spec)
        elif spec.type == 'output':
            self.signals.emit_new_output_port(descriptor.identifier,
                                              descriptor.name, spec.name, spec)

    def get_port_spec_from_descriptor(self, desc, port_name, port_type):
        for d in self.get_module_hierarchy(desc):
            if d.has_port_spec(port_name, port_type):
                return d.get_port_spec(port_name, port_type)

        # if we don't find it, raise MissingPort exception
        raise MissingPort(desc, port_name, port_type)

    def get_port_spec(self, package, module_name, namespace, 
                      port_name, port_type):
        desc = self.get_descriptor_by_name(package, module_name, namespace)
        return self.get_port_spec_from_descriptor(desc, port_name, 
                                                  port_type)

    def has_port_spec_from_descriptor(self, desc, port_name, port_type):
        for d in self.get_module_hierarchy(desc):
            if d.has_port_spec(port_name, port_type):
                return True
        return False

    def has_port_spec(self, package, module_name, namespace,
                      port_name, port_type):
        desc = self.get_descriptor_by_name(package, module_name, namespace)
        return self.has_port_spec_from_descriptor(desc, port_name, 
                                                  port_type)

    def add_port(self, descriptor, port_name, port_type, port_sig=None, 
                 port_sigstring=None, optional=False, sort_key=-1,
                 labels=None, defaults=None, values=None, entry_types=None, 
                 docstring=None, shape=None, min_conns=0, max_conns=-1,
                 depth=0):
        spec = self.create_port_spec(port_name, port_type, port_sig,
                                     port_sigstring, optional, sort_key,
                                     labels, defaults, values, entry_types,
                                     docstring, shape,
                                     min_conns, max_conns, depth)

        self.add_port_spec(descriptor, spec)

    def add_input_port(self, module, portName, portSignature, optional=False, 
                       sort_key=-1, labels=None, defaults=None,
                       values=None, entry_types=None, docstring=None,
                       shape=None, min_conns=0, max_conns=-1, depth=0):
        """add_input_port(module: class,
                          portName: string,
                          portSignature: string,
                          optional: bool,
                          sort_key: int,
                          labels: tuple(string),
                          defaults: tuple(string),
                          values: list(list(string)),
                          entry_types: list(string),
                          docstring: string,
                          shape: tuple,
                          min_conns: int,
                          max_conns: int,
                          depth: int) -> None

        Registers a new input port with VisTrails. Receives the module
        that will now have a certain port, a string representing the
        name, and a signature of the port, described in
        doc/module_registry.txt. Optionally, it receives whether the
        input port is optional."""
        descriptor = self.get_descriptor(module)
        if isinstance(portSignature, basestring):
            self.add_port(descriptor, portName, 'input', None, portSignature,
                          optional, sort_key, labels, defaults, values,
                          entry_types, docstring, shape, min_conns, max_conns,
                          depth)
        else:
            self.add_port(descriptor, portName, 'input', portSignature, None, 
                          optional, sort_key, labels, defaults, values,
                          entry_types, docstring, shape, min_conns, max_conns,
                          depth)


    def add_output_port(self, module, portName, portSignature, optional=False, 
                        sort_key=-1, docstring=None, shape=None, 
                        min_conns=0, max_conns=-1, depth=0):
        """add_output_port(module: class,
                           portName: string,
                           portSignature: string,
                           optional: bool,
                           sort_key: int,
                           docstring: string,
                           shape: tuple,
                           min_conns: int,
                           max_conns: int,
                           depth: int) -> None

        Registers a new output port with VisTrails. Receives the
        module that will now have a certain port, a string
        representing the name, and a signature of the port, described
        in doc/module_registry.txt. Optionally, it receives whether
        the output port is optional."""
        descriptor = self.get_descriptor(module)
        if isinstance(portSignature, basestring):
            self.add_port(descriptor, portName, 'output', None, portSignature, 
                          optional, sort_key, None, None, None, None, 
                          docstring, shape, min_conns, max_conns, depth)
        else:
            self.add_port(descriptor, portName, 'output', portSignature, None, 
                          optional, sort_key, None, None, None, None, 
                          docstring, shape, min_conns, max_conns, depth)

    def create_package(self, codepath, load_configuration=True):
        package_id = self.idScope.getNewId(Package.vtType)
        package = Package(id=package_id,
                          codepath=codepath,
                          load_configuration=load_configuration)
        return package

    def initialize_package(self, package):
        if package.initialized():
            return
        debug.splashMessage("Initializing " + package.codepath + "...")
        debug.log("Initializing " + package.codepath)
        if (package.identifier, package.version) not in self.package_versions:
            self.add_package(package)
        self.set_current_package(package)
        try:
            package.initialize()
            # Perform auto-initialization
            if hasattr(package.module, '_modules'):
                modules = package.module._modules
                if isinstance(modules, dict):
                    module_list = []
                    for namespace, m_list in modules.iteritems():
                        for module in m_list:
                            m_dict = {'namespace': namespace}
                            if isinstance(module, tuple):
                                m_dict.update(module[1])
                                module_list.append((module[0], m_dict))
                            elif '_settings' in module.__dict__:
                                kwargs = module._settings._asdict()
                                kwargs.update(m_dict)
                                module._settings = ModuleSettings(**kwargs)
                                module_list.append(module)
                            else:
                                module_list.append((module, m_dict))
                else:
                    module_list = modules
                modules = _toposort_modules(module_list)
                # We add all modules before adding ports because
                # modules inside package might use each other as ports
                for module in modules:
                    self.auto_add_module(module)

            # allow all modules to auto_add_ports!
            added_descriptors = set()
            for descriptor in package.descriptor_list:
                if hasattr(descriptor, 'module'):
                    self.auto_add_ports(descriptor.module)
                    added_descriptors.add(descriptor)
            # Perform auto-initialization of abstractions
            if hasattr(package.module, '_subworkflows'):
                subworkflows = \
                    _toposort_abstractions(package,
                                           package.module._subworkflows)
                for subworkflow in subworkflows:
                    self.auto_add_subworkflow(subworkflow)
            for descriptor in package.descriptor_list:
                if descriptor not in added_descriptors:
                    if hasattr(descriptor, 'module'):
                        self.auto_add_ports(descriptor.module)
                        added_descriptors.add(descriptor)
        except MissingRequirement:
            raise
        except Exception, e:
            raise package.InitializationFailed(package, 
                                               [traceback.format_exc()])

        # The package might have decided to rename itself, let's store that
        self.set_current_package(None)
        debug.splashMessage("Initializing " + package.codepath + '... done.')
        package._initialized = True 

    def delete_module(self, identifier, module_name, namespace=None):
        """deleteModule(module_name): Removes a module from the registry."""
        descriptor = self.get_descriptor_by_name(identifier, module_name, 
                                                 namespace)
        assert len(descriptor.children) == 0

        # invalidate the map of converters
        converter_desc = self.get_descriptor(
                vistrails.core.modules.vistrails_module.Converter)
        if self.is_descriptor_subclass(descriptor, converter_desc):
            self._conversions = dict()
            self._converters.remove(descriptor)

        self.signals.emit_deleted_module(descriptor)
        if self.is_abstraction(descriptor):
            self.signals.emit_deleted_abstraction(descriptor)
        package = self.packages[descriptor.identifier]
        self.delete_descriptor(descriptor, package)
        if descriptor.module is not None:
            del self._module_key_map[descriptor.module]

    def remove_package(self, package):
        """remove_package(package) -> None:
        Removes an entire package from the registry.

        """
        # graph is the class hierarchy graph for this subset
        graph = Graph()
        if package.identifier not in self.packages:
            raise MissingPackage(package.identifier)
        package = self.packages[package.identifier]
        for descriptor in package.descriptor_list:
            graph.add_vertex(descriptor.sigstring)
        for descriptor in package.descriptor_list:            
            base_id = descriptor.base_descriptor_id
            if base_id in package.descriptors_by_id:
                base_descriptor = \
                    package.descriptors_by_id[descriptor.base_descriptor_id]
                graph.add_edge(descriptor.sigstring, base_descriptor.sigstring)

        top_sort = graph.vertices_topological_sort()
        # set up fast removal of model
        for sigstring in top_sort:
            self.delete_module(
                *vistrails.core.modules.utils.parse_descriptor_string(sigstring))
        
        # Remove upgraded package subworkflows from registry
        for key, version_dict in package._abs_pkg_upgrades.iteritems():
            for version, descriptor in version_dict.iteritems():
                self.delete_module(descriptor.identifier, descriptor.name, 
                                   descriptor.namespace)
        package._abs_pkg_upgrades.clear()
        
        package.unload()
        self.delete_package(package)
        self.signals.emit_deleted_package(package)

    def delete_input_port(self, descriptor, port_name):
        """ Just remove a name input port with all of its specs """
        descriptor.delete_input_port(port_name)

    def delete_output_port(self, descriptor, port_name):
        """ Just remove a name output port with all of its specs """
        descriptor.delete_output_port(port_name)

    def source_ports_from_descriptor(self, descriptor, sorted=True):
        ports = [p[1] for p in self.module_ports('output', descriptor)]
        if sorted:
            ports.sort(key=lambda x: x.name)
        return ports
    
    def destination_ports_from_descriptor(self, descriptor, sorted=True):
        ports = [p[1] for p in self.module_ports('input', descriptor)]
        if sorted:
            ports.sort(key=lambda x: x.name)
        return ports
        
    def all_source_ports(self, descriptor, sorted=True):
        """Returns source ports for all hierarchy leading to given module"""
        getter = self.source_ports_from_descriptor
        return [(desc.name, getter(desc, sorted))
                for desc in self.get_module_hierarchy(descriptor)]

    def all_destination_ports(self, descriptor, sorted=True):
        """Returns destination ports for all hierarchy leading to
        given module"""
        getter = self.destination_ports_from_descriptor
        return [(desc.name, getter(desc, sorted))
                for desc in self.get_module_hierarchy(descriptor)]

    def get_port_from_all_destinations(self, descriptor, name):
        """Searches for port identified by name in the destination ports
        for all hierarchy leading to given module """
        all_ports = self.all_destination_ports(descriptor)
        for (klass, port_list) in all_ports:
            for port in port_list:
                if port.name == name:
                    return port
        else:
            return None
        
    def is_method(self, port_spec):
        basic_pkg = get_vistrails_basic_pkg_id()
        constant_desc = \
            self.get_descriptor_by_name(basic_pkg, 'Constant')
        return port_spec.type == 'input' and \
            all(self.is_descriptor_subclass(d, constant_desc) 
                for d in port_spec.descriptors())
    is_constant = is_method

    def is_constant_module(self, module):
        basic_pkg = get_vistrails_basic_pkg_id()
        constant_cls = \
                    self.get_descriptor_by_name(basic_pkg, 'Constant').module
        return issubclass(module, constant_cls)

    def method_ports(self, module_descriptor):
        """method_ports(module_descriptor: ModuleDescriptor) 
              -> [PortSpec]}

        Returns a list of port specs that are methods 
        (spec contains only subclasses of Constant).

        """
        getter = self.module_destination_ports_from_descriptor
        return [spec for spec in sorted(getter(False, module_descriptor),
                                        key=lambda x: x.name)
                if self.is_method(spec)]

    def port_and_port_spec_match(self, port, port_spec):
        """port_and_port_spec_match(port: Port | PortSpec, 
                                    port_spec: PortSpec
                                    ) -> bool
        Checks if port is similar to port_spec or not.  These ports must
        have the same name and type"""
        if port.type in PortSpec.port_type_map:
            port_type = port.type
        elif port.type in PortSpec.port_type_map.inverse:
            port_type = PortSpec.port_type_map.inverse[port.type]
        else:
            raise TypeError('Port type "%s" invalid' % str(port.type))
        if port_type != port_spec.type:
            return False
        if port.name != port_spec.name:
            return False
        if port.sigstring == port_spec.sigstring:
            return True
        return self.are_specs_matched(port, port_spec)

    def ports_can_connect(self, sourceModulePort, destinationModulePort,
                          allow_conversion=False, out_converters=None):
        """ports_can_connect(sourceModulePort,destinationModulePort) ->
        Boolean returns true if there could exist a connection
        connecting these two ports."""
        if sourceModulePort.type == destinationModulePort.type:
            return False
        return self.are_specs_matched(sourceModulePort, destinationModulePort,
                                      allow_conversion=allow_conversion,
                                      out_converters=out_converters)

    def is_port_sub_type(self, sub, super):
        """ is_port_sub_type(sub: Port, super: Port) -> bool        
        Check if port super and sub are similar or not. These ports
        must have exact name as well as position
        
        """
        if sub.type != super.type:
            return False
        if sub.name != super.name:
            return False
        return self.are_specs_matched(sub, super)

    def get_converters(self, sub_descs, super_descs):
        key = (tuple(sub_descs), tuple(super_descs))

        # Get the result from the cache
        try:
            return self._conversions[key]
        except KeyError:
            pass

        converters = []

        # Compute the result
        for converter in self._converters:
            if converter.module is (
                    vistrails.core.modules.vistrails_module.Converter):
                continue

            if converter.module.can_convert(sub_descs, super_descs):
                converters.append(converter)

        # Store in the cache that there was no result
        self._conversions[key] = converters
        return converters

    def is_descriptor_list_subclass(self, sub_descs, super_descs):
        basic_pkg = get_vistrails_basic_pkg_id()
        variant_desc = self.get_descriptor_by_name(basic_pkg, 'Variant')
        module_desc = self.get_descriptor_by_name(basic_pkg, 'Module')

        for (sub_desc, super_desc) in izip(sub_descs, super_descs):
            if sub_desc == variant_desc or super_desc == variant_desc:
                continue
            if super_desc == module_desc and sub_desc != module_desc:
                warnings.warn(
                        "Connecting any type on a Module input port is "
                        "deprecated\nPlease make the output port a Variant to "
                        "get this behavior.",
                        category=VistrailsDeprecation)
                #return False
            if not self.is_descriptor_subclass(sub_desc, super_desc):
                return False
        return True

    def are_specs_matched(self, sub, super, allow_conversion=False,
                          out_converters=None):
        """ are_specs_matched(sub: Port, super: Port) -> bool        
        Check if specs of sub and super port are matched or not
        
        """
        # For a connection, this gets called for sub -> super
        basic_pkg = get_vistrails_basic_pkg_id()
        variant_desc = self.get_descriptor_by_name(basic_pkg, 'Variant')
        list_desc = self.get_descriptor_by_name(basic_pkg, 'List')
        # sometimes sub is coming None
        # I don't know if this is expected, so I will put a test here
        sub_descs = []
        if sub:
            sub_descs = sub.descriptors()
        if sub_descs is None:
            return False
        elif sub_descs == [variant_desc]:
            return True
        super_descs = []
        if super:
            super_descs = super.descriptors()
        if super_descs is None:
            return False
        elif super_descs == [variant_desc]:
            return True
        elif [list_desc] in [super_descs, sub_descs]:
            # Allow Lists to connect to anything
            return True
        #elif super_descs == [list_desc] and sub_descs != [list_desc] \
        #     and sub.depth > 0:
        #    # List is handled as Variant with depth 1
        #    return True
        #elif sub_descs == [list_desc] and super_descs != [list_desc] \
        #     and super.depth > 0:
        #    # List is handled as Variant with depth 1
        #    return True

        if (len(sub_descs) == len(super_descs) and
                self.is_descriptor_list_subclass(sub_descs, super_descs)):
            return True

        if allow_conversion:
            converters = self.get_converters(sub_descs, super_descs)
            if converters:
                if out_converters is not None:
                    out_converters.extend(converters)
                return True

        return False

    def get_module_hierarchy(self, descriptor):
        """get_module_hierarchy(descriptor) -> [klass].
        Returns the module hierarchy all the way to Module, excluding
        any mixins."""
        if descriptor.module is None:
            descriptors = [descriptor]
            base_id = descriptor.base_descriptor_id
            while base_id >= 0:
                descriptor = self.descriptors_by_id[base_id]
                descriptors.append(descriptor)
                base_id = descriptor.base_descriptor_id
            return descriptors
        return [self.get_descriptor(klass)
                for klass in descriptor.module.mro()
                if issubclass(klass, vistrails.core.modules.vistrails_module.Module)]

    def get_descriptor_subclasses(self, descriptor):
        # need to find all descriptors that are subdescriptors of descriptor
        sub_list = []
        for pkg in self.package_versions.itervalues():
            for d in pkg.descriptor_list:
                if self.is_descriptor_subclass(d, descriptor):
                    sub_list.append(d)
        return sub_list
        
    def get_input_port_spec(self, module, portName):
        """ get_input_port_spec(module: Module, portName: str) ->
        spec-tuple Return the output port of a module given the module
        and port name.

        FIXME: This should be renamed.
        
        """
        descriptor = module.module_descriptor
        if module.has_port_spec(portName, 'input'):
            return module.get_port_spec(portName, 'input')
        return None

    def get_output_port_spec(self, module, portName):
        """ get_output_port_spec(module: Module, portName: str) -> spec-tuple
        Return the output port of a module given the module
        and port name.

        FIXME: This should be renamed.
        
        """
        descriptor = module.module_descriptor
        if module.has_port_spec(portName, 'output'):
            return module.get_port_spec(portName, 'output')
        return None

    @staticmethod
    def get_subclass_candidates(module):
        """get_subclass_candidates(module) -> [class]

        Tries to eliminate irrelevant mixins for the hierarchy. Returns all
        base classes that subclass from Module."""
        return [klass
                for klass in module.__bases__
                if issubclass(klass, vistrails.core.modules.vistrails_module.Module)]

    def set_current_package(self, package):
        """ set_current_package(package: Package) -> None        
        Set the current package for all addModule operations to
        name. This means that all modules added after this call will
        be assigned to the specified package.  Set package to None to
        indicate that VisTrails default package should be used instead.

        Do not call this directly. The package manager will call this
        with the correct value prior to calling 'initialize' on the
        package.
        
        """
        if package is None:
            package = self._default_package
        self._current_package = package

    def get_module_package(self, identifier, name, namespace):
        """ get_module_package(identifier, moduleName: str) -> str
        Return the name of the package where the module is registered.
        
        """
        descriptor = self.get_descriptor_by_name(identifier, name, namespace)
        return descriptor.module_package()

    def get_configuration_widget(self, identifier, name, namespace):
        descriptor = self.get_descriptor_by_name(identifier, name, namespace)
        package = self.get_package_by_name(identifier)
        prefix = package.prefix + package.codepath
        cls = descriptor.configuration_widget()
        return vistrails.core.modules.utils.load_cls(cls, prefix)

    def get_constant_config_params(self, widget_type=None, widget_use=None):
        if widget_type is None:
            widget_type = 'default'
        if widget_use is None:
            widget_use = 'default'
        return (widget_type, widget_use)

    def get_constant_config_widget(self, descriptor, widget_type=None, 
                                   widget_use=None):
        widget_type, widget_use = self.get_constant_config_params(widget_type,
                                                                  widget_use)
        for desc in self.get_module_hierarchy(descriptor):
            if desc.has_constant_config_widget(widget_use, widget_type):
                return desc.get_constant_config_widget(widget_use, widget_type)
        return None

    def get_all_constant_config_widgets(self, descriptor, widget_use=None):
        widget_use = self.get_constant_config_params(None, widget_use)[1]
        widgets = {}
        for desc in reversed(self.get_module_hierarchy(descriptor)):
            widgets.update(desc.get_all_constant_config_widgets(widget_use))
        return widgets.values()

    def set_constant_config_widget(self, descriptor, widget_class, 
                                   widget_type=None, widget_use=None):
        widget_type, widget_use = self.get_constant_config_params(widget_type,
                                                                  widget_use)
        basic_pkg = get_vistrails_basic_pkg_id()
        constant_desc = self.get_descriptor_by_name(basic_pkg, 'Constant')
        if not self.is_descriptor_subclass(descriptor, constant_desc):
            raise Exception('Descriptor "%s" must be a subclass of Constant '
                            'to use a constant configuration widget.' % \
                            descriptor.sigstring)
        descriptor.set_constant_config_widget(widget_class,
                                              widget_use, widget_type)

    def is_descriptor_subclass(self, sub, super):
        """is_descriptor_subclass(sub : ModuleDescriptor, 
                                  super: ModuleDescriptor) -> bool
        
        """
        # use issubclass for speed if we've loaded the modules
        if sub.module is not None and super.module is not None:
            return issubclass(sub.module, super.module)
        
        # otherwise, use descriptors themselves
        if sub == super:
            return True
        while sub != self.root_descriptor:
            sub = sub.base_descriptor
            if sub == super:
                return True

        return False

    def find_descriptor_subclass(self, d1, d2):
        if self.is_descriptor_subclass(d1, d2):
            return d1
        elif self.is_descriptor_subclass(d2, d1):
            return d2
        return None
        
    def find_descriptor_superclass(self, d1, d2):
        """find_descriptor_superclass(d1: ModuleDescriptor,
                                      d2: ModuleDescriptor) -> ModuleDescriptor
        Finds the lowest common superclass descriptor for d1 and d2

        """        
        if self.is_descriptor_subclass(d1, d2):
            return d2
        elif self.is_descriptor_subclass(d2, d1):
            return d1

        d1_list = [d1]
        while d1 != self.root_descriptor:
            d1 = d1.base_descriptor
            d1_list.append(d1)
        d1_idx = -1
        while self.is_descriptor_subclass(d2, d1_list[d1_idx]):
            d1_idx -= 1
        if d1_idx == -1:
            return None
        return d1_list[d1_idx+1]

    def is_abstraction(self, descriptor):
        basic_pkg = get_vistrails_basic_pkg_id()
        try:
            abstraction_desc = self.get_descriptor_by_name(basic_pkg, 
                                                       'SubWorkflow')
        except MissingModule:
            # No abstractions can be loaded before the basic
            # SubWorkflow descriptor is initialized
            return False
        return abstraction_desc != descriptor and \
            self.is_descriptor_subclass(descriptor, abstraction_desc)
            
    def show_module(self, descriptor):
        self.signals.emit_show_module(descriptor)
    def hide_module(self, descriptor):
        self.signals.emit_hide_module(descriptor)
    def update_module(self, old_descriptor, new_descriptor):
        self.signals.emit_module_updated(old_descriptor, new_descriptor)

    def expand_port_spec_string(self, p_string, cur_package=None, 
                                old_style=False):
        return vistrails.core.modules.utils.expand_port_spec_string(p_string, cur_package,
                                                          old_style)

###############################################################################

# registry                 = ModuleRegistry()
# add_module               = registry.add_module
# add_input_port           = registry.add_input_port
# has_input_port           = registry.has_input_port
# add_output_port          = registry.add_output_port
# set_current_package      = registry.set_current_package
# get_descriptor_by_name   = registry.get_descriptor_by_name
# get_module_by_name       = registry.get_module_by_name
# get_descriptor           = registry.get_descriptor

def get_module_registry():
    global registry
    if not registry:
        raise VistrailsInternalError("Registry not constructed yet.")
    return registry

def module_registry_loaded():
    global registry
    return registry is not None

##############################################################################


class TestModuleRegistry(unittest.TestCase):

    def test_portspec_construction(self):
        from vistrails.core.modules.basic_modules import Float, Integer
        t1 = PortSpec(signature=Float)
        t2 = PortSpec(signature=[Float])
        self.assertEquals(t1, t2)

        t1 = PortSpec(signature=[Float, Integer])
        t2 = PortSpec(signature=[Integer, Float])
        self.assertNotEquals(t1, t2)
