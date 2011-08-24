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

from constant_configuration import StandardConstantWidget, ColorWidget

############################################################################

class QueryWidgetMixin(object):

    def __init__(self, contents=None, query_method=None):
        self._last_contents = contents
        self._last_query_method = query_method

    # updateMethod intercepts calls from a child widget like the
    # contents_widget
    def updateMethod(self):
        self.update_parent()

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

class BaseQueryWidget(QtGui.QWidget, QueryWidgetMixin):
    def __init__(self, contents_klass, query_methods, param, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QueryWidgetMixin.__init__(self, param.strValue, param.queryMethod)

        contents = param.strValue
        queryMethod = param.queryMethod

        layout = QtGui.QHBoxLayout()
        self.op_button = QtGui.QToolButton()
        self.op_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.op_button.setArrowType(QtCore.Qt.NoArrow)
        action_group = QtGui.QActionGroup(self.op_button)
        actions = []
        checked_exists = False
        for method in query_methods:
            action = QtGui.QAction(method, self)
            action.setCheckable(True)
            action_group.addAction(action)
            if method == queryMethod:
                action.setChecked(True)
                checked_exists = True
            actions.append(action)
        if not checked_exists:
            actions[0].setChecked(True)
            self._last_query_method = str(actions[0].text())
            
        menu = QtGui.QMenu(self.op_button)
        menu.addActions(actions)
        self.op_button.setMenu(menu)
        self.op_button.setText(action_group.checkedAction().text())

        self.contents_widget = contents_klass(param)
        self.contents_widget.setContents(contents)

        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.op_button)
        layout.addWidget(self.contents_widget)
        self.setLayout(layout)

        self.connect(self.op_button, QtCore.SIGNAL('triggered(QAction*)'),
                     self.update_action)

    def contents(self):
        return self.contents_widget.contents()

    def setContents(self, strValue, silent=True):
        self.contents_widget.setContents(strValue)
        if not silent:
            self.update_parent()

    def update_action(self, action):
        self.op_button.setText(action.text())
        self.update_parent()

    def query_method(self):
        for action in self.op_button.menu().actions():
            if action.isChecked():
                return str(action.text())

class StandardQueryWidget(BaseQueryWidget):
    def __init__(self, param, parent=None):
        BaseQueryWidget.__init__(self, StandardConstantWidget, ["==", "!="],
                                 param, parent)

class StringQueryWidget(StandardQueryWidget):
    def __init__(self, param, parent=None):
        BaseQueryWidget.__init__(self, StandardConstantWidget, 
                                 ["*[]*", "==", "=~"],
                                 param, parent)
    
class NumericQueryWidget(StandardQueryWidget):
    def __init__(self, param, parent=None):
        BaseQueryWidget.__init__(self, StandardConstantWidget,
                                 ["==", "<", ">", "<=", ">="], 
                                 param, parent)
    
class ColorQueryWidget(StandardQueryWidget):
    def __init__(self, param, parent=None):
        BaseQueryWidget.__init__(self, ColorWidget, ["2.3", "5", "10", "50"],
                                 param, parent)
