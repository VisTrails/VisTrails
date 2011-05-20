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

from gui.vistrails_palette import QVistrailsPaletteInterface
from gui.mashups.alias_list import QAliasListPanel
from gui.mashups.mashups_manager import MashupsManager

class QMashupsInspector(QtGui.QFrame, QVistrailsPaletteInterface):
    """
    QMashupsInspector is a widget with tabs showing properties of the selected
    mashuptrail. It contains a list of tagged mashups, and when a mashup is
    selected, it shows the list of aliases in the mashup.
    
    """
    #signals
    mashupChanged = pyqtSignal()
    def __init__(self, controller=None, parent=None):
        """ QMashupsInspector(controller: MashupController,
                            parent: QWidget) -> QMashupsInspector
        
        """
        QtGui.QFrame.__init__(self, parent)
        QVistrailsPaletteInterface.__init__(self)
        print "****** Inspector INIT"
        self.setFrameStyle(QtGui.QFrame.Panel|QtGui.QFrame.Sunken)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        
        #ok, this will store the original vistrail controller
        self.controller = controller
        self.mshpController = None #MashupController
        self.manager = MashupsManager.getInstance()
        
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
        self.setLayout(layout)
        
        self.createMashupInspectorTab()
        self.createAliasPanelTab()
        self.createMashupsListTab()
        self.setWindowTitle("Mashups Inspector")
        self.oldPos = self.toolWindow().pos()
        
    def createAliasPanelTab(self):
        self.aliasPanel = QAliasListPanel(parent=self)
        self.stack.addWidget(self.aliasPanel)
        self.tabBar.addTab("Aliases")
        self.aliasPanel.aliasChanged.connect(self.mashupChanged)
        
    def createMashupInspectorTab(self):
        self.mashupInspector = QMashupProp(parent=self)
        self.stack.addWidget(self.mashupInspector)
        self.tabBar.addTab("Mashup")
        
    def createMashupsListTab(self):
        self.mashupsList = QMashupsListPanel(parent=self)
        self.stack.addWidget(self.mashupsList)
        self.tabBar.addTab("List")
        
    @pyqtSlot(int)
    def switchTab(self, index):
        self.stack.setCurrentIndex(index)
            
    def updateVistrailController(self, controller):
        self.controller = controller
        print "         *** Mashup Inspector: controller changed ", controller
    
    def updateVistrailVersion(self, version):
        if self.controller:
            self.vt_version = version
                
        print "         *** Mashup Inspector: version changed ", version
    
    def updateMshpController(self, mshpController):
        print "     **** updateMshpController", mshpController
        if (self.mshpController is not None and 
            self.mshpController != mshpController):
            self.mshpController.stateChanged.disconnect(self.stateChanged)
        self.mshpController = mshpController
        self.mshpController.stateChanged.connect(self.stateChanged)
        self.mashupInspector.updateController(mshpController)
        self.mashupsList.updateController(mshpController)
        self.aliasPanel.updateController(mshpController)
        
    def updateMshpVersion(self, version):
        print "updateMshpVersion", version
        
    def stateChanged(self):
        versionId = self.mshpController.currentVersion
        self.mashupInspector.updateVersion(versionId)
        self.mashupsList.stateChanged()
        
################################################################################        

class QMashupProp(QtGui.QWidget):
    def __init__(self, controller=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.controller = controller
        self.versionNumber = -1
        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(5)
        self.setLayout(vLayout)
        gLayout = QtGui.QGridLayout()
        gLayout.setMargin(0)
        gLayout.setSpacing(5)
        gLayout.setColumnMinimumWidth(1,5)
        gLayout.setRowMinimumHeight(0,24)
        gLayout.setRowMinimumHeight(1,24)
        gLayout.setRowMinimumHeight(2,24)
        gLayout.setRowMinimumHeight(3,24)        
        vLayout.addLayout(gLayout)
        
        tagLabel = QtGui.QLabel('Tag:', self)
        gLayout.addWidget(tagLabel, 0, 0, 1, 1)

        editLayout = QtGui.QHBoxLayout()
        editLayout.setMargin(0)
        editLayout.setSpacing(2)
        self.tagEdit = QtGui.QLineEdit()
        tagLabel.setBuddy(self.tagEdit)
        editLayout.addWidget(self.tagEdit)
        self.tagEdit.setEnabled(False)

        self.tagReset = QtGui.QToolButton(self)
        self.tagReset.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)))
        self.tagReset.setIconSize(QtCore.QSize(12,12))
        self.tagReset.setAutoRaise(True)
        self.tagReset.setEnabled(False)
        editLayout.addWidget(self.tagReset)

        gLayout.addLayout(editLayout, 0, 2, 1, 1)

        userLabel = QtGui.QLabel('User:', self)
        gLayout.addWidget(userLabel, 1, 0, 1, 1)
        
        self.userEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.userEdit, 1, 2, 1, 1)

        dateLabel = QtGui.QLabel('Date:', self)
        gLayout.addWidget(dateLabel, 2, 0, 1, 1)

        self.dateEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.dateEdit, 2, 2, 1, 1)
        
        vtLabel = QtGui.QLabel('Vistrail:', self)
        gLayout.addWidget(vtLabel, 3, 0, 1, 1)
        
        self.vtEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.vtEdit, 3, 2, 1, 1)
        
        vtVersionLabel = QtGui.QLabel('Workflow:', self)
        gLayout.addWidget(vtVersionLabel, 4, 0, 1, 1)
        
        self.vtVersionEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.vtVersionEdit, 4, 2, 1, 1)
        
        vLayout.addStretch()
        
        self.connect(self.tagEdit, QtCore.SIGNAL('editingFinished()'),
                     self.tagFinished)
        self.connect(self.tagEdit, QtCore.SIGNAL('textChanged(QString)'),
                     self.tagChanged)
        self.connect(self.tagReset, QtCore.SIGNAL('clicked()'),
                     self.tagCleared)
        
    def updateController(self, mshpController):
        self.controller = mshpController
       
        print "QMashupProp.updateController ", self.controller, self.controller.currentVersion
        if self.controller and self.controller.currentVersion > -1:
            self.versionNumber = self.controller.currentVersion
            self.tagEdit.setText(self.controller.mshptrail.getTagForActionId(
                                            self.controller.currentVersion))
            self.tagEdit.setEnabled(True)
            action = self.controller.mshptrail.actionMap[self.controller.currentVersion]
            self.userEdit.setText(action.user)
            self.dateEdit.setText(action.date)
            self.vtEdit.setText(self.controller.getVistrailName())
            self.vtVersionEdit.setText(self.controller.getVistrailWorkflowTag())
            return
        else:
            self.tagEdit.setEnabled(False)
            self.tagReset.setEnabled(False)
            self.tagEdit.setText('')
            self.userEdit.setText('')
            self.dateEdit.setText('')  
            self.vtEdit.setText('')
            self.vtVersionEdit.setText('')
        
    def updateVersion(self, versionNumber):
        self.versionNumber = versionNumber
        if self.controller and self.versionNumber > -1:
            tagtext = self.controller.mshptrail.getTagForActionId(
                                    self.versionNumber)
            print "updateVersion", versionNumber, tagtext
            self.tagEdit.setText(tagtext)
            action = self.controller.mshptrail.actionMap[self.versionNumber]
            self.userEdit.setText(action.user)
            self.dateEdit.setText(action.date)
            self.vtEdit.setText(self.controller.getVistrailName())
            self.vtVersionEdit.setText(self.controller.getVistrailWorkflowTag())
        else:
            self.tagEdit.setEnabled(False)
            self.tagReset.setEnabled(False)
            self.tagEdit.setText('')
            self.userEdit.setText('')
            self.dateEdit.setText('')  
            self.vtEdit.setText('')
            self.vtVersionEdit.setText('')
            
    def tagFinished(self):
        """ tagFinished() -> None
        Update the new tag to mashup
        
        """
        if self.controller:
            name = self.controller.mshptrail.getTagForActionId(self.versionNumber)
            currentText = str(self.tagEdit.text())
            if name != currentText:    
                print "will update current tag", currentText
                self.controller.updateCurrentTag(currentText)
                
                
    def tagChanged(self, text):
        """ tagChanged(text: QString) -> None
        Update the button state if there is text

        """
        self.tagReset.setEnabled(text != '')

    def tagCleared(self):
        """ tagCleared() -> None
        Remove the tag
        
        """ 
        self.tagEdit.setText('')
        self.tagFinished()

################################################################################
            
class QMashupsListPanel(QtGui.QWidget):
    def __init__(self, controller=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.controller = controller
        self.mashupsList = QtGui.QListWidget()
        self.mashupsList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
        label = QtGui.QLabel("Available mashups")
        layout.addWidget(label)
        layout.addWidget(self.mashupsList)
        self.setLayout(layout)
            
    def updateController(self, mshpController):
        self.controller = mshpController
        self.stateChanged()
                    
    def stateChanged(self):
        self.mashupsList.clear()
        if self.controller:
            self.tagMap = self.controller.mshptrail.getTagMap()
            currentTag = self.controller.getCurrentTag()
            tags = self.tagMap.keys()
            if len(tags) > 0:
                tags.sort()
                for tag in tags:
                    item = QtGui.QListWidgetItem(str(tag),self.mashupsList)
                    if tag == currentTag:
                        item.setSelected(True)
                