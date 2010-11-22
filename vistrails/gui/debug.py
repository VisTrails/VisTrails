############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
from PyQt4 import QtCore, QtGui
import core.debug
import StringIO
import api

################################################################################


class DebugView(QtGui.QDialog):
    """ Class used for showing error messages and
        debugging QT signals.

        Example of usage:
           import gui.debug
           gui.debug.watch_signal(my_signal)
     """
    #Singleton technique
    _instance = None
    class DebugViewSingleton():
        def __call__(self, *args, **kw):
            if DebugView._instance is None:
                obj = DebugView(*args, **kw)
                DebugView._instance = obj
            return DebugView._instance
        
    getInstance = DebugViewSingleton()

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        core.debug.DebugPrint.getInstance().set_stream(debugStream(self.write)) 
        self.setWindowTitle('VisTrails messages')
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.list = QtGui.QListWidget()
        self.connect(self.list,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                     self.showMessage)
        self.msg_box = None
       
#        self.text = QtGui.QTextEdit('')
#        text.insertPlainText(errorTrace)
#        self.text.setReadOnly(True)
#        self.text.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.resize(700, 400)
        layout.addWidget(self.list)
        buttons = QtGui.QHBoxLayout()
        layout.addLayout(buttons)
        close = QtGui.QPushButton('&Hide', self)
        close.setFixedWidth(120)
        buttons.addWidget(close)
        self.connect(close, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
        details = QtGui.QPushButton('&Show details', self)
        details.setFixedWidth(120)
        buttons.addWidget(details)
        self.connect(details, QtCore.SIGNAL('clicked()'),
                     self.details)
        copy = QtGui.QPushButton('Copy &Message', self)
        copy.setToolTip('Copy selected message to clipboard')
        copy.setFixedWidth(120)
        buttons.addWidget(copy)
        self.connect(copy, QtCore.SIGNAL('clicked()'),
                     self.copyMessage)
        copyAll = QtGui.QPushButton('Copy &All', self)
        copyAll.setToolTip('Copy all messages to clipboard (Can be a lot)')
        copyAll.setFixedWidth(120)
        buttons.addWidget(copyAll)
        self.connect(copyAll, QtCore.SIGNAL('clicked()'),
                     self.copyAll)

#        sp = StackPopup(errorTrace)
#        sp.exec_()

    def details(self):
        """ call showMessage on selected message """
        items = self.list.selectedItems()
        if len(items)>0:
            self.showMessage(items[0])
            
    def copyMessage(self):
        """ copy selected message to clipboard """
        items = self.list.selectedItems()
        if len(items)>0:
            text = str(items[0].data(32).toString())
            api.VistrailsApplication.clipboard().setText(text)

    def copyAll(self):
        """ copy selected message to clipboard """

        texts = []
        for i in range(self.list.count()):
            texts.append(str(self.list.item(i).data(32).toString()))
        text = '\n'.join(texts)
        api.VistrailsApplication.clipboard().setText(text)

    def showMessage(self, item):
        """ show item data in a messagebox """
        self.showMessageBox(str(item.data(32).toString()))

    def watch_signal(self, obj, sig):
        """self.watch_signal(QObject, QSignal) -> None. Connects a debugging
        call to a signal so that every time signal is emitted, it gets
        registered on the log.
        """
        self.connect(obj, sig, self.__debugSignal)

    def __debugSignal(self, *args):
        """ Receives debug signal """
        debug(str(args))

    def showMessageBox(self, s):
        s = str(s).strip()
        msgs = s.split('\n')
        if self.msg_box and self.msg_box.isVisible():
            self.msg_box.close()
        msg_box = QtGui.QMessageBox(self.parent())
        self.msg_box = msg_box
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
        text = "Time: %s\n Location: %s\n Message:\n%s" % \
                                            (msgs[1], msgs[2],
                                             '\n'.join(msgs[3:]))
        msg_box.setInformativeText('\n'.join(msgs[4:]))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.setDefaultButton(QtGui.QMessageBox.Ok)
        msg_box.setDetailedText(text)
        msg_box.show()

    def write(self, s):
#        t = self.text.toPlainText() if self.isVisible() else ''
#        self.text.setPlainText(t+s)
        s = str(s).strip()
        msgs = s.split('\n')
        text = msgs[3] if len(msgs)>2 else ''
        if msgs[0] == "CRITICAL":
            self.showMessageBox(s)
        item = QtGui.QListWidgetItem(text)
        item.setData(32, s)
        item.setFlags(item.flags()&~QtCore.Qt.ItemIsEditable)
        if msgs[0] == "INFO":
            item.setForeground(QtGui.QBrush(QtCore.Qt.black))
        elif msgs[0] == "WARNING":
            item.setForeground(QtGui.QBrush(QtGui.QColor("#D0D000")))
        elif msgs[0] == "CRITICAL":
            item.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.list.addItem(item)
        self.list.scrollToItem(item)

    def closeEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the dialog is about to close."""
        self.emit(QtCore.SIGNAL("messagesView(bool)"), False)

    def showEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the dialog is about to close."""
        count = self.list.count()
        if count:
            self.list.scrollToItem(self.list.item(count-1))
        self.emit(QtCore.SIGNAL("messagesView(bool)"), True)

class debugStream(StringIO.StringIO):
    def __init__(self, write):
        StringIO.StringIO.__init__(self)
        self.write = write

def watch_signal(obj, sig):
    DebugView.getInstance().watch_signal(obj, sig)


critical     = core.debug.critical
warning      = core.debug.warning
log          = core.debug.log
debug        = core.debug.debug
