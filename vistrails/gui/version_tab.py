###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" The file describes the pipeline tab widget to manage a single
vistrail version tree"""

from PyQt4 import QtCore, QtGui
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.version_prop import QVersionProp
from gui.version_view import QVersionTreeView

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

        self.versionProp = QVersionProp(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.versionProp.toolWindow())        
        
        self.controller = None
        self.connect(self.toolWindow(),
                     QtCore.SIGNAL('topLevelChanged(bool)'),
                     self.updateWindowTitle)
        self.connect(self.versionView.scene(),
                     QtCore.SIGNAL('twoVersionsSelected(int,int)'),
                     self.twoVersionsSelected)
        self.connect(self.versionView,
                     QtCore.SIGNAL('resetQuery()'),
                     self.resetQuery)

    def updateWindowTitle(self, topLevel):
        """ updateWindowTitle(topLevel: bool) -> None
        Change the current widget title depends on the top level status
        
        """
        if topLevel:
            self.setWindowTitle('Version Tree <' +
                                self.toolWindow().parent().windowTitle()+'>')
        else:
            self.setWindowTitle('Version Tree')

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
                self.disconnect(oldController,
                                QtCore.SIGNAL('invalidateSingleNodeInVersionTree'),
                                self.single_node_changed)
                self.disconnect(oldController,
                                QtCore.SIGNAL('notesChanged()'),
                                self.notesChanged)
            self.controller = controller
            self.versionView.scene().controller = controller
            self.connect(controller,
                         QtCore.SIGNAL('vistrailChanged()'),
                         self.vistrailChanged)
            self.connect(controller,
                         QtCore.SIGNAL('invalidateSingleNodeInVersionTree'),
                         self.single_node_changed)
            self.connect(controller,
                         QtCore.SIGNAL("notesChanged()"),
                         self.notesChanged)
            if controller:
                self.vistrailChanged()
                self.versionProp.updateController(controller)
                self.versionView.versionProp.updateController(controller)

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        An action was performed on the current vistrail
        
        """
        self.versionView.scene().setupScene(self.controller)
        if self.controller and self.controller.reset_version_view:
            self.versionView.scene().fitToAllViews()
        if self.controller:
            self.versionProp.updateVersion(self.controller.current_version)
            self.versionView.versionProp.updateVersion(self.controller.current_version)
        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def single_node_changed(self, old_version, new_version):
        """ single_node_changed(old_version, new_version)
        Handle single node change on version tree by not recomputing
        entire scene.

        """
        self.versionView.scene().update_scene_single_node_change(self.controller,
                                                                 old_version,
                                                                 new_version)
        if self.controller and self.controller.reset_version_view:
            self.versionView.scene().fitToAllViews()
        if self.controller:
            self.versionProp.updateVersion(self.controller.current_version)
            self.versionView.versionProp.updateVersion(self.controller.current_version)
        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def notesChanged(self):
        """ notesChanged() -> None
        The notes for the current vistrail version changed

        """
        if self.controller:
            self.versionView.versionProp.updateVersion(self.controller.current_version)

    def resetQuery(self):
        """ resetQuery() -> None
        pass along the signal

        """
        self.emit(QtCore.SIGNAL('resetQuery()'))
        self.versionProp.resetSearch(emit_signal=False)
        
