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
""" The file describes the pipeline tab widget to manage a single
vistrail version tree"""

from PyQt4 import QtCore, QtGui
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.version_prop import QVersionProp
from gui.version_search import QVersionSearch
from gui.version_view import QVersionTreeView
from gui.bookmark_window import BookmarksManager

################################################################################
        
class QVersionTab(QDockContainer, QToolWindowInterface):
    """
    QVersionTab is a tab widget setting QVersionTreeView in a
    center while having surrounding tool windows
    
    """
    def __init__(self, parent=None):
        """ QVersionTab(parent: QWidget) -> QVersionTab        
        Make it a main window with dockable area and a
        QVersionTreeView in the middle
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Version Tree')
        self.versionView = QVersionTreeView()
        self.setCentralWidget(self.versionView)
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()

        self.versionSearch = QVersionSearch(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.versionSearch.toolWindow())        
        self.versionProp = QVersionProp(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.versionProp.toolWindow())        
        
        self.controller = None
        self.connect(self.toolWindow(),
                     QtCore.SIGNAL('topLevelChanged(bool)'),
                     self.updateWindowTitle)
        self.connect(self.versionView.scene(),
                     QtCore.SIGNAL('versionSelected(int,bool)'),
                     self.versionSelected)
        self.connect(self.versionView.scene(),
                     QtCore.SIGNAL('twoVersionsSelected(int,int)'),
                     self.twoVersionsSelected)
        self.connect(self.versionView.scene(),
                     QtCore.SIGNAL('addToBookmarks'),
                     self.add_bookmark)
    def addViewActionsToMenu(self, menu):
        """addViewActionsToMenu(menu: QMenu) -> None
        Add toggle view actions to menu
        
        """
        menu.addAction(self.versionSearch.toolWindow().toggleViewAction())
        menu.addAction(self.versionProp.toolWindow().toggleViewAction())

    def removeViewActionsFromMenu(self, menu):
        """removeViewActionsFromMenu(menu: QMenu) -> None
        Remove toggle view actions from menu
        
        """
        menu.removeAction(self.versionSearch.toolWindow().toggleViewAction())
        menu.removeAction(self.versionProp.toolWindow().toggleViewAction())
        
    def updateWindowTitle(self, topLevel):
        """ updateWindowTitle(topLevel: bool) -> None
        Change the current widget title depends on the top level status
        
        """
        if topLevel:
            self.setWindowTitle('Version Tree <' +
                                self.toolWindow().parent().windowTitle()+'>')
        else:
            self.setWindowTitle('Pipeline')

    def versionSelected(self, versionId, byClick):
        """ versionSelected(versionId: int, byClick: bool) -> None
        A version has been selected/unselected, update the controller
        and the pipeline view
        
        """
        if self.controller:
            self.controller.resetPipelineView = byClick
            self.controller.changeSelectedVersion(versionId)
            self.versionProp.updateVersion(versionId)
            self.emit(QtCore.SIGNAL('versionSelectionChange'),versionId)
            
    def twoVersionsSelected(self, id1, id2):
        """ twoVersionsSelected(id1: Int, id2: Int) -> None
        Two versions are selected in the version tree, emit a signal
        
        """
        self.emit(QtCore.SIGNAL('twoVersionsSelected(int,int)'), id1, id2)

    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a vistrail controller to this version tree view
        
        """
        oldController = self.versionView.scene().controller
        if oldController!=controller:
            if oldController!=None:
                self.disconnect(oldController,
                                QtCore.SIGNAL('vistrailChanged()'),
                                self.vistrailChanged)
            self.controller = controller
            self.versionView.scene().controller = controller
            self.connect(controller,
                         QtCore.SIGNAL('vistrailChanged()'),
                         self.vistrailChanged)
            if controller:
                self.vistrailChanged()
                self.versionProp.updateController(controller)
                self.versionSearch.updateController(controller)

    def vistrailChanged(self):
        """ vistrailChanged() -> None        
        An action was performed on the current vistrail
        
        """
        self.versionView.scene().setupScene(self.controller)
        if self.controller and self.controller.resetVersionView:
            self.versionView.scene().fitToAllViews()
        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def add_bookmark(self, id, name):
        """add_bookmark(id: int, label:name) -> None
        Gather all information concerning the new bookmark and send it to 
        BookmarksManager

        """
        vistrailsFile = self.controller.fileName
        BookmarksManager.add_bookmark('',vistrailsFile,id,name)
