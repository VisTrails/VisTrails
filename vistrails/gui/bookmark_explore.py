############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
""" This file contains widgets related to parameter exploration 
of aliases in user's bookmarks

QAliasExplorationPanel
QAliasDorpBox
QAliasExplorationTable
QAliasTableItem

"""
from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from gui.common_widgets import QToolWindowInterface
from gui.bookmark_alias import QAliasTable, QAliasTableWidgetItem
from gui.param_explore import QRangeString 

################################################################################
class QAliasExplorationPanel(QtGui.QFrame, QToolWindowInterface):
    """
    QAliasExplorationPanel shows aliases to be explored.
    
    """
    def __init__(self, parent=None, manager=None):
        """ QAliasExplorationPanel(parent: QWidget, manaager: BookmarksManager)
                                                 -> QAliasExplorationPanel
        Initializes the panel and sets bookmark manager
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Panel|QtGui.QFrame.Sunken)
        self.manager = manager
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.dropbox = QAliasDropBox(None, self.manager)
        self.dropbox.bookmarkPanel = parent.bookmarkPanel
        layout.addWidget(self.dropbox, 1)
        self.setWindowTitle('Exploration')

class QAliasDropBox(QtGui.QScrollArea):
    """
    QAliasDropBox is just a widget such that alias items from
    QBookmarkAliasPanel can be dropped into its client rect. It then
    construct an input form based on the type of handling widget
    
    """
    def __init__(self, parent=None, manager=None):
        """ QAliasDropBox(parent: QWidget) -> QAliasDropBox
        Initialize widget constraints
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setAcceptDrops(True)
        self.bookmarkPanel = None
        self.panel = self.createPanel()
        self.panel.setVisible(False)
        self.setWidgetResizable(True)
        self.setWidget(self.panel)
        self.updateLocked = False
        self.manager = manager

    def createPanel(self):
        widget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        widget.layout().setMargin(0)
        widget.layout().setSpacing(0)

        self.sizeLabel = QtGui.QLabel('&Step Count')
        self.sizeEdit = QtGui.QSpinBox()
        self.sizeEdit.setMinimum(1)        
        self.connect(self.sizeEdit,QtCore.SIGNAL("valueChanged(int)"),
                     self.stepCountChanged)
        self.sizeLabel.setBuddy(self.sizeEdit)
        
        sizeLayout = QtGui.QHBoxLayout()
        sizeLayout.setMargin(1)
        sizeLayout.addWidget(self.sizeLabel)
        sizeLayout.addWidget(self.sizeEdit)
        sizeLayout.addStretch(0)
        layout.addLayout(sizeLayout)
        
        self.parameters = QAliasExplorationTable()
        
        layout.addWidget(self.parameters, 1)
        self.exploreButton = QtGui.QPushButton("Perform Exploration")
        layout.addWidget(self.exploreButton)
        self.exploreButton.setVisible(False)
        self.connect(self.exploreButton, QtCore.SIGNAL('clicked()'),
                     self.startParameterExploration)
        widget.setVisible(False)

        return widget

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from alias table
        
        """
        if type(event.source())==QAliasTable:
            data = event.mimeData()
            if hasattr(data, 'aliases'):
                event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drag move event from alias table
        
        """
        if type(event.source())==QAliasTable:
            data = event.mimeData()
            if hasattr(data, 'aliases'):
                event.accept()

    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new alias
        
        """
        if type(event.source())==QAliasTable:
            data = event.mimeData()
            if hasattr(data, 'aliases'):
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
                for item in data.aliases:
                    if self.parameters.rowCount() == 0:
                        self.parameters.horizontalHeader().show()
                        self.exploreButton.setVisible(True)
                        self.sizeLabel.setVisible(True)
                        self.sizeEdit.setVisible(True)
                    self.parameters.createAliasRow(item.alias, item.type)
                    # if item.port:
#                         function = ModuleFunction.fromSpec(item.port,
#                                                            item.spec)
#                         self.vWidget.addFunction(item.module,
#                                                  item.module.getNumFunctions(),
#                                                  function)
#                         self.scrollContentsBy(0, self.viewport().height())
#                    self.lockUpdate()
 #                        if self.controller:
#                             self.controller.previousModuleIds = [self.module.id]
#                             self.controller.addMethod(self.module.id, function)
#                         self.unlockUpdate()

    def updateModule(self, module):
        """ updateModule(module: Module)) -> None        
        Construct input forms with the list of functions of a module
        
        """
        self.module = module
        if self.updateLocked: return
        self.vWidget.clear()
        if module:
            fId = 0
            for f in module.functions:                
                self.vWidget.addFunction(module.id, fId, f)
                fId += 1

    def lockUpdate(self):
        """ lockUpdate() -> None
        Do not allow updateModule()
        
        """
        self.updateLocked = True
        
    def unlockUpdate(self):
        """ unlockUpdate() -> None
        Allow updateModule()
        
        """
        self.updateLocked = False

    def startParameterExploration(self):
        """ startParameterExploration() -> None
        Collects inputs from widgets and the builders to setup and
        start a parameter exploration
        
        """
        if not self.manager.controller:
            return
        specs = []
        stepCount = self.sizeEdit.value()
        specsPerDim = []
        for row in range(self.parameters.rowCount()):
            type = self.parameters.verticalHeaderItem(row).type
            alias = self.parameters.verticalHeaderItem(row).alias
            ranges = []
            if type == 'String':
                wgt = self.parameters.cellWidget(row,0)
                strCount = wgt.listWidget.count()
                strings = [str( wgt.listWidget.item(i%strCount).text())
                           for i in range(stepCount)]
                ranges.append(strings)
            else:
                convert = {'Integer': int,
                           'Float': float}
                cv = convert[type]
                sItem = self.parameters.item(row,0)
                eItem = self.parameters.item(row,1)
                ranges.append((cv(sItem.text()),cv(eItem.text())))
            interpolator = (alias, type, ranges, stepCount) 
            specsPerDim.append(interpolator)                
        specs.append(specsPerDim)
        ids = self.bookmarkPanel.bookmarkPalette.checkedList
        self.manager.parameterExploration(ids, specs)

    def stepCountChanged(self, count):
        """ stepCountChanged(count: int)        
        When the number step in this dimension is changed, notify and
        invalidate all of its children
        
        """
        pass

class QAliasExplorationTable(QtGui.QTableWidget):
    """
    QAliasExplorationTable just inherits from QTableWidget to have a customized
    table and items

    """
    def __init__(self, parent=None, manager=None):
        """ QAliasExplorationTable(parent: QWidget, manager:BookmarkManager ) -> 
        QAliasExplorationTable
        Set bookmark manager
        """
        QtGui.QTableWidget.__init__(self, parent)
        self.manager = manager
        self.aliases = {}
        self.setColumnCount(2)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        labels = QtCore.QStringList()
        labels << "Start" << "End"
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().hide()
        self.connect(self.verticalHeader(),
                     QtCore.SIGNAL("sectionClicked(int)"),
                     self.updateFocus)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        
    def createAliasRow(self, alias, type):
        """ createAliasRow( alias: str, type: str) -> None
        Creates a row in the table
        
        """
        row = self.rowCount()
        self.insertRow(row)
        
        item = QAliasTableWidgetItem(alias, type, alias)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setVerticalHeaderItem(row,item)
        
        if type != 'String':
            sItem = QAliasTableWidgetItem(alias, type, "") 
            sItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable \
                           | QtCore.Qt.ItemIsSelectable)
            eItem = QAliasTableWidgetItem(alias, type, "")
        
            self.setItem(row, 0, sItem)    
            self.setItem(row, 1, eItem)
        else:
            self.setSpan(row,0,1,2)
            widget = QtGui.QWidget(self)
            layout = QtGui.QGridLayout()
            widget.setLayout(layout)
            lineEdit = QRangeString(0, widget)
            widget.listWidget = lineEdit.listWidget
            layout.addWidget(lineEdit,0,1,1,2)
            h = widget.sizeHint().height()
            w = widget.sizeHint().width()
            self.setRowHeight(row,h)
            self.setCellWidget(row,0,widget)

    def updateFocus(self, row):
        """ updateFocus(row: int) -> None
        Set focus to the alias cell when clicking on the header cell 

        """
        self.setCurrentCell(row,0)

    def getItemRow(self, alias):
        for i in range(self.rowCount()):
            item = self.verticalHeaderItem(i)
            if item:
                if item.alias == alias:
                    return i
        return -1

    def removeAlias(self, alias):
        row = self.getItemRow(alias)
        if row > -1:
            self.removeRow(row)
