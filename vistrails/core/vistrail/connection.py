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
""" This python module defines Connection class.
"""
if __name__ == '__main__':
    import qt
    global app
    app = qt.createBogusQtApp()

import copy
from db.domain import DBConnection
import core.modules.module_registry
from core.modules.vistrails_module import ModuleConnector
from core.utils import VistrailsInternalError
from core.vistrail.port import PortEndPoint, Port

registry = core.modules.module_registry.registry

################################################################################

def moduleConnection(conn):
    """moduleConnection(conn)-> function 
    Returns a function to build a module connection

    """
    def theFunction(src, dst):
        iport = conn.destination.name
        oport = conn.source.name
        src.enableOutputPort(oport)
        dst.set_input_port(iport, ModuleConnector(src, oport))
    return theFunction

################################################################################

class Connection(DBConnection):
    """ A Connection is a connection between two modules.
    Right now there's only Module connections.

    """

    ##########################################################################
    # Constructors and copy
    
    @staticmethod
    def fromPorts(source, dest):
        """fromPorts(source: Port, dest: Port) -> Connection
        Static method that creates a Connection given source and 
        destination ports.

        """
        conn = Connection()
        conn.source = source
        conn.destination = dest
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
    
    def __init__(self):
        """__init__() -> Connection 
        Initializes source and destination ports.
        
        """
	DBConnection.__init__(self)
	#        self.__source = Port()
	#	_Connection._get_ports(self)['source'] = Port()
	#       self.__dest = Port()
	#	_Connection._get_ports(self)['destination'] = Port()
        self.connectionMap = {}
	self.source = Port()
	self.destination = Port()
        self.source.endPoint = PortEndPoint.Source
        self.destination.endPoint = PortEndPoint.Destination
        self.makeConnection = moduleConnection(self)

    def __copy__(self):
        """__copy__() -> Connection -  Returns a clone of self.
        
        """
        cp = DBConnection.__copy__(self)
        cp.__class__ = Connection
#         cp.id = self.id
#         cp.source = copy.copy(self.source)
#         cp.destination = copy.copy(self.destination)
        cp.makeConnection = moduleConnection(cp)
        cp.connectionMap = copy.copy(self.connectionMap)
        return cp

    ##########################################################################

    @staticmethod
    def convert(_connection):
#	print "converting connection: %s" % _connection
#	print "ports: %s" % _Connection._get_ports(_connection)
        _connection.__class__ = Connection

        # set connection map here
        _connection.connectionMap = {}
        for port in _connection.db_get_ports():
            Port.convert(port)
            if port.db_type == 'source':
                _connection.connectionMap['source'] = port
            elif port.db_type == 'destination':
                _connection.connectionMap['destination'] = port

        _connection.sourceInfo = \
	    (_connection.source.moduleName, _connection.source.sig)
        _connection.destinationInfo = \
	    (_connection.destination.moduleName, _connection.destination.sig)
#        print _connection.sourceInfo
#        print _connection.destinationInfo
        portFromRepresentation = registry.portFromRepresentation
        newSource = \
	    portFromRepresentation(_connection.source.moduleName, 
				   _connection.source.sig,
				   PortEndPoint.Source, None, True)
	newDestination = \
	    portFromRepresentation(_connection.destination.moduleName,
				   _connection.destination.sig,
				   PortEndPoint.Destination, None, True)
	newSource.moduleId = _connection.source.moduleId
	newDestination.moduleId = _connection.destination.moduleId
	_connection.source = newSource
	_connection.destination = newDestination
        _connection.makeConnection = moduleConnection(_connection)

    def genSignatures(self):
	sourceSigs = self.source.getSignatures()
	if type(sourceSigs) == list and len(sourceSigs) == 1:
	    self.source.sig = str(self.source.name) + sourceSigs[0]

	destSigs = self.destination.getSignatures()
	if type(destSigs) == list:
	    destSig = self.findSignature(sourceSigs[0], destSigs)
	    if destSig is not None:
		self.destination.sig = \
		    str(self.destination.name) + destSig

    def findSignature(self, sig, signatures):
        """findSignature(sig:str, signatures:[]) -> str 

        It looks for a match of sig in signatures, including
        overloaded functions. Returns None if it can't find any.

        """
        if sig[1:-1]=='Variant':
            return signatures[0]
        splittedSig = sig[1:-1].split(',')
        if splittedSig == ['']: splittedSig = []
        for s in signatures:
            splittedS = s[1:-1].split(',')
            if splittedS == ['']: splittedS = []
            if len(splittedS)==len(splittedSig):
                for i in range(len(splittedS)):
                    d1 = registry.getDescriptorByName(splittedS[i].strip())
                    d2 = registry.getDescriptorByName(splittedSig[i].strip())
                    if not d1 or not d2 or not issubclass(d1.module, d2.module):
                        break
                return s
        return None

    def serialize(self, dom, el):
        """ serialize(dom, el) -> None: writes itself as XML """

        child = dom.createElement('connect')
        child.setAttribute('id', str(self.id))
        sourceSigs = self.source.getSignatures()
        assert type(sourceSigs) == list
        assert len(sourceSigs) == 1
        destSigs = self.destination.getSignatures()
        assert type(destSigs) == list
        destSig = self.findSignature(sourceSigs[0], destSigs)
        assert destSig != None
        child.setAttribute('sourceId', str(self.source.moduleId))
        child.setAttribute('sourceModule', str(self.source.moduleName))
	child.setAttribute('sourcePort', 
			   str(self.source.name) + sourceSigs[0])
        child.setAttribute('destinationId', str(self.destination.moduleId))
        child.setAttribute('destinationModule', 
			   str(self.destination.moduleName))
        child.setAttribute('destinationPort', 
			   str(self.destination.name) + destSig)
        el.appendChild(child)

    @staticmethod
    def loadFromXML(connection):
        """ loadFromXML(connection) -> Connection
        Static method that parses an xml element and creates a Connection.
        Keyword arguments:
          - connection : xml.dom.minidom.Element
   
        """
        cId = int(connection.getAttribute('id'))
        c = Connection()
        sourceModule = connection.getAttribute('sourceModule')
        destinationModule = connection.getAttribute('destinationModule')
        sourcePort = connection.getAttribute('sourcePort')
        destinationPort = connection.getAttribute('destinationPort')
        portFromRepresentation = registry.portFromRepresentation
        c.source = portFromRepresentation(sourceModule, sourcePort, 
                                          PortEndPoint.Source,
                                          None, True)
        c.destination = portFromRepresentation(destinationModule, 
                                               destinationPort, 
                                               PortEndPoint.Destination,
                                               None, True)
	c.genSignatures()
        c.id = cId
        c.sourceId = int(connection.getAttribute('sourceId'))
        c.destinationId = int(connection.getAttribute('destinationId'))
        return c

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
    # Operators

    def __str__(self):
        """__str__() -> str - Returns a string representation of a Connection
        object. 

        """
        rep = "<Connection>%s %s</Connection>"
        return  rep % (str(self.source), str(self.destination))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self.__source == other.__source and
                self.__dest == other.__dest)

    def equals_no_id(self, other):
        """Checks equality up to ids (connection and ports)."""
        if type(self) != type(other):
            return False
        return (self.__source.equals_no_id(other.__source) and
                self.__dest.equals_no_id(other.__dest))
    
    ##########################################################################
    # Properties

    def _get_id(self):
        """ _get_id() -> int
        Returns this connection id. Do not use this function, 
        use id property: c.id 

        """
        return self.db_id

    def _set_id(self, i):
        """ _set_id(i : int) -> None 
        Sets this connection id. It updates both connection ids of 
        self.__source and self.__dest. Do not use this function, use id 
        property: c.id = i

        """
        self.db_id = i
        self.source.connectionId = i
        self.destination.connectionId = i
    id = property(_get_id, _set_id)

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

    def _get_type(self):
        """_get_type() -> VistrailModuleType - Returns this connection type.
        Do not use this function, use type property: c.type = t 

        """
        return self.source.type

    def _set_type(self, t):
        """ _set_type(t: VistrailModuleType) -> None 
        Sets this connection type and updates self.__source.type and 
        self.__dest.type. It also updates the correct makeConnection function.
        Do not use this function, use type property: c.type = t

        """
        self.source.type = t
        self.destination.type = t
        self.updateMakeConnection()
    type = property(_get_type, _set_type)

    def _get_source(self):
        """_get_source() -> Port
        Returns source port. Do not use this function, use source property: 
        c.source 

        """
#	return self.db_ports['source']
        return self.connectionMap['source']

    def _set_source(self, source):
        """_set_source(source: Port) -> None 
        Sets this connection source port. It also updates this connection 
        makeConnection function. Do not use this function, use source 
        property instead: c.source = source

        """
        if self.connectionMap.has_key('source'):
            self.db_delete_port(self.connectionMap['source'])
        self.db_add_port(source)
        self.connectionMap['source'] = source
    source = property(_get_source, _set_source)

    def _get_destination(self):
        """_get_destination() -> Port
        Returns destination port. Do not use this function, use destination
        property: c.destination 

        """
#	return self.db_ports['destination']
        return self.connectionMap['destination']

    def _set_destination(self, dest):
        """_set_destination(dest: Port) -> None 
        Sets this connection destination port. It also updates this connection 
        makeConnection function. Do not use this function, use destination 
        property instead: c.destination = dest

        """
        if self.connectionMap.has_key('destination'):
            self.db_delete_port(self.connectionMap['destination'])
        self.db_add_port(dest)
        self.connectionMap['destination'] = dest
    destination = property(_get_destination, _set_destination)

################################################################################
# Testing

import unittest

class TestConnection(unittest.TestCase):

    def testModuleConnection(self):
        a = Connection.fromID(0)
        c = moduleConnection(a)
        def bogus(asd):
            return 3
        assert type(c) == type(bogus)

    def testEmptyConnection(self):
        """Tests sane initialization of empty connection"""
        c = Connection()
        self.assertEquals(c.source.endPoint, PortEndPoint.Source)
        self.assertEquals(c.destination.endPoint, PortEndPoint.Destination)
        
if __name__ == '__main__':
    unittest.main()
