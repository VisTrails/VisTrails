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
from gui.common_widgets import QToolWindowInterface

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

        gLayout = QtGui.QGridLayout()
        gLayout.setMargin(0)
        gLayout.setSpacing(5)
        vLayout.addLayout(gLayout)
        
        tagLabel = QtGui.QLabel(' Version &Tag', self)
        gLayout.addWidget(tagLabel, 0, 0, 1, 1)

        self.tagEdit = QtGui.QLineEdit()
        tagLabel.setBuddy(self.tagEdit)
        gLayout.addWidget(self.tagEdit, 0, 1, 1, 1)
        self.tagEdit.setEnabled(False)

        self.tagApply = QtGui.QPushButton('Change')
        gLayout.addWidget(self.tagApply, 0, 2, 1, 1)        
                
        userLabel = QtGui.QLabel(' User', self)
        gLayout.addWidget(userLabel, 1, 0, 1, 1)
        
        self.userEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.userEdit, 1, 1, 1, 2)

        dateLabel = QtGui.QLabel(' Date', self)
        gLayout.addWidget(dateLabel, 2, 0, 1, 1)

        self.dateEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.dateEdit, 2, 1, 1, 2)

        notesTitle = QtGui.QGroupBox('Notes', self)
        notesTitle.setFlat(True)
        vLayout.addWidget(notesTitle)

        self.versionNotes = QVersionNotes()
        vLayout.addWidget(self.versionNotes)
        self.versionNotes.setEnabled(False)

        self.connect(self.tagEdit, QtCore.SIGNAL('returnPressed()'),
                     self.tagChanged)
        self.connect(self.tagApply, QtCore.SIGNAL('clicked(bool)'),
                     self.tagChanged)
        
        self.controller = None
        self.versionNumber = -1

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
        self.tagEdit.setText('')
        self.userEdit.setText('')
        self.dateEdit.setText('')
        

    def tagChanged(self):
        """ tagChanged() -> None
        Update the new tag to vistrail
        
        """
        if self.controller:
            self.controller.updateCurrentTag(str(self.tagEdit.text()))

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
            self.controller.updateNotes(str(self.toPlainText()))
