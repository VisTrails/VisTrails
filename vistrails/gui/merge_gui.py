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
from __future__ import division

from PyQt4 import QtGui, QtCore
import os
import vistrails.api

CHOICE_OTHER_ALL = 0
CHOICE_OTHER = 1
CHOICE_RESOLVED = 2
CHOICE_OWN = 3
CHOICE_OWN_ALL = 4

class resolve_tags(QtGui.QWidget):
    def __init__(self, a, b, text, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.value = 4
        self.a = a
        self.b = b
        self.text = text

        self.initUI()

    def initUI(self):

        self.setWindowTitle("Tag conflict!")
        self.move(250, 200)

        # main layout
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # info boxes
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)

        otherLabel = QtGui.QLabel(self)
        otherLabel.setAlignment(QtCore.Qt.AlignHCenter)
        otherLabel.setText("Other version")
        hbox.addWidget(otherLabel)

        ownLabel = QtGui.QLabel(self)
        ownLabel.setAlignment(QtCore.Qt.AlignHCenter)
        ownLabel.setText("Your version")
        hbox.addWidget(ownLabel)

        # tags
        self.tedit = QtGui.QLineEdit(self.text)
        self.tedit.setAlignment(QtCore.Qt.AlignHCenter)
        vbox.addWidget(self.tedit)

        # info boxes
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)

        # info boxes
        vbox1 = QtGui.QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignHCenter)
        hbox.addLayout(vbox1)
        userLabel = QtGui.QLabel(self)
        userLabel.setText("User: " + self.a.db_user)
        vbox1.addWidget(userLabel)
        timeLabel = QtGui.QLabel(self)
        timeLabel.setText("Time: " + str(self.a.db_date))
        vbox1.addWidget(timeLabel)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.setAlignment(QtCore.Qt.AlignHCenter)
        hbox.addLayout(vbox2)
        userLabel = QtGui.QLabel(self)
        userLabel.setText("User: " + self.b.db_user)
        vbox2.addWidget(userLabel)
        timeLabel = QtGui.QLabel(self)
        timeLabel.setText("Time: " + str(self.b.db_date))
        vbox2.addWidget(timeLabel)

        buttons = QtGui.QHBoxLayout()
        vbox.addLayout(buttons)

        self.otherAll = QtGui.QPushButton('Keep other (for all)', self)
        self.connect(self.otherAll, QtCore.SIGNAL('clicked()'), self.setOtherAll)
        buttons.addWidget(self.otherAll)
        self.other = QtGui.QPushButton('Keep other', self)
        self.connect(self.other, QtCore.SIGNAL('clicked()'), self.setOther)
        buttons.addWidget(self.other)
        self.resolve = QtGui.QPushButton('Resolved', self)
        self.connect(self.resolve, QtCore.SIGNAL('clicked()'), self.setResolved)
        buttons.addWidget(self.resolve)
        self.own = QtGui.QPushButton('Keep yours', self)
        self.connect(self.own, QtCore.SIGNAL('clicked()'), self.setOwn)
        buttons.addWidget(self.own)
        self.ownAll = QtGui.QPushButton('Keep yours (for all)', self)
        self.connect(self.ownAll, QtCore.SIGNAL('clicked()'), self.setOwnAll)
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

class resolve_notes(QtGui.QWidget):
    def __init__(self, a, b, text, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.value = 4
        self.a = a
        self.b = b
        self.text = text

        self.initUI()

    def initUI(self):

        self.setWindowTitle("Notes conflict!")
        self.move(250, 200)

        # main layout
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # thumbs layout
        self.tedit = QtGui.QTextEdit(self.text)
        vbox.addWidget(self.tedit)

        buttons = QtGui.QHBoxLayout()
        vbox.addLayout(buttons)

        self.otherAll = QtGui.QPushButton('Keep other (for all)', self)
        self.connect(self.otherAll, QtCore.SIGNAL('clicked()'), self.setOtherAll)
        buttons.addWidget(self.otherAll)
        self.other = QtGui.QPushButton('Keep other', self)
        self.connect(self.other, QtCore.SIGNAL('clicked()'), self.setOther)
        buttons.addWidget(self.other)
        self.resolve = QtGui.QPushButton('Resolved', self)
        self.connect(self.resolve, QtCore.SIGNAL('clicked()'), self.setResolved)
        buttons.addWidget(self.resolve)
        self.own = QtGui.QPushButton('Keep yours', self)
        self.connect(self.own, QtCore.SIGNAL('clicked()'), self.setOwn)
        buttons.addWidget(self.own)
        self.ownAll = QtGui.QPushButton('Keep yours (for all)', self)
        self.connect(self.ownAll, QtCore.SIGNAL('clicked()'), self.setOwnAll)
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

class resolve_thumbs(QtGui.QWidget):
    def __init__(self, a, b, old_tmp_dir, new_tmp_dir, parent=None):
        QtGui.QWidget.__init__(self, parent)

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
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # thumbs layout
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)

        other = QtGui.QVBoxLayout()
        hbox.addLayout(other)
        otherLabel = QtGui.QLabel(self)
        otherLabel.setText("Other version")
        other.addWidget(otherLabel)
        path = os.path.join(self.old_tmp_dir, 'thumbs', self.a.db_value)
        pixmap = QtGui.QPixmap(path)
        thumb1 = QtGui.QLabel(self)
        thumb1.setPixmap(pixmap)
        other.addWidget(thumb1)
        userLabel = QtGui.QLabel(self)
        userLabel.setText("User: " + self.a.db_user)
        other.addWidget(userLabel)
        timeLabel = QtGui.QLabel(self)
        timeLabel.setText("Time: " + str(self.a.db_date))
        other.addWidget(timeLabel)

        own = QtGui.QVBoxLayout()
        hbox.addLayout(own)
        ownLabel = QtGui.QLabel(self)
        ownLabel.setText("Your version")
        own.addWidget(ownLabel)
        path = os.path.join(self.old_tmp_dir, 'thumbs', self.b.db_value)
        pixmap = QtGui.QPixmap(path)
        thumb2 = QtGui.QLabel(self)
        thumb2.setPixmap(pixmap)
        own.addWidget(thumb2)
        userLabel = QtGui.QLabel(self)
        userLabel.setText("User: " + self.b.db_user)
        own.addWidget(userLabel)
        timeLabel = QtGui.QLabel(self)
        timeLabel.setText("Time: " + str(self.b.db_date))
        own.addWidget(timeLabel)

        buttons = QtGui.QHBoxLayout()
        vbox.addLayout(buttons)

        self.otherAll = QtGui.QPushButton('Keep other (for all)', self)
        self.connect(self.otherAll, QtCore.SIGNAL('clicked()'), self.setOtherAll)
        buttons.addWidget(self.otherAll)
        self.other = QtGui.QPushButton('Keep other', self)
        self.connect(self.other, QtCore.SIGNAL('clicked()'), self.setOther)
        buttons.addWidget(self.other)
        self.own = QtGui.QPushButton('Keep yours', self)
        self.connect(self.own, QtCore.SIGNAL('clicked()'), self.setOwn)
        buttons.addWidget(self.own)
        self.ownAll = QtGui.QPushButton('Keep yours (for all)', self)
        self.connect(self.ownAll, QtCore.SIGNAL('clicked()'), self.setOwnAll)
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
            app = QtGui.QApplication([])
            app.exec_()
        return exm.value, exm.text

    @staticmethod
    def resolveNotes(a, b, text):
        exm = resolve_notes(a, b, text)
        exm.show()
        app = vistrails.api.get_builder_window()
        if not app:
            app = QtGui.QApplication([])
            app.exec_()
        return exm.value, exm.text

    @staticmethod
    def resolveThumbs(a, b, old_tmp_dir, new_tmp_dir):
        exm = resolve_thumbs(a, b, old_tmp_dir, new_tmp_dir)
        exm.show()
        app = vistrails.api.get_builder_window()
        if not app:
            app = QtGui.QApplication([])
            app.exec_()
        return exm.value
