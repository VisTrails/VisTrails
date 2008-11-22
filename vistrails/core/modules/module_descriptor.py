############################################################################
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

import copy

from core.utils import VistrailsInternalError
from core.vistrail.port_spec import PortSpec, PortEndPoint
import core.debug
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
      custom configuration widget for the class.
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

    class MissingPort(Exception):
        def __init__(self, name, type):
            import traceback
            traceback.print_stack()
            Exception.__init__(self)
            self._name = name
            self._type = type
        def __str__(self):
            return "Missing port: %s, %s" % (self._name, self._type)

    def __init__(self, *args, **kwargs):
#         module, identifier, base_descriptor=None,
#                  name=None, namespace=None):

        self.children = []
        if 'module' in kwargs:
            self.module = kwargs['module']
            if 'name' not in kwargs:
                kwargs['name'] = self.module.__name__
            del kwargs['module']
        else:
            self.module = None
        if 'base_descriptor' in kwargs:
            self.base_descriptor = kwargs['base_descriptor']
            if 'base_descriptor_id' not in kwargs:
                kwargs['base_descriptor_id'] = self.base_descriptor.id
            del kwargs['base_descriptor']
            self._port_count = self.base_descriptor._port_count
            self.base_descriptor.children.append(self)
        else:
            self.base_descriptor = None
            self._port_count = 0
        # rename identifier to package for db
        if 'identifier' in kwargs:
            if 'package' not in kwargs:
                kwargs['package'] = kwargs['identifier']
            del kwargs['identifier']
        if 'base_descriptor_id' not in kwargs:
            kwargs['base_descriptor_id'] = -1
        DBModuleDescriptor.__init__(self, *args, **kwargs)

        self.port_specs = self.db_portSpecs_name_index

        self._abstraction_refs = 1
        self._is_abstract = False
        self._configuration_widget = None
        self._left_fringe = None
        self._right_fringe = None
        self._module_color = None
        self._hasher_callable = None
        self._widget_item = None

    def __copy__(self):
        return ModuleDescriptor.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModuleDescriptor.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ModuleDescriptor
        cp.base_descriptor = self.base_descriptor
        cp._abstraction_refs = self._abstraction_refs
        cp._port_count = self._port_count
        cp._is_abstract = self._is_abstract
        cp._configuration_widget = self._configuration_widget
        cp._left_fringe = self._left_fringe
        cp._right_fringe = self._right_fringe
        cp._module_color = self._module_color
        cp._hasher_callable = self._hasher_callable
        cp._widget_item = self._widget_item
        
        # FIXME this will break things, I think
        cp.children = copy.copy(self.children)
        cp.port_specs = cp.db_portSpecs_name_index
        return cp
        
    @staticmethod
    def convert(_desc):
        if _desc.__class__ == ModuleDescriptor:
            return
        _desc.__class__ = ModuleDescriptor
        
        # do more init stuff
        _desc.children = []
        _desc.base_descriptor = None
        _desc._port_count = 0
        _desc._abstraction_refs = 1
        _desc._is_abstract = False
        _desc._configuration_widget = None
        _desc._left_fringe = None
        _desc._right_fringe = None
        _desc._module_color = None
        _desc._hasher_callable = None
        _desc._widget_item = None
        _desc.port_specs = _desc.db_portSpecs_name_index
        
    ##########################################################################
    # Properties

    id = DBModuleDescriptor.db_id
    name = DBModuleDescriptor.db_name
    identifier = DBModuleDescriptor.db_package
    package = DBModuleDescriptor.db_package
    namespace = DBModuleDescriptor.db_namespace
    base_descriptor_id = DBModuleDescriptor.db_base_descriptor_id
    port_specs_list = DBModuleDescriptor.db_portSpecs
    
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
            _check_fringe(left_fringe)
            _check_fringe(right_fringe)
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
            raise self.MissingPort(name, port_type)
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



