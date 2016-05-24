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

def TextEditor(parent=None):
    try:
        py_import('PyQt4.Qsci', {'linux-debian': 'python-qscintilla2',
                                 'linux-ubuntu': 'python-qscintilla2'}, True)
    except ImportError:
        return OldTextEditor(parent)
    else:
        return NewTextEditor(parent)

def NewTextEditor(parent):
    vistrails.core.requirements.require_python_module('PyQt4.Qsci')
    from PyQt4.Qsci import QsciScintilla
    class _TextEditor(QsciScintilla):
    
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

    return _TextEditor(parent)

class OldTextEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.formatChanged(None)
        self.setCursorWidth(8)
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
            
class TextConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, 
                                           TextEditor, False, False, parent, False, portName='value')
