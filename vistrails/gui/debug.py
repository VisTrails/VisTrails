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

################################################################################


class DebugView(QtGui.QDialog):
    """ Class used for debugging QT signals.
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
        self.text = QtGui.QTextEdit('')
#        text.insertPlainText(errorTrace)
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        layout.addWidget(self.text)
        close = QtGui.QPushButton('Close', self)
        close.setFixedWidth(100)
        layout.addWidget(close)
        self.connect(close, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))
#        sp = StackPopup(errorTrace)
#        sp.exec_()

    def watch_signal(self, obj, sig):
        """self.watch_signal(QObject, QSignal) -> None. Connects a debugging
        call to a signal so that every time signal is emitted, it gets
        registered on the log.
        """
        self.connect(obj, sig, self.__debugSignal)

    def __debugSignal(self, *args):
        debug(str(args))

    def write(self, s):
        t = self.text.toPlainText() if self.isVisible() else ''
        self.text.setPlainText(t+s)
        slider = self.text.verticalScrollBar()
        slider.setValue(slider.maximum())
        # show on screen
        if not self.isVisible():
            self.resize(700, 400)
            self.show()

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
