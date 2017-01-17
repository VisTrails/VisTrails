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

from vistrails.core.bundles.pyimport import py_import
import vistrails.core.requirements
from vistrails.gui.modules.source_configure import SourceConfigurationWidget
from PyQt4 import QtCore, QtGui
from vistrails.gui.theme import CurrentTheme

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

def PythonEditor(parent=None):
    try:
        py_import('PyQt4.Qsci', {'linux-debian': 'python-qscintilla2',
                                 'linux-ubuntu': 'python-qscintilla2'}, True)
    except ImportError:
        return OldPythonEditor(parent)
    else:
        return NewPythonEditor(parent)

def NewPythonEditor(parent):
    vistrails.core.requirements.require_python_module('PyQt4.Qsci')
    from PyQt4.Qsci import QsciScintilla, QsciLexerPython
    class _PythonEditor(QsciScintilla):
    
        def __init__(self, parent=None):
            QsciScintilla.__init__(self, parent)
            ## set the default font of the editor
            ## and take the same font for line numbers
            font = CurrentTheme.PYTHON_SOURCE_EDITOR_FONT
            self.setFont(font)
            fm = QtGui.QFontMetrics(font)
        
            ## Line numbers
            # conventionally, margin 0 is for line numbers
            self.setMarginWidth(0, fm.width( "0000" ) + 4)
            self.setMarginLineNumbers(0, True)
            self.setAutoIndent(True)

            ## Edge Mode shows a red vetical bar at 80 chars
            self.setEdgeMode(QsciScintilla.EdgeLine)
            self.setEdgeColumn(80)
            self.setEdgeColor(QtGui.QColor("#CCCCCC"))
        
            ## Folding visual : we will use boxes
            self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        
            ## Braces matching
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
            ## Editing line color
        #    self.setCaretLineVisible(True)
        #    self.setCaretLineBackgroundColor(QtGui.QColor("#CDA869"))
            
            
                    ## Margins colors
            # line numbers margin
            self.setMarginsBackgroundColor(QtGui.QColor("#FFFFFF"))
            self.setMarginsForegroundColor(QtGui.QColor("#000000"))
        
            # folding margin colors (foreground,background)
            self.setFoldMarginColors(QtGui.QColor("#DDDDDD"),QtGui.QColor("#DDDDDD"))
            # do not use tabs
            self.setIndentationsUseTabs(False)
            self.setTabWidth(4)
            self.setTabIndents(True)
        
            ## Choose a lexer
            lexer = QsciLexerPython()
            lexer.setDefaultFont(font)
            lexer.setFont(font)
            self.setLexer(lexer)
        
            # set autocompletion
            self.setAutoCompletionThreshold(2)
            self.setAutoCompletionSource(QsciScintilla.AcsDocument)
            self.setAutoCompletionCaseSensitivity(True)
            self.setAutoCompletionReplaceWord(True)
            self.setAutoCompletionFillupsEnabled(True)
            
        def setPlainText(self, text):
            """ setPlainText(text: str) -> None
            redirect to setText
            
            """
            self.setText(text)
        
        def toPlainText(self):
            """ setPlainText(text: str) -> None
            redirect to self.text()
            
            """
            text = self.text()
            return text.replace('\r\n', '\n').replace('\r', '\n')
    
#        def focusOutEvent(self, event):
#            if self.parent():
#                QtCore.QCoreApplication.sendEvent(self.parent(), event)
#            QsciScintilla.focusOutEvent(self, event)

    return _PythonEditor(parent)

class OldPythonEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
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
            
#    def focusOutEvent(self, event):
#        if self.parent():
#            QtCore.QCoreApplication.sendEvent(self.parent(), event)
#        QtGui.QTextEdit.focusOutEvent(self, event)

class PythonSourceConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, 
                                           PythonEditor, True, True, parent)
