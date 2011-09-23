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
from itertools import izip

from core.vistrail.annotation import Annotation
from core.vistrail.location import Location
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.port_spec import PortSpec, PortEndPoint
from db.domain import DBGroup

from core.utils import NoSummon, VistrailsInternalError, report_stack
from core.modules.basic_modules import identifier as basic_pkg, \
    version as basic_pkg_version
import core.modules.sub_module
import core.modules.module_registry
from core.modules.module_registry import get_module_registry, ModuleRegistry

class Group(DBGroup, Module):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        if 'pipeline' in kwargs:
            kwargs['workflow'] = kwargs['pipeline']
            del kwargs['pipeline']
        DBGroup.__init__(self, *args, **kwargs)
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
        Module.set_defaults(self, other)

    def setup_indices(self):        
        # delay this until needed (on materialize)
        self._port_specs = None
        self._port_specs_id_index = None
        # self.make_port_specs()

    def __copy__(self):
        return Group.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBGroup.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Group
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_group):
        if _group.__class__ == Group:
            return
        _group.__class__ = Group
        if _group.db_location:
            Location.convert(_group.db_location)
        if _group.db_workflow:
            from core.vistrail.pipeline import Pipeline
            Pipeline.convert(_group.db_workflow)
	for _function in _group.db_functions:
	    ModuleFunction.convert(_function)
        for _annotation in _group.db_get_annotations():
            Annotation.convert(_annotation)
        _group.set_defaults()

    ##########################################################################
    # Properties

    # We need to repeat these here because Module uses DBModule. ...
    id = DBGroup.db_id
    cache = DBGroup.db_cache
    annotations = DBGroup.db_annotations
    location = DBGroup.db_location
    center = DBGroup.db_location
    # version = DBGroup.db_version
    # name = DBGroup.db_name
    # label = DBGroup.db_name
    # namespace = DBGroup.db_namespace
    # package = DBGroup.db_package

    name = 'Group'
    label = 'Group'
    package = basic_pkg
    namespace = None
    version = basic_pkg_version
    internal_version = ''

    def summon(self):
        result = self.module_descriptor.module()
        result.pipeline = self.pipeline
        if self._port_specs is None:
            self.make_port_specs()
        result.input_remap = self._input_remap
        result.output_remap = self._output_remap
        if self.cache != 1:
            result.is_cacheable = lambda *args: False
        if hasattr(result, 'input_ports_order'):
            result.input_ports_order = [p.name for p in self.destinationPorts()]
        if hasattr(result, 'output_ports_order'):
            result.output_ports_order = [p.name for p in self.sourcePorts()]
        result.registry = get_module_registry()
        return result

    def is_group(self):
        return True

    def _get_pipeline(self):
        return self.db_workflow
    def _set_pipeline(self, pipeline):
        self.db_workflow = pipeline
        self.setup_indices()
    pipeline = property(_get_pipeline, _set_pipeline)
    workflow = pipeline
    
    # override these from the Module class with defaults
    # these are "local" port_specs, but Group's are "registry"
    def _get_port_specs(self):
        if self._port_specs_id_index is None:
            if self._port_specs is None:
                self.make_port_specs()
            self._port_specs_id_index = {}
            self._port_specs_id_index = \
                dict([(p.id, p) for p in self._port_specs.itervalues()])
        return self._port_specs_id_index
    port_specs = property(_get_port_specs)

    def _get_port_spec_list(self):
        if self._port_specs is None:
            self.make_port_specs()
        return self._port_specs.values()
    port_spec_list = property(_get_port_spec_list)

    def has_portSpec_with_name(self, name):
        if self._port_specs is None:
            self.make_port_specs()
        return name in self._port_specs

    def get_portSpec_by_name(self, name):
        if self._port_specs is None:
            self.make_port_specs()
        if name in self._port_specs:
            return self._port_specs[name]
        return None

    def add_port_spec(self, spec):
        # operate on self._port_specs instead of db level
        if self._port_specs is None:
            self.make_port_specs()
        self._port_specs[(spec.name, spec.type)] = spec
        self.port_specs[spec.id] = spec
        if spec.type == 'input':
            self._input_port_specs.append(spec)
        elif spec.type == 'output':
            self._output_port_specs.append(spec)
    def delete_port_spec(self, spec):
        if spec.type == 'input':
            self._input_port_specs.remove(spec)
        elif spec.type == 'output':
            self._output_port_specs.remove(spec)
        # operate on self._port_specs instead of db level
        del self._port_specs[(spec.name, spec.type)]
        del self.port_specs[spec.id]

    def _get_input_port_specs(self):
        if self._port_specs is None:
            self.make_port_specs()
        return Module._get_input_port_specs(self)
    input_port_specs = property(_get_input_port_specs)
    def _get_output_port_specs(self):
        if self._port_specs is None:
            self.make_port_specs()
        return Module._get_output_port_specs(self)
    output_port_specs = property(_get_output_port_specs)

    def get_port_spec_info(self, module):
        return core.modules.sub_module.get_port_spec_info(self.pipeline, 
                                                          module)

    def make_port_specs(self):
        self._port_specs = {}
        self._input_port_specs = []
        self._output_port_specs = []
        self._input_remap = {}
        self._output_remap = {}
        if self.pipeline is None:
            return

        registry = get_module_registry()
        for module in self.pipeline.module_list:
            if module.name == 'OutputPort' and module.package == basic_pkg:
                (port_name, sigstring, optional, _) = \
                    self.get_port_spec_info(module)
                port_spec = registry.create_port_spec(port_name, 'output',
                                                      None, sigstring,
                                                      optional)
                self._port_specs[(port_name, 'output')] = port_spec
                self._output_port_specs.append(port_spec)
                self._output_remap[port_name] = module
            elif module.name == 'InputPort' and module.package == basic_pkg:
                (port_name, sigstring, optional, _) = \
                    self.get_port_spec_info(module)
                port_spec = registry.create_port_spec(port_name, 'input',
                                                      None, sigstring,
                                                      optional)
                self._port_specs[(port_name, 'input')] = port_spec
                self._input_port_specs.append(port_spec)
                self._input_remap[port_name] = module

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an 
        GroupModule object. 

        """
        rep = '<group id="%s">'
        rep += str(self.location)
        rep += str(self.functions)
        rep += str(self.annotations)
        rep += '</group>'
        return  rep % str(self.id)

    def __eq__(self, other):
        """ __eq__(other: GroupModule) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        if self.location != other.location:
            return False
        if len(self.functions) != len(other.functions):
            return False
        if len(self.annotations) != len(other.annotations):
            return False
        for f,g in izip(self.functions, other.functions):
            if f != g:
                return False
        for f,g in izip(self.annotations, other.annotations):
            if f != g:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


################################################################################
# Testing

import unittest
from db.domain import IdScope

class TestGroup(unittest.TestCase):

    def create_group(self, id_scope=IdScope()):
        from core.vistrail.location import Location
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module_param import ModuleParam

        params = [ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                                  type='Int',
                                  val='1')]
        functions = [ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                    name='value',
                                    parameters=params)]
        location = Location(id=id_scope.getNewId(Location.vtType),
                            x=12.342,
                            y=-19.432)
        module = \
            Group(id=id_scope.getNewId(Group.vtType),
                  location=location,
                  functions=functions,
                  )
        return module

    def test_copy(self):
        """Check that copy works correctly"""
        
        id_scope = IdScope()
        m1 = self.create_group(id_scope)
        m2 = copy.copy(m1)
        self.assertEquals(m1, m2)
        self.assertEquals(m1.id, m2.id)
        m3 = m1.do_copy(True, id_scope, {})
        self.assertEquals(m1, m3)
        self.assertNotEquals(m1.id, m3.id)

    def test_serialization(self):
        """ Check that serialize and unserialize are working properly """
        import core.db.io

        m1 = self.create_group()
        xml_str = core.db.io.serialize(m1)
        m2 = core.db.io.unserialize(xml_str, Group)
        self.assertEquals(m1, m2)
        self.assertEquals(m1.id, m2.id)
