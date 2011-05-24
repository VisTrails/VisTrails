############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from gui.pipeline_view import QPipelineView
from gui.base_view import BaseView
from gui.mashups.mashup_app import QMashupAppMainWindow
from gui.mashups.mashups_manager import MashupsManager
from gui.mashups.alias_list import QAliasListPanel

class QMashupView(QtGui.QMainWindow, BaseView):
    #signals
    #mashupChanged = pyqtSignal()
    
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
        BaseView.__init__(self)
        self.set_title("Mashup")
        
        self.controller = None
        self.mshpController = None
        self.createActions()
        #Setting up a toolbar
        self.createToolBar()
        
        widget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.tabBar = QtGui.QTabBar(self)
        self.tabBar.setDocumentMode(True)
        self.tabBar.setTabsClosable(False)
        self.tabBar.setExpanding(False)
        self.tabBar.currentChanged.connect(self.switchTab)
        self.stack = QtGui.QStackedWidget(self)
        layout.addWidget(self.tabBar)
        layout.addWidget(self.stack)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.createAliasPanelTab()
        #self.createPipelineTab()
        self.previewTab = None
        self.setWindowTitle("Mashup Builder")
        self.vtversion = -1
        self.manager = MashupsManager.getInstance()
        
    def set_default_layout(self):
        from gui.mashups.mashups_inspector import QMashupsInspector
        from gui.mashups.alias_parameter_view import QAliasParameterView
        self.layout = \
            {QtCore.Qt.LeftDockWidgetArea: QMashupsInspector,
             QtCore.Qt.RightDockWidgetArea: QAliasParameterView,
             }
            
    def set_action_links(self):
        self.action_links = \
            {
            }
        
    def set_controller(self, controller):
        """set_controller(controller:VistrailController) -> None
         This will set vistrail controller"""
        if controller == self.controller:
            return
        if self.controller is not None:
            self.disconnect(self.controller,
                             QtCore.SIGNAL('versionWasChanged'),
                             self.versionChanged)
        self.controller = controller
        if self.controller:
            self.connect(self.controller,
                         QtCore.SIGNAL('versionWasChanged'),
                         self.versionChanged)
        print "      *** mashup view set vtController: ", controller
        
    def versionChanged(self):
        self.vtversion = self.controller.current_version
        print "      *** mashup view versionChanged ", self.vtversion
        
    def updateView(self):
        from gui.vistrails_window import _app
        if self.mshpController is not None:
            self.mshpController.versionChanged.disconnect(self.mshpVersionChanged)
            if self.mshpController.vtController is not None:
                self.disconnect(self.mshpController.vtController,
                             QtCore.SIGNAL('vistrailChanged()'),
                             self.mshpControllerVistrailChanged)
        self.mshpController = self.manager.createMashupController(self.controller,
                                                                 self.vtversion)
        #self.pipelineTab.set_controller(self.mshpController.vtController)
        #self.pipelineTab.set_to_current()
        self.mshpController.vtController.change_selected_version(self.vtversion)
        self.connect(self.mshpController.vtController,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.mshpControllerVistrailChanged)
        self.mshpController.versionChanged.connect(self.mshpVersionChanged)
        self.aliasPanel.updateController(self.mshpController)
        _app.notify('mshpcontroller_changed', self.mshpController)
    
    def createActions(self):
        self.saveAction = QtGui.QAction("Save", self,
                                        triggered=self.saveTriggered)
        self.previewAction = QtGui.QAction("Preview",  self,
                                           triggered=self.previewTriggered,
                                           checkable=True)
        
    def createToolBar(self):
        self.toolbar = QtGui.QToolBar(self)
        
        self.toolbar.addAction(self.previewAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.saveAction)
        self.addToolBar(self.toolbar)
        
    def createAliasPanelTab(self):
        self.aliasPanel = QAliasListPanel(parent=self)
        self.stack.addWidget(self.aliasPanel)
        self.tabBar.addTab("Aliases")
        
    def createPreviewTab(self):
        self.previewTab = QtGui.QWidget()
        self.refreshButton = QtGui.QPushButton("Refresh", self)
        self.refreshButton.setFlat(True)
        self.refreshButton.setEnabled(False)
        self.refreshButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                                           QtGui.QSizePolicy.Fixed))
        self.previewApp = QMashupAppMainWindow(parent=self, 
                                               controller=self.mshpController)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
        layout.addWidget(self.refreshButton, QtCore.Qt.AlignLeft)
        layout.addWidget(self.previewApp)
        self.previewTab.setLayout(layout)
        self.stack.insertWidget(1, self.previewTab)
        self.tabBar.insertTab(1, "Preview")
        self.stack.setCurrentIndex(1)
        self.tabBar.setCurrentIndex(1)
    
    @pyqtSlot(int)    
    def switchTab(self, index):
        self.stack.setCurrentIndex(index)
        
    def updatePreviewTab(self, info):
        if self.previewTab:
            self.stack.removeWidget(self.previewTab)
            self.tabBar.removeTab(1)
            self.previewTab = None
        if info[0] != self.controller:
            print "Controllers are different!"
        self.createPreviewTab()
        
    def previewTriggered(self):
        if self.previewAction.isChecked():
            self.updatePreviewTab((self.controller,))
        else:
            if self.previewTab:
                self.stack.removeWidget(self.previewTab)
                self.tabBar.removeTab(1)
                self.previewTab = None
                
    def saveTriggered(self):
        print "save pressed"
        
    def mshpControllerVistrailChanged(self):
        print "*** vistrailChanged mashup view ", self.mshpController.vtController.current_version
        pipeline = self.mshpController.vtController.current_pipeline
        self.mshpController.updateAliasesFromPipeline(pipeline)
        
    def mshpVersionChanged(self, versionId):
        print "mshpVersion", versionId
        self.aliasPanel.updateVersion(versionId)
        
    def aliasChanged(self, param):
        print "mashupView aliasChanged", param
        self.mshpController.updateAliasFromParam(param)