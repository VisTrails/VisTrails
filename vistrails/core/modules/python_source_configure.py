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
from core import system
from core.modules.source_configure import SourceConfigurationWidget
from core.utils import PortAlreadyExists
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from gui.theme import CurrentTheme
import urllib

class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__( self, document ):
        QtGui.QSyntaxHighlighter.__init__( self, document )
        self.rules = []
        
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.blue)
        self.rules += [(r"\b%s\b"%w, keywordFormat, -1, -1, False)
                       for w in ["def","from", 
                                 "import","for","in", 
                                 "while","True","None",
                                 "False","pass","return",
                                 "self","tuple","list",
                                 "print","if","else",
                                 "elif","len","string"
                                 "assert","try","except",
                                 "exec", "break", "continue",
                                 "not", "and", "or", "as",
                                 "type", "int", "float",
                                 ]]
        
        defclassFormat = QtGui.QTextCharFormat()
        defclassFormat.setForeground(QtCore.Qt.blue)
        self.rules += [(r"\bclass\b\s*(\w+)", defclassFormat, -1, -1, False)]

        commentFormat = QtGui.QTextCharFormat()
        commentFormat.setFontItalic(True)
        commentFormat.setForeground(QtCore.Qt.darkGreen)
        self.rules += [(r"#[^\n]*", commentFormat, -1, -1, False)]

        literalFormat = QtGui.QTextCharFormat()
        literalFormat.setForeground(QtGui.QColor(65, 105, 225)) #royalblue
        self.rules += [
            # Whole docstring
            (r"'''.*'''", literalFormat, -1, -1, True),
            (r'""".*"""', literalFormat, -1, -1, True),
            # Hanging docstring (single quote)
            (r"'''.*$", literalFormat, -1, 2, False),
            (r"^.*'''", literalFormat, 2, -1, True),
            (r"^.*$", literalFormat, 2, 2, False),
            # Hanging docstring (double quote)
            (r'""".*$', literalFormat, -1, 3, False),
            (r'^.*"""', literalFormat, 3, -1, True),
            (r'^.*$', literalFormat, 3, 3, False),
            # Whole string
            (r"'[^']*'", literalFormat, -1, -1, False),
            (r'"[^"]*"', literalFormat, -1, -1, False),
            # Hanging string (single quote)
            (r"'[^']*$", literalFormat, -1,  0, False),
            (r"^[^']*$", literalFormat,  0,  0, False),
            (r"^[^']*'", literalFormat,  0, -1, False),
            # Hanging string (double quotes)
            (r'"[^"]*$', literalFormat, -1,  1, False),
            (r'^[^"]*$', literalFormat,  1,  1, False),
            (r'^[^"]*"', literalFormat,  1, -1, False),
            ]
        
    def highlightBlock(self, text):
        baseFormat = self.format(0)
        prevState = self.previousBlockState()
        self.setCurrentBlockState(prevState)        
        shift = 0
        while True:
            matchedRule = (None, -1, -1, -1, -1)
            for rule in self.rules:
                if rule[2]==self.currentBlockState():
                    RE = QtCore.QRegExp(rule[0])
                    RE.setMinimal(rule[4])
                    pos = RE.indexIn(text, shift)
                    if (pos!=-1 and (matchedRule[0]==None or pos<matchedRule[1]) and
                        RE.matchedLength()>0):
                        matchedRule = (rule[1], pos, RE.matchedLength(), rule[3])
            if matchedRule[0]!=None:
                self.setFormat(matchedRule[1], matchedRule[2], matchedRule[0])
                self.setCurrentBlockState(matchedRule[3])
                shift = matchedRule[1]+matchedRule[2]
            else:
                break

class PythonEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.formatChanged(None)
        self.setCursorWidth(8)
        self.highlighter = PythonHighlighter(self.document())
        self.connect(self,
                     QtCore.SIGNAL('currentCharFormatChanged(QTextCharFormat)'),
                     self.formatChanged)

    def formatChanged(self, f):
        self.setFont(CurrentTheme.PYTHON_SOURCE_EDITOR_FONT)

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> Nont
        Handle tab with 4 spaces
        
        """
        if event.key()==QtCore.Qt.Key_Tab:
            self.insertPlainText('    ')
        else:
            # super(PythonEditor, self).keyPressEvent(event)
            QtGui.QTextEdit.keyPressEvent(self, event)
            
    def focusOutEvent(self, event):
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QTextEdit.focusOutEvent(self, event)
                 
class PythonSourceConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, 
                                           PythonEditor, True, True, parent)
