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
""" This file contains widgets related to the panel 
displaying a list of common aliases in user's bookmarks

QBookmarkAliasPanel
QAliasTable
QAliasTableItem

"""
from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from gui.common_widgets import (QSearchTreeWindow,
                                QSearchTreeWidget,
                                QToolWindowInterface)

################################################################################
class QBookmarkAliasPanel(QtGui.QFrame, QToolWindowInterface):
    """
    QBookmarkAliasPanel shows common aliases to be manipulated.
    
    """
    def __init__(self, parent=None, manager=None):
        """ QBookmarkPalette(parent: QWidget) -> QBookmarkPalette
        Set bookmark manager
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Panel|QtGui.QFrame.Sunken)
        self.manager = manager
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.parameters = QAliasTable(None, self.manager)
        layout.addWidget(self.parameters, 1)
        self.setWindowTitle('Parameters')
        
    def updateAliasTable(self, aliases):
        """updateAliasTable(aliases:dict) -> None
        Reload aliases from the ensemble
        
        """
        self.parameters.updateFromEnsemble(aliases)

class QAliasTable(QtGui.QTableWidget):
    """
    QAliasTable just inherits from QTableWidget to have a customized
    table and items

    """
    def __init__(self, parent=None, manager=None):
        """ QAliasTable(parent: QWidget, manager:BookmarkManager,
                        rows: int, cols: int) -> QAliasTable
        Set bookmark manager
        """
        QtGui.QTableWidget.__init__(self, parent)
        self.manager = manager
        self.aliases = {}
        self.setColumnCount(1)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        self.connect(self,
                     QtCore.SIGNAL("cellChanged(int,int)"),
                     self.processCellChanges)
        
    def processCellChanges(self, row, col):
        """ parseCellChanges(row: int, col: int) -> None
        Event handler for capturing when the contents in a cell changes

        """
        if col == 0:
            value = str(self.item(row,col).text())
            alias = str(self.verticalHeaderItem(row).text())
            self.manager.updateAlias(alias, value)
                        
        
    def updateFromEnsemble(self, aliases):
        """ updateFromEnsemble(aliases: dict) -> None        
        Setup this table to show common aliases
        
        """
        def createAliasRow(alias, type, value):
            """ createAliasItem( alias: str, type: str, 
                                 value: str) -> QAliasTableWidgetItem
            Creates a row in the table
            
            """
            row = self.rowCount()
            self.insertRow(row)
            item = QAliasTableWidgetItem(alias)
            self.setVerticalHeaderItem(row,item)
            
            item = QAliasTableWidgetItem(value)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.setItem(row, 0, item)
            
        if self.manager:
            self.setRowCount(0)
            for alias, info in aliases.iteritems():
                type = info[0]
                value = info[1][0]
                createAliasRow(alias,type,value)

class QAliasTableWidgetItem(QtGui.QTableWidgetItem):
    """
    QAliasTableWidgetItem represents alias on QAliasTableWidget
    
    """
    def __init__(self, text):
        """ QAliasTableWidgetItem(text: string): 
        Create a new table widget item with text

        """
        QtGui.QTableWidgetItem.__init__(self, text)
