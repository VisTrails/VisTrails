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
import core.modules.module_registry
from core.modules.vistrails_module import ModuleConnector
from core.utils import VistrailsInternalError
from core.vistrail.port import PortEndPoint, Port
from core.vistrail.module_param import VistrailModuleType

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
        dst.setInputPort(iport, ModuleConnector(src, oport))
    return theFunction

def noMakeConnection(conn):
    """noMakeConnection(conn)-> function 
    Returns a function that raises an Exception

    """
    def theFunction(src, dst):
        raise NoMakeConnection(conn)
    return theFunction

################################################################################

class Connection(object):
    """ A Connection is a connection between two modules.
    Right now there's only Module connections.

    """
    @staticmethod
    def fromPorts(source, dest):
        """fromPorts(source: Port, dest: Port) -> Connection
        Static method that creates a Connection given source and 
        destination ports.

        """
        conn = Connection()
        conn.source = source
        conn.destination = dest
        conn.updateMakeConnection()
        return conn
        
    @staticmethod
    def fromTypeID(type, id):
        """fromTypeID(type: VistrailModuleType.Module, id: int) -> Connection
        Static method that creates a Connection given type and id.

        """
        conn = Connection()
        conn.id = id
        conn.type = type
        conn.source.endPoint = PortEndPoint.Source
        conn.destination.endPoint = PortEndPoint.Destination
        conn.updateMakeConnection()
        return conn
    
    def __init__(self):
        """__init__() -> Connection 
        Initializes source and destination ports.
        
        """
        self.__source = Port()
        self.__dest = Port()
        self.source.endPoint = PortEndPoint.Source
        self.destination.endPoint = PortEndPoint.Destination

    def findSignature(self, sig, signatures):
        """findSignature(sig:str, signatures:[]) -> str 

        It looks for a match of sig in signatures, including
        overloaded functions. Returns None if it can't find any.

        """
        splittedSig = sig[1:-1].split(',')
	if splittedSig == ['']: splittedSig = []
        for s in signatures:
            splittedS = s[1:-1].split(',')
	    if splittedS == ['']: splittedS = []
            if len(splittedS)==len(splittedSig):
                for i in range(len(splittedS)):
                    d1 = registry.getDescriptorByName(splittedS[i])
                    d2 = registry.getDescriptorByName(splittedSig[i])
                    if not d1 or not d2 or not issubclass(d1.module, d2.module):
                        break
                return s
        return None

    def serialize(self, dom, el):
        """ serialize(dom, el) -> None: writes itself as XML """
        assert self.__source.type == VistrailModuleType.Module
        child = dom.createElement('connect')
        child.setAttribute('id', str(self.__source.connectionId))
        sourceSigs = self.__source.getSignatures()
        assert type(sourceSigs) == list
        assert len(sourceSigs) == 1
        destSigs = self.__dest.getSignatures()
        assert type(destSigs) == list
        destSig = self.findSignature(sourceSigs[0], destSigs)
        assert destSig != None
        child.setAttribute('sourceId', str(self.__source.moduleId))
        child.setAttribute('sourceModule', str(self.__source.moduleName))
        child.setAttribute('sourcePort', 
                           str(self.__source.name) + sourceSigs[0])
        child.setAttribute('destinationId', str(self.__dest.moduleId))
        child.setAttribute('destinationModule', str(self.__dest.moduleName))
        child.setAttribute('destinationPort', str(self.__dest.name) + destSig)
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
                                          PortEndPoint.Source)

        c.destination = portFromRepresentation(destinationModule, 
                                               destinationPort, 
                                               PortEndPoint.Destination)
        c.id = cId
        c.type = VistrailModuleType.Module
        c.sourceId = int(connection.getAttribute('sourceId'))
        c.destinationId = int(connection.getAttribute('destinationId'))
        return c

    def __str__(self):
        """__str__() -> str - Returns a string representation of a Connection
        object. 

        """
        rep = "<Connection>%s %s</Connection>"
        return  rep % (str(self.__source), str(self.__dest))

    def updateMakeConnection(self):
        """updateMakeConnection() -> None 
        Updates self.makeConnection to the right function according to 
        self.type. 
        
        """ 
        if self.type == VistrailModuleType.Module:
            c = moduleConnection
        else:
            c = noMakeConnection
        self.makeConnection = c(self)

    def __copy__(self):
        """__copy__() -> Connection -  Returns a clone of self.
        
        """
        cp = Connection()
        cp.id = self.id
        cp.source = copy.copy(self.source)
        cp.destination = copy.copy(self.destination)
        cp.type = self.type
        return cp

    def _get_id(self):
        """ _get_id() -> int
        Returns this connection id. Do not use this function, 
        use id property: c.id 

        """
        return self.__source.connectionId
    
    def _set_id(self, i):
        """ _set_id(i : int) -> None 
        Sets this connection id. It updates both connection ids of 
        self.__source and self.__dest. Do not use this function, use id 
        property: c.id = i

        """
        self.__source.connectionId = i
        self.__dest.connectionId = i
    id = property(_get_id, _set_id)

    def _get_sourceId(self):
        """ _get_sourceId() -> int
        Returns the module id of source port. Do not use this function, 
        use sourceId property: c.sourceId 

        """
        return self.__source.moduleId
    
    def _set_sourceId(self, id):
        """ _set_sourceId(id : int) -> None 
        Sets this connection source id. It updates both self.__source.moduleId
        and self.__source.id. Do not use this function, use sourceId 
        property: c.sourceId = id

        """
        self.__source.moduleId = id
        self.__source.id = id
    sourceId = property(_get_sourceId, _set_sourceId)
    
    def _get_destinationId(self):
        """ _get_destinationId() -> int
        Returns the module id of dest port. Do not use this function, 
        use sourceId property: c.destinationId 

        """
        return self.__dest.moduleId

    def _set_destinationId(self, id):
        """ _set_destinationId(id : int) -> None 
        Sets this connection destination id. It updates self.__dest.moduleId. 
        Do not use this function, use destinationId property: 
        c.destinationId = id

        """
        self.__dest.moduleId = id
    destinationId = property(_get_destinationId, _set_destinationId)

    def _get_type(self):
        """_get_type() -> VistrailModuleType - Returns this connection type.
        Do not use this function, use type property: c.type = t 

        """
        return self.__source.type

    def _set_type(self, t):
        """ _set_type(t: VistrailModuleType) -> None 
        Sets this connection type and updates self.__source.type and 
        self.__dest.type. It also updates the correct makeConnection function.
        Do not use this function, use type property: c.type = t

        """
        self.__source.type = t
        self.__dest.type = t
        self.updateMakeConnection()
    type = property(_get_type, _set_type)

    def _get_source(self):
        """_get_source() -> Port
        Returns source port. Do not use this function, use source property: 
        c.source 

        """
        return self.__source

    def _set_source(self, source):
        """_set_source(source: Port) -> None 
        Sets this connection source port. It also updates this connection 
        makeConnection function. Do not use this function, use source 
        property instead: c.source = source

        """
        self.__source = source        
        self.updateMakeConnection()
    source = property(_get_source, _set_source)

    def _get_destination(self):
        """_get_destination() -> Port
        Returns destination port. Do not use this function, use destination
        property: c.destination 

        """
        return self.__dest

    def _set_destination(self, dest):
        """_set_destination(dest: Port) -> None 
        Sets this connection destination port. It also updates this connection 
        makeConnection function. Do not use this function, use destination 
        property instead: c.destination = dest

        """
        self.__dest = dest
        self.updateMakeConnection()
    destination = property(_get_destination, _set_destination)
    
################################################################################
# Testing

import unittest

class TestConnection(unittest.TestCase):

    def testModuleConnection(self):
        a = Connection.fromTypeID(VistrailModuleType.Module, 0)
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
