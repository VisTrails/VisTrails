import xml.dom.minidom

from core.xml_utils import *
from core.vistrail import Vistrail
from core.common import VistrailsInternalError
from core.vis_action import VisAction
from core.vis_macro import VisMacro
from core.data_structures import Graph

################################################################################

class UnknownVersion(Exception):
    def __init__(self, fname):
        self.fname = fname
    def __str__(self):
        return "Can't determine version of file '%s'." % self.fname

################################################################################

class XMLParser(object):
    """Class to parse a vistrail from the XML representation.


    After instantiating an object, call 'openVistrail(filename)'
    to parse the xml file and then call 'getVistrail()'.
    
    Example of usage:

        >>> import xml_parser
        >>> parser = xml_parser.XMLParser()
        >>> parser.openVistrail('/path/to/vistrail.xml')
        >>> v = parser.getVistrail()

    """
    def openVistrail(self, filename):
        """ Parses a XML file.

        Parameters
        ----------

        - filename : 'str'
          xml file to be parsed

        """
        self.filename = filename
        self.dom = xml.dom.minidom.parse(filename)

    def closeVistrail(self):
        """ Removes the association with the XML file loaded by openVistrail method """
        self.filename = None
        self.dom = None

    def vistrailVersion(self):
        root = self.dom.documentElement
        if str(root.nodeName) == 'visTrail':
	    version = root.getAttribute('version')
	    if version:
		return version
	    else:
		return '0.3.0'
        if (str(root.nodeName) != 'vistrail' or
            not root.getAttribute('version')):
            raise UnknownVersion(self.filename)

    def getVistrailBase(self):
        """ Returns a fresh vistrail representing the vistrail stored in the XML file """
        def createTagMap(vistrail):
            """ Creates the vistrail.tagMap for the just-parsed XML file """
            root = self.dom.documentElement
            for tag in named_elements(root, 'tag'):
                tagName = tag.getAttribute('name')
                tagTime = tag.getAttribute('time')
                vistrail.addTag(str(tagName), int(tagTime))
        def createActionMap(vistrail):
            """ Creates the action map for the just-parsed XML file """
            root = self.dom.documentElement
            for xmlaction in named_elements(root, 'action'):
                action = VisAction.createFromXML(xmlaction)
                if vistrail.hasVersion(action.timestep):
                    raise VistrailsInternalError("XML file contains two actions with the same time "+str(action.timestep) )
                else:
                    vistrail.addVersion(action)
        def createMacroMap(vistrail):
            """ Creates the macro map for the just-parsed XML file """
            root = self.dom.documentElement
            for xmlmacro in named_elements(root, 'macro'):
                macro = VisMacro.createFromXML(vistrail, xmlmacro)
                vistrail.addMacro(macro)
        def createDBTags(vistrail):
	    """ Loads the eXist DB stuff into the vistrail as loaded by the vistrail.serialize() method """
	    root = self.dom.documentElement
	    #  The loop should terminate after 1 pass, but it's safer this way.
	    for info in named_elements(root, 'dbinfo'):
		vistrail.remoteFilename = info.getAttribute('remoteFilename')
		vistrail.lastDBTime = info.getAttribute('remoteTime')
        result = Vistrail()
        createActionMap(result)
        createTagMap(result)
        createMacroMap(result)
        createDBTags(result)
        result.invalidateCurrentTime()
        result.changed = False
        return result

    def getVistrailBase0_1_0(self):
        """ Returns a fresh vistrail representing the vistrail stored in the XML file """
        def createTagMap(vistrail):
            """ Creates the vistrail.tagMap for the just-parsed XML file """
            root = self.dom.documentElement
            for tag in named_elements(root, 'tag'):
                tagName = tag.getAttribute('name')
                tagTime = tag.getAttribute('time')
                vistrail.addTag(str(tagName), int(tagTime))
        def createActionMap(vistrail):
            """ Creates the action map for the just-parsed XML file """
            root = self.dom.documentElement
            for xmlaction in named_elements(root, 'action'):
                action = VisAction.createFromXML(xmlaction, '0.1.0')
                if vistrail.hasVersion(action.timestep):
                    raise VistrailsInternalError("XML file contains two actions with the same time "+str(action.timestep) )
                else:
                    vistrail.addVersion(action)
        def createMacroMap(vistrail):
            """ Creates the macro map for the just-parsed XML file """
            root = self.dom.documentElement
            for xmlmacro in named_elements(root, 'macro'):
                macro = VisMacro.createFromXML(vistrail, xmlmacro)
                vistrail.addMacro(macro)
        def createDBTags(vistrail):
	    """ Loads the eXist DB stuff into the vistrail as loaded by the vistrail.serialize() method """
	    root = self.dom.documentElement
	    #  The loop should terminate after 1 pass, but it's safer this way.
	    for info in named_elements(root, 'dbinfo'):
		vistrail.remoteFilename = info.getAttribute('remoteFilename')
		vistrail.lastDBTime = info.getAttribute('remoteTime')
        result = Vistrail()
        createActionMap(result)
        createTagMap(result)
        createMacroMap(result)
        createDBTags(result)
        result.invalidateCurrentTime()
        result.changed = False
        return result

    def translate0to0_1_0(self, vistrail):
        return vistrail

    def translate0_1_0to0_3_0(self, vistrail):
	#the problem is in the connections because they are incomplete
	#we need to materialize all the modules and complete the connection information
	for (v,a) in vistrail.actionMap.items():
	    if a.type == 'AddConnection':
		id = a.connection.id
		p = vistrail.getPipeline(v)
		sourceId = a.connection.sourceId
		destinationId = a.connection.destinationId
		sourceModule = p.getModuleById(sourceId)
		destinationModule = p.getModuleById(destinationId)
		    
		for p in sourceModule.sourcePorts():
		    if p.name == a.connection.source.name:
			if a.connection.source.name == 'self':
			    for s in p.getSignatures():
				if sourceModule.name == s[1:-1]:
				    a.connection.source = p
				    break
			else:
			    a.connection.source = p
			    break

		for p in destinationModule.destinationPorts():
		    if p.name == a.connection.destination.name:
			a.connection.destination = p
			break
		a.connection.id = id
		a.connection.destinationId = destinationId
		a.connection.sourceId = sourceId

	return vistrail

    parseVersion = {'0': getVistrailBase,
                    '0.1.0': getVistrailBase0_1_0,
		    '0.3.0': getVistrailBase}

    graph = Graph()
    graph.addVertex('0')
    graph.addVertex('0.1.0')
    graph.addVertex('0.3.0')
    graph.addEdge('0', '0.1.0')
    graph.addEdge('0.1.0','0.3.0')

    currentVersion = '0.3.0'

    def getVistrail(self):
        def translateName(v):
            return v.replace('.','_')
        """ Returns a fresh vistrail representing the vistrail stored in the XML file """
        version = self.vistrailVersion()
        vistrail = self.parseVersion[version](self)

        # Compute path through version graph to translate version to current one
        v = self.graph.bfs(version)
        path = [XMLParser.currentVersion]
        while path[-1] != version:
            path.append(v[path[-1]])
        path.reverse()
        for i in xrange(len(path)-1):
            funname = ('translate' + translateName(path[i]) +
                       'to' + translateName(path[i+1]))
            vistrail = getattr(self, funname)(vistrail)
        return vistrail

################################################################################

import unittest

