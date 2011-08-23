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
pipeline

QPipelineTab
"""

from PyQt4 import QtCore, QtGui
from core.vistrail.module import Module
from core.vistrail.connection import Connection
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.method_palette import QMethodPalette
from gui.module_configuration import QModuleConfiguration
from gui.module_methods import QModuleMethods
from gui.pipeline_view import QPipelineView
from gui.vistrail_variables import QVistrailVariables
from weakref import proxy

################################################################################

class QPipelineTab(QDockContainer, QToolWindowInterface):
    """
    QPipelineTab is a tab widget setting QPipelineView in a center
    while having surrounding tool windows for manipulating a pipeline
    
    """
    def __init__(self, parent=None):
        """ QPipelineTab(parent: QWidget) -> QPipelineTab        
        Make it a main window with dockable area and a QPipelineView
        in the middle
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Pipeline')
        self.pipelineView = QPipelineView()
        self.pipelineView.scene().pipeline_tab = proxy(self)
        self.setCentralWidget(self.pipelineView)
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()        
        
        self.methodPalette = QMethodPalette(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.methodPalette.toolWindow())
        
        self.moduleMethods = QModuleMethods(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.moduleMethods.toolWindow())
        
        self.moduleConfig = QModuleConfiguration(self, self.pipelineView.scene())
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, 
                           self.moduleConfig.toolWindow())
        
        self.vistrailVars = QVistrailVariables(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.vistrailVars.toolWindow())
        
        self.connect(self.toolWindow(),
                     QtCore.SIGNAL('topLevelChanged(bool)'),
                     self.updateWindowTitle)
        self.connect(self.pipelineView.scene(),
                     QtCore.SIGNAL('moduleSelected'),
                     self.moduleSelected)
        self.connect(self.moduleConfig,
                     QtCore.SIGNAL('doneConfigure'),
                     self.pipelineView.scene().perform_configure_done_actions)
        self.connect(self.pipelineView.scene(),
                     QtCore.SIGNAL('showConfigureWindow'),
                     self.moduleConfig.activate)
        self.connect(self.pipelineView,
                     QtCore.SIGNAL('resetQuery()'),
                     self.resetQuery)

        self.controller = None

    def addViewActionsToMenu(self, menu):
        """addViewActionsToMenu(menu: QMenu) -> None
        Add toggle view actions to menu
        
        """
        menu.addAction(self.methodPalette.toolWindow().toggleViewAction())
        menu.addAction(self.moduleMethods.toolWindow().toggleViewAction())
        menu.addAction(self.moduleConfig.toolWindow().toggleViewAction())
        menu.addAction(self.vistrailVars.toolWindow().toggleViewAction())

    def removeViewActionsFromMenu(self, menu):
        """removeViewActionsFromMenu(menu: QMenu) -> None
        Remove toggle view actions from menu
        
        """
        menu.removeAction(self.methodPalette.toolWindow().toggleViewAction())
        menu.removeAction(self.moduleMethods.toolWindow().toggleViewAction())
        menu.removeAction(self.moduleConfig.toolWindow().toggleViewAction())
        menu.removeAction(self.vistrailVars.toolWindow().toggleViewAction())

    def updatePipeline(self, pipeline):
        """ updatePipeline(pipeline: Pipeline) -> None        
        Setup the pipeline to display and control a specific pipeline
        
        """
        self.pipelineView.scene().setupScene(pipeline)

    def updateWindowTitle(self, topLevel):
        """ updateWindowTitle(topLevel: bool) -> None
        Change the current widget title depends on the top level status
        
        """
        if topLevel:
            self.setWindowTitle('Pipeline <' +
                                self.toolWindow().parent().windowTitle()+'>')
        else:
            self.setWindowTitle('Pipeline')

    def moduleSelected(self, moduleId, selection = []):
        """ moduleChanged(moduleId: int, selection: [QGraphicsModuleItem])
                          -> None
        Set up the view when module selection has been changed
        
        """
        if self.pipelineView.scene().controller:
            pipeline = self.pipelineView.scene().controller.current_pipeline
        else:
            pipeline = None
        if pipeline and pipeline.modules.has_key(moduleId):
            module = pipeline.modules[moduleId]
            self.methodPalette.setEnabled(True)
            self.moduleMethods.setEnabled(True)
            self.moduleConfig.setEnabled(True)
        else:
            module = None
            self.methodPalette.setEnabled(False)
            self.moduleMethods.setEnabled(False)
            self.moduleConfig.setEnabled(False)
        self.methodPalette.setUpdatesEnabled(False)
        self.moduleMethods.setUpdatesEnabled(False)
        self.moduleConfig.setUpdatesEnabled(False)
        try:
            self.methodPalette.updateModule(module)
            self.moduleMethods.updateModule(module)
            self.moduleConfig.updateModule(module)
            self.emit(QtCore.SIGNAL('moduleSelectionChange'),
                      [m.id for m in selection])
        finally:
            self.methodPalette.setUpdatesEnabled(True)
            self.moduleMethods.setUpdatesEnabled(True)
            self.moduleConfig.setUpdatesEnabled(True) 

    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a vistrail controller to this pipeline view
        
        """
        oldController = self.pipelineView.scene().controller
        if oldController!=controller:
            if oldController!=None:
                self.disconnect(oldController,
                                QtCore.SIGNAL('versionWasChanged'),
                                self.versionChanged)
                oldController.current_pipeline_view = None
            self.controller = controller
            self.pipelineView.scene().controller = controller
            self.connect(controller,
                         QtCore.SIGNAL('versionWasChanged'),
                         self.versionChanged)
            self.methodPalette.controller = controller
            self.moduleMethods.controller = controller
            self.moduleConfig.controller = controller
            self.vistrailVars.updateController(controller)
            controller.current_pipeline_view = self.pipelineView.scene()

    def versionChanged(self, newVersion):
        """ versionChanged(newVersion: int) -> None        
        Update the pipeline when the new vistrail selected in the
        controller
        
        """
        self.updatePipeline(self.controller.current_pipeline)
            
    def resetQuery(self):
        """ resetQuery() -> None
        pass along the signal

        """
        self.emit(QtCore.SIGNAL('resetQuery()'))

    def checkModuleConfigPanel(self):
        """ checkModuleConfigPanel(self) -> None 
        This will ask if user wants to save changes """
        if self.moduleConfig.hasChanges:
            self.moduleConfig.confWidget.widget.askToSaveChanges()