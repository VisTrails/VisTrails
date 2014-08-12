###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
from vistrails.core.configuration import get_vistrails_configuration
""" This python module defines Connection class.
"""
import copy
from vistrails.db.domain import DBConnection
from vistrails.core.vistrail.port import PortEndPoint, Port

import unittest
from vistrails.db.domain import IdScope

################################################################################

class Connection(DBConnection):
    """ A Connection is a connection between two modules.
    Right now there's only Module connections.

    """

    ##########################################################################
    # Constructors and copy
    
    @staticmethod
    def from_port_specs(source, dest):
        """from_port_specs(source: PortSpec, dest: PortSpec) -> Connection
        Static method that creates a Connection given source and 
        destination ports.

        """
        conn = Connection()
        conn.source = copy.copy(source)
        conn.destination = copy.copy(dest)
        return conn
        
    @staticmethod
    def fromID(id):
        """fromTypeID(id: int) -> Connection
        Static method that creates a Connection given an id.

        """
        conn = Connection()
        conn.id = id
        conn.source.endPoint = PortEndPoint.Source
        conn.destination.endPoint = PortEndPoint.Destination
        return conn
    
    def __init__(self, *args, **kwargs):
        """__init__() -> Connection 
        Initializes source and destination ports.
        
        """
        DBConnection.__init__(self, *args, **kwargs)
        if self.id is None:
            self.db_id = -1
        if not len(self.ports) > 0:
            self.source = Port(type='source')
            self.destination = Port(type='destination')

    def __copy__(self):
        """__copy__() -> Connection -  Returns a clone of self.
        
        """
        return Connection.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConnection.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Connection
        for port in cp.ports:
            Port.convert(port)
        return cp

    ##########################################################################

    @staticmethod
    def convert(_connection):
#        print "ports: %s" % _Connection._get_ports(_connection)
        if _connection.__class__ == Connection:
            return
        _connection.__class__ = Connection

        for port in _connection.ports:
            Port.convert(port)

    ##########################################################################
    # Debugging

    def show_comparison(self, other):
        if type(other) != type(self):
            print "Type mismatch"
            return
        if self.__source != other.__source:
            print "Source mismatch"
            self.__source.show_comparison(other.__source)
            return
        if self.__dest != other.__dest:
            print "Dest mismatch"
            self.__dest.show_comparison(other.__dest)
            return
        print "no difference found"
        assert self == other

    ##########################################################################
    # Properties

    id = DBConnection.db_id
    ports = DBConnection.db_ports
    
    def add_port(self, port):
        self.db_add_port(port)

    def _get_sourceId(self):
        """ _get_sourceId() -> int
        Returns the module id of source port. Do not use this function, 
        use sourceId property: c.sourceId 

        """
        return self.source.moduleId

    def _set_sourceId(self, id):
        """ _set_sourceId(id : int) -> None 
        Sets this connection source id. It updates both self.__source.moduleId
        and self.__source.id. Do not use this function, use sourceId 
        property: c.sourceId = id

        """
        self.source.moduleId = id
        self.source.id = id
    sourceId = property(_get_sourceId, _set_sourceId)

    def _get_destinationId(self):
        """ _get_destinationId() -> int
        Returns the module id of dest port. Do not use this function, 
        use sourceId property: c.destinationId 

        """
        return self.destination.moduleId

    def _set_destinationId(self, id):
        """ _set_destinationId(id : int) -> None 
        Sets this connection destination id. It updates self.__dest.moduleId. 
        Do not use this function, use destinationId property: 
        c.destinationId = id

        """
        self.destination.moduleId = id
    destinationId = property(_get_destinationId, _set_destinationId)

    def _get_source(self):
        """_get_source() -> Port
        Returns source port. Do not use this function, use source property: 
        c.source 

        """
        try:
            return self.db_get_port_by_type('source')
        except KeyError:
            pass
        return None

    def _set_source(self, source):
        """_set_source(source: Port) -> None 
        Sets this connection source port. Do not use this function,
        use source property instead: c.source = source

        """
        try:
            port = self.db_get_port_by_type('source')
            self.db_delete_port(port)
        except KeyError:
            pass
        if source is not None:
            self.db_add_port(source)
    source = property(_get_source, _set_source)

    def _get_destination(self):
        """_get_destination() -> Port
        Returns destination port. Do not use this function, use destination
        property: c.destination 

        """
#        return self.db_ports['destination']
        try:
            return self.db_get_port_by_type('destination')
        except KeyError:
            pass
        return None

    def _set_destination(self, dest):
        """_set_destination(dest: Port) -> None
         Sets this connection destination port. Do not use this
        function, use destination property instead: c.destination = dest

        """
        try:
            port = self.db_get_port_by_type('destination')
            self.db_delete_port(port)
        except KeyError:
            pass
        if dest is not None:
            self.db_add_port(dest)
    destination = property(_get_destination, _set_destination)
    dest = property(_get_destination, _set_destination)

    ##########################################################################
    # Operators

    def __str__(self):
        """__str__() -> str - Returns a string representation of a Connection
        object. 

        """
        rep = "<connection id='%s'>%s%s</connection>"
        return  rep % (str(self.id), str(self.source), str(self.destination))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self.source == other.source and
                self.dest == other.dest)

    def equals_no_id(self, other):
        """Checks equality up to ids (connection and ports)."""
        if type(self) != type(other):
            return False
        return (self.source.equals_no_id(other.source) and
                self.dest.equals_no_id(other.dest))
    
################################################################################
# Testing


class TestConnection(unittest.TestCase):

    def create_connection(self, id_scope=IdScope()):
        from vistrails.core.vistrail.port import Port
        from vistrails.core.modules.basic_modules import identifier as basic_pkg
        source = Port(id=id_scope.getNewId(Port.vtType),
                      type='source', 
                      moduleId=21L, 
                      moduleName='String', 
                      name='value',
                      signature='(%s:String)' % basic_pkg)
        destination = Port(id=id_scope.getNewId(Port.vtType),
                           type='destination',
                           moduleId=20L,
                           moduleName='Float',
                           name='value',
                           signature='(%s:Float)' % basic_pkg)
        connection = Connection(id=id_scope.getNewId(Connection.vtType),
                                ports=[source, destination])
        return connection

    def test_copy(self):
        id_scope = IdScope()
        
        c1 = self.create_connection(id_scope)
        c2 = copy.copy(c1)
        self.assertEquals(c1, c2)
        self.assertEquals(c1.id, c2.id)
        c3 = c1.do_copy(True, id_scope, {})
        self.assertEquals(c1, c3)
        self.assertNotEquals(c1.id, c3.id)

    def test_serialization(self):
        import vistrails.core.db.io
        c1 = self.create_connection()
        xml_str = vistrails.core.db.io.serialize(c1)
        c2 = vistrails.core.db.io.unserialize(xml_str, Connection)
        self.assertEquals(c1, c2)
        self.assertEquals(c1.id, c2.id)

    def testEmptyConnection(self):
        """Tests sane initialization of empty connection"""
        c = Connection()
        self.assertEquals(c.source.endPoint, PortEndPoint.Source)
        self.assertEquals(c.destination.endPoint, PortEndPoint.Destination)
        
if __name__ == '__main__':
    unittest.main()
