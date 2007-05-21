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
import xml.dom.minidom
import xml.parsers.expat

from core.vistrail.vistrail import Vistrail
from core.utils import VistrailsInternalError
from core.utils.uxml import named_elements, XMLWrapper
from core.vistrail.action import Action
from core.data_structures.graph import Graph
from core.vistrail.pipeline import Pipeline
from core.vistrail import dbservice

################################################################################

class UnknownVersion(Exception):
    def __init__(self, fname):
        self.fname = fname
    def __str__(self):
        return "Can't determine version of file '%s'." % self.fname

################################################################################

class XMLParser(XMLWrapper):
    """Class to parse a vistrail from the XML representation.


    After instantiating an object, call 'openVistrail(filename)'
    to parse the xml file and then call 'getVistrail()'.
    
    Example of usage:

        >>> import xml_parser
        >>> parser = xml_parser.XMLParser()
        >>> parser.openVistrail('/path/to/vistrail.xml')
        >>> v = parser.getVistrail()

    """
    def oldOpenVistrail(self, filename):
        """oldOpenVistrail(filename: str) -> None 
        Parses a XML file.

        """
        self._filename = filename
        self.open_file(filename)
    
    def openVistrail(self, filename):
        self.myVistrail = dbservice.openVistrail(filename)

    def oldCloseVistrail(self):
        """closeVistrail() -> None 
        Removes the association with the XML file loaded by openVistrail 
        method. 

        """
        self.close_file()
    
    def closeVistrail(self):
        pass

    def vistrailVersion(self):
        """vistrailVersion() -> str 
        Returns version of vistrail file. First it tries reading version 
        attribute, if it is available. If not assumes to be in latest version.

        """
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
        """getVistrailBase() -> Vistrail 
        Returns a fresh vistrail representing the vistrail stored in the 
        XML file. 
        
        """
        def createTagMap(vistrail):
            """createTagMap(vistrail) -> None 
            Creates the vistrail.tagMap for the just-parsed XML file """
            root = self.dom.documentElement
            for tag in named_elements(root, 'tag'):
                tagName = tag.getAttribute('name')
                tagTime = tag.getAttribute('time')
                vistrail.addTag(str(tagName), int(tagTime))
        def createPrunedVersions(vistrail):
            """createPrunedVersions(vistrail) -> None
            Creates the vistrail.prunedVersions for the just-parsed XML file"""
            root = self.dom.documentElement
            for prune in named_elements(root, 'prune'):
                version = prune.getAttribute('time')
                vistrail.pruneVersion(int(version))
        def createSavedQueries(vistrail):
            """createSavedQueries(vistrail) -> None
            Creates the vistrail.savedQueries for the just-parsed XML file"""
            root = self.dom.documentElement
            savedQueries = []
            for query in named_elements(root, 'query'):
                qType = query.getAttribute('type')
                qName = query.getAttribute('name')
                qText = query.getAttribute('text')
                savedQueries.append((qType, qName, qText))
            vistrail.setSavedQueries(savedQueries)
        def createActionMap(vistrail):
            """createActionMap(vistrail) -> None 
            Creates the action map for the just-parsed XML file """
            root = self.dom.documentElement
            for xmlaction in named_elements(root, 'action'):
                action = Action.createFromXML(xmlaction)
                if action.notes:
                    action.notes = action.notes.strip('\n\t ')
                    #getting rid of notes generated with the None text
                    if action.notes == 'None':
                        action.notes = ''
                else:
                    action.notes = ''
                if vistrail.hasVersion(action.timestep):
                    msg = "XML file contains two actions with same time "
                    msg += str(action.timestep)
                    raise VistrailsInternalError(msg)
                else:
                    vistrail.addVersion(action)
        result = Vistrail()
        createActionMap(result)
        createTagMap(result)
        createPrunedVersions(result)
        createSavedQueries(result)
        result.invalidateCurrentTime()
        result.changed = False
        return result

    def getVistrailBase0_1_0(self):
        """getVistrailBase0_1_0() -> Vistrail 
        Returns a fresh vistrail representing the vistrail stored in the 
        XML file. This is for files with version 0.1.0 

        """
        def createTagMap(vistrail):
            """createTagMap(vistrail)-> None 
            Creates the vistrail.tagMap for the just-parsed XML file """
            root = self.dom.documentElement
            for tag in named_elements(root, 'tag'):
                tagName = tag.getAttribute('name')
                tagTime = tag.getAttribute('time')
                vistrail.addTag(str(tagName), int(tagTime))
        def createPrunedVersions(vistrail):
            """createPrunedVersions(vistrail) -> None
            Creates the vistrail.prunedVersions for the just-parsed XML file"""
            root = self.dom.documentElement
            for prune in named_elements(root, 'prune'):
                version = prune.getAttribute('time')
                vistrail.pruneVersion(int(version))
        def createSavedQueries(vistrail):
            """createSavedQueries(vistrail) -> None
            Creates the vistrail.savedQueries for the just-parsed XML file"""
            root = self.dom.documentElement
            savedQueries = []
            for query in named_elements(root, 'query'):
                qType = query.getAttribute('type')
                qName = query.getAttribute('name')
                qText = query.getAttribute('text')
                savedQueries.append((qType, qName, qText))
            vistrail.setSavedQueries(savedQueries)
        def createActionMap(vistrail):
            """createActionMap(vistrail) -> None 
            Creates the action map for the just-parsed XML file """
            root = self.dom.documentElement
            for xmlaction in named_elements(root, 'action'):
                action = Action.createFromXML(xmlaction, '0.1.0')
                if vistrail.hasVersion(action.timestep):
                    msg = "XML file contains two actions with the same time "
                    msg += +str(action.timestep)
                    raise VistrailsInternalError(mesg)
                else:
                    vistrail.addVersion(action)
        result = Vistrail()
        createActionMap(result)
        createTagMap(result)
        createPrunedVersions(result)
        createSavedQueries(result)
        result.invalidateCurrentTime()
        result.changed = False
        return result

    def translate0to0_1_0(self, vistrail):
        """translate0to0_1_0(vistrail) -> Vistrail
        Convert vistrail from version 0 to 0.1.0.
        
        """
        return vistrail

    def translate0_1_0to0_3_0(self, vistrail):
        """translate0_1_0to0_3_0(vistrail) -> Vistrail
        Convert vistrail from version 0.1.0 to 0.3.0.

        """
	#the problem is in the connections because they are incomplete
	#we need to materialize all the modules and complete the connection 
        #information
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

    def translate0_3_0to0_3_1(self, vistrail):
	# The change here is that we are honoring the 'cache' attribute, and 
	# it should be the case that the default value is 1, but it was
        # 0. We'll change that under the hood.
	for (v,a) in vistrail.actionMap.items():
	    if a.type == 'AddModule':
                if a.module.cache == 0:
                    a.module.cache = 1

	return vistrail


    def translate0_3_1to0_4_0(self, vistrail):
        # The change here is that every action will now contain
        # a field _inverse, that is another action such that

        # p' = copy.copy(p)
        # x.perform(p')
        # x._inverse.perform(p')
        # p' == p

        # for all actions x and pipelines p

        vistrail_graph = vistrail.getVersionGraph()
        pipeline = Pipeline()
        def enter_vertex(action_timestep):
            action = vistrail.actionMap[action_timestep]
            action._inverse = action.make_inverse(pipeline)
            action.perform(pipeline)
        def leave_vertex(action_timestep):
            action = vistrail.actionMap[action_timestep]
            try:
                action._inverse.perform(pipeline)
            except:
                print "FAILED"
                print self._filename
                print action, type(action), id(action)
                print action._inverse, type(action._inverse), id(action._inverse)
                print action.moduleId, action._inverse.moduleId
                print action.portType, action._inverse.portType
                print action.portName, action._inverse.portName
                print action.portSpec
                raise
        vistrail_graph.dfs(enter_vertex=enter_vertex,
                           leave_vertex=leave_vertex)
        return vistrail
        

    parseVersion = {'0': getVistrailBase,
                    '0.1.0': getVistrailBase0_1_0,
		    '0.3.0': getVistrailBase,
                    '0.3.1': getVistrailBase}

    graph = Graph()
    graph.add_vertex('0')
    graph.add_vertex('0.1.0')
    graph.add_vertex('0.3.0')
    graph.add_vertex('0.3.1')
    graph.add_edge('0', '0.1.0')
    graph.add_edge('0.1.0','0.3.0')
    graph.add_edge('0.3.0','0.3.1')
#     graph.add_edge('0.3.1','0.4.0')

    currentVersion = '0.3.1'

    def oldGetVistrail(self):
        """getVistrail() -> Vistrail
        Parses a vistrail file calling the specific functions according to 
        version. Returns a fresh vistrail.
        
        """
        def translateName(v):
            return v.replace('.','_')
    
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

    def getVistrail(self):
        Vistrail.convert(self.myVistrail)
        return self.myVistrail

################################################################################

import unittest
import core.system

class TestXmlParser(unittest.TestCase):
    def test1(self):
        """ Exercising reading file """
        parser = XMLParser()
        parser.openVistrail(core.system.vistrails_root_directory() +
                            '/tests/resources/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()

# FIXME this test doesn't apply since we're redirectory to db.services.io
#
#     def test2(self):
#         """ Exercise malformed loading. """
#         parser = XMLParser()

#         self.assertRaises(IOError, parser.openVistrail,
#                           core.system.vistrails_root_directory() +
#                           '/tests/resources/file_that_does_not_exist.xml')
#         import xml.parsers.expat
#         self.assertRaises(XMLParser.XMLParseError,
#                           parser.openVistrail,
#                           (core.system.vistrails_root_directory() +
#                            '/tests/resources/dummy_broken.xml'))
        

if __name__ == '__main__':
    unittest.main()
