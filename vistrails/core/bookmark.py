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

"""
from core.utils import VistrailsInternalError
from core.utils.uxml import named_elements, XMLWrapper

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

    def addBookmark(self, bookmark):
        """addBookmark(bookmark: Bookmark) -> None
        Adds a bookmark to the collection """
        self.bookmarks.addBookmark(bookmark)
        self.bookmarkMap[bookmark.id] = bookmark
        self.changed = True
        self.updateGUI = True

    def findBookmark(self, id, node=None):
        """findBookmark(id,node=None) -> BookmarkTree
        Finds a bookmark node with a given id starting at node.
        When node = None, it will start from the root.
        
        """
        if node == None:
            node = self.root
        if node.bookmark.id == id:
            return node
        else:
            for child in self.children:
                self.findBookmark(id,child)

    def removeBookmark(self, node):
        del self.bookmarkMap[node.bookmark.id]
        for c in node.children:
            self.removeBookmark(c)
        if node.parent:
            node.parent.children.remove(node)
        del node
        
    def clear(self):
        """ clear() -> None 
        Remove current bookmarks """
        self.bookmarks.clear()
        self.bookmarkMap = {}
        self.changed = True

    def parse(self, filename):
        """loadBookmarks(filename: str) -> None  
        Loads a collection of bookmarks from a XML file, appending it to
        self.bookmarks.
        
        """
        self.openFile(filename)
        root = self.dom.documentElement
        for element in named_elements(root, 'bookmark'):    
            self.addBookmark(Bookmark.parse(element))
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

    def getFreshId(self):
        """getFreshId() -> int - Returns an unused id. """
        i = 0
        for bmark in self.bookmarks.asList():
            i = max(i, bmark.id)
        return i+1

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

if __name__ == '__main__':
    unittest.main()
