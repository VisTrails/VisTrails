# Simulates a Python shell inside a Qt Widget.
# Based on PyCute: http://gerard.vermeulen.free.fr/
# PyCute is a Python shell for PyQt.
#
#    Creating, displaying and controlling PyQt widgets from the Python command
#    line interpreter is very hard, if not, impossible.  PyCute solves this
#    problem by interfacing the Python interpreter to a PyQt widget.
#
#    My use is interpreter driven plotting to QwtPlot instances. Why?
#    
#    Other popular scientific software packages like SciPy, SciLab, Octave,
#    Maple, Mathematica, GnuPlot, ..., also have interpreter driven plotting.  
#    It is well adapted to quick & dirty exploration. 
#
#    Of course, PyQt's debugger -- eric -- gives you similar facilities, but
#    PyCute is smaller and easier to integrate in applications.
#    Eric requires Qt-3.x
#
#    PyCute is based on ideas and code from:
#    - Python*/Tools/idle/PyShell.py (Python Software Foundation License)
#    - PyQt*/eric/Shell.py (Gnu Public License)

from PyQt4 import QtGui, QtCore
from code import InteractiveInterpreter
import core.system
import copy
import os
import sys

class ShellGui(QtGui.QDialog):
    def __init__(self, parent, builder=None):
        QtGui.QDialog.__init__(self, parent)
        self.builder = builder
        self.setWindowTitle("VisTrails Shell")
        
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setLayout(layout)
        #locals() returns the original dictionary, not a copy as
        #the docs say
        self.firstLocals = copy.copy(locals())
        
        self.shell = VisShell(locals(),None)
        self.layout().addWidget(self.shell)
        self.resize(600,400)
        self.createMenu()
    
    def createMenu(self):
        self.newSessionAct = QtGui.QAction(self.tr("&Restart"),self)
        self.newSessionAct.setShortcut(self.tr("Ctrl+R"))
        self.connect(self.newSessionAct, QtCore.SIGNAL("triggered()"),self.newSession)

        self.saveSessionAct = QtGui.QAction(self.tr("&Save"), self)
        self.saveSessionAct.setShortcut(self.tr("Ctrl+S"))
        self.connect(self.saveSessionAct, QtCore.SIGNAL("triggered()"),self.saveSession)

        self.closeSessionAct = QtGui.QAction(self.tr("Close"), self)
        self.closeSessionAct.setShortcut(self.tr("Ctrl+W"))
        self.connect(self.closeSessionAct,QtCore.SIGNAL("triggered()"), self.closeSession)
        
        self.menuBar = QtGui.QMenuBar(self)
        menu = self.menuBar.addMenu(self.tr("&Session"))
        menu.addAction(self.newSessionAct)
        menu.addAction(self.saveSessionAct)
        menu.addAction(self.closeSessionAct)

        self.layout().setMenuBar(self.menuBar)

    def closeEvent(self, e):
        self.closeSession()
    
    def showEvent(self, e):
        self.shell.show()
        QtGui.QDialog.showEvent(self,e)

    def closeSession(self):
        self.shell.hide()
        self.hide()

    def newSession(self):
        self.shell.restart(copy.copy(self.firstLocals))

    def saveSession(self):
        import time
        import os.path

        default = 'visTrails' + '-' + time.strftime("%Y%m%d-%H%M.log")
        default = os.path.join(system.vistrailsDirectory(),default)
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Save Session As..",
                                                     default,
                                                     "Log files (*.log)")
        if not fileName:
            return

        self.shell.saveSession(str(fileName))

        
class VisShell(QtGui.QTextEdit):
    def __init__(self, locals=None, parent=None):
        """Constructor.

        The optional 'locals' argument specifies the dictionary in
        which code will be executed; it defaults to a newly created
        dictionary with key "__name__" set to "__console__" and key
        "__doc__" set to None.

        The optional 'log' argument specifies the file in which the
        interpreter session is to be logged.
        
        The optional 'parent' argument specifies the parent widget.
        If no parent widget has been specified, it is possible to
        exit the interpreter by Ctrl-D.

        """

        QtGui.QTextEdit.__init__(self, parent)
        self.setReadOnly(False)
        
        # to exit the main interpreter by a Ctrl-D if VisShell has no parent
        if parent is None:
            self.eofKey = QtCore.Qt.Key_D
        else:
            self.eofKey = None

        self.interpreter = None
        # storing current state
        self.prev_stdout = sys.stdout
        self.prev_stdin = sys.stdin
        self.prev_stderr = sys.stderr

        # capture all interactive input/output
        sys.stdout   = self
        sys.stderr   = self
        sys.stdin    = self

        self.reset(locals)
        
        # user interface setup
        
        self.setAcceptRichText(False)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        
        # font
        if system.systemType == 'Linux':
            font = QtGui.QFont("Fixed", 12)
        elif system.systemType in ['Windows', 'Microsoft']:
            font = QtGui.QFont("Courier New", 8)
        elif system.systemType == 'Darwin':
            font = QtGui.QFont("Monaco", 12)
        else:
            raise SystemExit, "FIXME for 'os2', 'ce' or 'riscos'"
        font.setFixedPitch(1)
        self.setCurrentFont(font)

        # interpreter prompt.
        if hasattr(sys, "ps1"):
            sys.ps1
        else:
            sys.ps1 = ">>> "
        if hasattr(sys, "ps2"):
            sys.ps2
        else:
            sys.ps2 = "... "
        
        # interpreter banner
        
        self.write('VisTrails shell running Python %s on %s.\n' %
                   (sys.version, sys.platform))
        self.write('Type "copyright", "credits" or "license"'
                   ' for more information on Python.\n')
        self.write(sys.ps1)

    def reset(self, locals):
        if self.interpreter:
            del self.interpreter
        self.interpreter = InteractiveInterpreter(locals)
         # last line + last incomplete lines
        self.line    = QtCore.QString()
        self.lines   = []
        # the cursor position in the last line
        self.point   = 0
        # flag: the interpreter needs more input to run the last lines. 
        self.more    = 0
        # flag: readline() is being used for e.g. raw_input() and input()
        self.reading = 0
        # history
        self.history = []
        self.pointer = 0
        self.last   = 0

    def flush(self):
        """
        Simulate stdin, stdout, and stderr.
        """
        pass

    def isatty(self):
        """
        Simulate stdin, stdout, and stderr.
        """
        return 1

    def readline(self):
        """
        Simulate stdin, stdout, and stderr.
        """
        self.reading = 1
        self.__clearLine()
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)
      
        while self.reading:
            qApp.processOneEvent()
        if self.line.length() == 0:
            return '\n'
        else:
            return str(self.line) 
    
    def write(self, text):
        """
        Simulate stdin, stdout, and stderr.
        """
                
        self.append(text)
        cursor = self.textCursor()
        self.last = cursor.position()
        
    def writelines(self, text):
        """
        Simulate stdin, stdout, and stderr.
        """
        map(self.write, text)
        print "DO WE EVER GET HERE? IF YES, OPTIMIZATION POSSIBLE"

    def fakeUser(self, lines):
        """
        Simulate a user: lines is a sequence of strings, (Python statements).
        """
        for line in lines:
            self.line = QtCore.QString(line.rstrip())
            self.write(self.line)
            self.__run()
            
    def __run(self):
        """
        Append the last line to the history list, let the interpreter execute
        the last line(s), and clean up accounting for the interpreter results:
        (1) the interpreter succeeds
        (2) the interpreter fails, finds no errors and wants more line(s)
        (3) the interpreter fails, finds errors and writes them to sys.stderr
        """
        self.pointer = 0
        self.history.append(QtCore.QString(self.line))
        self.lines.append(str(self.line))
        source = '\n'.join(self.lines)
        self.more = self.interpreter.runsource(source)
        if self.more:
            self.write(sys.ps2)
        else:
            self.write(sys.ps1)
            self.lines = []
        self.__clearLine()
        
    def __clearLine(self):
        """
        Clear input line buffer
        """
        self.line.truncate(0)
        self.point = 0
        
    def __insertText(self, text):
        """
        Insert text at the current cursor position.
        """
        self.insertPlainText(text)
        self.line.insert(self.point, text)
        self.point += text.length()
        
    def keyPressEvent(self, e):
        """
        Handle user input a key at a time.
        """
        text  = e.text()
        key   = e.key()
        if not text.isEmpty():
            ascii = ord(str(text))
        else:
            ascii = -1
        if text.length() and ascii>=32 and ascii<127:
            self.__insertText(text)
            return

        if e.modifiers() & QtCore.Qt.MetaModifier and key == self.eofKey:
            self.hide()
        
        if e.modifiers() & QtCore.Qt.ControlModifier or e.modifiers() & QtCore.Qt.ShiftModifier:
            e.ignore()
            return

        if key == QtCore.Qt.Key_Backspace:
            if self.point:
                QtGui.QTextEdit.keyPressEvent(self, e)
                self.point -= 1
                self.line.remove(self.point, 1)
        elif key == QtCore.Qt.Key_Delete:
            QtGui.QTextEdit.keyPressEvent(self, e)
            self.line.remove(self.point, 1)
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if self.reading:
                self.reading = 0
            else:
                self.__run()
        elif key == QtCore.Qt.Key_Tab:
            self.__insertText(text)
        elif key == QtCore.Qt.Key_Left:
            if self.point:
                QtGui.QTextEdit.keyPressEvent(self, e)
                self.point -= 1
        elif key == QtCore.Qt.Key_Right:
            if self.point < self.line.length():
                QtGui.QTextEdit.keyPressEvent(self, e)
                self.point += 1
        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.setPosition(cursor.position() + 4)
            self.setTextCursor(cursor)
            self.point = 0
        elif key == QtCore.Qt.Key_End:
            QtGui.QTextEdit.keyPressEvent(self, e)
            self.point = self.line.length()
        elif key == QtCore.Qt.Key_Up:
            if len(self.history):
                if self.pointer == 0:
                    self.pointer = len(self.history)
                self.pointer -= 1
                self.__recall()
        elif key == QtCore.Qt.Key_Down:
            if len(self.history):
                self.pointer += 1
                if self.pointer == len(self.history):
                    self.pointer = 0
                self.__recall()
        else:
            e.ignore()

    def __recall(self):
        """
        Display the current item from the command history.
        """
        cursor = self.textCursor()
        cursor.setPosition(self.last)
        
        cursor.select(QtGui.QTextCursor.LineUnderCursor)

        cursor.removeSelectedText()
        self.setTextCursor(cursor)
        self.insertPlainText(sys.ps1)
        self.__clearLine()
        self.__insertText(self.history[self.pointer])

        
    def focusNextPrevChild(self, next):
        """
        Suppress tabbing to the next window in multi-line commands. 
        """
        if next and self.more:
            return 0
        return QtGui.QTextEdit.focusNextPrevChild(self, next)

    def mousePressEvent(self, e):
        """
        Keep the cursor after the last prompt.
        """
        if e.button() == QtCore.Qt.LeftButton:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            self.setTextCursor(cursor)
        return

    def hide(self):
        #recovering the state
        sys.stdout   = self.prev_stdout
        sys.stderr   = self.prev_stderr
        sys.stdin    = self.prev_stdin

    def show(self):
        # storing current state
        self.prev_stdout = sys.stdout
        self.prev_stdin = sys.stdin
        self.prev_stderr = sys.stderr

        # capture all interactive input/output
        sys.stdout   = self
        sys.stderr   = self
        sys.stdin    = self

    def saveSession(self, fileName):
        """ Write its contents to a file """
        output = open(str(fileName), 'w')
        output.write(self.toPlainText())
        output.close()

    def restart(self, locals=None):
        self.clear()
        self.reset(locals)
        self.write('VisTrails shell running Python %s on %s.\n' %
                   (sys.version, sys.platform))
        self.write('Type "copyright", "credits" or "license"'
                   ' for more information on Python.\n')
        self.write(sys.ps1)

    def contentsContextMenuEvent(self,ev):
        """
        Suppress the right button context menu.
        """
        return
