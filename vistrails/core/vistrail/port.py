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
""" This module contains class definitions for:
    * Port
    * PortEndPoint

 """
from core.utils import enum
from core.utils import VistrailsInternalError, all
import core.modules.vistrails_module
import __builtin__
import copy

################################################################################

PortEndPoint = enum('PortEndPoint',
                    ['Invalid', 'Source', 'Destination'])

################################################################################

class Port(object):
    """ A port denotes one endpoint of a Connection.

    self.spec: list of list of (module, str) 
    
    """

    ##########################################################################
    # Constructor and copy
    
    def __init__(self):
        self.endPoint = PortEndPoint.Invalid
        self.moduleId = 0
        self.connectionId = 0
        self.moduleName = ""
        self.name = ""
        self.spec = None
        self.optional = False
        self.sort_key = -1

    def __copy__(self):
        cp = Port()
        cp.endPoint = self.endPoint
        cp.moduleId = self.moduleId
        cp.connectionId = self.connectionId
        cp.moduleName = self.moduleName
        cp.name = self.name
        cp.spec = copy.copy(self.spec)
        cp.optional = self.optional
        cp.sort_key = self.sort_key
        return cp
    
    ##########################################################################

    def getSig(self, spec):
        """ getSig(spec: tuple) -> str
        Return a string of signature based a port spec
        
        """
        if type(spec) == list:
            return "(" + ",".join([self.getSig(s) for s in spec]) + ")"
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

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(self) != type(other):
            print "Type mismatch"
        elif self.endPoint != other.endPoint:
            print "endpoint mismatch"
        elif self.connectionId != other.connectionId:
            print "connectionId mismatch"
        elif self.moduleName != other.moduleName:
            print "moduleName mismatch"
        elif self.name != other.name:
            print "name mismatch"
        elif self.spec != other.spec:
            print "spec mismatch"
        elif self.optional != self.optional:
            print "optional mismatch"
        elif self.sort_key != self.sort_key:
            print "sort_key mismatch"
        else:
            print "no difference found"
            assert self == other

    ##########################################################################
    # Operators

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.endPoint == other.endPoint and
                self.moduleId == other.moduleId and
                self.connectionId == other.connectionId and
                self.moduleName == other.moduleName and
                self.name == other.name and
                self.spec == other.spec and
                self.optional == other.optional and
                self.sort_key == other.sort_key)
    
    def __str__(self):
        """ __str__() -> str 
        Returns a string representation of a Port object.  """
        return '<Port endPoint="%s" moduleId=%s connectionId=%s name=%s ' \
            'type=Module %s/>' % (self.endPoint,
                                  self.moduleId,
                                  self.connectionId,
                                  self.name,
                                  self.spec)

    def equals_no_id(self, other):
        if type(self) != type(other):
            return False
        return (self.endPoint == other.endPoint and
                self.moduleName == other.moduleName and
                self.name == other.name and
                self.spec == other.spec and
                self.optional == other.optional and
                self.sort_key == other.sort_key)

###############################################################################

import unittest

if __name__ == '__main__':
    import core.modules.basic_modules
    import core.modules.module_registry
    
class TestPort(unittest.TestCase):
    def setUp(self):
        self.registry = core.modules.module_registry.registry

    def testPort(self):
        x = Port()
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
        """Test passing incompatible specs"""
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
        

    def test_registry_port_subtype(self):
        """Test registry isPortSubType"""
        descriptor = self.registry.getDescriptorByName('String')
        ports = self.registry.sourcePortsFromDescriptor(descriptor)
        assert self.registry.isPortSubType(ports[0], ports[0])

    def test_registry_ports_can_connect(self):
        """Test registry isPortSubType"""
        descriptor = self.registry.getDescriptorByName('String')
        oport = self.registry.sourcePortsFromDescriptor(descriptor)[0]
        iport = self.registry.destinationPortsFromDescriptor(descriptor)[0]
        assert self.registry.portsCanConnect(oport, iport)

    # TODO: Exercise obvious bug on line 80.


if __name__ == '__main__':
    unittest.main()

