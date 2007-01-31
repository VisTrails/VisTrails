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

""" File for Interacting with Bookmarks, a more user-friendly way of 
using Vistrails

QBookmarksWindow
BookmarksManager
PipelineSceneInterface

"""

import os.path
from PyQt4 import QtCore, QtGui
from gui.bookmark_panel import QBookmarkPanel
from gui.bookmark_alias import QBookmarkAliasPanel
from gui.bookmark_explore import QAliasExplorationPanel
from gui.vistrail_controller import VistrailController
from core.xml_parser import XMLParser
from core.param_explore import InterpolateDiscreteParam, ParameterExploration
from core.bookmark import Bookmark, BookmarkCollection
from core.ensemble_pipelines import EnsemblePipelines
    
################################################################################

class QBookmarksWindow(QtGui.QMainWindow):
    """
    QBookmarksWindow is a main widget containing several tool windows
    for interacting with bookmarked vistrails pipelines without having to use 
    the builder.
    It is based in QBuilderWindow visual style.
        
    """
    def __init__(self, parent=None, logger=None):
        """ __init__(parent: QWidget) -> QBookmarksWindow
        Construct a window with menus, toolbar, and floating toolwindow
        
        """
        QtGui.QMainWindow.__init__(self, parent)
        
        self.setWindowTitle('VisTrails Bookmarks')
        self.setStatusBar(QtGui.QStatusBar(self))
        self.setDockNestingEnabled(True)
        BookmarksManager.logger = logger

        self.bookmarkPanel = QBookmarkPanel(self,BookmarksManager)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.bookmarkPanel.toolWindow())

        self.bookmarkAliasPanel = QBookmarkAliasPanel(self,BookmarksManager)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.bookmarkAliasPanel.toolWindow())

        self.aliasExplorePanel = QAliasExplorationPanel(self,BookmarksManager)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.aliasExplorePanel.toolWindow())
        
        self.createActions()
        self.createMenu()
        self.createToolBar()

        self.connectSignals()
        self.setVisible(False)

    def sizeHint(self):
        """ sizeHint() -> QRect
        Return the recommended size of the bookmarks window
        
        """
        return QtCore.QSize(800, 600)

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Enter or 
            event.key() == QtCore.Qt.Key_Return) and \
            (event.modifiers() & QtCore.Qt.ControlModifier):
            if self.bookmarkPanel.isVisible():          
                self.bookmarkPanel.executeAction.trigger()

    def createActions(self):
        """ createActions() -> None
        Construct all menu/toolbar actions for bookmarks panel
        
        """
        pass
                
    def createMenu(self):
        """ createMenu() -> None
        Initialize menu bar of bookmarks window
        
        """
        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(
            self.bookmarkPanel.toolWindow().toggleViewAction())
        self.viewMenu.addAction(
            self.bookmarkAliasPanel.toolWindow().toggleViewAction())
        
    def createToolBar(self):
        """ createToolBar() -> None
        Create a default toolbar for bookmarks window
        
        """
        pass

    def closeEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the window is about to close."""
        self.hide()
        self.emit(QtCore.SIGNAL("bookmarksHidden()"))

    def showEvent(self, e):
        """showEvent(e: QShowEvent) -> None
        Event handler called immediately before the window is shown.
        Checking if the bookmarks list is sync with the Collection """
        if BookmarksManager.collection.updateGUI:
            self.bookmarkPanel.updateBookmarkPalette()
            BookmarksManager.collection.updateGUI = False

    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between various GUI components        
        
        """
        self.connect(BookmarksManager, 
                     QtCore.SIGNAL("updateAliasGUI"),
                     self.bookmarkAliasPanel.updateAliasTable)
        self.connect(BookmarksManager, 
                     QtCore.SIGNAL("updateBookmarksGUI"),
                     self.bookmarkPanel.updateBookmarkPalette)
        self.connect(self.bookmarkAliasPanel.parameters,
                     QtCore.SIGNAL("rowRemoved"),
                     self.aliasExplorePanel.dropbox.parameters.removeAlias)
        
################################################################################

class PipelineSceneInterface(object):
    """Simulates a QPipelineScene. """
    def setModuleActive(self, id):
        pass

    def setModuleComputing(self, id):
        pass
    
    def setModuleSuccess(self, id):
        pass
    
    def setModuleError(self, id, error):
        pass

class BookmarksManagerSingleton(QtCore.QObject):
    def __init__(self):
        """__init__() -> BookmarksManagerSingleton
        Creates Bookmarks manager 
        """
        QtCore.QObject.__init__(self)
        self.logger = None
        self.collection = BookmarkCollection()
        self.filename = ''
        self.pipelines = {}
        self.ensemble = None
        self.controller = VistrailController()

    def loadBookmarks(self):
        if os.path.exists(self.filename):
            self.collection.parse(self.filename)

    def __call__(self):
        """ __call__() -> BookmarksManagerSingleton
        Return self for calling method
        
        """
        return self

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
        self.emit(QtCore.SIGNAL("updateBookmarksGUI"))
        self.collection.updateGUI = False

    def removeBookmark(self, id):
        """removeBookmark(id: int) -> None 
        Remove bookmark with id from the collection 
        
        """
        self.collection.removeBookmark(id)
        self.collection.serialize(self.filename)
        
    def updateAlias(self, alias, value):
        """updateAlias(alias: str, value: str) -> None
        Change the value of an alias and propagate changes in the pipelines
        
        """
        self.ensemble.update(alias,value)
    
    def loadPipelines(self, ids):
        """loadPipelines(ids) -> None
        Given a list of bokmark ids, loads its correspondent pipelines and sets
        an ensemble 

        """
        parser = XMLParser()
        self.pipelines = {}
        for id in ids:
            bookmark = self.collection.bookmarkMap[id]
            parser.openVistrail(bookmark.filename)
            v = parser.getVistrail()
            self.pipelines[id] = v.getPipeline(bookmark.pipeline)
            parser.closeVistrail()
        self.ensemble = EnsemblePipelines(self.pipelines)
        self.ensemble.assembleAliases()
        self.emit(QtCore.SIGNAL("updateAliasGUI"), self.ensemble.aliases)

    def executeWorkflows(self, ids):
        """executeWorkflows(ids:list of Bookmark.id) -> None
        Execute the workflows bookmarked with the ids

        """
        view = PipelineSceneInterface()
        wList = []
        self.controller.logger = self.logger
        for id in ids:
            bookmark = self.collection.bookmarkMap[id]
            wList.append((bookmark.filename,
                          bookmark.pipeline,
                          self.ensemble.pipelines[id],
                          view,
                          self.logger))
            
        self.controller.executeWorkflowList(wList)

    def writeBookmarks(self):
        """writeBookmarks() -> None - Write collection to disk."""
        self.collection.serialize(self.filename)
    
    def cleanup(self):
        """cleanup() -> None
        Removes temp files generated during execution 

        """
        self.controller.cleanup()

    def parameterExploration(self, ids, specs):
        """parameterExploration(ids: list, specs: list) -> None
        Build parameter exploration in original format for each bookmark id.
        
        """
        view = PipelineSceneInterface()
        print "ids: ", ids
        for id in ids:
            newSpecs = []
            bookmark = self.collection.bookmarkMap[id]
            print "specsCount", len(specs)
            for specsPerDim in specs:
                newSpecs.append(self.mergeParameters(id, specsPerDim))
            p = ParameterExploration(newSpecs)
            pipelineList = p.explore(self.ensemble.pipelines[id])
            vistrails = ()
            for pipeline in pipelineList:
                vistrails += ((bookmark.filename,
                               bookmark.pipeline,
                               pipeline,
                               view,
                               None),)
            self.controller.executeWorkflowList(vistrails)
    
    def mergeParameters(self, id, specs):
        """mergeParameters(id: int, specs: list) -> list
        Identifies aliases in a common function and generates only one tuple
        for them 
        
        """
        aliases = {}
        for interpolator in specs:
            #build alias dictionary
             alias = interpolator[0]
             info = self.ensemble.getSource(id,alias)
             if info:
                 aliases[alias] = (info, interpolator[2],interpolator[3])
        newSpecs = [] 
        repeated = []
        for alias, data in aliases.iteritems():
            print "repeated ", repeated
            if alias not in repeated:
                mId = data[0][0]
                fId = data[0][1]
                pId = data[0][2]
                common = {}
                common[pId] = alias
                for a, d in aliases.iteritems():
                    if a != alias:
                        if mId == d[0][0] and fId == d[0][1]:
                            common[d[0][2]] = a
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
                        d = aliases[common[i]]
                        r = d[1][0]
                        newRange.append(r)
                interpolator = InterpolateDiscreteParam(m,
                                                        f.name,
                                                        newRange,
                                                        data[2])
                print newRange
                newSpecs.append(interpolator)
        return newSpecs

###############################################################################

def initBookmarks(filename):
    """initBookmarks(filename: str) -> None 
    Sets BookmarksManager's filename and tells it to load bookmarks from this
    file

    """
    BookmarksManager.filename = filename
    BookmarksManager.loadBookmarks()

def finalizeBookmarks():
    """finalizeBookmarks() -> None 
    Cleans up the controller.
    """
    
    BookmarksManager.cleanup()
    BookmarksManager.deleteLater()


#singleton technique
BookmarksManager = BookmarksManagerSingleton()
del BookmarksManagerSingleton
