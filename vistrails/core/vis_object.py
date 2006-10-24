# Check for testing
if __name__ == '__main__':
    import qt
    global app
    app = qt.createBogusQtApp()


from data_structures import Point
from vis_types import VistrailModuleType
from common import NoSummon
from xml_utils import *
from vis_types import ModuleFunction, ModuleParam
import copy
import modules.module_registry
from sets import Set

registry = modules.module_registry.registry

################################################################################

# A VisModule stores not only the information, but a method (summon)
# that creates a 'live' object suitable for use in the vtk_graph class.

def noSummon(obj):
    raise NoSummon(obj)

class VisModule(object):
    """ Represents a module from a VisPipeline """

    def __init__(self):
        self.id = -1
        self.cache = 0
        self.functions = []
        self.annotations = {}
        self.center = Point(-1.0, -1.0)
        self.name = ""
        self.portVisible = Set()
        self.registry = None

    def getNumFunctions(self):
        return len(self.functions)

    def findType(self,classname):
        if registry.hasModule(classname):
            return VistrailModuleType.Module
        else:
            return VistrailModuleType.Invalid

    def uniqueSortedPorts(self, ports):
        if len(ports)==0:
            return ports
        ports.sort(lambda n1,n2: cmp(n1.name,n2.name))
        result = [ports[0]]
        names = [p.name for p in ports]
        for i in range(1,len(names)):
            if not ports[i].name in names[:i]:
                result.append(ports[i])
        return result

    def sourcePorts(self):
        """ Returns list of source (output) ports module supports

        Returns
        -------
    
        - 'list' of 'VisPort' 

        """
        ports = []
        thing = registry.getDescriptorByName(self.name).module
        for (n, registry_ports) in registry.sourcePorts(thing):
            ports.extend([copy.copy(x) for x in registry_ports])
        if self.registry:
            for (n, registry_ports) in self.registry.sourcePorts(thing):
                ports.extend([copy.copy(x) for x in registry_ports])
        ports = self.uniqueSortedPorts(ports)
        for p in ports:
            p.id = self.id
        return ports

    def destinationPorts(self):
        """ Returns list of destination (input) ports module supports

        Returns
        -------

        - 'list' of 'VisPort' 

        """
        ports = []        
        thing = registry.getDescriptorByName(self.name).module
        for (n, registry_ports) in registry.destinationPorts(thing):
            ports.extend([copy.copy(x) for x in registry_ports])
        if self.registry:
            for (n, registry_ports) in self.registry.destinationPorts(thing):
                ports.extend([copy.copy(x) for x in registry_ports])
        ports = self.uniqueSortedPorts(ports)
        for p in ports:
            p.id = self.id
        return ports

    def updateType(self):
        """updateType() -> None.
Updates the type information according to given name, and sets the
appropriate summon method."""
        self.type = self.findType(self.name)
        if self.type == VistrailModuleType.Module:
            self.summon = lambda *args: registry.getDescriptorByName(self.name).module()
            self.summonProxy = lambda *args: noSummon(self)
            self.createCacheFixture = lambda *args: noSummon(self)
        else:
            self.summon = lambda *args: noSummon(self)
            self.summonProxy = lambda *args: noSummon(self)
            self.createCacheFixture = lambda *args: noSummon(self)

    def serialize(self, dom, element):
        """ Writes itself as XML """
	child = dom.createElement('object')
	child.setAttribute('cache', str(self.cache))
	child.setAttribute('id',    str(self.id))
	child.setAttribute('name',  self.name)
	child.setAttribute('x',     str(self.center.x))
	child.setAttribute('y',     str(self.center.y))
        element.appendChild(child)

    def dumpToXML(self, dom, element):
	child = dom.createElement('module')
	child.setAttribute('cache', str(self.cache))
	child.setAttribute('id',    str(self.id))
	child.setAttribute('name',  self.name)
	child.setAttribute('x',     str(self.center.x))
	child.setAttribute('y',     str(self.center.y))
	for fi in range(len(self.functions)):
	    f = self.functions[fi]
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
		child.appendChild(xmlfunc)
	annot = dom.createElement('annotation')
	
	for (k,v) in self.annotations.items():
	    set = dom.createElement('set')
	    set.setAttribute('key',str(k))
	    set.setAttribute('value',str(v))
	    annot.appendChild(set)
        child.appendChild(annot)
	element.appendChild(child)

    @staticmethod
    def loadFromXML(element):
	m = VisModule()
	(m.name, cache, id, x, y) = [str(element.getAttribute(x))
                                     for x in ['name', 'cache', 'id',
                                               'x', 'y']]
        m.cache = int(cache)
        m.id = int(id)
        m.center.x = float(x)
        m.center.y = float(y)
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
		
		if p[1] >= len(m.functions):
		    f = ModuleFunction()
		    f.name = p[2]
		    m.functions.append(f)
		    if len(m.functions)-1 != p[1]:
			raise VistrailsInternalError("Pipeline function id is inconsistent")
		f = m.functions[p[1]]
		if f.name != p[2]:
		    raise VistrailsInternalError("Pipeline function name is inconsistent")
		if p[3] == -1:
		    continue
		if p[3] >= len(f.params):
		    param = ModuleParam()
		    param.name = p[4]
		    f.params.append(param)
		    if len(f.params)-1 != p[3]:
			raise VistrailsInternalError("Pipeline parameter id is inconsistent")
		param = f.params[p[3]]
		param.name = p[4]
		param.strValue = p[5]
		param.type = p[6]
		if param.type.find('char')>-1 or param.type=='str':
		    param.type = 'string'
		param.alias = p[7]
    
        m.annotations = {}
        for a in named_elements(element, 'annotation'):
            m.annotations[str(a.getAttribute('key'))] = str(a.getAttribute('value'))
	return m

    def deleteFunction(self, functionId):
        """ Deletes function invocation of given index

        Parameters
        ----------

        - functionId : 'int'
          the function identifier
          
        """
        del self.functions[functionId]

    def deleteAnnotation(self, key):
        """ Deletes annotation of given key

        Parameters
        ----------

        - key: 'str'
          the key name
          
        """
        del self.annotations[key]

    def __copy__(self):
        cp = VisModule()
        cp.center = Point(self.center.x, self.center.y)
        cp.functions = [copy.copy(f) for f in self.functions]
        cp.id = self.id
        cp.cache = self.cache
        cp.name = self.name
        return cp

    def __str__(self):
        return "<<name='%s' id='%s' functions=%s>>" % (self.name,
                                                       self.id,
                                                       self.functions)
    # autoprop
    def _set_name(self, name):
        self.__name = name
        self.updateType()
    def _get_name(self):
        return self.__name
    name = property(_get_name, _set_name)

################################################################################
# Testing

import unittest

class TestVisModule(unittest.TestCase):

    def testAccessors(self):
        """Check that accessors are working."""
        x = VisModule()
        self.assertEquals(x.id, -1)
        x.id = 10
        self.assertEquals(x.id, 10)
        self.assertEquals(x.cache, 0)
        x.cache = 1
        self.assertEquals(x.cache, 1)
        self.assertEquals(x.center.x, -1.0)
        x.center.x = 1
        self.assertEquals(x.center.x, 1)
        self.assertEquals(x.name, "")

    def testNoSummon(self):
        """Check that NoSummon is working properly."""
        x = VisModule()
        try:
            x.summon()
        except NoSummon:
            pass
        else:
            self.fail("Expected a NoSummon")
    
    def testSummonModule(self):
        """Check that summon creates a correct module"""
        import modules.basic_modules
        x = VisModule()
        x.name = "String"
        try:
            c = x.summon()
            assert type(c) == registry.getDescriptorByName("String").module
        except NoSummon:
            self.fail("Expected to get a String object, got a NoSummon exception")
        
if __name__ == '__main__':
    unittest.main()
    
