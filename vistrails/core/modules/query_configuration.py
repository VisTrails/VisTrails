###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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

from PyQt4 import QtCore, QtGui
from core.utils import any, expression
from core import system

############################################################################

class QueryWidgetMixin(object):

    def __init__(self, contents=None, query_method=None):
        self._last_contents = contents
        self._last_query_method = query_method

    def update_parent(self):
        new_contents = self.contents()
        new_query_method = self.query_method()
        if (new_contents != self._last_contents or 
            new_query_method != self._last_query_method):
            if self.parent() and hasattr(self.parent(), 'updateMethod'):
                self.parent().updateMethod()
            self._last_contents = new_contents
            self._last_query_method = new_query_method
            self.emit(QtCore.SIGNAL('contentsChanged'), (self,new_contents))

class QUpdateLineEdit(QtGui.QLineEdit):
    def __init__(self, *args, **kwargs):
        QtGui.QLineEdit.__init__(self, *args, **kwargs)
    
    def focusOutEvent(self, event):
        QtGui.QLineEdit.focusOutEvent(self, event)
        self.parent().update_parent()

class StandardQueryWidget(QtGui.QWidget, QueryWidgetMixin):
    def __init__(self, param, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QueryWidgetMixin.__init__(self, param.strValue, param.queryMethod)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        contents = param.strValue
        queryMethod = param.queryMethod

        layout = QtGui.QHBoxLayout()
        self.op_button = QtGui.QToolButton()
        self.op_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.op_button.setArrowType(QtCore.Qt.NoArrow)
        actions = self.get_op_actions()
        action_group = QtGui.QActionGroup(self.op_button)
        for action in actions:
            action.setCheckable(True)
            action_group.addAction(action)
        menu = QtGui.QMenu(self.op_button)
        actions = action_group.actions()
        menu.addActions(actions)
        self.op_button.setMenu(menu)
        if queryMethod is not None:
            for action in actions:
                if str(action.text()) == queryMethod:
                    action.setChecked(True)
                    break
        else:
            actions[0].setChecked(True)
        self.op_button.setText(action_group.checkedAction().text())

        self.line_edit = QUpdateLineEdit()
        self.line_edit.setText(contents)
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.op_button)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

        self.connect(self.line_edit, QtCore.SIGNAL('returnPressed()'),
                     self.update_parent)
        self.connect(self.op_button, QtCore.SIGNAL('triggered(QAction*)'),
                     self.update_action)

    def get_op_actions(self):
        return [QtGui.QAction("==", self),
                QtGui.QAction("!=", self)]

    def contents(self):
        return self.line_edit.text()

    def setContents(self, strValue, silent=True):
        self.line_edit.setText(strValue)
        if not silent:
            self.update_parent()

    def update_action(self, action):
        self.op_button.setText(action.text())
        self.update_parent()

    def query_method(self):
        for action in self.op_button.menu().actions():
            if action.isChecked():
                return str(action.text())

class StringQueryWidget(StandardQueryWidget):
    def __init__(self, param, parent=None):
        StandardQueryWidget.__init__(self, param, parent)
    
    def get_op_actions(self):
        return [QtGui.QAction("*[]*", self),
                QtGui.QAction("==", self),
                QtGui.QAction("=~", self)]

class NumericQueryWidget(StandardQueryWidget):
    def __init__(self, param, parent=None):
        StandardQueryWidget.__init__(self, param, parent)
    
    def get_op_actions(self):
        return [QtGui.QAction("==", self),
                QtGui.QAction("<", self),
                QtGui.QAction(">", self),
                QtGui.QAction("<=", self),
                QtGui.QAction(">=", self)]
