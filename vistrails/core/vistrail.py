from vis_pipeline import VisPipeline
from vis_connection import VisConnection
from vis_types import *
from graph import Graph
from debug import DebugPrint
from vis_macro import VisMacro
from xUpdateFunctions import UpdateFunctions
import xml.dom.minidom
import copy
import time
import getpass
import copy
import string
from enum import enum


class Vistrail(object):
    def __init__(self):
        self.changed = False
        self.actionMap = {}
        self.tagMap = {}
        self.inverseTagMap = {}
        self.latestTime = 0
        self.macroMap = {}
        self.macroIdMap = {}
        self.currentVersion = -1
        self.expand=[] #to expand selections in versiontree
        self.currentGraph=None
	self.lastDBTime = 0
	self.remoteFilename = ""

    def getVersionName(self, version):
        if self.inverseTagMap.has_key(version):
            return self.inverseTagMap[version]
        
    def getPipeline(self, version):
        """V.getPipeline(number or tagname) -> Pipeline

        Returns
        -------
        - 'VisPipeline'
        
        """
        return Vistrail.getPipelineDispatcher[type(version)](self, version)
    
    def getPipelineVersionName(self, version):
        """Returns a pipeline given a version name

        Parameters
        ----------

        - version : 'str'
          the version name

        Returns
        -------

        - 'VisPipeline'

        """
        number = self.tagMap[version]
        return self.getPipelineVersionNumber(number)
    
    def getPipelineVersionNumber(self, version):
        """Returns a pipeline given a version number

        Parameters
        ----------

        - version : 'int'
          the version number

        Returns
        -------

        - 'VisPipeline'

        """
        result = VisPipeline()
        if version == 0:
            return result
        for action in self.actionChain(version):
            action.perform(result)
        for connection in result.connections.values():
            if connection.type == VistrailModuleType.Object:
                moduleId = connection.sourceId
                connection.objectType = result.getModuleById(moduleId).name
        return result

    def getPipelineShare(self, v1, v2):
        """ Returns a list of shared modules between the two versions 
        Parameters
        ----------
        - v1 : 'int'
         version number 1

        - v2 : 'int'
         version number 2

        """
        #get first common ancestor
        p = self.getFirstCommonVersion(v1,v2)

        #get the modules present in v1 and v2
        #this is not good
        parent = self.getPipeline(p)
        v1andv2 = []
        notInV1 = []
        notInV2 = []
        pm = []
        for m in parent.modules.keys():
            v1andv2.append(m)
            pm.append(m)
        l1 = self.actionChain(v1,p)
        l2 = self.actionChain(v2,p)
        l = l1 + l2
        for a in l:
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in v1andv2:
                        v1andv2.remove(id)
        for a in l2:
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in pm:
                        notInV2.append(id)
        for a in l1:
            if a.type == "DeleteModule":
                for id in a.ids:
                    if id in pm:
                        notInV1.append(id)

        for a in l1:
            if a.type == "AddModule":
                if a.module.id not in notInV2:
                    notInV2.append(a.module.id)
        for a in l2:
            if a.type == "AddModule":
                if a.module.id not in notInV1:
                    notInV1.append(a.module.id)

        v1param = {}
        for a in l1:
            if a.type == "ChangeParameter" and a.parameters:
                if a.parameters[0][0] in v1andv2:
                    values = [p[5] for p in a.parameters]
                    if not (a.parameters[0][0] in v1param):
                        v1param[a.parameters[0][0]] = []
                    v1param[a.parameters[0][0]].append(string.joinfields([a.parameters[0][2],'(',
                                                                          string.joinfields(values,','),
                                                                          ')'],''))
        v2param = {}
        for a in l2:
            if a.type == "ChangeParameter" and a.parameters:
                if a.parameters[0][0] in v1andv2:
                    values = [p[5] for p in a.parameters]
                    if not (a.parameters[0][0] in v2param):
                        v2param[a.parameters[0][0]] = []
                    v2param[a.parameters[0][0]].append(string.joinfields([a.parameters[0][2],'(',
                                                                          string.joinfields(values,','),
                                                                          ')'],''))
        return [v1andv2,v1param,v2param]
            
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
    
    def getLastCommonVersion(self, v):
        """Returns the last version that is common to both v1 and v2
	Parameters
        -----------------
        - v : The VisTrail to compare to.
        
        - returns:  The timestep representing the last version common
        to both vistrails.
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

    def writeToDB(self, filepath, server, username, password):
        """ Writes the vistrail to eXist database given the full path to the file"""
        tempTimestamp = 0
        tagElements = []
        macroElements = []
        update = UpdateFunctions(server, username, password)
        if(update.docExists(filepath)):
            tempDoc = update.getDom(filepath)
            actionElements = tempDoc.getElementsByTagName("action")
            tempLen = len(actionElements)
            tempTimestamp = 0
            for act in actionElements:
                t = act.getAttribute("time")
                if t > tempTimestamp:
                    tempTimestamp = t
            tagElements = tempDoc.getElementsByTagName("tag")
            macroElements = tempDoc.getElementsByTagName("macro")
                        
        source = """("""
        actionLen = len(self.actionMap.values())
        tagLen = len(self.tagMap.items())
        macroLen = len(self.macroMap.values())
        
        i = 0
        for (time, action) in self.actionMap.items():
            if(int(time) > int(tempTimestamp)):
                if(i == actionLen-1):
                    if(tagLen == 0):
                        source = source + action.writeToDB()
                    else:
                        source = source + action.writeToDB() + ""","""
                else:
                    source = source + action.writeToDB() + ""","""
            i = i + 1
        i = 0
        
        for (name, time) in self.tagMap.items():
            if(self.hasTagDBHelper(str(time), tagElements) == 0):
                if(i == tagLen-1):
                    if(macroLen == 0):
                        source = source + """<tag name=\"""" + str(name) + """\" time=\"""" + str(time) + """\" />"""
                    else:
                        source = source + """<tag name=\"""" + str(name) + """\" time=\"""" + str(time) + """\" />,"""
                else:
                    source = source + """<tag name=\"""" + str(name) + """\" time=\"""" + str(time) + """\" />,"""
            i = i + 1
        i = 0
        for (name, macro) in self.macroMap.items():
            if(self.hasMacroDBHelper(str(name), macroElements) == 0):
                if(i == macroLen-1):
                    source = source + macro.writeToDB()
                else:
                    source = source + macro.writeToDB() + ""","""
            i = i + 1

        source = source + """)"""
        #source.rstrip(""" ,""")
        #print source

        # Check if file already exists
	#Insert actions
        #update = UpdateFunctions(server, username, passwd)
        if(source != """()"""):
            if(update.docExists(filepath) == False):
                update.createNewDoc(filepath)
            update.addActions(source, "/db/" + filepath)
		
		
    def hasTagDBHelper(self, time, tagElements):
        
        #tagElementsLen = len(tagElements)
        #i = 0
        for tag in tagElements:
            #print type(tag.getAttribute("time"))
            if(tag.getAttribute("time") == time):
                return 1
	return 0
    
    def hasMacroDBHelper(self, name, macroElements):
	
	for macro in macroElements:
            #print type(tag.getAttribute("time"))
            if(macro.getAttribute("name") == name):
	        return 1
	return 0
    
    def actionChain(self, t, start=0):
        """  Returns the action chain necessary to recreate a vistrail from a certain time
        
        Parameters
        ----------
        
        - t : 'int'
          time
        
        Returns
        -------

        - 'list' of 'VisAction'
        
        """
        result = []
        action = copy.copy(self.actionMap[t])
        
        while 1:
            result.append(action)
            if action.timestep == start:
                break
            if action.parent == start:
                if start != 0:
                    action = copy.copy(self.actionMap[action.parent])
                break
            action = copy.copy(self.actionMap[action.parent])
        result.reverse()
        return result
    
    def hasVersion(self, version):
        """ Returns True if version with given timestamp exists

        Parameters
        ----------

        - version : 'int'
          the version timestamp

        Returns
        -------

        - 'Boolean'
        
        """
        return self.actionMap.has_key(version)
    
    def addVersion(self, action):
        """ Adds new version to vistrail

        Parameters
        ----------

        - action : 'VisAction'
          the new action
          
        """
        self.actionMap[action.timestep] = action
        self.changed = True
        action.vistrail = self

    def hasTag(self, tag):
        """ Returns True if a tag with given name or number exists
        Parameters
        ----------

        - tag : 'str' or 'int'

        Returns
        -------

        - 'boolean'

        """
        if type(tag) == type(0):
            return self.inverseTagMap.has_key(tag)
        elif type(tag) == type('str'):
            return self.tagMap.has_key(tag)
        
    def addTag(self, version_name, version_number):
        """ Adds new tag to vistrail

        Parameters
        ----------

        - version_name : 'str'
          the version name

        - version_number : 'int'
          the version timestamp
          
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
        """ Changes a tag in the vistrail
        
        Parameters
        ----------
        
        - version_name : 'str'
          the new version name

        - version_number : 'int'
          the version timestamp
          
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
        self.inverseTagMap[version_number] = version_name
        self.tagMap[version_name] = version_number
        self.changed = True

    def changenotes(self, notes, version_number):
        """ Changes a tag in the vistrail
        
        Parameters
        ----------
        
        - notes : 'str'
          the new version notes

        - version_number : 'int'
          the version timestamp
          
        """
    
        if self.actionMap.has_key(version_number):
            self.actionMap[version_number].notes = notes
        self.changed = True
        
    def getVersionGraph(self):
        """ Returns the version graph

        Returns
        -------

        - 'Graph'
        
        """
        result = Graph()
        result.addVertex(0)
        for action in self.actionMap.values():
            result.addEdge(action.parent,
                           action.timestep,
                           0)
        return result

    def getTerseGraph(self):
        """ Returns the version graph

        Returns
        -------

        - 'Graph'
        
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
        """ uses the data in self.expand to expand a localized part of the graph
        self.expand has tuples to be expanded. (list of tuples)

        Returns
        -------

        - 'Graph'

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
                if (bottom,-1) in result.edgesFrom(top) and (top,-1) in result.edgesTo(bottom):
                    result.deleteEdge(top,bottom,-1)
            while bottom>top:
                p=fullgraph.parent(bottom)
                result.addVertex(p)
                result.addEdge(p,bottom,0) #0 means not annotated
                bottom=p
         #on a refined expansion, this is necessary
        if (lowest,-1) in result.edgesFrom(highest) and (highest,-1) in result.edgesTo(lowest):
            result.deleteEdge(highest,lowest,-1)
            
        #self.currentGraph=result.__copy__()
        self.expand=[]
        return result

    def getCurrentGraph(self):
        """returns the current version graph. if there is not one, returns the
        terse graph instead"""
        if not self.currentGraph:
            self.currentGraph=self.getTerseGraph().__copy__()
        return self.currentGraph

    def setCurrentGraph(self, newGraph):
        self.currentGraph=newGraph.__copy__()

    def invalidateCurrentTime(self):
        """ Recomputes the next unused timestep from scratch  """
        self.latestTime = 1
        for time in self.actionMap.keys():
            if time >= self.latestTime:
                self.latestTime = time + 1
                
    def getFreshTimestep(self):
        """ Returns an unused timestep

        Returns
        -------

        - 'int'
        
        """
        v = 1
        for time in self.actionMap.keys():
            v = max(v, time)
        return v+1

    def getDate(self):
	""" Returns the date and time

	Returns
	-------
	
	- 'str'
	"""
	return time.strftime("%d %b %Y %H:%M:%S", time.localtime())
    
    def getUser(self):
	""" Returns the username
	
	Returns
	-------
	
	- 'str'
	"""
	return getpass.getuser()

    def serialize(self, filename):
        """ Writes collection to disk under given filename

        Parameters
        ----------

        - filename : 'str'
          
        """
	import xml_parser
	version = xml_parser.XMLParser().currentVersion
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
        """ Applies a macro to a given pipeline

        Parameters
        ----------

        - name : 'str'

        - pipeline : 'VisPipeline'
        
        """
        self.macroMap[name].applyMacro(pipeline)

    def addMacro(self, macro):
        """ Adds a macro to macroMap.
        Parameters
        ----------

        - macro : 'VisMacro'

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
        """ Deletes a macro with a given id """
        macro = self.macroIdMap[id]
        del self.macroIdMap[id]
        del self.macroMap[macro.name]
        
    def changeMacroName(self,oldname):
        """ The macro has changed its name. This updates the key (name) of the
        macro in the macroMap.

        Parameters
        ----------
        - oldname : 'str'
          previous key
          
        """
        macro = self.macroMap[oldname]
        if self.macroMap.has_key(macro.name):
            raise MacroExists(macro.name)
        else:
            self.macroMap.pop(oldname)
            self.macroMap[macro.name] = macro

    def freshMacroId(self):
        """ Returns an unused macro ID

        Returns
        -------

        - 'int'

        """
        # This is dumb and slow
        m = 0
        while self.macroIdMap.has_key(m):
            m += 1
        return m

    def setExp(self, exp):
        self.expand=exp

    # Dispatch in runtime according to type
    getPipelineDispatcher = {}
    getPipelineDispatcher[type(0)] = getPipelineVersionNumber
    getPipelineDispatcher[type('0')] = getPipelineVersionName


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
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('test_files/lung.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        #testing nodes in different branches
        v1 = 532
        v2 = 661
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)
        print "Common version in different branches", p1
        
        #testing nodes in the same branch
        v1 = 1342
        v2 = 794
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)
        print "Common version in the same branch", p1

        if p1 == 0 or p2 == 0:
            self.fail("vistrails tree is not single rooted.")

    def test2(self):
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('tests/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        #testing diff
        v1 = 17
        v2 = 27
        v3 = 22
        v.getPipelineDiff(v1,v2)
        v.getPipelineDiff(v1,v3)

if __name__ == '__main__':
    unittest.main()
