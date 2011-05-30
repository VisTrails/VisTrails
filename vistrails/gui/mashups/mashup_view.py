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
from gui.base_view import BaseView
from gui.mashups.mashup_app import QMashupAppMainWindow
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
        self.button_to_tab_idx = {}
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
        from gui.vistrails_window import _app
        self.vtversion = self.controller.current_version
        if self.vtversion > -1:
            _app.qactions['mashup'].setEnabled(True)
        else:
            _app.qactions['mashup'].setEnabled(False)
        print "      *** mashup view versionChanged ", self.vtversion
        
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
        self.saveAction = QtGui.QAction("Keep", self,
                                        triggered=self.saveTriggered)
        self.saveAction.setToolTip("Keep current mashup")
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
        #QMashupAppMainWindow(parent=self, 
        #                                  controller=self.mshpController,
        #                                  version=version)
        
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
#    def updatePreviewTab(self):
#        if self.previewTab:
#            self.stack.removeWidget(self.previewTab)
#            self.tabBar.removeTab(1)
#            self.previewTab = None
#        self.createPreviewTab()
#        
#    def checkAndUpdatePreview(self):
#        if self.previewTab:
#            self.updatePreviewTab()
            
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
        print "*** vistrailChanged mashup view ", self.mshpController.vtController.current_version
        pipeline = self.mshpController.vtController.current_pipeline
        self.mshpController.updateAliasesFromPipeline(pipeline)
        
    def mshpVersionChanged(self, versionId):
        print "*** mshpVersionChanged ", versionId
        self.aliasPanel.updateVersion(versionId)
        if not self.mshpController.versionHasTag(versionId):
            self.saveAction.setEnabled(True)
        else:
            self.saveAction.setEnabled(False)
            
    def mshpStateChanged(self):
        for idx in range(self.stack.count()):
            view = self.stack.widget(idx)
            if type(view) == QMashupViewTab:
                tab_idx = view.tab_idx
                self.tabBar.setTabText(tab_idx,
                  "Preview: %s"%self.mshpController.getMashupName(view.version))
                
    def aliasChanged(self, param):
        print "mashupView aliasChanged", param
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
        self.layout = \
            {QtCore.Qt.LeftDockWidgetArea: QMashupsInspector,
             QtCore.Qt.RightDockWidgetArea: QAliasParameterView,
             }
    
    def set_action_links(self):
        self.action_links = \
            {
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
        