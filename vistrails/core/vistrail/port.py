""" This module contains class definitions for:
    * Port
    * PortEndPoint

 """
from core.utils import enum
from core.utils import VistrailsInternalError, all
from core.vistrail.module_param import VistrailModuleType
import core.modules.vistrails_module
import __builtin__

################################################################################

PortEndPoint = enum('PortEndPoint',
                    ['Invalid', 'Source', 'Destination'])

################################################################################

class Port(object):
    """ A port denotes one endpoint of a Connection.

    self.spec: list of list of (module, str) 
    
    """
    def getSignatures(self):
        """getSignatures() -> list
        Returns a list of all accepted signatures of this port, by generating
        a string representation of each port spec.
        
        """
        def getSig(spec):
            if type(spec) == __builtin__.list:
                return "(" + ", ".join([getSig(s) for s in spec]) + ")"
            assert type(spec == __builtin__.tuple)
            spec = spec[0]
            if issubclass(spec, core.modules.vistrails_module.Module):
                return spec.__name__
            raise VistrailsInternalError("getSig Can't handle type %s" 
                                         % type(spec))
        return [getSig(spec) for spec in self.spec]

    def toolTip(self):
        """ toolTip() -> str
        Generates an appropriate tooltip for the port. 
        
        """
        def endPointType():
            d = {PortEndPoint.Invalid: "Invalid",
                 PortEndPoint.Source: "Output",
                 PortEndPoint.Destination: "Input"}
            return d[self.endPoint]
        return "%s port %s\n%s" % (endPointType(), 
                                   self.name, 
                                   "; ".join(self.getSignatures()))
    
    def __init__(self):
        self.endPoint = PortEndPoint.Invalid
        self.moduleId = 0
        self.connectionId = 0
        self.moduleName = ""
        self.name = ""
        self.type = VistrailModuleType.Module
        self.spec = None
        self.optional = False
    
    def __str__(self):
        """ __str__() -> str 
        Returns a string representation of a Port object.  """
        return '<Port endPoint="%s" moduleId=%s connectionId=%s name=%s ' \
            'type=Module %s/>' % (self.endPoint,
                                  self.moduleId,
                                  self.connectionId,
                                  self.name,
                                  self.spec)

###############################################################################

import unittest

if __name__ == '__main__':
    import core.modules.basic_modules
    import core.modules.module_registry
    from core.vistrail.module_param import VistrailModuleType

class TestPort(unittest.TestCase):
    
    def testPort(self):
        x = Port()
        a = str(x)
        x.type = VistrailModuleType.Filter
        a = str(x)
        x.type = VistrailModuleType.Object
        a = str(x)
        
    def testPortSpec(self):
        descriptor = core.modules.module_registry.registry.getDescriptorByName('String')
        ports = core.modules.module_registry.registry.sourcePortsFromDescriptor(descriptor)
        assert all(ports, lambda x: x.moduleName == 'String')
        portRepr = 'value(String)'
        p = core.modules.module_registry.registry.portFromRepresentation('String', portRepr, PortEndPoint.Source)
        assert p.name == 'value'
        assert p.moduleName == 'String'

    def testPortSpec2(self):
        descriptor = core.modules.module_registry.registry.getDescriptorByName('String')
        ports = core.modules.module_registry.registry.sourcePortsFromDescriptor(descriptor)
        assert all(ports, lambda x: x.moduleName == 'String')
        portRepr = 'value(Float)'
        try:
            p = core.modules.module_registry.registry.portFromRepresentation('String', portRepr, PortEndPoint.Source)
            self.fail("Expected to fail - passed an incompatible spec representation")
        except VistrailsInternalError:
            pass
        
        
if __name__ == '__main__':
    unittest.main()

