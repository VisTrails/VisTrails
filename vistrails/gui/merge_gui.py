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


from vistrails.gui.qt import QtGui, QtCore, QtWidgets

import os
import vistrails.api

CHOICE_OTHER_ALL = 0
CHOICE_OTHER = 1
CHOICE_RESOLVED = 2
CHOICE_OWN = 3
CHOICE_OWN_ALL = 4

class resolve_tags(QtWidgets.QWidget):
    def __init__(self, a, b, text, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.value = 4
        self.a = a
        self.b = b
        self.text = text

        self.initUI()

    def initUI(self):

        self.setWindowTitle("Tag conflict!")
        self.move(250, 200)

        # main layout
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # info boxes
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        otherLabel = QtWidgets.QLabel(self)
        otherLabel.setAlignment(QtCore.Qt.AlignHCenter)
        otherLabel.setText("Other version")
        hbox.addWidget(otherLabel)

        ownLabel = QtWidgets.QLabel(self)
        ownLabel.setAlignment(QtCore.Qt.AlignHCenter)
        ownLabel.setText("Your version")
        hbox.addWidget(ownLabel)

        # tags
        self.tedit = QtWidgets.QLineEdit(self.text)
        self.tedit.setAlignment(QtCore.Qt.AlignHCenter)
        vbox.addWidget(self.tedit)

        # info boxes
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        # info boxes
        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignHCenter)
        hbox.addLayout(vbox1)
        userLabel = QtWidgets.QLabel(self)
        userLabel.setText("User: " + self.a.db_user)
        vbox1.addWidget(userLabel)
        timeLabel = QtWidgets.QLabel(self)
        timeLabel.setText("Time: " + str(self.a.db_date))
        vbox1.addWidget(timeLabel)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.setAlignment(QtCore.Qt.AlignHCenter)
        hbox.addLayout(vbox2)
        userLabel = QtWidgets.QLabel(self)
        userLabel.setText("User: " + self.b.db_user)
        vbox2.addWidget(userLabel)
        timeLabel = QtWidgets.QLabel(self)
        timeLabel.setText("Time: " + str(self.b.db_date))
        vbox2.addWidget(timeLabel)

        buttons = QtWidgets.QHBoxLayout()
        vbox.addLayout(buttons)

        self.otherAll = QtWidgets.QPushButton('Keep other (for all)', self)
        self.otherAll.clicked.connect(self.setOtherAll)
        buttons.addWidget(self.otherAll)
        self.other = QtWidgets.QPushButton('Keep other', self)
        self.other.clicked.connect(self.setOther)
        buttons.addWidget(self.other)
        self.resolve = QtWidgets.QPushButton('Resolved', self)
        self.resolve.clicked.connect(self.setResolved)
        buttons.addWidget(self.resolve)
        self.own = QtWidgets.QPushButton('Keep yours', self)
        self.own.clicked.connect(self.setOwn)
        buttons.addWidget(self.own)
        self.ownAll = QtWidgets.QPushButton('Keep yours (for all)', self)
        self.ownAll.clicked.connect(self.setOwnAll)
        buttons.addWidget(self.ownAll)

    def setOtherAll(self):
        self.value = CHOICE_OTHER_ALL
        self.close()
    def setOther(self):
        self.value = CHOICE_OTHER
        self.close()
    def setResolved(self):
        self.value = CHOICE_RESOLVED
        self.text = str(self.tedit.text())
        self.close()
    def setOwn(self):
        self.value = CHOICE_OWN
        self.close()
    def setOwnAll(self):
        self.value = CHOICE_OWN_ALL
        self.close()

class resolve_notes(QtWidgets.QWidget):
    def __init__(self, a, b, text, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.value = 4
        self.a = a
        self.b = b
        self.text = text

        self.initUI()

    def initUI(self):

        self.setWindowTitle("Notes conflict!")
        self.move(250, 200)

        # main layout
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # thumbs layout
        self.tedit = QtWidgets.QTextEdit(self.text)
        vbox.addWidget(self.tedit)

        buttons = QtWidgets.QHBoxLayout()
        vbox.addLayout(buttons)

        self.otherAll = QtWidgets.QPushButton('Keep other (for all)', self)
        self.otherAll.clicked.connect(self.setOtherAll)
        buttons.addWidget(self.otherAll)
        self.other = QtWidgets.QPushButton('Keep other', self)
        self.other.clicked.connect(self.setOther)
        buttons.addWidget(self.other)
        self.resolve = QtWidgets.QPushButton('Resolved', self)
        self.resolve.clicked.connect(self.setResolved)
        buttons.addWidget(self.resolve)
        self.own = QtWidgets.QPushButton('Keep yours', self)
        self.own.clicked.connect(self.setOwn)
        buttons.addWidget(self.own)
        self.ownAll = QtWidgets.QPushButton('Keep yours (for all)', self)
        self.ownAll.clicked.connect(self.setOwnAll)
        buttons.addWidget(self.ownAll)

    def setOtherAll(self):
        self.value = CHOICE_OTHER_ALL
        self.close()
    def setOther(self):
        self.value = CHOICE_OTHER
        self.close()
    def setResolved(self):
        self.value = CHOICE_RESOLVED
        self.text = str(self.tedit.toHtml())
        self.close()
    def setOwn(self):
        self.value = CHOICE_OWN
        self.close()
    def setOwnAll(self):
        self.value = CHOICE_OWN_ALL
        self.close()

class resolve_thumbs(QtWidgets.QWidget):
    def __init__(self, a, b, old_tmp_dir, new_tmp_dir, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.value = 4
        self.a = a
        self.b = b

        self.old_tmp_dir = old_tmp_dir
        self.new_tmp_dir = new_tmp_dir
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Thumbnail conflict!")
        self.move(250, 200)

        # main layout
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # thumbs layout
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        other = QtWidgets.QVBoxLayout()
        hbox.addLayout(other)
        otherLabel = QtWidgets.QLabel(self)
        otherLabel.setText("Other version")
        other.addWidget(otherLabel)
        path = os.path.join(self.old_tmp_dir, 'thumbs', self.a.db_value)
        pixmap = QtGui.QPixmap(path)
        thumb1 = QtWidgets.QLabel(self)
        thumb1.setPixmap(pixmap)
        other.addWidget(thumb1)
        userLabel = QtWidgets.QLabel(self)
        userLabel.setText("User: " + self.a.db_user)
        other.addWidget(userLabel)
        timeLabel = QtWidgets.QLabel(self)
        timeLabel.setText("Time: " + str(self.a.db_date))
        other.addWidget(timeLabel)

        own = QtWidgets.QVBoxLayout()
        hbox.addLayout(own)
        ownLabel = QtWidgets.QLabel(self)
        ownLabel.setText("Your version")
        own.addWidget(ownLabel)
        path = os.path.join(self.old_tmp_dir, 'thumbs', self.b.db_value)
        pixmap = QtGui.QPixmap(path)
        thumb2 = QtWidgets.QLabel(self)
        thumb2.setPixmap(pixmap)
        own.addWidget(thumb2)
        userLabel = QtWidgets.QLabel(self)
        userLabel.setText("User: " + self.b.db_user)
        own.addWidget(userLabel)
        timeLabel = QtWidgets.QLabel(self)
        timeLabel.setText("Time: " + str(self.b.db_date))
        own.addWidget(timeLabel)

        buttons = QtWidgets.QHBoxLayout()
        vbox.addLayout(buttons)

        self.otherAll = QtWidgets.QPushButton('Keep other (for all)', self)
        self.otherAll.clicked.connect(self.setOtherAll)
        buttons.addWidget(self.otherAll)
        self.other = QtWidgets.QPushButton('Keep other', self)
        self.other.clicked.connect(self.setOther)
        buttons.addWidget(self.other)
        self.own = QtWidgets.QPushButton('Keep yours', self)
        self.own.clicked.connect(self.setOwn)
        buttons.addWidget(self.own)
        self.ownAll = QtWidgets.QPushButton('Keep yours (for all)', self)
        self.ownAll.clicked.connect(self.setOwnAll)
        buttons.addWidget(self.ownAll)

    def setOtherAll(self):
        self.value = CHOICE_OTHER_ALL
        self.close()
    def setOther(self):
        self.value = CHOICE_OTHER
        self.close()
    def setOwn(self):
        self.value = CHOICE_OWN
        self.close()
    def setOwnAll(self):
        self.value = CHOICE_OWN_ALL
        self.close()

class MergeGUI(object):
    @staticmethod
    def resolveTags(a, b, text):
        exm = resolve_tags(a, b, text)
        exm.show()
        app = vistrails.api.get_builder_window()
        if not app:
            app = QtWidgets.QApplication([])
            app.exec_()
        return exm.value, exm.text

    @staticmethod
    def resolveNotes(a, b, text):
        exm = resolve_notes(a, b, text)
        exm.show()
        app = vistrails.api.get_builder_window()
        if not app:
            app = QtWidgets.QApplication([])
            app.exec_()
        return exm.value, exm.text

    @staticmethod
    def resolveThumbs(a, b, old_tmp_dir, new_tmp_dir):
        exm = resolve_thumbs(a, b, old_tmp_dir, new_tmp_dir)
        exm.show()
        app = vistrails.api.get_builder_window()
        if not app:
            app = QtWidgets.QApplication([])
            app.exec_()
        return exm.value
