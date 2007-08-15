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
# Check for testing
""" This module defines the class Module 
"""
if __name__ == '__main__':
    import gui.qt
    global app
    app = gui.qt.createBogusQtApp()

import copy
from sets import Set
from db.domain import DBModule
from core.data_structures.point import Point
from core.vistrail.annotation import Annotation
from core.vistrail.location import Location
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.utils import NoSummon, VistrailsInternalError
from core.utils.uxml import named_elements
import core.modules.module_registry
registry = core.modules.module_registry.registry

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
#        self.name = name
#        self.id = id
#        self.cache = 1
#        self.annotations = {}
#        self.center = Point(-1.0, -1.0)
        self.portVisible = Set()
        self.registry = None

    def __copy__(self):
        """__copy__() -> Module - Returns a clone of itself"""
        cp = DBModule.__copy__(self)
        cp.__class__ = Module
#         cp.center = Point(self.center.x, self.center.y)
#         cp.functions = [copy.copy(f) for f in self.functions]
#         cp.id = self.id
#         cp.cache = self.cache
#         cp.name = self.name
#         cp.annotations = copy.copy(self.annotations)
        cp.registry = copy.copy(self.registry)
        cp.portVisible = copy.copy(self.portVisible)
        return cp

    @staticmethod
    def convert(_module):
        if _module.__class__ == Module:
            return
	_module.__class__ = Module
        if _module.db_location:
            Location.convert(_module.db_location)
	for _function in _module.db_functions:
	    ModuleFunction.convert(_function)
        for _annotation in _module.db_get_annotations():
            Annotation.convert(_annotation)
        _module.portVisible = Set()
	_module.registry = None

    ##########################################################################
        
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

    # type check this (list, hash)
    def _get_functions(self):
        self.db_functions.sort(lambda x, y: cmp(x.db_pos, y.db_pos))
        return self.db_functions
    def _set_functions(self, functions):
	# want to convert functions to hash...?
        self.db_functions = functions
    functions = property(_get_functions, _set_functions)

    # type check this (list, hash)
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

    def _get_location(self):
        return self.db_location
    def _set_location(self, location):
        self.db_location = location
    location = property(_get_location, _set_location)

    # grrr this doesn't capture deep access like center.x = 1.2344
    def _get_center(self):
        if self.db_location is not None:
            return Point(self.db_location.db_x, 
                         self.db_location.db_y)
        return Point(-1.0, -1.0)
    def _set_center(self, center):
        # this should not be called! -- use the actions to update location!
        if self.db_location is None:
            self.db_location = Location(id=-1,
                                        x=center.x, 
                                        y=center.y)
        else:
            self.db_location.db_x = center.x
            self.db_location.db_y = center.y
    center = property(_get_center, _set_center)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_package(self):
        return self.db_package
    def _set_package(self, package):
        self.db_package = package
    package = property(_get_package, _set_package)

    def _get_version(self):
        return self.db_version
    def _set_version(self, version):
        self.db_version = version
    version = property(_get_version, _set_version)

    def _get_port_specs(self):
        return self.db_portSpecs
    def _set_port_specs(self, port_specs):
        self.db_portSpecs = port_specs
    port_specs = property(_get_port_specs, _set_port_specs)
    def has_portSpec_with_name(self, name):
        return self.db_has_portSpec_with_name(name)
    def get_portSpec_by_name(self, name):
        return self.db_get_portSpec_by_name(name)

    def addFunction(self, function):
	self.db_add_function(function)

    def deleteFunction(self, function):
        """deleteFunction(function: ModuleFunction) -> None 
        Deletes function
          
        """
        self.db_delete_function(function)

    def summon(self):
        getDescriptorByName = registry.getDescriptorByName
        result = getDescriptorByName(self.name).module()
        if self.cache != 1:
            result.is_cacheable = lambda *args: False
        if hasattr(result, 'srcPortsOrder'):
            result.srcPortsOrder = [p.name for p in self.destinationPorts()]
        return result

    def getNumFunctions(self):
        """getNumFunctions() -> int - Returns the number of functions """
        return len(self.functions)

    def uniqueSortedPorts(self, ports):
        """uniqueSortedPorts(ports) -> list of ports 
        Returns a list of ports sorted by name discarding repeated names.

        """
        if len(ports)==0:
            return ports
        ports.sort(lambda n1,n2: cmp(n1.sort_key,n2.sort_key))
        result = [ports[0]]
        names = [p.name for p in ports]
        for i in range(1,len(names)):
            if not ports[i].name in names[:i]:
                result.append(ports[i])
        return result

    def sourcePorts(self):
        """sourcePorts() -> list of Port 
        Returns list of source (output) ports module supports.

        """
        ports = []
        thing = registry.getDescriptorByName(self.name).module
        for (n, registry_ports) in registry.sourcePorts(thing):
            ports.extend([copy.copy(x) for x in registry_ports])
        ports = self.uniqueSortedPorts(ports)
        if self.registry:
            for (n, registry_ports) in self.registry.sourcePorts(thing):
                ports.extend([copy.copy(x) for x in registry_ports])
        for p in ports:
            p.id = self.id
        return ports

    def destinationPorts(self):
        """destinationPorts() -> list of Port 
        Returns list of destination (input) ports module supports

        """
        ports = []
        thing = registry.getDescriptorByName(self.name).module
        for (n, registry_ports) in registry.destinationPorts(thing):
            ports.extend([copy.copy(x) for x in registry_ports])

        ports = self.uniqueSortedPorts(ports)
        if self.registry:
            for (n, registry_ports) in self.registry.destinationPorts(thing):
                ports.extend([copy.copy(x) for x in registry_ports])
        for p in ports:
            p.id = self.id
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
        elif self.center != other.center:
            print "center mismatch"
            self.center.show_comparison(other.center)
        elif len(self.functions) != len(other.functions):
            print "function length mismatch"
            print len(self.functions), len(other.functions)
        else:
            for f, g in zip(self.functions, other.functions):
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
        return ("(Module '%s' id=%s functions:%s)@%X" %
                (self.name,
                 self.id,
                 [str(f) for f in self.functions],
                 id(self)))

    def __eq__(self, other):
        """ __eq__(other: Module) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.cache != other.cache:
            return False
        if self.center != other.center:
            return False
        if len(self.functions) != len(other.functions):
            return False
        for f, g in zip(self.functions, other.functions):
            if f != g:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    ##########################################################################
    # Properties


################################################################################
# Testing

import unittest
import xml.dom.minidom
from core.utils.uxml import named_elements

class TestModule(unittest.TestCase):

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
        self.assertEquals(x.center.x, -1.0)
        x.center = Point(1, x.center.y)
        self.assertEquals(x.center.x, 1)
        self.assertEquals(x.name, "")

    def testSummonModule(self):
        """Check that summon creates a correct module"""
        
        x = Module()
        x.name = "String"
        try:
            c = x.summon()
            assert type(c) == registry.getDescriptorByName("String").module
        except NoSummon:
            msg = "Expected to get a String object, got a NoSummon exception"
            self.fail(msg)

    def testLoadAndDumpModule(self):
        """ Check that serialize and unserialize are working properly """
        from core.vistrail import dbservice

        m = Module()
        m.name = "Float"
        m.cache = 0
        m.id = 0
        m.center = Point(-59.7779886737, 142.491920766)
        f = ModuleFunction()
        f.name = "value"
        m.addFunction(f)
        param = ModuleParam()
        param.name = "&lt;no description&gt;"
        param.strValue = "1.2"
        param.type = "Float"
        param.alias = ""
        f.params.append(param)

        dom = dbservice.serialize(m)
        mnew = dbservice.unserialize(Module.vtType, dom)
        Module.convert(mnew)
        
        m.show_comparison(mnew)
        assert m == mnew        

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
    
