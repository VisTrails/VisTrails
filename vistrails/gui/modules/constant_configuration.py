###############################################################################
##
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
""" This file specifies the configuration widget for Constant
modules. Please notice that this is different from the module configuration
widget described in module_configure.py. We present a Color constant to be
used as a template for creating a configuration widget for other custom
constants.

"""
from PyQt4 import QtCore, QtGui
from core.utils import any, expression
from core import system

############################################################################

class ConstantWidgetMixin(object):

    def __init__(self, contents=None):
        self._last_contents = contents

    def update_parent(self):
        newContents = self.contents()
        if newContents != self._last_contents:
            if self.parent() and hasattr(self.parent(), 'updateMethod'):
                self.parent().updateMethod()
            self._last_contents = newContents
            self.emit(QtCore.SIGNAL('contentsChanged'), (self,newContents))    

class StandardConstantWidget(QtGui.QLineEdit, ConstantWidgetMixin):
    """
    StandardConstantWidget is a basic widget to be used
    to edit int/float/string values in VisTrails.

    When creating your own widget, you can subclass from this widget if you
    need only a QLineEdit or use your own QT widget. There are two things you
    need to pay attention to:

    1) Re-implement the contents() method so we can get the current value
       stored in the widget.

    2) When the user is done with configuration, make sure to call
       update_parent() so VisTrails can pass that information to the Provenance
       System. In this example we do that on focusOutEvent and when the user
       presses the return key.

    """
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'

        """
        QtGui.QLineEdit.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # assert param.namespace == None
        # assert param.identifier == 'edu.utah.sci.vistrails.basic'
        contents = param.strValue
        contentType = param.type
        self.setText(contents)
        self._contentType = contentType
        self.connect(self,
                     QtCore.SIGNAL('returnPressed()'),
                     self.update_parent)

    def contents(self):
        """contents() -> str
        Re-implement this method to make sure that it will return a string
        representation of the value that it will be passed to the module
        As this is a QLineEdit, we just call text()

        """
        self.update_text()
        return str(self.text())

    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Re-implement this method so the widget can change its value after 
        constructed. If silent is False, it will propagate the event back 
        to the parent.
        As this is a QLineEdit, we just call setText(strValue)
        """
        self.setText(strValue)
        self.update_text()
        if not silent:
            self.update_parent()
            
    def update_text(self):
        """ update_text() -> None
        Update the text to the result of the evaluation

        """
        # FIXME: eval should pretty much never be used
        base = expression.evaluate_expressions(self.text())
        if self._contentType == 'String':
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)
                
    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        width = min(metrics.width(self.text())+10,70)
        return QtCore.QSize(width, 
                            metrics.height()+6)
    
    def minimumSizeHint(self):
        return self.sizeHint()
    
    ###########################################################################
    # event handlers

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        self._contents = str(self.text())
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QLineEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QLineEdit.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

###############################################################################
# File Constant Widgets

class PathChooserToolButton(QtGui.QToolButton):
    """
    PathChooserToolButton is a toolbar button that opens a browser for
    paths.  The lineEdit is updated with the pathname that is selected.

    """
    def __init__(self, parent=None, lineEdit=None, toolTip=None):
        """
        PathChooserToolButton(parent: QWidget, 
                              lineEdit: StandardConstantWidget) ->
                 PathChooserToolButton

        """
        QtGui.QToolButton.__init__(self, parent)
        self.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DirOpenIcon)))
        self.setIconSize(QtCore.QSize(12,12))
        if toolTip is None:
            toolTip = 'Open a file chooser'
        self.setToolTip(toolTip)
        self.setAutoRaise(True)
        self.lineEdit = lineEdit
        self.connect(self,
                     QtCore.SIGNAL('clicked()'),
                     self.runDialog)

    def setPath(self, path):
        """
        setPath() -> None

        """
        if self.lineEdit and path and not path.isEmpty():
            self.lineEdit.setText(path)
            self.lineEdit.update_parent()
            self.parent().update_parent()
    
    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        return QtGui.QFileDialog.getOpenFileName(self,
                                                 'Use Filename '
                                                 'as Value...',
                                                 text,
                                                 'All files '
                                                 '(*.*)')

    def runDialog(self):
        path = self.openChooser()
        self.setPath(path)

class PathChooserWidget(QtGui.QWidget, ConstantWidgetMixin):
    """
    PathChooserWidget is a widget containing a line edit and a button that
    opens a browser for paths. The lineEdit is updated with the pathname that is
    selected.

    """    
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
        parent: QWidget)
        Initializes the line edit with contents

        """
        QtGui.QWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        layout = QtGui.QHBoxLayout()
        self.line_edit = StandardConstantWidget(param, self)
        self.browse_button = self.create_browse_button()
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)

    def create_browse_button(self):
        return PathChooserToolButton(self, self.line_edit)

    def updateMethod(self):
        if self.parent() and hasattr(self.parent(), 'updateMethod'):
            self.parent().updateMethod()

    def contents(self):
        """contents() -> str
        Return the contents of the line_edit

        """
        return self.line_edit.contents()
    
    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Updates the contents of the line_edit 
        """
        self.line_edit.setContents(strValue, silent)
        if not silent:
            self.update_parent()
 
        
    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QWidget.focusInEvent(self, event)   
        
    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QWidget.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

class FileChooserToolButton(PathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None):
        PathChooserToolButton.__init__(self, parent, lineEdit, 
                                       "Open a file chooser")
        
    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        return QtGui.QFileDialog.getOpenFileName(self,
                                                 'Use Filename '
                                                 'as Value...',
                                                 text,
                                                 'All files '
                                                 '(*.*)')

class FileChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        return FileChooserToolButton(self, self.line_edit)


class DirectoryChooserToolButton(PathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None):
        PathChooserToolButton.__init__(self, parent, lineEdit, 
                                       "Open a directory chooser")

    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        return QtGui.QFileDialog.getExistingDirectory(self,
                                                      'Use Directory '
                                                      'as Value...',
                                                      text)

class DirectoryChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        return DirectoryChooserToolButton(self, self.line_edit)

class OutputPathChooserToolButton(PathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None):
        PathChooserToolButton.__init__(self, parent, lineEdit,
                                       "Open a path chooser")
    
    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        return QtGui.QFileDialog.getSaveFileName(self,
                                                 'Save Path',
                                                 text,
                                                 'All files (*.*)')

class OutputPathChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        return OutputPathChooserToolButton(self, self.line_edit)

class BooleanWidget(QtGui.QCheckBox, ConstantWidgetMixin):

    _values = ['True', 'False']
    _states = [QtCore.Qt.Checked, QtCore.Qt.Unchecked]

    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        Initializes the line edit with contents
        """
        QtGui.QCheckBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        assert param.type == 'Boolean'
        assert param.identifier == 'edu.utah.sci.vistrails.basic'
        assert param.namespace is None
        self.connect(self, QtCore.SIGNAL('stateChanged(int)'),
                     self.change_state)
        self.setContents(param.strValue)
        
    def contents(self):
        return self._values[self._states.index(self.checkState())]

    def setContents(self, strValue, silent=True):
        if strValue:
            value = strValue
        else:
            value = "False"
        assert value in self._values
        self.setCheckState(self._states[self._values.index(value)])
        if not silent:
            self.update_parent()
            
    def change_state(self, state):
        self.update_parent()

###############################################################################
# Constant Color widgets

class ColorChooserButton(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAutoFillBackground(True)
        self.setColor(QtGui.QColor(255,255,255))
        self.setFixedSize(30,22)
        if system.systemType == 'Darwin':
            #the mac's nice look messes up with the colors
            self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)

    def setColor(self, qcolor, silent=True):
        self.qcolor = qcolor
        
        self._palette = QtGui.QPalette(self.palette())
        self._palette.setBrush(QtGui.QPalette.Base, self.qcolor)
        self._palette.setBrush(QtGui.QPalette.Window, self.qcolor)
        self.setPalette(self._palette)
        self.repaint()
        if not silent:
            self.emit(QtCore.SIGNAL("color_selected"))

    def sizeHint(self):
        return QtCore.QSize(24,24)

    def mousePressEvent(self, event):
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        if event.button() == QtCore.Qt.LeftButton:
            self.openChooser()
       

    def openChooser(self):
        """
        openChooser() -> None

        """
        color = QtGui.QColorDialog.getColor(self.qcolor, self.parent())
        if color.isValid():
            self.setColor(color, silent=False)
        else:
            self.setColor(self.qcolor)


class ColorWidget(QtGui.QWidget, ConstantWidgetMixin):
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        """
        contents = param.strValue
        contentsType = param.type
        QtGui.QWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        layout = QtGui.QHBoxLayout()
        self.color_indicator = ColorChooserButton(self)
        self.connect(self.color_indicator,
                     QtCore.SIGNAL("color_selected"),
                     self.update_parent)
        self._last_contents = contents
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.color_indicator)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setContents(contents)
        
    def contents(self):
        """contents() -> str
        Return the string representation of color_indicator

        """
        return "%s,%s,%s" % (self.color_indicator.qcolor.redF(),
                             self.color_indicator.qcolor.greenF(),
                             self.color_indicator.qcolor.blueF())
        
    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Updates the color_indicator to display the color in strValue
        
        """
        if strValue != '':
            color = strValue.split(',')
            qcolor = QtGui.QColor(float(color[0])*255,
                                  float(color[1])*255,
                                  float(color[2])*255)
            self.color_indicator.setColor(qcolor, silent)
        
    def mousePressEvent(self, event):
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QWidget.mousePressEvent(self, event)
        
    ###########################################################################
    # event handlers

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QFrame.focusInEvent(self, event)    
