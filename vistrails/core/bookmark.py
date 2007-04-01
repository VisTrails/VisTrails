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
""" This file contains classes related to loading and saving a set of
bookmarks in a XML file. 
It defines the following classes:
 - Bookmark
 - BookmarkCollection
 - BookmarkTree
 - BookmarkController 
"""
import os.path
import core.interpreter.default
from core.utils import VistrailsInternalError, DummyView
from core.utils.uxml import named_elements, XMLWrapper
from core.xml_parser import XMLParser
from core.ensemble_pipelines import EnsemblePipelines
from core.interpreter.default import default_interpreter
from core.param_explore import InterpolateDiscreteParam, ParameterExploration

################################################################################

class Bookmark(object):
    """Stores a Vistrail Bookmark"""
    def __init__(self, parent='', id=-1, vistrailsFile='', pipeline=0, name='', 
                 type=''):
        """__init__(vistrailsFile: str, number: int, tag: str) -> Bookmark"""
        self.id = id
        self.parent = parent
        self.filename = vistrailsFile
        self.pipeline = pipeline
        self.name = name
        self.type = type

    def serialize(self, dom, element):
        bmark = dom.createElement('bookmark')
        bmark.setAttribute('id', str(self.id))
        bmark.setAttribute('parent', str(self.parent))
        bmark.setAttribute('name', str(self.name))
        bmark.setAttribute('type', str(self.type))
        if self.type == 'item':
            bmark.setAttribute('pipeline', str(self.pipeline))
            node = dom.createElement('filename')
            filename = dom.createTextNode(str(self.filename))
            node.appendChild(filename)
            bmark.appendChild(node)
            
        element.appendChild(bmark)

    def __str__(self):
        """ __str__() -> str - Writes itself as a string """ 
        return """<<id= '%s' name='%s' type='%s' parent='%s' 
        filename='%s' pipeline='%s'>>""" %  (
            self.id,
            self.name,
            self.type,
            self.parent,
            self.filename,
            self.pipeline)

    @staticmethod
    def parse(element):
        bookmark = Bookmark()
        bookmark.id = int(element.getAttribute('id'))
        bookmark.parent = element.getAttribute('parent')
        bookmark.name = element.getAttribute('name')
        bookmark.type = element.getAttribute('type')
        if bookmark.type == "item":
            for n in element.childNodes:
                if n.localName == "filename":
                    bookmark.filename = str(n.firstChild.nodeValue).strip()
                    break
            bookmark.pipeline = int(element.getAttribute('pipeline'))
        return bookmark

    def __eq__(self, other):
        """ __eq__(other: Bookmark) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.type != other.type:
            return False
        if self.parent != other.parent:
            return False
        if self.type == 'item':
            if self.filename != other.filename:
                return False
            if self.pipeline != other.pipeline:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

class BookmarkCollection(XMLWrapper):
    """Class to store a collection of bookmarks.

    """
    def __init__(self):
        """ __init__() -> BookmarkCollection """
        root = Bookmark()
        root.id = 0
        root.name = "Bookmarks"
        root.type = "folder"
        self.bookmarks = BookmarkTree(root)
        self.bookmarkMap = {}
        self.changed = False
        self.updateGUI = True
        self.currentId = 1

    def addBookmark(self, bookmark):
        """addBookmark(bookmark: Bookmark) -> None
        Adds a bookmark to the collection """
        self.bookmarks.addBookmark(bookmark)
        if self.bookmarkMap.has_key(bookmark.id):
            raise VistrailsInternalError("Bookmark with repeated id")

        self.currentId = max(self.currentId, bookmark.id+1)
        self.bookmarkMap[bookmark.id] = bookmark
        self.changed = True
        self.updateGUI = True

    def findBookmark(self, id, node=None):
        """findBookmark(id,node=None) -> BookmarkTree
        Finds a bookmark node with a given id starting at node.
        When node = None, it will start from the root.
        
        """
        if node == None:
            node = self.bookmarks
        if node.bookmark.id == id:
            return node
        else:
            for child in node.children:
                result = self.findBookmark(id,child)
                if result:
                    return result
            else:
                return None

    def removeBookmark(self, id, node=None):
        """removeBookmark(id: int, node: BookmarkTree) -> None 
        Remove bookmark and children starting searchin from node
        
        """
        child = self.findBookmark(id, node)
        if child:
            del self.bookmarkMap[id]
            for c in child.children:
                self.removeBookmark(c.bookmark.id,c)
            if child.parent:
                child.parent.children.remove(child)
            del child
        
    def clear(self):
        """ clear() -> None 
        Remove current bookmarks """
        self.bookmarks.clear()
        self.bookmarkMap = {}
        self.changed = True
        self.currentId = 1

    def parse(self, filename):
        """loadBookmarks(filename: str) -> None  
        Loads a collection of bookmarks from a XML file, appending it to
        self.bookmarks.
        
        """
        self.openFile(filename)
        root = self.dom.documentElement
        for element in named_elements(root, 'bookmark'):    
            self.addBookmark(Bookmark.parse(element))
        self.refreshCurrentId()
        self.changed = False
        self.updateGUI = True

    def serialize(self, filename):
        """serialize(filename:str) -> None 
        Writes bookmark collection to disk under given filename.
          
        """
        dom = self.createDocument('bookmarks')
        root = dom.documentElement
        
        for bookmark in self.bookmarkMap.values():
            bookmark.serialize(dom, root)

        self.writeDocument(root, filename)
        self.changed = False

    def refreshCurrentId(self):
        """refreshCurrentId() -> None
        Recomputes the next unused id from scratch
        
        """
        self.currentId = max([0] + self.bookmarkMap.keys()) + 1

    def getFreshId(self):
        """getFreshId() -> int - Returns an unused id. """
        return self.currentId

###############################################################################

class BookmarkTree(object):
    """BookmarkTree implements an n-ary tree of bookmarks. """
    def __init__(self, bookmark):
        self.bookmark = bookmark
        self.children = []
        self.parent = None

    def addBookmark(self, bookmark):
        #assert bookmark.parent == self.bookmark.name
        result = BookmarkTree(bookmark)
        result.parent = self
        self.children.append(result)
        return result
    
    def clear(self):
        for node in self.children:
            node.clear()
        self.children = [] 
    
    def asList(self):
        """asList() -> list of bookmarks
        Returns all its nodes in a list """
        result = []
        result.append(self.bookmark)
        for node in self.children:
            result.extend(node.asList())
        return result
        
################################################################################

class BookmarkController(object):
    def __init__(self):
        """__init__() -> BookmarkController
        Creates Bookmark Controller
        
        """
        self.collection = BookmarkCollection()
        self.filename = ''
        self.pipelines = {}
        self.activePipelines = []
        self.ensemble = EnsemblePipelines()

    def loadBookmarks(self):
        """loadBookmarks() -> None
        Load Bookmark collection and instantiate all pipelines

        """

        if os.path.exists(self.filename):
            self.collection.parse(self.filename)
            self.loadAllPipelines()
    
    def addBookmark(self, parent, vistrailsFile, pipeline, name=''):
        """addBookmark(parent: int, vistrailsFile: str, pipeline: int,
                       name: str) -> None
        creates a bookmark with the given information and adds it to the 
        collection

        """
        id = self.collection.getFreshId()
        bookmark = Bookmark(parent, id, vistrailsFile,pipeline,name,"item")
        self.collection.addBookmark(bookmark)
        self.collection.serialize(self.filename)
        self.loadPipeline(id)

    def removeBookmark(self, id):
        """removeBookmark(id: int) -> None 
        Remove bookmark with id from the collection 
        
        """
        self.collection.removeBookmark(id)
        del self.pipelines[id]
        del self.ensemble.pipelines[id]
        if id in self.activePipelines:
            del self.activePipelines[id]
        if id in self.ensemble.activePipelines:
            del self.ensemble.activePipelines[id]
        self.ensemble.assembleAliases()
        self.collection.serialize(self.filename)
    
    def updateAlias(self, alias, value):
        """updateAlias(alias: str, value: str) -> None
        Change the value of an alias and propagate changes in the pipelines
        
        """
        self.ensemble.update(alias,value)
    
    def reloadPipeline(self, id):
        """reloadPipeline(id: int) -> None
        Given a bookmark id, loads its original pipeline in the ensemble 

        """
        if self.pipelines.has_key(id):
            self.ensemble.addPipeline(id, self.pipelines[id])
            self.ensemble.assembleAliases()

    def loadPipeline(self, id):
        """loadPipeline(id: int) -> None
        Given a bookmark id, loads its correspondent pipeline and include it in
        the ensemble 

        """
        parser = XMLParser()
        bookmark = self.collection.bookmarkMap[id]
        parser.openVistrail(bookmark.filename)
        v = parser.getVistrail()
        self.pipelines[id] = v.getPipeline(bookmark.pipeline)
        parser.closeVistrail()
        self.ensemble.addPipeline(id, self.pipelines[id])
        self.ensemble.assembleAliases()

    def loadAllPipelines(self):
        """loadAllPipelines() -> None
        Load all bookmarks' pipelines and sets an ensemble 

        """
        parser = XMLParser()
        self.pipelines = {}
        for id, bookmark in self.collection.bookmarkMap.iteritems():
            parser.openVistrail(bookmark.filename)
            v = parser.getVistrail()
            self.pipelines[id] = v.getPipeline(bookmark.pipeline)
            parser.closeVistrail()
        self.ensemble = EnsemblePipelines(self.pipelines)
        self.ensemble.assembleAliases()

    def setActivePipelines(self, ids):
        """ setActivePipelines(ids: list) -> None
        updates the list of active pipelines 
        
        """
        self.activePipelines = ids
        self.ensemble.activePipelines = ids
        self.ensemble.assembleAliases()

    def writeBookmarks(self):
        """writeBookmarks() -> None - Write collection to disk."""
        self.collection.serialize(self.filename)

    def executeWorkflows(self, ids):
        """executeWorkflows(ids:list of Bookmark.id) -> None
        Execute the workflows bookmarked with the ids

        """
        view = DummyView()
        wList = []
        for id in ids:
            bookmark = self.collection.bookmarkMap[id]
            wList.append((bookmark.filename,
                          bookmark.pipeline,
                          self.ensemble.pipelines[id],
                          view))
            
        self.executeWorkflowList(wList)
    
    def executeWorkflowList(self, vistrails):
        """executeWorkflowList(vistrails: [(name, version, 
                                            pipeline, view]) -> None
        Executes a list of pipelines, where:
         - name: str is the vistrails filename
         - version: int is the version number
         - pipeline: Pipeline object
         - view: interface to a QPipelineScene
        
        """
        interpreter = default_interpreter.get()
        for vis in vistrails:
            (name, version, pipeline, view) = vis
            (objs, errors, executed) = interpreter.execute(pipeline, 
                                                           name, 
                                                           version, 
                                                           view)

    def parameterExploration(self, ids, specs):
        """parameterExploration(ids: list, specs: list) -> None
        Build parameter exploration in original format for each bookmark id.
        
        """
        view = DummyView()
        for id in ids:
            newSpecs = []
            bookmark = self.collection.bookmarkMap[id]
            newSpecs = self.mergeParameters(id, specs)
            p = ParameterExploration(newSpecs)
            pipelineList = p.explore(self.ensemble.pipelines[id])
            vistrails = ()
            for pipeline in pipelineList:
                vistrails += ((bookmark.filename,
                               bookmark.pipeline,
                               pipeline,
                               view),)
            self.executeWorkflowList(vistrails)
    
    def mergeParameters(self, id, specs):
        """mergeParameters(id: int, specs: list) -> list
        Identifies aliases in a common function and generates only one tuple
        for them 
        
        """
        aliases = {}
        aList = []
        for dim in range(len(specs)):
            specsPerDim = specs[dim]
            for interpolator in specsPerDim:
                #build alias dictionary
                 alias = interpolator[0]
                 info = self.ensemble.getSource(id,alias)
                 if info:
                     if aliases.has_key(alias):
                         aliases[alias].append((info, 
                                                interpolator[2],
                                                interpolator[3],
                                                dim))
                     else:
                         aliases[alias] = [(info, 
                                            interpolator[2],
                                            interpolator[3],
                                            dim)]
                     aList.append((alias,info, 
                                   interpolator[2],
                                   interpolator[3],
                                   dim))
        newSpecs = [] 
        repeated = []
        newSpecsPerDim = {}
        for data in aList:
            alias = data[0]
            if alias not in repeated:
                mId = data[1][0]
                fId = data[1][1]
                pId = data[1][2]
                common = {}
                common[pId] = alias
                for d in aList:
                    a = d[0]
                    if a != alias:
                        if mId == d[1][0] and fId == d[1][1]:
                            #assuming that we cannot set the same parameter
                            #across the dimensions
                            common[d[1][2]] = a
                            repeated.append(a)
                pip = self.ensemble.pipelines[id]
                m = pip.getModuleById(mId)
                f = m.functions[fId]
                pCount = len(f.params)
                newRange = []
                for i in range(pCount):
                    if i not in common.keys():
                        p = f.params[i]
                        newRange.append((p.value(),p.value()))
                    else:
                        dList = aliases[common[i]]
                        r = None
                        for d in dList:
                            if d[0][2] == i:
                                r = d[1][0]
                        newRange.append(r)
                interpolator = InterpolateDiscreteParam(m,
                                                        f.name,
                                                        newRange,
                                                        data[3])
                if newSpecsPerDim.has_key(data[4]):
                    newSpecsPerDim[data[4]].append(interpolator)
                else:
                    newSpecsPerDim[data[4]] = [interpolator]
        for dim in sorted(newSpecsPerDim.keys()):
            lInter = newSpecsPerDim[dim]
            l = []
            for inter in lInter:
                l.append(inter)
            newSpecs.append(l)
        return newSpecs


###############################################################################

import unittest
import core.system
import os
class TestBookmarkCollection(unittest.TestCase):
    def test1(self):
        """ Exercising writing and reading a file """
        collection = BookmarkCollection()
        bookmark = Bookmark()
        bookmark.id = 1
        bookmark.parent = ''
        bookmark.name = 'contour 4'
        bookmark.type = 'item'
        bookmark.filename = 'brain_vistrail.xml'
        bookmark.pipeline = 126
        
        collection.addBookmark(bookmark)

        #writing
        collection.serialize('bookmarks.xml')

        #reading it again
        collection.clear()
        collection.parse('bookmarks.xml')
        newbookmark = collection.bookmarks.asList()[1]
        assert bookmark == newbookmark
    
        #remove created file
        os. unlink('bookmarks.xml')

    def test_empty_bookmark(self):
        """ Exercises doing things on an empty bookmark. """
        collection = BookmarkCollection()
        collection.parse(core.system.visTrailsRootDirectory() +
                         'tests/resources/empty_bookmarks.xml')

if __name__ == '__main__':
    unittest.main()
