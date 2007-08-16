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
""" This file describe a widget for keeping version notes,info and tag
name

QVersionProp
QVersionNotes
"""

from PyQt4 import QtCore, QtGui
from core.query.version import SearchCompiler, SearchParseError, TrueSearch
from gui.theme import CurrentTheme
from gui.common_widgets import QToolWindowInterface
from gui.common_widgets import QSearchBox
from core.utils import all

################################################################################

class QVersionProp(QtGui.QWidget, QToolWindowInterface):
    """
    QVersionProp is a widget holding property of a version including
    tagname and notes
    
    """    
    def __init__(self, parent=None):
        """ QVersionProp(parent: QWidget) -> QVersionProp
        Initialize the main layout
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Properties')

        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(5)
        self.setLayout(vLayout)

        self.searchBox = QSearchBox(self)
        vLayout.addWidget(self.searchBox)
        
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
        self.tagReset.setIcon(CurrentTheme.VIEW_MANAGER_CLOSE_ICON)
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

        self.notesLabel = QtGui.QLabel('Notes:')
        gLayout.addWidget(self.notesLabel, 3, 0, 1, 1)

        self.versionNotes = QVersionNotes()
        vLayout.addWidget(self.versionNotes)
        self.versionNotes.setEnabled(False)

        self.connect(self.tagEdit, QtCore.SIGNAL('editingFinished()'),
                     self.tagFinished)
        self.connect(self.tagEdit, QtCore.SIGNAL('textChanged(QString)'),
                     self.tagChanged)
        self.connect(self.tagReset, QtCore.SIGNAL('clicked()'),
                     self.tagCleared)
        self.connect(self.searchBox, QtCore.SIGNAL('resetSearch()'),
                     self.resetSearch)
        self.connect(self.searchBox, QtCore.SIGNAL('executeSearch(QString)'),
                     self.executeSearch)
        self.connect(self.searchBox, QtCore.SIGNAL('refineMode(bool)'),
                     self.refineMode)

        self.controller = None
        self.versionNumber = -1
        self.refineMode(False)

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None
        Assign the controller to the property page
        
        """
        self.controller = controller
        self.versionNotes.controller = controller

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None
        Update the property page of the version
        
        """
        self.versionNumber = versionNumber
        self.versionNotes.updateVersion(versionNumber)
        
        if self.controller:
            if self.controller.vistrail.actionMap.has_key(versionNumber):
                action = self.controller.vistrail.actionMap[versionNumber]
                name = self.controller.vistrail.getVersionName(versionNumber)
                self.tagEdit.setText(name)
                self.userEdit.setText(action.user)
                self.dateEdit.setText(action.date)
                self.tagEdit.setEnabled(True)
                return
            else:
                self.tagEdit.setEnabled(False)
                self.tagReset.setEnabled(False)
        self.tagEdit.setText('')
        self.userEdit.setText('')
        self.dateEdit.setText('')
        

    def tagFinished(self):
        """ tagFinished() -> None
        Update the new tag to vistrail
        
        """
        if self.controller:
            self.controller.updateCurrentTag(str(self.tagEdit.text()))

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
        
    def resetSearch(self):
        """
        resetSearch() -> None

        """
        if self.controller:
            self.controller.setSearch(None)
    
    def executeSearch(self, text):
        """
        executeSearch(text: QString) -> None

        """
        s = str(text)
        if self.controller:
            try:
                search = SearchCompiler(s).searchStmt
            except SearchParseError, e:
                QtGui.QMessageBox.warning(self,
                                          QtCore.QString("Search Parse Error"),
                                          QtCore.QString(str(e)),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.NoButton,
                                          QtGui.QMessageBox.NoButton)
                search = None
            self.controller.setSearch(search, s)

    def refineMode(self, on):
        """
        refineMode(on: bool) -> None
        
        """
        if self.controller:
            self.controller.setRefine(on)

class QVersionNotes(QtGui.QTextEdit):
    """
    QVersionNotes is text widget that update/change a version notes
    
    """    
    def __init__(self, parent=None):
        """ QVersionNotes(parent: QWidget) -> QVersionNotes
        Initialize control variables
        
        """
        QtGui.QTextEdit.__init__(self, parent)
        self.controller = None
        self.versionNumber = -1

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None
        Update the text to be the notes of the vistrail versionNumber
        
        """
        self.versionNumber = versionNumber
        if self.controller:
            if self.controller.vistrail.actionMap.has_key(versionNumber):
                action = self.controller.vistrail.actionMap[versionNumber]
                if action.notes:
                    self.setHtml(action.notes)
                    # work around a strange bug where an empty new paragraph gets added every time
                    self.trim_first_paragraph()
                else:
                    self.setHtml('')
                self.setEnabled(True)
                return
            else:
                self.setEnabled(False)
        self.setPlainText('')

    def focusOutEvent(self, event):
        """ focusOutEvent(event: QFocusEvent) -> None
        Update the version notes if the text has been modified
        
        """
        if self.controller and self.document().isModified():
            self.controller.updateNotes(str(self.toHtml()))

    def trim_first_paragraph(self):
        doc = self.document()
        count = doc.blockCount()
        cursor = QtGui.QTextCursor(doc)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        sel = cursor.selection().toPlainText()
        if all(sel, lambda c: c == ' '):
            cursor.removeSelectedText()
            cursor = QtGui.QTextCursor(doc)
            cursor.deleteChar()
