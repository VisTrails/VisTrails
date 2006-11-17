# Check for testing
if __name__ == '__main__':
    import qt
    global app
    app = qt.createBogusQtApp()
import copy
from core.modules.module_registry import registry
from core.modules.vistrails_module import ModuleConnector

from core.utils import VistrailsInternalError
from core.vis_types import VisPortEndPoint, VisPort, VistrailModuleType

################################################################################

def visConnectionFromPorts(source, dest):
    return VisConnection.fromPorts(source, dest)
def visConnectionFromTypeID(type,id):
    return VisConnection.fromTypeID(type, id)

################################################################################

def moduleConnection(conn):
    def theFunction(src, dst):
        iport = conn.destination.name
        oport = conn.source.name
        src.enableOutputPort(oport)
        dst.setInputPort(iport, ModuleConnector(src, oport))
    return theFunction

def noMakeConnection(conn):
    def theFunction(src, dst):
        raise NoMakeConnection(conn)
    return theFunction

################################################################################

class VisConnection(object):
    """ A VistrailConnection is a connection between two modules.
    Right now there's only Module connections."""

    @staticmethod
    def fromPorts(source, dest):
        """ Creates a VisConnection given source and destination ports

        Parameters
        ----------

        - source : 'VisPort'
        - dest : 'VisPort'

        Returns
        -------

        - 'VisConnection'

        """
        conn = VisConnection()
        conn.source = source
        conn.destination = dest
        conn.updateMakeConnection()
        return conn
        
    @staticmethod
    def fromTypeID(type, id):
        """ Creates a VisConnection given type and id

        Parameters
        ----------

        - type : VistrailModuleType.Module
        - id : 'int' 

        Returns
        -------

        - 'VisConnection'

        """
        conn = VisConnection()
        conn.id = id
        conn.type = type
        conn.source.endPoint = VisPortEndPoint.Source
        conn.destination.endPoint = VisPortEndPoint.Destination
        conn.updateMakeConnection()
        return conn
    
    def __init__(self):
        self.__source = VisPort()
        self.__dest = VisPort()

    def findSignature(self, sig, signatures):
        splittedSig = sig[1:-1].split(',')
	if splittedSig == ['']: splittedSig = []
        for s in signatures:
            splittedS = s[1:-1].split(',')
	    if splittedS == ['']: splittedS = []
            if len(splittedS)==len(splittedSig):
                ok = True
                for i in range(len(splittedS)):
                    d1 = registry.getDescriptorByName(splittedS[i])
                    d2 = registry.getDescriptorByName(splittedSig[i])
                    if not d1 or not d2 or not issubclass(d1.module, d2.module):
                        ok = False
                        break
                return s
        return None

    def serialize(self, dom, el):
        """ serialize(dom, el): writes itself as XML """
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
        child.setAttribute('sourcePort', str(self.__source.name) + sourceSigs[0])
        child.setAttribute('destinationId', str(self.__dest.moduleId))
        child.setAttribute('destinationModule', str(self.__dest.moduleName))
        child.setAttribute('destinationPort', str(self.__dest.name) + destSig)
        el.appendChild(child)

    @staticmethod
    def loadFromXML(connection):
        cId = int(connection.getAttribute('id'))
        c = VisConnection()
        sourceModule = connection.getAttribute('sourceModule')
        destinationModule = connection.getAttribute('destinationModule')
        sourcePort = connection.getAttribute('sourcePort')
        destinationPort = connection.getAttribute('destinationPort')
        
        c.source = registry.portFromRepresentation(sourceModule, sourcePort, VisPortEndPoint.Source)
        c.destination = registry.portFromRepresentation(destinationModule, destinationPort, VisPortEndPoint.Destination)
        c.id = cId
        c.type = VistrailModuleType.Module
        c.sourceId = int(connection.getAttribute('sourceId'))
        c.destinationId = int(connection.getAttribute('destinationId'))
        return c

    def __str__(self):
        return "<VisConnection>%s %s</VisConnection>" % (str(self.__source), str(self.__dest))

    def pythonSource(self):
        """ c.pythonSource() - Outputs self as a python call suitable for exporting """
        raise VistrailsInternalError('unimplemented')

    def updateMakeConnection(self):
        if self.type == VistrailModuleType.Module:
            c = moduleConnection
        else:
            c = noMakeConnection
        self.makeConnection = c(self)

    def __copy__(self):
        cp = VisConnection()
        cp.id = self.id
        cp.source = copy.copy(self.source)
        cp.destination = copy.copy(self.destination)
        cp.type = self.type
        return cp

    def _get_id(self):
        return self.__source.connectionId
    def _set_id(self, i):
        self.__source.connectionId = i
        self.__dest.connectionId = i
    id = property(_get_id, _set_id)

    def _get_sourceId(self):
        return self.__source.moduleId
    def _set_sourceId(self, id):
        self.__source.moduleId = id
        self.__source.id = id
    sourceId = property(_get_sourceId, _set_sourceId)
    
    def _get_destinationId(self):
        return self.__dest.moduleId
    def _set_destinationId(self, id):
        self.__dest.moduleId = id
    destinationId = property(_get_destinationId, _set_destinationId)

    def _get_type(self):
        return self.__source.type
    def _set_type(self, t):
        self.__source.type = t
        self.__dest.type = t
        self.updateMakeConnection()
    type = property(_get_type, _set_type)

    def _get_source(self):
        return self.__source
    def _set_source(self, source):
        self.__source = source        
        self.updateMakeConnection()
    source = property(_get_source, _set_source)

    def _get_destination(self):
        return self.__dest
    def _set_destination(self, dest):
        self.__dest = dest
        self.updateMakeConnection()
    destination = property(_get_destination, _set_destination)
    
################################################################################
# Testing

import unittest

class TestVisConnection(unittest.TestCase):

    def testModuleConnection(self):
        a = VisConnection.fromTypeID(VistrailModuleType.Module, 0)
        c = moduleConnection(a)
        def bogus(asd):
            return 3
        assert type(c) == type(bogus)
        
if __name__ == '__main__':
    unittest.main()
