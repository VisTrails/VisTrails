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
            
