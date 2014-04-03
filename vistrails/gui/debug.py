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
import cgi
import logging
from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import get_vistrails_configuration
import vistrails.core.debug
from vistrails.gui.application import get_vistrails_application
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.theme import CurrentTheme
import vistrails.gui.utils
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################


class DebugView(QtGui.QWidget, QVistrailsPaletteInterface):
    """ Class used for showing error messages and
        debugging QT signals.

        Example of usage:
           import gui.debug
           gui.debug.watch_signal(my_signal)
     """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        ui = logging.StreamHandler(debugStream(self.write))
        ui.setFormatter(logging.Formatter(
                '%(levelname)s\n%(asctime)s\n%(message)s'))
        ui.setLevel(logging.DEBUG)
        vistrails.core.debug.DebugPrint.getInstance().logger.addHandler(ui)
        self.setWindowTitle('VisTrails Messages')
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        # top message filter buttons
        filters = QtGui.QHBoxLayout()
        layout.addLayout(filters)

        filterLabel = QtGui.QLabel('Filter:')
        filterLabel.setFixedWidth(40)
        filters.addWidget(filterLabel)

        self.levels = {}
        for i, name in enumerate(('DEBUG', 'INFO', 'WARNING', 'CRITICAL')):
            box = QtGui.QCheckBox(name, self)
            box.setCheckable(True)
            box.setChecked(name != 'DEBUG')
            box.setStyleSheet(
                    'color: %s;\n'
                    'background-color: %s' % (
                    CurrentTheme.DEBUG_COLORS[name].name(),
                    CurrentTheme.DEBUG_FILTER_BACKGROUND_COLOR.name()))
            self.connect(box, QtCore.SIGNAL('toggled(bool)'), self.refresh)
            filters.addWidget(box)
            self.levels[name] = box

        filters.addStretch()

        # message list
        self.list = QtGui.QListWidget()
        self.connect(self.list,
                     QtCore.SIGNAL('currentItemChanged(QListWidgetItem *, QListWidgetItem *)'),
                     self.showMessage)
        layout.addWidget(self.list)

        # message details field
        self.text = QtGui.QTextEdit()
        self.text.setReadOnly(True)
        self.text.hide()
        layout.addWidget(self.text)

        # bottom buttons
        buttons = QtGui.QGridLayout()
        layout.addLayout(buttons)
        leftbuttons = QtGui.QGridLayout()
        buttons.addLayout(leftbuttons, 0, 0, QtCore.Qt.AlignLeft)
        rightbuttons = QtGui.QGridLayout()
        buttons.addLayout(rightbuttons, 0, 1, QtCore.Qt.AlignRight)

        copy = QDockPushButton('Copy &Message', self)
        copy.setToolTip('Copy selected message to clipboard')
        copy.setFixedWidth(125)
        rightbuttons.addWidget(copy, 0, 0)
        self.connect(copy, QtCore.SIGNAL('clicked()'),
                     self.copyMessage)

        copyAll = QDockPushButton('Copy &All', self)
        copyAll.setToolTip('Copy all messages to clipboard (Can be a lot)')
        copyAll.setFixedWidth(125)
        rightbuttons.addWidget(copyAll, 0, 1)
        self.connect(copyAll, QtCore.SIGNAL('clicked()'),
                     self.copyAll)
        self.msg_box = None
        self.itemQueue = []
        self.resize(700, 400)

    def refresh(self):
        for i in xrange(self.list.count()):
            item = self.list.item(i)
            level = item.data(32).split('\n')[0]
            self.list.setItemHidden(item, not self.levels[level].isChecked())

    def copyMessage(self):
        """ copy selected message to clipboard """
        items = self.list.selectedItems()
        if len(items)>0:
            text = items[0].data(32)
            get_vistrails_application().clipboard().setText(text)

    def copyAll(self):
        """ copy all messages to clipboard """
        texts = []
        for i in range(self.list.count()):
            texts.append(self.list.item(i).data(32))
        text = '\n'.join(texts)
        get_vistrails_application().clipboard().setText(text)

    def showMessage(self, item, olditem):
        """ show item data in a messagebox """
        s = item.data(32)
        msgs = s.split('\n')
        msgs = [cgi.escape(i) for i in msgs]
        format = {'INFO': 'Message:',
                  'WARNING': 'Warning message:',
                  'CRITICAL': 'Critical message:'}
        
        text = '<HTML><BODY BGCOLOR="#FFFFFF">'
        text += '<H4>%s</H4>' % format.get(msgs[0], 'Message:')
        text += '<H4>%s<br></H4>' % msgs[3]
        text += '<table border="0">'
        if len(msgs)>4:
            text += '<tr><td>&nbsp;</td><td align=left>%s</td></tr>' % '<br>'.join(msgs[4:])
            text += '<tr><td>&nbsp;</td><td>&nbsp;</td></tr>'
        text += '<tr><td align=right><b>Time:</b></td><td>%s</td></tr>' % msgs[1]
        text += '<tr><td align=right><b>Location:</b></td><td>%s</td></tr>' % msgs[2]
        text += '</table></BODY></HTML>'

        self.text.setHtml(text)
        self.text.show()

    def watch_signal(self, obj, sig):
        """self.watch_signal(QObject, QSignal) -> None. Connects a debugging
        call to a signal so that every time signal is emitted, it gets
        registered on the log.
        """
        self.connect(obj, sig, self.__debugSignal)

    def __debugSignal(self, *args):
        """ Receives debug signal """
        debug(str(args))

    def updateMessageBox(self, item):
        self.currentItem = item
        msg_box = self.msg_box
        # update messagebox with data from item
        s = item.data(32)
        msgs = s.split('\n')
        if msgs[0] == "INFO":
            msg_box.setIcon(QtGui.QMessageBox.Information)
            msg_box.setWindowTitle("Information")
        elif msgs[0] == "WARNING":
            msg_box.setIcon(QtGui.QMessageBox.Warning)
            msg_box.setWindowTitle("Warning")
        elif msgs[0] == "CRITICAL":
            msg_box.setIcon(QtGui.QMessageBox.Critical)
            msg_box.setWindowTitle("Critical error")
        msg_box.setText(msgs[3])

    def showMessageBox(self, item):
        """ Displays the current message in a messagebox
            if a message is already shown the same message is shown again
            but with a "next message"-button
        """
        msg_box = self.msg_box
        if not msg_box or not msg_box.isVisible():
            # create messagebox
            # app segfaults if the handle to the old messagebox is removed
            self.old_msg_box = msg_box
            msg_box = QtGui.QMessageBox(self.parent())
            self.msg_box = msg_box
            msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
            msg_box.setDefaultButton(QtGui.QMessageBox.Ok)
            msg_box.setEscapeButton(QtGui.QMessageBox.Ok)
            msg_box.addButton('&Show Messages', msg_box.RejectRole)
            self.manyButton = None
            self.connect(msg_box,
                         QtCore.SIGNAL('buttonClicked(QAbstractButton *)'),
                         self.messageButtonClicked)
            self.connect(msg_box,
                         QtCore.SIGNAL('rejected()'),
                         self.rejectMessage)
            self.updateMessageBox(item)
        else:
            self.itemQueue.append(item)

        # check queue
        if self.itemQueue:
            # need to set nextmessage-button
            many = len(self.itemQueue)
            text = '&Next Message (%s more)' % many
            if not self.manyButton:
                # create button
                self.manyButton=QtGui.QPushButton(text)
                msg_box.addButton(self.manyButton, msg_box.DestructiveRole)
            else:
                self.manyButton.setText(text)
        else:
            # remove button if it exist
            if self.manyButton:
                msg_box.removeButton(self.manyButton)
                self.manyButton = None
        if not msg_box.isVisible():
            msg_box.show()
        msg_box.resize(msg_box.sizeHint())
        msg_box.updateGeometry()
        msg_box.activateWindow()
        msg_box.raise_()

    def messageButtonClicked(self, button):
        role = self.msg_box.buttonRole(button)
        if role == self.msg_box.RejectRole:
            self.itemQueue = []
            self.set_visible(True)
            self.list.setCurrentItem(self.currentItem)
            self.list.scrollToItem(self.currentItem)
        elif role == self.msg_box.DestructiveRole:
            # show next message
            item = self.itemQueue[0]
            del self.itemQueue[0]
            self.showMessageBox(item)
        else:
            self.itemQueue = []
        
    def write(self, s):
        """write(s) -> None
        adds the string s to the message list and displays it
        """
        # adds the string s to the list and 
        s = s.strip()
        msgs = s.split('\n')

        if len(msgs)<=3:
            msgs.append('Error logging message: invalid log format')
            s += '\n' + msgs[3]
        if not len(msgs[3].strip()):
            msgs[3] = "Unknown Error"
            s = '\n'.join(msgs)
        text = msgs[3]
        item = QtGui.QListWidgetItem(text)
        item.setData(32, s)
        item.setFlags(item.flags()&~QtCore.Qt.ItemIsEditable)
        self.list.addItem(item)
        item.setForeground(CurrentTheme.DEBUG_COLORS[msgs[0]])
        self.list.setItemHidden(item, not self.levels[msgs[0]].isChecked())
        alwaysShowDebugPopup = getattr(get_vistrails_configuration(),
                                       'showDebugPopups',
                                       False)
        if msgs[0] == 'CRITICAL':
            if self.isVisible() and not alwaysShowDebugPopup:
                self.raise_()
                self.activateWindow()
                modal = get_vistrails_application().activeModalWidget()
                if modal:
                    # need to beat modal window
                    self.showMessageBox(item)
            else:
                self.showMessageBox(item)

    def closeEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the dialog is about to close."""
        self.emit(QtCore.SIGNAL("messagesView(bool)"), False)

    def showEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the dialog is about to close."""
        self.emit(QtCore.SIGNAL("messagesView(bool)"), True)

    def reject(self):
        """ Captures Escape key and closes window correctly """
        self.close()

    def rejectMessage(self):
        """ Captures Escape key and closes messageBox correctly """
        self.itemQueue = []
        self.msg_box.close()

class debugStream(object):
    def __init__(self, write):
        self._write = write

    def write(self, *args, **kwargs):
        return self._write(*args, **kwargs)

def watch_signal(obj, sig):
    DebugView.getInstance().watch_signal(obj, sig)


critical     = vistrails.core.debug.critical
warning      = vistrails.core.debug.warning
log          = vistrails.core.debug.log
debug        = vistrails.core.debug.debug

class TestDebugView(vistrails.gui.utils.TestVisTrailsGUI):

    def test_messages(self):
        debugview = DebugView.instance()
        # test message types
        examples = ["INFO\ntime\nplace\nShort test message\n"
                    "Full test message\nmulti-line",
                    "INFO\ntime\nplace\nShort test message only",
                    "INFO\ntime\nplace\n", # empty message
                    "INFO\ntime\nplace" # no message
                    ]
        examples += ["%s\ntime\nplace\nShort test message\nFull test message"\
                     % m for m in ['INFO', 'WARNING', 'CRITICAL', 'DEBUG']]
        for m in examples:
            debugview.write(m)
            item = debugview.list.item(debugview.list.count()-1)
            debugview.showMessageBox(item)
        # test message copying
        debugview.copyMessage()
        debugview.copyAll()
        # test button toggling
        debugview.levels['INFO'].setChecked(False)
        debugview.levels['INFO'].setChecked(True)
        debugview.levels['WARNING'].setChecked(False)
        debugview.levels['WARNING'].setChecked(True)
        debugview.levels['CRITICAL'].setChecked(False)
        debugview.levels['CRITICAL'].setChecked(True)
