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

""" This file contains widgets for displaying a list of aliases.

Classes defined in this file:

QAliasListPanel
QAliasListItem
QAliasList

"""
from __future__ import division

import copy
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal


from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core.mashup.alias import Alias
from vistrails.gui.base_view import BaseView
from vistrails.gui.mashups.alias_inspector import QAliasInspector
from vistrails.gui.utils import show_question, YES_BUTTON, NO_BUTTON

###############################################################################
class QAliasListPanel(QtGui.QWidget, BaseView):
    """
    QAliasListPanel shows list of aliases in pipeline.
    
    """
    #signals
    highlightModule = pyqtSignal(int)
    aliasesChanged = pyqtSignal()
    aliasChanged = pyqtSignal(Alias)
    aliasRemoved = pyqtSignal(str)
    
    def __init__(self, controller=None, parent=None):
        """ QAliasListPanel(controller: MashupController,
                            parent: QWidget) -> QAliasListPanel
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.controller = None
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        layout = QtGui.QVBoxLayout()
        self.aliases = QAliasList(controller, self)
        self.inspector = QAliasInspector(self.aliases)
        self.updateController(controller)
        self.setLayout(layout)
        #self.layout().setMargin(0)
        #self.layout().setSpacing(1)
        self.splitter = QtGui.QSplitter()
        layout.addWidget(self.splitter)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.aliases)
        self.splitter.addWidget(self.inspector)
        self.splitter.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.splitter.setStretchFactor(0,0)
        self.splitter.setStretchFactor(1,1)

        #connecting signals        
        self.aliases.itemSelectionChanged.connect(self.updateInspector)
        self.aliases.highlightModule.connect(self.highlightModule)
        self.aliases.aliasUpdated.connect(self.updateAlias)
        self.aliases.aliasRemoved.connect(self.aliasRemoved)
        
        self.inspector.aliasChanged.connect(self.updateAlias)
        
    def updateController(self, controller, other_dict=None):
        if self.controller:
            self.aliasRemoved.disconnect(self.controller.removeAlias)
            self.aliasChanged.disconnect(self.controller.updateAlias)
        self.controller = controller
        if self.controller:
            self.aliases.controller = self.controller
            if (self.controller.currentMashup.alias_list and
                len(self.controller.currentMashup.alias_list) > 0):
                self.aliases.populateFromMashup(self.controller)
            else:
                self.aliases.clear()
            self.aliasRemoved.connect(self.controller.removeAlias)
            self.aliasChanged.connect(self.controller.updateAlias)

    def updateVersion(self, versionId):    
        #print "AliasPanel.updateVersion "
        if self.controller:
            if (self.controller.currentMashup.alias_list and
                len(self.controller.currentMashup.alias_list) > 0):
                self.aliases.populateFromMashup(self.controller)
            else:
                self.aliases.clear()
                
    @pyqtSlot()
    def updateInspector(self):
        if len(self.aliases.selectedItems()) == 1:
            item = self.aliases.selectedItems()[0]
            self.inspector.updateContents(item.alias, self.controller)
        else:
            self.inspector.updateContents()
       
    @pyqtSlot(Alias) 
    def updateAlias(self, alias):
        #make sure the module is highlighted in the pipeline view 
        # or method_drop box is empty
        self.aliasChanged.emit(alias)
        self.aliasesChanged.emit()
        
    def set_default_layout(self):
        from vistrails.gui.mashups.mashups_inspector import QMashupsInspector
        from vistrails.gui.mashups.alias_parameter_view import QAliasParameterView
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QMashupsInspector,
             QtCore.Qt.RightDockWidgetArea: QAliasParameterView,
             })
            
    def set_action_links(self):
        self.action_links = \
            {
            }
        
###############################################################################

class QAliasList(QtGui.QTreeWidget):
    """
    QAliasList just inherits from QListView to have a customized
    list and items

    """
    #signals
    aliasUpdated = pyqtSignal(Alias)
    aliasRemoved = pyqtSignal(str)
    highlightModule = pyqtSignal(int)
    
    def __init__(self, controller, panel, parent=None):
        """ QAliasList(parent: QWidget) -> QAliasTable

        """
        QtGui.QTreeWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setRootIsDecorated(False)
        self.panel = panel
        self.aliases = Bidict()
        self.alias_widgets = {}
        self.controller = controller
        self.header().setStretchLastSection(True)
        self.setHeaderLabels(["Position", "Name", "Type"])
        self.itemSelectionChanged.connect(self.setPreviousSelected)
        self.connect(self,
                     QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)"),
                     self.currentAliasChanged)
        self.previousSelected = -1
    
    @pyqtSlot() 
    def setPreviousSelected(self):
        if len(self.selectedItems()) == 1:
            item = self.selectedItems()[0]
            self.previousSelected = self.indexOfTopLevelItem(item)
        else:
            self.previousSelected = -1      
    
    def processCellChanges(self, row, col):
        """ processCellChanges(row: int, col: int) -> None
        Event handler for capturing when the contents in a cell changes

        """
        item = self.item(row, col)
        if col == 0:
            old_alias = item.alias.alias
            new_alias = str(item.text())
            if new_alias in self.aliases.keys():
                QtGui.QMessageBox.warning(self,
                                          "VisMashup",
                                          """Label name %s already exists. 
                                          Please type a different name. """ % 
                                          new_alias)
                item.setText(old_alias)
                return
            elif new_alias == '':
                del self.aliases[old_alias]
                wdgt = self.cellWidget(row, 1)
                del self.alias_widgets[wdgt]
                item.alias.alias = ''
                self.removeRow(row)
                wdgt.deleteLater()
                self.updateRowNumbers()
            else:
                self.aliases[new_alias] = self.aliases[old_alias]
                del self.aliases[old_alias]
                item.alias.alias = new_alias
                
        elif col == 1:
            wdgt = self.cellWidget(row,col)
            if wdgt is not None:
                item.alias.value = wdgt.contents()
        self.aliasUpdated.emit(item.alias)
        
    def currentAliasChanged(self, current, previous):
        if current:
            if ((previous is not None and current.alias != previous.alias) or
                previous is None):
                self.highlightModule.emit(current.alias.component.vtmid)
        else:
            self.highlightModule.emit(-1)
        
    def _getOtherParameterInfo(self, pipeline, id, ptype):
        parameter = pipeline.db_get_object(ptype,id)
        return (parameter.type, parameter.strValue, 1, parameter.pos)
        
    def createAliasItem(self, alias):
        """ createAliasRow( alias: core.mashup.Alias) -> AliasItem
            Creates a row in the list
            
        """
        
        alias.pos = self.topLevelItemCount()
        labels = [str(alias.component.pos), str(alias.name), \
                  str(alias.component.type)]
        item = QAliasListItem(self, alias, labels)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable )
        
        return alias
     
    def populateFromMashup(self, mashupController):
        #print "populateFromMashup ", self , self.previousSelected    
        if self.controller != mashupController:
            self.controller = mashupController
        self.itemSelectionChanged.disconnect(self.setPreviousSelected)
        self.aliases = {}
        self.alias_cache = {}
        self.alias_widgets = {}
        self.clear()
        mashup = self.controller.currentMashup
        if len(mashup.alias_list) > 0:
            for alias in mashup.alias_list:
                alias = self.createAliasItem(copy.copy(alias))
                self.aliases[alias.name] = alias
        
        if self.previousSelected > -1:
            if self.previousSelected >= self.topLevelItemCount():
                self.previousSelected = self.topLevelItemCount()-1
            item = self.topLevelItem(self.previousSelected)
            self.setItemSelected(item, True)
            self.setCurrentItem(item)
        self.itemSelectionChanged.connect(self.setPreviousSelected)
            
    def updatePosNumbers(self):
        new_order = []
        for idx in range(self.topLevelItemCount()):
            item = self.topLevelItem(idx)
            new_order.append(item.alias.component.pos)
            item.setText(0,str(idx))
        return new_order
            
    def moveItemToNewPos(self, old, new):
        """moveItemToNewPos(old:int, new:int) -> None
        Move item from pos old to pos new
        
        """
        self.itemSelectionChanged.disconnect(self.panel.updateInspector)
        item = self.takeTopLevelItem(old)
        self.insertTopLevelItem(new,item)
        self.clearSelection()
        new_order = self.updatePosNumbers()
        self.setItemSelected(item, True)
        self.itemSelectionChanged.connect(self.panel.updateInspector)
        self.controller.reorderAliases(new_order)
            
    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
         Capture 'Del', 'Backspace' for deleting aliases
       
        """       
        if (event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            self.removeCurrentAlias()
                
    @pyqtSlot(bool)
    def removeCurrentAlias(self, checked=False):
        item = self.currentItem()
        if not item:
            return
        name = item.alias.name
        # item will get recreated after question dialog shows so keep only index
        pos = self.indexOfTopLevelItem(item)
        res = show_question("Mashups", 
                "Are you sure do you want to remove '%s' from the mashup?"%name,
                [YES_BUTTON, NO_BUTTON], NO_BUTTON)
        if res == YES_BUTTON:
            self.previousSelected = pos 
            self.takeTopLevelItem(pos)
            del self.aliases[name]

            self.updatePosNumbers()
            if pos >= self.topLevelItemCount() - 1:
                pos = self.topLevelItemCount() - 1
            self.previousSelected = pos
            if pos != -1:
                new_item = self.topLevelItem(pos)
                self.setCurrentItem(new_item)
                self.setItemSelected(new_item, True)
            self.aliasRemoved.emit(name)        
################################################################################

class QAliasListItem (QtGui.QTreeWidgetItem):
    """
    QAliasListtItem represents alias on QAliasList
    
    """
    def __init__(self, parent, alias, labels):
        """ QAliasListItem(alias: AliasItem, labels: string): 
        Create a new item with alias and text

        """
        QtGui.QTreeWidgetItem.__init__(self, parent, labels)
        self.alias = alias

###############################################################################    

        
