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
from gui.pipeline_tab import QPipelineTab
from gui.mashups.mashup_app import QMashupAppMainWindow

class QMashupView(QtGui.QMainWindow):
    def __init__(self, mashupController, inspector, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
        self.controller = mashupController
        
        self.createActions()
        #Setting up a toolbar
        self.createToolBar(inspector)
        
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
        self.createPipelineTab()
        self.previewTab = None
        self.setWindowTitle("Mashup Builder")
        
    def createActions(self):
        self.saveAction = QtGui.QAction("Save", self,
                                        triggered=self.saveTriggered)
        self.previewAction = QtGui.QAction("Preview",  self,
                                           triggered=self.previewTriggered,
                                           checkable=True)
        
    def createToolBar(self, inspector):
        self.toolbar = QtGui.QToolBar(self)
        
        self.toolbar.addAction(self.previewAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(inspector.toolWindow().toggleViewAction())
        self.addToolBar(self.toolbar)
        
    def createPipelineTab(self):
        """ createPipelineTab() -> None
        Create a pipeline tab and append it to the list of windows

        """
        self.pipelineTab = QPipelineTab(self)
        self.pipelineTab.pipelineView.setPIPEnabled(False)
        self.pipelineTab.pipelineView.setReadOnlyMode(True)
        self.pipelineTab.moduleConfig.toolWindow().hide()
        self.pipelineTab.setController(self.controller.vtController)
        self.controller.vtController.change_selected_version(
                                                self.controller.vtVersion)
        self.stack.addWidget(self.pipelineTab)
        self.tabBar.addTab("Pipeline")
        
    def createPreviewTab(self):
        self.previewTab = QtGui.QWidget()
        self.refreshButton = QtGui.QPushButton("Refresh", self)
        self.refreshButton.setFlat(True)
        self.refreshButton.setEnabled(False)
        self.refreshButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                                           QtGui.QSizePolicy.Fixed))
        self.previewApp = QMashupAppMainWindow(parent=self, 
                                               controller=self.controller)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
        layout.addWidget(self.refreshButton, QtCore.Qt.AlignLeft)
        layout.addWidget(self.previewApp)
        self.previewTab.setLayout(layout)
        self.stack.insertWidget(1, self.previewTab)
        self.tabBar.insertTab(1, "Preview")
        self.stack.setCurrentIndex(1)
        
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