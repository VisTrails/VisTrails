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
# Check for testing
""" This module defines the class Module 
"""
from __future__ import division

import copy
from itertools import izip
import weakref

from vistrails.db.domain import DBModule
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.location import Location
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.core.utils import NoSummon
from vistrails.core.modules.module_registry import get_module_registry

import unittest

################################################################################

# A Module stores not only the information, but a method (summon) that
# creates a 'live' object, subclass of core/modules/vistrail_module/Module

class Module(DBModule):
    """ Represents a module from a Pipeline """

    ##########################################################################
    # Constructor and copy

    def __init__(self, *args, **kwargs):
        DBModule.__init__(self, *args, **kwargs)
        if self.cache is None:
            self.cache = 1
        if self.id is None:
            self.id = -1
        if self.location is None:
            self.location = Location(x=-1.0, y=-1.0)
        if self.name is None:
            self.name = ''
        if self.package is None:
            self.package = ''
        if self.version is None:
            self.version = ''
        self.set_defaults()

    def set_defaults(self, other=None):
        if other is None:
            self.visible_input_ports = set()
            self.visible_output_ports = set()
            self.connected_input_ports = {}
            self.connected_output_ports = {}
            self.is_valid = False
            self.is_breakpoint = False
            self.is_watched = False
            self._descriptor_info = None
            self._module_descriptor = None
            self.list_depth = 0
            self.iterated_ports = []
        else:
            self.visible_input_ports = copy.copy(other.visible_input_ports)
            self.visible_output_ports = copy.copy(other.visible_output_ports)
            self.connected_input_ports = copy.copy(other.connected_input_ports)
            self.connected_output_ports = \
                copy.copy(other.connected_output_ports)
            self.is_valid = other.is_valid
            self.is_breakpoint = other.is_breakpoint
            self.is_watched = other.is_watched
            self._descriptor_info = None
            self.list_depth = other.list_depth
            self.iterated_ports = other.iterated_ports
            self._module_descriptor = other._module_descriptor
        if not self.namespace:
            self.namespace = None
        self.function_idx = self.db_functions_id_index
        self.setup_indices()

    def setup_indices(self):
        self._input_port_specs = []
        self._output_port_specs = []
        for port_spec in self.port_spec_list:
            if port_spec.type == 'input':
                self._input_port_specs.append(port_spec)
            elif port_spec.type == 'output':
                self._output_port_specs.append(port_spec)

    def __copy__(self):
        """__copy__() -> Module - Returns a clone of itself"""
        return Module.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModule.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Module
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_module):
        if _module.__class__ == Module:
            return
        _module.__class__ = Module
        for _port_spec in _module.db_portSpecs:
            PortSpec.convert(_port_spec)
        if _module.db_location:
            Location.convert(_module.db_location)
        for _function in _module.db_functions:
            ModuleFunction.convert(_function)
        for _annotation in _module.db_get_annotations():
            Annotation.convert(_annotation)
        for _control_parameter in _module.db_get_controlParameters():
            ModuleControlParam.convert(_control_parameter)
        _module.set_defaults()

    ##########################################################################
    # CONSTANTS
        
    VISTRAIL_VAR_ANNOTATION = '__vistrail_var__'
    INLINE_WIDGET_ANNOTATION = '__inline_widgets__'

    ##########################################################################

    id = DBModule.db_id
    cache = DBModule.db_cache
    annotations = DBModule.db_annotations
    control_parameters = DBModule.db_controlParameters
    location = DBModule.db_location
    center = DBModule.db_location
    name = DBModule.db_name
    label = DBModule.db_name
    namespace = DBModule.db_namespace
    package = DBModule.db_package
    version = DBModule.db_version
    port_spec_list = DBModule.db_portSpecs
    internal_version = ''

    # type check this (list, hash)
    def _get_functions(self):
        self.db_functions.sort(key=lambda x: x.db_pos)
        return self.db_functions
    def _set_functions(self, functions):
        # want to convert functions to hash...?
        self.db_functions = functions
    functions = property(_get_functions, _set_functions)
    def add_function(self, function):
        self.db_add_function(function)
    def has_function_with_real_id(self, f_id):
        return self.db_has_function_with_id(f_id)
    def get_function_by_real_id(self, f_id):
        return self.db_get_function_by_id(f_id)
    def delete_function_by_real_id(self, f_id):
        self.db_delete_function(self.db_get_function_by_id(f_id))

    def add_annotation(self, annotation):
        self.db_add_annotation(annotation)
    def delete_annotation(self, annotation):
        self.db_delete_annotation(annotation)
    def has_annotation_with_key(self, key):
        return self.db_has_annotation_with_key(key)
    def get_annotation_by_key(self, key):
        return self.db_get_annotation_by_key(key)        
    def add_control_parameter(self, controlParameter):
        self.db_add_controlParameter(controlParameter)
    def delete_control_parameter(self, controlParameter):
        self.db_delete_controlParameter(controlParameter)
    def has_control_parameter_with_name(self, name):
        return self.db_has_controlParameter_with_name(name)
    def get_control_parameter_by_name(self, name):
        return self.db_get_controlParameter_by_name(name)
    def toggle_breakpoint(self):
        self.is_breakpoint = not self.is_breakpoint
    def toggle_watched(self):
        self.is_watched = not self.is_watched

    def is_vistrail_var(self):
        return self.has_annotation_with_key(Module.VISTRAIL_VAR_ANNOTATION)
    def get_vistrail_var(self):
        return self.get_annotation_by_key(Module.VISTRAIL_VAR_ANNOTATION).value

    def _get_port_specs(self):
        return self.db_portSpecs_id_index
    port_specs = property(_get_port_specs)
    def has_portSpec_with_name(self, name):
        return self.db_has_portSpec_with_name(name)
    def get_portSpec_by_name(self, name):
        return self.db_get_portSpec_by_name(name)
    def add_port_spec(self, spec):
        DBModule.db_add_portSpec(self, spec)
        if spec.type == 'input':
            self._input_port_specs.append(spec)
        elif spec.type == 'output':
            self._output_port_specs.append(spec)
    # override DBModule.db_add_portSpec so that _*_port_specs are updated
    db_add_portSpec = add_port_spec
    def delete_port_spec(self, spec):
        if spec.type == 'input':
            self._input_port_specs.remove(spec)
        elif spec.type == 'output':
            self._output_port_specs.remove(spec)
        DBModule.db_delete_portSpec(self, spec)
    # override DBModule.db_delete_portSpec so that _*_port_specs are updated
    db_delete_portSpec = delete_port_spec

    def _get_input_port_specs(self):
        return sorted(self._input_port_specs, 
                      key=lambda x: (x.sort_key, x.id))
    input_port_specs = property(_get_input_port_specs)
    def _get_output_port_specs(self):
        return sorted(self._output_port_specs, 
                      key=lambda x: (x.sort_key, x.id))
    output_port_specs = property(_get_output_port_specs)

    def _get_descriptor_info(self):
        if self._descriptor_info is None:
            self._descriptor_info = (self.package, self.name, 
                                     self.namespace, self.version,
                                     str(self.internal_version))
        return self._descriptor_info
    descriptor_info = property(_get_descriptor_info)

    def _get_module_descriptor(self):
        if self._module_descriptor is None or \
                self._module_descriptor() is None:
            reg = get_module_registry()
            self._module_descriptor = \
                weakref.ref(reg.get_descriptor_by_name(*self.descriptor_info))
        return self._module_descriptor()
    def _set_module_descriptor(self, descriptor):
        self._module_descriptor = weakref.ref(descriptor)
    module_descriptor = property(_get_module_descriptor, 
                                 _set_module_descriptor)

    def _get_editable_input_ports(self):
        if self.has_annotation_with_key(Module.INLINE_WIDGET_ANNOTATION):
            values = self.get_annotation_by_key(
                             Module.INLINE_WIDGET_ANNOTATION).value.split(',')
            return set() if values == [''] else set(values)
        elif get_module_registry(
                   ).is_constant_module(self.module_descriptor.module):
            # Show value by default on constant modules
            return set(['value'])
        return set()
    editable_input_ports = property(_get_editable_input_ports)

    def get_port_spec(self, port_name, port_type):
        """get_port_spec(port_name: str, port_type: str: ['input' | 'output'])
             -> PortSpec

        """
        if self.has_portSpec_with_name((port_name, port_type)):
            return self.get_portSpec_by_name((port_name, port_type))
        desc = self.module_descriptor
        reg = get_module_registry()
        return reg.get_port_spec_from_descriptor(desc, port_name, port_type)

    def has_port_spec(self, port_name, port_type):
        if self.has_portSpec_with_name((port_name, port_type)):
            return True
        reg = get_module_registry()
        desc = self.module_descriptor
        return reg.has_port_spec_from_descriptor(desc, port_name, port_type)

    def summon(self):
        result = self.module_descriptor.module()
        result.transfer_attrs(self)

        # FIXME this may not be quite right because we don't have self.registry
        # anymore.  That said, I'm not sure how self.registry would have
        # worked for hybrids...
        result.registry = get_module_registry()
        return result

    def is_group(self):
        return False
    def is_abstraction(self):
        return False

    def getNumFunctions(self):
        """getNumFunctions() -> int - Returns the number of functions """
        return len(self.functions)

    def sourcePorts(self):
        """sourcePorts() -> list of Port 
        Returns list of source (output) ports module supports.

        """
        registry = get_module_registry()
        desc = self.module_descriptor
        ports = registry.module_source_ports_from_descriptor(True, desc)
        ports.extend(self.output_port_specs)
        return ports
    
    def destinationPorts(self):
        """destinationPorts() -> list of Port 
        Returns list of destination (input) ports module supports

        """
        registry = get_module_registry()
        desc = self.module_descriptor
        ports = registry.module_destination_ports_from_descriptor(True, desc)
        ports.extend(self.input_port_specs)
        return ports

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(other) != type(self):
            print "Type mismatch"
            print type(self), type(other)
        elif self.id != other.id:
            print "id mismatch"
            print self.id, other.id
        elif self.name != other.name:
            print "name mismatch"
            print self.name, other.name
        elif self.cache != other.cache:
            print "cache mismatch"
            print self.cache, other.cache
        elif self.location != other.location:
            print "location mismatch"
            # FIXME Location has no show_comparison
            # self.location.show_comparison(other.location)
        elif len(self.functions) != len(other.functions):
            print "function length mismatch"
            print len(self.functions), len(other.functions)
        else:
            for f, g in izip(self.functions, other.functions):
                if f != g:
                    print "function mismatch"
                    f.show_comparison(g)
                    return
            print "No difference found"
            assert self == other

    ##########################################################################
    # Operators

    def __str__(self):
        """__str__() -> str Returns a string representation of itself. """
        def get_name():
            if self.namespace:
                return self.namespace + '|' + self.name
            return self.name
        return ("(Module '%s:%s' id=%s functions:%s port_specs:%s annotations:%s control_parameters:%s)@%X" %
                (self.package,
                 get_name(),
                 self.id,
                 [str(f) for f in self.functions],
                 [str(port_spec) for port_spec in self.db_portSpecs],
                 [str(a) for a in self.annotations],
                 [str(c) for c in self.control_parameters],
                 id(self)))

    def __eq__(self, other):
        """ __eq__(other: Module) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        if self.package != other.package:
            return False
        if self.cache != other.cache:
            return False
        if self.location != other.location:
            return False
        if len(self.functions) != len(other.functions):
            return False
        if len(self.annotations) != len(other.annotations):
            return False
        if len(self.control_parameters) != len(other.control_parameters):
            return False
        for f, g in izip(self.functions, other.functions):
            if f != g:
                return False
        for f, g in izip(self.annotations, other.annotations):
            if f != g:
                return False
        for f, g in izip(self.control_parameters, other.control_parameters):
            if f != g:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    ##########################################################################
    # Properties


################################################################################
# Testing


class TestModule(unittest.TestCase):

    def create_module(self, id_scope=None):
        from vistrails.core.modules.basic_modules import identifier as basic_pkg
        from vistrails.db.domain import IdScope
        if id_scope is None:
            id_scope = IdScope()
        
        params = [ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                                  type='Int',
                                  val='1')]
        functions = [ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                    name='value',
                                    parameters=params)]
        control_parameters = [ModuleControlParam(id=id_scope.getNewId(ModuleControlParam.vtType),
                                  name='combiner',
                                  value='pairwise')]
        module = Module(id=id_scope.getNewId(Module.vtType),
                        name='Float',
                        package=basic_pkg,
                        functions=functions,
                        controlParameters=control_parameters)
        return module

    def test_copy(self):
        """Check that copy works correctly"""
        from vistrails.db.domain import IdScope
        
        id_scope = IdScope()
        m1 = self.create_module(id_scope)
        m2 = copy.copy(m1)
        self.assertEquals(m1, m2)
        self.assertEquals(m1.id, m2.id)
        m3 = m1.do_copy(True, id_scope, {})
        self.assertEquals(m1, m3)
        self.assertNotEquals(m1.id, m3.id)

    def test_serialization(self):
        """ Check that serialize and unserialize are working properly """
        import vistrails.core.db.io

        m1 = self.create_module()
        xml_str = vistrails.core.db.io.serialize(m1)
        m2 = vistrails.core.db.io.unserialize(xml_str, Module)
        self.assertEquals(m1, m2)
        self.assertEquals(m1.id, m2.id)
        
    def testEq(self):
        """Check correctness of equality operator."""
        x = Module()
        self.assertNotEquals(x, None)

    def testAccessors(self):
        """Check that accessors are working."""
        x = Module()
        self.assertEquals(x.id, -1)
        x.id = 10
        self.assertEquals(x.id, 10)
        self.assertEquals(x.cache, 1)
        x.cache = 1
        self.assertEquals(x.cache, 1)
        self.assertEquals(x.location.x, -1.0)
        x.location = Location(x=1, y=x.location.y)
        self.assertEquals(x.location.x, 1)
        self.assertEquals(x.name, "")

    def testSummonModule(self):
        """Check that summon creates a correct module"""
        from vistrails.core.modules.basic_modules import identifier as basic_pkg

        x = Module()
        x.name = "String"
        x.package = basic_pkg
        try:
            registry = get_module_registry()
            c = x.summon()
            m = registry.get_descriptor_by_name(basic_pkg, 'String').module
            assert isinstance(c, m)
        except NoSummon:
            msg = "Expected to get a String object, got a NoSummon exception"
            self.fail(msg)

    def test_constructor(self):
        m1_param = ModuleParam(val="1.2",
                               type="Float",
                               alias="",
                               )
        m1_function = ModuleFunction(name="value",
                                     parameters=[m1_param],
                                     )
        m1 = Module(id=0,
                    name='Float',
                    functions=[m1_function],
                    )
                    
        m2 = Module()
        m2.name = "Float"
        m2.id = 0
        f = ModuleFunction()
        f.name = "value"
        m2.functions.append(f)
        param = ModuleParam()
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        f.params.append(param)
        assert m1 == m2

    def test_str(self):
        m = Module(id=0,
                   name='Float',
                   functions=[ModuleFunction(name='value',
                                             parameters=[ModuleParam(type='Int',
                                                                     val='1',
                                                                     )],
                                             )],
                   )
        str(m)
        
if __name__ == '__main__':
    unittest.main()
    
