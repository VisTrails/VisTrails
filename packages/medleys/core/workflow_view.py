############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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
workflow views.
It defines the following
classes:
 - WorkflowView
 - WorkflowViewCollection
 - WorkflowViewTree
 - WorkflowViewCollectionController
"""
import os.path
from xml_node import XMLNode
from core.ensemble_pipelines import EnsemblePipelines
from core.interpreter.default import get_default_interpreter
from core.param_explore import InterpolateDiscreteParam, ParameterExploration
from core.utils import VistrailsInternalError, DummyView, enum
from core.db.locator import FileLocator, DBLocator

################################################################################
#Exceptions
#class MedleyError(Exception):
#    """MedleyError is raised when there's something wrong with a medley or a
#       workflow view. For example, a file not found, or an inexistent connection
#       to db """
#    dispatchError = {0 : 'No location information for this bookmark',
#                     1 : 'Vistrails file %s not found',
#                     2 : 'Version %s not found in %s',
#                     3 : 'Vistrails %s not found on DB',
#                     4 : 'DB Connection is invalid' }
#    def __init__(self, error_code, info=None):
#        self.code = error_code
#        self.info = info
#
#    def __str__(self):
#        if self.info:
#            return BookmarkError.dispatchError[self.code] % self.info
#        else:
#            return BookmarkError.dispatchError[self.code]

################################################################################
class WorkflowView(XMLNode):
    """Stores a Vistrail Bookmark"""
    def __init__(self, parent=None, id=None, locator=None, pipeline=None, name=None,
                 type=None, alias_map=None):
        """__init__(parent: int, id: int, locator: Locator,
                    pipeline: long, name: str, type: str, alias_map: dict)
                                            -> WorkflowView
        It creates a workflow view."""
        self._id = id
        self._parent = parent
        self._locator = locator
        self._pid = pipeline
        self._name = name
        self._type = type
        self._alias_map = alias_map

    def to_xml(self, node=None):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
        Convert this object to an XML representation.
        """

        if node is None:
            node = ElementTree.Element('workflowview')

        node.set('id', self.convert_to_str(self._id, 'long'))
        node.set('parent', self.convert_to_str(self._parent, 'long'))
        node.set('name', self.convert_to_str(self._name, 'str'))
        node.set('type', self.convert_to_str(self._type, 'str'))
        
        # self._type can also be a folder, so we only store the locator and
        # pipeline if it is a workflow view
        if self._type == 'item':
            node.set('pipeline_id', self.convert_to_str(self._pid, 'long'))
            childnode = ElementTree.SubElement(node,'locator')
            self._locator.to_xml(childnode)
            for (k,v) in self._alias_map.iteritems():
                child_ = ElementTree.SubElement(node, 'alias')
                child_.set('name', self.convert_to_str(k, 'str'))
                childcomp = ElementTree.SubElement(child_,'component')
                v.to_xml(childcomp)

        return node

    @staticmethod
    def from_xml(node):
        """ from_xml(node: ElementTree.Element) -> WorkflowView
        Parse an XML object representing a WorkflowView and returns a WorkflowView
        object.
        It checks if the vistrails file/connection exists.

        """
        if node.tag != 'workflowview':
            return None

        wfv = WorkflowView()
        #read Attributes
        data = node.get('id', None)
        wfv._id = WorkflowView.convert_from_str(data, 'long')
        data = node.get('parent', None)
        wfv._parent = WorkflowView.convert_from_str(data, 'long')
        data = node.get('name', None)
        wfv._name = WorkflowView.convert_from_str(data, 'str')
        data = node.get('type', None)
        wfv._type = WorkflowView.convert_from_str(data, 'str')
        
        if wfv._type == "item":
            data = node.get('pipeline_id', None)
            wfv._pid = WorkflowView.convert_from_str(data, 'long')
            wfv._alias_map = {}
            #read locator
            for child in node.getchildren():
                if child.tag == "locator":
                    data_ = child.get('type', None)
                    loc_type = WorkflowView.convert_from_str(data_, 'str')
                    if loc_type == 'file':
                        wfv._locator = FileLocator.from_xml(child)
                    elif loc_type == 'db':
                        wfv._locator = DBLocator.from_xml(child)
                elif child.tag == "alias":
                    data = child.get('name', None)
                    name = WorkflowView.convert_from_str(data,'str')
                    component = None
                    for child_ in child.getchildren():
                        if child_.tag == "component":
                            component = Component.from_xml(child_)
                    wfv._alias_map[name] = component
        return wfv

    #def get_locator_error(self):
    #    """get_locator_error -> BookmarkError
    #    Inspects locator and returns an error object if it is the case.
    #
    #    """
    #    if self.locator:
    #        if self.locator.is_valid():
    #            return None
    #        else:
    #            if isinstance(self.locator, FileLocator()):
    #                filename = self.locator.name
    #                return BookmarkError(1,self.locator.name)
    #            elif isinstance(self.locator, DBLocator):
    #                if not self.locator.update_db_connection_from_gui():
    #                    return BookmarkError(error_code=4)
    #                else:
    #                    return None
    #    else:
    #        return BookmarkError(error_code=0)

    #
    # operators
    #
    
    def __eq__(self, other):
        """ __eq__(other: Bookmark) -> boolean
        Returns True if self and other have the same attributes. Used by ==
        operator.

        """
        if self._id != other._id:
            return False
        if self._name != other._name:
            return False
        if self._type != other._type:
            return False
        if self._parent != other._parent:
            return False
        if self._type == 'item':
            if self._locator != other._locator:
                return False
            if self._pid != other._pid:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        """ __str__() -> str - Writes itself as a string """
        return """<workflowview id= '%s' name='%s' type='%s' parent='%s'
pipeline='%s' locator=%s>""" %  (
            self._id,
            self._name,
            self._type,
            self._parent,
            self._pid,
            self._locator)

class WorkflowViewCollection(XMLNode):
    """Class to store a collection of workflow views.

    """
    def __init__(self):
        """ __init__() -> WorkflowViewCollection """
        root = WorkflowView(id=0, name="Workflow Views", type="folder")
        self._wfviews = WorkflowViewTree(root)
        self._wfview_map = {}
        self._changed = False
        self._updateGUI = True
        self._current_id = 1

    def add_workflow_view(self, wfview):
        """add_workflow_view(wfview: WorkflowView) -> None
        Adds a workflow view to the collection """

        if self._wfview_map.has_key(wfview._id):
            msg = "Workflow view with repeated id: %s"% wfview._id
            raise VistrailsInternalError(msg)
        
        self._wfviews.add_workflow_view(wfview)
        self._current_id = max(self._current_id, wfview._id+1)
        self._wfview_map[wfview._id] = wfview
        self._changed = True
        self._updateGUI = True

    def find_workflow_view(self, id, node=None):
        """find_workflow_view(id, node=None) -> WorkflowViewTree
        Finds a workflow view node with a given id starting at node.
        When node = None, it will start from the root.

        """
        if node == None:
            node = self._wfviews
        if node.wfview._id == id:
            return node
        else:
            for child in node.children:
                result = self.find_workflow_view(id, child)
                if result:
                    return result
            else:
                return None

    def remove_workflow_view(self, id, node=None):
        """remove_workflow_view(id: int, node: WorkflowViewTree) -> None
        Remove workflow view and all its children starting searching from node

        """
        child = self.find_workflow_view(id, node)
        if child:
            del self._wfview_map[id]
            for c in child.children:
                self.remove_workflow_view(c._wfview._id,c)
            if child.parent:
                child.parent.children.remove(child)
            del child

    def clear(self):
        """ clear() -> None
        Remove current workflow views """
        self._wfviews.clear()
        self._wfview_map = {}
        self._changed = True
        self._current_id = 1

    def from_xml(self, node):
        """from_xml(filename: str) -> None
        Loads a collection of workflow views from XML, appending it to
        self._wfviews.

        """
        if node.tag == "workflowviews":
            for child in node.getchildren():
                if child.tag == "workflowview":
                    self.add_workflow_view(WorkflowView.from_xml(child))
        self.refresh_current_id()
        self._changed = False
        self._updateGUI = True

    def to_xml(self, node=None):
        """serialize(filename:str) -> None
        Writes bookmark collection to disk under given filename.

        """
        if node is None:
            node = ElementTree.Element('workflowviews')
        
        for wfv in self.wfview_map.itervalues():
            child = ElementTree.SubElement(node, 'workflowview')
            wfv.to_xml(child)

        self._changed = False

    def refresh_current_id(self):
        """refresh_current_id() -> None
        Recomputes the next unused id from scratch

        """
        self._current_id = max([0] + self._wfview_map.keys()) + 1

    def get_fresh_id(self):
        """get_fresh_id() -> int - Returns an unused id. """
        return self._current_id

###############################################################################

class WorkflowViewTree(object):
    """WorkflowViewTree implements an n-ary tree of workflow views. """
    def __init__(self, wfview):
        self._wfview = wfview
        self.children = []
        self.parent = None

    def add_bookmark(self, bookmark):
        #assert bookmark.parent == self.bookmark.name
        result = BookmarkTree(bookmark)
        result.parent = self
        self.children.append(result)
        return result

    def clear(self):
        for node in self.children:
            node.clear()
        self.children = []

    def as_list(self):
        """as_list() -> list of WorkflowView
        Returns all its nodes in a list """
        result = []
        result.append(self._wfview)
        for node in self.children:
            result.extend(node.as_list())
        return result

################################################################################

class WorkflowViewCollectionController(object):
    def __init__(self):
        """__init__() -> WorkflowViewCollectionController
        Creates WorkflowCollectionController
        """
        self.collection = BookmarkCollection()
        self.filename = ''
        self.pipelines = {}
        self.controllers = {}
        self.active_pipelines = []
        self.ensemble = EnsemblePipelines()
        self.loaded = False

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
        bookmark.locator = FileLocator('brain_vistrail.xml')
        bookmark.pipeline = 126

        collection.add_bookmark(bookmark)

        #writing
        collection.serialize('bookmarks.xml')

        #reading it again
        collection.clear()
        collection.parse('bookmarks.xml')
        newbookmark = collection.bookmarks.as_list()[1]
        assert bookmark == newbookmark

        #remove created file
        os.unlink('bookmarks.xml')

    def test_empty_bookmark(self):
        """ Exercises doing things on an empty bookmark. """
        collection = BookmarkCollection()
        collection.parse(core.system.vistrails_root_directory() +
                         'tests/resources/empty_bookmarks.xml')

if __name__ == '__main__':
    unittest.main()
