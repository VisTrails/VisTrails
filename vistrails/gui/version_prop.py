###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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
##  - Neither the name of the University of Utah nor the names of its 
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
""" This file describe a widget for keeping version notes,info and tag
name

QVersionProp
QVersionNotes
QVersionPropOverlay
QExpandButton
QNotesDialog
"""
import os.path
from PyQt4 import QtCore, QtGui
from core.query.version import SearchCompiler, SearchParseError, TrueSearch
from core.thumbnails import ThumbnailCache
from gui.theme import CurrentTheme
from gui.common_widgets import QToolWindowInterface
from gui.common_widgets import QSearchBox
from core.utils import all
from core import debug

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

        self.searchBox = QSearchBox(True, False, self)
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

        self.notesLabel = QtGui.QLabel('Notes:')
        gLayout.addWidget(self.notesLabel, 3, 0, 1, 1)

        self.versionNotes = QVersionNotes()
        vLayout.addWidget(self.versionNotes)
        self.versionNotes.setEnabled(False)

        self.versionThumbs = QVersionThumbs()
        vLayout.addWidget(self.versionThumbs)
        
        eLayout = QtGui.QVBoxLayout()
        self.versionEmbedBtn = QtGui.QPushButton("Embed")
        eLayout.addWidget(self.versionEmbedBtn)
        self.versionEmbedBtn.setEnabled(False)
        self.versionEmbedBtn.setMinimumHeight(20)
        self.versionEmbedBtn.setSizePolicy(QtGui.QSizePolicy(
                                                       QtGui.QSizePolicy.Fixed,
                                                       QtGui.QSizePolicy.Fixed))
        self.versionEmbedBtn.setToolTip("Get workflow embed code")
        vLayout.addLayout(eLayout)
        
        self.versionEmbedPanel = QVersionEmbed(self)
        self.versionEmbedPanel.setVisible(False)
        
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
        self.connect(self.versionEmbedBtn, QtCore.SIGNAL('clicked()'),
                     self.showEmbedPanel)

        self.controller = None
        self.versionNumber = -1
        self.refineMode(False)

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None
        Assign the controller to the property page
        
        """
        self.controller = controller
        self.versionNotes.controller = controller
        self.versionEmbedPanel.controller = controller
        self.versionThumbs.controller = controller

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None
        Update the property page of the version
        
        """
        self.versionNumber = versionNumber
        self.versionNotes.updateVersion(versionNumber)
        self.versionThumbs.updateVersion(versionNumber)
        self.versionEmbedPanel.updateVersion(versionNumber)
        if self.controller:
            if self.controller.vistrail.actionMap.has_key(versionNumber):
                action = self.controller.vistrail.actionMap[versionNumber]
                name = self.controller.vistrail.getVersionName(versionNumber)
                self.tagEdit.setText(name)
                self.userEdit.setText(action.user)
                self.dateEdit.setText(action.date)
                self.tagEdit.setEnabled(True)
                self.versionEmbedBtn.setEnabled(versionNumber > 0)
                if versionNumber == 0:
                    self.versionEmbedPanel.hide()
                return
            else:
                self.tagEdit.setEnabled(False)
                self.tagReset.setEnabled(False)
                self.versionEmbedBtn.setEnabled(False)
                self.versionEmbedPanel.hide()
                
        self.tagEdit.setText('')
        self.userEdit.setText('')
        self.dateEdit.setText('')
        

    def tagFinished(self):
        """ tagFinished() -> None
        Update the new tag to vistrail
        
        """
        if self.controller:
            name = self.controller.vistrail.getVersionName(self.versionNumber)
            currentText = str(self.tagEdit.text())
            if name != currentText:    
                self.controller.update_current_tag(currentText)
                self.versionEmbedPanel.updateVersion(self.versionNumber)

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
        
    def resetSearch(self, emit_signal=True):
        """
        resetSearch() -> None

        """
        if self.controller and emit_signal:
            self.controller.set_search(None)
            self.emit(QtCore.SIGNAL('textQueryChange(bool)'), False)
        else:
            self.searchBox.clearSearch()
    
    def executeSearch(self, text):
        """
        executeSearch(text: QString) -> None

        """
        s = str(text)
        if self.controller:
            try:
                search = SearchCompiler(s).searchStmt
            except SearchParseError, e:
                debug.warning("Search Parse Error", str(e))
                search = None
            self.controller.set_search(search, s)
            self.emit(QtCore.SIGNAL('textQueryChange(bool)'), s!='')

    def refineMode(self, on):
        """
        refineMode(on: bool) -> None
        
        """
        if self.controller:
            self.controller.set_refine(on)
            
    def showEmbedPanel(self):
        self.versionEmbedPanel.show()

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
        self.update_on_focus_out = True
        self.setAcceptRichText(False)
        # Reset text to black, for some reason it is grey by default on the mac
        self.palette().setBrush(QtGui.QPalette.Text,
                                QtGui.QBrush(QtGui.QColor(0,0,0,255)))
        

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None
        Update the text to be the notes of the vistrail versionNumber
        
        """
        self.versionNumber = versionNumber
        if self.controller:
            if self.controller.vistrail.actionMap.has_key(versionNumber):
                action = self.controller.vistrail.actionMap[versionNumber]
                notes = self.controller.vistrail.get_notes(versionNumber)
                if notes:
                    self.setHtml(notes)
                    # work around a strange bug where an empty new paragraph gets added every time
                    self.trim_first_paragraph()
                else:
                    self.setHtml('')
                self.setEnabled(True)
                return
            else:
                self.setEnabled(False)
        self.setPlainText('')

    def commit_changes(self):
        if self.controller and self.document().isModified():
            self.controller.update_notes(str(self.toHtml()))

    def reset_changes(self):
        """ reset_changes() -> None

        """
        self.updateVersion(self.versionNumber)

    def focusOutEvent(self, event):
        """ focusOutEvent(event: QFocusEvent) -> None
        Update the version notes if the text has been modified
        
        """
        if self.update_on_focus_out:
            self.commit_changes()
        QtGui.QTextEdit.focusOutEvent(self,event)

    def trim_first_paragraph(self):
        doc = self.document()
        count = doc.blockCount()
        cursor = QtGui.QTextCursor(doc)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        sel = cursor.selection().toPlainText()
        if all(c == ' ' for c in sel):
            cursor.removeSelectedText()
            cursor = QtGui.QTextCursor(doc)
            cursor.deleteChar()


################################################################################
class QVersionPropOverlay(QtGui.QFrame):
    """
    QVersionPropOverlay is a transparent widget that sits on top of the version
    view.  It displays properties of a version: tag, user, date, and notes.

    """
    propagatingEvent = set([
        QtCore.QEvent.MouseButtonDblClick,
        QtCore.QEvent.MouseButtonPress,
        QtCore.QEvent.MouseButtonRelease,
        QtCore.QEvent.MouseMove,
        QtCore.QEvent.Wheel,
        ])
    def __init__(self, parent=None, mouseWidget=None):
        """ QVersionPropOverlay(parent: QWidget) -> QVersionPropOverlay
        Setup layout

        """
        QtGui.QFrame.__init__(self, parent)
        self.propagatingWidget = mouseWidget
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(0,0,0,0))
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.layout = QtGui.QGridLayout()
        self.layout.setVerticalSpacing(1)

        self.tag_label = QtGui.QLabel()
        self.tag_label.palette().setBrush(QtGui.QPalette.Text,
                                          CurrentTheme.VERSION_PROPERTIES_PEN)
        self.tag_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.tag_label.setText(QtCore.QString("Tag:"))

        self.tag = QtGui.QLabel()
        self.tag.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.description_label = QtGui.QLabel()
        self.description_label.palette().setBrush(QtGui.QPalette.Text,
                                                  CurrentTheme.VERSION_PROPERTIES_PEN)
        self.description_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.description_label.setText(QtCore.QString("Action:"))

        self.description = QtGui.QLabel()
        self.description.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.user_label = QtGui.QLabel()
        self.user_label.palette().setBrush(QtGui.QPalette.Text,
                                           CurrentTheme.VERSION_PROPERTIES_PEN)
        self.user_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.user_label.setText(QtCore.QString("User:"))

        self.user = QtGui.QLabel()
        self.user.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.date_label = QtGui.QLabel()
        self.date_label.palette().setBrush(QtGui.QPalette.Text,
                                           CurrentTheme.VERSION_PROPERTIES_PEN)
        self.date_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.date_label.setText(QtCore.QString("Date:"))
        
        self.date = QtGui.QLabel()
        self.date.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.notes_label = QtGui.QLabel()
        self.notes_label.palette().setBrush(QtGui.QPalette.Text,
                                           CurrentTheme.VERSION_PROPERTIES_PEN)
        self.notes_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.notes_label.setText(QtCore.QString("Notes:"))

        self.notes = QtGui.QLabel()
        self.notes.setTextFormat(QtCore.Qt.PlainText)
        self.notes.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        
        self.notes_button = QExpandButton()
        self.notes_button.hide()

        self.notes_layout = QtGui.QHBoxLayout()
        self.notes_layout.addWidget(self.notes)
        self.notes_layout.addWidget(self.notes_button)
        self.notes_layout.addStretch()

        self.layout.addWidget(self.tag_label, 0, 0)
        self.layout.addWidget(self.tag, 0, 1)
        self.layout.addWidget(self.description_label, 1, 0)
        self.layout.addWidget(self.description, 1, 1)
        self.layout.addWidget(self.user_label, 2, 0)
        self.layout.addWidget(self.user, 2, 1)
        self.layout.addWidget(self.date_label, 3, 0)
        self.layout.addWidget(self.date, 3, 1)
        self.layout.addWidget(self.notes_label, 4, 0)
        self.layout.addLayout(self.notes_layout, 4, 1)

        self.layout.setColumnMinimumWidth(0,35)
        self.layout.setColumnMinimumWidth(1,200)
        self.layout.setContentsMargins(2,2,2,2)
        self.layout.setColumnStretch(1,1)
        self.setLayout(self.layout)
        self.updateGeometry()
        self.controller = None
        
        self.notes_dialog = QNotesDialog(self)
        self.notes_dialog.hide()

        QtCore.QObject.connect(self.notes_button,
                               QtCore.SIGNAL("pressed()"),
                               self.openNotes)

    def updateGeometry(self):
        """ updateGeometry() -> None
        Keep in upper left of screen

        """
        parentGeometry = self.parent().geometry()
        self.pos_x = 4
        self.pos_y = 4
        self.move(self.pos_x, self.pos_y)

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None
        Assign the controller to the properties
        
        """
        self.controller = controller
        self.notes_dialog.updateController(controller)

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None
        Update the text items
        
        """
        self.notes_dialog.updateVersion(versionNumber)
        if self.controller:
            if self.controller.vistrail.actionMap.has_key(versionNumber):
                action = self.controller.vistrail.actionMap[versionNumber]
                name = self.controller.vistrail.getVersionName(versionNumber)
                description = self.controller.vistrail.get_description(versionNumber)
                self.tag.setText(self.truncate(QtCore.QString(name)))
                self.description.setText(self.truncate(QtCore.QString(description)))
                self.user.setText(self.truncate(QtCore.QString(action.user)))
                self.date.setText(self.truncate(QtCore.QString(action.date)))
                notes = self.controller.vistrail.get_notes(action.id)
                if notes:
                    s = self.convertHtmlToText(QtCore.QString(notes))
                    self.notes.setText(self.truncate(s))
                else:
                    self.notes.setText('')
                self.notes_button.show()
            else:
                self.tag.setText('')
                self.description.setText('')
                self.user.setText('')
                self.date.setText('')
                self.notes.setText('')
                self.notes_button.hide()

    def convertHtmlToText(self, str):
        """ convertHtmlToText(str: QString) -> QString
        Remove HTML tags and newlines
        
        """
        # Some text we want to ignore lives outside brackets in the header
        str.replace(QtCore.QRegExp("<head>.*</head>"), "")
        # Remove all other tags
        str.replace(QtCore.QRegExp("<[^>]*>"), "")
        # Remove newlines
        str.replace(QtCore.QRegExp("\n"), " ")
        return str

    def truncate(self, str):
        """ truncate(str: QString) -> QString
        Shorten string to fit in smaller space
        
        """
        if (str.size() > 24):
            str.truncate(22)
            str.append("...")
        return str

    def openNotes(self):
        """ openNotes() -> None

        Show notes dialog
        """
        self.notes_dialog.show()
        self.notes_dialog.activateWindow()

    def event(self, e):
        """ Propagate all mouse events to the right widget """
        if e.type() in self.propagatingEvent:
            if self.propagatingWidget!=None:
                QtCore.QCoreApplication.sendEvent(self.propagatingWidget, e)
                return False
        return QtGui.QFrame.event(self, e)

################################################################################
class QExpandButton(QtGui.QLabel):
    """
    A transparent button type with a + draw in 
    """
    def __init__(self, parent=None):
        """
        QExpandButton(parent: QWidget) -> QExpandButton
        """
        QtGui.QLabel.__init__(self, parent)
        
        self.drawButton(0)
        self.setToolTip('Edit Notes')
        self.setScaledContents(False)
        self.setFrameShape(QtGui.QFrame.NoFrame)

    def sizeHint(self):
        """ sizeHint() -> QSize
        
        """
        return QtCore.QSize(10,10)
        

    def mousePressEvent(self, e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Capture mouse press event on the frame to move the widget
        
        """
        if e.buttons() & QtCore.Qt.LeftButton:
            self.drawButton(1)
    
    def mouseReleaseEvent(self, e):
        self.drawButton(0)
        self.emit(QtCore.SIGNAL('pressed()'))

    def drawButton(self, down):
        """ drawButton(down: bool) -> None
        Custom draw function
        
        """
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter()
        painter.begin(self.picture)
        painter.setRenderHints(QtGui.QPainter.Antialiasing, False)
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidth(1)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        if (down):
            pen.setColor(QtGui.QColor(150,150,150,150))
        else:
            pen.setColor(QtGui.QColor(0,0,0,255))

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(0,0,8,8)
        painter.drawLine(QtCore.QLine(4,2,4,6))
        painter.drawLine(QtCore.QLine(2,4,6,4))
        painter.end()
        self.setPicture(self.picture)

################################################################################
class QNotesDialog(QtGui.QDialog):
    """
    A small non-modal dialog with text entry to modify and view notes

    """
    def __init__(self, parent=None):
        """
        QNotesDialog(parent: QWidget) -> QNotesDialog

        """
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.notes = QVersionNotes(self)
        self.notes.update_on_focus_out = False
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.notes)
        layout.setMargin(0)

        self.apply_button = QtGui.QPushButton('Apply', self)
        self.apply_button.setDefault(False)
        self.apply_button.setAutoDefault(False)
        self.ok_button = QtGui.QPushButton('Ok', self)
        self.ok_button.setDefault(False)
        self.ok_button.setAutoDefault(False)
        self.cancel_button = QtGui.QPushButton('Cancel', self)
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        self.buttonLayout = QtGui.QHBoxLayout()
        layout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.apply_button)
        self.buttonLayout.addWidget(self.ok_button)
        self.buttonLayout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.controller = None

        QtCore.QObject.connect(self.apply_button,
                               QtCore.SIGNAL("released()"),
                               self.apply_pressed)

        QtCore.QObject.connect(self.ok_button,
                               QtCore.SIGNAL("released()"),
                               self.ok_pressed)

        QtCore.QObject.connect(self.cancel_button,
                               QtCore.SIGNAL("released()"),
                               self.cancel_pressed)
    def apply_pressed(self):
        """ apply_pressed() -> None

        """
        self.notes.commit_changes()

    def ok_pressed(self):
        """ ok_pressed() -> None
        
        """
        self.notes.commit_changes()
        self.close()

    def cancel_pressed(self):
        """ cancel_pressed() -> None
        
        """
        self.notes.reset_changes()
        self.close()

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None

        """
        self.controller = controller
        self.notes.controller = controller

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None

        """
        self.notes.updateVersion(versionNumber)
        if self.controller:
            if self.controller.vistrail.actionMap.has_key(versionNumber):
                name = self.controller.vistrail.getVersionName(versionNumber)
                title = QtCore.QString("Notes: "+name)
                self.setWindowTitle(title)
            else:
                self.setWindowTitle("Notes")

    def sizeHint(self):
        """ sizeHint() -> QSize
        
        """
        return QtCore.QSize(250,200)
        
################################################################################
class QVersionEmbed(QtGui.QWidget):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, 
                               f | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Embed Options')
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.versionNumber = None
        self.versionTag = ''
        label1 = QtGui.QLabel("Embed:")
        self.cbcontent = QtGui.QComboBox()
        self.cbcontent.setEditable(False)
        items = QtCore.QStringList()
        items << "Workflow Results" << "Workflow Graph" << "History Tree Graph";
        self.cbcontent.addItems(items)
        label2 = QtGui.QLabel("In")
        
        self.cbtype = QtGui.QComboBox()
        self.cbtype.setEditable(False)
        items = QtCore.QStringList()
        items << "Wiki" << "Latex" << "Shared Memory";
        self.cbtype.addItems(items)
        
        self.controller = None
        self.pptag = 'Image(s) from (%s,%s,%s,%s,%s)'
        
        #options
        self.gbEmbedOpt = QtGui.QGroupBox("Embed Options")
        self.chbPdf = QtGui.QCheckBox("As PDF")
        self.chbSmartTag = QtGui.QCheckBox("Smart Tag")
        self.chbCache = QtGui.QCheckBox("Cache Images")
        self.chbLatexVTL = QtGui.QCheckBox("Include .vtl")
        self.chbLatexVTL.setVisible(False)
        
        gblayout = QtGui.QGridLayout()
        gblayout.addWidget(self.chbPdf, 0, 0)
        gblayout.addWidget(self.chbSmartTag, 0, 1)
        gblayout.addWidget(self.chbCache, 0, 2)
        gblayout.addWidget(self.chbLatexVTL, 1, 0)
        self.gbEmbedOpt.setLayout(gblayout)
        
        self.gbDownOpt = QtGui.QGroupBox("Download Options")
        self.chbWorkflow = QtGui.QCheckBox("Include Workflow")
        self.chbFullTree = QtGui.QCheckBox("Include Full Tree")
        self.chbFullTree.setEnabled(False)
        self.chbExecute = QtGui.QCheckBox("Execute Workflow")
        self.chbSpreadsheet = QtGui.QCheckBox("Show Spreadsheet Only")
        
        gblayout = QtGui.QGridLayout()
        gblayout.addWidget(self.chbWorkflow, 0, 0)
        gblayout.addWidget(self.chbFullTree, 0, 1)
        gblayout.addWidget(self.chbExecute, 1, 0)
        gblayout.addWidget(self.chbSpreadsheet, 1, 1)
        self.gbDownOpt.setLayout(gblayout)
        
        self.embededt = QtGui.QTextEdit(self)
        self.embededt.setAcceptRichText(False)
        self.embededt.setReadOnly(False)
        self.exportHtml = '<a href="export">Export...</a>'
        self.copyHtml = '<a href="copy">Copy to Clipboard</a>'
        self.copylabel = QtGui.QLabel(self.copyHtml)
        self.copylabel.setCursor(QtCore.Qt.PointingHandCursor)
        
        label3 = QtGui.QLabel("After making your selection, click on 'Copy To \
Clipboard'. The code changes based on your selection.")
        label3.setWordWrap(True)
        
        font = QtGui.QFont("Arial", 10, QtGui.QFont.Normal)
        font.setItalic(True)
        label3.setFont(font)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(label1,0,0)
        layout.addWidget(self.cbcontent,0,1)
        layout.addWidget(label2,1,0)
        layout.addWidget(self.cbtype,1,1)
        layout.addWidget(self.gbEmbedOpt,2,0,1,-1)
        layout.addWidget(self.gbDownOpt,3,0,1,-1)
        layout.addWidget(self.copylabel,4,1,QtCore.Qt.AlignRight)
        layout.addWidget(self.embededt,5,0,1,-1)
        layout.addWidget(label3,6,0,1,-1)
        layout.setColumnStretch(1, 1)
        
        self.setLayout(layout)
        
        #connect signals
        self.connect(self.cbtype,
                     QtCore.SIGNAL("activated(const QString &)"),
                     self.changeEmbedType)
        
        self.connect(self.copylabel,
                     QtCore.SIGNAL("linkActivated(const QString &)"),
                     self.linkActivated)
        
        self.connect(self.cbcontent,
                     QtCore.SIGNAL("activated(const QString &)"),
                     self.changeOption)
        
        optlist = [self.cbcontent,
                   self.chbPdf,
                   self.chbSmartTag,
                   self.chbCache,
                   self.chbLatexVTL,
                   self.chbWorkflow,
                   self.chbFullTree,
                   self.chbExecute,
                   self.chbSpreadsheet]
        for cb in optlist:
            self.connect(cb, QtCore.SIGNAL("toggled(bool)"),
                         self.changeOption)
        #special cases
        self.connect(self.chbWorkflow, QtCore.SIGNAL("toggled(bool)"),
                     self.changeIncludeWorkflow)
        self.connect(self.chbSpreadsheet, QtCore.SIGNAL("toggled(bool)"),
                     self.changeShowSpreadsheet)
        self.connect(self.chbExecute, QtCore.SIGNAL("toggled(bool)"),
                     self.changeExecute)
        self.connect(self.cbcontent,
                     QtCore.SIGNAL("activated(const QString &)"),
                     self.changeContent)
        self.connect(self.chbSmartTag, QtCore.SIGNAL("toggled(bool)"),
                     self.changeSmartTag)
        self.connect(self.chbCache, QtCore.SIGNAL("toggled(bool)"),
                     self.changeCache)
        
    def closeEvent(self,e):
        """ closeEvent(e: QCloseEvent) -> None
        Doesn't allow the Legend widget to close, but just hide
        instead
        
        """
        e.ignore()
        self.hide()
    
    def focusInEvent(self, event):
        if self.controller:
            if self.controller.locator:
                app = QtGui.QApplication.instance()
                if hasattr(app, 'builderWindow'):
                    manager = app.builderWindow.viewManager
                    manager.ensureVistrail(self.controller.locator)
                    
                    
    def checkLocator(self):
        """checkLocator() -> bool
        Only vistrails on a database are allowed to embed a tag"""
        result = False
        if self.controller:
            if self.controller.locator:
                title = "Embed Options for %s"%self.controller.locator.name
                self.setWindowTitle(title)
                result = True
        return result

    def checkControllerStatus(self):
        """checkControllerStatus() -> bool
        this checks if the controller has saved the latest changes """
        result = False
        if self.controller:
            result = not self.controller.changed
        return result
    
    def updateEmbedText(self):
        ok = (self.checkLocator() and self.checkControllerStatus() and
              self.versionNumber > 0)
        self.embededt.setEnabled(ok)
        self.copylabel.setEnabled(ok)
        self.embededt.setText('')

        if self.controller and self.versionNumber > 0:
            if self.controller.locator and not self.controller.changed:
                loc = self.controller.locator
                if hasattr(loc,'host'):
                    self.updateCbtype('db')    
                elif hasattr(loc, 'name'):
                    self.updateCbtype('file')
                        
                if self.versionTag != "":
                    self.chbSmartTag.setEnabled(True)
                else:
                    self.chbSmartTag.setChecked(False)
                    self.chbSmartTag.setEnabled(False)
                    
                self.setEmbedText()
            elif self.controller.changed:
                self.embededt.setPlainText('You must save your vistrail to proceed')
            else:
                self.embededt.setPlainText('')
                
    def setEmbedText(self):
        #check options
        options = {}
        options['content'] = str(self.cbcontent.currentText())
        options['pdf'] = self.chbPdf.isChecked()
        options['smartTag'] = self.chbSmartTag.isChecked()
        options['buildalways'] = not self.chbCache.isChecked()
        options['includeWorkflow'] = self.chbWorkflow.isChecked()
        options['includeFullTree'] = self.chbFullTree.isChecked()
        options['execute'] = self.chbExecute.isChecked()
        options['showspreadsheetonly'] = self.chbSpreadsheet.isChecked()
        
        if self.cbtype.currentText() == "Wiki":
            text = self.buildWikiTag(options)
        elif self.cbtype.currentText() == "Latex":
            options['getvtl'] = self.chbLatexVTL.isChecked()
            text = self.buildLatexCommand(options)
        elif text == "Shared Memory":
            text = self.pptag
        self.embededt.setPlainText(text)
            
    def updateVersion(self, versionNumber):
        self.versionNumber = versionNumber
        if versionNumber > 0:
            self.versionTag = self.controller.vistrail.getVersionName(self.versionNumber)
        self.updateEmbedText()

    def linkActivated(self, link):
        if link=='copy':
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(self.embededt.toPlainText())
        elif link=='export':
            app = QtCore.QCoreApplication.instance()
            app.builderWindow.interactiveExportCurrentPipeline()
    
    def changeEmbedType(self, text):
        if text!='Shared Memory':
            self.copylabel.setText(self.copyHtml)
        else:
            self.copylabel.setText(self.exportHtml)
        self.chbLatexVTL.setVisible(text == 'Latex')
        self.chbPdf.setEnabled(text == 'Latex')
        self.setEmbedText()  
        
    def changeOption(self, value):
        self.setEmbedText()
        
    def changeContent(self, text):
        if text == "Workflow Results":
            self.chbExecute.setEnabled(True)
            self.chbSpreadsheet.setEnabled(True)
            self.chbCache.setEnabled(True)
            self.chbSmartTag.setEnabled(True)
        else:
            self.chbExecute.setChecked(False)
            self.chbSpreadsheet.setChecked(False)
            self.chbExecute.setEnabled(False)
            self.chbSpreadsheet.setEnabled(False)
            if text == "History Tree Graph":
                self.chbCache.setChecked(False)
                self.chbCache.setEnabled(False)
                self.chbSmartTag.setChecked(False)
                self.chbSmartTag.setEnabled(False)
            else:
                self.chbCache.setEnabled(True)
                self.chbSmartTag.setEnabled(True)
                
    def updateCbtype(self, type):
        currentText = self.cbtype.currentText()
        self.cbtype.clear()
        items = QtCore.QStringList()
        if type == 'db':
            items << "Wiki" << "Latex" << "Shared Memory";
        elif type == 'file':
            items << "Latex";
        self.cbtype.addItems(items)
        index = items.indexOf(currentText)
        if index > 0:
            self.cbtype.setCurrentIndex(index)
        text = str(self.cbtype.currentText())
        self.chbLatexVTL.setVisible(text == 'Latex')
        self.chbPdf.setEnabled(text == 'Latex')
            
    def buildLatexCommand(self, options):
        text = '\\vistrail['
        loc = self.controller.locator
        if hasattr(loc, 'host'):
            text += 'host=%s,\ndb=%s,\nport=%s,\nvtid=%s,\n'% (loc.host,
                                                               loc.db,
                                                               loc.port,
                                                               loc.obj_id)
        else:
            text += 'filename=%s,\n' % os.path.basename(loc.name)
        if options['content'] != "History Tree Graph":    
            text += 'version=%s,\n'%self.versionNumber
            if options['smartTag']:
                text += 'tag={%s},\n'%self.versionTag
        if options['pdf']:
            text += 'pdf,\n'
        if options['buildalways']:
            text+= 'buildalways,\n'
        if options['getvtl']:
            text += 'getvtl,\n'
        if options['includeWorkflow']:
            text+= 'embedworkflow,\n'
            if options['includeFullTree']:
                text += 'includefulltree,\n'
        if options['content'] == "Workflow Graph":
            text += 'showworkflow,\n'
        elif options['content'] == "History Tree Graph":
            text += 'showtree,\n'
        else:
            if options['execute']:
                text += 'execute,\n'
            if options['showspreadsheetonly']:
                text += 'showspreadsheetonly,\n'
        
        text = text[0:-2] + "]{}"
        return text        

    def buildWikiTag(self, options):
        text = '<vistrail '
        loc = self.controller.locator
        
        text += 'host="%s" db="%s" port="%s" vtid="%s" '% (loc.host,
                                                            loc.db,
                                                            loc.port,
                                                            loc.obj_id)
        if options['content'] != "History Tree Graph":
            text += 'version="%s" '%self.versionNumber
            if options['smartTag']:
                text += 'tag="%s " '%self.versionTag
        if options['buildalways']:
            text+= 'buildalways="True" '
        if options['includeWorkflow']:
            text+= 'embedworkflow="True" '
            if options['includeFullTree']:
                text += 'includefulltree="True" '
        if options['content'] == "Workflow Graph":
            text += 'showworkflow="True" ' #"Workflow Results" << "Workflow Graph" << "History Tree Graph";
        elif options['content'] == "History Tree Graph":
            text += 'showtree="True" '
        else:
            if options['execute']:
                text += 'execute="True" '
            if options['showspreadsheetonly']:
                text += 'showspreadsheetonly="True" '
        
        text += "/>"
        return text        

    def changeIncludeWorkflow(self,checked):
        self.chbFullTree.setEnabled(checked)
        if self.cbcontent.currentText() == "History Tree Graph":
            self.chbFullTree.setChecked(checked)
        
    def changeShowSpreadsheet(self, checked):
        if checked:
            self.chbExecute.setChecked(True)
            
    def changeExecute(self, checked):
        if not checked:
            self.chbSpreadsheet.setChecked(False)
            
    def changeSmartTag(self, checked):
        if checked and self.cbtype.currentText() == 'Latex':
            self.chbCache.setChecked(False)
            
    def changeCache(self, checked):
        if checked and self.cbtype.currentText() == 'Latex':
            self.chbSmartTag.setChecked(False)
################################################################################

class QVersionThumbs(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.versionNumber = None
        label = QtGui.QLabel("Preview:")
        self.thumbs = QtGui.QLabel()
        self.thumbs.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setFrameStyle(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidget(self.thumbs)
        self.scrollArea.setWidgetResizable(True)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.addWidget(label)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)
        self.controller = None
        
    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None

        """
        self.controller = controller
        
    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None

        """
        if self.controller:
            vistrail = self.controller.vistrail
            if versionNumber in vistrail.actionMap.keys():
                action = vistrail.actionMap[versionNumber]
                if action and vistrail.has_thumbnail(action.id):
                    cache = ThumbnailCache.getInstance()
                    fname = cache.get_abs_name_entry(
                        vistrail.get_thumbnail(action.id))
                    if fname is not None:
                        pixmap = QtGui.QPixmap(fname)
                        self.thumbs.setPixmap(pixmap)
                        self.thumbs.adjustSize()
                    self.thumbs.setFrameShape(QtGui.QFrame.StyledPanel)
                    return
                
        self.thumbs.setPixmap(QtGui.QPixmap())
        self.thumbs.setFrameShape(QtGui.QFrame.NoFrame)
