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
        self.annotationMap = {}
        self.annotationValueMap = {}
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
        cp.annotationMap = copy.copy(self.annotationMap)
        cp.annotationValueMap = copy.copy(self.annotationValueMap)
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
        _module.annotationMap = {}
        _module.annotationValueMap = {}
        for annotation in _module.db_get_annotations():
            _module.annotationMap[annotation.db_key] = annotation
            _module.annotationValueMap[annotation.db_key] = annotation.db_value
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
        return self.db_functions
    def _set_functions(self, functions):
	# want to convert functions to hash...?
        self.db_functions = functions
    functions = property(_get_functions, _set_functions)

    # type check this (list, hash)
    def _get_annotations(self):
        if self.is_dirty:
            self.annotationMap = {}
            self.annotationValueMap = {}
            for annotation in self.db_get_annotations():
                self.annotationMap[annotation.db_key] = annotation
                self.annotationValueMap[annotation.db_key] = annotation.db_value
        return self.annotationValueMap
    def _set_annotations(self, annotations):
        # this should not be called! -- use the actions to update annotations!
        for (key, value) in annotations:
            new_annotation = DBAnnotation(id=-1,
                                          key=key,
                                          value=value)
            self.db_add_annotation(new_annotation)
            self.annotationMap[key] = new_annotation
            self.annotationValueMap[key] = value
    annotations = property(_get_annotations, _set_annotations)


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

    def addFunction(self, function):
	self.db_add_function(function)

    def deleteFunction(self, functionId):
        """deleteFunction(functionId:int) -> None 
        Deletes function invocation of given index
          
        """
        try:
            del self.db_functions[functionId]
        except:
            raise VistrailsInternalError('Invalid functionId in deleteFunction')

    def addAnnotation(self, key, value):
        new_annotation = Annotation(id=-1, key=key, value=value)
	self.db_add_annotation(new_annotation)
        self.annotationMap[key] = new_annotation
        self.annotationValueMap[key] = value

    def deleteAnnotation(self, key):
        """deleteAnnotation(key:str) -> None 
        Deletes annotation of given key
          
        """
        try:
            to_delete = self.annotationMap[key]
            self.db_delete_annotation(to_delete)
            del self.annotationMap[key]
            del self.annotationValueMap[key]
        except:
            raise VistrailsInternalError('Invalid key in deleteAnnotation')


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

    def serialize(self, dom, element):
        """serialize(dom, element) -> None - Writes itself as XML """
        child = dom.createElement('object')
        child.setAttribute('cache', str(self.cache))
        child.setAttribute('id',    str(self.id))
        child.setAttribute('name',  self.name)
        child.setAttribute('x',     str(self.center.x))
        child.setAttribute('y',     str(self.center.y))
        element.appendChild(child)

    def dumpToXML(self, dom, element):
        """dumpToXML(dom,element) -> None 
        Writes the whole Module object as XML, including functions, parameters,
        and annotations. Used when copying a module.

        """
        child = dom.createElement('module')
        child.setAttribute('cache', str(self.cache))
        child.setAttribute('id',    str(self.id))
        child.setAttribute('name',  self.name)
        child.setAttribute('x',     str(self.center.x))
        child.setAttribute('y',     str(self.center.y))
        for fi in range(len(self.functions)):
            f = self.functions[fi]
            if f.getNumParams() == 0 or f.params[0].id == -1:
                xmlfunc = dom.createElement('function')
                xmlfunc.setAttribute('functionId', str(fi))
                xmlfunc.setAttribute('function', f.name)
                xmlfunc.setAttribute('parameterId',"-1")
                xmlfunc.setAttribute('parameter', "")
                xmlfunc.setAttribute('value', "")
                xmlfunc.setAttribute('type',"")
                xmlfunc.setAttribute('alias',"")
                xmlfunc.setAttribute('queryMethod',"0")
                child.appendChild(xmlfunc)
            else:
                for i in range(f.getNumParams()):
                    p = f.params[i]
                    xmlfunc = dom.createElement('function')
                    xmlfunc.setAttribute('functionId', str(fi))
                    xmlfunc.setAttribute('function', f.name)
                    xmlfunc.setAttribute('parameterId',str(i))
                    xmlfunc.setAttribute('parameter', p.name)
                    xmlfunc.setAttribute('value', p.strValue)
                    xmlfunc.setAttribute('type',p.type)
                    xmlfunc.setAttribute('alias',p.alias)
                    xmlfunc.setAttribute('queryMethod',str(p.queryMethod))
                    child.appendChild(xmlfunc)
	if len(self.annotations.values()) > 0:
	    annot = dom.createElement('annotation')
	    #         for (k,v) in self.annotations.items():
	    #             set = dom.createElement('set')
	    #             set.setAttribute('key',str(k))
	    #             set.setAttribute('value',str(v))
	    #             annot.appendChild(set)
	    for annotation in self.annotations.values():
		set = dom.createElement('set')
		set.setAttribute('key', annotation.key)
		set.setAttribute('value', annotation.value)
		annot.appendChild(set)
	    child.appendChild(annot)
        # Also dump the local registry
        # Nothing fancy here. Only the port name and its type
        if self.registry:            
            desc = self.registry.getDescriptorByName(self.name)
            for (pName, pSpec) in desc.inputPorts.iteritems():
                s = []
                for p in pSpec[0]:
                    d = registry.getDescriptor(p[0])
                    s.append(d.name)
                xmlInput = dom.createElement('inputport')
                xmlInput.setAttribute('name', str(pName))
                xmlInput.setAttribute('type', "(" +",".join(s)+")")
                child.appendChild(xmlInput)
            for (pName, pSpec) in desc.outputPorts.iteritems():
                s = []
                for p in pSpec[0]:
                    d = registry.getDescriptor(p[0])
                    s.append(d.name)
                xmlOutput = dom.createElement('outputport')
                xmlOutput.setAttribute('name', str(pName))
                xmlOutput.setAttribute('type', "(" +",".join(s)+")")
                child.appendChild(xmlOutput)
                
        element.appendChild(child)

    @staticmethod
    def loadFromXML(element):
        """loadFromXML(element) -> Module 
        Builds a Module object from XML generated by dumpToXML function.

        """
        m = Module()
        (m.name, cache, id, x, y) = [str(element.getAttribute(x))
                                     for x in ['name', 'cache', 'id',
                                               'x', 'y']]
        m.cache = int(cache)
        m.id = int(id)
        m.center.x = float(x)
        m.center.y = float(y)
        moduleThing = registry.getDescriptorByName(m.name).module
        for n in element.childNodes:
            if n.localName == "function":
                p = []
                p.append(-1)
                p.append(int(n.getAttribute('functionId')))
                p.append(str(n.getAttribute('function')))
                p.append(int(n.getAttribute('parameterId')))
                p.append(str(n.getAttribute('parameter')))
                p.append(str(n.getAttribute('value')))
                p.append(str(n.getAttribute('type')))
                p.append(str(n.getAttribute('alias')))
                p.append(int(n.getAttribute('queryMethod')))

                if p[1] >= len(m.functions):
                    f = ModuleFunction()
                    f.name = p[2]
                    m.addFunction(f)
                    if len(m.functions)-1 != p[1]:
                        msg = "Pipeline function id is inconsistent"
                        raise VistrailsInternalError(msg)
                f = m.functions[p[1]]
                if f.name != p[2]:
                    msg = "Pipeline function name is inconsistent"
                    raise VistrailsInternalError()
                if p[3] == -1:
                    continue
                if p[3] >= len(f.params):
                    param = ModuleParam()
                    param.name = p[4]
                    f.params.append(param)
                    if len(f.params)-1 != p[3]:
                        msg = "Pipeline parameter id is inconsistent"
                        raise VistrailsInternalError(msg)
                param = f.params[p[3]]
                param.name = p[4]
                param.strValue = p[5]
                param.type = p[6]
                if param.type.find('char')>-1 or param.type=='str':
                    param.type = 'string'
                param.alias = p[7]
                param.queryMethod = p[8]
            elif n.localName in ["inputport", "outputport"]:
                if not m.registry:
                    m.registry = core.modules.module_registry.ModuleRegistry()
                    m.registry.addModule(moduleThing)
                (name, types) = (str(n.getAttribute('name')), str(n.getAttribute('type')))
                types = types[1:-1].split(',')
                spec = [registry.getDescriptorByName(t).module for t in types]
                if len(spec)==1:
                    spec = spec[0]
                if n.localName=="inputport":
                    m.registry.addInputPort(moduleThing, name, spec)
                else:
                    m.registry.addOutputPort(moduleThing, name, spec)
    
        m.annotations = {}
        for a in named_elements(element, 'annotation'):
            akey = str(a.getAttribute('key'))
            avalue = str(a.getAttribute('value'))
#            m.annotations[akey] = avalue
	    m.addAnnotation(akey, avalue)
        return m

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
        """ Check that fromXML and toXML are working properly """
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

        dom = dbservice.toXML(m)
        mnew = dbservice.fromXML('module', dom)
        Module.convert(mnew)
        
#         impl = xml.dom.minidom.getDOMImplementation()
#         dom = impl.createDocument(None, 'test',None)
#         root = dom.documentElement
#         m.dumpToXML(dom,root)
#         xmlstr = str(dom.toxml())
#         dom = xml.dom.minidom.parseString(xmlstr)
#         root = dom.documentElement
#         for xmlmodule in named_elements(root, 'module'):
#             mnew = Module.loadFromXML(xmlmodule)
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
    
