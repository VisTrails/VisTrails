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
from db.domain import DBPort
from core.utils import enum
from core.utils import VistrailsInternalError, all
import core.modules.vistrails_module
import __builtin__
import copy

################################################################################

PortEndPoint = enum('PortEndPoint',
                    ['Invalid', 'Source', 'Destination'])

################################################################################

class Port(DBPort):
    """ A port denotes one endpoint of a Connection.

    self.spec: list of list of (module, str) 
    
    """

    ##########################################################################
    # Constructor and copy
    
    def __init__(self, *args, **kwargs):
	DBPort.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
#         self._sig = self.db_sig
#         if self.db_sig is not None:
#             self._name = self.
#             (self._name, self._spec) = self.make_name_spec_tuple()
#         else:
#             self._name = ""
#             self._spec = []
        if self.moduleId is None:
            self.moduleId = 0
        if self.moduleName is None:
            self.moduleName = ""
        if self.name is None:
            self.name = ""
        if self.specStr is None:
            self.specStr = ""
        
        self.optional = False
        self.sort_key = -1
        self._spec = None

    def __copy__(self):
        return Port.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPort.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Port
#         cp._name = self._name

        cp.optional = self.optional
        cp.sort_key = self.sort_key
        cp._spec = copy.copy(self._spec)
        return cp

    @staticmethod
    def convert(_port):
	_port.__class__ = Port
#         if _port.db_sig is not None:
#             (_port._name, _port._spec) = _port.make_name_spec_tuple()
#         else:
#             _port._name = ""
#             _port._spec = []

        _port.optional = False
        _port.sort_key = -1
        _port._spec = None
        # the following makes sense because _set_name actually fixes the name
        # for us for now.
        # _port._set_name(_port._get_name())

    ##########################################################################

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_endPoint(self):
	map = {'source': PortEndPoint.Source,
	       'destination': PortEndPoint.Destination}
	endPoint = self.db_type
	if map.has_key(endPoint):
	    return map[endPoint]
	return PortEndPoint.Invalid
    def _set_endPoint(self, endPoint):
	map = {PortEndPoint.Source: 'source',
	       PortEndPoint.Destination: 'destination'}
	if map.has_key(endPoint):
            self.db_type = map[endPoint]
	else:
            self.db_type = ''
    endPoint = property(_get_endPoint, _set_endPoint)

    def _get_moduleId(self):
        return self.db_moduleId
    def _set_moduleId(self, moduleId):
        self.db_moduleId = moduleId
    moduleId = property(_get_moduleId, _set_moduleId)

    def _get_moduleName(self):
        return self.db_moduleName
    def _set_moduleName(self, moduleName):
        self.db_moduleName = moduleName
    moduleName = property(_get_moduleName, _set_moduleName)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_specStr(self):
        return self.db_spec
    def _set_specStr(self, specStr):
        self.db_spec = specStr
    specStr = property(_get_specStr, _set_specStr)

    def _get_spec(self):
	return self._spec
    def _set_spec(self, spec):
	self._spec = spec
        self.specStr = self._spec.create_sigstring()
    spec = property(_get_spec, _set_spec)

    def _get_sig(self):
        return self.name + self.specStr
    sig = property(_get_sig)

		     
#     def _get_type(self):
#  	return self._type
#     def _set_type(self, type):
#  	self._type = type
#     type = property(_get_type, _set_type)


    def toolTip(self):
        """ toolTip() -> str
        Generates an appropriate tooltip for the port. 
        
        """
        d = {PortEndPoint.Invalid: "Invalid",
             PortEndPoint.Source: "Output",
             PortEndPoint.Destination: "Input"}
        return "%s port %s\n%s" % (d[self.endPoint], 
                                   self.name,
                                   self.spec.create_sigstring(short=True))

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
# FIXME module id can change...
#                self.moduleId == other.moduleId and
                self.moduleName == other.moduleName and
                self.name == other.name and
                self.specStr == other.specStr and
                self.optional == other.optional and
                self.sort_key == other.sort_key)
    
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
                self.specStr == other.specStr and
                self.optional == other.optional and
                self.sort_key == other.sort_key)

###############################################################################

import unittest
from db.domain import IdScope

if __name__ == '__main__':
    import core.modules.basic_modules
    import core.modules.module_registry
    
class TestPort(unittest.TestCase):
    def setUp(self):
        self.registry = core.modules.module_registry.registry

    def create_port(self, id_scope=IdScope()):
        port = Port(id=id_scope.getNewId(Port.vtType),
                    type='source',
                    moduleId=12L, 
                    moduleName='String', 
                    name='self',
                    spec='edu.utah.sci.vistrails.basic:String')
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

