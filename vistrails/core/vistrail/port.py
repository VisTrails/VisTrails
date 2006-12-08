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
    def getSig(self, spec):
        """ getSig(spec: tuple) -> str
        Return a string of signature based a port spec
        
        """
        if type(spec) == __builtin__.list:            
            return "(" + ", ".join([self.getSig(s) for s in spec]) + ")"
        assert type(spec == __builtin__.tuple)
        spec = spec[0]
        if issubclass(spec, core.modules.vistrails_module.Module):
            return spec.__name__
        raise VistrailsInternalError("getSig Can't handle type %s" 
                                         % type(spec))
    
    def getSignatures(self):
        """getSignatures() -> list
        Returns a list of all accepted signatures of this port, by generating
        a string representation of each port spec.
        
        """
        return [self.getSig(spec) for spec in self.spec]

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
    def setUp(self):
        self.registry = core.modules.module_registry.registry

    def testPort(self):
        x = Port()
        a = str(x)
        x.type = VistrailModuleType.Filter
        a = str(x)
        x.type = VistrailModuleType.Object
        a = str(x)
        
    def testPortSpec(self):
        descriptor = self.registry.getDescriptorByName('String')
        ports = self.registry.sourcePortsFromDescriptor(descriptor)
        assert all(ports, lambda x: x.moduleName == 'String')
        portRepr = 'value(String)'
        p = self.registry.portFromRepresentation('String', portRepr, 
                                                     PortEndPoint.Source)
        assert p.name == 'value'
        assert p.moduleName == 'String'

    def testPortSpec2(self):
        descriptor = self.registry.getDescriptorByName('String')
        ports = self.registry.sourcePortsFromDescriptor(descriptor)
        assert all(ports, lambda x: x.moduleName == 'String')
        portRepr = 'value(Float)'
        try:
            p = self.registry.portFromRepresentation('String', portRepr, 
                                                         PortEndPoint.Source)
            msg = "Expected to fail - passed an incompatible spec " \
                "representation"
            self.fail(msg)
        except VistrailsInternalError:
            pass
        
if __name__ == '__main__':
    unittest.main()

