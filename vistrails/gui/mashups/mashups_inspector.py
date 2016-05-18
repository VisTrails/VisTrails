###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot
import vistrails.core.system
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.mashups.mashups_manager import MashupsManager
from vistrails.gui.utils import show_warning
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

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
        #print "****** Inspector INIT"
        self.set_title("Mashups Inspector")
        self.setFrameStyle(QtGui.QFrame.Panel|QtGui.QFrame.Sunken)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        
        #ok, this will store the original vistrail controller
        self.controller = controller
        self.mshpController = None #MashupController
        self.manager = MashupsManager.getInstance()
        
        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(3)
        self.workflowLabel = QtGui.QLabel("Workflow: ")
        layout.addWidget(self.workflowLabel)
        self.mashupsList = QMashupsListPanel(parent=self)
        listLabel = QtGui.QLabel("Available Mashups:")
        layout.addWidget(listLabel)
        layout.addWidget(self.mashupsList)
        
        self.mashupInspector = QMashupProp(parent=self)
        inspector_group = QtGui.QGroupBox("Mashup properties")
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(1)
        g_layout.setSpacing(3)
        g_layout.addWidget(self.mashupInspector)
        inspector_group.setLayout(g_layout)
        layout.addWidget(inspector_group)
        self.setLayout(layout)
                    
    def updateVistrailController(self, controller):
        self.controller = controller
        #print "         *** Mashup Inspector: controller changed ", controller
    
    def updateVistrailVersion(self, version):
        if self.controller:
            self.vt_version = version
                
        #print "         *** Mashup Inspector: version changed ", version
    
    def updateMshpController(self, mshpController):
        #print "     **** updateMshpController", mshpController
        if (self.mshpController is not None and 
            self.mshpController != mshpController):
            self.mshpController.stateChanged.disconnect(self.stateChanged)
        self.mshpController = mshpController
        self.workflowLabel.setText(
          "Workflow: <b>%s</b>"%self.mshpController.getVistrailWorkflowTag())
        self.mshpController.stateChanged.connect(self.stateChanged)
        self.mashupInspector.updateController(mshpController)
        self.mashupsList.updateController(mshpController)
        
    def updateMshpVersion(self, version):
        pass
        #print "updateMshpVersion", version
        
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
        
        #vtVersionLabel = QtGui.QLabel('Workflow:', self)
        #gLayout.addWidget(vtVersionLabel, 0, 0, 1, 1)
        
        #self.vtVersionEdit = QtGui.QLabel('', self)
        #gLayout.addWidget(self.vtVersionEdit, 0, 2, 1, 1)
        
        tagLabel = QtGui.QLabel('Mashup Tag:', self)
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
        
        self.btnExport = QDockPushButton("Export...")
        gLayout.addWidget(self.btnExport, 3,0,1,3, QtCore.Qt.AlignHCenter)
        
        vLayout.addStretch()
        
        self.connect(self.tagEdit, QtCore.SIGNAL('editingFinished()'),
                     self.tagFinished)
        self.connect(self.tagEdit, QtCore.SIGNAL('textChanged(QString)'),
                     self.tagChanged)
        self.connect(self.tagReset, QtCore.SIGNAL('clicked()'),
                     self.tagCleared)
        self.connect(self.btnExport, QtCore.SIGNAL("clicked()"),
                     self.exportMashupGUI)
        
    def updateController(self, mshpController):
        self.controller = mshpController
       
        #print "QMashupProp.updateController ", self.controller, self.controller.currentVersion
        if self.controller and self.controller.currentVersion > -1:
            self.versionNumber = self.controller.currentVersion
            self.tagEdit.setText(self.controller.mshptrail.getTagForActionId(
                                            self.controller.currentVersion))
            self.tagEdit.setEnabled(True)
            action = self.controller.mshptrail.actionMap[self.controller.currentVersion]
            self.userEdit.setText(action.user)
            self.dateEdit.setText(action.date)
            #self.vtEdit.setText(self.controller.getVistrailName())
            #self.vtVersionEdit.setText(self.controller.getVistrailWorkflowTag())
            return
        else:
            self.tagEdit.setEnabled(False)
            self.tagReset.setEnabled(False)
            self.tagEdit.setText('')
            self.userEdit.setText('')
            self.dateEdit.setText('')  
            #self.vtEdit.setText('')
            #self.vtVersionEdit.setText('')
        
    def updateVersion(self, versionNumber):
        self.versionNumber = versionNumber
        if self.controller and self.versionNumber > -1:
            tagtext = self.controller.mshptrail.getTagForActionId(
                                    self.versionNumber)
            #print "updateVersion", versionNumber, tagtext
            self.tagEdit.setText(tagtext)
            action = self.controller.mshptrail.actionMap[self.versionNumber]
            self.userEdit.setText(action.user)
            self.dateEdit.setText(action.date)
            #self.vtEdit.setText(self.controller.getVistrailName())
            #self.vtVersionEdit.setText(self.controller.getVistrailWorkflowTag())
        else:
            self.tagEdit.setEnabled(False)
            self.tagReset.setEnabled(False)
            self.tagEdit.setText('')
            self.userEdit.setText('')
            self.dateEdit.setText('')  
            #self.vtEdit.setText('')
            #self.vtVersionEdit.setText('')
            
    def tagFinished(self):
        """ tagFinished() -> None
        Update the new tag to mashup
        
        """
        if self.controller:
            name = self.controller.mshptrail.getTagForActionId(self.versionNumber)
            currentText = str(self.tagEdit.text())
            if name != currentText:    
                #print "will update current tag", currentText
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
        
    def exportMashupGUI(self):
        if self.controller:
            dialog = QMashupExportDialog(self)
            if dialog.exec_() == QtGui.QDialog.Accepted:
                result = dialog.btnPressed
                fileName = QtGui.QFileDialog.getSaveFileName(
                           self,
                           "Export Mashup...",
                           vistrails.core.system.vistrails_file_directory(),
                           "VisTrail link files (*.vtl)")
                if fileName:
                    filename = str(fileName)
                    res = MashupsManager.exportMashup(filename, 
                                                      self.controller.originalController, 
                                                      self.controller.mshptrail,
                                                      self.controller.currentVersion,
                                                      result)
                    if not res:
                        show_warning('VisTrails - Exporting Mashup',
                    'There was an error and the mashup could not be exported.')
                        
################################################################################
            
class QMashupsListPanel(QtGui.QWidget):
    def __init__(self, controller=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.controller = controller
        self.mashupsList = QtGui.QListWidget()
        self.mashupsList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.mashupsList.itemSelectionChanged.connect(self.changeSelection)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
        layout.addWidget(self.mashupsList)
        self.setLayout(layout)
            
    def updateController(self, mshpController):
        self.controller = mshpController
        self.stateChanged()
                    
    def stateChanged(self):
        self.mashupsList.itemSelectionChanged.disconnect(self.changeSelection)
        self.mashupsList.clear()
        if self.controller:
            self.tagMap = self.controller.mshptrail.getTagMap()
            currentTag = self.controller.getCurrentTag()
            tags = self.tagMap.keys()
            latestversion = self.controller.mshptrail.getLatestVersion()
            if not self.controller.versionHasTag(latestversion):
                item = QMashupListPanelItem("<latest>",
                                            latestversion,
                                            self.mashupsList)
                if latestversion == self.controller.currentVersion:
                    item.setSelected(True)

            if len(tags) > 0:
                tags.sort()
                for tag in tags:
                    item = QMashupListPanelItem(str(tag),
                                                self.tagMap[tag],
                                                self.mashupsList)
                    if tag == currentTag:
                        item.setSelected(True)
                        
        self.mashupsList.itemSelectionChanged.connect(self.changeSelection)
    
    @pyqtSlot()
    def changeSelection(self):
        items = self.mashupsList.selectedItems()
        if len(items) == 1:
            version = items[0].version
            if version != self.controller.currentVersion:
                self.controller.setCurrentVersion(version, quiet=False)
            
    def selectMashup(self, name):
        itemlist = self.mashupsList.findItems(name,
                                              QtCore.Qt.MatchExactly)
        if len(itemlist) == 1:
            item = itemlist[0]
            self.mashupsList.setCurrentItem(item)
            
################################################################################

class QMashupListPanelItem(QtGui.QListWidgetItem):
    def __init__(self, tag, version, parent=None):
        QtGui.QListWidgetItem.__init__(self, tag, parent)
        self.tag = tag
        self.version = version
        
################################################################################

class QMashupExportDialog(QtGui.QDialog):
    FULLTREE = 0
    MINIMAL = 1
    LINK = 2
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle('VisTrails - Exporting Mashup')
        dlgLayout = QtGui.QVBoxLayout()
        gb = QtGui.QGroupBox("This will export the mashup as a file:")
        gblayout = QtGui.QVBoxLayout()
        self.rbMinimal = QtGui.QRadioButton("Include only this mashup\
 and its original workflow")
        self.rbMinimal.setChecked(True)
        self.rbFullTree = QtGui.QRadioButton("Include full tree (this will also\
 include other mashups)")
        self.rbLink = QtGui.QRadioButton("As a link (this will work only on\
 this machine)")
        gblayout.addWidget(self.rbMinimal)
        gblayout.addWidget(self.rbFullTree)
        gblayout.addWidget(self.rbLink)
        gb.setLayout(gblayout)
        
        btnOk = QtGui.QPushButton("OK")
        btnCancel = QtGui.QPushButton("Cancel")
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addStretch()
        btnLayout.addWidget(btnOk)
        btnLayout.addWidget(btnCancel)
        btnLayout.addStretch()
        
        dlgLayout.addWidget(gb)
        dlgLayout.addLayout(btnLayout)
        self.setLayout(dlgLayout)
        
        self.btnPressed = -1
        self.connect(btnOk, QtCore.SIGNAL("clicked()"), self.btnOkPressed) 
        self.connect(btnCancel, QtCore.SIGNAL("clicked()"), self.btnCancelPressed)
        
    def btnOkPressed(self):
        if self.rbFullTree.isChecked():
            self.btnPressed = self.FULLTREE
        elif self.rbMinimal.isChecked():
            self.btnPressed = self.MINIMAL
        elif self.rbLink.isChecked():
            self.btnPressed = self.LINK
        self.accept()
        
    def btnCancelPressed(self):
        self.btnPressed = -1
        self.reject()