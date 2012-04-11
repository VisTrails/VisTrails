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

import copy

from core.utils import VistrailsInternalError
from core.vistrail.port_spec import PortSpec, PortEndPoint
import core.debug
import core.modules.module_registry
from db.domain import DBModuleDescriptor

# this is used by add_port to signal a repeated port. Should never
# happen, but it does. Probably means a bug on the dynamic modules
# such as MplPlot and Tuple.  Of course, that also means that we
# should be robust in the presence of these errors, since user-defined
# modules could exhibit this bug

class OverloadedPort(Exception):
    pass

###############################################################################
# ModuleDescriptor

class ModuleDescriptor(DBModuleDescriptor):
    """ModuleDescriptor is a class that holds information about
    modules in the registry. There exists exactly one ModuleDescriptor
    for every registered VisTrails module in the system.

    self.module: reference to the python class that defines the module
    self.name: name of the module
    self.identifier: identifier of the package that module belongs to
    self.input_ports: dictionary of names of input ports to the types
      consumed by the ports
    self.output_ports: dictionary of names of output ports to the types
      produces by the ports
    self.input_ports_optional: dictionary of input port names that records
      whether ports should show up by default on GUI
    self.output_ports_optional: dictionary of output port names that records
      whether ports should show up by default on GUI
    self.port_order: stores a map from names to numbers to order the ports
      in the GUI

    self._is_abstract: whether module is abstract
    self._configuration_widget: reference to the Qt class that provides a
      custom configuration widget for the class.  Note that this can
      be a tuple (path, name) that will be loaded only when needed via
      __import__ (! this is preferred !) or as a QWidget (deprecated)

    self._left_fringe and self._right_fringe: lists of 2D points that
      define a drawing style for modules in the GUI
    self._module_color: color of the module in the GUI

    self._widget_item: stores a reference to the ModuleTreeWidgetItem so
      that when ports are added to modules things get correctly updated.

    self._input_port_cache, self._output_port_cache,
      self._port_caches: Dictionaries for fast port spec lookup,
      created because port spec lookups are sometimes part of hot code
      paths and need to go as fast as possible.
    """

    ##########################################################################

    def __init__(self, *args, **kwargs):
        self.children = []
        if 'module' in kwargs:
            self.module = kwargs['module']
            if 'name' not in kwargs:
                kwargs['name'] = self.module.__name__
            del kwargs['module']
        else:
            self.module = None
        if 'base_descriptor' in kwargs:
            if kwargs['base_descriptor'] is not None:
                self._base_descriptor = kwargs['base_descriptor']
                if 'base_descriptor_id' not in kwargs:
                    kwargs['base_descriptor_id'] = self._base_descriptor.id
                self._port_count = self._base_descriptor._port_count
                self._base_descriptor.children.append(self)
            else:
                self._base_descriptor = None
                self._port_count = 0
            del kwargs['base_descriptor']
        else:
            self._base_descriptor = None
            self._port_count = 0
        # rename identifier to package for db
        if 'identifier' in kwargs:
            if 'package' not in kwargs:
                kwargs['package'] = kwargs['identifier']
            del kwargs['identifier']
        if 'base_descriptor_id' not in kwargs:
            kwargs['base_descriptor_id'] = -1
        DBModuleDescriptor.__init__(self, *args, **kwargs)
        self.set_defaults()

    def set_defaults(self, other=None):
        if other is None:
            self._abstraction_refs = 1
            self._is_abstract = False
            self._configuration_widget = None
            self._left_fringe = None
            self._right_fringe = None
            self._module_color = None
            self._hasher_callable = None
            self._widget_item = None
            self._is_hidden = False
            self._namespace_hidden = False
            self.children = []
            # The ghost attributes represent the original values
            # for the descriptor of an upgraded package subworkflow
            # so it can be displayed with it's original package
            # rather than 'local.abstractions'
            self.ghost_identifier = ''
            self.ghost_package_version = ''
            self.ghost_namespace = None
        else:
            # FIXME this will break things, I think
            self.children = copy.copy(other.children)
            
            self._base_descriptor = other._base_descriptor
            self.module = other.module
            self._port_count = other._port_count
            self._abstraction_refs = self._abstraction_refs
            self._is_abstract = other._is_abstract
            self._configuration_widget = other._configuration_widget
            self._left_fringe = other._left_fringe
            self._right_fringe = other._right_fringe
            self._module_color = other._module_color
            self._hasher_callable = other._hasher_callable
            self._widget_item = other._widget_item
            self._is_hidden = other._is_hidden
            self._namespace_hidden = other._namespace_hidden
            self.ghost_identifier = other.ghost_identifier
            self.ghost_package_version = other.ghost_package_version
            self.ghost_namespace = other.ghost_namespace
        self.port_specs = self.db_portSpecs_name_index
        if self.version is None:
            self.version = ''
        if self.namespace is None:
            self.namespace = ''

    def __copy__(self):
        return ModuleDescriptor.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModuleDescriptor.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleDescriptor
        cp.set_defaults(self)
        return cp
        
    @staticmethod
    def convert(_desc):
        if _desc.__class__ == ModuleDescriptor:
            return
        _desc.__class__ = ModuleDescriptor
        
        for port_spec in _desc.db_portSpecs:
            PortSpec.convert(port_spec)

        # do more init stuff
        _desc.children = []
        _desc.module = None
        _desc._base_descriptor = None
        _desc._port_count = 0
        _desc.set_defaults()

    ##########################################################################
    # Properties

    id = DBModuleDescriptor.db_id
    name = DBModuleDescriptor.db_name
    identifier = DBModuleDescriptor.db_package
    package = DBModuleDescriptor.db_package
    namespace = DBModuleDescriptor.db_namespace
    package_version = DBModuleDescriptor.db_package_version
    version = DBModuleDescriptor.db_version
    base_descriptor_id = DBModuleDescriptor.db_base_descriptor_id
    port_specs_list = DBModuleDescriptor.db_portSpecs
    
    def _get_base_descriptor(self):
        if self._base_descriptor is None and self.base_descriptor_id >= 0:
            from core.modules.module_registry import get_module_registry
            reg = get_module_registry()
            self._base_descriptor = \
                reg.descriptors_by_id[self.base_descriptor_id]
        return self._base_descriptor
    def _set_base_descriptor(self, base_descriptor):
        self._base_descriptor = base_descriptor
        self.base_descriptor_id = base_descriptor.id
    base_descriptor = property(_get_base_descriptor, _set_base_descriptor)

    def _get_sigstring(self):
        if self.db_namespace:
            return self.db_package + ':' + self.db_name + ':' + \
                self.db_namespace
        return self.db_package + ':' + self.db_name
    sigstring = property(_get_sigstring)

    def set_module_abstract(self, v):
        self._is_abstract = v

    def module_abstract(self):
#         if not self.has_ports():
#             return True
        return self._is_abstract

    def set_configuration_widget(self, configuration_widget_type):
        """set_configuration_widget(configuration_widget_type: 
                                        (path, name) tuple or QWidget) -> None
        
        """
        self._configuration_widget = configuration_widget_type

    def configuration_widget(self):
        return self._configuration_widget

    def set_module_color(self, color):
        if color:
            assert type(color) == tuple
            assert len(color) == 3
            for i in 0,1,2:
                assert type(color[i]) == float
        self._module_color = color

    def module_color(self):
        return self._module_color

    def set_module_fringe(self, left_fringe, right_fringe):
        if left_fringe is None:
            assert right_fringe is None
            self._left_fringe = None
            self._right_fringe = None
        else:
            core.modules.module_registry._check_fringe(left_fringe)
            core.modules.module_registry._check_fringe(right_fringe)
            self._left_fringe = left_fringe
            self._right_fringe = right_fringe

    def module_fringe(self):
        if self._left_fringe is None and self._right_fringe is None:
            return None
        return (self._left_fringe, self._right_fringe)

    def module_package(self):
        return self.identifier

    def set_hasher_callable(self, callable_):
        self._hasher_callable = callable_
    def hasher_callable(self):
        return self._hasher_callable

    def _get_is_hidden(self):
        return self._is_hidden
    def _set_is_hidden(self, hidden):
        self._is_hidden = hidden
    is_hidden = property(_get_is_hidden, _set_is_hidden)

    def _get_namespace_hidden(self):
        return self._namespace_hidden
    def _set_namespace_hidden(self, hidden):
        self._namespace_hidden = hidden
    namespace_hidden = property(_get_namespace_hidden, _set_namespace_hidden)

    ##########################################################################
    # Operators

    def __hash__(self):
        return (type(self), self.package, self.name, self.namespace, 
                self.version).__hash__()

    def __eq__(self, other):
        return (self.package == other.package and
                self.name == other.name and
                self.namespace == other.namespace and
                self.version == other.version)

    def __str__(self):
        return ("ModuleDescriptor(id=%s, package=%s, name=%s, namespace=%s, "
                "version=%s, base_descriptor_id=%s)" % \
                    (self.id, self.package, self.name, self.namespace,
                     self.version, self.base_descriptor_id))
 
    ##########################################################################
    # Abstract module detection support

    def set_widget(self, widget_item):
        self._widget_item = widget_item

    def has_ports(self):
        """Returns True is module has any ports (this includes
        superclasses).  This method exists to make automatic abstract
        module detection efficient."""
        return self._port_count > 0

    def port_count(self):
        """Return the total number of available for the module."""
        return self._port_count

    # Signal handling
    def new_input_port(self):
        """Updates needed variables when new input port is added
        to either this module or the superclass."""
        self._port_count += 1
        if self._widget_item:
            self._widget_item.added_input_port()
        for child in self.children:
            child.new_input_port()
        
    def new_output_port(self):
        """Updates needed variables when new output port is added
        to either this module or the superclass."""
        self._port_count += 1
        if self._widget_item:
            self._widget_item.added_output_port()
        for child in self.children:
            child.new_output_port()

    ##########################################################################

    # port_type is 'input' or 'output'
    def has_port_spec(self, name, port_type):
        return self.db_has_portSpec_with_name((name, port_type))

    def get_port_spec(self, name, port_type):
        if not self.db_has_portSpec_with_name((name, port_type)):
            raise Exception("ModuleDescriptor.get_port_spec called when spec "
                            " (%s, %s) doesn't exist" % (name, port_type))
        return self.db_get_portSpec_by_name((name, port_type))

    def set_port_spec(self, name, port_type, port_spec):
        self.db_add_portSpec(port_spec)

    def add_port_spec(self, port_spec):
        self.db_add_portSpec(port_spec)

    def delete_port_spec(self, port_spec):
        self.db_delete_portSpec(port_spec)

    def new_port_spec(self, name, type, signature=None, sigstring=None,
                      optional=False, sort_key=-1):
        # DEPRECATED: create using ModuleRegistry
        if signature is None and sigstring is None:
            raise VistrailsInternalError("new_port_spec: signature and "
                                         "sigstring cannot both be None")
        if sigstring is not None:
            return PortSpec(id=-1,
                            name=name,
                            type=type,
                            sigstring=sigstring,
                            optional=optional,
                            sort_key=sort_key)
        return PortSpec(id=-1,
                        name=name,
                        type=type,
                        signature=signature,
                        optional=optional,
                        sort_key=sort_key)

    def add_input_port(self, name, signature, optional):
        # DEPRECATED: use add_port_spec
        sort_key = len(port_specs_list)
        result = self.new_port_spec(name, 'input', signature=signature, 
                                    optional=optional, sort_key=sort_key)
        self.add_port_spec(result)
        return result
        
    def add_output_port(self, name, signature, optional):
        # DEPRECATED: use add_port_spec
        sort_key = len(port_specs_list)
        result = self.new_port_spec(name, 'output', signature=signature, 
                                    optional=optional, sort_key=sort_key)
        self.add_port_spec(result)
        return result
        
    def delete_input_port(self, name):
        key = (name, 'input')
        if key in self.port_specs:
            self.delete_port_spec(self.port_specs[key])
        else:
            raise VistrailsInternalError("delete_input_port called on "
                                         "nonexistent port '%s'" % name)

    def delete_output_port(self, name):
        key = (name, 'output')
        if key in self.port_specs:
            self.delete_port_spec(self.port_specs[key])
        else:
            raise VistrailsInternalError("delete_output_port called on "
                                         "nonexistent port '%s'" % name)



