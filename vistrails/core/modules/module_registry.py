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

from PyQt4 import QtCore
import __builtin__
from itertools import izip
import copy
import os
import traceback

from core.data_structures.graph import Graph
import core.debug
import core.modules
import core.modules.vistrails_module
from core.modules.module_descriptor import ModuleDescriptor
from core.modules.package import Package
from core.utils import VistrailsInternalError, memo_method, all, \
     InvalidModuleClass, ModuleAlreadyExists, append_to_dict_of_lists, \
     all, profile
from core.system import vistrails_root_directory, vistrails_version
from core.vistrail.port import Port, PortEndPoint
from core.vistrail.port_spec import PortSpec
import core.cache.hasher
from db.domain import DBRegistry

##############################################################################

# This is used by add_module to make sure the fringe specifications
# make sense
def _check_fringe(fringe):
    assert type(fringe) == list
    assert len(fringe) >= 1
    for v in fringe:
        assert type(v) == tuple
        assert len(v) == 2
        assert type(v[0]) == float
        assert type(v[1]) == float

def _toposort_modules(module_list):
    """_toposort_modules([class]) -> [class]

    _toposort_modules takes a list of modules and returns them
    sorted topologically wrt to the subclass relation, such that
    if a and b are both in the list and issubclass(a,b), then a
    will appear before b in the resulting order.
    """

    g = Graph()
    for m in module_list:
        g.add_vertex(m)
    for m in module_list:
        for subclass in m.mro()[1:]: # skip self
            if subclass in g.vertices:
                g.add_edge(subclass, m)
    return g.vertices_topological_sort()

###############################################################################
# ModuleRegistrySignals

# Refactored this because __class__ assignment fails on ModuleRegistry
# if it inherits from QtCore.QObject
class ModuleRegistrySignals(QtCore.QObject):

    # new_module_signal is emitted with descriptor of new module
    new_module_signal = QtCore.SIGNAL("new_module")
    # deleted_module_signal is emitted with descriptor of deleted module
    deleted_module_signal = QtCore.SIGNAL("deleted_module")
    # deleted_package_signal is emitted with package identifier
    deleted_package_signal = QtCore.SIGNAL("deleted_package")
    # new_input_port_signal is emitted with identifier and name of module, 
    # new port and spec
    new_input_port_signal = QtCore.SIGNAL("new_input_port_signal")
    # new_output_port_signal is emitted with identifier and name of module,
    # new port and spec
    new_output_port_signal = QtCore.SIGNAL("new_output_port_signal")

    def __init__(self):
        QtCore.QObject.__init__(self)

    def emit_new_module(self, descriptor):
        self.emit(self.new_module_signal, descriptor)
    
    def emit_deleted_module(self, descriptor):
        self.emit(self.deleted_module_signal, descriptor)

    def emit_deleted_package(self, package):
        self.emit(self.deleted_package_signal, package)

    def emit_new_input_port(self, identifier, name, port_name, spec):
        self.emit(self.new_input_port_signal, identifier, name, port_name, spec)

    def emit_new_output_port(self, identifier, name, port_name, spec):
        self.emit(self.new_output_port_signal, identifier, name, port_name, 
                  spec)

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


class ModuleRegistry(DBRegistry):
    """ModuleRegistry serves as a registry of VisTrails modules.
    """

    class MissingModulePackage(Exception):
        def __init__(self, identifier, name, namespace):
            Exception.__init__(self)
            self._identifier = identifier
            self._name = name
            self._namespace = namespace
        def __str__(self):
            if self._namespace:
                return "Missing package: %s, %s|%s" % (self._identifier,
                                                       self._namespace,
                                                       self._name)
            else:
                return "Missing package: %s, %s" % (self._identifier,
                                                    self._name)
                

    class MissingBaseClass(Exception):
        def __init__(self, base):
            Exception.__init__(self)
            self._base = base

        def __str__(self):
            return "Base class has not been registered : %s" % (self._base.__name__)

    ##########################################################################
    # Constructor and copy

    def __init__(self, *args, **kwargs):
        """ModuleRegistry is the base class for objects that store a hierarchy
        of registered VisTrails Modules. There is one global registry for the
        system, and some modules have local registries (in the case of
        dynamically configurable modules, like PythonSource).

        """
        
        self.signals = ModuleRegistrySignals()

        if 'root_descriptor_id' not in kwargs:
            kwargs['root_descriptor_id'] = -1
        DBRegistry.__init__(self, *args, **kwargs)

        self.packages = self.db_packages_identifier_index
        self._current_package = self.create_default_package()
        self._module_key_map = {}
        self.descriptors = {}
        self.descriptors_by_id = {}
        
        # _constant_hasher_map stores callables for custom parameter
        # hashers
        self._constant_hasher_map = {}

        for package in self.package_list:
            for descriptor in package.descriptor_list:
                k = (descriptor.package, descriptor.name, descriptor.namespace)
                self.descriptors[k] = descriptor
                self.descriptors_by_id[descriptor.id] = descriptor
                if descriptor.module is not None:
                    self._module_key_map[descriptor.module] = k
        for descriptor in self.descriptors.itervalues():
            if descriptor.base_descriptor_id in self.descriptors_by_id:
                base_descriptor = \
                    self.descriptors_by_id[descriptor.base_descriptor_id]
                base_descriptor.children.append(descriptor)
        if self.root_descriptor_id >= 0:
            self.root_descriptor = \
                self.descriptors_by_id[self.root_descriptor_id]                
        else:
            root_id = self.idScope.getNewId(ModuleDescriptor.vtType)
            self.root_descriptor = \
                ModuleDescriptor(id=root_id,
                                 module=core.modules.vistrails_module.Module,
                                 package=self._current_package.identifier,
                                 namespace=None)
            self.root_descriptor_id = root_id
            self.add_descriptor(self.root_descriptor, self._current_package)
            key = (self._current_package.identifier, "Module", None)
            self._module_key_map[core.modules.vistrails_module.Module] = key

    def __copy__(self):
        ModuleRegistry.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRegistry.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleRegistry
        cp._module_key_map = {}
        cp.descriptors = {}
        cp.descriptors_by_id = {}
        cp._constant_hasher_map = {}
        for package in cp.package_list:
            for descriptor in package.descriptor_list:
                if descriptor.namespace.strip() == "":
                    descriptor.namespace = None
                k = (descriptor.package, descriptor.name, descriptor.namespace)
                cp.descriptors[k] = descriptor
                cp.descriptors_by_id[descriptor.id] = descriptor
                if descriptor.module is not None:
                    cp._module_key_map[descriptor.module] = k
        for descriptor in cp.descriptors.itervalues():
            if descriptor.base_descriptor_id in cp.descriptors_by_id:
                base_descriptor = \
                    cp.descriptors_by_id[descriptor.base_descriptor_id]
                base_descriptor.children.append(descriptor)
        if cp.root_descriptor_id:
            cp.root_descriptor = cp.descriptors_by_id[cp.root_descriptor_id]
        cp.packages = cp.db_packages_identifier_index

        cp._current_package = cp.packages[self._current_package.identifier]
        cp._default_package = cp.packages[self._default_package.identifier]

        return cp

    @staticmethod
    def convert(_reg):
        if _reg.__class__ == ModuleRegistry:
            return
        _reg.__class__ = ModuleRegistry
        _reg._module_key_map = {}
        _reg.descriptors = {}
        _reg.descriptors_by_id = {}
        for package in _reg.package_list:
            Package.convert(package)
            for descriptor in package.descriptor_list:
                if descriptor.namespace.strip() == "":
                    descriptor.namespace = None
                k = (descriptor.package, descriptor.name, descriptor.namespace)
                _reg.descriptors[k] = descriptor
                _reg.descriptors_by_id[descriptor.id] = descriptor
                if descriptor.module is not None:
                    _reg._module_key_map[descriptor.module] = k
        for descriptor in _reg.descriptors.itervalues():
            if descriptor.base_descriptor_id in _reg.descriptors_by_id:
                base_descriptor = \
                    _reg.descriptors_by_id[descriptor.base_descriptor_id]
                base_descriptor.children.append(descriptor)
        if _reg.root_descriptor_id is not None:
            _reg.root_descriptor = \
                _reg.descriptors_by_id[_reg.root_descriptor_id]
        _reg.packages = _reg.db_packages_identifier_index
        _reg.signals = ModuleRegistrySignals()

        if 'edu.utah.sci.vistrails.basic' in _reg.packages:
            _reg._default_package = \
                _reg.packages['edu.utah.sci.vistrails.basic']
            _reg._current_package = _reg._default_package
        else:
            _reg._current_package = reg.create_default_package()

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

    def add_descriptor(self, desc, package=None):
        if package is None:
            package = self._default_package
        self.descriptors[(desc.package, desc.name, desc.namespace)] = desc
        self.descriptors_by_id[desc.id] = desc
        package.add_descriptor(desc)
    def delete_descriptor(self, desc, package=None):
        if package is None:
            package = self._default_package
        if desc.base_descriptor_id != -1 and desc.base_descriptor:
            desc.base_descriptor.children.remove(desc)
        del self.descriptors[(desc.package, desc.name, desc.namespace)]
        del self.descriptors_by_id[desc.id]
        package.delete_descriptor(desc)
    def add_package(self, package):
        DBRegistry.db_add_package(self, package)
    def delete_package(self, package):
        DBRegistry.db_delete_package(self, package)

    def create_default_package(self):
        default_codepath = os.path.join(vistrails_root_directory(), 
                                        "core", "modules", "basic_modules.py")
        self._default_package = \
            Package(id=self.idScope.getNewId(Package.vtType),
                    codepath=default_codepath,
                    load_configuration=False,
                    identifier='edu.utah.sci.vistrails.basic',
                    name='Basic Modules',
                    version=vistrails_version(),
                    description="Basic modules for VisTrails")
        self.add_package(self._default_package)
        return self._default_package

    ##########################################################################
    # Per-module registry functions

    def add_hierarchy(self, global_registry, module):
        # a per-module registry needs to have all the module hierarchy
        # registered there so that add_module doesn't fail with
        # missing base class. We do _NOT_ add the ports, so watch out!
        
        reg = global_registry
        d = reg.get_descriptor_by_name(module.package, module.name, 
                                       module.namespace)
        # we exclude the first module in the hierarchy because it's Module
        # which we know exists (constructor adds)
        hierarchy = reg.get_module_hierarchy(d)
        for desc in reversed(hierarchy[:-1]):
            old_base = desc.base_descriptor
            base_descriptor = self.get_descriptor_by_name(old_base.package,
                                                          old_base.name,
                                                          old_base.namespace)
            self.update_registry(desc.module, desc.package, desc.name, 
                                 desc.namespace, base_descriptor)

    def get_module_by_name(self, identifier, name, namespace=None):
        """get_module_by_name(name: string): class

        Returns the VisTrails module (the class) registered under the
        given name.

        """
        return self.get_descriptor_by_name(identifier, name, namespace).module

    def has_descriptor_with_name(self, identifier, name, namespace=None):
        if namespace is not None and namespace.strip() == "":
            namespace = None
        return (identifier, name, namespace) in self.descriptors
    has_module = has_descriptor_with_name

    def get_descriptor_by_name(self, identifier, name, namespace=None):
        """get_descriptor_by_name(package_identifier,
                                  module_name,
                                  namespace) -> ModuleDescriptor

        Raises ModuleRegistry.MissingModulePackage if lookup fails.
        """
        if namespace is not None and namespace.strip() == "":
            namespace = None
        try:
            return self.descriptors[(identifier, name, namespace)]
        except KeyError:
            if identifier not in self.packages:
                msg = ("Cannot find package %s: it is missing" % identifier)
                raise self.MissingModulePackage(identifier, name, namespace)
            else:
                if namespace is None:
                    key = name
                else:
                    key = name + ':' + namespace
                # key = name if namespace is None else name + ':' + namespace
                msg = ("Package %s does not contain module %s" %
                       (identifier, key))
                raise self.MissingModulePackage(identifier, name, namespace)

    def get_descriptor(self, module):
        """get_descriptor(module: class) -> ModuleDescriptor

        Returns the ModuleDescriptor of a given vistrails module (a
        class that subclasses from modules.vistrails_module.Module)

        """
        # assert type(module) == type
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
        
    def module_source_ports(self, do_sort, identifier, module_name, 
                            namespace=None):
        descriptor = self.get_descriptor_by_name(identifier, module_name, 
                                                 namespace)
        ports = {}
        for desc in reversed(self.get_module_hierarchy(descriptor)):
            ports.update(self.module_ports('output', desc))
        all_ports = ports.values()
        if do_sort:
            all_ports.sort(key=lambda x: (x.sort_key, x.id))
        return all_ports

    def module_destination_ports(self, do_sort, identifier, module_name,
                                 namespace=None):
        descriptor = self.get_descriptor_by_name(identifier, module_name, 
                                                 namespace)
        ports = {}
        for desc in reversed(self.get_module_hierarchy(descriptor)):
            ports.update(self.module_ports('input', desc))
        all_ports = ports.values()
        if do_sort:
            all_ports.sort(key=lambda x: (x.sort_key, x.id))
        return all_ports

    ##########################################################################
    # Legacy

    def get_descriptor_from_name_only(self, name):
        """get_descriptor_from_name_only(name) -> descriptor

        This tries to return a descriptor from a name without a
        package. The call should only be used for converting from
        legacy vistrails to new ones. For one, it is slow on misses. 

        """
        matches = [x for x in
                   self.descriptors.iterkeys()
                   if x[1] == name]
        if len(matches) == 0:
            raise self.MissingModulePackage("<unknown package>",
                                            name,
                                            None)
        if len(matches) > 1:
            raise Exception("ambiguous resolution...")
        k = matches[0]
        result = self.get_descriptor_by_name(*k)
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
            return core.cache.hasher.Hasher.module_signature(module, chm)
        c = descriptor.hasher_callable()
        if c:
            return c(pipeline, module, chm)
        else:
            return core.cache.hasher.Hasher.module_signature(module, chm)

    def get_module_color(self, identifier, name, namespace=None):
        return self.get_descriptor_by_name(identifier, name, namespace).module_color()

    def get_module_fringe(self, identifier, name, namespace=None):
        return self.get_descriptor_by_name(identifier, name, namespace).module_fringe()

    def update_registry(self, module, identifier, name, namespace, 
                        base_descriptor):
        if namespace is not None and not namespace.strip():
            namespace = None

        # create descriptor
        descriptor_id = self.idScope.getNewId(ModuleDescriptor.vtType)
        descriptor = ModuleDescriptor(id=descriptor_id,
                                      module=module,
                                      package=identifier,
                                      base_descriptor=base_descriptor,
                                      name=name,
                                      namespace=namespace,
                                      )

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
                                  )
            self.add_package(package)
        else:
            package = self.packages[identifier]
        self.add_descriptor(descriptor, package)

        if module is not None:
            self._module_key_map[module] = (identifier, name, namespace)
        return descriptor

    def auto_add_ports(self, module):
        """auto_add_module(module or (module, kwargs)): add
        input/output ports to registry. Don't call this directly - it is
        meant to be used by the packagemanager, when inspecting the package
        contents."""
        if hasattr(module, '_input_ports'):
            for (port_name, port_types) in module._input_ports:
                self.add_input_port(module, port_name, port_types)
        if hasattr(module, '_output_ports'):
            for (port_name, port_types) in module._output_ports:
                self.add_output_port(module, port_name, port_types)

    def auto_add_module(self, module):
        """auto_add_module(module or (module, kwargs)): add module
        to registry. Don't call this directly - it is
        meant to be used by the packagemanager, when inspecting the package
        contents."""
        if type(module) == type:
            self.add_module(module)
        elif (type(module) == tuple and
              len(module) == 2 and
              type(module[0]) == type and
              type(module[1]) == dict):
            self.add_module(module[0], **module[1])
            module = module[0]
        else:
            raise TypeError("Expected module or (module, kwargs)")

    def add_module(self, module, **kwargs):
        """add_module(module: class, **kwargs) -> Tree

        kwargs:
          name=None,
          configureWidgetType=None,
          signatureCallable=None,
          moduleColor=None,
          moduleFringe=None,
          moduleLeftFringe=None,
          moduleRightFringe=None,
          abstract=None,
          package=None,
          namespace=None

        Registers a new module with VisTrails. Receives the class
        itself and an optional name that will be the name of the
        module (if not given, uses module.__name__).  This module will
        be available for use in pipelines.

        If moduleColor is not None, then registry stores it so that
        the gui can use it correctly. moduleColor must be a tuple of
        three floats between 0 and 1.

        if moduleFringe is not None, then registry stores it so that
        the gui can use it correctly. moduleFringe must be a list of
        pairs of floating points.  The first point must be (0.0, 0.0),
        and the last must be (0.0, 1.0). This will be used to generate
        custom lateral fringes for module boxes. It must be the case
        that all x values must be positive, and all y values must be
        between 0.0 and 1.0. Alternatively, the user can set
        moduleLeftFringe and moduleRightFringe to set two different
        fringes.

        if package is not None, then we override the current package
        to be the given one. This is only intended to be used with
        local per-module module registries (in other words: if you
        don't know what a local per-module registry is, you can ignore
        this, and never use the 'package' option).        

        If namespace is not None, then we associate a namespace with
        the module. A namespace is essentially appended to the package
        identifier so that multiple modules inside the same package
        can share the same name.

        If signatureCallable is not None, then the cache uses this
        callable as the function to generate the signature for the
        module in the cache. The function should take three
        parameters: the pipeline (of type core.vistrail.Pipeline), the
        module (of type core.vistrail.Module), and a dict that stores
        parameter hashers. This dict is supposed to be passed to
        core/cache/hasher.py:Hasher, in case that needs to be called.

        If constantSignatureCallable is not None, then the cache uses
        this callable as the funciton to generate the signature for
        the given constant.  If this is not None, then the added
        module must be a subclass of Constant.

        Notice: in the future, more named parameters might be added to
        this method, and the order is not specified. Always call
        add_module with named parameters.

        """
        # Setup named arguments. We don't use named parameters so
        # that positional parameter calls fail earlier
        def fetch(name, default):
            r = kwargs.get(name, default)
            try:
                del kwargs[name]
            except KeyError:
                pass
            return r
        name = fetch('name', module.__name__)
        configureWidgetType = fetch('configureWidgetType', None)
        signatureCallable = fetch('signatureCallable', None)
        constantSignatureCallable = fetch('constantSignatureCallable', None)
        moduleColor = fetch('moduleColor', None)
        moduleFringe = fetch('moduleFringe', None)
        moduleLeftFringe = fetch('moduleLeftFringe', None) 
        moduleRightFringe = fetch('moduleRightFringe', None)
        is_abstract = fetch('abstract', False)
        identifier = fetch('package', self._current_package.identifier)
        namespace = fetch('namespace', None)

        key = (identifier, name, namespace)
        
        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed to addModule: %s' % kwargs)
        if key in self.descriptors:
            raise ModuleAlreadyExists(identifier, name)

        # We allow multiple inheritance as long as only one of the superclasses
        # is a subclass of Module.
        candidates = self.get_subclass_candidates(module)
        if len(candidates) != 1:
            raise InvalidModuleClass(module)
        baseClass = candidates[0]
        if not self._module_key_map.has_key(baseClass) :
            raise self.MissingBaseClass(baseClass) 
        
        base_key = self._module_key_map[baseClass]
        base_descriptor = self.descriptors[base_key]

        descriptor = self.update_registry(module, identifier, name, namespace,
                                          base_descriptor)

        descriptor.set_module_abstract(is_abstract)
        descriptor.set_configuration_widget(configureWidgetType)

        if signatureCallable:
            descriptor.set_hasher_callable(signatureCallable)

        if constantSignatureCallable:
            try:
                c = self.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                                'Constant').module
            except self.MissingModulePackage:
                msg = "Constant not found - can't set constantSignatureCallable"
                raise VistrailsInternalError(msg)
            if not issubclass(module, c):
                raise TypeError("To set constantSignatureCallable, module " +
                                "must be a subclass of Constant")
            self._constant_hasher_map[key] = constantSignatureCallable
        descriptor.set_module_color(moduleColor)

        if moduleFringe:
            _check_fringe(moduleFringe)
            leftFringe = list(reversed([(-x, 1.0-y) for (x, y) in moduleFringe]))
            descriptor.set_module_fringe(leftFringe, moduleFringe)
        elif moduleLeftFringe and moduleRightFringe:
            _check_fringe(moduleLeftFringe)
            _check_fringe(moduleRightFringe)
            descriptor.set_module_fringe(moduleLeftFringe, moduleRightFringe)
                 
        self.signals.emit_new_module(descriptor)
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
                         optional=False, sort_key=-1):
        if signature is None and sigstring is None:
            raise VistrailsInternalError("create_port_spec: one of signature "
                                         "and sigstring must be specified")
        spec_id = self.idScope.getNewId(PortSpec.vtType)
        spec = PortSpec(id=spec_id,
                        name=name,
                        type=type,
                        signature=signature,
                        sigstring=sigstring,
                        optional=optional,
                        sort_key=sort_key)
        return spec

    def add_port_spec(self, descriptor, port_spec):
        descriptor.add_port_spec(port_spec)

    def get_port_spec_from_descriptor(self, desc, port_name, port_type):
        try:
            for d in self.get_module_hierarchy(desc):
                if d.has_port_spec(port_name, port_type):
                    return d.get_port_spec(port_name, port_type)
        except ModuleDescriptor.MissingPort:
            print "missing port: '%s:%s|%s', '%s:%s'" % (package, module_name,
                                                         namespace, port_name,
                                                         port_type)
            raise
        return None

    def get_port_spec(self, package, module_name, namespace, 
                      port_name, port_type):
        try:
            desc = self.get_descriptor_by_name(package, module_name, namespace)
            return self.get_port_spec_from_descriptor(desc, port_name, 
                                                      port_type)
        except self.MissingModulePackage:
            print "missing desc: '%s:%s|%s'" % (package, module_name, namespace)
            raise
        return None

    def has_port_spec_from_descriptor(self, desc, port_name, port_type):
        for d in self.get_module_hierarchy(desc):
            if d.has_port_spec(port_name, port_type):
                return True
        return False

    def has_port_spec(self, package, module_name, namespace,
                      port_name, port_type):
        try:
            desc = self.get_descriptor_by_name(package, module_name, namespace)
            return self.has_port_spec_from_descriptor(desc, port_name, 
                                                      port_type)
        except self.MissingModulePackage:
            print "missing desc: '%s:%s|%s'" % (package, module_name, namespace)
            raise
        return None        

    def add_port(self, descriptor, port_name, port_type, port_sig=None, 
                 port_sigstring=None, optional=False, sort_key=-1):
        spec = self.create_port_spec(port_name, port_type, port_sig,
                                     port_sigstring, optional, sort_key)
        descriptor.add_port_spec(spec)
        if port_type == 'input':
            self.signals.emit_new_input_port(descriptor.identifier,
                                             descriptor.name, port_name, spec)
        elif port_type == 'output':
            self.signals.emit_new_output_port(descriptor.identifier,
                                             descriptor.name, port_name, spec)

    def add_input_port(self, module, portName, portSignature, 
                       optional=False, sort_key=-1):
        """add_input_port(module: class,
                          portName: string,
                          portSignature: string,
                          optional=False,
                          sort_key=-1) -> None

        Registers a new input port with VisTrails. Receives the module
        that will now have a certain port, a string representing the
        name, and a signature of the port, described in
        doc/module_registry.txt. Optionally, it receives whether the
        input port is optional."""
        descriptor = self.get_descriptor(module)
        self.add_port(descriptor, portName, 'input', portSignature, None, 
                      optional, sort_key)

    def add_output_port(self, module, portName, portSignature, 
                        optional=False, sort_key=-1):
        """add_output_port(module: class,
                           portName: string,
                           portSignature: string,
                           optional=False,
                           sort_key=-1) -> None

        Registers a new output port with VisTrails. Receives the
        module that will now have a certain port, a string
        representing the name, and a signature of the port, described
        in doc/module_registry.txt. Optionally, it receives whether
        the output port is optional."""
        descriptor = self.get_descriptor(module)
        self.add_port(descriptor, portName, 'output', portSignature, None, 
                      optional, sort_key)

    def create_package(self, codepath, load_configuration=True):
        package_id = self.idScope.getNewId(Package.vtType)
        package = Package(id=package_id,
                          codepath=codepath,
                          load_configuration=load_configuration)
        return package

    def initialize_package(self, package):
        if package.initialized():
            return
        print "Initializing", package.codepath
        if package.identifier not in self.packages:
            self.add_package(package)
        self.set_current_package(package)
        try:
            package.module.initialize()
            # Perform auto-initialization
            if hasattr(package.module, '_modules'):
                modules = _toposort_modules(package.module._modules)
                # We add all modules before adding ports because
                # modules inside package might use each other as ports
                for module in modules:
                    self.auto_add_module(module)
                for module in modules:
                    self.auto_add_ports(module)
        except Exception, e:
            raise package.InitializationFailed(package, e, 
                                               traceback.format_exc())

        # The package might have decided to rename itself, let's store that
        self.set_current_package(None)
        package._initialized = True 

    def delete_module(self, identifier, module_name, namespace=None):
        """deleteModule(module_name): Removes a module from the registry."""
        descriptor = self.get_descriptor_by_name(identifier, module_name, 
                                                 namespace)
        assert len(descriptor.children) == 0
        self.signals.emit_deleted_module(descriptor)
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
        m_package = self.packages[package.identifier]
        for descriptor in m_package.descriptor_list:
            graph.add_vertex(descriptor.sigstring)
        for descriptor in m_package.descriptor_list:            
            base_id = descriptor.base_descriptor_id
            if base_id in m_package.descriptors_by_id:
                base_descriptor = \
                    m_package.descriptors_by_id[descriptor.base_descriptor_id]
                graph.add_edge(descriptor.sigstring, base_descriptor.sigstring)

        top_sort = graph.vertices_topological_sort()
        # set up fast removal of model
        for sigstring in top_sort:
            self.delete_module(*(sigstring.split(':')))
        self.delete_package(m_package)
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
        constant_desc = \
            self.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                        'Constant')
        return all(self.is_descriptor_subclass(d, constant_desc) 
                   for d in port_spec.descriptors())

    def method_ports(self, module_descriptor):
        """method_ports(module_descriptor: ModuleDescriptor) 
              -> list of PortSpecs

        Returns the list of ports that can also be interpreted as
        method calls. These are the ones whose spec contains only
        subclasses of Constant."""
        # module_descriptor = self.get_descriptor(module)
        # FIXME don't hardcode this

        # do lookups of methods in the global registry!
        global_registry = get_module_registry()
        return [spec for spec in \
                    self.destination_ports_from_descriptor(module_descriptor)
                if global_registry.is_method(spec)]

    def port_and_port_spec_match(self, port, port_spec):
        """port_and_port_spec_match(port: Port, port_spec: PortSpec) -> bool
        Checks if port is similar to port_spec or not.  These ports must
        have the same name and type"""
        if PortSpec.port_type_map.inverse[port.type] != port_spec.type:
            return False
        if port.name != port_spec.name:
            return False
        return self.are_specs_matched(port, port_spec)

    def ports_can_connect(self, sourceModulePort, destinationModulePort):
        """ports_can_connect(sourceModulePort,destinationModulePort) ->
        Boolean returns true if there could exist a connection
        connecting these two ports."""
        if sourceModulePort.type == destinationModulePort.type:
            return False
        return self.are_specs_matched(sourceModulePort, destinationModulePort)

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

    def are_specs_matched(self, sub, super):
        """ are_specs_matched(sub: Port, super: Port) -> bool        
        Check if specs of sub and super port are matched or not
        
        """
        variantType = core.modules.basic_modules.Variant
        variant_desc = \
            self.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                        'Variant')
        # sometimes sub is coming None
        # I don't know if this is expected, so I will put a test here
        sub_descs = []
        if sub:
            sub_descs = sub.descriptors()
        if sub_descs == [variant_desc]:
            return True
        super_descs = []
        if super:
            super_descs = super.descriptors()
        if super_descs == [variant_desc]:
            return True

        if len(sub_descs) != len(super_descs):
            return False
        
        for (sub_desc, super_desc) in izip(sub_descs, super_descs):
            if (sub_desc == variant_desc or super_desc == variant_desc):
                continue
            if not self.is_descriptor_subclass(sub_desc, super_desc):
                return False
        return True

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
                if issubclass(klass, core.modules.vistrails_module.Module)]
        
    def get_input_port_spec(self, module, portName):
        """ get_input_port_spec(module: Module, portName: str) ->
        spec-tuple Return the output port of a module given the module
        and port name.

        FIXME: This should be renamed.
        
        """
        descriptor = self.get_descriptor_by_name(module.package, module.name, 
                                                 module.namespace)
        if module.registry:
            reg = module.registry
        else:
            reg = self
        moduleHierarchy = reg.get_module_hierarchy(descriptor)
        for des in moduleHierarchy:
            if (portName, 'input') in des.port_specs:
                return des.port_specs[(portName, 'input')]
        return None

    def get_output_port_spec(self, module, portName):
        """ get_output_port_spec(module: Module, portName: str) -> spec-tuple        
        Return the output port of a module given the module
        and port name.

        FIXME: This should be renamed.
        
        """
        descriptor = self.get_descriptor_by_name(module.package, module.name, 
                                                 module.namespace)
        if module.registry:
            reg = module.registry
        else:
            reg = self
        moduleHierarchy = reg.get_module_hierarchy(descriptor)
        for des in moduleHierarchy:
            if (portName, 'output') in des.port_specs:
                return des.port_specs[(portName, 'output')]
        return None

    @staticmethod
    def get_subclass_candidates(module):
        """get_subclass_candidates(module) -> [class]

        Tries to eliminate irrelevant mixins for the hierarchy. Returns all
        base classes that subclass from Module."""
        return [klass
                for klass in module.__bases__
                if issubclass(klass, core.modules.vistrails_module.Module)]

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
        return descriptor.configuration_widget()
        

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

import unittest

class TestModuleRegistry(unittest.TestCase):

    def test_portspec_construction(self):
        from core.modules.basic_modules import Float, Integer
        t1 = PortSpec(signature=Float)
        t2 = PortSpec(signature=[Float])
        self.assertEquals(t1, t2)

        t1 = PortSpec(signature=[Float, Integer])
        t2 = PortSpec(signature=[Integer, Float])
        self.assertNotEquals(t1, t2)
