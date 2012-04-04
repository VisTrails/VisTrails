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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from core.data_structures.bijectivedict import Bidict
from gui.base_view import BaseView
from gui.mashups.mashups_manager import MashupsManager
from gui.mashups.alias_list import QAliasListPanel
from gui.utils import show_question, YES_BUTTON, NO_BUTTON, CANCEL_BUTTON

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
        self.tab_to_stack_idx = {}
        self.button_to_tab_idx = Bidict()
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
        widget.setVisible(True)
        #self.createPipelineTab()
        self.setWindowTitle("Mashup Builder")
        self.vtversion = -1
        self.manager = MashupsManager.getInstance()
        
    def set_default_layout(self):
        from gui.mashups.mashups_inspector import QMashupsInspector
        from gui.mashups.alias_parameter_view import QAliasParameterView
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QMashupsInspector,
             QtCore.Qt.RightDockWidgetArea: QAliasParameterView,
             })
            
    def set_action_links(self):
        self.action_links = \
            {
            }
            
    def set_action_defaults(self):
        self.action_defaults['execute'] = [('setEnabled', False, False)]
        
    def set_controller(self, controller):
        """set_controller(controller:VistrailController) -> None
         This will set vistrail controller"""
        if controller == self.controller:
            return
#        if self.controller is not None:
#            self.disconnect(self.controller,
#                             QtCore.SIGNAL('versionWasChanged'),
#                             self.versionChanged)
        self.controller = controller
#        if self.controller:
#            self.connect(self.controller,
#                         QtCore.SIGNAL('versionWasChanged'),
#                         self.versionChanged)
        #print "      *** mashup view set vtController: ", controller
        
    def versionChanged(self, version):
        window = self.window()
        self.vtversion = version
        if self.vtversion > -1:
            window.qactions['mashup'].setEnabled(True)
        else:
            window.qactions['mashup'].setEnabled(False)
        #print "      *** mashup view versionChanged ", self.vtversion
        
    def controllerChanged(self, controller):
        from gui.vistrails_window import _app
        self.set_controller(controller)
        self.versionChanged(self.controller.current_version)
        if _app.get_current_tab() == self:
            self.updateView()
        
    def updateView(self):
        from gui.vistrails_window import _app
        if self.vtversion > 0:
            if self.mshpController is not None:
                self.mshpController.versionChanged.disconnect(self.mshpVersionChanged)
                self.mshpController.stateChanged.disconnect(self.mshpStateChanged)
                if self.mshpController.vtController is not None:
                    self.disconnect(self.mshpController.vtController,
                                    QtCore.SIGNAL('vistrailChanged()'),
                                    self.mshpControllerVistrailChanged)
            self.controller.flush_delayed_actions()
            self.vtversion = self.controller.current_version
            self.mshpController = self.manager.createMashupController(self.controller,
                                                                 self.vtversion)
            #self.pipelineTab.set_controller(self.mshpController.vtController)
            #self.pipelineTab.set_to_current()
            self.mshpController.vtController.change_selected_version(self.vtversion)
            self.connect(self.mshpController.vtController,
                         QtCore.SIGNAL('vistrailChanged()'),
                         self.mshpControllerVistrailChanged)
            self.mshpController.versionChanged.connect(self.mshpVersionChanged)
            self.mshpController.stateChanged.connect(self.mshpStateChanged)
            self.aliasPanel.updateController(self.mshpController)
            self.clearPreviewTabs()
            _app.notify('mshpcontroller_changed', self.mshpController)
    
    def createActions(self):
        self.saveAction = QtGui.QAction("Tag", self,
                                        triggered=self.saveTriggered)
        self.saveAction.setToolTip("Tag current mashup")
        self.saveAction.setEnabled(False)
        self.previewAction = QtGui.QAction("Preview",  self,
                                           triggered=self.previewTriggered,
                                           checkable=False)
        self.previewAction.setToolTip("Preview current mashup")
        
    def createToolBar(self):
        self.toolbar = QtGui.QToolBar(self)
        
        self.toolbar.addAction(self.previewAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.saveAction)
        self.addToolBar(self.toolbar)
        
    def createAliasPanelTab(self):
        self.aliasPanel = QAliasListPanel(parent=self)
        
        idx = self.stack.addWidget(self.aliasPanel)
        self.aliasPanel.set_index(idx)
        tab_idx = self.tabBar.addTab("Aliases")
        self.aliasPanel.set_tab_idx(tab_idx)
        self.tab_to_stack_idx[tab_idx] = idx
        
    def createPreviewTab(self, version):
        
        previewTab = QMashupViewTab(self.mshpController, version)
#        self.refreshButton = QtGui.QPushButton("Refresh", self)
#        self.refreshButton.setFlat(True)
#        self.refreshButton.setEnabled(False)
#        self.refreshButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
#                                                           QtGui.QSizePolicy.Fixed))
        previewApp = self.manager.createMashupApp(self.controller,
                                                  self.mshpController.mshptrail,
                                                  version)
        previewApp.appWasClosed.connect(self.previewTabWasClosed)
        
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
        #layout.addWidget(self.refreshButton, QtCore.Qt.AlignLeft)
        layout.addWidget(previewApp)
        previewTab.setLayout(layout)
        idx = self.stack.addWidget(previewTab)
        previewTab.set_index(idx)
        tab_idx = self.tabBar.addTab("Preview: %s"%self.mshpController.getMashupName(version))
        previewTab.set_tab_idx(tab_idx)
        self.tab_to_stack_idx[tab_idx] = idx
        closeButton = QMashupViewCloseButton(self.tabBar)
        closeSide = self.tabBar.style().styleHint(
                                   QtGui.QStyle.SH_TabBar_CloseButtonPosition,
                                   None, self.tabBar)
        closeButton.clicked.connect(self.closePreviewTab)
        self.tabBar.setTabButton(tab_idx, closeSide, closeButton)
        self.button_to_tab_idx[closeButton] = tab_idx
        self.tabBar.setCurrentIndex(tab_idx)
        
    @pyqtSlot()
    def closePreviewTab(self):
        closeButton = self.sender()
        tab_idx = self.button_to_tab_idx[closeButton]
        self.tabBar.removeTab(tab_idx)
        stack_idx = self.tab_to_stack_idx[tab_idx]
        if stack_idx >= 0:
            self.stack.removeWidget(self.stack.widget(stack_idx))
        del self.button_to_tab_idx[closeButton]
        self.updateIndexes(tab_idx, stack_idx)
    
    def previewTabWasClosed(self, previewApp):
        previewTab = previewApp.parent()
        tab_idx = previewTab.get_tab_idx()
        stack_idx = self.tab_to_stack_idx[tab_idx]
        if previewTab == self.stack.widget(stack_idx):
            #this means the quit button was pressed 
            closeButton = self.button_to_tab_idx.inverse[tab_idx]
            self.tabBar.removeTab(tab_idx)
            self.stack.removeWidget(self.stack.widget(stack_idx))
            del self.button_to_tab_idx[closeButton]
            self.updateIndexes(tab_idx, stack_idx)
        
    def updateIndexes(self, rm_tab_idx, rm_stack_idx):
        for (b,tab_idx) in self.button_to_tab_idx.iteritems():
            if tab_idx > rm_tab_idx:
                self.button_to_tab_idx[b] -= 1
        for idx in range(self.stack.count()):
            if idx >= rm_stack_idx:
                view = self.stack.widget(idx)
                view.set_index(idx)
                view.set_tab_idx(view.tab_idx-1)
                
    def clearPreviewTabs(self):
        tab_idx = self.tabBar.count()-1
        while self.tabBar.count() > 1:
            idx = self.tab_to_stack_idx[tab_idx]
            if type(self.stack.widget(idx)) == QMashupViewTab:
                self.tabBar.removeTab(tab_idx)
                if idx >= 0:
                    self.stack.removeWidget(self.stack.widget(idx))
            tab_idx -= 1
        
    @pyqtSlot(int)    
    def switchTab(self, index):
        try:
            self.stack.setCurrentIndex(self.tab_to_stack_idx[index])
        except KeyError:
            pass
            
    def previewTriggered(self):
        self.createPreviewTab(self.mshpController.currentVersion)
                
    def saveTriggered(self):
        (pid, pname) = self.mshpController.findFirstTaggedParent(self.mshpController.currentVersion)
        if pid >= 1:
            res = show_question("VisTrails::Mashups", 
                """You've decided to keep a modified version of '%s'.
Would you like to update it (this will move the tag to the current version)?
Click on No to create a new tag.""" %pname,
                [CANCEL_BUTTON, YES_BUTTON, NO_BUTTON], 0)
            if res == YES_BUTTON:
                #move tag
                self.mshpController.moveTag(pid, 
                                            self.mshpController.currentVersion,
                                            pname)
            elif res == NO_BUTTON:
                # show createNewtag dialog
                tag_exists = True
                ok = True
                while ok and tag_exists:
                    (text, ok) = QtGui.QInputDialog.getText(self, "VisTrails::Mashups",
                                                            "Enter a new tag:",
                                                            text="")
                    if ok and not text.isEmpty():
                        tag = str(text)
                        if self.mshpController.updateCurrentTag(tag):
                            tag_exists = False
        
    def mshpControllerVistrailChanged(self):
        #print "*** vistrailChanged mashup view ", self.mshpController.vtController.current_version
        pipeline = self.mshpController.vtController.current_pipeline
        self.mshpController.updateAliasesFromPipeline(pipeline)
        
    def mshpVersionChanged(self, versionId):
        from gui.vistrails_window import _app
        #print "*** mshpVersionChanged ", versionId
        self.aliasPanel.updateVersion(versionId)
        if not self.mshpController.versionHasTag(versionId):
            self.saveAction.setEnabled(True)
        else:
            self.saveAction.setEnabled(False)
        _app.notify('mshpversion_changed', versionId)
            
    def mshpStateChanged(self):
        for idx in range(self.stack.count()):
            view = self.stack.widget(idx)
            if type(view) == QMashupViewTab:
                tab_idx = view.tab_idx
                self.tabBar.setTabText(tab_idx,
                  "Preview: %s"%self.mshpController.getMashupName(view.version))
                
    def aliasChanged(self, param):
        #print "mashupView aliasChanged", param
        self.mshpController.updateAliasFromParam(param)
        
###############################################################################

class QMashupViewTab(QtGui.QWidget, BaseView):
    def __init__(self, mshpController, version, parent=None):
        QtGui.QWidget.__init__(self, parent)
        BaseView.__init__(self)
        self.mshpController = mshpController
        self.version = version
    
    def set_default_layout(self):
        from gui.mashups.mashups_inspector import QMashupsInspector
        from gui.mashups.alias_parameter_view import QAliasParameterView
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QMashupsInspector,
             QtCore.Qt.RightDockWidgetArea: QAliasParameterView,
             })
    
    def set_action_links(self):
        self.action_links = \
            {
            }
            
    def set_action_defaults(self):
        self.action_defaults = \
            {#'execute' : [('setEnabled', False, False)],
             }
        
###############################################################################

class QMashupViewCloseButton(QtGui.QAbstractButton):
    def __init__(self, parent):
        QtGui.QAbstractButton.__init__(self)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setToolTip("Close Tab")
        self.resize(self.sizeHint())
        
    def sizeHint(self):
        self.ensurePolished()
        width = self.style().pixelMetric(QtGui.QStyle.PM_TabCloseIndicatorWidth, 
                                         None, self)
        height = self.style().pixelMetric(QtGui.QStyle.PM_TabCloseIndicatorHeight,
                                          None, self)
        return QtCore.QSize(width, height)
    
    def enterEvent(self, event):
        if self.isEnabled():
            self.update()
        QtGui.QAbstractButton.enterEvent(self, event)
        
    def leaveEvent(self, event):
        if self.isEnabled():
            self.update()
        QtGui.QAbstractButton.leaveEvent(self, event)
        
    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        opt = QtGui.QStyleOption()
        opt.init(self)
        opt.state |= QtGui.QStyle.State_AutoRaise
        if (self.isEnabled() and self.underMouse() and 
            not self.isChecked() and not self.isDown()):
            opt.state |= QtGui.QStyle.State_Raised
        if self.isChecked():
            opt.state |= QtGui.QStyle.State_On
        if self.isDown():
            opt.state |= QtGui.QStyle.State_Sunken
        tb = self.parent()
        if isinstance(tb, QtGui.QTabBar):
            index = tb.currentIndex()
            position = self.style().styleHint(QtGui.QStyle.SH_TabBar_CloseButtonPosition,
                                              None, tb)
            if tb.tabButton(index, position) == self:
                opt.state |= QtGui.QStyle.State_Selected
        self.style().drawPrimitive(QtGui.QStyle.PE_IndicatorTabClose, opt, p, 
                                   self)
        
