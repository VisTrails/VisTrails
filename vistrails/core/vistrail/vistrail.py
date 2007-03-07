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
""" This file contains the definition of the class Vistrail """
if __name__ == '__main__':
    import qt
    global app
    app = qt.createBogusQtApp()

import xml.dom.minidom
import copy
import time
import getpass
import copy
import string
from core.vistrail.module_param import VistrailModuleType
from core.vistrail.pipeline import Pipeline
from core.data_structures.graph import Graph
from core.debug import DebugPrint
from core.utils import enum, VistrailsInternalError

################################################################################

class Vistrail(object):
    def __init__(self):
        self.changed = False
        self.actionMap = {}
        self.tagMap = {}
        self.inverseTagMap = {}
        self.latestTime = 1
        self.macroMap = {}
        self.macroIdMap = {}
        self.currentVersion = -1
        self.expand=[] #to expand selections in versiontree
        self.currentGraph=None
        self.lastDBTime = 0
        self.remoteFilename = ""

    def getVersionName(self, version):
        """ getVersionName(version) -> str 
        Returns the name of a version, if it exists. Returns an empty string
        if it doesn't. 
        
        """
        if self.inverseTagMap.has_key(version):
            return self.inverseTagMap[version]
        else:
            return ""
    
    def getPipeline(self, version):
        """getPipeline(number or tagname) -> Pipeline
        Return a pipeline object given a version number or a version name. 

        """
        return Vistrail.getPipelineDispatcher[type(version)](self, version)
    
    def getPipelineVersionName(self, version):
        """getPipelineVersionName(version:str) -> Pipeline
        Returns a pipeline given a version name. If version name doesn't exist
        it will return None.

        """
        if self.tagMap.has_key(version):
            number = self.tagMap[version]
            return self.getPipelineVersionNumber(number)
        else:
            return None
    
    def getPipelineVersionNumber(self, version):
        """getPipelineVersionNumber(version:int) -> Pipeline
        Returns a pipeline given a version number.

        """
        result = Pipeline()
        if version == 0:
            return result
        for action in self.actionChain(version):
            action.perform(result)
        for connection in result.connections.values():
            if connection.type == VistrailModuleType.Object:
                moduleId = connection.sourceId
                connection.objectType = result.getModuleById(moduleId).name
        return result

    def getPipelineDiffByAction(self, v1, v2):
        """ getPipelineDiffByAction(v1: int, v2: int) -> tuple(list,list,list)        
        Compute the diff between v1 and v2 just by looking at the
        action chains. The value returned is a tuple containing lists
        of shared, v1 not v2, and v2 not v1 modules
        
        """
        # Get first common ancestor
        p = self.getFirstCommonVersion(v1,v2)
        
        # Get the modules present in v1 and v2
        v1andv2 = []
        v2Only = []
        v1Only = []
        sharedCreations = []
        parent = self.getPipeline(p)
        for m in parent.modules.keys():
            v1andv2.append(m)
            sharedCreations.append(m)
        l1 = self.actionChain(v1,p)
        l2 = self.actionChain(v2,p)
        l = l1 + l2

        # Take deleted modules out of shared modules
        for a in l:
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in v1andv2:
                        v1andv2.remove(id)

        # Add deleted "shared modules" of v2 to v1
        for a in l2:
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in sharedCreations:
                        v1Only.append(id)
                        
        # Add deleted "shared modules" of v1 to v2
        for a in l1:
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in sharedCreations:
                        v2Only.append(id)

        # Add module created by v1 only
        for a in l1:
            if a.type == "AddModule":
                if a.module.id not in v1Only:
                    v1Only.append(a.module.id)
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in v1Only:
                        v1Only.remove(id)
                    
        # Add module created by v2 only
        for a in l2:
            if a.type == "AddModule":
                if a.module.id not in v2Only:
                    v2Only.append(a.module.id)
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in v2Only:
                        v2Only.remove(id)
                    
        return (v1andv2,v1Only,v2Only)

    def getPipelineDiff(self, v1, v2):
        """ getPipelineDiff(v1: int, v2: int) -> tuple        
        Perform a diff between 2 versions, this will obtain the shared
        modules by getting shared nodes on the version tree. After,
        that, it will perform a heuristic algorithm to match
        signatures of modules to get more shared/diff modules. The
        heuristic is O(N^2), where N = the number of modules

        Keyword arguments:
        v1     --- the first version number
        v2     --- the second version number
        return --- (p1, p2: VistrailPipeline,
                    [shared modules (id in v1, id in v2) ...],
                    [v1 not v2 modules],
                    [v2 not v1 modules],
                    [parameter-changed modules (see-below)])

        parameter-changed modules = [((module id in v1, module id in v2),
                                      [(function in v1, function in v2)...]),
                                      ...]
        
        """
        # Instantiate pipelines associated with v1 and v2
        p1 = self.getPipelineVersionNumber(v1)
        p2 = self.getPipelineVersionNumber(v2)

        # Find the shared modules deriving from the version tree
        # common ancestor
        (v1Andv2, v1Only, v2Only) = self.getPipelineDiffByAction(v1, v2)

        # Convert v1Andv2 to a list of tuple
        v1Andv2 = [(i,i) for i in v1Andv2]

        # Looking for more shared modules by looking at all modules of
        # v1 and determine if there is an corresponding one in v2.
        # Only look by name for now
        for m1id in copy.copy(v1Only):
            m1 = p1.modules[m1id]
            for m2id in v2Only:
                m2 = p2.modules[m2id]
                if m1.name==m2.name:
                    v1Andv2.append((m1id, m2id))
                    v1Only.remove(m1id)
                    v2Only.remove(m2id)
                    break

        # Capture parameter changes
        paramChanged = []
        for (m1id,m2id) in copy.copy(v1Andv2):
            m1 = p1.modules[m1id]
            m2 = p2.modules[m2id]
            # Get signatures of all functions in m1 and m2
            signature1 = []
            signature2 = []
            for f1 in m1.functions:
                signature1.append((f1.name,
                                   [(p.type, str(p.strValue))
                                    for p in f1.params]))
            for f2 in m2.functions:
                signature2.append((f2.name,
                                   [(p.type, str(p.strValue))
                                    for p in f2.params]))

            if signature1!=signature2:
                v1Andv2.remove((m1id,m2id))
                paramMatching = []
                id2 = 0
                for s1 in signature1:
                    # Looking for a match and perform a panel-to-panel
                    # comparison
                    i = id2
                    match = None
                    while i<len(signature2):
                        s2 = signature2[i]
                        if s1==s2:
                            match = i
                            break
                        if s1[0]==s2[0] and match==None:
                            match = i
                        i += 1
                    if match!=None:
                        paramMatching.append((s1, signature2[match]))
                        while id2<match:
                            paramMatching.append(((None, None), signature2[id2]))
                            id2 += 1
                        id2 += 1
                    else:
                        paramMatching.append((s1, (None, None)))
                while id2<len(signature2):
                    paramMatching.append(((None, None), signature2[id2]))
                    id2 += 1
                paramChanged.append(((m1id,m2id),paramMatching))
        return (p1, p2, v1Andv2, v1Only, v2Only, paramChanged)                    
                        
    def getFirstCommonVersion(self, v1, v2):
        """ Returns the first version that it is common to both v1 and v2 
        Parameters
        ----------
        - v1 : 'int'
         version number 1

        - v2 : 'int'
         version number 2

        """
        t1 = []
        t2 = []
        t1.append(v1)
        t = self.actionMap[v1].parent
        while  t != 0:
            t1.append(t)
            t = self.actionMap[t].parent
        
        t = v2
        while t != 0:
            if t in t1:
                return t
            t = self.actionMap[t].parent
        return 0
    
    def getLastCommonVersion(self, v):
        """getLastCommonVersion(v: Vistrail) -> int
        Returns the last version that is common to this vistrail and v
	
        """
        # TODO:  There HAS to be a better way to do this...
        common = []
        for action in self.actionMap:
            if(v.hasVersion(action.timestep)):
                common.append(action.timestep)
                
        timestep = 0
        for time in common:
            if time > timestep:
                timestep = time

        return timestep	
		    
    def actionChain(self, t, start=0):
        """ actionChain(t:int, start=0) -> [Action]  
        Returns the action chain (list of Action)  necessary to recreate a 
        pipeline from a  certain time
                      
        """
        result = []
        action = self.actionMap[t]
        
        while 1:
            result.append(action)
            if action.timestep == start:
                break
            if action.parent == start:
                if start != 0:
                    action = self.actionMap[action.parent]
                break
            action = self.actionMap[action.parent]
        result.reverse()
        return result
    
    def hasVersion(self, version):
        """hasVersion(version:int) -> boolean
        Returns True if version with given timestamp exists

        """
        return self.actionMap.has_key(version)
    
    def addVersion(self, action):
        """ addVersion(action: Action) -> None 
        Adds new version to vistrail
          
        """
        if self.actionMap.has_key(action.timestep):
            raise VistrailsInternalError("existing timestep")
        self.latestTime = max(self.latestTime, action.timestep+1)
        self.actionMap[action.timestep] = action
        self.changed = True
        action.vistrail = self

    def hasTag(self, tag):
        """ hasTag(tag) -> boolean 
        Returns True if a tag with given name or number exists
       
        """
        if type(tag) == type(0):
            return self.inverseTagMap.has_key(tag)
        elif type(tag) == type('str'):
            return self.tagMap.has_key(tag)
        
    def addTag(self, version_name, version_number):
        """addTag(version_name, version_number) -> None
        Adds new tag to vistrail
          
        """
        if self.inverseTagMap.has_key(version_number):
            DebugPrint.log("Version is already tagged")
            raise VersionAlreadyTagged()
        if self.tagMap.has_key(version_name):
            DebugPrint.log("Tag already exists")
            raise TagExists()
        self.tagMap[version_name] = version_number
        self.inverseTagMap[version_number] = version_name
        self.changed = True
        
    def changeTag(self, version_name, version_number):
        """changeTag(version_name, version_number) -> None        
        Changes the old tag of version_number to version_name in the
        vistrail.  If version_name is empty, this version will be
        untagged.
                  
        """
        if not self.inverseTagMap.has_key(version_number):
            DebugPrint.log("Version is not tagged")
            raise VersionNotTagged()
        if self.inverseTagMap[version_number] == version_name:
            return None
        if self.tagMap.has_key(version_name):
            DebugPrint.log("Tag already exists")
            raise TagExists()
        self.tagMap.pop(self.inverseTagMap[version_number])
        if version_name=='':
            self.inverseTagMap.pop(version_number)
        else:
            self.inverseTagMap[version_number] = version_name
            self.tagMap[version_name] = version_number
        self.changed = True

    def changenotes(self, notes, version_number):
        """ changenotes(notes:str, version_number) -> None 
        Changes the notes of a version
                  
        """
    
        if self.actionMap.has_key(version_number):
            self.actionMap[version_number].notes = notes
        self.changed = True
        
    def getVersionGraph(self):
        """getVersionGraph() -> Graph 
        Returns the version graph
        
        """
        result = Graph()
        result.addVertex(0)
        for action in self.actionMap.values():
            result.addEdge(action.parent,
                           action.timestep,
                           0)
        return result

    def getTerseGraph(self):
        """ getTerseGraph() -> Graph 
        Returns the version graph skiping the non-tagged internal nodes. 
        Branches are kept.
        
        """
        complete = self.getVersionGraph()
        x = []
        x.append(0)
        while len(x):
            current = x.pop()
            efrom = complete.edgesFrom(current)
            eto = complete.edgesTo(current)

            for (e1,e2) in efrom:
                x.append(e1)
            if len(efrom) == 1 and len(eto) == 1 and not self.hasTag(current):
                to_me = eto[0][0]
                from_me = efrom[0][0]
                complete.deleteEdge(to_me, current, None)
                complete.deleteEdge(current, from_me, None)
                complete.addEdge(to_me, from_me, -1)
                complete.deleteVertex(current)
        return complete

    def getSemiTerseGraph(self):
        """ getSemiTerseGraph() -> Graph 
        Uses the data in self.expand to expand a localized part of the graph
        self.expand has tuples to be expanded. (list of tuples)

        """

        fullgraph=self.getVersionGraph()
        result=self.getCurrentGraph()

        highest=lowest=0

        if len(self.expand):
            lowest=0
            highest=self.expand[0][0]

        while len(self.expand):
            (v1,v2)=self.expand.pop()
            bottom=max(v1,v2)
            top=min(v1,v2)
            lowest=max(lowest,bottom)
            highest=min(highest,top)
            V = result.vertices
            #check to see if the edge is there, since the graph may be refined
            if V.has_key(top) and V.has_key(bottom):
                if ( (bottom,-1) in result.edgesFrom(top) and 
                     (top,-1) in result.edgesTo(bottom) ):
                    result.deleteEdge(top,bottom,-1)
            while bottom>top:
                p=fullgraph.parent(bottom)
                result.addVertex(p)
                result.addEdge(p,bottom,0) #0 means not annotated
                bottom=p
         #on a refined expansion, this is necessary
        if ( (lowest,-1) in result.edgesFrom(highest) and 
             (highest,-1) in result.edgesTo(lowest) ):
            result.deleteEdge(highest,lowest,-1)
            
        #self.currentGraph=result.__copy__()
        self.expand=[]
        return result

    def getCurrentGraph(self):
        """getCurrentGraph() -> Graph
        returns the current version graph. if there is not one, returns the
        terse graph instead 

        """
        if not self.currentGraph:
            self.currentGraph=copy.copy(self.getTerseGraph())
        return self.currentGraph

    def setCurrentGraph(self, newGraph):
        """setCurrentGraph(newGraph: Graph) -> None
        Sets a copy of newGraph as the currentGraph. 

        """
        self.currentGraph=copy.copy(newGraph)

    def invalidateCurrentTime(self):
        """ invalidateCurrentTime() -> None 
        Recomputes the next unused timestep from scratch  
        """
        self.latestTime = max(self.actionMap.keys())
        self.latestTime += 1
                
    def getFreshTimestep(self):
        """getFreshTimestep() -> int - Returns an unused timestep. """

        return self.latestTime

    def getDate(self):
	""" getDate() -> str - Returns the current date and time. """
	return time.strftime("%d %b %Y %H:%M:%S", time.localtime())
    
    def getUser(self):
	""" getUser() -> str - Returns the username. """
	return getpass.getuser()

    def serialize(self, filename):
        """serialize(filename:str) -> None 
        Writes vistrail to disk under given filename.
          
        """
        #couldn't remove this because of circular reference in xml_parser
        import core.xml_parser 
        version = core.xml_parser.XMLParser().currentVersion
        impl = xml.dom.minidom.getDOMImplementation()
        dom = impl.createDocument(None, 'visTrail', None)
        root = dom.documentElement
        root.setAttribute('version', str(version))
        for action in self.actionMap.values():
            actionElement = dom.createElement('action')
            actionElement.setAttribute('time', str(action.timestep))
            actionElement.setAttribute('parent', str(action.parent))
            if action.date != None:
                actionElement.setAttribute('date', str(action.date))
            if action.user != None:
                actionElement.setAttribute('user', str(action.user))
            if action.notes != None:
                action.notes = action.notes.strip()
            if action.notes != '':
                notesElement = dom.createElement('notes')
                text = dom.createTextNode(str(action.notes))
                notesElement.appendChild(text)
                actionElement.appendChild(notesElement)
            root.appendChild(actionElement)
            action.serialize(dom, actionElement)
        for (name, time) in self.tagMap.items():
            tagElement = dom.createElement('tag')
            tagElement.setAttribute('name', str(name))
            tagElement.setAttribute('time', str(time))
            root.appendChild(tagElement)
        for macro in self.macroMap.values():
            macro.serialize(dom,root)
        if len(self.remoteFilename) > 0:
            el = dom.createElement('dbinfo')
            el.setAttribute('remoteFilename', str(self.remoteFilename))
            el.setAttribute('remoteTime', str(self.lastDBTime))
            root.appendChild(el)
        outputFile = file(filename,'w')
        root.writexml(outputFile, "  ", "  ", '\n')
        outputFile.close()
        self.changed = False

    def applyMacro(self,name,pipeline):
        """applyMacro(name:str, pipeline:Pipeline) -> None
        Applies a macro to a given pipeline
         
        """
        self.macroMap[name].applyMacro(pipeline)

    def addMacro(self, macro):
        """addMacro(macro:Macro) -> None 
        Adds a macro to macroMap.

        """
        if self.macroMap.has_key(macro.name):
            raise MacroExists(macro.name)
        macro.id = self.freshMacroId()
        if macro.name == '':
            macro.name = 'noname' + str(macro.id)
        self.macroMap[macro.name] = macro
        self.macroIdMap[macro.id] = macro
        self.changed = True

    def deleteMacro(self, id):
        """deleteMacro(id) -> None 
        Deletes a macro with a given id """
        macro = self.macroIdMap[id]
        del self.macroIdMap[id]
        del self.macroMap[macro.name]
        
    def changeMacroName(self,oldname):
        """ changeMacroName(oldname) -> None 
        The macro has changed its name. This updates the key (name) of the
        macro in the macroMap.
          
        """
        macro = self.macroMap[oldname]
        if self.macroMap.has_key(macro.name):
            raise MacroExists(macro.name)
        else:
            self.macroMap.pop(oldname)
            self.macroMap[macro.name] = macro

    def freshMacroId(self):
        """freshMacroId() -> int - Returns an unused macro id """
        # This is dumb and slow
        m = 0
        while self.macroIdMap.has_key(m):
            m += 1
        return m

    def setExp(self, exp):
        """setExp(exp) -> None - Set current list of nodes to be expanded"""
        self.expand=exp

    # Dispatch in runtime according to type
    getPipelineDispatcher = {}
    getPipelineDispatcher[type(0)] = getPipelineVersionNumber
    getPipelineDispatcher[type('0')] = getPipelineVersionName

    class InvalidAbstraction(Exception):
        pass

    def create_abstraction(self,
                           pipeline_version,
                           subgraph,
                           abstraction_name):
        pipeline = self.getPipeline(pipeline_version)
        current_graph = pipeline.graph
        if not current_graph.topologically_contractible(subgraph):
            msg = "Abstraction violates DAG constraints."
            raise self.InvalidAbstraction(msg)
        input_ports = current_graph.connections_to_subgraph(subgraph)
        output_ports = current_graph.connections_from_subgraph(subgraph)

        print "Inputs: "
        
        print "Outputs:"
        
##############################################################################

class VersionAlreadyTagged(Exception):
    def __str__(self):
        return "Version is already tagged"
    pass

class TagExists(Exception):
    def __str__(self):
        return "Tag already exists"
    pass

class VersionNotTagged(Exception):
    def __str__(self):
        return "Version is not tagged"
    pass

class MacroExists(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Macro '"+ self.name + "' already exists"
    pass

import unittest

class TestVistrail(unittest.TestCase):
    def test1(self):
        import core.vistrail
        import core.xml_parser
        import core.system
        parser = core.xml_parser.XMLParser()
        parser.openVistrail(core.system.visTrailsRootDirectory() +
                            '/tests/resources/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        #testing nodes in different branches
        v1 = 36
        v2 = 41
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)
        
        #testing nodes in the same branch
        v1 = 15
        v2 = 36
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)

        if p1 == 0 or p2 == 0:
            self.fail("vistrails tree is not single rooted.")

    def test2(self):
        import core.vistrail
        import core.xml_parser
        parser = core.xml_parser.XMLParser()
        parser.openVistrail(core.system.visTrailsRootDirectory() +
                            '/tests/resources/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        #testing diff
        v1 = 17
        v2 = 27
        v3 = 22
        v.getPipelineDiff(v1,v2)
        v.getPipelineDiff(v1,v3)

#     def test_abstraction(self):
#         import core.vistrail
#         import core.xml_parser
#         parser = core.xml_parser.XMLParser()
#         parser.openVistrail(core.system.visTrailsRootDirectory() +
#                             '/tests/resources/ect.xml')
#         v = parser.getVistrail()
#         parser.closeVistrail()
#         #testing diff
#         p = v.getPipeline('WindowedSync (lambda-mu) Error')
#         print p.modules[43], p.modules[45]
#         print p.graph

if __name__ == '__main__':
    unittest.main()
