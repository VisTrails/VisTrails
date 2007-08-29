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

import copy
from itertools import izip
from sets import Set

from core.vistrail.location import Location
from core.vistrail.module_function import ModuleFunction
from core.vistrail.annotation import Annotation
from db.domain import DBAbstractionRef

class AbstractionModule(DBAbstractionRef):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAbstractionRef.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        self.portVisible = Set()
        # FIXME should we have a registry for an abstraction module?

    def __copy__(self):
        return AbstractionModule.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAbstractionRef.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = AbstractionModule
        cp.portVisible = copy.copy(self.portVisible)
        return cp

    @staticmethod
    def convert(_abstraction_module):
        if _abstraction_module.__class__ == AbstractionModule:
            return
        _abstraction_module.__class__ = AbstractionModule
        if _abstraction_module.db_location:
            Location.convert(_abstraction_module.db_location)
	for _function in _abstraction_module.db_functions:
	    ModuleFunction.convert(_function)
        for _annotation in _abstraction_module.db_get_annotations():
            Annotation.convert(_annotation)
        _abstraction_module.portVisible = Set()


    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_cache(self):
        return self.db_cache
    def _set_cache(self, cache):
        self.db_cache = cache
    cache = property(_get_cache, _set_cache)

    def _get_abstraction_id(self):
        return self.db_abstraction_id
    def _set_abstraction_id(self, id):
        self.db_abstraction_id = id
    abstraction_id = property(_get_abstraction_id, _set_abstraction_id)

    def _get_location(self):
        return self.db_location
    def _set_location(self, location):
        self.db_location = location
    location = property(_get_location, _set_location)

    def _get_version(self):
        return self.db_version
    def _set_version(self, version):
        self.db_version = version
    version = property(_get_version, _set_version)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_functions(self):
        self.db_functions.sort(lambda x, y: cmp(x.db_pos, y.db_pos))
        return self.db_functions
    def _set_functions(self, functions):
	# want to convert functions to hash...?
        self.db_functions = functions
    functions = property(_get_functions, _set_functions)

    def _get_package(self):
        return self._package
    def _set_package(self, package):
        print "doesn't make sense for abstraction module"
        self._package = package
    package = property(_get_package, _set_package)

    def _get_annotations(self):
        return self.db_annotations
    def _set_annotations(self, annotations):
        self.db_annotations = annotations
    annotations = property(_get_annotations, _set_annotations)
    def add_annotation(self, annotation):
        self.db_add_annotation(annotation)
    def delete_annotation(self, annotation):
        self.db_delete_annotation(annotation)
    def has_annotation_with_key(self, key):
        return self.db_has_annotation_with_key(key)
    def get_annotation_by_key(self, key):
        return self.db_get_annotation_by_key(key)        

    def summon(self):
        # we shouldn't ever call this since we're expanding abstractions
        return None

    def sourcePorts(self):
        return []

    def destinationPorts(self):
        return []

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an 
        AbstractionModule object. 

        """
        rep = '<abstraction_module id="%s" abstraction_id="%s" verion="%s">'
        rep += str(self.location)
        rep += str(self.functions)
        rep += str(self.annotations)
        rep += '</abstraction_module>'
        return  rep % (str(self.id), str(self.abstraction_id), 
                       str(self.version))

    def __eq__(self, other):
        """ __eq__(other: AbstractionModule) -> boolean
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

class TestModule(unittest.TestCase):

    def create_abstraction_module(self, id_scope=IdScope()):
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
            AbstractionModule(id=id_scope.getNewId(AbstractionModule.vtType),
                              abstraction_id=1,
                              version=12,
                              location=location,
                              functions=functions)
        return module

    def test_copy(self):
        """Check that copy works correctly"""
        
        id_scope = IdScope()
        m1 = self.create_abstraction_module(id_scope)
        m2 = copy.copy(m1)
        self.assertEquals(m1, m2)
        self.assertEquals(m1.id, m2.id)
        m3 = m1.do_copy(True, id_scope, {})
        self.assertEquals(m1, m3)
        self.assertNotEquals(m1.id, m3.id)

    def test_serialization(self):
        """ Check that serialize and unserialize are working properly """
        import core.db.io

        m1 = self.create_abstraction_module()
        xml_str = core.db.io.serialize(m1)
        m2 = core.db.io.unserialize(xml_str, AbstractionModule)
        self.assertEquals(m1, m2)
        self.assertEquals(m1.id, m2.id)
