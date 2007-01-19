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
""" This file describe a widget for search and refine the version tree

QVersionProp
QVersionNotes
"""

from PyQt4 import QtCore, QtGui
from core.query.version import SearchCompiler, SearchParseError, TrueSearch
from gui.common_widgets import QToolWindowInterface

################################################################################

class QVersionSearch(QtGui.QWidget, QToolWindowInterface):
    """
    QVersionSearch is a widget that can perform a search/refine on
    version tree
    
    """    
    def __init__(self, parent=None):
        """ QVersionSearch(parent: QWidget) -> QVersionSearch
        Initialize the main layout
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Search & Refine')

        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)

        searchLabel = QtGui.QLabel(' Query Template', self)
        vLayout.addWidget(searchLabel)

        self.statementEdit = QtGui.QLineEdit()
        searchLabel.setBuddy(self.statementEdit)
        vLayout.addWidget(self.statementEdit)

        hLayout = QtGui.QHBoxLayout()
        hLayout.setMargin(5)
        hLayout.setSpacing(5)
        vLayout.addLayout(hLayout)
        
        self.searchButton = QtGui.QPushButton('Search')
        hLayout.addWidget(self.searchButton)

        self.refineButton = QtGui.QPushButton('Refine')
        hLayout.addWidget(self.refineButton)

        self.resetButton = QtGui.QPushButton('Reset')
        hLayout.addWidget(self.resetButton)


        self.connect(self.statementEdit,
                     QtCore.SIGNAL('returnPressed()'),
                     self.searchButton.click)

        self.connect(self.searchButton,
                     QtCore.SIGNAL('clicked()'),
                     self.search)

        self.connect(self.refineButton,
                     QtCore.SIGNAL('clicked()'),
                     self.refine)

        self.connect(self.resetButton,
                     QtCore.SIGNAL('clicked()'),
                     self.reset)

        self.controller = None

    def search(self):
        """ search() -> None
        Search and update the version tree
        
        """
        if self.controller:
            s = str(self.statementEdit.text())
            try:
                search = SearchCompiler(s).searchStmt
            except SearchParseError, e:
                QtGui.QMessageBox.warning(self,
                                          QtCore.QString("Search Parse Error"),
                                          QtCore.QString(str(e)),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.NoButton,
                                          QtGui.QMessageBox.NoButton)
                search = TrueSearch()
            self.controller.setSearch(search)

    def refine(self):
        """ refine() -> None
        Refine and update the version tree
        
        """
        if self.controller:
            s = str(self.statementEdit.text())
            try:
                search = SearchCompiler(s).searchStmt
            except SearchParseError, e:
                QtGui.QMessageBox.warning(self,
                                          QtCore.QString("Search Parse Error"),
                                          QtCore.QString(str(e)),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.NoButton,
                                          QtGui.QMessageBox.NoButton)
                search = TrueSearch()
            self.controller.setSearch(search, True)

    def reset(self):
        """ reset() -> None
        Reset the version tree to include everything
        
        """
        if self.controller:
            self.controller.setSearch(None)
            
