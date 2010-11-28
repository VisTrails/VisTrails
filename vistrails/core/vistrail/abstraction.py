############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

from PyQt4.QtCore import QObject
import copy

from core.modules.module_registry import get_module_registry
import core.modules.sub_module 
from core.utils import VistrailsInternalError
from core.vistrail.annotation import Annotation
from core.vistrail.location import Location
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from db.domain import DBAbstraction

class Abstraction(DBAbstraction, Module):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAbstraction.__init__(self, *args, **kwargs)
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
        pass

    def __copy__(self):
        return Abstraction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAbstraction.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Abstraction
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_abstraction):
        if _abstraction.__class__ == Abstraction:
            return
        _abstraction.__class__ = Abstraction
        if _abstraction.db_location:
            Location.convert(_abstraction.db_location)
	for _function in _abstraction.db_functions:
	    ModuleFunction.convert(_function)
        for _annotation in _abstraction.db_get_annotations():
            Annotation.convert(_annotation)
        _abstraction.set_defaults()

    ##########################################################################
    # Properties
    
    # We need to repeat these here because Module uses DBModule. ...
    id = DBAbstraction.db_id
    cache = DBAbstraction.db_cache
    annotations = DBAbstraction.db_annotations
    location = DBAbstraction.db_location
    center = DBAbstraction.db_location
    name = DBAbstraction.db_name
    label = DBAbstraction.db_name
    namespace = DBAbstraction.db_namespace
    package = DBAbstraction.db_package
    version = DBAbstraction.db_version
    internal_version = DBAbstraction.db_internal_version

    def is_abstraction(self):
        return True

    def is_latest_version(self):
        if not hasattr(self, '_is_latest_version'):
            def update_version_status():
                reg = get_module_registry()
                desc = reg.get_descriptor_by_name(self.package, self.name, self.namespace)
                latest_version = desc.module.vistrail.get_latest_version()
                self._is_latest_version = (long(latest_version) == long(self.internal_version))
            reg = get_module_registry()
            QObject.connect(reg.signals, reg.signals.new_abstraction_signal, update_version_status)
            QObject.connect(reg.signals, reg.signals.deleted_abstraction_signal, update_version_status)
            update_version_status()
        return self._is_latest_version

    def _get_pipeline(self):
        return self.module_descriptor.module.pipeline
    pipeline = property(_get_pipeline)

    def _get_vistrail(self):
        return self.module_descriptor.module.vistrail
    vistrail = property(_get_vistrail)

    # override db-mirrored accesses in Module
    port_specs = {}
    port_spec_list = []
    _input_port_specs = []
    _output_port_specs = []

    def has_portSpec_with_name(self, name):
        return False
    def get_portSpec_by_name(self, name):
        return None
    def add_port_spec(self, port_spec):
        raise VistrailsInternalError("Cannot add port spec to abstraction")
    def delete_port_spec(self, port_spec):
        raise VistrailsInternalError("Cannot delete port spec from abstraction")

    ##########################################################################

    def get_port_spec_info(self, module):
        return core.modules.sub_module.get_port_spec_info(self.pipeline, 
                                                          module)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Abstraction
        object. 

        """
#        rep = '<abstraction id="%s" name="%s">' + \
#             '<actions>%s</actions>' + \
#             '<tags>%s</tags>' + \
#             '</abstraction>'
#         return  rep % (str(self.id), str(self.name), 
#                        [str(a) for a in self.action_list],
#                        [str(t) for t in self.tag_list])
        rep = '<abstraction id="%s" name="%s"/>'
        return rep % (str(self.id), str(self.name))

    def __eq__(self, other):
        """ __eq__(other: Abstraction) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Testing

import unittest

class TestAbstraction(unittest.TestCase):
    pass
#     def create_abstraction(self, id_scope=None):
#         from core.vistrail.action import Action
#         from core.vistrail.module import Module
#         from core.vistrail.module_function import ModuleFunction
#         from core.vistrail.module_param import ModuleParam
#         from core.vistrail.operation import AddOp
#         from core.vistrail.tag import Tag
#         from db.domain import IdScope
#         from datetime import datetime
        
#         if id_scope is None:
#             id_scope = IdScope()
#         function = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
#                                   name='value')
#         m = Module(id=id_scope.getNewId(Module.vtType),
#                    name='Float',
#                    package='edu.utah.sci.vistrails.basic',
#                    functions=[function])

#         add_op = AddOp(id=id_scope.getNewId('operation'),
#                        what='module',
#                        objectId=m.id,
#                        data=m)
#         add_op2 = AddOp(id=id_scope.getNewId('operation'),
#                        what='function',
#                        objectId=function.id,
#                        data=function)
#         action = Action(id=id_scope.getNewId(Action.vtType),
#                         prevId=0,
#                         date=datetime(2007,11, 18),
#                         operations=[add_op, add_op2])
#         tag = Tag(id=id_scope.getNewId(Tag.vtType),
#                   name='a tag')
#         abstraction = Abstraction(id=id_scope.getNewId(Abstraction.vtType),
#                                   name='blah',
#                                   actions=[action],
#                                   tags=[tag])
#         return abstraction

#     def test_copy(self):
#         import copy
#         from db.domain import IdScope

#         id_scope = IdScope()

#         a1 = self.create_abstraction(id_scope)
#         a2 = copy.copy(a1)
#         self.assertEquals(a1, a2)
#         self.assertEquals(a1.id, a2.id)
#         a3 = a1.do_copy(True, id_scope, {})
#         self.assertEquals(a1, a3)
#         self.assertNotEquals(a1.id, a3.id)

#     def test_serialization(self):
#         import core.db.io 
#         a1 = self.create_abstraction()
#         xml_str = core.db.io.serialize(a1)
#         a2 = core.db.io.unserialize(xml_str, Abstraction)
#         self.assertEquals(a1, a2)
#         self.assertEquals(a1.id, a2.id)
