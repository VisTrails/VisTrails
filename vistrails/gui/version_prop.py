###############################################################################
##
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
QVersionThumbs
QVersionMashups

"""
import re
from PyQt4 import QtCore, QtGui
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core import debug
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core.utils import all
from vistrails.core.vistrail.controller import custom_color_key, \
    parse_custom_color
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

class ColorChooserButton(QtGui.QPushButton):
    color_selected = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtGui.QToolButton.__init__(self, parent)
        self.setColor(None)

        self.connect(self, QtCore.SIGNAL('clicked()'), self.changeColor)

    def setColor(self, color, silent=True):
        self.color = color
        if color is not None:
            self.setStyleSheet('ColorChooserButton {'
                               'border: 1px solid black; '
                               'background-color: rgb(%d, %d, %d); }' % (
                               color.red(), color.green(), color.blue()))
        else:
            self.setStyleSheet('ColorChooserButton {'
                               'border: 1px dashed black; }')
        self.update()
        if not silent:
            self.color_selected.emit(self.color)

    def sizeHint(self):
        return QtCore.QSize(20, 20)

    def changeColor(self):
        if self.color is not None:
            self.setColor(None, silent=False)
        else:
            color = QtGui.QColorDialog.getColor(QtCore.Qt.white, self)
            if color.isValid():
                self.setColor(color, silent=False)

################################################################################

class QVersionProp(QtGui.QWidget, QVistrailsPaletteInterface):
    """
    QVersionProp is a widget holding property of a version including
    tagname and notes
    
    """    
    def __init__(self, parent=None):
        """ QVersionProp(parent: QWidget) -> QVersionProp
        Initialize the main layout
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Workflow Info')

        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(2)
        vLayout.setSpacing(2)
        self.setLayout(vLayout)

        gLayout = QtGui.QGridLayout()
        gLayout.setMargin(2)
        gLayout.setSpacing(5)
        gLayout.setColumnMinimumWidth(1,5)
        gLayout.setRowMinimumHeight(0,20)
        gLayout.setRowMinimumHeight(1,20)
        gLayout.setRowMinimumHeight(2,20)
        gLayout.setRowMinimumHeight(3,20)
        vLayout.addLayout(gLayout)
        
        tagLabel = QtGui.QLabel('Tag:', self)
        gLayout.addWidget(tagLabel, 0, 0, 1, 1)

        editLayout = QtGui.QHBoxLayout()
        editLayout.setMargin(2)
        editLayout.setSpacing(2)
        self.tagEdit = QtGui.QLineEdit()
        tagLabel.setBuddy(self.tagEdit)
        editLayout.addWidget(self.tagEdit)
        self.tagEdit.setEnabled(False)
        self.tagEdit.setMinimumHeight(22)

        self.tagReset = QtGui.QToolButton(self)
        self.tagReset.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)))
        self.tagReset.setIconSize(QtCore.QSize(12,12))
        self.tagReset.setAutoRaise(True)
        self.tagReset.setEnabled(False)
        editLayout.addWidget(self.tagReset)

        configuration = get_vistrails_configuration()
        self.use_custom_colors = configuration.check('enableCustomVersionColors')

        if self.use_custom_colors:
            self.customColor = ColorChooserButton(self)
            editLayout.addWidget(self.customColor)
            self.customColor.color_selected.connect(self.custom_color_selected)

        gLayout.addLayout(editLayout, 0, 2, 1, 1)

        userLabel = QtGui.QLabel('User:', self)
        gLayout.addWidget(userLabel, 1, 0, 1, 1)
        
        self.userEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.userEdit, 1, 2, 1, 1)

        dateLabel = QtGui.QLabel('Date:', self)
        gLayout.addWidget(dateLabel, 2, 0, 1, 1)

        self.dateEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.dateEdit, 2, 2, 1, 1)

        idLabel = QtGui.QLabel('ID:', self)
        gLayout.addWidget(idLabel, 3, 0, 1, 1)
        
        self.idEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.idEdit, 3, 2, 1, 1)

        self.notesLabel = QtGui.QLabel('Notes:')
        gLayout.addWidget(self.notesLabel, 4, 0, 1, 1)

        self.versionNotes = QVersionNotes()
        vLayout.addWidget(self.versionNotes)
        self.versionNotes.setEnabled(False)

        self.versionThumbs = QVersionThumbs()
        vLayout.addWidget(self.versionThumbs)
        
        self.versionMashups = QVersionMashups()
        vLayout.addWidget(self.versionMashups)
                
        self.connect(self.tagEdit, QtCore.SIGNAL('editingFinished()'),
                     self.tagFinished)
        self.connect(self.tagEdit, QtCore.SIGNAL('textChanged(QString)'),
                     self.tagChanged)
        self.connect(self.tagReset, QtCore.SIGNAL('clicked()'),
                     self.tagCleared)

        self.controller = None
        self.versionNumber = -1

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None
        Assign the controller to the property page
        
        """
        if self.controller == controller:
            return
        self.controller = controller
        self.versionNotes.controller = controller
        self.versionThumbs.controller = controller
        self.versionMashups.controller = controller
        if controller is not None:
            self.updateVersion(controller.current_version)
        else:
            self.updateVersion(-1)

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None
        Update the property page of the version
        
        """
        self.versionNumber = versionNumber
        self.versionNotes.updateVersion(versionNumber)
        self.versionThumbs.updateVersion(versionNumber)
        self.versionMashups.updateVersion(versionNumber)
        if self.controller:
            if self.use_custom_colors:
                custom_color = self.controller.vistrail.get_action_annotation(
                        versionNumber, custom_color_key)
                if custom_color is not None:
                    try:
                        custom_color = parse_custom_color(custom_color.value)
                        custom_color = QtGui.QColor(*custom_color)
                    except ValueError, e:
                        debug.warning("Version %r has invalid color "
                                      "annotation (%s)" % (versionNumber, e))
                        custom_color = None
                self.customColor.setColor(custom_color)

            if self.controller.vistrail.actionMap.has_key(versionNumber):
                action = self.controller.vistrail.actionMap[versionNumber]
                name = self.controller.vistrail.getVersionName(versionNumber)
                self.tagEdit.setText(name)
                self.userEdit.setText(action.user)
                self.dateEdit.setText(action.date)
                self.idEdit.setText(unicode(action.id))
                self.tagEdit.setEnabled(True)
                return
            else:
                self.tagEdit.setEnabled(False)
                self.tagReset.setEnabled(False)

        self.tagEdit.setText('')
        self.userEdit.setText('')
        self.dateEdit.setText('')
        self.idEdit.setText('')

    def tagFinished(self):
        """ tagFinished() -> None
        Update the new tag to vistrail
        
        """
        if self.controller:
            name = self.controller.vistrail.getVersionName(self.versionNumber)
            currentText = str(self.tagEdit.text())
            if name != currentText:    
                self.controller.update_current_tag(currentText)

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

    def custom_color_selected(self, color):
        if color is not None:
            self.controller.vistrail.set_action_annotation(
                    self.controller.current_version, custom_color_key,
                    '%d,%d,%d' % (color.red(), color.green(), color.blue()))
        else:
            self.controller.vistrail.set_action_annotation(
                    self.controller.current_version, custom_color_key, None)
        self.controller.set_changed(True)
        self.controller.recompute_terse_graph()
        self.controller.invalidate_version_tree()

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
        self.tag_label.setText("Tag:")

        self.tag = QtGui.QLabel()
        self.tag.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.description_label = QtGui.QLabel()
        self.description_label.palette().setBrush(QtGui.QPalette.Text,
                                                  CurrentTheme.VERSION_PROPERTIES_PEN)
        self.description_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.description_label.setText("Action:")

        self.description = QtGui.QLabel()
        self.description.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.user_label = QtGui.QLabel()
        self.user_label.palette().setBrush(QtGui.QPalette.Text,
                                           CurrentTheme.VERSION_PROPERTIES_PEN)
        self.user_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.user_label.setText("User:")

        self.user = QtGui.QLabel()
        self.user.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.date_label = QtGui.QLabel()
        self.date_label.palette().setBrush(QtGui.QPalette.Text,
                                           CurrentTheme.VERSION_PROPERTIES_PEN)
        self.date_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.date_label.setText("Date:")
        
        self.date = QtGui.QLabel()
        self.date.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)

        self.notes_label = QtGui.QLabel()
        self.notes_label.palette().setBrush(QtGui.QPalette.Text,
                                           CurrentTheme.VERSION_PROPERTIES_PEN)
        self.notes_label.setFont(CurrentTheme.VERSION_PROPERTIES_FONT)
        self.notes_label.setText("Notes:")

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
        if self.controller == controller:
            return
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
                self.tag.setText(self.truncate(name))
                self.description.setText(self.truncate(description))
                self.user.setText(self.truncate(action.user))
                self.date.setText(self.truncate(action.date))
                notes = self.controller.vistrail.get_notes(action.id)
                if notes:
                    s = self.convertHtmlToText(notes)
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
        str = re.sub(r"<head>.*</head>", r"", str)
        # Remove all other tags
        str = re.sub(r"<[^>]*>", r"", str)
        # Remove newlines
        str = re.sub(r"\n", r"", str)
        return str

    def truncate(self, str):
        """ truncate(str: string) -> string
        Shorten string to fit in smaller space
        
        """
        if len(str) > 24:
            str = str[:22] + "..."
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
                title = "Notes: "+name
                self.setWindowTitle(title)
            else:
                self.setWindowTitle("Notes")

    def sizeHint(self):
        """ sizeHint() -> QSize
        
        """
        return QtCore.QSize(250,200)
        
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
        layout.setMargin(2)
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

################################################################################
class QVersionMashups(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.versionNumber = None
        self.controller = None
        #label = QtGui.QLabel("Mashups:")
        self.mashupsButton = QtGui.QToolButton()
        self.mashupsButton.setText("Mashups")
        self.mashupsButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.mashupsButton.setArrowType(QtCore.Qt.RightArrow)
        self.mashupsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
#        font = QtGui.QFont("Arial", 11, QtGui.QFont.Normal)
#        font.setItalic(True)
#        self.group = QtGui.QGroupBox()
#        helplabel = QtGui.QLabel("Double-click a mashup to execute it")
#        helplabel.setFont(font)
#        self.mashupsList = QtGui.QListWidget()
#        self.mashupsList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
#        self.mashupsList.itemDoubleClicked.connect(self.mashupDoubleClicked)
#        glayout = QtGui.QVBoxLayout()
#        glayout.setMargin(2)
#        glayout.setSpacing(5)
#        #layout.addWidget(label)
#        glayout.addWidget(self.mashupsList)
#        glayout.addWidget(helplabel)
#        self.group.setLayout(glayout)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(5)
        #layout.addStretch()
        layout.addWidget(self.mashupsButton)
        #layout.addWidget(self.group)
        self.setLayout(layout)
        self.apps = {}
        #self.group.setVisible(False)
        #self.connect(self.mashupsButton, QtCore.SIGNAL("clicked(bool)"),
        #             self.showList)
        
    def createMashupsMenu(self, tagMap):
        tags = tagMap.keys()
        self.mashupsButton.setText("Mashups (%s)"%str(len(tags)))
        #latestversion = mtrail.getLatestVersion()
        mashupsMenu = QtGui.QMenu(self)
        if len(tags) > 0:
            tags.sort()
            for tag in tags:
                action = QtGui.QAction(str(tag), self, 
                                       triggered=self.mashupSelected)
                action.setData(tagMap[tag])
                mashupsMenu.addAction(action)
            self.mashupsButton.setEnabled(True)
        return mashupsMenu
    
#    def showList(self, on):
#        self.group.setVisible(on)
        
    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None

        """
        self.controller = controller

    def updateVersion(self, versionNumber):
        """ updateVersion(versionNumber: int) -> None

        """
        #self.mashupsList.clear()
        
        from vistrails.gui.mashups.mashups_manager import MashupsManager
        from vistrails.gui.mashups.mashups_inspector import QMashupListPanelItem
        getMshptrail = MashupsManager.getMashuptrailforVersionInVistrailController
        if self.controller:
            vistrail = self.controller.vistrail
            if versionNumber in vistrail.actionMap.keys():
                self.mtrail = getMshptrail(self.controller, versionNumber)
                if self.mtrail:
                    tagMap = self.mtrail.getTagMap()
                    self.mashupsButton.setMenu(self.createMashupsMenu(tagMap))
#                    tags = tagMap.keys()
#                    self.mashupsButton.setText("Mashups (%s)"%str(len(tags)))
#                    #latestversion = mtrail.getLatestVersion()
#                    if len(tags) > 0:
#                        tags.sort()
#                        for tag in tags:
#                            item = QMashupListPanelItem(str(tag),
#                                                        tagMap[tag],
#                                                        self.mashupsList)
#                        self.mashupsButton.setEnabled(True)
#                    else:
#                        self.mashupsButton.setEnabled(False)
                else:
                    self.mashupsButton.setText("Mashups (0)")
                    self.mashupsButton.setEnabled(False)
            else:
                self.mashupsButton.setText("Mashups (0)")
                self.mashupsButton.setEnabled(False)
        else:
            self.mashupsButton.setText("Mashups (0)")
            self.mashupsButton.setEnabled(False)
                
    def mashupSelected(self):
        action = self.sender()
        version, ok = action.data()
        self.openMashup(version)

    def openMashup(self, version):
        from vistrails.gui.mashups.mashups_manager import MashupsManager
        item_key = (self.mtrail.id, version)
        if self.apps.has_key(item_key):
            app = self.apps[item_key]
            if app:
                app.activateWindow()
                return
        
        app = MashupsManager.createMashupApp(self.controller, self.mtrail, 
                                             version)
        app.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        app.appWasClosed.connect(self.appWasClosed)
        self.apps[item_key] = app
        app.activateWindow()
        app.raise_()
                
    def appWasClosed(self, app):
        for (k, a) in self.apps.iteritems():
            if a == app:
                self.apps[k] = None
