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

""" This file contains widgets for displaying a list of aliases.

Classes defined in this file:

QAliasListPanel
QAliasListItem
QAliasList

"""

import copy
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal


from core.data_structures.bijectivedict import Bidict
from gui.mashups.alias_inspector import QAliasInspector
from core.mashup.alias import Alias
from gui.utils import show_question, YES_BUTTON, NO_BUTTON

###############################################################################
class QAliasListPanel(QtGui.QWidget):
    """
    QAliasListPanel shows list of aliases in pipeline.
    
    """
    #signals
    highlightModule = pyqtSignal(int)
    aliasesChanged = pyqtSignal()
    aliasChanged = pyqtSignal(Alias)
    
    def __init__(self, controller=None, parent=None):
        """ QAliasListPanel(controller: MashupController,
                            parent: QWidget) -> QAliasListPanel
        
        """
        QtGui.QWidget.__init__(self, parent)
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
        self.aliases.aliasRemoved.connect(self.removeAlias)
        
        self.inspector.aliasChanged.connect(self.updateAlias)
        
    def updateController(self, controller, other_dict=None):
        self.controller = controller
        if self.controller:
            self.aliases.controller = self.controller
            if (self.controller.currentMashup.alias_list and
                len(self.controller.currentMashup.alias_list) > 0):
                self.aliases.populateFromMashup(self.controller)
#            if other_dict is not None:
#                self.aliases.populateFromOtherDict(other_dict)
#                
#            elif self.controller.current_pipeline:
#                self.aliases.populateFromPipeline(
#                                            self.controller.current_pipeline)
        
    
    @pyqtSlot()
    def updateInspector(self):
        if len(self.aliases.selectedItems()) == 1:
            item = self.aliases.selectedItems()[0]
            self.inspector.updateContents(item.alias, self.controller)
        else:
            self.inspector.setVisible(False)
       
    @pyqtSlot()
    def removeAlias(self):
        self.aliasesChanged.emit()
        
    @pyqtSlot(Alias) 
    def updateAlias(self, alias):
        #make sure the module is highlighted in the pipeline view 
        # or method_drop box is empty
        self.highlightModule.emit(alias.component.vtmid)
        self.aliasChanged.emit(alias)
        self.aliasesChanged.emit()
        
    def reloadAliases(self):
        if self.controller.current_pipeline:
            self.aliases.populateFromPipeline(self.controller.current_pipeline)

###############################################################################

class QAliasList(QtGui.QTreeWidget):
    """
    QAliasList just inherits from QListView to have a customized
    list and items

    """
    #signals
    aliasUpdated = pyqtSignal(Alias)
    aliasRemoved = pyqtSignal()
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
        self.current_item = None
        self.controller = controller
        self.header().setStretchLastSection(True)
        self.setHeaderLabels(QtCore.QStringList() << "Position" << "Name" << "Type")
        
        self.connect(self,
                     QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)"),
                     self.currentAliasChanged)
                        
    def processCellChanges(self, row, col):
        """ processCellChanges(row: int, col: int) -> None
        Event handler for capturing when the contents in a cell changes

        """
        print "cellChanged"
        item = self.item(row, col)
        print item.alias
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
        print self.aliases
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
        labels = QtCore.QStringList() << str(alias.component.pos) << str(alias.name) << \
                                         str(alias.component.type)
        item = QAliasListItem(self, alias, labels)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable )
        
        return alias
     
    def populateFromMashup(self, mashupController):
        print "populateFromMashup"   
        if self.controller != mashupController:
            self.controller = mashupController
            
        self.aliases = {}
        self.alias_cache = {}
        self.alias_widgets = {}
        self.clear()
        mashup = self.controller.currentMashup
        if len(mashup.alias_list) > 0:
            for alias in mashup.alias_list:
                item = self.createAliasItem(alias)
                self.aliases[item.name] = item
                
    def populateFromOtherDict(self, other):
        #FIXME This function has not been migrated for the new GUI components
        print "populateFromOtherDict"
        for k, v in other.iteritems():
            print k , v
#        self.disconnect(self,
#                        QtCore.SIGNAL("cellChanged(int,int)"),
#                        self.processCellChanges)
        self.aliases = {}
        self.alias_cache = {}
        self.alias_widgets = {}
        self.clear()
        self.createHeader()
        self.setRowCount(0)
        if other:
            sorted_items = range(len(other))
            for aname, item in other.iteritems():
                sorted_items[item.pos] = aname
            
            for aname in sorted_items:
                info_item = other[aname]
                #print "before creating", aname, info_item.value
                self.alias_cache[aname] = copy.copy(info_item)
                item = self.createAliasRow(aname, info_item)
                self.aliases[aname] = item
                        
#        self.connect(self,
#                     QtCore.SIGNAL("cellChanged(int,int)"),
#                     self.processCellChanges)
        
    def getItemRow(self, alias):
        for i in xrange(self.rowCount()):
            item = self.item(i,0)
            if item:
                if item.alias == alias:
                    return i
        return -1
    
    def updatePosNumbers(self):
        for idx in range(self.topLevelItemCount()):
            item = self.topLevelItem(idx)
            item.alias.component.pos = idx
            item.setText(0,str(item.alias.component.pos))
            
    def moveItemToNewPos(self, old, new):
        """moveItemToNewPos(old:int, new:int) -> None
        Move item from pos old to pos new
        
        """
        self.itemSelectionChanged.disconnect(self.panel.updateInspector)
        item = self.takeTopLevelItem(old)
        self.insertTopLevelItem(new,item)
        self.clearSelection()
        self.updatePosNumbers()
        self.setItemSelected(item, True)
        self.itemSelectionChanged.connect(self.panel.updateInspector)
        
    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
         Capture 'Del', 'Backspace' for deleting aliases
       
        """       
        if (event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            self.removeCurrentAlias()
                
    @pyqtSlot(bool)
    def removeCurrentAlias(self, checked=False):
        item = self.currentItem() 
        name = item.alias.name
        res = show_question("Mashups", 
                "Are you sure do you want to remove '%s' from the mashup?"%name,
                [YES_BUTTON, NO_BUTTON], NO_BUTTON)
        if res == YES_BUTTON:
        
            old_alias = item.alias.name
            del self.aliases[old_alias]
        
            item.alias.name = ''
            pos = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(pos)
            self.updatePosNumbers()
            if pos < self.topLevelItemCount() -1:
                new_item = self.topLevelItem(pos)
            else:
                new_item = self.topLevelItem(pos-1)
            self.setCurrentItem(new_item)
            self.aliasRemoved.emit()        
################################################################################

class QAliasListItem (QtGui.QTreeWidgetItem):
    """
    QAliasListtItem represents alias on QAliasList
    
    """
    def __init__(self, parent, alias, labels):
        """ QAliasListItem(alias: AliasItem, labels: QStringList): 
        Create a new item with alias and text

        """
        QtGui.QTreeWidgetItem.__init__(self, parent, labels)
        self.alias = alias

###############################################################################    

        