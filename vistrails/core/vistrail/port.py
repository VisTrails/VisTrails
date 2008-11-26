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

 """
from db.domain import DBPort
from core.utils import VistrailsInternalError, all
from core.vistrail.port_spec import PortSpec, PortEndPoint
import core.modules.vistrails_module
import __builtin__
import copy

################################################################################

class Port(DBPort):
    """ A port denotes one endpoint of a Connection.

    self.spec: list of list of (module, str) 
    
    """
    
    ##########################################################################
    # Constructor and copy
    
    def __init__(self, *args, **kwargs):
        """The preferred way to create a port is to pass a PortSpec with
        new information.  The construcotr pulls name, type, and signature 
        info from the PortSpec.
        
        Example: Port(id=<id>, spec=<port_spec>, moduleId=<id>, 
                      moduleName=<name>)

        You can also pass the name, type, and signature, separately.
        
        Example: Port(id=<id>, name=<name>, type=[source|destination],
                      signature=<sig>, moduleId=<id>, moduleName=<name>)

        """

        self._spec = None
        if 'spec' in kwargs:
            self.spec = kwargs['spec']
            del kwargs['spec']
            if 'name' not in kwargs:
                kwargs['name'] = self.spec.name
            if 'type' not in kwargs:
                if self.spec.type in PortSpec.port_type_map:
                    kwargs['type'] = PortSpec.port_type_map[self.spec.type]
            if 'signature' not in kwargs:
                kwargs['signature'] = self.spec.sigstring
        else:
            self.spec = None
        if 'id' not in kwargs:
            kwargs['id'] = -1
        if 'moduleId' not in kwargs:
            kwargs['moduleId'] = 0
        if 'moduleName' not in kwargs:
            kwargs['moduleName'] = ""
        if 'name' not in kwargs:
            kwargs['name'] = ""
        if 'signature' not in kwargs:
            kwargs['signature'] = ""

	DBPort.__init__(self, *args, **kwargs)

        self.find_port_types()
#             # if there is no spec, create it
#             spec_type = PortSpec.port_type_map.inverse[self.type]
#             self._spec = PortSpec(name=self.name, 
#                                   type=spec_type,
#                                   sigstring=self.signature)
        
    def __copy__(self):
        return Port.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPort.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Port
        cp._descriptors = copy.copy(self._descriptors)
        cp._spec = copy.copy(self._spec)
        return cp

    @staticmethod
    def convert(_port):
        if _port.__class__ == Port:
            return
        _port.__class__ = Port
        _port._spec = None
        _port._descriptors = None
        _port.find_port_types()

    def find_port_types(self):
        from core.modules.module_registry import get_module_registry
        registry = get_module_registry()
        self._descriptors = []
        if self.signature:
            signature_str = self.signature[1:-1].strip()
            if signature_str != "":
                try:
                    for type_str in signature_str.split(','):
                        desc = registry.get_descriptor_by_name( \
                            *(type_str.split(':')))
                        self._descriptors.append(desc)
                except registry.MissingModulePackage, e:
                    print ('Cannot find module "%s" in \n' 
                           'package "%s". Make sure package is \n' 
                           'enabled in the Preferences dialog.' % \
                               (e._name, e._identifier))
                    self._descriptors = []
                    return

    ##########################################################################
    # Properties
    
    id = DBPort.db_id
    moduleId = DBPort.db_moduleId
    moduleName = DBPort.db_moduleName
    name = DBPort.db_name
    type = DBPort.db_type

    def _get_endPoint(self):
        if self.db_type in PortSpec.end_point_map:
            return PortSpec.end_point_map[self.db_type]
        return PortEndPoint.Invalid
    def _set_endPoint(self, endPoint):
        if endPoint in PortSpec.end_point_map.inverse:
            self.db_type = PortSpec.end_point_map.inverse[endPoint]
        else:
            self.db_type = 'invalid'
    endPoint = property(_get_endPoint, _set_endPoint)

    def _get_signature(self):
        if not self.db_signature and self.spec is not None:
            self.db_signature = self.spec.sigstring
        return self.db_signature
    def _set_signature(self, signature):
        self.db_signature = signature
    signature = property(_get_signature, _set_signature)
    
    def _get_spec(self):
        return self._spec
    def _set_spec(self, spec):
        self._spec = spec
        if self._spec is not None:
            self.signature = self._spec.sigstring
        else:
            self.signature = ""
    spec = property(_get_spec, _set_spec)

    # FIXME get rid of this one?
    def _get_sig(self):
        return self.name + self.signature
    sig = property(_get_sig)

    def descriptors(self):
        return self._descriptors

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(self) != type(other):
            print "Type mismatch"
        elif self.endPoint != other.endPoint:
            print "endpoint mismatch"
        elif self.moduleName != other.moduleName:
            print "moduleName mismatch"
        elif self.name != other.name:
            print "name mismatch"
        elif self.spec != other.spec:
            print "spec mismatch"
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
# FIXME module id can change...
#                self.moduleId == other.moduleId and
                self.moduleName == other.moduleName and
                self.name == other.name and
                self.signature == other.signature)
    
    def __str__(self):
        """ __str__() -> str 
        Returns a string representation of a Port object.  """
        return '<Port endPoint="%s" moduleId=%s name=%s ' \
            'type=Module %s/>' % (self.endPoint,
                                  self.moduleId,
                                  self.name,
                                  self.spec)

    def equals_no_id(self, other):
        if type(self) != type(other):
            return False
        return (self.endPoint == other.endPoint and
                self.moduleName == other.moduleName and
                self.name == other.name and
                self.signature == other.signature)

###############################################################################

import unittest
from db.domain import IdScope

if __name__ == '__main__':
    import core.modules.basic_modules
    import core.modules.module_registry
    
class TestPort(unittest.TestCase):
    def setUp(self):
        self.registry = core.modules.module_registry.get_module_registry()

    def create_port(self, id_scope=IdScope()):
        port = Port(id=id_scope.getNewId(Port.vtType),
                    type='source',
                    moduleId=12L, 
                    moduleName='String', 
                    name='value',
                    signature='(edu.utah.sci.vistrails.basic:String)')
        return port

    def test_copy(self):
        id_scope = IdScope()
        
        p1 = self.create_port(id_scope)
        p2 = copy.copy(p1)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)
        p3 = p1.do_copy(True, id_scope, {})
        self.assertEquals(p1, p3)
        self.assertNotEquals(p1.id, p3.id)

    def test_serialization(self):
        import core.db.io
        p1 = self.create_port()
        xml_str = core.db.io.serialize(p1)
        p2 = core.db.io.unserialize(xml_str, Port)
        self.assertEquals(p1, p2)
        self.assertEquals(p1.id, p2.id)

    def testPort(self):
        x = Port()
        a = str(x)

    def test_registry_port_subtype(self):
        """Test registry isPortSubType"""
        descriptor = self.registry.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                                          'String')
        ports = self.registry.source_ports_from_descriptor(descriptor)
        assert self.registry.is_port_sub_type(ports[0], ports[0])

    def test_registry_ports_can_connect(self):
        """Test registry isPortSubType"""
        descriptor = self.registry.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                                          'String')
        oport = self.registry.source_ports_from_descriptor(descriptor)[0]
        iport = self.registry.destination_ports_from_descriptor(descriptor)[0]
        assert self.registry.ports_can_connect(oport, iport)


if __name__ == '__main__':
    unittest.main()

